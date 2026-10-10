#!/usr/bin/env python3
"""Build the OpenCharity site: webapp/atlas.html (artifact fragment) and docs/index.html (GitHub Pages).

One site, five sections, one country page (see the "OpenCharity UI & Navigation Plan"):
  #/                 Home: three entry questions, top 5, search
  #/map[/<slug>]     world map coloured by charity score or any attribute; click a country
                     for its page in a side panel (a preview sheet on phones)
  #/rankings/<key>   five ranking tabs + "More ways to rank" (incl. your own weights)
  #/compare/a,b,...  up to 5 countries in colour-coded cells
  #/banking/<key>    map + list for personal bank accounts as a non-resident
  #/country/<slug>   full country page: summary card + tabs (Registering, Banking,
                     Tax and compliance, Sources)
  #/about            scoring, colour key, plain-words glossary, research, downloads
Filters (slide-in panel), ranking and map colouring live in the URL query (?f=…&q=…&fee=…&days=…&mode=…).

Charity score (0-100) = registration ease 25 + set up without visiting 20 + fee 10 + speed 10
+ charity bank account 10 + personal account 10 + open foreign funding 5 + Google for Nonprofits 10.

Inputs: charities_by_country_v2.csv, banking_by_country.csv (via build_atlas helpers),
webapp/geo/countries-50m.json, webapp/flags/*.svg (country-flag-icons, MIT).
"""
import json
from pathlib import Path

from build_atlas import ALIAS, GEO, POINTS, add_banking, enrich
from build_webapp import build_data
from iso2 import ISO2, SOMALILAND_SVG

BASE = Path(__file__).parent
FLAGS = BASE / "webapp" / "flags"
OUT = BASE / "webapp" / "atlas.html"
DOCS = BASE / "docs" / "index.html"
REPO = "https://github.com/OpenCharity-org/OpenCharity"
SITE = "https://opencharity-org.github.io/OpenCharity/"


