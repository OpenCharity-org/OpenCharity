#!/usr/bin/env python3
"""Build webapp/atlas.html: a world-map view of the charity registration dataset.

Reads  charities_by_country_v2.csv  and  webapp/geo/countries-50m.json
       (world-atlas@2.0.2 TopoJSON, Natural Earth 1:50m).
Writes webapp/atlas.html — one self-contained page (and docs/index.html, the same
page as a full HTML document for GitHub Pages) (data + map geometry
embedded; d3 and topojson-client load from cdnjs).

Map: choropleth coloured by difficulty / remote founding / fee / time / bank
access / foreign-funding rules / Google for Nonprofits / confidence;
micro-states drawn as dots. Click a country for its full dossier.
Ranking: overall, custom weights, easiest, cheapest, fastest, most remote-friendly,
easiest banking, fewest funding restrictions (and reverses). Multi-select facets
(OR within a facet, AND across facets) plus fee/time ceilings filter both the map
and the list. Up to 6 countries can be benchmarked side by side against the
median of the filtered set. View state persists in localStorage.

Fee and time are parsed from free text: the fee is the lowest US$ figure in
the fee cell ("none"/"free" = 0), the time is the first duration in the time
cell, in days. Unparseable cells rank last.
"""
import csv
import json
import re
from pathlib import Path

from build_webapp import build_data

BASE = Path(__file__).parent
GEO = BASE / "webapp" / "geo" / "countries-50m.json"
BANKING = BASE / "banking_by_country.csv"  # merge_banking.py: personal accounts for non-residents
OUT = BASE / "webapp" / "atlas.html"
DOCS = BASE / "docs" / "index.html"  # GitHub Pages copy (full HTML document)

# dataset name -> Natural Earth feature name
ALIAS = {
    "United States": "United States of America",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Antigua & Barbuda": "Antigua and Barb.",
    "St. Kitts & Nevis": "St. Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St. Vincent & Grenadines": "St. Vin. and Gren.",
    "Dominican Republic": "Dominican Rep.",
    "Macau": "Macao",
    "Solomon Islands": "Solomon Is.",
    "Marshall Islands": "Marshall Is.",
    "Central African Republic": "Central African Rep.",
    "Republic of the Congo": "Congo",
    "Congo (DRC)": "Dem. Rep. Congo",
    "Equatorial Guinea": "Eq. Guinea",
    "Sao Tome & Principe": "São Tomé and Principe",
    "Eswatini": "eSwatini",
    "Bosnia & Herzegovina": "Bosnia and Herz.",
    "North Macedonia": "Macedonia",
    "Vatican City": "Vatican",
    "Western Sahara": "W. Sahara",
    "South Sudan": "S. Sudan",
}
# jurisdictions with no 1:50m polygon: [lon, lat]
POINTS = {"Tuvalu": [179.2, -8.5]}

# same weights as build_xlsx.score (lower = better)
DIFF_SCORE = {"easy": 0, "medium": 1, "hard": 2, "very hard": 3}
PRES_SCORE = {"yes": 0, "partial": 1, "no": 3}


def _num(s):
    return float(s.replace(",", ""))


def parse_fee(text):
    """Lowest and highest US$ figure in the fee cell, or (None, None)."""
    t = text.lower().strip()
    if not t or re.search(r"not permitted|not available|^n/?a\b|unpublished|not published", t):
        return None, None
    if re.match(r"^(none|free|nil|no fee|us\$\s?0\b|\$\s?0\b|0\b)", t):
        return 0.0, 0.0
    m = re.search(r"(?:us)?\$\s?(\d[\d,]*(?:\.\d+)?)\s*(k)?(?:\s*[-–]\s*(?:us)?\$?\s?(\d[\d,]*(?:\.\d+)?)\s*(k)?)?", t)
    if not m:
        m2 = re.match(r"^~?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:usd)?\s*$", t)
        if m2:
            v = _num(m2.group(1))
            return v, v
        return None, None
    lo = _num(m.group(1)) * (1000 if m.group(2) else 1)
    if not m.group(3):
        return lo, lo
    hi_raw = _num(m.group(3))
    hi = hi_raw * (1000 if (m.group(4) or m.group(2)) else 1)
    if m.group(4) and not m.group(2) and _num(m.group(1)) < hi_raw:
        lo *= 1000  # "$1-2k" means 1,000-2,000
    return lo, max(lo, hi)


UNIT = r"(business days?|working days?|days?|weeks?|months?|years?)"
DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}


def _days(n, unit):
    return round(_num(n) * DAYS[re.sub(r"s$", "", unit.split()[-1])])


def parse_time(text):
    """First duration in the time cell as (low_days, high_days), or (None, None)."""
    t = text.lower()
    if re.match(r"^\s*n/?a\b|not available|not feasible\W*$", t):
        return None, None
    m = re.search(rf"(\d+(?:\.\d+)?)\s*{UNIT}\s*[-–]\s*(\d+(?:\.\d+)?)\s*{UNIT}", t)
    if m:
        return _days(m.group(1), m.group(2)), _days(m.group(3), m.group(4))
    m = re.search(rf"(\d+(?:\.\d+)?)\s*(?:[-–]|to)\s*(\d+(?:\.\d+)?)\+?\s*{UNIT}", t)
    if m:
        return _days(m.group(1), m.group(3)), _days(m.group(2), m.group(3))
    m = re.search(rf"(\d+(?:\.\d+)?)\s*{UNIT}", t)
    if m:
        v = _days(m.group(1), m.group(2))
        return v, v
    return None, None


def bank_cat(text):
    t = text.lower()
    if t.startswith(("effectively blocked", "blocked")) or "effectively blocked" in t[:90]:
        return "blocked"
    if re.search(r"fully online|possible online|online (?:opening|onboarding|application)s? (?:is |are )?(?:possible|available)"
                 r"|\bemis?\b|\bwise\b|roshan|remote(?:ly)? open\w* (?:is )?possible|start online|partially online|via ekyc"
                 r"|onboards non-residents fully online", t) \
            and not re.search(r"no fully online|online (?:onboarding )?(?:is )?unavailable|no online", t):
        return "remote"
    return "visit"


def fee_bin(lo):
    if lo is None:
        return "unknown"
    return "free" if lo == 0 else "low" if lo <= 100 else "mid" if lo <= 500 else "high"


def time_bin(lo):
    if lo is None:
        return "unknown"
    return "fast" if lo <= 14 else "month" if lo <= 31 else "quarter" if lo <= 92 else "slow"


def enrich(d):
    d["fee_lo"], d["fee_hi"] = parse_fee(d["fee_usd"])
    d["days_lo"], d["days_hi"] = parse_time(d["time_to_reg"])
    d["fee_bin"] = fee_bin(d["fee_lo"])
    d["time_bin"] = time_bin(d["days_lo"])
    d["bank_cat"] = bank_cat(d["bank_access"])
    d["funding_cat"] = "open" if d["donor_restr"].lower().startswith(("none", "no restriction", "no fcra")) else "restricted"
    d["score"] = (DIFF_SCORE.get(d["difficulty"].lower(), 2) * 2 + PRES_SCORE.get(d["no_presence"].lower(), 2) * 2
                  + (0 if d["gfn"] == "Yes" else 3) + {"high": 0, "med": 1}.get(d["confidence"].lower(), 2))
    return d


# banking_by_country.csv column -> record key
PB_COLS = {
    "Non-resident personal account": "pb_status", "Opening method": "pb_method",
    "Local residence required": "pb_res", "Banking difficulty": "pb_diff",
    "Documents required": "pb_docs", "Minimum deposit & fees": "pb_dep",
    "Banks accepting non-residents": "pb_banks", "Restrictions": "pb_restr",
    "Alternatives (fintech / regional)": "pb_alt", "Confidence": "pb_conf", "Sources": "pb_src",
    "Opening fee (USD)": "pb_open", "Minimum deposit (USD)": "pb_mindep", "Monthly fee (USD)": "pb_month",
    "Cost note": "pb_costnote",
}
PB_NUM = ("pb_open", "pb_mindep", "pb_month")


def pb_year_bin(v):
    if v is None:
        return "unknown"
    return "free" if v == 0 else "low" if v <= 60 else "mid" if v <= 240 else "high"


def pb_dep_bin(v):
    if v is None:
        return "unknown"
    return "none" if v == 0 else "low" if v <= 500 else "mid" if v <= 10000 else "high"


def add_banking(data):
    rows = {r["Country"]: r for r in csv.DictReader(open(BANKING, encoding="utf-8"))}
    missing = [d["country"] for d in data if d["country"] not in rows]
    if missing:
        raise SystemExit(f"{BANKING.name} has no row for: {missing}")
    for d in data:
        for col, key in PB_COLS.items():
            d[key] = rows[d["country"]][col]
        for key in PB_NUM:
            d[key] = float(d[key]) if d[key] != "" else None
        # first-year fees: 12 monthly fees + the opening fee (unpublished opening fee counts as 0); needs a known monthly fee
        d["pb_year"] = 12 * d["pb_month"] + (d["pb_open"] or 0) if d["pb_month"] is not None else None
        d["pb_cost_bin"] = pb_year_bin(d["pb_year"])
        d["pb_dep_bin"] = pb_dep_bin(d["pb_mindep"])


def main():
    data, src_name = build_data()
    data = [enrich(d) for d in data]
    add_banking(data)
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    geo["objects"]["countries"]["geometries"] = [
        g for g in geo["objects"]["countries"]["geometries"]
        if g["properties"]["name"] != "Antarctica"
    ]
    names = {g["properties"]["name"] for g in geo["objects"]["countries"]["geometries"]}
    missing = [d["country"] for d in data
               if ALIAS.get(d["country"], d["country"]) not in names and d["country"] not in POINTS]
    if missing:
        raise SystemExit(f"no map shape for: {missing}")

    def js(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (TEMPLATE.replace("__DATA__", js(data))
            .replace("__GEO__", js(geo))
            .replace("__ALIAS__", js(ALIAS))
            .replace("__POINTS__", js(POINTS))
            .replace("__COUNT__", str(len(data)))
            .replace("__SRC__", src_name))
    OUT.write_text(html, encoding="utf-8")
    # GitHub Pages: same page wrapped in a full document (the artifact host adds this skeleton itself)
    head, body = html.split('<div class="wrap"', 1)
    DOCS.parent.mkdir(exist_ok=True)
    DOCS.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                    '<meta name="description" content="How hard it is for an Australia-based founder to register a charity in every country: '
                    'rules, fees, timelines and sources.">\n'
                    '<meta property="og:title" content="Charity Registration Atlas">\n'
                    f'<meta property="og:description" content="Rank and compare {len(data)} jurisdictions by how easy, cheap and fast it is to register a charity from Australia.">\n'
                    '<meta property="og:image" content="https://raw.githubusercontent.com/OpenCharity-org/OpenCharity/main/docs/screenshots/desktop-light.png">\n'
                    '<meta property="og:url" content="https://opencharity-org.github.io/OpenCharity/">\n'
                    '<meta name="twitter:card" content="summary_large_image">\n'
                    + head + '</head>\n<body style="margin:0">\n<div class="wrap"' + body + '\n</body>\n</html>\n', encoding="utf-8")
    (DOCS.parent / ".nojekyll").write_text("", encoding="utf-8")
    nf = sum(d["fee_lo"] is None for d in data)
    nt = sum(d["days_lo"] is None for d in data)
    print(f"wrote {OUT} ({len(data)} jurisdictions, {len(html) // 1024} KB; "
          f"fee unparsed {nf}, time unparsed {nt})")


TEMPLATE = r"""<title>Charity Registration Atlas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* Layout: map-first atlas. Facet panel drives map + ranked list; dossier beside the map; comparison table benchmarks picked countries against the filtered median. */
:root {
  --bg: #eef2f3; --surface: #ffffff; --ink: #15212a; --muted: #566773; --line: #d3dce0;
  --sea: #dde7ec; --land-none: #c9d1d5; --accent: #1d5d86; --accent-soft: #dbe9f2; --focus: #1d5d86;
  --d1: #2c8a68; --d2: #c79a1e; --d3: #cf6529; --d4: #8a2840; --d0: #9aa7ae;
  --best: #e0f1e9; --chip-ink: #ffffff;
  --f-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --f-body: "Public Sans", "Helvetica Neue", Arial, system-ui, sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e151a; --surface: #152027; --ink: #e3ebef; --muted: #8fa1ac; --line: #26343d;
  --sea: #111c23; --land-none: #2c3942; --accent: #74b4de; --accent-soft: #1b3445; --focus: #74b4de;
  --d1: #3aa982; --d2: #d8ad35; --d3: #e27a3e; --d4: #c0485f; --d0: #5d6d77;
  --best: #17362b; --chip-ink: #0e151a;
  color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0e151a; --surface: #152027; --ink: #e3ebef; --muted: #8fa1ac; --line: #26343d;
  --sea: #111c23; --land-none: #2c3942; --accent: #74b4de; --accent-soft: #1b3445; --focus: #74b4de;
  --d1: #3aa982; --d2: #d8ad35; --d3: #e27a3e; --d4: #c0485f; --d0: #5d6d77;
  --best: #17362b; --chip-ink: #0e151a;
  color-scheme: dark; }

* { box-sizing: border-box; }
[hidden] { display: none !important; }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); }
.wrap { max-width: 1440px; margin: 0 auto; padding-inline: 20px; padding-block: 20px 48px; display: grid; grid-template-columns: minmax(0, 1fr); gap: 16px; }
.wrap.has-tray { padding-bottom: 110px; }
h1, h2, h3 { font-family: var(--f-display); text-wrap: balance; margin: 0; letter-spacing: -0.01em; }
a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.mono { font-family: var(--f-mono); font-variant-numeric: tabular-nums; }
.lbl { font: 500 11px var(--f-mono); letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }

.titlebar { display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: center; justify-content: space-between; }
.hlinks { display: flex; flex-wrap: wrap; gap: 6px; }
.btn.ghost { background: transparent; text-decoration: none; display: inline-flex; align-items: center; font-size: 12.5px; padding: 5px 10px; }
.ftoggle { display: none; }
details.dmore { display: grid; gap: 14px; }
details.dmore > summary { cursor: pointer; font: 600 13px var(--f-body); color: var(--accent); list-style: none; border-top: 1px solid var(--line); padding-top: 12px; }
details.dmore > summary::-webkit-details-marker { display: none; }
details.dmore > summary::before { content: "+ "; } details.dmore[open] > summary::before { content: "− "; }
details.dmore[open] > summary { margin-bottom: 12px; }
header.top h1 { font-size: clamp(26px, 4vw, 40px); font-weight: 700; line-height: 1.05; }
header.top p { margin: 6px 0 0; color: var(--muted); max-width: 72ch; }

/* controls */
.controls { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 14px 16px; display: grid; gap: 14px; }
.row { display: flex; flex-wrap: wrap; gap: 10px 12px; align-items: end; }
.field { display: grid; gap: 4px; min-width: 0; }
.field > span { font: 500 11px var(--f-mono); letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.field input, .field select { font: 14px var(--f-body); color: var(--ink); background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; min-width: 0; max-width: 100%; }
.field.rank select { font-weight: 600; border-color: var(--ink); background: var(--surface); }
.field.grow { flex: 1 1 220px; } .field.grow input { width: 100%; }
.field.numf input { width: 120px; }
.btn { font: 600 13px var(--f-body); color: var(--ink); background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 7px 12px; cursor: pointer; }
.btn.primary { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.btn.link { background: none; border: 0; color: var(--accent); text-decoration: underline; text-underline-offset: 3px; padding-inline: 4px; }
.count { font: 12px var(--f-mono); color: var(--muted); margin-left: auto; align-self: center; }

.facets { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 12px 18px; }
.facet { border: 0; margin: 0; padding: 0; min-width: 0; display: grid; gap: 6px; align-content: start; }
.facet legend { padding: 0; margin-bottom: 6px; }
.facet.wide { grid-column: 1 / -1; }
.opts { display: flex; flex-wrap: wrap; gap: 5px; }
.opt { display: inline-flex; align-items: center; gap: 6px; font: 600 12.5px var(--f-body); color: var(--ink); background: var(--bg); border: 1px solid var(--line);
  border-radius: 999px; padding: 4px 10px 4px 7px; cursor: pointer; }
.opt .sw { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.opt .n { font: 400 11.5px var(--f-mono); color: var(--muted); }
.opt[aria-pressed="true"] { border-color: var(--accent); background: var(--accent-soft); box-shadow: inset 0 0 0 1px var(--accent); }
.opt.zero:not([aria-pressed="true"]):not(.exc) { opacity: .45; }
#active .summary { flex-basis: 100%; margin: 4px 0 0; font-size: 13.5px; color: var(--muted); }
#active .summary b { color: var(--ink); }
.opt.exc { border-color: var(--d4); background: var(--surface); box-shadow: inset 0 0 0 1px var(--d4); color: var(--muted); }
.opt.exc::before { content: "not"; font: 700 10.5px var(--f-mono); text-transform: uppercase; color: var(--d4); text-decoration: none; display: inline-block; }
details.more summary { cursor: pointer; font: 600 13px var(--f-body); color: var(--accent); list-style: none; }
details.more summary::-webkit-details-marker { display: none; }
details.more summary::before { content: "+ "; } details.more[open] summary::before { content: "− "; }
details.more[open] summary { margin-bottom: 12px; }

.active { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; min-height: 28px; }
.active .tag { display: inline-flex; align-items: center; gap: 6px; font: 600 12px var(--f-body); background: var(--accent-soft); color: var(--ink); border: 1px solid var(--accent); border-radius: 6px; padding: 3px 4px 3px 8px; }
.active .tag button { all: unset; cursor: pointer; width: 18px; height: 18px; display: grid; place-items: center; border-radius: 4px; font-size: 14px; line-height: 1; }
.active .tag button:hover { background: var(--surface); }
.active .tag button:focus-visible { outline: 2px solid var(--focus); }
.active .none { color: var(--muted); font-size: 13px; }

.weights { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 10px 18px; padding: 12px 14px; background: var(--bg); border: 1px solid var(--line); border-radius: 10px; }
.weights .whead { grid-column: 1 / -1; display: flex; flex-wrap: wrap; gap: 6px 14px; align-items: baseline; justify-content: space-between; }
.weights .whead p { margin: 0; font-size: 13px; color: var(--muted); }
.wrow { display: grid; gap: 2px; }
.wrow label { display: flex; justify-content: space-between; font: 600 13px var(--f-body); }
.wrow output { font: 500 12px var(--f-mono); color: var(--muted); }
.wrow input { width: 100%; accent-color: var(--accent); }

.modes { display: flex; flex-wrap: wrap; gap: 4px; padding: 4px; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
.modes button { font: 600 12.5px var(--f-body); color: var(--muted); background: none; border: 0; padding: 6px 10px; border-radius: 7px; cursor: pointer; }
.modes button[aria-pressed="true"] { background: var(--ink); color: var(--bg); }

.main { display: grid; grid-template-columns: minmax(0, 1fr) 400px; gap: 16px; align-items: start; }
@media (max-width: 980px) { .main { grid-template-columns: minmax(0, 1fr); } }
.mapcol { display: grid; gap: 10px; min-width: 0; }

.mapcard { background: var(--sea); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; position: relative; min-width: 0; }
#map { display: block; width: 100%; height: auto; touch-action: none; cursor: grab; }
#map:active { cursor: grabbing; }
.country { stroke: var(--sea); stroke-width: 0.5; vector-effect: non-scaling-stroke; cursor: pointer; transition: opacity .15s; }
.country.nodata { fill: var(--land-none); cursor: default; }
.country.dim, .dot.dim { opacity: 0.16; }
.country:hover:not(.nodata) { stroke: var(--ink); stroke-width: 1; }
.country.sel, .dot.sel { stroke: var(--ink); stroke-width: 2; }
.country.cmp, .dot.cmp { stroke: var(--accent); stroke-width: 2; }
.dot { stroke: var(--sea); stroke-width: 1; vector-effect: non-scaling-stroke; cursor: pointer; }
.c-d1 { fill: var(--d1); background: var(--d1); } .c-d2 { fill: var(--d2); background: var(--d2); }
.c-d3 { fill: var(--d3); background: var(--d3); } .c-d4 { fill: var(--d4); background: var(--d4); }
.c-d0 { fill: var(--d0); background: var(--d0); }

.legend { position: absolute; left: 12px; bottom: 12px; right: 56px; display: flex; flex-wrap: wrap; gap: 6px; pointer-events: none; }
.legend button { pointer-events: auto; display: inline-flex; align-items: center; gap: 7px; font: 600 12px var(--f-body); color: var(--ink);
  background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 4px 10px 4px 6px; cursor: pointer; }
.legend button[aria-pressed="false"] { opacity: .45; text-decoration: line-through; }
.legend .sw { width: 12px; height: 12px; border-radius: 50%; }
.legend .n { font-family: var(--f-mono); color: var(--muted); font-weight: 400; }
.zoom { position: absolute; right: 12px; top: 12px; display: grid; gap: 4px; }
.zoom button { width: 32px; height: 32px; font: 600 16px var(--f-body); color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 8px; cursor: pointer; }
.tip { position: absolute; pointer-events: none; background: var(--ink); color: var(--bg); font-size: 12.5px; padding: 6px 9px; border-radius: 7px; max-width: 260px; line-height: 1.35; }
.tip b { font-weight: 600; }
@media (max-width: 640px) { .legend { position: static; padding: 0 12px 12px; } }

aside.dossier { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 20px; display: grid; gap: 16px; min-width: 0; }
@media (min-width: 981px) { aside.dossier { position: sticky; top: calc(env(safe-area-inset-top, 0px) + 16px); max-height: calc(100vh - 32px); overflow-y: auto; } }
.dossier .eyebrow { font: 500 11px var(--f-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.dossier .dh { display: flex; gap: 12px; align-items: start; justify-content: space-between; }
.dossier h2 { font-size: 28px; line-height: 1.1; margin-top: 2px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { font: 600 12px var(--f-body); padding: 3px 9px; border-radius: 999px; color: var(--chip-ink); }
.chip.plain { color: var(--ink); background: transparent; border: 1px solid var(--line); }
.facts { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; margin: 0; }
.facts div { background: var(--surface); padding: 10px 12px; min-width: 0; }
.facts dt { font: 500 11px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.facts dd { margin: 2px 0 0; font-size: 13.5px; overflow-wrap: anywhere; }
.facts .big { font: 600 18px var(--f-display); }
.sec h3 { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
.sec p { margin: 0; font-size: 14px; overflow-wrap: anywhere; }
.sec.pb { background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; }
.sec.pb .chips { margin: 6px 0 10px; }
.pbl { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 4px 12px; margin: 0; font-size: 14px; }
.pbl dt { font: 500 11px var(--f-mono); letter-spacing: .05em; text-transform: uppercase; color: var(--muted); padding-top: 3px; }
.pbl dd { margin: 0; overflow-wrap: anywhere; }
.pbsrc { margin: 8px 0 0; font-size: 13px; }
.facts.pbcost { margin-bottom: 6px; }
.facts.pbcost .big { font-size: 18px; }
.pbnote { margin: 0 0 10px; font-size: 13px; color: var(--muted); }
@media (max-width: 520px) { .pbl { grid-template-columns: minmax(0, 1fr); } .pbl dd { margin-bottom: 6px; } }
.sec + .sec { border-top: 1px solid var(--line); padding-top: 14px; }
.sec ul { margin: 4px 0 0; padding-left: 18px; font-size: 13px; color: var(--muted); display: grid; gap: 5px; overflow-wrap: anywhere; }
.sec .src a { word-break: break-all; }
.empty { color: var(--muted); }

section.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; display: grid; gap: 12px; min-width: 0; }
.phead { display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 16px; justify-content: space-between; }
.phead h2 { font-size: 22px; }
.phead p { margin: 0; color: var(--muted); font-size: 13px; }
.tablewrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
/* the ranking table always fits the panel width: columns wrap instead of scrolling sideways */
#tbl { width: 100%; table-layout: auto; }
#tbl th, #tbl td { padding: 8px 6px; }
#tbl th { white-space: normal; line-height: 1.3; vertical-align: bottom; letter-spacing: .03em; }
#tbl td .pill { white-space: normal; align-items: flex-start; line-height: 1.3; }
#tbl td .pill i { margin-top: 4px; }
#tbl td.name { white-space: normal; min-width: 8em; }
#tbl td.num { white-space: normal; }
th { text-align: left; font: 500 11px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); padding: 8px 10px; border-bottom: 1px solid var(--line); white-space: nowrap; }
th button { all: unset; cursor: pointer; }
th button:focus-visible { outline: 2px solid var(--focus); }
th[aria-sort="ascending"] button::after { content: " ↑" attr(data-pri); } th[aria-sort="descending"] button::after { content: " ↓" attr(data-pri); }
th[aria-sort="ascending"], th[aria-sort="descending"] { color: var(--ink); }
td { padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
#tbl tbody tr { cursor: pointer; }
#tbl tbody tr:hover, #tbl tbody tr.sel { background: var(--bg); }
td.ck { width: 34px; } td.ck input { width: 16px; height: 16px; accent-color: var(--accent); cursor: pointer; }
td.rank { font: 500 13px var(--f-mono); color: var(--muted); width: 3.5em; }
td.name { font-weight: 600; white-space: nowrap; }
td .sub { display: block; font-weight: 400; color: var(--muted); font-size: 12px; }
td .pill { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
td .pill i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; flex: none; }
td.num { font-family: var(--f-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
td.fit b { font: 600 13px var(--f-mono); }
.bar { display: block; height: 4px; border-radius: 2px; background: var(--line); margin-top: 4px; width: 64px; }
.bar i { display: block; height: 100%; border-radius: 2px; background: var(--accent); }

/* comparison */
#cmpTbl { min-width: 640px; table-layout: fixed; }
#cmpTbl th.attr, #cmpTbl td.attr { width: 170px; }
#cmpTbl thead th { vertical-align: bottom; white-space: normal; }
#cmpTbl thead th .cn { display: flex; align-items: start; justify-content: space-between; gap: 6px; font: 700 15px var(--f-display); letter-spacing: 0; text-transform: none; color: var(--ink); }
#cmpTbl thead th .cn button { all: unset; cursor: pointer; color: var(--muted); font-size: 16px; line-height: 1; padding: 0 2px; }
#cmpTbl thead th .cn a { color: inherit; text-decoration: none; cursor: pointer; }
#cmpTbl thead th.bench .cn { color: var(--muted); font-style: italic; }
#cmpTbl td { font-size: 13px; overflow-wrap: anywhere; }
#cmpTbl td.best { background: var(--best); }
#cmpTbl td.bench { color: var(--muted); background: var(--bg); }
#cmpTbl td.attr { font: 500 11px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
#cmpTbl tr.text td:not(.attr) { color: var(--ink); font-size: 12.5px; }
.cmpnote { font-size: 12.5px; color: var(--muted); margin: 0; }
.cmpnote .key { display: inline-block; width: 10px; height: 10px; background: var(--best); border: 1px solid var(--line); vertical-align: -1px; margin-right: 4px; }

/* compare tray */
.tray { position: fixed; left: 0; right: 0; bottom: 0; z-index: 5; background: var(--surface); border-top: 1px solid var(--line);
  padding: 10px 20px calc(10px + env(safe-area-inset-bottom, 0px)); box-shadow: 0 -6px 20px rgba(0, 0, 0, .12); }
.tray .in { max-width: 1440px; margin: 0 auto; display: flex; flex-wrap: wrap; gap: 8px 12px; align-items: center; }
.tray .names { display: flex; flex-wrap: wrap; gap: 6px; flex: 1 1 300px; min-width: 0; }
.tray .tag { display: inline-flex; align-items: center; gap: 4px; font: 600 12.5px var(--f-body); border: 1px solid var(--accent); background: var(--accent-soft); border-radius: 6px; padding: 3px 4px 3px 8px; }
.tray .tag button { all: unset; cursor: pointer; padding: 0 4px; font-size: 14px; }
.tray .tag button:focus-visible { outline: 2px solid var(--focus); }

footer { color: var(--muted); font-size: 12.5px; max-width: 95ch; display: grid; gap: 6px; }
footer p { margin: 0; }
@media (max-width: 520px) { .wrap { padding-inline: 16px; } .facts { grid-template-columns: 1fr; } .dossier h2 { font-size: 24px; } .count { margin-left: 0; } .tray { padding-inline: 16px; } }
/* phones */
@media (max-width: 1040px) {
  #tbl { min-width: 0; }
  #tbl thead { display: none; }
  #tbl tbody tr { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; padding: 12px 2px; border-bottom: 1px solid var(--line); }
  #tbl td { border: 0; padding: 0; }
  #tbl td.ck { width: auto; order: 0; }
  #tbl td.rank { order: 1; width: auto; }
  #tbl td.name { order: 2; flex: 1 1 calc(100% - 110px); white-space: normal; }
  #tbl td.name .sub { display: inline; margin-left: 6px; }
  #tbl td.fit { order: 3; display: flex; align-items: center; gap: 6px; }
  #tbl td.fit .bar { margin: 0; }
  #tbl td.pc, #tbl td.num { order: 4; font-size: 12.5px; }
  #tbl td.num[data-l]::before { content: attr(data-l) " "; font: 500 10.5px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
  #tbl td.gfn { display: none; }
}
@media (max-width: 760px) {
  .ftoggle { display: inline-flex; margin-left: auto; }
  .controls:not(.open) .fbody { display: none; }
  .controls { gap: 10px; padding: 12px; }
  .field.rank { flex: 1 1 100%; } .field.rank select { width: 100%; }
  .field.numf { flex: 1 1 40%; } .field.numf input { width: 100%; }
  .count { margin-left: 0; }
  .facets { grid-template-columns: minmax(0, 1fr); }
  .modes { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; -webkit-overflow-scrolling: touch; }
  .modes::-webkit-scrollbar { display: none; }
  .modes button { flex: none; }
  .mapcard { display: flex; flex-direction: column; }
  .zoom { position: static; display: flex; order: 3; padding: 0 12px 12px; gap: 6px; }
  .zoom button { width: 36px; height: 32px; }
  .hlinks .btn { font-size: 12px; padding: 4px 8px; }
  #tbl { min-width: 0; }
  #tbl thead { display: none; }
  #tbl tbody tr { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 10px; padding: 12px 2px; border-bottom: 1px solid var(--line); }
  #tbl td { border: 0; padding: 0; }
  #tbl td.ck { width: auto; order: 0; }
  #tbl td.rank { order: 1; width: auto; }
  #tbl td.name { order: 2; flex: 1 1 calc(100% - 110px); white-space: normal; }
  #tbl td.name .sub { display: inline; margin-left: 6px; }
  #tbl td.fit { order: 3; display: flex; align-items: center; gap: 6px; }
  #tbl td.fit .bar { margin: 0; }
  #tbl td.pc, #tbl td.num { order: 4; font-size: 12.5px; }
  #tbl td.num[data-l]::before { content: attr(data-l) " "; font: 500 10.5px var(--f-mono); letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
  #tbl td.gfn { display: none; }
  #cmpTbl th.attr, #cmpTbl td.attr { width: 104px; position: sticky; left: 0; z-index: 1; background: var(--surface); }
  .tray { padding-block: 8px; }
  .tray .names { flex-wrap: nowrap; overflow-x: auto; flex-basis: 100%; order: 1; }
  .tray .in > .lbl { display: none; }
  .tray .btn { order: 2; }
  .wrap.has-tray { padding-bottom: 130px; }
  section.panel { padding: 14px; }
  aside.dossier { padding: 16px; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
</style>

<div class="wrap" id="wrap">
  <header class="top">
    <div class="titlebar">
      <h1>Charity Registration Atlas</h1>
      <div class="hlinks">
        <a class="btn ghost" href="https://github.com/OpenCharity-org/OpenCharity" target="_blank" rel="noopener">GitHub</a>
        <a class="btn ghost" href="https://github.com/OpenCharity-org/OpenCharity/raw/main/charities_by_country_v2.csv" target="_blank" rel="noopener">CSV</a>
        <a class="btn ghost" href="https://github.com/OpenCharity-org/OpenCharity/raw/main/charities_by_country_v2.xlsx" target="_blank" rel="noopener">Excel</a>
        <button type="button" class="btn ghost" id="theme" aria-label="Switch colour theme">Theme</button>
      </div>
    </div>
    <p>How hard it is to register a charity in __COUNT__ jurisdictions, judged for a founder living in Australia with no ties to the country, plus whether you can open a personal bank account there as a non-resident. Stack as many filters as you like, rank by what matters to you, and tick countries to benchmark them side by side.</p>
  </header>

  <form class="controls" id="controls" aria-label="Rank and filter">
    <div class="row">
      <label class="field rank"><span>Rank by</span><select id="rankby"></select></label>
      <label class="field grow"><span>Search</span><input id="q" type="search" placeholder="Country, law, entity type…"></label>
      <label class="field numf"><span>Max fee (US$)</span><input id="maxfee" type="number" min="0" step="10" inputmode="numeric" placeholder="No limit"></label>
      <label class="field numf"><span>Max time (days)</span><input id="maxdays" type="number" min="0" step="1" inputmode="numeric" placeholder="No limit"></label>
      <span class="count" id="count"></span>
      <button type="button" class="btn ftoggle" id="ftoggle" aria-expanded="false" aria-controls="fbody">Filters</button>
    </div>
    <div class="weights" id="weights" hidden></div>
    <div class="fbody" id="fbody">
      <div class="facets" id="facets"></div>
      <details class="more" id="moreFacets"><summary>Region, Google for Nonprofits and confidence</summary><div class="facets" id="facets2"></div></details>
    </div>
    <div class="row">
      <div class="active" id="active" aria-live="polite"></div>
      <button type="button" class="btn link" id="reset">Clear all filters</button>
    </div>
  </form>

  <div class="main">
    <div class="mapcol">
      <div class="modes" role="group" aria-label="Colour the map by" id="modes"></div>
      <div class="mapcard">
        <svg id="map" viewBox="0 0 960 500" role="img" aria-label="World map of charity registration conditions"></svg>
        <div class="zoom"><button type="button" id="zin" aria-label="Zoom in">+</button><button type="button" id="zout" aria-label="Zoom out">−</button><button type="button" id="zreset" aria-label="Reset view">⟲</button></div>
        <div class="legend" id="legend"></div>
        <div class="tip" id="tip" hidden></div>
      </div>
    </div>
    <aside class="dossier" id="dossier" aria-live="polite"></aside>
  </div>

  <section class="panel" id="compare" hidden>
    <div class="phead">
      <h2>Benchmark</h2>
      <p class="cmpnote"><span class="key"></span>best among the countries you picked. The grey column is the median of the <span id="benchN"></span> countries your filters match.</p>
    </div>
    <div class="tablewrap"><table id="cmpTbl"></table></div>
  </section>

  <section class="panel">
    <div class="phead">
      <h2 id="rankTitle">Ranking</h2>
      <p id="rankNote"></p>
    </div>
    <div class="tablewrap"><table id="tbl">
      <thead><tr>
        <th><span class="lbl" title="Tick to benchmark">Cmp</span></th>
        <th data-k="rank"><button type="button">#</button></th>
        <th data-k="country"><button type="button">Country</button></th>
        <th data-k="fit" id="fitTh" hidden><button type="button">Fit</button></th>
        <th data-k="difficulty"><button type="button">Difficulty</button></th>
        <th data-k="no_presence"><button type="button">Remote founding</button></th>
        <th data-k="fee_lo"><button type="button">Fee (US$)</button></th>
        <th data-k="days_lo"><button type="button">Time</button></th>
        <th data-k="bank_cat"><button type="button">Charity bank</button></th>
        <th data-k="pb_status"><button type="button">Personal acct</button></th>
        <th data-k="pb_method"><button type="button">Personal remote?</button></th>
        <th data-k="pb_year"><button type="button">Acct fees/yr</button></th>
        <th data-k="funding_cat"><button type="button">Foreign funding</button></th>
        <th data-k="gfn"><button type="button">Google NP</button></th>
      </tr></thead>
      <tbody></tbody>
    </table></div>
  </section>

  <footer>
    <p>Source: <span class="mono">__SRC__</span>, researched against registries, gazettes and NGO-law texts, re-verified October 2026. Difficulty and remote founding are judged for an Australian-resident founder with no local presence.</p>
    <p>Filters: click an option once to include it, twice to exclude it, and a third time to clear it. Included options inside one group widen the match (any of them); separate groups narrow it (all must hold); excluded options are always left out. The number on each option is how many countries you would get by adding it. Fee uses the lowest US$ figure in each country's fee note; a few notes include agent or notary costs, so read the full note. Time uses the shortest stated duration. Countries with no published fee or time fail a fee or time limit and rank last. "Best overall" weighs difficulty, remote founding, Google for Nonprofits eligibility and research confidence; "Your weights" uses the sliders. Bank-account groups are read from the research notes: "remote option" means at least one bank or licensed e-money provider onboards non-residents without a visit. "Personal account" is a separate question: whether a non-resident foreign individual (no local visa or address) can open a personal account at a licensed local bank; fintech options are listed in each dossier but don't count.</p>
    <p>This is research, not legal advice. Confirm with the registry before filing. Grey areas on the map are dependent territories (Puerto Rico, New Caledonia, the Faroe Islands and others); charities there register under the parent country's law, so use that country's entry.</p>
  </footer>
</div>

<div class="tray" id="tray" hidden>
  <div class="in">
    <span class="lbl">Benchmark</span>
    <div class="names" id="trayNames"></div>
    <button type="button" class="btn primary" id="trayGo">Compare</button>
    <button type="button" class="btn link" id="trayClear">Clear</button>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<script>
const DATA = __DATA__;
const GEO = __GEO__;
const ALIAS = __ALIAS__;
const POINTS = __POINTS__;

/* ---------- vocabularies ---------- */
const MODES = {
  difficulty: { label: "Difficulty", key: "difficulty", cats: [["easy", "Easy", "d1"], ["medium", "Medium", "d2"], ["hard", "Hard", "d3"], ["very hard", "Very hard", "d4"]] },
  remote: { label: "Remote founding", key: "no_presence", cats: [["yes", "Fully remote", "d1"], ["partial", "Partly remote", "d2"], ["no", "Must be present", "d4"]] },
  fee: { label: "Fee", key: "fee_bin", cats: [["free", "Free", "d1"], ["low", "$1–100", "d2"], ["mid", "$101–500", "d3"], ["high", "Over $500", "d4"], ["unknown", "Not published", "d0"]] },
  time: { label: "Time", key: "time_bin", cats: [["fast", "Up to 2 weeks", "d1"], ["month", "Up to a month", "d2"], ["quarter", "1–3 months", "d3"], ["slow", "Over 3 months", "d4"], ["unknown", "Not stated", "d0"]] },
  bank: { label: "Charity bank account", key: "bank_cat", cats: [["remote", "Remote option", "d1"], ["visit", "Branch visit", "d2"], ["blocked", "Effectively blocked", "d4"]] },
  pbank: { label: "Personal account (non-resident)", key: "pb_status", cats: [["yes", "Open to non-residents", "d1"], ["limited", "Limited", "d3"], ["no", "Residents only", "d4"]] },
  pbcost: { label: "Personal account cost", key: "pb_cost_bin", cats: [["free", "Free", "d1"], ["low", "Up to $60/yr", "d2"], ["mid", "$61–240/yr", "d3"], ["high", "Over $240/yr", "d4"], ["unknown", "Not published", "d0"]] },
  pbopen: { label: "Personal account opening", key: "pb_method", cats: [["remote", "Remote, no visit", "d1"], ["in-person", "Branch visit", "d2"], ["not available", "Not available", "d4"]] },
  funding: { label: "Foreign funding", key: "funding_cat", cats: [["open", "No notable limits", "d1"], ["restricted", "Restricted", "d3"]] },
  gfn: { label: "Google for Nonprofits", key: "gfn", cats: [["Yes", "Eligible", "d1"], ["No", "Not eligible", "d4"]] },
  confidence: { label: "Confidence", key: "confidence", cats: [["high", "High", "d1"], ["med", "Medium", "d2"]] },
};
const REGIONS = [...new Set(DATA.map(d => d.region))].sort();
// facet key -> {label, cats}; the first six show up front, the rest under "more"
const FACETS = {};
for (const m of Object.values(MODES)) FACETS[m.key] = { label: m.label, cats: m.cats };
FACETS.pb_dep_bin = { label: "Personal account minimum deposit", cats: [["none", "None", "d1"], ["low", "Up to $500", "d2"], ["mid", "$501–10k", "d3"], ["high", "Over $10k", "d4"], ["unknown", "Not published", "d0"]] };
FACETS.pb_res = { label: "Local residence needed (personal account)", cats: [["no", "No", "d1"], ["often", "Often", "d2"], ["yes", "Yes", "d4"]] };
FACETS.pb_diff = { label: "Personal banking difficulty", cats: MODES.difficulty.cats };
FACETS.region = { label: "Region", cats: REGIONS.map(r => [r, r, null]) };
const FRONT = ["difficulty", "no_presence", "fee_bin", "time_bin", "bank_cat", "funding_cat", "pb_status", "pb_method"];
const MORE = ["pb_cost_bin", "pb_dep_bin", "pb_res", "pb_diff", "region", "gfn", "confidence"];

const LABEL = {}; for (const [k, f] of Object.entries(FACETS)) for (const [v, l, c] of f.cats) LABEL[k + ":" + v] = [l, c];
const ORDER = { difficulty: ["easy", "medium", "hard", "very hard"], no_presence: ["yes", "partial", "no"], gfn: ["Yes", "No"],
  confidence: ["high", "med"], bank_cat: ["remote", "visit", "blocked"], funding_cat: ["open", "restricted"],
  pb_status: ["yes", "limited", "no"], pb_method: ["remote", "in-person", "not available"], pb_res: ["no", "often", "yes"],
  pb_diff: ["easy", "medium", "hard", "very hard"] };
const DIFF_N = { easy: 0, medium: 1, hard: 2, "very hard": 3 };

const BIG = 1e12;
const ord = (k, d) => { const i = ORDER[k].indexOf(d[k]); return i < 0 ? 99 : i; };
const num = (v, desc) => v == null ? BIG : (desc ? -v : v);   // missing values always rank last

/* ---------- custom weights ---------- */
const WEIGHTS = [
  ["difficulty", "Ease of registering"], ["remote", "Remote founding"], ["fee", "Low fee"], ["time", "Speed"],
  ["bank", "Charity bank account"], ["pbank", "Personal account as non-resident"], ["pbcost", "Cheap personal account"], ["funding", "Open foreign funding"],
  ["gfn", "Google for Nonprofits"], ["conf", "Research confidence"],
];
const W_DEFAULT = { difficulty: 3, remote: 3, fee: 2, time: 2, bank: 2, pbank: 1, pbcost: 0, funding: 1, gfn: 1, conf: 1 };
const pct = key => { const v = DATA.filter(d => d[key] != null).map(d => d[key]).sort((a, b) => a - b);
  return x => { if (x == null) return 1; let i = 0; while (i < v.length && v[i] < x) i++; return v.length > 1 ? i / (v.length - 1) : 0; }; };
const feePct = pct("fee_lo"), dayPct = pct("days_lo"), pbYearPct = pct("pb_year");
// penalty 0 (best) .. 1 (worst) per factor
const PEN = {
  difficulty: d => (DIFF_N[d.difficulty] ?? 3) / 3,
  remote: d => ({ yes: 0, partial: .5, no: 1 })[d.no_presence] ?? 1,
  fee: d => feePct(d.fee_lo),
  time: d => dayPct(d.days_lo),
  bank: d => ({ remote: 0, visit: .5, blocked: 1 })[d.bank_cat] ?? 1,
  pbank: d => (({ yes: 0, limited: .5, no: 1 })[d.pb_status] ?? 1) * .7 + (({ remote: 0, "in-person": .5, "not available": 1 })[d.pb_method] ?? 1) * .3,
  pbcost: d => pbYearPct(d.pb_year),
  funding: d => d.funding_cat === "open" ? 0 : 1,
  gfn: d => d.gfn === "Yes" ? 0 : 1,
  conf: d => d.confidence === "high" ? 0 : .5,
};
let W = { ...W_DEFAULT };
const fit = d => { let s = 0, t = 0; for (const k in W) { s += W[k] * PEN[k](d); t += W[k]; } return t ? Math.round(100 * (1 - s / t)) : 0; };

const RANKS = {
  overall:   { label: "Best overall", mode: "difficulty", note: "Easiest, most remote-friendly first; ties broken by fee, then time.", key: d => [d.score, num(d.fee_lo), num(d.days_lo)] },
  custom:    { label: "Your weights", mode: null, note: "Fit score 0–100 from the sliders: each factor scores a country from best to worst, weighted by how much it matters to you.", key: d => [-fit(d), d.score] },
  easiest:   { label: "Easiest first", mode: "difficulty", note: "Easy → very hard; ties broken by remote founding, then fee.", key: d => [ord("difficulty", d), ord("no_presence", d), num(d.fee_lo)] },
  hardest:   { label: "Hardest first", mode: "difficulty", note: "Very hard → easy.", key: d => [-ord("difficulty", d), -ord("no_presence", d), d.country] },
  cheapest:  { label: "Cheapest to register", mode: "fee", note: "Lowest stated fee first (usually the government fee; some notes include agent or notary costs); unpublished fees last.", key: d => [num(d.fee_lo), num(d.fee_hi), ord("difficulty", d)] },
  priciest:  { label: "Most expensive fee", mode: "fee", note: "Highest stated fee first; unpublished fees last.", key: d => [num(d.fee_hi, true), num(d.fee_lo, true)] },
  fastest:   { label: "Fastest to register", mode: "time", note: "Shortest stated registration time first.", key: d => [num(d.days_lo), num(d.days_hi), ord("difficulty", d)] },
  slowest:   { label: "Slowest to register", mode: "time", note: "Longest stated registration time first.", key: d => [num(d.days_hi, true), num(d.days_lo, true)] },
  remote:    { label: "Most remote-friendly", mode: "remote", note: "Fully remote founding first, then easiest banking, then difficulty.", key: d => [ord("no_presence", d), ord("bank_cat", d), ord("difficulty", d)] },
  bank:      { label: "Easiest bank account", mode: "bank", note: "Remote opening possible → branch visit → effectively blocked.", key: d => [ord("bank_cat", d), ord("difficulty", d)] },
  pbank:     { label: "Easiest personal account (non-resident)", mode: "pbank", note: "Open to non-residents → limited → residents only; then remote opening first, then banking difficulty.", key: d => [ord("pb_status", d), ord("pb_method", d), ord("pb_diff", d), ord("pb_res", d)] },
  pbcheap:   { label: "Cheapest personal account", mode: "pbcost", note: "Lowest first-year fees (12 monthly fees + opening fee, US$) first, then lowest minimum deposit; unpublished fees last. Fee figures exist for about a third of countries, so check the cost note in each dossier.", key: d => [num(d.pb_year), num(d.pb_mindep), ord("pb_status", d)] },
  pbhard:    { label: "Hardest personal account", mode: "pbank", note: "Residents-only and closed banking systems first.", key: d => [-ord("pb_status", d), -ord("pb_diff", d), -ord("pb_method", d)] },
  funding:   { label: "Fewest funding limits", mode: "funding", note: "No notable foreign-funding restrictions first.", key: d => [ord("funding_cat", d), ord("difficulty", d)] },
  cheapfast: { label: "Cheap and fast", mode: "fee", note: "Sum of fee rank and time rank; both must be stated.", key: null },
  alpha:     { label: "A–Z", mode: null, note: "Alphabetical.", key: d => [d.country] },
};
(() => {
  const pos = f => { const s = DATA.filter(d => f(d) != null).sort((a, b) => f(a) - f(b)); const m = new Map(); s.forEach((d, i) => m.set(d.country, i)); return m; };
  const pf = pos(d => d.fee_lo), pt = pos(d => d.days_lo);
  RANKS.cheapfast.key = d => (pf.has(d.country) && pt.has(d.country)) ? [pf.get(d.country) + pt.get(d.country), ord("difficulty", d)] : [BIG];
})();

/* ---------- helpers ---------- */
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const slug = s => s.toLowerCase().normalize("NFD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const byName = new Map(DATA.map(d => [d.country, d]));
const geoName = new Map(DATA.map(d => [ALIAS[d.country] || d.country, d.country]));
const bySlug = new Map(DATA.map(d => [slug(d.country), d.country]));
const fmtUSD = v => v >= 1000 ? "$" + (v / 1000).toFixed(v % 1000 ? 1 : 0) + "k" : "$" + Math.round(v);
const usd = v => v == null ? "—" : v === 0 ? "Free" : fmtUSD(v);
const dep = v => v == null ? "—" : v === 0 ? "None" : fmtUSD(v);
const feeTxt = d => d.fee_lo == null ? "—" : d.fee_hi === 0 ? "Free" : d.fee_lo === d.fee_hi ? fmtUSD(d.fee_lo) : `${fmtUSD(d.fee_lo)}–${fmtUSD(d.fee_hi)}`;
const dur = n => n < 14 ? `${n} d` : n < 60 ? `${Math.round(n / 7)} wk` : n < 365 ? `${Math.round(n / 30)} mo` : `${(n / 365).toFixed(n % 365 ? 1 : 0)} yr`;
const timeTxt = d => { if (d.days_lo == null) return "—"; if (d.days_lo === d.days_hi) return dur(d.days_lo);
  const a = dur(d.days_lo).split(" "), b = dur(d.days_hi).split(" "); return a[1] === b[1] ? `${a[0]}–${b[0]} ${b[1]}` : `${a.join(" ")} – ${b.join(" ")}`; };
const store = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const load = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
const pill = (key, v) => { const l = LABEL[key + ":" + v]; return l ? `<span class="pill"><i class="c-${l[1]}"></i>${esc(l[0])}</span>` : esc(v); };

/* ---------- state ---------- */
let mode = "difficulty", selected = null, rankBy = "overall", colSort = [];   // [{k, dir}], first = highest priority
const F = Object.fromEntries(Object.keys(FACETS).map(k => [k, new Set()]));   // included options (any of them)
const X = Object.fromEntries(Object.keys(FACETS).map(k => [k, new Set()]));   // excluded options (none of them)
let CMP = [];
{
  const s = load("atlas-state") || {};
  if (MODES[s.mode]) mode = s.mode;
  if (RANKS[s.rankBy]) rankBy = s.rankBy;
  if (s.F) for (const k in s.F) if (F[k]) s.F[k].forEach(v => F[k].add(v));
  if (s.X) for (const k in s.X) if (X[k]) s.X[k].forEach(v => { if (!F[k].has(v)) X[k].add(v); });
  if (Array.isArray(s.cmp)) CMP = s.cmp.filter(c => byName.has(c)).slice(0, 6);
  if (s.W) for (const k in W) if (typeof s.W[k] === "number") W[k] = s.W[k];
  if (s.q) $("q").value = s.q;
  if (s.maxfee != null) $("maxfee").value = s.maxfee;
  if (s.maxdays != null) $("maxdays").value = s.maxdays;
}
const save = () => store("atlas-state", { mode, rankBy, cmp: CMP, W, q: $("q").value, maxfee: $("maxfee").value, maxdays: $("maxdays").value,
  F: Object.fromEntries(Object.entries(F).map(([k, s]) => [k, [...s]])), X: Object.fromEntries(Object.entries(X).map(([k, s]) => [k, [...s]])) });

$("rankby").innerHTML = Object.entries(RANKS).map(([k, r]) => `<option value="${k}">${esc(r.label)}</option>`).join("");
$("rankby").value = rankBy;

/* ---------- filtering ---------- */
const HAY = new Map(DATA.map(d => [d.country, [d.country, d.region, d.entity, d.requirements, d.bottleneck, d.notes, d.cost_time, d.tax_exempt, d.deduction, d.donor_restr, d.compliance, d.bank_access, d.pb_docs, d.pb_banks, d.pb_restr, d.pb_alt, d.pb_dep].join(" ").toLowerCase()]));
function passes(d, skip) {
  for (const k in F) if (k !== skip && ((F[k].size && !F[k].has(d[k])) || X[k].has(d[k]))) return false;
  const t = $("q").value.trim().toLowerCase();
  if (t && !HAY.get(d.country).includes(t)) return false;
  const mf = $("maxfee").value, md = $("maxdays").value;
  if (mf !== "" && (d.fee_lo == null || d.fee_lo > +mf)) return false;
  if (md !== "" && (d.days_lo == null || d.days_lo > +md)) return false;
  return true;
}
const matches = d => passes(d);

function renderFacets() {
  const draw = keys => keys.map(k => {
    const f = FACETS[k];
    const opts = f.cats.map(([v, l, c]) => {
      const n = DATA.filter(d => d[k] === v && passes(d, k)).length, on = F[k].has(v), off = X[k].has(v);
      const tip = on ? "Showing only these (with any others ticked). Click to exclude instead" : off ? "Excluded. Click to clear this filter" : "Click to show only these; click again to exclude; a third time to clear";
      return `<button type="button" class="opt${n ? "" : " zero"}${off ? " exc" : ""}" data-f="${k}" data-v="${esc(v)}" aria-pressed="${on ? "true" : off ? "mixed" : "false"}" title="${tip}" aria-label="${esc(l)}: ${on ? "included" : off ? "excluded" : "not filtered"}, ${n} countries">${c ? `<i class="sw c-${c}"></i>` : ""}${esc(l)} <span class="n">${n}</span></button>`;
    }).join("");
    return `<fieldset class="facet${k === "region" ? " wide" : ""}"><legend class="lbl">${esc(f.label)}${F[k].size ? ` · ${F[k].size} included` : ""}${X[k].size ? ` · ${X[k].size} excluded` : ""}</legend><div class="opts">${opts}</div></fieldset>`;
  }).join("");
  $("facets").innerHTML = draw(FRONT);
  $("facets2").innerHTML = draw(MORE);
  if (MORE.some(k => F[k].size || X[k].size)) $("moreFacets").open = true;
}

function renderActive() {
  const tags = [];
  for (const k in F) for (const v of F[k]) tags.push([`${FACETS[k].label}: ${LABEL[k + ":" + v]?.[0] ?? v}`, `f|${k}|${v}`]);
  for (const k in X) for (const v of X[k]) tags.push([`${FACETS[k].label}: not ${LABEL[k + ":" + v]?.[0] ?? v}`, `x|${k}|${v}`]);
  if ($("q").value.trim()) tags.push([`Search: “${$("q").value.trim()}”`, "q"]);
  if ($("maxfee").value !== "") tags.push([`Fee ≤ $${$("maxfee").value}`, "maxfee"]);
  if ($("maxdays").value !== "") tags.push([`Time ≤ ${$("maxdays").value} days`, "maxdays"]);
  // plain-language summary: every group applies at once
  const L = (k, v) => LABEL[k + ":" + v]?.[0] ?? v, parts = [];
  for (const k in F) { const inc = [...F[k]].map(v => L(k, v)), exc = [...X[k]].map(v => L(k, v));
    if (inc.length) parts.push(`${FACETS[k].label.toLowerCase()} is ${inc.join(" or ")}`);
    if (exc.length) parts.push(`${FACETS[k].label.toLowerCase()} is not ${exc.join(" or ")}`); }
  if ($("q").value.trim()) parts.push(`mentions “${$("q").value.trim()}”`);
  if ($("maxfee").value !== "") parts.push(`fee is at most $${$("maxfee").value}`);
  if ($("maxdays").value !== "") parts.push(`time is at most ${$("maxdays").value} days`);
  const n = DATA.filter(matches).length;
  $("active").innerHTML = tags.length
    ? `<span class="lbl">Active</span>` + tags.map(([t, id]) => `<span class="tag">${esc(t)}<button type="button" data-rm="${esc(id)}" aria-label="Remove ${esc(t)}">×</button></span>`).join("")
      + `<p class="summary">Showing <b>${n}</b> ${n === 1 ? "country" : "countries"} where ${parts.map(esc).join(" <b>and</b> ")}.</p>`
    : `<span class="none">No filters yet. Pick as many as you like: they all apply together. Click an option once to include it, twice to exclude it, three times to clear it.</span>`;
  $("reset").hidden = !tags.length;
  $("ftoggle").textContent = tags.length ? `Filters · ${tags.length}` : "Filters";
}

function renderWeights() {
  const show = rankBy === "custom";
  $("weights").hidden = !show;
  if (!show) return;
  $("weights").innerHTML = `<div class="whead"><span class="lbl">How much does each factor matter? (0 = ignore, 5 = critical)</span>
      <button type="button" class="btn link" id="wreset">Reset weights</button></div>` +
    WEIGHTS.map(([k, l]) => `<div class="wrow"><label for="w-${k}">${esc(l)} <output id="wo-${k}">${W[k]}</output></label>
      <input type="range" id="w-${k}" data-w="${k}" min="0" max="5" step="1" value="${W[k]}"></div>`).join("");
}

/* ---------- ranking ---------- */
const cmp = (a, b) => { for (let i = 0; i < Math.max(a.length, b.length); i++) { const x = a[i], y = b[i]; if (x === y) continue; if (x === undefined) return -1; if (y === undefined) return 1;
  if (typeof x === "string" || typeof y === "string") return String(x).localeCompare(String(y)); return x - y; } return 0; };
const ranked = () => { const kf = RANKS[rankBy].key; return [...DATA].sort((a, b) => cmp(kf(a), kf(b)) || a.country.localeCompare(b.country)); };
function colVal(d, k) {
  if (k === "rank") return rankPos.get(d.country);
  if (k === "fit") return -fit(d);
  if (ORDER[k]) return ord(k, d);
  if (k === "fee_lo" || k === "days_lo" || k === "pb_year") return d[k] == null ? BIG : d[k];
  return d[k].toLowerCase();
}

/* ---------- map ---------- */
const svg = d3.select("#map"), MW = 960, MH = 500;
const g = svg.append("g");
const feats = topojson.feature(GEO, GEO.objects.countries).features;
const proj = d3.geoNaturalEarth1().fitExtent([[6, 6], [MW - 6, MH - 6]], { type: "FeatureCollection", features: feats });
const path = d3.geoPath(proj);
const countries = g.append("g").selectAll("path").data(feats).join("path").attr("d", path);
const featOf = new Map(); feats.forEach(f => { const c = geoName.get(f.properties.name); if (c) featOf.set(c, f); });
const dotData = DATA.filter(d => POINTS[d.country] || path.area(featOf.get(d.country)) < 6).map(d => {
  const xy = POINTS[d.country] ? proj(POINTS[d.country]) : path.centroid(featOf.get(d.country));
  return { d, x: xy[0], y: xy[1] };
});
const dots = g.append("g").selectAll("circle").data(dotData).join("circle").attr("class", "dot").attr("cx", p => p.x).attr("cy", p => p.y).attr("r", 3.2);

let rankPos = new Map();
const tip = $("tip"), card = document.querySelector(".mapcard");
function showTip(ev, name) {
  const d = byName.get(name), r = card.getBoundingClientRect();
  tip.innerHTML = d ? `<b>${esc(d.country)}</b> · #${rankPos.get(d.country)} ${esc(RANKS[rankBy].label.toLowerCase())}${rankBy === "custom" ? ` (fit ${fit(d)})` : ""}<br>${esc(LABEL["difficulty:" + d.difficulty]?.[0] || d.difficulty)} · ${esc(LABEL["no_presence:" + d.no_presence]?.[0] || "")}<br>Fee ${esc(feeTxt(d))} · Time ${esc(timeTxt(d))}<br>Personal account: ${esc(LABEL["pb_status:" + d.pb_status]?.[0] || "")} · ${esc(LABEL["pb_method:" + d.pb_method]?.[0] || "")}`
                    : `<b>${esc(name)}</b><br>Not in dataset`;
  tip.hidden = false;
  const x = Math.max(8, Math.min(ev.clientX - r.left + 14, r.width - tip.offsetWidth - 8)), y = Math.max(ev.clientY - r.top - tip.offsetHeight - 10, 8);
  tip.style.left = x + "px"; tip.style.top = y + "px";
}
countries.on("mousemove", (ev, f) => showTip(ev, geoName.get(f.properties.name) || f.properties.name))
  .on("mouseleave", () => tip.hidden = true)
  .on("click", (ev, f) => { const c = geoName.get(f.properties.name); if (c) select(c, true); });
dots.on("mousemove", (ev, p) => showTip(ev, p.d.country)).on("mouseleave", () => tip.hidden = true)
  .on("click", (ev, p) => select(p.d.country, true));
const zoom = d3.zoom().scaleExtent([1, 14]).translateExtent([[0, 0], [MW, MH]]).on("zoom", ev => {
  g.attr("transform", ev.transform); dots.attr("r", 3.2 / Math.sqrt(ev.transform.k));
});
svg.call(zoom).on("dblclick.zoom", null);
$("zin").onclick = () => svg.transition().duration(250).call(zoom.scaleBy, 1.6);
$("zout").onclick = () => svg.transition().duration(250).call(zoom.scaleBy, 1 / 1.6);
$("zreset").onclick = () => svg.transition().duration(300).call(zoom.transform, d3.zoomIdentity);

/* ---------- render ---------- */
const cls = d => { const m = MODES[mode]; const c = m.cats.find(x => x[0] === d[m.key]); return c ? "c-" + c[2] : ""; };
function paint() {
  const list = ranked();
  rankPos = new Map(list.map((d, i) => [d.country, i + 1]));
  const cmpSet = new Set(CMP);
  countries.attr("class", f => { const c = geoName.get(f.properties.name); if (!c) return "country nodata";
    const d = byName.get(c); return `country ${cls(d)}${matches(d) ? "" : " dim"}${cmpSet.has(c) ? " cmp" : ""}${c === selected ? " sel" : ""}`; });
  dots.attr("class", p => `dot ${cls(p.d)}${matches(p.d) ? "" : " dim"}${cmpSet.has(p.d.country) ? " cmp" : ""}${p.d.country === selected ? " sel" : ""}`);
  dots.filter(p => p.d.country === selected || cmpSet.has(p.d.country)).raise();
  const m = MODES[mode], fs = F[m.key];
  $("legend").innerHTML = m.cats.map(([v, l, c]) =>
    `<button type="button" data-v="${esc(v)}" aria-pressed="${(!fs.size || fs.has(v)) && !X[m.key].has(v)}" title="Click to hide or show ${esc(l)}"><span class="sw c-${c}"></span>${esc(l)} <span class="n">${DATA.filter(d => d[m.key] === v).length}</span></button>`).join("");
  $("modes").innerHTML = Object.entries(MODES).map(([k, mm]) =>
    `<button type="button" data-m="${k}" aria-pressed="${k === mode}">${esc(mm.label)}</button>`).join("");
  renderFacets(); renderActive(); renderTable(list); renderCompare(); renderTray();
  save();
}

const tbody = document.querySelector("#tbl tbody");
function renderTable(list) {
  let rows = list.filter(matches);
  if (colSort.length) rows = [...rows].sort((a, b) => {
    for (const { k, dir } of colSort) { const x = colVal(a, k), y = colVal(b, k); if (x !== y) return (x < y ? -1 : 1) * dir; }
    return rankPos.get(a.country) - rankPos.get(b.country); });
  const custom = rankBy === "custom";
  $("fitTh").hidden = !custom;
  $("count").textContent = `${rows.length} of ${DATA.length} match`;
  $("rankTitle").textContent = `Ranked: ${RANKS[rankBy].label}`;
  const colName = k => document.querySelector(`#tbl th[data-k="${k}"] button`)?.textContent.replace(/[↑↓\d\s]+$/, "").trim() || k;
  $("rankNote").textContent = colSort.length
    ? `Sorted by ${colSort.map(({ k, dir }) => `${colName(k)} ${dir > 0 ? "↑" : "↓"}`).join(", then ")}, then ${RANKS[rankBy].label.toLowerCase()}. Click a header again to flip it, a third time to remove it; click # to clear all.`
    : RANKS[rankBy].note + " Click column headers to sort; click several to sort by more than one.";
  const cmpSet = new Set(CMP);
  tbody.innerHTML = rows.map(d => { const f = custom ? fit(d) : 0; return `<tr tabindex="0" data-c="${esc(d.country)}"${d.country === selected ? ' class="sel"' : ""}>
    <td class="ck"><input type="checkbox" data-cmp="${esc(d.country)}" aria-label="Benchmark ${esc(d.country)}"${cmpSet.has(d.country) ? " checked" : ""}${!cmpSet.has(d.country) && CMP.length >= 6 ? " disabled" : ""}></td>
    <td class="rank">#${rankPos.get(d.country)}</td>
    <td class="name">${esc(d.country)}<span class="sub">${esc(d.region)}</span></td>
    ${custom ? `<td class="fit"><b>${f}</b><span class="bar"><i style="width:${f}%"></i></span></td>` : ""}
    <td class="pc">${pill("difficulty", d.difficulty)}</td>
    <td class="pc">${pill("no_presence", d.no_presence)}</td>
    <td class="num" data-l="Fee" title="${esc(d.fee_usd)}">${esc(feeTxt(d))}</td>
    <td class="num" data-l="Time" title="${esc(d.time_to_reg)}">${esc(timeTxt(d))}</td>
    <td class="pc">${pill("bank_cat", d.bank_cat)}</td>
    <td class="pc" title="Personal account for non-residents · difficulty ${esc(d.pb_diff)}">${pill("pb_status", d.pb_status)}</td>
    <td class="pc" title="How a non-resident opens a personal account">${pill("pb_method", d.pb_method)}</td>
    <td class="num" data-l="Acct/yr" title="${esc(d.pb_costnote)}">${esc(usd(d.pb_year))}</td>
    <td class="pc">${pill("funding_cat", d.funding_cat)}</td>
    <td class="pc gfn">${pill("gfn", d.gfn)}</td></tr>`; }).join("")
    || `<tr><td colspan="14" class="empty">No jurisdictions match all these filters. Remove one of the active filters above.</td></tr>`;
  document.querySelectorAll("#tbl th[data-k]").forEach(th => th.setAttribute("aria-sort",
    colSort.length ? ((c => c ? (c.dir > 0 ? "ascending" : "descending") : "none")(colSort.find(c => c.k === th.dataset.k))) : (th.dataset.k === "rank" ? "ascending" : "none")));
  document.querySelectorAll("#tbl th[data-k]").forEach(th => { const i = colSort.findIndex(c => c.k === th.dataset.k);
    const b = th.querySelector("button"); if (b) b.dataset.pri = i >= 0 && colSort.length > 1 ? i + 1 : ""; });
}

/* ---------- benchmark ---------- */
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const mostCommon = (rows, k) => { const c = {}; rows.forEach(d => c[d[k]] = (c[d[k]] || 0) + 1); return Object.entries(c).sort((a, b) => b[1] - a[1])[0]?.[0]; };
function renderCompare() {
  const sec = $("compare");
  sec.hidden = !CMP.length;
  if (!CMP.length) return;
  const cs = CMP.map(c => byName.get(c)), pool = DATA.filter(matches);
  $("benchN").textContent = pool.length;
  const bench = { fee_lo: median(pool.map(d => d.fee_lo).filter(v => v != null)), days_lo: median(pool.map(d => d.days_lo).filter(v => v != null)) };
  // rows: [label, cell(d), sortValue(d) for "best" (lower is better) or null for text, bench text]
  const R = [
    ["Rank", d => `#${rankPos.get(d.country)} <span class="sub">${esc(RANKS[rankBy].label)}</span>`, d => rankPos.get(d.country), "—"],
    ...(rankBy === "custom" ? [["Fit score", d => `<b>${fit(d)}</b>`, d => -fit(d), String(median(pool.map(fit)) ?? "—")]] : []),
    ["Difficulty", d => pill("difficulty", d.difficulty), d => ord("difficulty", d), pill("difficulty", mostCommon(pool, "difficulty"))],
    ["Remote founding", d => pill("no_presence", d.no_presence), d => ord("no_presence", d), pill("no_presence", mostCommon(pool, "no_presence"))],
    ["Fee", d => esc(feeTxt(d)), d => num(d.fee_lo), bench.fee_lo == null ? "—" : fmtUSD(bench.fee_lo)],
    ["Time", d => esc(timeTxt(d)), d => num(d.days_lo), bench.days_lo == null ? "—" : dur(Math.round(bench.days_lo))],
    ["Charity bank account", d => pill("bank_cat", d.bank_cat), d => ord("bank_cat", d), pill("bank_cat", mostCommon(pool, "bank_cat"))],
    ["Personal account (non-resident)", d => pill("pb_status", d.pb_status), d => ord("pb_status", d), pill("pb_status", mostCommon(pool, "pb_status"))],
    ["Personal account opening", d => pill("pb_method", d.pb_method), d => ord("pb_method", d), pill("pb_method", mostCommon(pool, "pb_method"))],
    ["Personal account: first-year cost", d => esc(usd(d.pb_year)), d => num(d.pb_year), (v => v == null ? "—" : usd(v))(median(pool.map(d => d.pb_year).filter(v => v != null)))],
    ["Personal account: opening fee", d => esc(usd(d.pb_open)), d => num(d.pb_open), (v => v == null ? "—" : usd(v))(median(pool.map(d => d.pb_open).filter(v => v != null)))],
    ["Personal account: monthly fee", d => esc(usd(d.pb_month)), d => num(d.pb_month), (v => v == null ? "—" : usd(v))(median(pool.map(d => d.pb_month).filter(v => v != null)))],
    ["Personal account: min deposit", d => esc(dep(d.pb_mindep)), d => num(d.pb_mindep), (v => v == null ? "—" : dep(v))(median(pool.map(d => d.pb_mindep).filter(v => v != null)))],
    ["Personal banking difficulty", d => pill("pb_diff", d.pb_diff), d => ord("pb_diff", d), pill("pb_diff", mostCommon(pool, "pb_diff"))],
    ["Foreign funding", d => pill("funding_cat", d.funding_cat), d => ord("funding_cat", d), pill("funding_cat", mostCommon(pool, "funding_cat"))],
    ["Google for Nonprofits", d => pill("gfn", d.gfn), d => ord("gfn", d), pill("gfn", mostCommon(pool, "gfn"))],
    ["Confidence", d => pill("confidence", d.confidence), d => ord("confidence", d), pill("confidence", mostCommon(pool, "confidence"))],
    ["Entity", d => esc(d.entity), null, ""],
    ["Main bottleneck", d => esc(d.bottleneck), null, ""],
    ["Local requirements", d => esc(d.requirements), null, ""],
    ["Fee note", d => esc(d.fee_usd), null, ""],
    ["Time note", d => esc(d.time_to_reg), null, ""],
    ["Charity bank note", d => esc(d.bank_access), null, ""],
    ["Personal account: documents", d => esc(d.pb_docs), null, ""],
    ["Personal account: deposit & fees", d => esc(d.pb_dep), null, ""],
    ["Personal account: banks", d => esc(d.pb_banks), null, ""],
    ["Tax-exempt status", d => esc(d.tax_exempt), null, ""],
    ["Annual compliance", d => esc(d.compliance), null, ""],
  ];
  const head = `<thead><tr><th class="attr"></th>${cs.map(d => `<th><span class="cn"><a data-go="${esc(d.country)}">${esc(d.country)}</a><button type="button" data-uncmp="${esc(d.country)}" aria-label="Remove ${esc(d.country)} from benchmark">×</button></span></th>`).join("")}
    <th class="bench"><span class="cn">Filtered median</span></th></tr></thead>`;
  const body = R.map(([label, cell, sv, b]) => {
    let best = null;
    if (sv && cs.length > 1) { const vals = cs.map(sv); const mn = Math.min(...vals); if (mn < BIG && vals.some(v => v !== mn)) best = mn; }
    return `<tr class="${sv ? "" : "text"}"><td class="attr">${esc(label)}</td>${cs.map(d => `<td class="${best != null && sv(d) === best ? "best" : ""}">${cell(d) || "—"}</td>`).join("")}<td class="bench">${b}</td></tr>`;
  }).join("");
  $("cmpTbl").innerHTML = head + `<tbody>${body}</tbody>`;
}
function renderTray() {
  $("tray").hidden = !CMP.length;
  $("wrap").classList.toggle("has-tray", CMP.length > 0);
  $("trayNames").innerHTML = CMP.map(c => `<span class="tag">${esc(c)}<button type="button" data-uncmp="${esc(c)}" aria-label="Remove ${esc(c)}">×</button></span>`).join("")
    + (CMP.length < 6 ? `<span class="lbl" style="align-self:center">${6 - CMP.length} more allowed</span>` : "");
}
function toggleCmp(c, on) {
  const has = CMP.includes(c);
  if (on === undefined) on = !has;
  if (on && !has && CMP.length < 6) CMP.push(c);
  if (!on && has) CMP = CMP.filter(x => x !== c);
  const refocus = document.activeElement?.dataset?.cmp;
  paint(); if (selected) renderDossier();
  if (refocus) tbody.querySelector(`input[data-cmp="${CSS.escape(refocus)}"]`)?.focus();
}

/* ---------- events ---------- */
// each option cycles: off -> include -> exclude -> off
function toggleFacet(k, v) {
  if (F[k].has(v)) { F[k].delete(v); X[k].add(v); }
  else if (X[k].has(v)) X[k].delete(v);
  else F[k].add(v);
  paint();
}
$("controls").addEventListener("click", e => {
  const o = e.target.closest(".opt"); if (o) return toggleFacet(o.dataset.f, o.dataset.v);
  const rm = e.target.closest("[data-rm]"); if (rm) {
    const id = rm.dataset.rm;
    if (id.startsWith("f|") || id.startsWith("x|")) { const [t, k, v] = id.split("|"); (t === "f" ? F : X)[k].delete(v); } else $(id).value = "";
    return paint();
  }
  if (e.target.id === "wreset") { W = { ...W_DEFAULT }; renderWeights(); paint(); }
});
$("legend").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return;
  const k = MODES[mode].key, v = b.dataset.v, shown = (!F[k].size || F[k].has(v)) && !X[k].has(v);
  if (shown) { F[k].delete(v); X[k].add(v); } else { X[k].delete(v); if (F[k].size) F[k].add(v); }
  paint(); });
$("modes").addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; mode = b.dataset.m; paint(); });
$("rankby").addEventListener("change", () => { rankBy = $("rankby").value; colSort = [];
  const m = RANKS[rankBy].mode; if (m) mode = m; renderWeights(); paint(); if (selected) renderDossier(); });
$("controls").addEventListener("input", e => {
  if (e.target.dataset.w) { W[e.target.dataset.w] = +e.target.value; $("wo-" + e.target.dataset.w).textContent = e.target.value; }
  if (e.target.id !== "rankby") { paint(); if (selected && e.target.dataset.w) renderDossier(); }
});
$("controls").addEventListener("submit", e => e.preventDefault());
$("reset").addEventListener("click", () => { for (const k in F) { F[k].clear(); X[k].clear(); } ["q", "maxfee", "maxdays"].forEach(id => $(id).value = ""); paint(); });
document.querySelector("#tbl thead").addEventListener("click", e => { const th = e.target.closest("th[data-k]"); if (!th) return;
  const k = th.dataset.k;
  // each header cycles: ascending -> descending -> off; several can be active at once
  if (k === "rank") colSort = [];
  else { const c = colSort.find(x => x.k === k);
    if (!c) colSort.push({ k, dir: 1 }); else if (c.dir > 0) c.dir = -1; else colSort = colSort.filter(x => x !== c); }
  renderTable(ranked()); });
tbody.addEventListener("click", e => {
  const ck = e.target.closest("input[data-cmp]"); if (ck) { toggleCmp(ck.dataset.cmp, ck.checked); return; }
  const tr = e.target.closest("tr[data-c]"); if (tr) select(tr.dataset.c, true, true); });
tbody.addEventListener("keydown", e => { if (e.key === "Enter" && !e.target.matches("input")) { const tr = e.target.closest("tr[data-c]"); if (tr) select(tr.dataset.c, true, true); } });
document.addEventListener("click", e => {
  const u = e.target.closest("[data-uncmp]"); if (u) { toggleCmp(u.dataset.uncmp, false); return; }
  const go = e.target.closest("[data-go]"); if (go) { select(go.dataset.go, true); return; }
  const add = e.target.closest("[data-addcmp]"); if (add) toggleCmp(add.dataset.addcmp);
});
$("trayGo").addEventListener("click", () => $("compare").scrollIntoView({ behavior: "smooth", block: "start" }));
$("trayClear").addEventListener("click", () => { CMP = []; paint(); if (selected) renderDossier(); });

/* ---------- dossier ---------- */
let dossierOpen = window.matchMedia("(min-width: 981px)").matches;
const sec = (title, body) => body ? `<div class="sec"><h3>${esc(title)}</h3><p>${esc(body)}</p></div>` : "";
function renderDossier() {
  const d = byName.get(selected); if (!d) return;
  const notes = (d.notes || "").split(/\s+\|\s+/).filter(Boolean);
  const srcs = (d.sources || "").split(/\s*;\s*/).filter(s => /^https?:\/\//.test(s));
  const pbs = (d.pb_src || "").split(/\s*;\s*/).filter(s => /^https?:\/\//.test(s));
  const chip = (key, v) => { const l = LABEL[key + ":" + v]; return l ? `<span class="chip c-${l[1]}">${esc(l[0])}</span>` : ""; };
  const inCmp = CMP.includes(d.country);
  $("dossier").innerHTML = `
    <div class="dh"><div><div class="eyebrow">${esc(d.region)} · #${rankPos.get(d.country)} of ${DATA.length}, ${esc(RANKS[rankBy].label.toLowerCase())}${rankBy === "custom" ? ` · fit ${fit(d)}` : ""}</div><h2>${esc(d.country)}</h2></div>
      <button type="button" class="btn${inCmp ? "" : " primary"}" data-addcmp="${esc(d.country)}"${!inCmp && CMP.length >= 6 ? " disabled" : ""}>${inCmp ? "Remove from benchmark" : "Benchmark"}</button></div>
    <div class="chips">${chip("difficulty", d.difficulty)}${chip("no_presence", d.no_presence)}
      <span class="chip plain">Google for Nonprofits: ${d.gfn === "Yes" ? "eligible" : "not eligible"}</span>
      <span class="chip plain">Charity bank: ${esc(LABEL["bank_cat:" + d.bank_cat][0].toLowerCase())}</span>
      <span class="chip plain">Personal account: ${esc(LABEL["pb_status:" + d.pb_status]?.[0].toLowerCase() ?? "—")}, ${esc(LABEL["pb_method:" + d.pb_method]?.[0].toLowerCase() ?? "—")}</span>
      <span class="chip plain">Confidence: ${esc(d.confidence === "med" ? "medium" : d.confidence)}</span></div>
    <dl class="facts">
      <div><dt>Registration fee</dt><dd class="big">${esc(feeTxt(d))}</dd><dd>${esc(d.fee_usd || "—")}</dd></div>
      <div><dt>Time to register</dt><dd class="big">${esc(timeTxt(d))}</dd><dd>${esc(d.time_to_reg || "—")}</dd></div>
    </dl>
    ${sec("Entity to register", d.entity)}
    ${sec("Main bottleneck", d.bottleneck)}
    <details class="dmore" id="dmore"${dossierOpen ? " open" : ""}><summary>Requirements, banking (charity and personal), tax, compliance and sources</summary>
    ${sec("Local requirements", d.requirements)}
    ${sec("Cost and time in practice", d.cost_time)}
    ${sec("Charity bank account", d.bank_access)}
    ${sec("Tax-exempt status", d.tax_exempt)}
    ${sec("Donor tax deductions", d.deduction)}
    ${sec("Foreign funding rules", d.donor_restr)}
    ${sec("Annual compliance", d.compliance)}
    <div class="sec pb"><h3>Personal bank account as a non-resident</h3>
      <div class="chips">${chip("pb_status", d.pb_status)}${chip("pb_method", d.pb_method)}
        <span class="chip plain">Residence needed: ${esc(d.pb_res)}</span><span class="chip plain">Difficulty: ${esc(d.pb_diff)}</span>
        <span class="chip plain">Confidence: ${esc(d.pb_conf)}</span></div>
      <dl class="facts pbcost"><div><dt>Opening fee</dt><dd class="big">${esc(usd(d.pb_open))}</dd></div>
        <div><dt>Monthly fee</dt><dd class="big">${esc(usd(d.pb_month))}</dd></div>
        <div><dt>Min deposit</dt><dd class="big">${esc(dep(d.pb_mindep))}</dd></div>
        <div><dt>First year</dt><dd class="big">${esc(usd(d.pb_year))}</dd></div></dl>
      <p class="pbnote">${esc(d.pb_costnote)}</p>
      <dl class="pbl"><dt>Documents</dt><dd>${esc(d.pb_docs)}</dd><dt>Deposit &amp; fees</dt><dd>${esc(d.pb_dep)}</dd>
        <dt>Banks</dt><dd>${esc(d.pb_banks)}</dd><dt>Restrictions</dt><dd>${esc(d.pb_restr)}</dd><dt>Alternatives</dt><dd>${esc(d.pb_alt)}</dd></dl>
      ${pbs.length ? `<p class="pbsrc">${pbs.map((s, i) => `<a href="${esc(s)}" target="_blank" rel="noopener">source ${i + 1}</a>`).join(" · ")}</p>` : ""}</div>
    ${notes.length ? `<div class="sec"><h3>Research notes</h3><ul>${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>` : ""}
    ${srcs.length ? `<div class="sec src"><h3>Sources</h3><ul>${srcs.map(s => `<li><a href="${esc(s)}" target="_blank" rel="noopener">${esc(s.replace(/^https?:\/\/(www\.)?/, ""))}</a></li>`).join("")}</ul></div>` : ""}
    </details>`;
  $("dmore").addEventListener("toggle", e => { dossierOpen = e.target.open; });
}
function select(name, user, fromTable) {
  if (!byName.has(name)) return;
  selected = name;
  paint(); renderDossier();
  $("dossier").scrollTop = 0;
  if (user) {
    try { history.replaceState(null, "", "#" + slug(name)); } catch (e) {}
    const narrow = window.matchMedia("(max-width: 980px)").matches;
    if (fromTable || narrow) $(narrow ? "dossier" : "map").scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

$("ftoggle").addEventListener("click", () => {
  const open = !$("controls").classList.contains("open");
  $("controls").classList.toggle("open", open); $("ftoggle").setAttribute("aria-expanded", open);
});
const THEMES = ["system", "light", "dark"];
let theme = load("atlas-theme"); if (!THEMES.includes(theme)) theme = "system";
function applyTheme() {
  if (theme === "system") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", theme);
  $("theme").textContent = { system: "Theme: auto", light: "Theme: light", dark: "Theme: dark" }[theme];
}
$("theme").addEventListener("click", () => { theme = THEMES[(THEMES.indexOf(theme) + 1) % 3]; store("atlas-theme", theme); applyTheme(); });
applyTheme();

renderWeights();
const start = bySlug.get((location.hash || "").slice(1)) || ranked().filter(matches)[0]?.country || ranked()[0].country;
select(start, false);
</script>
"""

if __name__ == "__main__":
    main()