def main():
    data, src_name = build_data()
    data = [enrich(d) for d in data]
    add_banking(data)
    flags = {}
    for d in data:
        d.pop("score", None)
        code = ISO2[d["country"]].lower() or "xs"
        d["iso"] = code
        svg = SOMALILAND_SVG if code == "xs" else (FLAGS / f"{code}.svg").read_text(encoding="utf-8")
        flags[code] = " ".join(svg.split())
    geo = json.loads(GEO.read_text(encoding="utf-8"))
    geo["objects"]["countries"]["geometries"] = [
        g for g in geo["objects"]["countries"]["geometries"] if g["properties"]["name"] != "Antarctica"]
    names = {g["properties"]["name"] for g in geo["objects"]["countries"]["geometries"]}
    missing = [d["country"] for d in data if ALIAS.get(d["country"], d["country"]) not in names and d["country"] not in POINTS]
    if missing:
        raise SystemExit(f"no map shape for: {missing}")

    def js(obj):
        return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = (TEMPLATE.replace("__DATA__", js(data)).replace("__GEO__", js(geo)).replace("__ALIAS__", js(ALIAS))
            .replace("__POINTS__", js(POINTS)).replace("__FLAGS__", js(flags)).replace("__COUNT__", str(len(data)))
            .replace("__REPO__", REPO).replace("__SRC__", src_name))
    OUT.write_text(html, encoding="utf-8")
    head, body = html.split('<a class="skip"', 1)
    DOCS.parent.mkdir(exist_ok=True)
    DOCS.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                    f'<meta name="description" content="Where can you register a charity from Australia? {len(data)} countries ranked and '
                    'compared: rules, fees, timelines, bank accounts and sources.">\n'
                    '<meta property="og:title" content="OpenCharity: Charity Registration Atlas">\n'
                    f'<meta property="og:description" content="Map, rank and compare {len(data)} jurisdictions by how easy it is to '
                    'register a charity and open a bank account from Australia.">\n'
                    '<meta property="og:image" content="https://raw.githubusercontent.com/OpenCharity-org/OpenCharity/main/docs/screenshots/map.png">\n'
                    f'<meta property="og:url" content="{SITE}">\n'
                    '<meta name="twitter:card" content="summary_large_image">\n'
                    + head + '</head>\n<body>\n<a class="skip"' + body + '\n</body>\n</html>\n', encoding="utf-8")
    (DOCS.parent / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {OUT} and {DOCS} ({len(data)} jurisdictions, {len(html) // 1024} KB)")


TEMPLATE = r"""<title>OpenCharity: Charity Registration Atlas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* One site, five sections. Calm by default: each section shows one task; filters, details and
   extra rankings sit one click away. One score scale (6 steps) and one status scale (4 + grey),
   each with symbols. Light/dark follow the system unless the visitor picks. */
:root {
  --bg: #f3f5f6; --surface: #ffffff; --surface-2: #eef2f4; --ink: #16212a; --muted: #56656f; --line: #d6dee2;
  --accent: #1d5d86; --accent-soft: #e2eef6; --focus: #1d5d86; --sea: #dde7ec; --land-none: #c9d2d6;
  --ok: #1d9a47; --mid: #2a6dd4; --warn: #d9760a; --bad: #cc2d33; --na: #85939a;
  --b5: #1a9850; --b4: #66bd63; --b3: #a6d96a; --b2: #fdd257; --b1: #fc8d59; --b0: #d73027;
  --s1: #3b82f6; --s2: #10b981; --s3: #f59e0b; --s4: #a855f7;
  --shadow: 0 10px 30px rgba(20, 35, 45, .16);
  --f-display: "Bricolage Grotesque", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --f-body: "Public Sans", "Helvetica Neue", Arial, system-ui, sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #0e151a; --surface: #152027; --surface-2: #1b2830; --ink: #e3ebef; --muted: #96a7b1; --line: #27353e;
  --accent: #78b6e0; --accent-soft: #1b3445; --focus: #78b6e0; --sea: #111c23; --land-none: #2c3942;
  --ok: #2fb260; --mid: #5590ec; --warn: #ec8f2b; --bad: #e0494f; --na: #5f6e77;
  --shadow: 0 12px 30px rgba(0, 0, 0, .45); color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #0e151a; --surface: #152027; --surface-2: #1b2830; --ink: #e3ebef; --muted: #96a7b1; --line: #27353e;
  --accent: #78b6e0; --accent-soft: #1b3445; --focus: #78b6e0; --sea: #111c23; --land-none: #2c3942;
  --ok: #2fb260; --mid: #5590ec; --warn: #ec8f2b; --bad: #e0494f; --na: #5f6e77;
  --shadow: 0 12px 30px rgba(0, 0, 0, .45); color-scheme: dark; }

* { box-sizing: border-box; }
[hidden] { display: none !important; }
html, body { margin: 0; }
body { background: var(--bg); color: var(--ink); font: 15px/1.55 var(--f-body); -webkit-font-smoothing: antialiased; }
a { color: var(--accent); }
button, input, select { font: inherit; color: inherit; }
:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; border-radius: 4px; }
h1, h2, h3 { font-family: var(--f-display); line-height: 1.15; margin: 0; }
.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.skip { position: absolute; left: 8px; top: -60px; background: var(--accent); color: #fff; padding: 8px 12px; border-radius: 6px; z-index: 100; }
.skip:focus { top: 8px; }
.lbl { font: 500 11px var(--f-mono); letter-spacing: .07em; text-transform: uppercase; color: var(--muted); }
.btn { display: inline-flex; align-items: center; gap: 6px; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 7px 12px; font-weight: 600; font-size: 14px; cursor: pointer; text-decoration: none; color: var(--ink); min-height: 38px; }
.btn:hover { border-color: var(--accent); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: var(--surface); }
.btn.link { background: none; border: 0; color: var(--accent); padding: 4px 6px; min-height: 0; }
.btn .n { background: var(--accent); color: var(--surface); border-radius: 999px; padding: 0 7px; font-size: 12px; }

/* ---------- top bar ---------- */
header.top { position: sticky; top: 0; z-index: 40; background: var(--surface); border-bottom: 1px solid var(--line); }
.topin { max-width: 1440px; margin: 0 auto; padding: 0 20px; height: 60px; display: flex; align-items: center; gap: 18px; }
.brand { display: flex; align-items: center; gap: 9px; text-decoration: none; color: var(--ink); font: 700 19px var(--f-display); flex: none; }
.brand svg { width: 26px; height: 26px; color: var(--accent); }
nav.sections { display: flex; gap: 2px; align-self: stretch; }
nav.sections a { display: flex; align-items: center; padding: 0 12px; text-decoration: none; color: var(--muted); font-weight: 600; font-size: 14.5px; border-bottom: 3px solid transparent; }
nav.sections a:hover { color: var(--ink); }
nav.sections a[aria-current="page"] { color: var(--ink); border-bottom-color: var(--accent); }
.search { position: relative; flex: 1; max-width: 380px; margin-left: auto; }
.search input { width: 100%; background: var(--surface-2); border: 1px solid var(--line); border-radius: 999px; padding: 8px 14px 8px 36px; font-size: 14.5px; }
.search svg { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); width: 16px; height: 16px; color: var(--muted); pointer-events: none; }
.search kbd { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font: 500 11px var(--f-mono); color: var(--muted); border: 1px solid var(--line); border-radius: 4px; padding: 0 5px; }
.results { position: absolute; left: 0; right: 0; top: calc(100% + 6px); background: var(--surface); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--shadow); padding: 6px; max-height: 60vh; overflow-y: auto; z-index: 50; }
.results a { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 8px; color: var(--ink); text-decoration: none; font-size: 14px; }
.results a:hover, .results a:focus-visible, .results a.hl { background: var(--surface-2); outline: none; }
.results a small { margin-left: auto; color: var(--muted); font-size: 12px; }
.results .grp { padding: 6px 10px 2px; }
.iconbtn { width: 38px; height: 38px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); display: grid; place-items: center; cursor: pointer; flex: none; }
.iconbtn svg { width: 18px; height: 18px; }
.checkbtn { flex: none; }
.mobsearch { display: none; }

/* ---------- layout ---------- */
main { max-width: 1440px; margin: 0 auto; padding: 22px 20px 110px; }
.shead { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px 20px; flex-wrap: wrap; margin-bottom: 14px; }
.shead h1 { font-size: 30px; }
.shead p { margin: 4px 0 0; color: var(--muted); max-width: 70ch; }
.toolbar { display: flex; flex-wrap: wrap; gap: 8px 10px; align-items: center; margin: 0 0 12px; }
.count { font: 500 12.5px var(--f-mono); color: var(--muted); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { display: inline-flex; align-items: center; gap: 4px; background: var(--accent-soft); border-radius: 999px; padding: 2px 4px 2px 10px; font-size: 13px; }
.tag button { background: none; border: 0; cursor: pointer; color: var(--accent); font-size: 16px; line-height: 1; padding: 0 5px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 14px; }

/* ---------- chips, badges, bars ---------- */
.chip { display: inline-flex; align-items: center; gap: 5px; border-radius: 999px; padding: 2px 10px 2px 8px; font-size: 12.5px; font-weight: 600; color: #fff; white-space: nowrap; line-height: 1.5; }
.chip .y { font-weight: 800; }
.c-ok { background: var(--ok); } .c-mid { background: var(--mid); } .c-warn { background: var(--warn); } .c-bad { background: var(--bad); } .c-na { background: var(--na); }
.hatch { background-image: repeating-linear-gradient(45deg, rgba(255,255,255,.32) 0 3px, transparent 3px 7px); }
.badge { display: inline-block; min-width: 44px; text-align: center; border-radius: 7px; padding: 2px 7px; font: 700 16px var(--f-display); color: #14202a; }
.badge.lg { font-size: 28px; min-width: 70px; padding: 4px 10px; border-radius: 10px; }
.bg-b5 { background: var(--b5); color: #fff; } .bg-b4 { background: var(--b4); } .bg-b3 { background: var(--b3); } .bg-b2 { background: var(--b2); } .bg-b1 { background: var(--b1); } .bg-b0 { background: var(--b0); color: #fff; }
.parts { display: flex; height: 7px; border-radius: 4px; overflow: hidden; background: var(--surface-2); }
.parts i { display: block; height: 100%; }
.p0 { background: var(--s1); } .p1 { background: var(--s2); } .p2 { background: var(--s3); } .p3 { background: var(--s4); }
.flag { display: inline-block; width: 24px; aspect-ratio: 3 / 2; background-size: cover; background-position: center; border-radius: 3px; box-shadow: 0 0 0 1px rgba(0,0,0,.12); flex: none; vertical-align: -3px; }
.flag.lg { width: 48px; border-radius: 4px; }
.key { display: flex; flex-wrap: wrap; gap: 6px 14px; font-size: 13px; color: var(--muted); }
.key i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 5px; vertical-align: -1px; }

/* ---------- home ---------- */
.hero { text-align: center; padding: 34px 0 10px; }
.hero h1 { font-size: clamp(30px, 4.6vw, 48px); max-width: 20ch; margin: 0 auto; }
.hero p { color: var(--muted); font-size: 17px; max-width: 60ch; margin: 12px auto 0; }
.entries { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin: 30px 0; }
.entry { display: block; padding: 22px; text-decoration: none; color: var(--ink); transition: transform .12s, box-shadow .12s; }
.entry:hover, .entry:focus-visible { transform: translateY(-2px); box-shadow: var(--shadow); }
.entry .ic { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; background: var(--accent-soft); color: var(--accent); margin-bottom: 14px; }
.entry .ic svg { width: 24px; height: 24px; }
.entry h2 { font-size: 21px; }
.entry p { margin: 6px 0 0; color: var(--muted); font-size: 14.5px; }
.entry .go { display: inline-block; margin-top: 12px; font-weight: 600; color: var(--accent); }
.homegrid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr); gap: 16px; }
.homegrid .card { padding: 18px 20px; }
.homegrid h2 { font-size: 19px; margin-bottom: 10px; }
.top5 { list-style: none; margin: 0; padding: 0; }
.top5 li a { display: grid; grid-template-columns: 28px 28px minmax(0, 1fr) auto; align-items: center; gap: 10px; padding: 8px 4px; border-bottom: 1px solid var(--line); color: var(--ink); text-decoration: none; }
.top5 li:last-child a { border-bottom: 0; }
.top5 .r { font: 500 13px var(--f-mono); color: var(--muted); }
.stat3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 4px; }
.stat3 b { display: block; font: 700 28px var(--f-display); }
.stat3 span { font-size: 13px; color: var(--muted); }

/* ---------- map ---------- */
.mapwrap { position: relative; }
.mapcard { position: relative; overflow: hidden; background: var(--sea); border-radius: 14px; border: 1px solid var(--line); }
.mapcard svg { display: block; width: 100%; height: auto; }
path.cty { stroke: var(--surface); stroke-width: .45; cursor: pointer; }
path.cty.nodata { fill: var(--land-none); cursor: default; }
path.cty.dim, circle.dot.dim { opacity: .2; }
path.cty:hover { stroke: var(--ink); stroke-width: .9; }
path.cty.sel, circle.dot.sel { stroke: var(--ink); stroke-width: 2; }
circle.dot { stroke: var(--surface); stroke-width: .7; cursor: pointer; }
.zoom { position: absolute; left: 12px; top: 12px; display: grid; gap: 6px; z-index: 3; }
.zoom button { width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--line); background: var(--surface); font-size: 18px; font-weight: 700; cursor: pointer; }
.tip { position: absolute; pointer-events: none; z-index: 5; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 8px 11px; font-size: 13px; max-width: 260px; box-shadow: var(--shadow); }
.legend { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; align-items: center; }
.leg { display: inline-flex; align-items: center; gap: 6px; background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px 11px 3px 6px; font-size: 13px; cursor: pointer; }
.leg i { width: 14px; height: 14px; border-radius: 4px; }
.leg .n { color: var(--muted); font: 500 11.5px var(--f-mono); }
.leg[aria-pressed="true"] { border-color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
.modesel { display: inline-flex; align-items: center; gap: 8px; }
select.sel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; font-size: 14px; min-height: 38px; }
.listtoggle[aria-pressed="true"] { background: var(--accent-soft); border-color: var(--accent); }

/* side panel (country on the map) */
.cpanel { position: absolute; top: 12px; right: 12px; bottom: 12px; width: min(440px, calc(100% - 24px)); background: var(--surface); border: 1px solid var(--line); border-radius: 14px; box-shadow: var(--shadow); overflow-y: auto; z-index: 6; }
.cpanel .close { position: sticky; top: 8px; float: right; margin: 8px 8px 0 0; z-index: 2; }
.mapwrap.withpanel .mapcard { min-height: 560px; }
#bankMap svg { max-height: 430px; margin: 0 auto; }

/* ---------- filter panel ---------- */
.scrim { position: fixed; inset: 0; background: rgba(10, 18, 24, .45); z-index: 60; }
.fpanel { position: fixed; z-index: 61; left: 0; top: 0; bottom: 0; width: min(380px, 100%); background: var(--surface); border-right: 1px solid var(--line); box-shadow: var(--shadow); display: flex; flex-direction: column; }
.fpanel header { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-bottom: 1px solid var(--line); }
.fpanel header h2 { font-size: 20px; }
.fbody { flex: 1; overflow-y: auto; padding: 6px 16px 16px; }
.fgroup { padding: 12px 0; border-bottom: 1px solid var(--line); }
.fgroup > h3 { font: 700 13px var(--f-body); text-transform: uppercase; letter-spacing: .05em; color: var(--accent); margin-bottom: 8px; }
.facet { border: 0; margin: 0 0 10px; padding: 0; }
.facet legend { font-weight: 600; font-size: 14px; margin-bottom: 5px; padding: 0; }
.opts { display: flex; flex-wrap: wrap; gap: 5px; }
.opt { display: inline-flex; align-items: center; gap: 6px; background: var(--surface-2); border: 1px solid var(--line); border-radius: 999px; padding: 4px 11px 4px 8px; font-size: 13px; cursor: pointer; min-height: 32px; }
.opt i { width: 10px; height: 10px; border-radius: 50%; }
.opt .n { color: var(--muted); font: 500 11.5px var(--f-mono); }
.opt[aria-pressed="true"] { background: var(--accent-soft); border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }
.opt.zero { opacity: .45; }
.limits { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.limits label, .ftext label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 3px; }
.limits input, .ftext input { width: 100%; background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; }
.fpanel footer { display: flex; gap: 10px; padding: 12px 16px; border-top: 1px solid var(--line); }
.fpanel footer .primary { flex: 1; justify-content: center; }

/* ---------- rankings ---------- */
.tabs { display: flex; flex-wrap: wrap; gap: 4px; border-bottom: 1px solid var(--line); margin-bottom: 12px; }
.tabs button, .tabs select { background: none; border: 0; border-bottom: 3px solid transparent; padding: 9px 12px; font-weight: 600; font-size: 14.5px; color: var(--muted); cursor: pointer; }
.tabs button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent); }
.tabs select { border: 1px solid var(--line); border-radius: 8px; margin: 3px 0 6px auto; padding: 6px 10px; }
.tabs select.on { color: var(--ink); border-color: var(--accent); }
.rnote { color: var(--muted); font-size: 14px; margin: 0 0 10px; }
.rlist { list-style: none; margin: 0; padding: 0; }
.rrow { display: grid; grid-template-columns: 52px minmax(0, 1fr) minmax(0, 170px) auto 54px 40px; gap: 14px; align-items: center; padding: 10px 12px; border-bottom: 1px solid var(--line); cursor: pointer; }
.rrow:hover, .rrow:focus-visible { background: var(--surface-2); }
.rrow .rk { font: 500 14px var(--f-mono); color: var(--muted); }
.rrow .who { display: flex; align-items: center; gap: 12px; min-width: 0; }
.rrow .nm { font-weight: 600; font-size: 15.5px; min-width: 0; }
.rrow .nm small { display: block; color: var(--muted); font-weight: 400; font-size: 12.5px; }
.rrow .nm .parts { margin-top: 5px; max-width: 220px; }
.rrow .met { font-size: 14px; font-weight: 600; text-align: right; }
.rrow .ch { display: flex; gap: 4px; flex-wrap: wrap; justify-content: flex-end; }
.addc { width: 34px; height: 34px; border-radius: 50%; border: 1.5px solid var(--accent); background: none; color: var(--accent); font-weight: 700; font-size: 17px; cursor: pointer; line-height: 1; }
.addc[aria-pressed="true"] { background: var(--accent); color: var(--surface); }
.addc:disabled { opacity: .3; cursor: not-allowed; }
.weights { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px 18px; padding: 14px 16px; margin-bottom: 12px; }
.weights label { display: flex; justify-content: space-between; font-size: 13.5px; font-weight: 600; }
.weights input { width: 100%; accent-color: var(--accent); }

/* ---------- compare ---------- */
.cmpwrap { overflow-x: auto; }
table.cmp { border-collapse: separate; border-spacing: 0; width: 100%; min-width: 760px; table-layout: fixed; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
table.cmp col.l { width: 220px; }
table.cmp th, table.cmp td { border-bottom: 1px solid var(--line); padding: 0; }
table.cmp .l { position: sticky; left: 0; z-index: 2; background: var(--surface); text-align: left; padding: 10px 14px; font-weight: 600; font-size: 13.5px; }
.chead { padding: 14px 10px 10px; text-align: center; }
.chead a { color: var(--ink); text-decoration: none; font: 700 16px var(--f-display); display: block; margin: 6px 0; }
.chead .rm { background: none; border: 0; color: var(--muted); cursor: pointer; font-size: 13px; }
.chead input { width: 100%; border: 1px dashed var(--line); border-radius: 8px; padding: 9px 10px; background: var(--bg); text-align: center; }
td.cell { text-align: center; padding: 7px 8px !important; color: #fff; font-size: 13px; font-weight: 600; position: relative; }
td.cell .v { display: block; font-weight: 400; font-size: 12px; opacity: .95; }
td.cell.blank { background: transparent; }
td.cell .info { position: absolute; right: 5px; top: 5px; width: 20px; height: 20px; border-radius: 50%; border: 0; background: rgba(255,255,255,.9); color: #14202a; font: italic 700 12px Georgia, serif; cursor: pointer; }
tr.grp td { background: var(--surface-2); font: 700 12px var(--f-body); text-transform: uppercase; letter-spacing: .06em; color: var(--accent); padding: 7px 14px !important; }
td.txt { font-size: 13px; padding: 9px 12px !important; vertical-align: top; }
td.txt .clamp { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
td.txt.open .clamp { -webkit-line-clamp: unset; }
tr.textrow { cursor: pointer; }
.cmptools { display: flex; flex-wrap: wrap; gap: 10px 16px; align-items: center; margin-bottom: 12px; }
.switch { display: inline-flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; cursor: pointer; }
.switch input { width: 18px; height: 18px; accent-color: var(--accent); }
.notebox { position: fixed; z-index: 70; max-width: 360px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; font-size: 13.5px; box-shadow: var(--shadow); }
.notebox b { display: block; margin-bottom: 4px; }
.empty { padding: 36px 16px; text-align: center; color: var(--muted); }

/* ---------- country page ---------- */
.crumbs { font-size: 13.5px; color: var(--muted); margin-bottom: 10px; }
.crumbs a { color: var(--muted); }
.cgrid { display: grid; grid-template-columns: minmax(0, 380px) minmax(0, 1fr); gap: 18px; align-items: start; }
.summary { padding: 18px; }
.summary .hd { display: flex; align-items: center; gap: 12px; }
.summary h1, .summary h2.t { font-size: 28px; }
.summary .sub { color: var(--muted); font-size: 13.5px; }
.summary .scorerow { display: flex; align-items: center; gap: 12px; margin: 14px 0 6px; }
.summary .scorerow p { margin: 0; font-size: 13.5px; color: var(--muted); }
.verdicts { list-style: none; margin: 12px 0; padding: 0; display: grid; gap: 6px; }
.verdicts li { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 10px; font-size: 14px; }
.verdicts li .vl { color: var(--muted); }
.facts2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 12px 0; }
.facts2 div { background: var(--surface-2); border-radius: 10px; padding: 10px 12px; }
.facts2 b { display: block; font: 700 20px var(--f-display); }
.facts2 span { font-size: 12.5px; color: var(--muted); }
.cacts { display: flex; gap: 8px; flex-wrap: wrap; }
.ctabs { display: flex; gap: 2px; border-bottom: 1px solid var(--line); overflow-x: auto; scrollbar-width: none; }
.ctabs button { background: none; border: 0; border-bottom: 3px solid transparent; padding: 10px 14px; font-weight: 600; font-size: 14.5px; color: var(--muted); cursor: pointer; white-space: nowrap; }
.ctabs button[aria-selected="true"] { color: var(--ink); border-bottom-color: var(--accent); }
.tabbody { padding: 6px 18px 18px; }
.sec { padding: 12px 0; border-bottom: 1px solid var(--line); }
.sec:last-child { border-bottom: 0; }
.sec h3 { font: 700 15px var(--f-body); margin-bottom: 3px; }
.sec p { margin: 0; font-size: 14.5px; overflow-wrap: anywhere; }
.sec ul { margin: 4px 0 0; padding-left: 18px; font-size: 14px; }
.sec li { margin: 3px 0; overflow-wrap: anywhere; }
.costs { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 6px 0; }
.costs div { background: var(--surface-2); border-radius: 10px; padding: 8px 10px; }
.costs b { display: block; font: 700 17px var(--f-display); }
.costs span { font-size: 12px; color: var(--muted); }
.breakdown { display: grid; gap: 6px; margin-top: 8px; }
.bk { display: grid; grid-template-columns: 170px minmax(0, 1fr) 48px; gap: 10px; align-items: center; font-size: 13.5px; }
.bk .tr { height: 9px; background: var(--surface-2); border-radius: 5px; overflow: hidden; }
.bk .tr i { display: block; height: 100%; border-radius: 5px; }
.bk b { text-align: right; font-weight: 600; font-size: 13px; }
.cpanel .summary { padding: 14px 16px 6px; }
.cpanel .tabbody { padding: 4px 16px 16px; }

/* ---------- compare tray ---------- */
.tray { position: fixed; left: 50%; transform: translateX(-50%); bottom: 16px; z-index: 30; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; box-shadow: var(--shadow); padding: 8px 10px 8px 14px; display: flex; align-items: center; gap: 10px; max-width: calc(100% - 32px); }
.tray .names { display: flex; gap: 6px; overflow-x: auto; scrollbar-width: none; }

/* ---------- modal ---------- */
.modal { position: fixed; inset: 0; z-index: 80; background: rgba(10, 18, 24, .5); display: grid; place-items: start center; padding: 70px 16px 16px; overflow-y: auto; }
.mbox { width: min(560px, 100%); padding: 22px; position: relative; }
.mbox h2 { font-size: 24px; }
.mbox .x { position: absolute; right: 10px; top: 10px; }
.mbox label { display: block; font-weight: 600; font-size: 14px; margin: 14px 0 5px; }
.mbox select { width: 100%; }
.vrows { display: grid; gap: 6px; margin-top: 14px; }
.vrow { display: grid; grid-template-columns: minmax(0, 1fr) auto; align-items: center; gap: 10px; padding: 9px 12px; border-radius: 10px; color: #fff; font-size: 14px; }
.vrow b { text-align: right; }

/* ---------- about ---------- */
.about { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.about .card { padding: 18px 20px; }
.about h2 { font-size: 20px; margin-bottom: 8px; }
.about table { width: 100%; border-collapse: collapse; font-size: 14px; }
.about td, .about th { text-align: left; padding: 6px 8px 6px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
.about .full { grid-column: 1 / -1; }

footer.site { border-top: 1px solid var(--line); background: var(--surface); }
footer.site .in { max-width: 1440px; margin: 0 auto; padding: 18px 20px 26px; display: flex; flex-wrap: wrap; gap: 8px 24px; justify-content: space-between; font-size: 13.5px; color: var(--muted); }
footer.site p { margin: 0; max-width: 80ch; }

/* ---------- phones ---------- */
.tabbar { display: none; }
@media (max-width: 1100px) { nav.sections a { padding: 0 8px; } .search { max-width: 260px; } }
@media (max-width: 980px) {
  .cgrid { grid-template-columns: minmax(0, 1fr); }
  .homegrid, .about { grid-template-columns: minmax(0, 1fr); }
  .rrow { grid-template-columns: 44px minmax(0, 1fr) auto 50px 38px; }
  .rrow .ch { display: none; }
}
@media (max-width: 760px) {
  .topin { height: 54px; padding: 0 12px; gap: 10px; }
  nav.sections, .search, .checkbtn { display: none; }
  .mobsearch { display: grid; margin-left: auto; }
  main { padding: 16px 16px 120px; }
  .shead h1 { font-size: 25px; }
  .entries { grid-template-columns: minmax(0, 1fr); gap: 10px; margin: 20px 0; }
  .entry { padding: 16px; display: grid; grid-template-columns: 44px minmax(0, 1fr); gap: 0 14px; }
  .entry .ic { margin: 0; grid-row: span 3; }
  .tabbar { display: grid; grid-template-columns: repeat(5, 1fr); position: fixed; left: 0; right: 0; bottom: 0; z-index: 45; background: var(--surface); border-top: 1px solid var(--line); padding-bottom: env(safe-area-inset-bottom); }
  .tabbar a, .tabbar button { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 2px; min-height: 56px; background: none; border: 0; color: var(--muted); text-decoration: none; font-size: 11.5px; font-weight: 600; cursor: pointer; }
  .tabbar svg { width: 22px; height: 22px; }
  .tabbar [aria-current="page"] { color: var(--accent); }
  .tray { bottom: 66px; padding: 6px 8px 6px 12px; }
  .tray .names { display: none; }
  .fpanel { width: 100%; }
  .rrow { grid-template-columns: minmax(0, 1fr) auto 38px; grid-template-areas: "who badge add" "ch ch ch"; gap: 6px 10px; padding: 12px 6px; }
  .rrow .rk { display: none; } .rrow .met { display: none; }
  .rrow .who { grid-area: who; } .rrow .badge { grid-area: badge; } .rrow .addc { grid-area: add; }
  .rrow .ch { display: flex; grid-area: ch; justify-content: flex-start; }
  .rrow .who .rkm { display: inline; }
  .cpanel { position: fixed; top: auto; left: 0; right: 0; bottom: 56px; width: 100%; max-height: 62vh; border-radius: 16px 16px 0 0; }
  .cpanel .ctabs, .cpanel .tabbody { display: none; }
  .mapwrap.withpanel .mapcard { min-height: 0; }
  .costs { grid-template-columns: 1fr 1fr; }
  .bk { grid-template-columns: 120px minmax(0, 1fr) 44px; font-size: 12.5px; }
  table.cmp col.l { width: 130px; }
  table.cmp .l { font-size: 12.5px; padding: 8px; }
  .modal { padding-top: 20px; }
}
.rkm { display: none; font: 500 12px var(--f-mono); color: var(--muted); margin-right: 4px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; animation: none !important; scroll-behavior: auto !important; } }
</style>

<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="topin">
    <a class="brand" href="#/" aria-label="OpenCharity home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c3 3.2 3 15.8 0 19M12 2.5c-3 3.2-3 15.8 0 19"/></svg>OpenCharity</a>
    <nav class="sections" aria-label="Sections">
      <a href="#/" data-v="home">Home</a><a href="#/map" data-v="map">Map</a><a href="#/rankings" data-v="rankings">Rankings</a><a href="#/compare" data-v="compare">Compare</a><a href="#/banking" data-v="banking">Banking</a>
    </nav>
    <div class="search" role="search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
      <input id="search" type="search" placeholder="Search countries, regions, rules…" autocomplete="off" aria-label="Search" aria-controls="results" aria-expanded="false">
      <kbd aria-hidden="true">/</kbd>
      <div class="results" id="results" hidden></div>
    </div>
    <button type="button" class="iconbtn mobsearch" id="mobSearch" aria-label="Search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>
    <button type="button" class="btn primary checkbtn" id="checkerBtn">Charity Checker</button>
    <button type="button" class="iconbtn" id="themeBtn" aria-label="Theme: follows your system"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M12 4a8 8 0 0 0 0 16z" fill="currentColor"/></svg></button>
  </div>
</header>

<main id="main" tabindex="-1">
  <section id="v-home" hidden></section>
  <section id="v-map" hidden></section>
  <section id="v-rankings" hidden></section>
  <section id="v-compare" hidden></section>
  <section id="v-banking" hidden></section>
  <section id="v-country" hidden></section>
  <section id="v-about" hidden></section>
</main>

<footer class="site"><div class="in">
  <p>Research, not legal or financial advice. Judged for a founder living in Australia with no ties to each country. Confirm with the registry or bank before you act. Charity data re-verified October 2026; personal-banking data October 2026, many rows from secondary sources (shown hatched).</p>
  <p><a href="#/about">How it works</a> · <a href="__REPO__/raw/main/charities_by_country_v2.csv" target="_blank" rel="noopener">CSV</a> · <a href="__REPO__/raw/main/charities_by_country_v2.xlsx" target="_blank" rel="noopener">Excel</a> · <a href="__REPO__" target="_blank" rel="noopener">GitHub</a></p>
</div></footer>

<div class="tray" id="tray" hidden><span class="lbl">Compare</span><div class="names" id="trayNames"></div><a class="btn primary" id="trayGo" href="#/compare">Compare <span class="n" id="trayN">0</span></a><button type="button" class="btn link" id="trayClear">Clear</button></div>

<nav class="tabbar" aria-label="Sections">
  <a href="#/" data-v="home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/></svg>Home</a>
  <a href="#/map" data-v="map"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg>Map</a>
  <a href="#/rankings" data-v="rankings"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 20V10M12 20V4M19 20v-7"/></svg>Rankings</a>
  <a href="#/compare" data-v="compare"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="14" y="4" width="7" height="16" rx="1.5"/></svg>Compare</a>
  <button type="button" id="checkerTab"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/></svg>Checker</button>
</nav>

<div class="scrim" id="scrim" hidden></div>
<aside class="fpanel" id="fpanel" hidden role="dialog" aria-modal="true" aria-labelledby="fTitle">
  <header><h2 id="fTitle">Filters</h2><button type="button" class="iconbtn" id="fClose" aria-label="Close filters">✕</button></header>
  <div class="fbody" id="fbody"></div>
  <footer><button type="button" class="btn" id="fClear">Clear all</button><button type="button" class="btn primary" id="fShow">Show countries</button></footer>
</aside>
<div class="modal" id="modal" hidden role="dialog" aria-modal="true" aria-labelledby="mTitle"><div class="mbox card" id="mbox"></div></div>
<div class="notebox" id="note" hidden role="tooltip"></div>
<div class="sr" aria-live="polite" id="live"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<script>
const DATA = __DATA__;
const GEO = __GEO__;
const ALIAS = __ALIAS__;
const POINTS = __POINTS__;
const FLAGS = __FLAGS__;

/* ================= helpers ================= */
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const slug = s => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const byName = new Map(DATA.map(d => [d.country, d]));
const bySlug = new Map(DATA.map(d => [slug(d.country), d]));
const geoName = new Map(DATA.map(d => [ALIAS[d.country] || d.country, d.country]));
const store = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
const load = k => { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } };
const fmtUSD = v => v >= 1000 ? "$" + (v / 1000).toFixed(v % 1000 ? 1 : 0) + "k" : v < 10 && v % 1 ? "$" + v.toFixed(2) : "$" + Math.round(v);
const usd = v => v == null ? "—" : v === 0 ? "Free" : fmtUSD(v);
const dep = v => v == null ? "—" : v === 0 ? "None" : fmtUSD(v);
const feeTxt = d => d.fee_lo == null ? "Not published" : d.fee_hi === 0 ? "Free" : d.fee_lo === d.fee_hi ? fmtUSD(d.fee_lo) : `${fmtUSD(d.fee_lo)}–${fmtUSD(d.fee_hi)}`;
const dur = n => n < 14 ? `${n} days` : n < 60 ? `${Math.round(n / 7)} weeks` : n < 365 ? `${Math.round(n / 30)} months` : `${(n / 365).toFixed(n % 365 ? 1 : 0)} years`;
const timeTxt = d => { if (d.days_lo == null) return "Not stated"; if (d.days_lo === d.days_hi) return dur(d.days_lo);
  const a = dur(d.days_lo).split(" "), b = dur(d.days_hi).split(" "); return a[1] === b[1] ? `${a[0]}–${b[0]} ${b[1]}` : `${a.join(" ")} – ${b.join(" ")}`; };
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };
const narrow = () => matchMedia("(max-width: 760px)").matches;
{ const s = document.createElement("style");
  s.textContent = Object.entries(FLAGS).map(([k, v]) => `.fl-${k}{background-image:url("data:image/svg+xml,${encodeURIComponent(v)}")}`).join("");
  document.head.appendChild(s); }
const flag = (d, lg) => `<span class="flag${lg ? " lg" : ""} fl-${d.iso}" aria-hidden="true"></span>`;

/* ================= vocabulary: plain words + definitions ================= */
// value -> [label, colour, definition]
const CAT = {
  difficulty: { easy: ["Easy", "ok", "Simple rules and few steps for an Australian founder"], medium: ["Medium", "mid", "Some extra steps, such as a local address or notary"],
    hard: ["Hard", "warn", "Significant local requirements or slow approval"], "very hard": ["Very hard", "bad", "Closed to foreign founders in practice, or close to it"] },
  no_presence: { yes: ["Set up without visiting", "ok", "Every step can be done from Australia"], partial: ["Needs a local agent", "mid", "A local address, agent or resident officer is required"],
    no: ["Must travel there", "bad", "At least one step needs you in the country"] },
  fee_bin: { free: ["Free", "ok", "No government registration fee"], low: ["$1–100", "mid", "Lowest stated fee up to US$100"], mid: ["$101–500", "warn", "Lowest stated fee US$101–500"],
    high: ["Over $500", "bad", "Lowest stated fee above US$500"], unknown: ["Fee not published", "na", "No official fee found"] },
  time_bin: { fast: ["Up to 2 weeks", "ok", "Shortest stated time up to 14 days"], month: ["Up to a month", "mid", "Shortest stated time up to 31 days"],
    quarter: ["1–3 months", "warn", "Shortest stated time up to 92 days"], slow: ["Over 3 months", "bad", "Shortest stated time above 92 days"], unknown: ["Time not stated", "na", "No official time found"] },
  bank_cat: { remote: ["Bank account without a visit", "ok", "At least one bank or licensed e-money provider onboards the charity remotely"],
    visit: ["Bank needs a visit", "mid", "A signatory must attend a branch for checks"], blocked: ["Bank account blocked", "bad", "Banks effectively refuse foreign-founded charities"] },
  funding_cat: { open: ["Foreign money welcome", "ok", "No notable limits on donations from abroad"], restricted: ["Rules on foreign money", "warn", "Donations from abroad need approval, reporting or a levy"] },
  gfn: { Yes: ["Google for Nonprofits", "ok", "Charities registered here can join Google's programme"], No: ["No Google for Nonprofits", "bad", "Google's programme isn't offered here"] },
  pb_status: { yes: ["Banks accept non-residents", "ok", "Several mainstream banks open personal accounts for non-residents"],
    limited: ["Some banks, case by case", "warn", "Only a few banks, premium accounts or large deposits"], no: ["Residents only", "bad", "A local residence permit is needed, or banking is closed"] },
  pb_method: { remote: ["Open without visiting", "ok", "At least one bank opens a non-resident's account remotely"], "in-person": ["Open at a branch", "mid", "You must visit a branch in person"],
    "not available": ["Can't open", "bad", "No bank opens accounts for non-residents"] },
  pb_cost_bin: { free: ["No account fees", "ok", "No monthly or opening fee published"], low: ["Up to $60 a year", "mid", "First-year fees up to US$60"], mid: ["$61–240 a year", "warn", "First-year fees US$61–240"],
    high: ["Over $240 a year", "bad", "First-year fees above US$240"], unknown: ["Fees not published", "na", "No published fee figures"] },
  pb_dep_bin: { none: ["No minimum deposit", "ok", "No opening deposit required"], low: ["Deposit up to $500", "mid", "Opening deposit up to US$500"], mid: ["Deposit $501–10k", "warn", "Opening deposit US$501–10,000"],
    high: ["Deposit over $10k", "bad", "Opening deposit above US$10,000"], unknown: ["Deposit not published", "na", "No published deposit figure"] },
  pb_res: { no: ["No residence needed", "ok", "Banks don't ask for local residence"], often: ["Residence often needed", "warn", "Many banks ask for local residence"], yes: ["Residence required", "bad", "Local residence is required"] },
  confidence: { high: ["Confidence: high", "ok", "Checked against official sources"], med: ["Confidence: medium", "mid", "Official and secondary sources"] },
};
const SYM = { ok: "✓", mid: "•", warn: "!", bad: "✕", na: "?" };
const BANKING_KEYS = new Set(["pb_status", "pb_method", "pb_cost_bin", "pb_dep_bin", "pb_res"]);
const cat = (k, d) => CAT[k]?.[d[k]] || [d[k] || "—", "na", ""];
const ordOf = (k, d) => { const i = Object.keys(CAT[k]).indexOf(d[k]); return i < 0 ? 99 : i; };
const low = (k, d) => BANKING_KEYS.has(k) && d.pb_conf === "low";
const chip = (k, d, text) => { const [l, c, def] = cat(k, d), lc = low(k, d);
  return `<span class="chip c-${c}${lc ? " hatch" : ""}" title="${esc(def)}${lc ? " · low-confidence research" : ""}"><span class="y" aria-hidden="true">${SYM[c]}</span>${esc(text || l)}</span>`; };

/* ================= charity score ================= */
const pct = key => { const v = DATA.filter(d => d[key] != null).map(d => d[key]).sort((a, b) => a - b);
  return x => { let i = 0; while (i < v.length && v[i] < x) i++; return v.length > 1 ? i / (v.length - 1) : 0; }; };
const feeP = pct("fee_lo"), dayP = pct("days_lo");
const FACTORS = [
  ["ease", "Ease of registering", 25, 0, d => ({ easy: 25, medium: 17, hard: 8, "very hard": 0 })[d.difficulty] ?? 0],
  ["remote", "Set up without visiting", 20, 0, d => ({ yes: 20, partial: 10, no: 0 })[d.no_presence] ?? 0],
  ["fee", "Low registration fee", 10, 1, d => d.fee_lo == null ? 0 : 10 * (1 - feeP(d.fee_lo))],
  ["speed", "Fast registration", 10, 1, d => d.days_lo == null ? 0 : 10 * (1 - dayP(d.days_lo))],
  ["cbank", "Charity bank account", 10, 2, d => ({ remote: 10, visit: 5, blocked: 0 })[d.bank_cat] ?? 0],
  ["pbank", "Personal account", 10, 2, d => (({ yes: 7, limited: 3.5, no: 0 })[d.pb_status] ?? 0) + (({ remote: 3, "in-person": 1.5, "not available": 0 })[d.pb_method] ?? 0)],
  ["funding", "Foreign money welcome", 5, 3, d => d.funding_cat === "open" ? 5 : 0],
  ["gfn", "Google for Nonprofits", 10, 3, d => d.gfn === "Yes" ? 10 : 0],
];
const GROUPS = ["Registration", "Cost and speed", "Banking", "Funding and Google"];
const BANDS = [[85, "Excellent", "b5"], [70, "Very good", "b4"], [55, "Good", "b3"], [40, "Fair", "b2"], [25, "Hard", "b1"], [0, "Very hard", "b0"]];
for (const d of DATA) {
  d.pts = Object.fromEntries(FACTORS.map(([k, , , , f]) => [k, f(d)]));
  d.grp = GROUPS.map((_, g) => FACTORS.filter(f => f[3] === g).reduce((s, f) => s + d.pts[f[0]], 0));
  d.cs = Math.round(d.grp.reduce((a, b) => a + b, 0));
  d.band = BANDS.find(([m]) => d.cs >= m)[2];
}
CAT.band = Object.fromEntries(BANDS.map(([m, l, c], i) => [c, [`${l} ${m}${i ? "–" + (BANDS[i - 1][0] - 1) : "+"}`, c, `Charity score ${m}${i ? "–" + (BANDS[i - 1][0] - 1) : "–100"}`]]));
const bandLabel = d => BANDS.find(b => b[2] === d.band)[1];
const badge = (d, lg) => `<span class="badge bg-${d.band}${lg ? " lg" : ""}" title="Charity score ${d.cs} out of 100: ${esc(bandLabel(d))}">${d.cs}<span class="sr"> out of 100</span></span>`;
const parts = d => `<span class="parts" aria-hidden="true">${d.grp.map((v, i) => `<i class="p${i}" style="width:${v}%"></i>`).join("")}</span>`;

/* ================= state + URL ================= */
const FACETS = {
  Registering: [["difficulty", "Difficulty"], ["no_presence", "Setting up"], ["fee_bin", "Registration fee"], ["time_bin", "Time to register"], ["funding_cat", "Foreign donations"], ["gfn", "Google for Nonprofits"]],
  Banking: [["bank_cat", "Charity bank account"], ["pb_status", "Personal account"], ["pb_method", "Opening a personal account"], ["pb_cost_bin", "Personal account fees"], ["pb_dep_bin", "Minimum deposit"], ["pb_res", "Local residence"]],
  "Score and research": [["band", "Charity score"], ["confidence", "Research confidence"]],
  Region: [["region", "Region"]],
};
const FKEYS = Object.values(FACETS).flat().map(([k]) => k);
const FLABEL = Object.fromEntries(Object.values(FACETS).flat());
const REGIONS = [...new Set(DATA.map(d => d.region))].sort();
const optsOf = k => k === "region" ? REGIONS.map(r => [r, r, null, ""]) : Object.entries(CAT[k]).map(([v, [l, c, def]]) => [v, l, c, def]);
const MODES = [["band", "Charity score"], ["difficulty", "Difficulty"], ["no_presence", "Setting up"], ["fee_bin", "Registration fee"], ["time_bin", "Time to register"],
  ["bank_cat", "Charity bank account"], ["pb_status", "Personal account"], ["pb_method", "Opening a personal account"], ["pb_cost_bin", "Personal account fees"],
  ["funding_cat", "Foreign donations"], ["gfn", "Google for Nonprofits"], ["confidence", "Research confidence"]];
const W_DEFAULT = { ease: 3, remote: 3, fee: 2, speed: 2, cbank: 2, pbank: 1, funding: 1, gfn: 1 };
const S = { F: Object.fromEntries(FKEYS.map(k => [k, new Set()])), q: "", fee: "", days: "", mode: "band", rank: "overall", bank: "pbank", cmp: [], W: { ...W_DEFAULT }, theme: "system", diff: null, list: false };
{ const s = load("oc-site") || {};
  if (s.F) for (const k in s.F) if (S.F[k]) s.F[k].forEach(v => S.F[k].add(v));
  for (const k of ["q", "fee", "days"]) if (typeof s[k] === "string") S[k] = s[k];
  if (MODES.some(([m]) => m === s.mode)) S.mode = s.mode;
  if (Array.isArray(s.cmp)) S.cmp = s.cmp.filter(c => byName.has(c)).slice(0, 5);
  if (s.W) for (const k in S.W) if (typeof s.W[k] === "number") S.W[k] = s.W[k];
  if (["system", "light", "dark"].includes(s.theme)) S.theme = s.theme; }
const save = () => store("oc-site", { F: Object.fromEntries(Object.entries(S.F).map(([k, v]) => [k, [...v]])), q: S.q, fee: S.fee, days: S.days, mode: S.mode, cmp: S.cmp, W: S.W, theme: S.theme });
const nFilters = () => Object.values(S.F).reduce((s, x) => s + x.size, 0) + (S.q ? 1 : 0) + (S.fee !== "" ? 1 : 0) + (S.days !== "" ? 1 : 0);
function query(withMode) {
  const p = new URLSearchParams(), f = Object.entries(S.F).filter(([, s]) => s.size).map(([k, s]) => k + ":" + [...s].join(",")).join(";");
  if (f) p.set("f", f); if (S.q) p.set("q", S.q); if (S.fee !== "") p.set("fee", S.fee); if (S.days !== "") p.set("days", S.days);
  if (withMode && S.mode !== "band") p.set("mode", S.mode);
  const s = p.toString(); return s ? "?" + s : "";
}
function readQuery(p) {
  if (![...p.keys()].length) return;
  for (const k in S.F) S.F[k].clear();
  for (const part of (p.get("f") || "").split(";").filter(Boolean)) { const [k, vs] = part.split(":"); if (S.F[k]) vs.split(",").forEach(v => S.F[k].add(v)); }
  S.q = p.get("q") || ""; S.fee = p.get("fee") || ""; S.days = p.get("days") || "";
  if (MODES.some(([m]) => m === p.get("mode"))) S.mode = p.get("mode");
}
const HAY = new Map(DATA.map(d => [d.country, [d.country, d.region, d.entity, d.requirements, d.bottleneck, d.notes, d.tax_exempt, d.donor_restr, d.bank_access, d.pb_banks, d.pb_docs, d.pb_restr, d.pb_alt].join(" ").toLowerCase()]));
function passes(d, skip) {
  for (const k in S.F) if (k !== skip && S.F[k].size && !S.F[k].has(d[k])) return false;
  if (S.q && !HAY.get(d.country).includes(S.q.toLowerCase())) return false;
  if (S.fee !== "" && (d.fee_lo == null || d.fee_lo > +S.fee)) return false;
  if (S.days !== "" && (d.days_lo == null || d.days_lo > +S.days)) return false;
  return true;
}
const announce = t => { $("live").textContent = t; };

/* ================= rankings ================= */
const fitOf = d => { let s = 0, t = 0; for (const [k, , mx] of FACTORS) { s += S.W[k] * d.pts[k] / mx; t += S.W[k]; } return t ? Math.round(100 * s / t) : 0; };
const lab = k => d => cat(k, d)[0];
const RANKS = {
  overall:  { label: "Best overall", metric: d => bandLabel(d), val: d => -d.cs, mode: "band", note: "Highest charity score first: registration ease, setting up without visiting, cost, speed, banking, foreign donations and Google for Nonprofits." },
  easiest:  { label: "Easiest", metric: lab("difficulty"), val: d => ordOf("difficulty", d) * 10 + ordOf("no_presence", d), mode: "difficulty", note: "Easiest rules first, then how much you can do without visiting." },
  cheapest: { label: "Cheapest", metric: feeTxt, val: d => d.fee_lo, mode: "fee_bin", note: "Lowest stated government fee first. Some notes include agent or notary costs; unpublished fees come last." },
  fastest:  { label: "Fastest", metric: timeTxt, val: d => d.days_lo, mode: "time_bin", note: "Shortest stated registration time first; unstated times come last." },
  remote:   { label: "Most remote", metric: lab("no_presence"), val: d => ordOf("no_presence", d) * 10 + ordOf("bank_cat", d), mode: "no_presence", note: "Countries you can set up without visiting first, then those where the charity's bank account also opens remotely." },
  hardest:  { label: "Hardest first", more: 1, metric: lab("difficulty"), val: d => -(ordOf("difficulty", d) * 10 + ordOf("no_presence", d)), mode: "difficulty", note: "Hardest rules first." },
  priciest: { label: "Most expensive", more: 1, metric: feeTxt, val: d => d.fee_hi == null ? null : -d.fee_hi, mode: "fee_bin", note: "Highest stated fee first." },
  slowest:  { label: "Slowest", more: 1, metric: timeTxt, val: d => d.days_hi == null ? null : -d.days_hi, mode: "time_bin", note: "Longest stated time first." },
  funding:  { label: "Foreign money welcome", more: 1, metric: lab("funding_cat"), val: d => ordOf("funding_cat", d) * 1000 - d.cs, mode: "funding_cat", note: "No notable limits on foreign donations first, then by charity score." },
  cheapfast:{ label: "Cheap and fast", more: 1, metric: d => `${feeTxt(d)} · ${timeTxt(d)}`, val: null, mode: "fee_bin", note: "Fee rank plus time rank; both must be stated." },
  custom:   { label: "Your weights", more: 1, metric: d => `Fit ${fitOf(d)}`, val: d => -fitOf(d), mode: "band", note: "Fit 0–100 from the sliders: each factor counts as much as you say it matters." },
  alpha:    { label: "A–Z", more: 1, metric: d => d.region, val: null, mode: "band", note: "Alphabetical." },
  pbank:    { bank: 1, label: "Easiest account", metric: lab("pb_status"), val: d => ordOf("pb_status", d) * 10 + ordOf("pb_method", d), mode: "pb_status", note: "Can a non-resident (no visa or address there) open a personal account at a licensed local bank? Easiest first." },
  pbremote: { bank: 1, label: "Without visiting", metric: lab("pb_method"), val: d => ordOf("pb_method", d) * 10 + ordOf("pb_status", d), mode: "pb_method", note: "Countries where a bank opens a non-resident's personal account remotely come first." },
  pbcheap:  { bank: 1, label: "Cheapest account", metric: d => d.pb_year == null ? "Fees not published" : usd(d.pb_year) + " a year", val: d => d.pb_year, mode: "pb_cost_bin", note: "First-year fees (12 monthly fees + opening fee, US$). Published for about a third of countries; the rest come last." },
};
{ const pos = f => { const s = DATA.filter(d => f(d) != null).sort((a, b) => f(a) - f(b)); return new Map(s.map((d, i) => [d.country, i])); };
  const pf = pos(d => d.fee_lo), pt = pos(d => d.days_lo);
  RANKS.cheapfast.val = d => pf.has(d.country) && pt.has(d.country) ? pf.get(d.country) + pt.get(d.country) : null;
  RANKS.alpha.val = d => d.country; }
function ranked(key) {
  const r = RANKS[key], v = d => { const x = r.val(d); return x == null ? Infinity : x; };
  const list = [...DATA].sort((a, b) => (key === "alpha" ? a.country.localeCompare(b.country) : v(a) - v(b)) || b.cs - a.cs || a.country.localeCompare(b.country));
  const pos = new Map(); let rank = 0, prev;
  list.forEach((d, i) => { const x = key === "alpha" ? i : v(d); if (x !== prev) { rank++; prev = x; } pos.set(d.country, x === Infinity ? null : rank); });
  return { list, pos };
}
const POWER = ranked("overall");

/* ================= maps ================= */
const FEATS = topojson.feature(GEO, GEO.objects.countries).features;
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const fillFor = k => { const m = {}; return d => { const c = k === "band" ? d.band : cat(k, d)[1]; return m[c] ??= css("--" + c); }; };
function makeMap(host, onPick) {
  host.innerHTML = `<div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button><button type="button" data-z="0" aria-label="Reset zoom">⟲</button></div>
    <svg viewBox="0 0 960 500" role="img" aria-label="World map. Use the list view or search to reach countries by keyboard."></svg><div class="tip" hidden></div>`;
  const W = 960, H = 500, svgEl = host.querySelector("svg"), tip = host.querySelector(".tip"), svg = d3.select(svgEl), g = svg.append("g");
  const proj = d3.geoNaturalEarth1().fitExtent([[6, 6], [W - 6, H - 6]], { type: "FeatureCollection", features: FEATS });
  const path = d3.geoPath(proj);
  const paths = g.append("g").selectAll("path").data(FEATS).join("path").attr("d", path).attr("class", "cty");
  const featOf = new Map(); FEATS.forEach(f => { const c = geoName.get(f.properties.name); if (c) featOf.set(c, f); });
  const dotData = DATA.filter(d => POINTS[d.country] || path.area(featOf.get(d.country)) < 6)
    .map(d => { const xy = POINTS[d.country] ? proj(POINTS[d.country]) : path.centroid(featOf.get(d.country)); return { d, x: xy[0], y: xy[1] }; });
  const dots = g.append("g").selectAll("circle").data(dotData).join("circle").attr("class", "dot").attr("cx", p => p.x).attr("cy", p => p.y).attr("r", 3.4);
  const zoom = d3.zoom().scaleExtent([1, 12]).translateExtent([[0, 0], [W, H]]).on("zoom", ev => { g.attr("transform", ev.transform); dots.attr("r", 3.4 / Math.sqrt(ev.transform.k)); });
  svg.call(zoom).on("dblclick.zoom", null);
  const anim = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 250;
  host.querySelectorAll("[data-z]").forEach(b => b.onclick = () => b.dataset.z === "0" ? svg.transition().duration(anim).call(zoom.transform, d3.zoomIdentity)
    : svg.transition().duration(anim).call(zoom.scaleBy, b.dataset.z === "in" ? 1.6 : 1 / 1.6));
  let tipFn = d => d.country;
  const show = (ev, name) => { const d = byName.get(name), r = host.getBoundingClientRect();
    tip.innerHTML = d ? tipFn(d) : `<b>${esc(name)}</b><br>Not in the dataset (a dependent territory follows its parent country)`; tip.hidden = false;
    tip.style.left = Math.max(6, Math.min(ev.clientX - r.left + 14, r.width - tip.offsetWidth - 6)) + "px";
    tip.style.top = Math.max(ev.clientY - r.top - tip.offsetHeight - 10, 6) + "px"; };
  paths.on("mousemove", (ev, f) => show(ev, geoName.get(f.properties.name) || f.properties.name)).on("mouseleave", () => tip.hidden = true)
    .on("click", (ev, f) => { const c = geoName.get(f.properties.name); if (c) { tip.hidden = true; onPick(c); } });
  dots.on("mousemove", (ev, p) => show(ev, p.d.country)).on("mouseleave", () => tip.hidden = true).on("click", (ev, p) => { tip.hidden = true; onPick(p.d.country); });
  return {
    paint(fill, dim, sel) {
      paths.attr("fill", f => { const c = geoName.get(f.properties.name); return c ? fill(byName.get(c)) : null; })
        .attr("class", f => { const c = geoName.get(f.properties.name); return "cty" + (c ? "" : " nodata") + (c && dim(byName.get(c)) ? " dim" : "") + (c && c === sel ? " sel" : ""); });
      dots.attr("fill", p => fill(p.d)).attr("class", p => "dot" + (dim(p.d) ? " dim" : "") + (p.d.country === sel ? " sel" : ""));
      dots.filter(p => p.d.country === sel).raise();
    },
    tip(fn) { tipFn = fn; },
  };
}

/* ================= router ================= */
let view = "home", arg = null, prevView = null;
const SECTIONS = ["home", "map", "rankings", "compare", "banking", "country", "about"];
function go(h) { if (location.hash !== h) location.hash = h; else route(); }
function route() {
  const raw = location.hash.replace(/^#\/?/, ""), [p, qs] = raw.split("?"), parts = decodeURIComponent(p || "").split("/").filter(Boolean);
  readQuery(new URLSearchParams(qs || ""));
  closeNote(); closeResults();
  const was = view;
  let v = parts[0] || "home"; arg = parts[1] || null;
  if (bySlug.has(v)) { arg = v; v = "country"; }                           // legacy #estonia links
  if (v === "country" && !bySlug.has(arg)) v = "map";
  if (!SECTIONS.includes(v)) v = "home";
  if (v === "rankings" && RANKS[arg] && !RANKS[arg].bank) S.rank = arg;
  if (v === "banking" && RANKS[arg]?.bank) S.bank = arg;
  if (v === "compare" && arg) { const cs = arg.split(",").map(s => bySlug.get(s)?.country).filter(Boolean); if (cs.length) S.cmp = [...new Set(cs)].slice(0, 5); }
  if (v !== was) prevView = was;
  view = v;
  SECTIONS.forEach(x => $("v-" + x).hidden = x !== v);
  document.querySelectorAll("nav.sections a, .tabbar a").forEach(a => a.dataset.v === (v === "country" ? prevView : v) ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  ({ home: renderHome, map: renderMap, rankings: renderRankings, compare: renderCompare, banking: renderBanking, country: renderCountryPage, about: renderAbout })[v]();
  renderTray(); save();
  document.title = (v === "country" ? bySlug.get(arg).country + " · " : v === "home" ? "" : $("v-" + v).querySelector("h1")?.textContent + " · ") + "OpenCharity";
  if (v !== was || v === "country") { window.scrollTo(0, 0); }
}
function syncURL() {   // keep the address in step with filters without a history entry
  const base = location.hash.split("?")[0] || "#/", h = base + (["map", "rankings", "banking"].includes(view) ? query(view === "map") : "");
  if (location.hash !== h) history.replaceState(null, "", h);
}
addEventListener("hashchange", route);

/* ================= shared pieces ================= */
function toolbar(n, total) {
  const k = nFilters(), tags = [];
  for (const [key, set] of Object.entries(S.F)) for (const v of set) tags.push([`${FLABEL[key]}: ${key === "region" ? v : CAT[key][v]?.[0] ?? v}`, `f|${key}|${v}`]);
  if (S.q) tags.push([`Contains “${S.q}”`, "q"]); if (S.fee !== "") tags.push([`Fee up to $${S.fee}`, "fee"]); if (S.days !== "") tags.push([`Up to ${S.days} days`, "days"]);
  return `<div class="toolbar"><button type="button" class="btn" data-open-filters aria-haspopup="dialog"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><path d="M3 5h18M6 12h12M10 19h4"/></svg>Filters${k ? ` <span class="n">${k}</span>` : ""}</button>
    <span class="count">${n} of ${total} countries</span><div class="tags">${tags.map(([t, id]) => `<span class="tag">${esc(t)}<button type="button" data-rm="${esc(id)}" aria-label="Remove ${esc(t)}">×</button></span>`).join("")}</div>
    ${k ? `<button type="button" class="btn link" data-clear>Clear all</button>` : ""}</div>`;
}
const rowsHTML = (list, pos, R, opts = {}) => list.map(d => {
  const inC = S.cmp.includes(d.country), p = pos.get(d.country);
  const chips = opts.bank ? [chip("pb_status", d), chip("pb_method", d)] : [chip("difficulty", d), chip("no_presence", d)];
  return `<li class="rrow" tabindex="0" data-c="${esc(d.country)}" aria-label="${esc(`${d.country}, ${p ? "rank " + p : "not ranked"}, charity score ${d.cs}`)}">
    <span class="rk">${p ? "#" + p : "—"}</span>
    <span class="who">${flag(d)}<span class="nm"><span class="rkm">${p ? "#" + p : ""}</span>${esc(d.country)}<small>${esc(d.region)}</small>${parts(d)}</span></span>
    <span class="met">${esc(R.metric(d))}</span><span class="ch">${chips.join("")}</span>${badge(d)}
    <button type="button" class="addc" data-add="${esc(d.country)}" aria-pressed="${inC}" aria-label="${inC ? "Remove" : "Add"} ${esc(d.country)} ${inC ? "from" : "to"} compare" title="${inC ? "Remove from" : "Add to"} compare"${!inC && S.cmp.length >= 5 ? " disabled" : ""}>${inC ? "✓" : "+"}</button></li>`;
}).join("");
const legendHTML = mode => `<div class="legend" role="group" aria-label="Map colours (click to filter)">${Object.entries(CAT[mode]).map(([v, [l, c, def]]) =>
  `<button type="button" class="leg" data-f="${mode}" data-v="${esc(v)}" aria-pressed="${S.F[mode].has(v)}" title="${esc(def)}. Click to show only these."><i style="background:var(--${c})"></i>${esc(l)} <span class="n">${DATA.filter(d => d[mode] === v && passes(d, mode)).length}</span></button>`).join("")}</div>`;

/* ================= HOME ================= */
function renderHome() {
  const top = POWER.list.slice(0, 5), remote = DATA.filter(d => d.no_presence === "yes").length, open = DATA.filter(d => d.pb_status === "yes").length;
  $("v-home").innerHTML = `<div class="hero"><h1>Where can you register a charity from Australia?</h1>
      <p>${DATA.length} countries researched: the rules, fees, timelines and bank accounts for a founder living in Australia, every claim linked to its source.</p></div>
    <div class="entries">
      <a class="entry card" href="#/rankings/overall"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 20V10M12 20V4M19 20v-7"/></svg></span><h2>Where is easiest?</h2><p>Every country ranked by how easy, cheap and fast it is to set up a charity.</p><span class="go">See the rankings →</span></a>
      <a class="entry card" href="#/compare"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="7" height="16" rx="1.5"/><rect x="14" y="4" width="7" height="16" rx="1.5"/></svg></span><h2>Compare countries</h2><p>Put two to five countries side by side and see where each one wins.</p><span class="go">Start comparing →</span></a>
      <a class="entry card" href="#/banking"><span class="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10h18M5 10v8M9.5 10v8M14.5 10v8M19 10v8M3 20h18M12 3l9 5H3z"/></svg></span><h2>Can I bank there?</h2><p>Where a non-resident can open a personal account, without visiting, and what it costs.</p><span class="go">Check banking →</span></a>
    </div>
    <div class="homegrid">
      <div class="card"><h2>Top 5 overall</h2><ol class="top5">${top.map(d => `<li><a href="#/country/${slug(d.country)}"><span class="r">#${POWER.pos.get(d.country)}</span>${flag(d)}<span>${esc(d.country)}</span>${badge(d)}</a></li>`).join("")}</ol>
        <p style="margin:10px 0 0"><a href="#/map">Explore the map →</a></p></div>
      <div class="card"><h2>At a glance</h2><div class="stat3"><div><b>${DATA.length}</b><span>countries and territories</span></div><div><b>${remote}</b><span>can be set up without visiting</span></div><div><b>${open}</b><span>where banks accept non-residents</span></div></div>
        <p style="margin:14px 0 0;font-size:14px;color:var(--muted)">The charity score (0–100) adds up registration ease, setting up without visiting, cost, speed, banking, foreign donations and Google for Nonprofits. <a href="#/about">How it works</a></p>
        <div class="key" style="margin-top:12px">${BANDS.map(([, l, c]) => `<span><i class="bg-${c}"></i>${esc(l)}</span>`).join("")}</div></div>
    </div>`;
}

/* ================= MAP ================= */
let mapObj = null;
function renderMap() {
  const sel = arg && bySlug.has(arg) ? bySlug.get(arg) : null, n = DATA.filter(d => passes(d)).length;
  if (!$("mapHost")) {
    $("v-map").innerHTML = `<div class="shead"><div><h1>Map</h1><p>Click a country to see its rules. Colours show the charity score, or pick another measure.</p></div>
        <div class="toolbar" style="margin:0"><label class="modesel"><span class="lbl">Colour by</span><select class="sel" id="modeSel">${MODES.map(([k, l]) => `<option value="${k}">${esc(l)}</option>`).join("")}</select></label>
        <button type="button" class="btn listtoggle" id="listToggle" aria-pressed="false">List view</button></div></div>
      <div id="mapTools"></div>
      <div class="mapwrap" id="mapWrap"><div class="mapcard" id="mapHost"></div><aside class="cpanel" id="cpanel" hidden aria-label="Country details"></aside></div>
      <div id="mapLegend"></div><ol class="rlist card" id="mapList" hidden style="margin-top:12px"></ol>`;
    mapObj = makeMap($("mapHost"), c => go("#/map/" + slug(c) + query(true)));
    $("modeSel").addEventListener("change", e => { S.mode = e.target.value; renderMap(); });
    $("listToggle").addEventListener("click", () => { S.list = !S.list; renderMap(); });
  }
  $("modeSel").value = S.mode;
  $("listToggle").setAttribute("aria-pressed", S.list);
  $("mapTools").innerHTML = toolbar(n, DATA.length);
  $("mapLegend").innerHTML = legendHTML(S.mode);
  mapObj.tip(d => `${flag(d)} <b>${esc(d.country)}</b> ${badge(d)}<br>${S.mode === "band" ? esc(bandLabel(d)) : esc(cat(S.mode, d)[0])}<br><span style="color:var(--muted)">Click for details</span>`);
  mapObj.paint(fillFor(S.mode), d => !passes(d), sel?.country);
  $("mapList").hidden = !S.list;
  if (S.list) { const { list, pos } = POWER; $("mapList").innerHTML = rowsHTML(list.filter(d => passes(d)), pos, RANKS.overall) || `<li class="empty">No countries match. Remove a filter.</li>`; }
  $("mapWrap").classList.toggle("withpanel", !!sel);
  $("cpanel").hidden = !sel;
  if (sel) { $("cpanel").innerHTML = `<button type="button" class="iconbtn close" data-closepanel aria-label="Close ${esc(sel.country)}">✕</button>` + countryHTML(sel, "panel"); bindTabs($("cpanel")); }
  announce(`${n} countries match`);
  syncURL();
}

/* ================= RANKINGS + BANKING ================= */
function rankView(host, key, bankMode) {
  const R = RANKS[key], { list, pos } = ranked(key), rows = list.filter(d => passes(d));
  const tabs = Object.entries(RANKS).filter(([, r]) => bankMode ? r.bank : !r.bank && !r.more);
  const more = bankMode ? [] : Object.entries(RANKS).filter(([, r]) => r.more);
  const base = bankMode ? "#/banking/" : "#/rankings/";
  host.innerHTML = `<div class="shead"><div><h1>${bankMode ? "Banking" : "Rankings"}</h1><p>${bankMode ? "Personal bank accounts for a non-resident: someone with no visa, address or job in the country." : "Who is best for what matters to you. Pick a ranking; filters narrow the list."}</p></div></div>
    <div class="tabs" role="tablist" aria-label="Ranking">${tabs.map(([k, r]) => `<button type="button" role="tab" data-rank="${base}${k}" aria-selected="${k === key}">${esc(r.label)}</button>`).join("")}
      ${more.length ? `<select class="${R.more ? "on" : ""}" id="moreRank" aria-label="More ways to rank"><option value="">More ways to rank…</option>${more.map(([k, r]) => `<option value="${k}"${k === key ? " selected" : ""}>${esc(r.label)}</option>`).join("")}</select>` : ""}</div>
    ${key === "custom" ? `<div class="weights card">${FACTORS.map(([k, l]) => `<div><label for="w-${k}">${esc(l)} <output id="wo-${k}">${S.W[k]}</output></label><input type="range" id="w-${k}" data-w="${k}" min="0" max="5" step="1" value="${S.W[k]}"></div>`).join("")}<div><button type="button" class="btn link" id="wReset">Reset weights</button></div></div>` : ""}
    <p class="rnote">${esc(R.note)}</p>
    ${toolbar(rows.length, DATA.length)}
    ${bankMode ? `<div class="mapcard" id="bankMap" style="margin-bottom:10px"></div>${legendHTML(R.mode)}<p class="key" style="margin:8px 0 12px">Hatched chips = low-confidence research (secondary sources only).</p>` : ""}
    <ol class="rlist card" id="rlist" aria-label="${esc(R.label)}">${rowsHTML(rows, pos, R, { bank: bankMode }) || `<li class="empty">No countries match all these filters. Remove one above.</li>`}</ol>`;
  host.querySelectorAll("[data-rank]").forEach(b => b.onclick = () => go(b.dataset.rank));
  $("moreRank")?.addEventListener("change", e => e.target.value && go(base + e.target.value));
  if (bankMode) { const m = makeMap($("bankMap"), c => go("#/country/" + slug(c)));
    m.tip(d => `${flag(d)} <b>${esc(d.country)}</b><br>${esc(cat(R.mode, d)[0])}${d.pb_year != null ? "<br>" + esc(usd(d.pb_year)) + " a year" : ""}`); m.paint(fillFor(R.mode), d => !passes(d), null); }
  announce(`${rows.length} countries ranked`);
  syncURL();
}
const renderRankings = () => rankView($("v-rankings"), S.rank, false);
const renderBanking = () => rankView($("v-banking"), S.bank, true);
function rerender() { if (view === "map") renderMap(); else if (view === "rankings") renderRankings(); else if (view === "banking") renderBanking(); save(); }

/* ================= COUNTRY (panel + page) ================= */
const ctab = {};
function countryHTML(d, mode) {
  const p = POWER.pos.get(d.country), inC = S.cmp.includes(d.country), page = mode === "page", t = ctab.cur || "reg";
  const srcs = s => (s || "").split(/\s*;\s*/).filter(x => /^https?:\/\//.test(x));
  const link = s => `<a href="${esc(s)}" target="_blank" rel="noopener">${esc(s.replace(/^https?:\/\/(www\.)?/, "").slice(0, 70))}</a>`;
  const sec = (h, b) => b ? `<div class="sec"><h3>${esc(h)}</h3><p>${esc(b)}</p></div>` : "";
  const notes = (d.notes || "").split(/\s+\|\s+/).filter(Boolean);
  const V = [["difficulty", "Registration"], ["no_presence", "Setting up"], ["bank_cat", "Charity bank"], ["pb_status", "Personal account"], ["funding_cat", "Foreign donations"], ["gfn", "Google"]];
  const summary = `<div class="summary"><div class="hd">${flag(d, 1)}<div>${page ? `<h1>${esc(d.country)}</h1>` : `<h2 class="t">${esc(d.country)}</h2>`}<div class="sub">${esc(d.region)} · #${p} of ${DATA.length} overall</div></div></div>
    <div class="scorerow">${badge(d, 1)}<p><b style="color:var(--ink)">${esc(bandLabel(d))}</b> charity score.<br>${GROUPS.map((g, i) => `${g} ${Math.round(d.grp[i])}`).join(" · ")}</p></div>${parts(d)}
    <div class="facts2"><div><span>Registration fee</span><b>${esc(feeTxt(d))}</b></div><div><span>Time to register</span><b>${esc(timeTxt(d))}</b></div></div>
    <ul class="verdicts">${V.map(([k, l]) => `<li><span class="vl">${l}</span>${chip(k, d)}</li>`).join("")}</ul>
    <div class="cacts"><button type="button" class="btn${inC ? "" : " primary"}" data-add="${esc(d.country)}"${!inC && S.cmp.length >= 5 ? " disabled" : ""}>${inC ? "✓ In compare" : "+ Add to compare"}</button>
      ${page ? "" : `<a class="btn" href="#/country/${slug(d.country)}">Open full page</a>`}</div></div>`;
  const TABS = [["reg", "Registering"], ["bank", "Banking"], ["tax", "Tax and compliance"], ["src", "Sources"]];
  const body = {
    reg: sec("Main bottleneck", d.bottleneck) + sec("Entity to register", d.entity) + sec("Local requirements", d.requirements) + sec("Cost and time in practice", d.cost_time) + sec("Fee note", d.fee_usd) + sec("Time note", d.time_to_reg),
    bank: `<div class="sec"><h3>Charity bank account</h3><p style="margin-bottom:6px">${chip("bank_cat", d)}</p><p>${esc(d.bank_access)}</p></div>
      <div class="sec"><h3>Personal account as a non-resident</h3><p style="display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px">${chip("pb_status", d)}${chip("pb_method", d)}${chip("pb_res", d)}</p>
        <div class="costs"><div><span>Opening fee</span><b>${esc(usd(d.pb_open))}</b></div><div><span>Monthly fee</span><b>${esc(usd(d.pb_month))}</b></div><div><span>Min deposit</span><b>${esc(dep(d.pb_mindep))}</b></div><div><span>First year</span><b>${esc(usd(d.pb_year))}</b></div></div>
        <p style="color:var(--muted);font-size:13px">${esc(d.pb_costnote)}${d.pb_conf === "low" ? " Low-confidence research: confirm with the bank." : ""}</p></div>`
      + sec("Documents", d.pb_docs) + sec("Banks", d.pb_banks) + sec("Restrictions", d.pb_restr) + sec("Alternatives", d.pb_alt),
    tax: sec("Tax-exempt status", d.tax_exempt) + sec("Donor tax deductions", d.deduction) + sec("Foreign donations", d.donor_restr) + sec("Annual compliance", d.compliance)
      + `<div class="sec"><h3>Score breakdown · ${d.cs} / 100</h3><div class="breakdown">${FACTORS.map(([k, l, mx, g]) => `<div class="bk"><span>${esc(l)}</span><span class="tr"><i class="p${g}" style="width:${100 * d.pts[k] / mx}%"></i></span><b>${Math.round(d.pts[k] * 10) / 10}/${mx}</b></div>`).join("")}</div></div>`,
    src: `${srcs(d.sources).length ? `<div class="sec"><h3>Charity sources</h3><ul>${srcs(d.sources).map(s => `<li>${link(s)}</li>`).join("")}</ul></div>` : ""}
      ${srcs(d.pb_src).length ? `<div class="sec"><h3>Banking sources (confidence: ${esc(d.pb_conf)})</h3><ul>${srcs(d.pb_src).map(s => `<li>${link(s)}</li>`).join("")}</ul></div>` : ""}
      ${notes.length ? `<div class="sec"><h3>Research notes</h3><ul>${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>` : ""}`,
  };
  return summary + `<div class="ctabs" role="tablist" aria-label="${esc(d.country)} details">${TABS.map(([k, l]) => `<button type="button" role="tab" id="t-${mode}-${k}" data-ct="${k}" aria-selected="${k === t}" aria-controls="tb-${mode}">${l}</button>`).join("")}</div>
    <div class="tabbody" role="tabpanel" id="tb-${mode}" aria-labelledby="t-${mode}-${t}" data-bodies='${esc(JSON.stringify(body))}'>${body[t]}</div>`;
}
function bindTabs(root) {
  root.querySelectorAll("[data-ct]").forEach(b => b.onclick = () => {
    ctab.cur = b.dataset.ct; const tb = root.querySelector(".tabbody"), bodies = JSON.parse(tb.dataset.bodies);
    root.querySelectorAll("[data-ct]").forEach(x => x.setAttribute("aria-selected", x === b)); tb.innerHTML = bodies[b.dataset.ct]; tb.setAttribute("aria-labelledby", b.id);
  });
  root.querySelector(".ctabs")?.addEventListener("keydown", e => { if (!["ArrowRight", "ArrowLeft"].includes(e.key)) return; const bs = [...root.querySelectorAll("[data-ct]")], i = bs.indexOf(document.activeElement);
    const n = bs.at((i + (e.key === "ArrowRight" ? 1 : -1)) % bs.length); n.focus(); n.click(); });
}
function renderCountryPage() {
  const d = bySlug.get(arg), back = prevView && prevView !== "country" ? prevView : "map";
  const backLbl = { home: "Home", map: "Map", rankings: "Rankings", compare: "Compare", banking: "Banking", about: "How it works" }[back];
  $("v-country").innerHTML = `<nav class="crumbs" aria-label="Breadcrumb"><a href="#/${back === "home" ? "" : back}" id="crumbBack">${backLbl}</a> › <a href="#/map?f=${encodeURIComponent("region:" + d.region)}">${esc(d.region)}</a> › <span aria-current="page">${esc(d.country)}</span></nav>
    <div class="cgrid"><div class="card" id="cpageL"></div><div class="card" id="cpageR"></div></div>`;
  const html = countryHTML(d, "page"), i = html.indexOf('<div class="ctabs"');
  $("cpageL").innerHTML = html.slice(0, i); $("cpageR").innerHTML = html.slice(i); bindTabs($("cpageR"));
  $("crumbBack").addEventListener("click", e => { if (history.length > 1 && prevView) { e.preventDefault(); history.back(); } });
}

/* ================= COMPARE ================= */
const ATTRS = [
  { g: "Registering" },
  { k: "difficulty", label: "Difficulty", note: d => d.bottleneck },
  { k: "no_presence", label: "Setting up", note: d => d.requirements },
  { k: "fee_bin", label: "Registration fee", x: feeTxt, note: d => d.fee_usd },
  { k: "time_bin", label: "Time to register", x: timeTxt, note: d => d.time_to_reg },
  { k: "funding_cat", label: "Foreign donations", note: d => d.donor_restr },
  { k: "gfn", label: "Google for Nonprofits" },
  { g: "Banking" },
  { k: "bank_cat", label: "Charity bank account", note: d => d.bank_access },
  { k: "pb_status", label: "Personal account", note: d => d.pb_banks },
  { k: "pb_method", label: "Opening it", note: d => d.pb_docs },
  { k: "pb_res", label: "Local residence", note: d => d.pb_restr },
  { k: "pb_cost_bin", label: "Account fees", x: d => d.pb_year ? usd(d.pb_year) + " a year" : null, note: d => d.pb_costnote },
  { k: "pb_dep_bin", label: "Minimum deposit", x: d => d.pb_mindep ? dep(d.pb_mindep) : null, note: d => d.pb_dep },
  { g: "Research" },
  { k: "confidence", label: "Research confidence" },
];
const TEXTS = [["bottleneck", "Main bottleneck"], ["entity", "Entity to register"], ["requirements", "Local requirements"], ["tax_exempt", "Tax-exempt status"], ["compliance", "Annual compliance"], ["pb_alt", "Banking alternatives"]];
const NOTES = [];
function renderCompare() {
  NOTES.length = 0;
  const cs = S.cmp.map(c => byName.get(c)), slots = [...cs, ...Array(Math.max(0, Math.min(5, cs.length + 1) - cs.length)).fill(null)];
  if (S.diff == null) S.diff = cs.length >= 3;
  const differs = a => cs.length > 1 && new Set(cs.map(d => d[a.k])).size > 1;
  const cellHTML = (a, d) => { const [l, c] = cat(a.k, d), x = a.x?.(d), n = a.note?.(d); let i = -1; if (n) { i = NOTES.length; NOTES.push([`${d.country}: ${a.label}`, n]); }
    return `<td class="cell c-${c}${low(a.k, d) ? " hatch" : ""}"><span aria-hidden="true">${SYM[c]}</span> ${esc(l)}${x && x !== l && x !== "—" ? `<span class="v">${esc(x)}</span>` : ""}${i >= 0 ? `<button type="button" class="info" data-note="${i}" aria-label="Details: ${esc(a.label)}">i</button>` : ""}</td>`; };
  let h = `<colgroup><col class="l">${slots.map(() => "<col>").join("")}</colgroup><thead><tr><th class="l"><span class="lbl">${cs.length} of 5 picked</span></th>`
    + slots.map(d => `<th>${d ? `<div class="chead">${flag(d, 1)}<a href="#/country/${slug(d.country)}">${esc(d.country)}</a>${badge(d)} <span class="lbl">#${POWER.pos.get(d.country)}</span><br><button type="button" class="rm" data-add="${esc(d.country)}">Remove</button></div>`
      : `<div class="chead"><label class="sr" for="addCountry">Add a country</label><input id="addCountry" list="allC" placeholder="+ Add a country"></div>`}</th>`).join("") + `</tr></thead><tbody>`;
  let grp = null, shown = 0;
  for (const a of ATTRS) {
    if (a.g) { grp = a.g; continue; }
    if (S.diff && cs.length > 1 && !differs(a)) continue;
    if (grp) { h += `<tr class="grp"><td class="l">${esc(grp)}</td>${slots.map(() => "<td></td>").join("")}</tr>`; grp = null; }
    h += `<tr><td class="l">${esc(a.label)}</td>${slots.map(d => d ? cellHTML(a, d) : `<td class="cell blank"></td>`).join("")}</tr>`; shown++;
  }
  h += `<tr class="grp"><td class="l">Details (click a row to expand)</td>${slots.map(() => "<td></td>").join("")}</tr>`
    + TEXTS.map(([k, l]) => `<tr class="textrow"><td class="l">${esc(l)}</td>${slots.map(d => d ? `<td class="txt"><div class="clamp">${esc(d[k] || "—")}</div></td>` : "<td></td>").join("")}</tr>`).join("");
  $("v-compare").innerHTML = `<div class="shead"><div><h1>Compare</h1><p>Two to five countries side by side. Tap <b>i</b> in a cell for the research note behind it.</p></div></div>
    ${cs.length ? `<div class="cmptools"><label class="switch"><input type="checkbox" id="diffOnly"${S.diff ? " checked" : ""}> Show differences only</label>
      <span class="key">${["ok", "mid", "warn", "bad", "na"].map(c => `<span><i class="c-${c}"></i>${SYM[c]} ${{ ok: "best", mid: "good", warn: "caution", bad: "hardest", na: "no data" }[c]}</span>`).join("")}<span><i class="c-mid hatch"></i>low confidence</span></span>
      <button type="button" class="btn link" id="cmpClear">Clear all</button></div>
      <div class="cmpwrap"><table class="cmp">${h}</tbody></table></div>${S.diff && cs.length > 1 && !shown ? `<p class="empty">These countries match on every rated row. Turn off "Show differences only" to see them.</p>` : ""}`
    : `<div class="card empty"><p style="font-size:16px;color:var(--ink)">Pick countries to compare.</p><p>Use <b>+</b> on any ranking row or <b>Add to compare</b> on a country, or type one here.</p>
       <p><input list="allC" id="addCountry" class="sel" style="max-width:320px;width:100%" placeholder="+ Add a country" aria-label="Add a country"></p>
       <p>Or try <a href="#/compare/estonia,georgia,united-kingdom">Estonia, Georgia and the UK</a>.</p></div>`}
    <datalist id="allC">${DATA.filter(d => !S.cmp.includes(d.country)).sort((a, b) => a.country.localeCompare(b.country)).map(d => `<option value="${esc(d.country)}">`).join("")}</datalist>`;
  const hh = "#/compare" + (S.cmp.length ? "/" + S.cmp.map(slug).join(",") : "");
  if (location.hash !== hh) history.replaceState(null, "", hh);
}
document.addEventListener("change", e => {
  if (e.target.id === "addCountry" && byName.has(e.target.value)) toggleCmp(e.target.value);
  if (e.target.id === "diffOnly") { S.diff = e.target.checked; renderCompare(); }
});
document.addEventListener("input", e => { if (e.target.id === "addCountry" && byName.has(e.target.value)) toggleCmp(e.target.value); });

/* ================= ABOUT ================= */
function renderAbout() {
  const conf = k => DATA.filter(d => d.pb_conf === k).length;
  $("v-about").innerHTML = `<div class="shead"><div><h1>How it works</h1><p>What the scores mean, where the data comes from and how to download it.</p></div></div>
    <div class="about">
      <div class="card"><h2>The charity score</h2><table><thead><tr><th>Factor</th><th>Points</th></tr></thead><tbody>${FACTORS.map(([, l, mx, g]) => `<tr><td><i class="p${g}" style="display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px"></i>${esc(l)}</td><td>${mx}</td></tr>`).join("")}<tr><td><b>Total</b></td><td><b>100</b></td></tr></tbody></table>
        <p style="font-size:13.5px;color:var(--muted)">Fee and speed score by percentile among countries with a stated value. Equal scores share a rank.</p></div>
      <div class="card"><h2>Colours</h2><p><b>Charity score</b></p><div class="key">${BANDS.map(([, , c], i) => `<span><i class="bg-${c}"></i>${esc(CAT.band[c][0])}</span>`).join("")}</div>
        <p style="margin-top:14px"><b>Status of one fact</b> (always with a symbol)</p><div class="key">${["ok", "mid", "warn", "bad", "na"].map(c => `<span><i class="c-${c}"></i>${SYM[c]} ${{ ok: "best", mid: "good", warn: "caution", bad: "hardest", na: "no data" }[c]}</span>`).join("")}<span><i class="c-mid hatch"></i>low-confidence research</span></div></div>
      <div class="card full"><h2>Plain words</h2><table><thead><tr><th>Label</th><th>Means</th></tr></thead><tbody>${["no_presence", "bank_cat", "pb_status", "pb_method", "funding_cat"].flatMap(k => Object.values(CAT[k]).map(([l, , def]) => `<tr><td>${esc(l)}</td><td>${esc(def)}</td></tr>`)).join("")}</tbody></table></div>
      <div class="card"><h2>Research</h2><p>Every row was researched and re-checked against statutes, gazettes, registries, tax authorities and central banks, last re-verified October 2026. Personal-banking research (October 2026): ${conf("high")} high, ${conf("medium")} medium and ${conf("low")} low-confidence rows; low-confidence rows are hatched.</p></div>
      <div class="card"><h2>Download the data</h2><p><a href="__REPO__/raw/main/charities_by_country_v2.csv" target="_blank" rel="noopener">Charity data (CSV)</a> · <a href="__REPO__/raw/main/banking_by_country.csv" target="_blank" rel="noopener">Banking data (CSV)</a> · <a href="__REPO__/raw/main/charities_by_country_v2.xlsx" target="_blank" rel="noopener">Workbook (Excel)</a> · <a href="__REPO__" target="_blank" rel="noopener">Source code</a></p>
        <p style="font-size:13.5px;color:var(--muted)">Research, not legal or financial advice. Confirm with the registry or bank before you act.</p></div>
    </div>`;
}

/* ================= filters panel ================= */
let lastFocus = null;
function renderFilterBody() {
  const n = DATA.filter(d => passes(d)).length;
  $("fbody").innerHTML = Object.entries(FACETS).map(([g, fs]) => `<div class="fgroup"><h3>${esc(g)}</h3>${fs.map(([k, l]) => `<fieldset class="facet"><legend>${esc(l)}</legend><div class="opts">${optsOf(k).map(([v, lb, c, def]) => {
      const cnt = DATA.filter(d => d[k] === v && passes(d, k)).length;
      return `<button type="button" class="opt${cnt ? "" : " zero"}" data-f="${k}" data-v="${esc(v)}" aria-pressed="${S.F[k].has(v)}"${def ? ` title="${esc(def)}"` : ""}>${c ? `<i style="background:var(--${c})"></i>` : ""}${esc(lb)} <span class="n">${cnt}</span></button>`; }).join("")}</div></fieldset>`).join("")}
      ${g === "Registering" ? `<div class="limits"><div><label for="fFee">Fee up to (US$)</label><input id="fFee" type="number" min="0" inputmode="numeric" placeholder="Any" value="${esc(S.fee)}"></div><div><label for="fDays">Time up to (days)</label><input id="fDays" type="number" min="0" inputmode="numeric" placeholder="Any" value="${esc(S.days)}"></div></div>` : ""}</div>`).join("")
    + `<div class="fgroup ftext"><label for="fText">Contains text</label><input id="fText" type="search" placeholder="e.g. foundation, notary" value="${esc(S.q)}"></div>`;
  $("fShow").textContent = `Show ${n} ${n === 1 ? "country" : "countries"}`;
}
function openFilters() { lastFocus = document.activeElement; renderFilterBody(); $("fpanel").hidden = false; $("scrim").hidden = false; $("fClose").focus(); }
function closeFilters() { $("fpanel").hidden = true; $("scrim").hidden = true; lastFocus?.focus?.(); }
$("fClose").onclick = closeFilters; $("scrim").onclick = closeFilters; $("fShow").onclick = closeFilters;
$("fClear").onclick = () => { clearAll(); renderFilterBody(); };
function clearAll() { for (const k in S.F) S.F[k].clear(); S.q = S.fee = S.days = ""; rerender(); }
$("fbody").addEventListener("input", e => {
  const id = e.target.id; if (!["fFee", "fDays", "fText"].includes(id)) return;
  S[{ fFee: "fee", fDays: "days", fText: "q" }[id]] = e.target.value.trim(); rerender();
  const n = DATA.filter(d => passes(d)).length; $("fShow").textContent = `Show ${n} ${n === 1 ? "country" : "countries"}`;
});
$("fpanel").addEventListener("keydown", e => { if (e.key !== "Tab") return; const f = [...$("fpanel").querySelectorAll("button, input")].filter(x => !x.disabled);
  if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f.at(-1).focus(); } else if (!e.shiftKey && document.activeElement === f.at(-1)) { e.preventDefault(); f[0].focus(); } });

/* ================= compare tray ================= */
function toggleCmp(c) {
  if (S.cmp.includes(c)) S.cmp = S.cmp.filter(x => x !== c); else if (S.cmp.length < 5) S.cmp.push(c);
  save(); renderTray();
  const f = document.activeElement?.dataset?.add;
  if (view === "compare") renderCompare(); else if (view === "country") renderCountryPage(); else rerender();
  if (f) document.querySelector(`[data-add="${CSS.escape(f)}"]`)?.focus();
  announce(S.cmp.includes(c) ? `${c} added to compare` : `${c} removed from compare`);
}
function renderTray() {
  $("tray").hidden = !S.cmp.length || view === "compare";
  $("trayN").textContent = S.cmp.length;
  $("trayGo").href = "#/compare/" + S.cmp.map(slug).join(",");
  $("trayNames").innerHTML = S.cmp.map(c => `<span class="tag">${esc(c)}<button type="button" data-add="${esc(c)}" aria-label="Remove ${esc(c)}">×</button></span>`).join("");
}
$("trayClear").onclick = () => { S.cmp = []; save(); renderTray(); if (view !== "compare") rerender(); };

/* ================= global clicks + keys ================= */
document.addEventListener("click", e => {
  const t = e.target;
  if (t.closest("[data-open-filters]")) return openFilters();
  if (t.closest("[data-clear]")) return clearAll();
  if (t.closest("[data-closepanel]")) return go("#/map" + query(true));
  if (t.id === "cmpClear") { S.cmp = []; save(); return renderCompare(); }
  if (t.id === "wReset") { S.W = { ...W_DEFAULT }; return rerender(); }
  const add = t.closest("[data-add]"); if (add) { e.preventDefault(); e.stopPropagation(); return toggleCmp(add.dataset.add); }
  const o = t.closest(".opt, .leg"); if (o) { const s = S.F[o.dataset.f]; s.has(o.dataset.v) ? s.delete(o.dataset.v) : s.add(o.dataset.v);
    if (s.size === optsOf(o.dataset.f).length) s.clear(); rerender(); if (!$("fpanel").hidden) { renderFilterBody(); $("fbody").querySelector(`[data-f="${o.dataset.f}"][data-v="${CSS.escape(o.dataset.v)}"]`)?.focus(); } return; }
  const rm = t.closest("[data-rm]"); if (rm) { const id = rm.dataset.rm; if (id.startsWith("f|")) { const [, k, v] = id.split("|"); S.F[k].delete(v); } else S[id] = ""; return rerender(); }
  const tr = t.closest("tr.textrow"); if (tr) return tr.querySelectorAll("td.txt").forEach(td => td.classList.toggle("open"));
  const row = t.closest(".rrow"); if (row) return go("#/country/" + slug(row.dataset.c));
});
document.addEventListener("input", e => { const w = e.target.dataset?.w; if (w) { S.W[w] = +e.target.value; $("wo-" + w).textContent = e.target.value; const p = e.target.id; rerender(); $(p)?.focus(); } });
document.addEventListener("keydown", e => {
  const typing = /INPUT|SELECT|TEXTAREA/.test(document.activeElement?.tagName);
  if (e.key === "/" && !typing) { e.preventDefault(); narrow() ? openMobileSearch() : $("search").focus(); return; }
  if (e.key === "Escape") { if (!$("modal").hidden) return closeModal(); if (!$("fpanel").hidden) return closeFilters(); if (!$("results").hidden) return closeResults(); if (!$("note").hidden) return closeNote(); if (view === "map" && arg) return go("#/map" + query(true)); }
  const row = document.activeElement?.closest?.(".rrow");
  if (row && !typing) {
    if (e.key === "Enter") return go("#/country/" + slug(row.dataset.c));
    if (e.key === "c") return toggleCmp(row.dataset.c);
    if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); (e.key === "ArrowDown" ? row.nextElementSibling : row.previousElementSibling)?.focus(); }
  }
});

/* notes popover */
function openNote(btn) { const [t, n] = NOTES[+btn.dataset.note] || []; if (!n) return; const box = $("note");
  box.innerHTML = `<b>${esc(t)}</b>${esc(n)}`; box.hidden = false; const r = btn.getBoundingClientRect();
  box.style.left = Math.max(8, Math.min(r.right - box.offsetWidth, innerWidth - box.offsetWidth - 8)) + "px";
  box.style.top = (r.bottom + 8 + box.offsetHeight > innerHeight ? r.top - box.offsetHeight - 8 : r.bottom + 8) + "px"; }
function closeNote() { $("note").hidden = true; }
document.addEventListener("click", e => { const b = e.target.closest("[data-note]"); if (b) { e.preventDefault(); e.stopPropagation(); openNote(b); } else if (!e.target.closest("#note")) closeNote(); }, true);
addEventListener("scroll", closeNote, { passive: true });

/* ================= search ================= */
function searchResults(t) {
  t = t.trim().toLowerCase(); if (!t) return [];
  const cs = DATA.filter(d => d.country.toLowerCase().includes(t)).sort((a, b) => b.country.toLowerCase().startsWith(t) - a.country.toLowerCase().startsWith(t) || a.country.localeCompare(b.country)).slice(0, 6);
  const rs = REGIONS.filter(r => r.toLowerCase().includes(t)).slice(0, 3);
  const tx = t.length > 2 ? DATA.filter(d => !cs.includes(d) && HAY.get(d.country).includes(t)).slice(0, 5) : [];
  return [...cs.map(d => ["c", d]), ...rs.map(r => ["r", r]), ...tx.map(d => ["t", d])];
}
function resultsHTML(res, t) {
  if (!res.length) return `<p class="empty" style="padding:14px">No match for “${esc(t)}”.</p>`;
  let h = "", last;
  for (const [k, x] of res) {
    if (k !== last) { h += `<div class="grp lbl">${{ c: "Countries", r: "Regions", t: "Mentioned in the research" }[k]}</div>`; last = k; }
    h += k === "r" ? `<a href="#/map?f=${encodeURIComponent("region:" + x)}">${esc(x)}<small>show on map</small></a>`
      : `<a href="#/country/${slug(x.country)}">${flag(x)}${esc(x.country)}<small>${k === "t" ? esc(x.region) : badge(x)}</small></a>`;
  }
  return h;
}
const closeResults = () => { $("results").hidden = true; $("search").setAttribute("aria-expanded", "false"); };
$("search").addEventListener("input", e => { const t = e.target.value; $("results").innerHTML = resultsHTML(searchResults(t), t); $("results").hidden = !t.trim(); $("search").setAttribute("aria-expanded", !!t.trim()); });
$("search").addEventListener("keydown", e => {
  const links = [...$("results").querySelectorAll("a")];
  if (e.key === "Enter" && links[0]) { e.preventDefault(); links[0].click(); $("search").value = ""; $("search").blur(); }
  if (e.key === "ArrowDown" && links[0]) { e.preventDefault(); links[0].focus(); }
});
$("results").addEventListener("keydown", e => { const links = [...$("results").querySelectorAll("a")], i = links.indexOf(document.activeElement);
  if (e.key === "ArrowDown") { e.preventDefault(); links[Math.min(i + 1, links.length - 1)].focus(); }
  if (e.key === "ArrowUp") { e.preventDefault(); i <= 0 ? $("search").focus() : links[i - 1].focus(); } });
$("results").addEventListener("click", e => { if (e.target.closest("a")) { $("search").value = ""; closeResults(); } });
document.addEventListener("click", e => { if (!e.target.closest(".search")) closeResults(); });
function openMobileSearch() {
  modal(`<h2 id="mTitle">Search</h2><input class="sel" id="mq" type="search" style="width:100%;margin-top:12px" placeholder="Country, region or rule" aria-label="Search"><div class="results" id="mres" style="position:static;box-shadow:none;border:0;padding:6px 0;max-height:none"></div>`);
  $("mq").addEventListener("input", e => { $("mres").innerHTML = resultsHTML(searchResults(e.target.value), e.target.value); });
  $("mres").addEventListener("click", e => { if (e.target.closest("a")) closeModal(); });
  $("mq").focus();
}
$("mobSearch").onclick = openMobileSearch;

/* ================= checker ================= */
function modal(html) { lastFocus = document.activeElement; $("mbox").innerHTML = `<button type="button" class="iconbtn x" id="mClose" aria-label="Close">✕</button>` + html; $("modal").hidden = false; }
function closeModal() { $("modal").hidden = true; lastFocus?.focus?.(); }
$("modal").addEventListener("click", e => { if (e.target.id === "modal" || e.target.closest("#mClose") || e.target.closest(".vgo")) closeModal(); });
function openChecker() {
  modal(`<h2 id="mTitle">Charity Checker</h2><p style="color:var(--muted);margin:4px 0 0">A quick yes-or-no for one country, for a founder living in Australia.</p>
    <label for="ckTo">Country</label><select class="sel" id="ckTo"><option value="">Choose a country…</option>${[...DATA].sort((a, b) => a.country.localeCompare(b.country)).map(d => `<option>${esc(d.country)}</option>`).join("")}</select><div id="ckOut"></div>`);
  $("ckTo").addEventListener("change", () => { const d = byName.get($("ckTo").value); if (!d) return $("ckOut").innerHTML = "";
    const row = (k, q, val) => { const [l, c] = cat(k, d); return `<div class="vrow c-${c}${low(k, d) ? " hatch" : ""}"><span>${esc(q)}</span><b><span aria-hidden="true">${SYM[c]}</span> ${esc(val ?? l)}</b></div>`; };
    $("ckOut").innerHTML = `<div class="vrows">${row("difficulty", "How hard is it?")}${row("no_presence", "Can I do it from Australia?")}${row("fee_bin", "Registration fee", feeTxt(d))}${row("time_bin", "How long?", timeTxt(d))}
      ${row("bank_cat", "Can the charity get a bank account?")}${row("pb_status", "Can I open a personal account?")}${row("pb_method", "Without visiting?")}${row("gfn", "Google for Nonprofits?", d.gfn === "Yes" ? "Yes" : "No")}</div>
      <p style="font-size:14px;margin:12px 0 0"><b>Main bottleneck:</b> ${esc(d.bottleneck)}</p>
      <div class="cacts" style="margin-top:12px"><a class="btn primary vgo" href="#/country/${slug(d.country)}">Open ${esc(d.country)}</a><button type="button" class="btn" data-add="${esc(d.country)}">+ Add to compare</button></div>`; });
  $("ckTo").focus();
}
$("checkerBtn").onclick = openChecker; $("checkerTab").onclick = openChecker;
$("modal").addEventListener("keydown", e => { if (e.key !== "Tab") return; const f = [...$("mbox").querySelectorAll("button, input, select, a")];
  if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f.at(-1).focus(); } else if (!e.shiftKey && document.activeElement === f.at(-1)) { e.preventDefault(); f[0].focus(); } });

/* ================= theme ================= */
const THEMES = ["system", "light", "dark"];
function applyTheme() {
  if (S.theme === "system") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", S.theme);
  $("themeBtn").setAttribute("aria-label", { system: "Theme: follows your system (click for light)", light: "Theme: light (click for dark)", dark: "Theme: dark (click to follow system)" }[S.theme]);
  $("themeBtn").title = $("themeBtn").getAttribute("aria-label");
}
$("themeBtn").onclick = () => { S.theme = THEMES[(THEMES.indexOf(S.theme) + 1) % 3]; applyTheme(); save(); mapObj = null; if (view === "map") $("v-map").innerHTML = ""; route(); };
matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change", () => { if (S.theme === "system") { mapObj = null; $("v-map").innerHTML = ""; route(); } });
applyTheme();
route();
</script>
"""

if __name__ == "__main__":
    main()
