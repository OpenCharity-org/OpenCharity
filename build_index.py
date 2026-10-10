#!/usr/bin/env python3
"""Build the OpenCharity Index: webapp/atlas.html (artifact fragment) and docs/index.html (GitHub Pages).

A rank-and-compare site for the charity dataset, laid out like a passport index:
  #/explore          wall of country "covers"; FIND searches
  #/rank             Global Charity Power Rank: sticky world map + ranked list grouped by
                     tied rank, each row a stacked score bar; rank-by menu, stackable filters
  #/banking          the same view ranked by personal bank access for non-residents
  #/compare/a,b,c    up to 5 countries side by side, every attribute a colour-coded cell
  #/country/<slug>   country dashboard: cover, key stats, map, score breakdown,
                     colour-coded requirements and the full research text with sources
  Charity Checker    pick a country, get the verdict

Charity score (0-100) = registration ease 25 + remote founding 20 + fee 10 + speed 10
+ charity bank account 10 + personal account 10 + open foreign funding 5 + Google for
Nonprofits 10. Fee and speed score by percentile among countries with a stated value.

Reads the same inputs as build_atlas.py (charities_by_country_v2.csv, banking_by_country.csv,
webapp/geo/countries-50m.json) plus webapp/flags/*.svg (country-flag-icons, MIT).
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

# fields the page never shows
DROP = ("score",)


def main():
    data, src_name = build_data()
    data = [enrich(d) for d in data]
    add_banking(data)
    flags = {}
    for d in data:
        for k in DROP:
            d.pop(k, None)
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
    head, body = html.split('<header class="top"', 1)
    DOCS.parent.mkdir(exist_ok=True)
    DOCS.write_text('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                    f'<meta name="description" content="Rank and compare {len(data)} countries by how easy it is to register a charity '
                    'and open a bank account from Australia.">\n'
                    '<meta property="og:title" content="OpenCharity Index">\n'
                    f'<meta property="og:description" content="Global Charity Power Rank: {len(data)} jurisdictions ranked by how easy, '
                    'cheap and fast it is to register a charity from Australia.">\n'
                    '<meta property="og:image" content="https://raw.githubusercontent.com/OpenCharity-org/OpenCharity/main/docs/screenshots/rank.png">\n'
                    '<meta property="og:url" content="https://opencharity-org.github.io/OpenCharity/">\n'
                    '<meta name="twitter:card" content="summary_large_image">\n'
                    + head + '</head>\n<body>\n<header class="top"' + body + '\n</body>\n</html>\n', encoding="utf-8")
    (DOCS.parent / ".nojekyll").write_text("", encoding="utf-8")
    print(f"wrote {OUT} and {DOCS} ({len(data)} jurisdictions, {len(html) // 1024} KB)")


TEMPLATE = r"""<title>OpenCharity Index</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Source+Serif+4:ital,opsz,wght@1,8..60,400&display=swap">
<style>
/* Dark-first, gold-accented index layout. Views: explore wall, ranked list beside a sticky map,
   side-by-side compare grid of colour-coded cells, per-country dashboard. */
:root {
  --bg: #121212; --bar: #000000; --surface: #1a1a1a; --surface-2: #222222; --line: #2b2b2b;
  --ink: #f1f1f1; --muted: #8e8e8e; --gold: #d29e68; --gold-ink: #1a1208; --gold-soft: #3a2c1e;
  --cta: #2a0f3d; --cta-line: #8a5bc4;
  --ok: #1f9e48; --mid: #2b6fdc; --warn: #ec840b; --bad: #d12f35; --na: #4f4f4f; --cell-ink: #ffffff;
  --s1: #4a8df8; --s2: #1fb37c; --s3: #f2a42f; --s4: #b46ae3;
  --b5: #1a9850; --b4: #66bd63; --b3: #b8df6a; --b2: #fee08b; --b1: #fc8d59; --b0: #d73027;
  --map-lo: #3a2f26; --map-hi: #dba873; --map-none: #262626;
  --f-ui: "Outfit", "Avenir Next", "Segoe UI", system-ui, sans-serif;
  --f-serif: "Source Serif 4", Georgia, "Times New Roman", serif;
  color-scheme: dark;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: #121212; --bar: #000000; --surface: #1a1a1a; --surface-2: #222222; --line: #2b2b2b;
  --ink: #f1f1f1; --muted: #8e8e8e; --gold: #d29e68; --gold-ink: #1a1208; --gold-soft: #3a2c1e;
  --map-lo: #3a2f26; --map-hi: #dba873; --map-none: #262626; color-scheme: dark; } }
:root[data-theme="dark"] {
  --bg: #121212; --bar: #000000; --surface: #1a1a1a; --surface-2: #222222; --line: #2b2b2b;
  --ink: #f1f1f1; --muted: #8e8e8e; --gold: #d29e68; --gold-ink: #1a1208; --gold-soft: #3a2c1e;
  --map-lo: #3a2f26; --map-hi: #dba873; --map-none: #262626; color-scheme: dark; }
:root[data-theme="light"] {
  --bg: #f4f1ec; --bar: #ffffff; --surface: #ffffff; --surface-2: #f0ebe4; --line: #e0d8cd;
  --ink: #1d1a16; --muted: #6d655b; --gold: #9c6a36; --gold-ink: #ffffff; --gold-soft: #f1e4d4;
  --cta: #f3ecfb; --cta-line: #7b4bb5;
  --map-lo: #efe3d3; --map-hi: #a36d36; --map-none: #e3ddd5; color-scheme: light;
  --b3: #a6d96a; --b2: #fdd257; --s3: #e8951c; }

* { box-sizing: border-box; }
[hidden] { display: none !important; }
html, body { margin: 0; }
body { background: var(--bg); color: var(--ink); font: 15px/1.5 var(--f-ui); -webkit-font-smoothing: antialiased; }
a { color: var(--gold); }
button, input, select { font: inherit; color: inherit; }
:focus-visible { outline: 2px solid var(--gold); outline-offset: 2px; }
.serif { font-family: var(--f-serif); font-style: italic; }

/* ---------- header ---------- */
header.top { position: sticky; top: 0; z-index: 30; background: var(--bar); border-bottom: 1px solid var(--line); }
.topin { max-width: 1440px; margin: 0 auto; display: flex; align-items: center; gap: 18px; padding: 0 20px; min-height: 64px; }
.brand { display: flex; align-items: center; gap: 12px; text-decoration: none; color: var(--ink); flex: none; }
.mark { width: 34px; height: 46px; border: 1.5px solid var(--gold); border-radius: 6px; display: grid; place-items: center; }
.mark svg { width: 18px; height: 18px; }
.wordmark { font-weight: 700; font-size: 22px; letter-spacing: .04em; line-height: 1; }
.wordmark span { font-weight: 300; }
.wordmark small { display: block; font-size: 9px; letter-spacing: .32em; color: var(--gold); font-weight: 500; margin-top: 4px; }
nav.main { margin-left: auto; display: flex; align-items: stretch; align-self: stretch; }
nav.main a { display: flex; align-items: center; padding: 0 12px; text-decoration: none; text-transform: uppercase; font-size: 14.5px; letter-spacing: .02em; color: var(--gold); }
nav.main a[aria-current="page"] { background: #e9e9e9; color: #555; }
:root[data-theme="light"] nav.main a[aria-current="page"] { background: var(--gold); color: var(--gold-ink); }
nav.main a:hover:not([aria-current]) { color: var(--ink); }
.more { position: relative; display: flex; align-items: center; }
.more > button { background: none; border: 0; color: var(--gold); font-size: 22px; line-height: 1; padding: 6px 8px; cursor: pointer; letter-spacing: .1em; }
.menu { position: absolute; right: 0; top: calc(100% + 10px); background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 6px; min-width: 210px; box-shadow: 0 12px 30px rgba(0,0,0,.35); }
.menu a, .menu button { display: block; width: 100%; text-align: left; background: none; border: 0; padding: 9px 12px; border-radius: 6px; color: var(--ink); text-decoration: none; font-size: 14px; cursor: pointer; }
.menu a:hover, .menu button:hover { background: var(--surface-2); }
.cta { flex: none; background: var(--cta); border: 1.5px solid var(--cta-line); color: var(--ink); border-radius: 999px; padding: 7px 18px; font-weight: 600; font-size: 14.5px; cursor: pointer; }
.cta:hover { filter: brightness(1.2); }

main { max-width: 1440px; margin: 0 auto; padding: 0 20px 70px; }
.ttl { text-align: center; padding: 22px 0 14px; }
.ttl h1 { margin: 0; color: var(--gold); font-weight: 500; font-size: 30px; line-height: 1.15; }
.ttl p { margin: 4px 0 0; font-size: 15.5px; }
.goldbtn { background: none; border: 1.5px solid var(--gold); color: var(--gold); padding: 9px 22px; text-transform: uppercase; font-weight: 600; letter-spacing: .04em; cursor: pointer; }
.goldbtn:hover { background: var(--gold); color: var(--gold-ink); }
.goldbtn.fill { background: var(--gold); color: var(--gold-ink); }

/* ---------- covers ---------- */
.cover { --w: 56px; width: var(--w); flex: none; aspect-ratio: 2 / 3; position: relative; container-type: inline-size; display: block;
  background: radial-gradient(120% 90% at 30% 20%, color-mix(in srgb, var(--pc) 78%, #fff 22%), var(--pc) 55%, color-mix(in srgb, var(--pc) 70%, #000)); border-radius: 2px 5px 5px 2px;
  box-shadow: inset 4cqw 0 0 rgba(0,0,0,.28), inset 0 0 0 1px rgba(255,255,255,.06), 0 1px 3px rgba(0,0,0,.5); color: #e2bc84; overflow: hidden; }
.cover .ci { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: 10cqw 7cqw 9cqw; }
.cover .ct { font-size: 9cqw; line-height: 1.12; text-transform: uppercase; text-align: center; letter-spacing: .06em; font-weight: 600; max-height: 3.4em; overflow: hidden; }
.cover .cf { width: 50%; aspect-ratio: 1; border-radius: 50%; background-size: cover; background-position: center; box-shadow: 0 0 0 3cqw rgba(226,188,132,.85), 0 0 0 5cqw rgba(0,0,0,.25); filter: saturate(.8) contrast(.95); }
.cover .cb { font-size: 7.5cqw; letter-spacing: .28em; text-transform: uppercase; opacity: .85; font-weight: 500; }
.flag { display: inline-block; width: 22px; aspect-ratio: 3 / 2; background-size: cover; background-position: center; border-radius: 2px; flex: none; box-shadow: 0 0 0 1px rgba(0,0,0,.25); vertical-align: -3px; }

/* ---------- explore ---------- */
.exhead { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; }
.exhead .ttl { grid-column: 2; }
.exhead .goldbtn { grid-column: 3; justify-self: end; }
.extools { display: flex; flex-wrap: wrap; gap: 6px; justify-content: center; margin: 0 0 14px; }
.chipbtn { background: var(--surface); border: 1px solid var(--line); color: var(--muted); border-radius: 999px; padding: 4px 12px; font-size: 13px; cursor: pointer; }
.chipbtn[aria-pressed="true"] { background: var(--gold); border-color: var(--gold); color: var(--gold-ink); }
.wall { display: grid; grid-template-columns: repeat(auto-fill, minmax(58px, 1fr)); gap: 5px; }
.wall a { display: block; position: relative; text-decoration: none; transition: transform .12s; }
.wall a .cover { --w: 100%; }
.wall a:hover, .wall a:focus-visible { transform: translateY(-3px) scale(1.06); z-index: 2; }
.wall a .sc { position: absolute; left: 50%; bottom: -4px; transform: translate(-50%, 100%); background: var(--gold); color: var(--gold-ink); font-size: 11px; font-weight: 700; padding: 1px 6px; border-radius: 4px; white-space: nowrap; opacity: 0; pointer-events: none; }
.wall a:hover .sc, .wall a:focus-visible .sc { opacity: 1; }

/* ---------- rank ---------- */
.rank { display: grid; grid-template-columns: minmax(0, 42fr) minmax(0, 58fr); gap: 24px; align-items: start; }
.rmap { position: sticky; top: 76px; height: calc(100vh - 92px); min-height: 460px; display: flex; flex-direction: column; }
.rmap .mapbox { flex: 1; min-height: 0; }
.mapbox { position: relative; }
.mapbox svg { width: 100%; height: 100%; display: block; }
.mapleg { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 14px 0 6px; }
.grad { width: 230px; height: 18px; border-radius: 2px; background: linear-gradient(90deg, var(--map-hi), var(--map-lo)); display: flex; justify-content: space-between; align-items: center; padding: 0 6px; font-size: 10.5px; text-transform: uppercase; color: #fff; font-weight: 500; }
:root[data-theme="light"] .grad span:last-child { color: var(--ink); }
.catleg { display: flex; gap: 10px; flex-wrap: wrap; font-size: 12.5px; color: var(--muted); }
.catleg i { display: inline-block; width: 11px; height: 11px; border-radius: 2px; margin-right: 5px; vertical-align: -1px; }
.zoom { position: absolute; left: 6px; top: 8px; display: grid; gap: 10px; z-index: 2; }
.zoom button { width: 28px; height: 28px; border-radius: 50%; border: 0; background: var(--gold); color: var(--gold-ink); font-size: 18px; font-weight: 700; line-height: 1; cursor: pointer; display: grid; place-items: center; }
path.cty { stroke: var(--bg); stroke-width: .4; cursor: pointer; transition: opacity .15s; }
path.cty.nodata { fill: var(--map-none); cursor: default; }
path.cty.dim, circle.dot.dim { opacity: .18; }
path.cty:hover { stroke: var(--ink); stroke-width: .8; }
path.cty.sel, circle.dot.sel { stroke: var(--ink); stroke-width: 1.6; }
#dMap path.cty.sel, #dMap circle.dot.sel { stroke: var(--gold); stroke-width: 2.4; }
circle.dot { stroke: var(--bg); stroke-width: .6; cursor: pointer; }
.stats { display: flex; gap: 26px; flex-wrap: wrap; border: 1px solid var(--line); background: var(--bar); padding: 10px 16px; margin-top: 8px; }
.stats div b { display: block; font-size: 30px; font-weight: 700; line-height: 1.05; }
.stats div span { font-size: 10.5px; text-transform: uppercase; color: var(--gold); letter-spacing: .03em; }
.tip { position: absolute; pointer-events: none; z-index: 5; background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 7px 10px; font-size: 13px; max-width: 250px; box-shadow: 0 8px 20px rgba(0,0,0,.35); }
.tip b { color: var(--gold); }

.rlist .ttl { text-align: left; padding-bottom: 8px; display: flex; gap: 12px; align-items: flex-end; justify-content: space-between; flex-wrap: wrap; }
.rlist .ttl h1 { font-size: 26px; }
.rankby { background: var(--surface); border: 1px solid var(--line); color: var(--ink); padding: 7px 10px; border-radius: 6px; max-width: 100%; }
.rhead { display: grid; grid-template-columns: minmax(0, 270px) var(--mw, 64px) minmax(0, 1fr); gap: 14px; align-items: center; position: sticky; top: 64px; z-index: 4; background: var(--bg); padding: 10px 0 0; }
.rhead .h { color: var(--muted); text-transform: uppercase; font-size: 13px; border-bottom: 1px solid var(--line); padding: 8px 0; }
.rhead .h b { color: var(--ink); margin-right: 6px; }
.rfilter { display: flex; gap: 8px; align-items: center; background: var(--bar); padding: 6px 8px; }
.rfilter input { flex: 1; min-width: 0; background: none; border: 0; padding: 4px; color: var(--ink); }
.rfilter input::placeholder { color: var(--muted); }
.fbtn { background: var(--surface-2); border: 1px solid var(--line); border-radius: 6px; padding: 4px 10px; font-size: 13px; color: var(--gold); cursor: pointer; white-space: nowrap; }
.fbtn[aria-expanded="true"], .fbtn.on { background: var(--gold); color: var(--gold-ink); border-color: var(--gold); }
.drawer { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 14px; margin: 10px 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px 18px; }
.drawer fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
.drawer legend { font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--gold); margin-bottom: 6px; padding: 0; }
.drawer .opts { display: flex; flex-wrap: wrap; gap: 5px; }
.opt { background: var(--surface-2); border: 1px solid var(--line); border-radius: 999px; padding: 3px 10px; font-size: 12.5px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.opt i { width: 9px; height: 9px; border-radius: 50%; }
.opt .n { color: var(--muted); font-size: 11.5px; }
.opt[aria-pressed="true"] { border-color: var(--gold); box-shadow: inset 0 0 0 1px var(--gold); }
.opt.zero { opacity: .45; }
.dfoot { grid-column: 1 / -1; display: flex; gap: 10px; align-items: center; justify-content: space-between; flex-wrap: wrap; font-size: 13px; color: var(--muted); }
.active { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 0; }
.tag { display: inline-flex; align-items: center; gap: 4px; background: var(--gold-soft); color: var(--ink); border-radius: 999px; padding: 2px 4px 2px 10px; font-size: 12.5px; }
.tag button { background: none; border: 0; color: var(--gold); cursor: pointer; font-size: 15px; line-height: 1; padding: 0 4px; }
.rgrp { color: var(--muted); text-transform: uppercase; font-size: 13px; padding: 18px 0 6px; border-bottom: 1px solid var(--line); max-width: 270px; }
.rgrp b { color: var(--ink); margin-right: 6px; }
.rrow { display: grid; grid-template-columns: minmax(0, 270px) var(--mw, 64px) minmax(0, 1fr) 28px; gap: 14px; align-items: center; padding: 10px 0; text-decoration: none; color: var(--ink); }
.rrow:hover .rn { color: var(--gold); }
.rrow .who { display: flex; align-items: center; gap: 12px; min-width: 0; }
.rrow .cover { --w: 44px; }
.rn { text-transform: uppercase; font-size: 14.5px; font-weight: 500; min-width: 0; }
.rn small { display: block; text-transform: none; color: var(--muted); font-size: 12px; font-weight: 400; }
.rm { font-size: 21px; font-weight: 700; text-align: right; white-space: nowrap; }
.rm.txt { font-size: 15px; }
.rm .mp { display: inline-block; font-size: 10.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .02em; color: #fff; border-radius: 999px; padding: 3px 9px; white-space: normal; line-height: 1.2; text-align: center; }
.rm .mp.ok { background: var(--ok); } .rm .mp.mid { background: var(--mid); } .rm .mp.warn { background: var(--warn); } .rm .mp.bad { background: var(--bad); } .rm .mp.na { background: var(--na); }
.rlist.catm { --mw: 130px; }
.sbar { display: flex; height: 28px; background: var(--surface-2); border-radius: 1px; overflow: hidden; }
.sbar span { display: flex; align-items: center; padding-left: 4px; font-size: 12px; font-weight: 700; color: #0d0d0d; white-space: nowrap; overflow: hidden; }
.sbar .g0 { background: var(--s1); } .sbar .g1 { background: var(--s2); } .sbar .g2 { background: var(--s3); } .sbar .g3 { background: var(--s4); }
.addc { width: 26px; height: 26px; border-radius: 50%; border: 1.5px solid var(--gold); background: none; color: var(--gold); font-weight: 700; cursor: pointer; line-height: 1; padding: 0; }
.addc[aria-pressed="true"] { background: var(--gold); color: var(--gold-ink); }
.addc:disabled { opacity: .3; cursor: not-allowed; }
.seglg { display: flex; flex-wrap: wrap; gap: 12px; font-size: 12.5px; color: var(--muted); margin: 2px 0 0; }
.seglg i { display: inline-block; width: 11px; height: 11px; margin-right: 5px; vertical-align: -1px; }
.empty { padding: 30px 0; color: var(--muted); }
/* score bands + status chips */
.sb { display: inline-block; min-width: 46px; text-align: center; border-radius: 6px; padding: 2px 6px; font-weight: 800; color: #111; }
.sb.b5, .sb.b0 { color: #fff; }
.bg-b5 { background: var(--b5); } .bg-b4 { background: var(--b4); } .bg-b3 { background: var(--b3); } .bg-b2 { background: var(--b2); } .bg-b1 { background: var(--b1); } .bg-b0 { background: var(--b0); }
.minis { display: flex; flex-wrap: wrap; gap: 3px; margin-top: 4px; }
.mini { font-size: 10.5px; line-height: 1.35; padding: 0 6px; border-radius: 4px; color: #fff; font-weight: 600; text-transform: none; white-space: nowrap; }
.mini.ok { background: var(--ok); } .mini.mid { background: var(--mid); } .mini.warn { background: var(--warn); } .mini.bad { background: var(--bad); } .mini.na { background: var(--na); }
.modes { display: flex; gap: 8px; align-items: center; padding-top: 12px; }
.modes .rankby { padding: 5px 8px; font-size: 14px; }
.modes .lbl { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--gold); margin-right: 4px; }
.legbtn { background: var(--surface); border: 1px solid var(--line); border-radius: 999px; padding: 3px 10px 3px 6px; font-size: 12.5px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; color: var(--ink); }
.legbtn i { width: 14px; height: 14px; border-radius: 3px; }
.legbtn .n { color: var(--muted); font-size: 11.5px; }
.legbtn[aria-pressed="true"] { border-color: var(--ink); box-shadow: inset 0 0 0 1px var(--ink); }
.legend { display: flex; flex-wrap: wrap; gap: 5px; padding: 10px 0 4px; }
.howto { font-size: 13px; color: var(--muted); margin: 4px 0 0; }
.howto b { color: var(--ink); }
.wall a .band { display: block; margin-top: 3px; text-align: center; border-radius: 3px; font-size: 11px; font-weight: 800; color: #111; line-height: 1.5; }
.wall a .band.b5, .wall a .band.b0 { color: #fff; }

/* ---------- compare ---------- */
.cmpwrap { overflow-x: auto; border-top: 1px solid var(--line); }
table.cmp { border-collapse: collapse; width: 100%; min-width: 900px; table-layout: fixed; }
table.cmp th, table.cmp td { border-bottom: 1px solid var(--line); padding: 0; }
table.cmp col.lab { width: 230px; }
table.cmp .lab { position: sticky; left: 0; z-index: 2; background: var(--bg); text-align: left; padding: 8px 10px; font-size: 12.5px; text-transform: uppercase; font-weight: 500; letter-spacing: .02em; }
table.cmp thead .lab { vertical-align: bottom; }
.hscore { display: flex; align-items: center; gap: 12px; padding: 12px 10px 6px; min-height: 92px; }
.hscore .cover { --w: 48px; }
.hscore b { font-size: 48px; font-weight: 500; line-height: 1; display: block; }
.hscore .ph { color: var(--muted); font-size: 17px; opacity: .5; }
.dots { display: flex; gap: 8px; font-size: 11px; color: var(--muted); margin-top: 6px; }
.dots i { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 3px; vertical-align: -1px; }
.dots i.ph { background: var(--line) !important; }
.cname { background: var(--gold); color: var(--gold-ink); font-weight: 600; text-align: center; padding: 9px 8px; font-size: 14.5px; display: flex; align-items: center; justify-content: center; gap: 6px; }
.cname button { background: none; border: 0; color: inherit; cursor: pointer; font-size: 17px; line-height: 1; opacity: .7; padding: 0 2px; }
.cname input { width: 100%; background: transparent; border: 0; color: var(--gold-ink); text-align: center; font-weight: 600; }
.cname input::placeholder { color: var(--gold-ink); opacity: .85; }
.cfilt { display: flex; align-items: center; gap: 8px; padding: 8px 10px; background: var(--bar); }
.cfilt input { flex: 1; min-width: 0; background: none; border: 0; color: var(--ink); }
.cgroup td { background: var(--surface); color: var(--gold); font-size: 11.5px; text-transform: uppercase; letter-spacing: .08em; padding: 6px 10px !important; }
.cgroup td.lab { background: var(--surface); }
td.cell { text-align: center; height: 46px; color: var(--cell-ink); position: relative; padding: 4px 34px !important; }
td.cell.ok { background: var(--ok); } td.cell.mid { background: var(--mid); } td.cell.warn { background: var(--warn); } td.cell.bad { background: var(--bad); } td.cell.na { background: var(--na); }
td.cell.blank { background: transparent; }
.pill { display: inline-block; border: 1.2px solid rgba(255,255,255,.85); border-radius: 999px; padding: 1px 10px; font-size: 11px; text-transform: uppercase; font-weight: 600; letter-spacing: .02em; margin: 2px 2px; white-space: nowrap; }
.pill.x { padding: 1px 7px; }
.sym { font-weight: 800; margin-right: 4px; }
.info { position: absolute; right: 8px; top: 50%; transform: translateY(-50%); width: 24px; height: 24px; border-radius: 50%; background: #fff; color: #1a1a1a; border: 0; font: 700 13px var(--f-serif); font-style: italic; cursor: pointer; display: grid; place-items: center; }
td.txt { font-size: 13px; padding: 8px 12px !important; vertical-align: top; color: var(--ink); background: var(--surface); text-align: left; }
td.txt .clamp { display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden; }
td.txt.open .clamp { -webkit-line-clamp: unset; }
tr.textrow { cursor: pointer; }
.colordots { display: flex; gap: 10px; padding: 0 10px 12px; align-items: center; }
.colordots button { width: 22px; height: 22px; border-radius: 50%; border: 0; cursor: pointer; padding: 0; }
.colordots button[aria-pressed="false"] { opacity: .25; }
.colordots .diff { background: conic-gradient(var(--ink) 0 50%, transparent 0) border-box; border: 2px solid var(--ink); }
.colordots .diff[aria-pressed="true"] { box-shadow: 0 0 0 2px var(--gold); }
.notebox { position: fixed; z-index: 50; max-width: 360px; background: var(--surface); color: var(--ink); border: 1px solid var(--line); border-radius: 10px; padding: 12px 14px; font-size: 13.5px; box-shadow: 0 14px 30px rgba(0,0,0,.4); }
.notebox b { display: block; color: var(--gold); margin-bottom: 4px; }

/* ---------- dashboard ---------- */
.dash { display: grid; grid-template-columns: 220px minmax(0, 1fr) minmax(0, 450px); gap: 26px; padding-top: 22px; align-items: start; }
.dleft .cover { --w: 100%; }
.dleft .acts { display: grid; grid-template-columns: 1fr 1fr; margin: 10px 0 18px; }
.dleft .acts button { background: var(--gold); color: var(--gold-ink); border: 0; border-right: 1px solid rgba(0,0,0,.25); padding: 7px 4px; font-weight: 700; text-transform: uppercase; font-size: 12.5px; cursor: pointer; }
.dleft .acts button:last-child { border-right: 0; }
.kv { margin: 0; border-top: 1px solid var(--line); }
.kv div { display: flex; justify-content: space-between; align-items: baseline; gap: 10px; border-bottom: 1px solid var(--line); padding: 6px 0 3px; }
.kv dt { font-size: 10.5px; text-transform: uppercase; color: var(--ink); letter-spacing: .02em; }
.kv dd { margin: 0; font-size: 17px; text-align: right; }
.kv dd.sm { font-size: 13.5px; }
.dmid h1 { margin: 0 0 6px; font-size: 25px; font-weight: 700; text-transform: uppercase; display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.dmid h1 .flag { width: 32px; }
.arrows { display: inline-flex; gap: 6px; }
.arrows a { width: 22px; height: 22px; border-radius: 50%; background: var(--ink); color: var(--bg); display: grid; place-items: center; text-decoration: none; font-size: 13px; font-weight: 700; }
.dmid .mapbox { height: 300px; }
.dmid .sbar { height: 26px; margin-top: 6px; }
.bk { margin-top: 18px; }
.bk h2, .dsec h2 { font-size: 13px; text-transform: uppercase; color: var(--gold); font-weight: 600; letter-spacing: .05em; margin: 0 0 10px; }
.bkrow { display: grid; grid-template-columns: 170px minmax(0, 1fr) 54px; gap: 10px; align-items: center; font-size: 13.5px; padding: 4px 0; }
.bkrow .tr { height: 12px; background: var(--surface-2); border-radius: 6px; overflow: hidden; }
.bkrow .tr i { display: block; height: 100%; background: var(--gold); border-radius: 6px; }
.bkrow b { text-align: right; font-weight: 600; }
.dsec { margin-top: 26px; }
.dsec .s { padding: 10px 0; border-bottom: 1px solid var(--line); }
.dsec h3 { margin: 0 0 3px; font-size: 14.5px; font-weight: 600; }
.dsec p { margin: 0; font-size: 14px; color: var(--ink); overflow-wrap: anywhere; }
.dsec ul { margin: 4px 0 0; padding-left: 18px; font-size: 13.5px; }
.dsec li { margin: 2px 0; overflow-wrap: anywhere; }
.dright h2 { color: var(--gold); font-weight: 500; font-size: 19px; text-transform: uppercase; text-align: center; margin: 4px 0 14px; }
.reqtools { display: flex; align-items: center; gap: 10px; background: var(--bar); padding: 9px 12px; }
.reqtools input { flex: 1; min-width: 0; background: none; border: 0; color: var(--ink); }
.reqtools .colordots { padding: 0; gap: 6px; }
.reqtools .colordots button { width: 16px; height: 16px; }
.reqhead { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); background: var(--gold); color: var(--gold-ink); font-weight: 600; font-size: 14.5px; }
.reqhead span { padding: 7px 10px; text-align: center; }
.req { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); border-bottom: 1px solid var(--line); min-height: 46px; }
.req .rl { display: flex; align-items: center; gap: 10px; padding: 6px 10px; font-size: 14px; }
.req .rc { display: flex; align-items: center; justify-content: center; flex-wrap: wrap; position: relative; padding: 4px 34px 4px 8px; color: var(--cell-ink); }
.req .rc.ok { background: var(--ok); } .req .rc.mid { background: var(--mid); } .req .rc.warn { background: var(--warn); } .req .rc.bad { background: var(--bad); } .req .rc.na { background: var(--na); }
.reqgrp { padding: 12px 10px 4px; font-size: 11.5px; color: var(--gold); text-transform: uppercase; letter-spacing: .08em; }

/* ---------- modal ---------- */
.modal { position: fixed; inset: 0; z-index: 60; background: rgba(0,0,0,.6); display: grid; place-items: start center; padding: 70px 16px 16px; overflow-y: auto; }
.mbox { width: min(560px, 100%); background: var(--surface); border: 1px solid var(--line); border-radius: 14px; padding: 22px; position: relative; }
.mbox h2 { margin: 0 0 4px; color: var(--gold); font-weight: 500; font-size: 24px; }
.mbox .x { position: absolute; right: 12px; top: 10px; background: none; border: 0; color: var(--muted); font-size: 24px; cursor: pointer; }
.mbox label { display: block; font-size: 11.5px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); margin: 14px 0 5px; }
.mbox select, .mbox input.big { width: 100%; background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 10px 12px; font-size: 16px; color: var(--ink); }
.verdict { margin-top: 16px; display: grid; gap: 8px; }
.vrow { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 10px; align-items: center; padding: 8px 12px; border-radius: 8px; color: #fff; font-size: 14px; }
.vrow.ok { background: var(--ok); } .vrow.mid { background: var(--mid); } .vrow.warn { background: var(--warn); } .vrow.bad { background: var(--bad); } .vrow.na { background: var(--na); }
.vrow b { font-weight: 600; text-align: right; }
.results { margin-top: 10px; max-height: 50vh; overflow-y: auto; }
.results a { display: flex; align-items: center; gap: 10px; padding: 8px 10px; border-radius: 6px; color: var(--ink); text-decoration: none; }
.results a:hover, .results a:focus-visible { background: var(--surface-2); }
.results a small { margin-left: auto; color: var(--gold); font-weight: 700; }

footer.bot { border-top: 1px solid var(--line); background: var(--bar); }
footer.bot .in { max-width: 1440px; margin: 0 auto; padding: 12px 20px; display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; font-size: 12px; text-transform: uppercase; letter-spacing: .02em; }
footer.bot b { color: var(--gold); font-weight: 600; }
footer.bot a { color: var(--ink); text-decoration: none; }
footer.bot p { margin: 0; }
.disc { max-width: 900px; margin: 30px auto 0; color: var(--muted); font-size: 12.5px; text-align: center; }

@media (max-width: 1180px) {
  .dash { grid-template-columns: 200px minmax(0, 1fr); }
  .dright { grid-column: 1 / -1; }
}
@media (max-width: 980px) {
  .rank { grid-template-columns: minmax(0, 1fr); }
  .rmap { position: static; height: auto; min-height: 0; }
  .rmap .mapbox { height: 300px; flex: none; }
  .rhead { top: 0; position: static; }
  nav.main a { padding: 0 9px; font-size: 13.5px; }
}
@media (max-width: 760px) {
  .topin { flex-wrap: wrap; gap: 6px 12px; padding: 8px 16px 0; min-height: 0; }
  .wordmark { font-size: 18px; }
  .mark { width: 28px; height: 38px; }
  .cta { margin-left: auto; padding: 6px 14px; font-size: 13.5px; }
  nav.main { order: 3; width: 100%; margin: 0 -16px; padding: 0 8px; overflow-x: auto; scrollbar-width: none; min-height: 42px; }
  nav.main a { white-space: nowrap; }
  main { padding-inline: 16px; }
  .exhead { grid-template-columns: minmax(0, 1fr); text-align: center; }
  .exhead .ttl, .exhead .goldbtn { grid-column: 1; justify-self: center; }
  .wall { grid-template-columns: repeat(auto-fill, minmax(48px, 1fr)); gap: 4px; }
  .rhead { grid-template-columns: minmax(0, 1fr) auto; }
  .rhead .h:nth-child(2) { display: none; }
  .rhead .rfilter { grid-column: 1 / -1; }
  .rrow { grid-template-columns: minmax(0, 1fr) auto 28px; gap: 10px; }
  .rrow .sbar { grid-column: 1 / -1; grid-row: 2; height: 20px; }
  .rrow .addc { grid-column: 3; grid-row: 1; }
  .rrow .cover { --w: 36px; }
  .dash { grid-template-columns: minmax(0, 1fr); }
  .dleft { display: grid; grid-template-columns: 110px minmax(0, 1fr); gap: 0 16px; }
  .dleft .cover { grid-row: span 2; }
  .dleft .acts { margin: 0 0 10px; }
  .dleft .kv { grid-column: 1 / -1; margin-top: 14px; }
  .bkrow { grid-template-columns: 120px minmax(0, 1fr) 44px; font-size: 12.5px; }
  .ttl h1 { font-size: 24px; }
  .hscore b { font-size: 34px; }
  .stats { gap: 16px; }
  .stats div b { font-size: 22px; }
}
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
</style>

<header class="top">
  <div class="topin">
    <a class="brand" href="#/explore" aria-label="OpenCharity Index home">
      <span class="mark" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" style="color:var(--gold)"><path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/></svg></span>
      <span class="wordmark">OPENCHARITY <span>INDEX</span><small>__COUNT__ JURISDICTIONS</small></span>
    </a>
    <nav class="main" aria-label="Sections">
      <a href="#/explore" data-v="explore">Explore</a>
      <a href="#/rank" data-v="rank">Rank</a>
      <a href="#/compare" data-v="compare">Compare</a>
      <a href="#/banking" data-v="banking">Banking</a>
      <div class="more">
        <button type="button" id="moreBtn" aria-expanded="false" aria-haspopup="true" aria-label="More">···</button>
        <div class="menu" id="menu" hidden>
          <button type="button" id="themeBtn">Switch to light theme</button>
          <a href="__REPO__/raw/main/charities_by_country_v2.csv" target="_blank" rel="noopener">Download charity data (CSV)</a>
          <a href="__REPO__/raw/main/banking_by_country.csv" target="_blank" rel="noopener">Download banking data (CSV)</a>
          <a href="__REPO__/raw/main/charities_by_country_v2.xlsx" target="_blank" rel="noopener">Download workbook (Excel)</a>
          <a href="https://opencharity-org.github.io/OpenCharity/classic.html" target="_blank" rel="noopener">Classic atlas</a>
          <a href="__REPO__" target="_blank" rel="noopener">GitHub</a>
        </div>
      </div>
    </nav>
    <button type="button" class="cta" id="checkerBtn">Charity Checker</button>
  </div>
</header>

<main>
  <!-- EXPLORE -->
  <section id="v-explore" hidden>
    <div class="exhead">
      <div class="ttl"><h1>Explore the world of charities</h1><p class="serif">Find a country. Explore them all.</p></div>
      <button type="button" class="goldbtn" id="findBtn">Find</button>
    </div>
    <div class="extools" id="exTools" role="group" aria-label="Region"></div>
    <div class="extools" id="exLegend" aria-label="Charity score colours"></div>
    <div class="wall" id="wall"></div>
  </section>

  <!-- RANK / BANKING -->
  <section id="v-rank" hidden>
    <div class="rank">
      <div class="rmap">
        <div class="modes" id="rModes" role="group" aria-label="Colour the map by"></div>
        <div class="legend" id="rLegend"></div>
        <div class="mapbox" id="rMapBox">
          <div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button></div>
          <svg id="rMap" viewBox="0 0 960 500" role="img" aria-label="World map coloured by the current ranking"></svg>
          <div class="tip" id="rTip" hidden></div>
        </div>
        <div class="stats" id="rStats"></div>
      </div>
      <div class="rlist" id="rList">
        <div class="ttl">
          <div><h1 id="rTitle">Global Charity Power Rank 2026</h1><p class="serif" id="rSub"></p></div>
          <select class="rankby" id="rankBy" aria-label="Rank by"></select>
        </div>
        <div class="seglg" id="segLegend"></div>

        <div class="rhead">
          <div class="h"><b>#</b><span id="rHeadLbl">Charity power rank</span></div>
          <div class="h" id="rMetric" style="text-align:right">Score</div>
          <div class="rfilter">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="color:var(--muted)" aria-hidden="true"><path d="M3 4h18l-7 8.5V19l-4 2v-8.5z"/></svg>
            <input id="q" type="search" placeholder="Filter results…" aria-label="Filter results by name or text">
            <button type="button" class="fbtn" id="fBtn" aria-expanded="false" aria-controls="drawer">Filters</button>
          </div>
        </div>
        <div class="drawer" id="drawer" hidden></div>
        <div class="active" id="active"></div>
        <div id="rRows"></div>
      </div>
    </div>
  </section>

  <!-- COMPARE -->
  <section id="v-compare" hidden>
    <div class="ttl"><h1>Compare Countries</h1><p class="serif">Select countries and compare how easy it is to set up a charity and bank there.</p></div>
    <div class="cmpwrap"><table class="cmp" id="cmp"></table></div>
  </section>

  <!-- COUNTRY -->
  <section id="v-country" hidden>
    <div class="dash" id="dash"></div>
  </section>

  <p class="disc">Research, not legal or financial advice. Judged for a founder living in Australia with no ties to each country; confirm with the registry or bank before you act. Charity data re-verified October 2026; personal-banking data October 2026 (many rows rest on secondary sources). Grey map areas are dependent territories, which follow the parent country's rules.</p>
</main>

<footer class="bot"><div class="in">
  <p><b>Open data</b> for charity founders · Built by <a href="__REPO__" target="_blank" rel="noopener">OpenCharity</a></p>
  <p><a href="__REPO__" target="_blank" rel="noopener">GitHub</a> · <a href="https://opencharity-org.github.io/OpenCharity/classic.html" target="_blank" rel="noopener">Classic atlas</a> · © 2026 OpenCharity · CC BY 4.0 data</p>
</div></footer>

<div class="modal" id="modal" hidden role="dialog" aria-modal="true" aria-labelledby="mTitle"><div class="mbox" id="mbox"></div></div>
<div class="notebox" id="note" hidden role="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/topojson/3.0.2/topojson.min.js"></script>
<script>
const DATA = __DATA__;
const GEO = __GEO__;
const ALIAS = __ALIAS__;
const POINTS = __POINTS__;
const FLAGS = __FLAGS__;

/* ---------- helpers ---------- */
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
const feeTxt = d => d.fee_lo == null ? "—" : d.fee_hi === 0 ? "Free" : d.fee_lo === d.fee_hi ? fmtUSD(d.fee_lo) : `${fmtUSD(d.fee_lo)}–${fmtUSD(d.fee_hi)}`;
const dur = n => n < 14 ? `${n} d` : n < 60 ? `${Math.round(n / 7)} wk` : n < 365 ? `${Math.round(n / 30)} mo` : `${(n / 365).toFixed(n % 365 ? 1 : 0)} yr`;
const timeTxt = d => { if (d.days_lo == null) return "—"; if (d.days_lo === d.days_hi) return dur(d.days_lo);
  const a = dur(d.days_lo).split(" "), b = dur(d.days_hi).split(" "); return a[1] === b[1] ? `${a[0]}–${b[0]} ${b[1]}` : `${a.join(" ")}–${b.join(" ")}`; };
const median = a => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y), m = s.length >> 1; return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

// flag images as CSS classes
{ const s = document.createElement("style");
  s.textContent = Object.entries(FLAGS).map(([k, v]) => `.fl-${k}{background-image:url("data:image/svg+xml,${encodeURIComponent(v)}")}`).join("");
  document.head.appendChild(s); }
const PAL = ["#1b2848", "#4d1626", "#173628", "#18181a", "#1c4650", "#22396f", "#691b27", "#2c2238", "#3d2a14", "#123a3a"];
const hash = s => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) >>> 0, 7);
const cover = d => `<span class="cover" style="--pc:${PAL[hash(d.country) % PAL.length]}" aria-hidden="true"><span class="ci"><span class="ct">${esc(d.country)}</span><span class="cf fl-${d.iso}"></span><span class="cb">Charity</span></span></span>`;
const flag = d => `<span class="flag fl-${d.iso}" aria-hidden="true"></span>`;

/* ---------- categories ---------- */
const CAT = {
  difficulty: { easy: ["Easy", "ok"], medium: ["Medium", "mid"], hard: ["Hard", "warn"], "very hard": ["Very hard", "bad"] },
  no_presence: { yes: ["Fully remote", "ok"], partial: ["Partly remote", "mid"], no: ["Must be present", "bad"] },
  fee_bin: { free: ["Free", "ok"], low: ["$1–100", "mid"], mid: ["$101–500", "warn"], high: ["Over $500", "bad"], unknown: ["Not published", "na"] },
  time_bin: { fast: ["Up to 2 weeks", "ok"], month: ["Up to a month", "mid"], quarter: ["1–3 months", "warn"], slow: ["Over 3 months", "bad"], unknown: ["Not stated", "na"] },
  bank_cat: { remote: ["Remote option", "ok"], visit: ["Branch visit", "mid"], blocked: ["Effectively blocked", "bad"] },
  funding_cat: { open: ["No notable limits", "ok"], restricted: ["Restricted", "warn"] },
  gfn: { Yes: ["Eligible", "ok"], No: ["Not eligible", "bad"] },
  pb_status: { yes: ["Open to non-residents", "ok"], limited: ["Limited", "warn"], no: ["Residents only", "bad"] },
  pb_method: { remote: ["Remote, no visit", "ok"], "in-person": ["Branch visit", "mid"], "not available": ["Not available", "bad"] },
  pb_cost_bin: { free: ["Free", "ok"], low: ["Up to $60/yr", "mid"], mid: ["$61–240/yr", "warn"], high: ["Over $240/yr", "bad"], unknown: ["Not published", "na"] },
  pb_dep_bin: { none: ["No minimum", "ok"], low: ["Up to $500", "mid"], mid: ["$501–10k", "warn"], high: ["Over $10k", "bad"], unknown: ["Not published", "na"] },
  pb_res: { no: ["Not needed", "ok"], often: ["Often needed", "warn"], yes: ["Required", "bad"] },
  confidence: { high: ["High", "ok"], med: ["Medium", "mid"] },
};
const COLORS = ["ok", "mid", "warn", "bad"];
const cat = (k, d) => CAT[k][d[k]] || [d[k] || "—", "na"];
const ordOf = (k, d) => { const i = Object.keys(CAT[k]).indexOf(d[k]); return i < 0 ? 99 : i; };

/* ---------- charity score ---------- */
const pct = key => { const v = DATA.filter(d => d[key] != null).map(d => d[key]).sort((a, b) => a - b);
  return x => { let i = 0; while (i < v.length && v[i] < x) i++; return v.length > 1 ? i / (v.length - 1) : 0; }; };
const feeP = pct("fee_lo"), dayP = pct("days_lo");
const FACTORS = [
  ["ease", "Ease of registering", 25, d => ({ easy: 25, medium: 17, hard: 8, "very hard": 0 })[d.difficulty] ?? 0],
  ["remote", "Remote founding", 20, d => ({ yes: 20, partial: 10, no: 0 })[d.no_presence] ?? 0],
  ["fee", "Low registration fee", 10, d => d.fee_lo == null ? 0 : 10 * (1 - feeP(d.fee_lo))],
  ["speed", "Speed of registration", 10, d => d.days_lo == null ? 0 : 10 * (1 - dayP(d.days_lo))],
  ["cbank", "Charity bank account", 10, d => ({ remote: 10, visit: 5, blocked: 0 })[d.bank_cat] ?? 0],
  ["pbank", "Personal account (non-resident)", 10, d => (({ yes: 7, limited: 3.5, no: 0 })[d.pb_status] ?? 0) + (({ remote: 3, "in-person": 1.5, "not available": 0 })[d.pb_method] ?? 0)],
  ["funding", "Open foreign funding", 5, d => d.funding_cat === "open" ? 5 : 0],
  ["gfn", "Google for Nonprofits", 10, d => d.gfn === "Yes" ? 10 : 0],
];
const GROUPS = [["Registration", ["ease", "remote"]], ["Cost & speed", ["fee", "speed"]], ["Banking", ["cbank", "pbank"]], ["Funding & Google", ["funding", "gfn"]]];
for (const d of DATA) {
  d.pts = Object.fromEntries(FACTORS.map(([k, , , f]) => [k, f(d)]));
  d.grp = GROUPS.map(([, ks]) => ks.reduce((s, k) => s + d.pts[k], 0));
  d.cs = Math.round(d.grp.reduce((a, b) => a + b, 0));
}
const BANDS = [[85, "Excellent 85+", "b5"], [70, "Very good 70–84", "b4"], [55, "Good 55–69", "b3"], [40, "Fair 40–54", "b2"], [25, "Hard 25–39", "b1"], [0, "Very hard 0–24", "b0"]];
for (const d of DATA) d.band = BANDS.find(([m]) => d.cs >= m)[2];
CAT.band = Object.fromEntries(BANDS.map(([, l, c]) => [c, [l, c]]));
const SYM = { ok: "✓", mid: "•", warn: "!", bad: "✕", na: "?" };
const badge = d => `<span class="sb bg-${d.band} ${d.band}" title="Charity score ${d.cs}/100 · ${esc(CAT.band[d.band][0])}">${d.cs}</span>`;
const sbar = d => `<span class="sbar" aria-label="Score breakdown: ${GROUPS.map(([g], i) => `${g} ${Math.round(d.grp[i])}`).join(", ")}">${d.grp.map((v, i) =>
  `<span class="g${i}" style="width:${v}%" title="${esc(GROUPS[i][0])}: ${Math.round(v)}">${v >= 5 ? Math.round(v) : ""}</span>`).join("")}</span>`;

/* ---------- rankings ---------- */
const lbl = k => Object.assign(d => cat(k, d)[0], { catKey: k });  // category metric, drawn as a coloured pill
const RANKS = {
  power:   { label: "Charity Power Rank", head: "Charity power rank", metric: "Score", show: d => d.cs, map: null, val: d => -d.cs,
             sub: "Countries ranked by their charity score: how easy, cheap and fast it is to register a charity from Australia, plus banking and funding access." },
  easiest: { label: "Easiest to register", head: "Easiest to register", metric: "Level", show: lbl("difficulty"), map: "difficulty", val: d => ordOf("difficulty", d) * 10 + ordOf("no_presence", d),
             sub: "Registration difficulty for an Australian founder, then how much of it can be done remotely." },
  remote:  { label: "Most remote-friendly", head: "Remote founding", metric: "Remote", show: lbl("no_presence"), map: "no_presence", val: d => ordOf("no_presence", d) * 10 + ordOf("bank_cat", d),
             sub: "Fully remote founding first, then how easily the charity can open a bank account." },
  cheapest:{ label: "Cheapest to register", head: "Cheapest registration", metric: "Fee", show: feeTxt, map: "fee_bin", val: d => d.fee_lo,
             sub: "Lowest stated government fee first (some notes include agent or notary costs). Unpublished fees last." },
  fastest: { label: "Fastest to register", head: "Fastest registration", metric: "Time", show: timeTxt, map: "time_bin", val: d => d.days_lo,
             sub: "Shortest stated registration time first. Unstated times last." },
  funding: { label: "Fewest funding limits", head: "Foreign funding", metric: "Funding", show: lbl("funding_cat"), map: "funding_cat", val: d => ordOf("funding_cat", d) * 10 + ordOf("difficulty", d),
             sub: "No notable limits on foreign donations first." },
  pbank:   { label: "Easiest personal bank account", head: "Banking rank", metric: "Account", show: lbl("pb_status"), map: "pb_status", val: d => ordOf("pb_status", d) * 10 + ordOf("pb_method", d),
             sub: "Can a non-resident foreigner (no visa or address there) open a personal account at a licensed local bank? Open first, then remote opening." },
  pbremote:{ label: "Personal account without a visit", head: "Remote account opening", metric: "Opening", show: lbl("pb_method"), map: "pb_method", val: d => ordOf("pb_method", d) * 10 + ordOf("pb_status", d),
             sub: "Countries where at least one bank opens a non-resident's personal account without a branch visit come first." },
  pbcheap: { label: "Cheapest personal account", head: "Account fees", metric: "Fees/yr", show: d => d.pb_year == null ? "—" : usd(d.pb_year), map: "pb_cost_bin", val: d => d.pb_year,
             sub: "First-year fees: 12 × monthly fee + opening fee, US$. Fee figures are published for about a third of countries; the rest rank last." },
  hardest: { label: "Hardest to register", head: "Hardest to register", metric: "Level", show: lbl("difficulty"), map: "difficulty", val: d => -(ordOf("difficulty", d) * 10 + ordOf("no_presence", d)),
             sub: "Very hard first." },
};
const BANK_RANKS = ["pbank", "pbremote", "pbcheap"];
const rankCache = {};
function rankOf(key) {
  if (rankCache[key]) return rankCache[key];
  const r = RANKS[key], v = d => { const x = r.val(d); return x == null ? Infinity : x; };
  const list = [...DATA].sort((a, b) => v(a) - v(b) || b.cs - a.cs || a.country.localeCompare(b.country));
  const pos = new Map(); let rank = 0, prev;
  for (const d of list) { const x = v(d); if (x !== prev) { rank++; prev = x; } pos.set(d.country, x === Infinity ? null : rank); }
  return rankCache[key] = { list, pos };
}
const powerRank = d => rankOf("power").pos.get(d.country);

/* ---------- facets ---------- */
const REGIONS = [...new Set(DATA.map(d => d.region))].sort();
const FACETS = [
  ["difficulty", "Difficulty"], ["no_presence", "Remote founding"], ["fee_bin", "Registration fee"], ["time_bin", "Time to register"],
  ["funding_cat", "Foreign funding"], ["gfn", "Google for Nonprofits"], ["bank_cat", "Charity bank account"],
  ["pb_status", "Personal account"], ["pb_method", "Personal account opening"], ["pb_cost_bin", "Personal account fees"],
  ["pb_dep_bin", "Minimum deposit"], ["pb_res", "Residence for account"], ["confidence", "Research confidence"], ["region", "Region"],
];
FACETS.unshift(["band", "Charity score"]);
const MODES = [["band", "Charity score"], ["difficulty", "Difficulty"], ["no_presence", "Remote founding"], ["fee_bin", "Fee"], ["time_bin", "Time"],
  ["bank_cat", "Charity bank"], ["pb_status", "Personal account"], ["pb_method", "Account opening"], ["pb_cost_bin", "Account fees"],
  ["funding_cat", "Foreign funding"], ["gfn", "Google for Nonprofits"], ["confidence", "Confidence"]];
const FLABEL = Object.fromEntries(FACETS);
const optsOf = k => k === "region" ? REGIONS.map(r => [r, r, null]) : Object.entries(CAT[k]).map(([v, [l, c]]) => [v, l, c]);

/* ---------- state ---------- */
const S = { mode: "band", rankBy: "power", bankBy: "pbank", F: Object.fromEntries(FACETS.map(([k]) => [k, new Set()])), cmp: [], region: "", theme: "dark", diffOnly: false, hide: new Set() };
{ const s = load("oci-state") || {};
  if (RANKS[s.rankBy] && !BANK_RANKS.includes(s.rankBy)) S.rankBy = s.rankBy;
  if (BANK_RANKS.includes(s.bankBy)) S.bankBy = s.bankBy;
  if (s.F) for (const k in s.F) if (S.F[k]) s.F[k].forEach(v => S.F[k].add(v));
  if (Array.isArray(s.cmp)) S.cmp = s.cmp.filter(c => byName.has(c)).slice(0, 5);
  if (["light", "dark"].includes(s.theme)) S.theme = s.theme; }
const save = () => store("oci-state", { rankBy: S.rankBy, bankBy: S.bankBy, cmp: S.cmp, theme: S.theme, F: Object.fromEntries(Object.entries(S.F).map(([k, v]) => [k, [...v]])) });

const HAY = new Map(DATA.map(d => [d.country, [d.country, d.region, d.entity, d.requirements, d.bottleneck, d.notes, d.tax_exempt, d.donor_restr, d.bank_access, d.pb_banks, d.pb_docs, d.pb_restr, d.pb_alt].join(" ").toLowerCase()]));
function passes(d, skip) {
  for (const k in S.F) if (k !== skip && S.F[k].size && !S.F[k].has(d[k])) return false;
  const t = $("q").value.trim().toLowerCase();
  return !t || HAY.get(d.country).includes(t);
}

/* ---------- maps ---------- */
const FEATS = topojson.feature(GEO, GEO.objects.countries).features;
function makeMap(svgEl, tipEl, onPick) {
  const W = 960, H = 500, svg = d3.select(svgEl), g = svg.append("g");
  const proj = d3.geoNaturalEarth1().fitExtent([[4, 4], [W - 4, H - 4]], { type: "FeatureCollection", features: FEATS });
  const path = d3.geoPath(proj);
  const paths = g.append("g").selectAll("path").data(FEATS).join("path").attr("d", path).attr("class", "cty");
  const featOf = new Map(); FEATS.forEach(f => { const c = geoName.get(f.properties.name); if (c) featOf.set(c, f); });
  const dotData = DATA.filter(d => POINTS[d.country] || path.area(featOf.get(d.country)) < 6)
    .map(d => { const xy = POINTS[d.country] ? proj(POINTS[d.country]) : path.centroid(featOf.get(d.country)); return { d, x: xy[0], y: xy[1] }; });
  const dots = g.append("g").selectAll("circle").data(dotData).join("circle").attr("class", "dot").attr("cx", p => p.x).attr("cy", p => p.y).attr("r", 3);
  const zoom = d3.zoom().scaleExtent([1, 12]).translateExtent([[0, 0], [W, H]]).on("zoom", ev => { g.attr("transform", ev.transform); dots.attr("r", 3 / Math.sqrt(ev.transform.k)); });
  svg.call(zoom).on("dblclick.zoom", null);
  const box = svgEl.parentElement;
  box.querySelectorAll("[data-z]").forEach(b => b.onclick = () => svg.transition().duration(250).call(zoom.scaleBy, b.dataset.z === "in" ? 1.6 : 1 / 1.6));
  let tipFn = d => d.country;
  const show = (ev, name) => { const d = byName.get(name), r = box.getBoundingClientRect();
    tipEl.innerHTML = d ? tipFn(d) : `<b>${esc(name)}</b><br>Not in dataset`; tipEl.hidden = false;
    tipEl.style.left = Math.max(6, Math.min(ev.clientX - r.left + 14, r.width - tipEl.offsetWidth - 6)) + "px";
    tipEl.style.top = Math.max(ev.clientY - r.top - tipEl.offsetHeight - 10, 6) + "px"; };
  paths.on("mousemove", (ev, f) => show(ev, geoName.get(f.properties.name) || f.properties.name)).on("mouseleave", () => tipEl.hidden = true)
    .on("click", (ev, f) => { const c = geoName.get(f.properties.name); if (c) onPick(c); });
  dots.on("mousemove", (ev, p) => show(ev, p.d.country)).on("mouseleave", () => tipEl.hidden = true).on("click", (ev, p) => onPick(p.d.country));
  return {
    paint(fill, dim = () => false, sel = null) {
      paths.attr("fill", f => { const c = geoName.get(f.properties.name); return c ? fill(byName.get(c)) : null; })
        .attr("class", f => { const c = geoName.get(f.properties.name); return "cty" + (c ? "" : " nodata") + (c && dim(byName.get(c)) ? " dim" : "") + (c && c === sel ? " sel" : ""); });
      dots.attr("fill", p => fill(p.d)).attr("class", p => "dot" + (dim(p.d) ? " dim" : "") + (p.d.country === sel ? " sel" : ""));
      dots.filter(p => p.d.country === sel).raise();
    },
    tip(fn) { tipFn = fn; },
    focus(name) {
      const f = featOf.get(name), pt = dotData.find(p => p.d.country === name);
      let x0, y0, x1, y1;
      if (f && path.area(f) >= 6) [[x0, y0], [x1, y1]] = path.bounds(f); else if (pt) { x0 = pt.x - 20; x1 = pt.x + 20; y0 = pt.y - 12; y1 = pt.y + 12; } else return;
      const k = Math.max(1, Math.min(5, 0.55 / Math.max((x1 - x0) / W, (y1 - y0) / H)));
      const t = d3.zoomIdentity.translate(W / 2, H / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
      svg.transition().duration(500).call(zoom.transform, t);
    },
    reset() { svg.call(zoom.transform, d3.zoomIdentity); },
  };
}
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const catFill = k => { const m = {}; return d => { const c = cat(k, d)[1]; return m[c] ??= css("--" + c); }; };

/* ---------- views ---------- */
let view = "explore", country = null, rMap = null, dMap = null;
const VIEWS = ["explore", "rank", "compare", "country"];
function go(h) { if (location.hash !== h) location.hash = h; else route(); }
function route() {
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, ""));
  const [v, arg] = h.split("/");
  closeNote();
  if (v === "country" && bySlug.has(arg)) { view = "country"; country = bySlug.get(arg).country; }
  else if (bySlug.has(v)) { view = "country"; country = bySlug.get(v).country; }       // legacy #estonia links
  else if (v === "compare") { view = "compare"; if (arg) { const cs = arg.split(",").map(s => bySlug.get(s)?.country).filter(Boolean); if (cs.length) S.cmp = [...new Set(cs)].slice(0, 5); } }
  else if (v === "rank" || v === "banking") view = v;
  else view = "explore";
  const sect = view === "banking" ? "rank" : view;
  VIEWS.forEach(x => $("v-" + x).hidden = x !== sect);
  document.querySelectorAll("nav.main a").forEach(a => a.dataset.v === view ? a.setAttribute("aria-current", "page") : a.removeAttribute("aria-current"));
  if (view === "explore") renderExplore();
  if (view === "rank" || view === "banking") renderRank();
  if (view === "compare") renderCompare();
  if (view === "country") renderCountry();
  document.title = view === "country" ? `${country} · OpenCharity Index` : "OpenCharity Index";
  save();
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);

/* explore */
function renderExplore() {
  $("exTools").innerHTML = [["", "All"], ...REGIONS.map(r => [r, r])].map(([v, l]) => `<button type="button" class="chipbtn" data-r="${esc(v)}" aria-pressed="${S.region === v}">${esc(l)}</button>`).join("");
  const list = DATA.filter(d => !S.region || d.region === S.region).sort((a, b) => a.country.localeCompare(b.country));
  $("exLegend").innerHTML = `<span class="howto" style="margin:0 6px 0 0;align-self:center">Charity score:</span>` + BANDS.map(([, l, c]) =>
    `<span class="legbtn" style="cursor:default"><i class="bg-${c}"></i>${esc(l)} <span class="n">${list.filter(d => d.band === c).length}</span></span>`).join("");
  $("wall").innerHTML = list.map(d => `<a href="#/country/${slug(d.country)}" title="${esc(d.country)} · score ${d.cs} · rank ${powerRank(d)}">${cover(d)}<span class="band bg-${d.band} ${d.band}">${d.cs}</span></a>`).join("");
}
$("exTools").addEventListener("click", e => { const b = e.target.closest("[data-r]"); if (b) { S.region = b.dataset.r; renderExplore(); } });
$("findBtn").addEventListener("click", () => openFind());

/* rank */
const curRank = () => view === "banking" ? S.bankBy : S.rankBy;
function renderRank() {
  const key = curRank(), R = RANKS[key], { list, pos } = rankOf(key);
  const opts = view === "banking" ? BANK_RANKS : Object.keys(RANKS).filter(k => !BANK_RANKS.includes(k) || true);
  $("rankBy").innerHTML = opts.map(k => `<option value="${k}">${esc(RANKS[k].label)}</option>`).join("");
  $("rankBy").value = key;
  $("rTitle").textContent = view === "banking" ? "Global Banking Rank 2026" : (key === "power" ? "Global Charity Power Rank 2026" : R.label);
  $("rSub").textContent = R.sub;
  $("rHeadLbl").textContent = R.head;
  $("rMetric").textContent = R.metric;
  $("segLegend").innerHTML = GROUPS.map(([g, ks], i) => `<span><i style="background:var(--s${i + 1})"></i>${esc(g)} (${ks.reduce((s, k) => s + FACTORS.find(f => f[0] === k)[2], 0)})</span>`).join("") + `<span>Bar = charity score out of 100</span>`;
  renderDrawer();
  $("rList").classList.toggle("catm", !!R.show.catKey);
  const rows = list.filter(d => passes(d));
  let html = "", last;
  for (const d of rows) {
    const p = pos.get(d.country);
    if (p !== last) { html += `<div class="rgrp"><b>${p ?? "—"}</b>${p == null ? "Not ranked (no data)" : esc(R.head)}</div>`; last = p; }
    const m = R.show(d), inC = S.cmp.includes(d.country), mk = R.show.catKey;
    html += `<a class="rrow" href="#/country/${slug(d.country)}"><span class="who">${cover(d)}<span class="rn">${esc(d.country)}<small>${esc(d.region)}</small></span></span>
      <span class="rm${typeof m === "number" ? "" : " txt"}">${mk ? `<span class="mp ${cat(mk, d)[1]}">${SYM[cat(mk, d)[1]]} ${esc(m)}</span>` : key === "power" ? badge(d) : esc(m)}</span>${sbar(d)}
      <button type="button" class="addc" data-add="${esc(d.country)}" aria-pressed="${inC}" aria-label="${inC ? "Remove" : "Add"} ${esc(d.country)} ${inC ? "from" : "to"} compare" title="Compare"${!inC && S.cmp.length >= 5 ? " disabled" : ""}>${inC ? "✓" : "+"}</button></a>`;
  }
  $("rRows").innerHTML = html || `<p class="empty">No countries match all these filters. Remove one above.</p>`;
  // map
  if (!rMap) rMap = makeMap($("rMap"), $("rTip"), c => go("#/country/" + slug(c)));
  rMap.tip(d => `<b>${esc(d.country)}</b><br>#${pos.get(d.country) ?? "—"} ${esc(R.head.toLowerCase())} · ${esc(R.show(d))}<br>Charity score ${d.cs}`);
  rMap.paint(catFill(S.mode), d => !passes(d));
  $("rModes").innerHTML = `<label class="lbl" for="modeSel">Colour map by</label><select class="rankby" id="modeSel">${MODES.map(([k, l]) => `<option value="${k}"${S.mode === k ? " selected" : ""}>${esc(l)}</option>`).join("")}</select>`;
  $("rLegend").innerHTML = Object.entries(CAT[S.mode]).map(([v, [l, c]]) => `<button type="button" class="legbtn" data-f="${S.mode}" data-v="${esc(v)}" aria-pressed="${S.F[S.mode].has(v)}" title="Show only ${esc(l)} (click again to undo)"><i style="background:var(--${c})"></i>${esc(l)} <span class="n">${DATA.filter(d => d[S.mode] === v && passes(d, S.mode)).length}</span></button>`).join("");
  const sc = rows.map(d => d.cs);
  $("rStats").innerHTML = `<div><b>${sc.length ? Math.round(sc.reduce((a, b) => a + b, 0) / sc.length) : "—"}</b><span>Average score</span></div>
    <div><b>${sc.length ? Math.round(median(sc)) : "—"}</b><span>Median score</span></div>
    <div><b>${rows.length}</b><span>Countries shown</span></div>
    <div><b>${rows.filter(d => view === "banking" ? d.pb_status === "yes" : d.no_presence === "yes").length}</b><span>${view === "banking" ? "Open to non-residents" : "Fully remote"}</span></div>`;
}
function renderDrawer() {
  const n = Object.values(S.F).reduce((s, x) => s + x.size, 0);
  $("fBtn").textContent = n ? `Filters · ${n}` : "Filters";
  $("fBtn").classList.toggle("on", n > 0);
  $("drawer").innerHTML = FACETS.map(([k, l]) => `<fieldset><legend>${esc(l)}</legend><div class="opts">${optsOf(k).map(([v, lab, c]) => {
    const cnt = DATA.filter(d => d[k] === v && passes(d, k)).length;
    return `<button type="button" class="opt${cnt ? "" : " zero"}" data-f="${k}" data-v="${esc(v)}" aria-pressed="${S.F[k].has(v)}">${c ? `<i style="background:var(--${c})"></i>` : ""}${esc(lab)} <span class="n">${cnt}</span></button>`; }).join("")}</div></fieldset>`).join("")
    + `<div class="dfoot"><span>Options in one group widen the match; separate groups narrow it.</span><button type="button" class="fbtn" id="fClear">Clear all</button></div>`;
  const tags = [];
  for (const [k] of FACETS) for (const v of S.F[k]) tags.push(`<span class="tag">${esc(FLABEL[k])}: ${esc(k === "region" ? v : CAT[k][v]?.[0] ?? v)}<button type="button" data-rm="${k}|${esc(v)}" aria-label="Remove filter">×</button></span>`);
  $("active").innerHTML = tags.join("");
}
$("rankBy").addEventListener("change", e => { if (view === "banking") S.bankBy = e.target.value; else S.rankBy = e.target.value; S.mode = RANKS[e.target.value].map || "band"; renderRank(); save(); });
$("rModes").addEventListener("change", e => { if (e.target.id === "modeSel") { S.mode = e.target.value; renderRank(); save(); } });
$("q").addEventListener("input", () => renderRank());
$("fBtn").addEventListener("click", () => { const open = $("drawer").hidden; $("drawer").hidden = !open; $("fBtn").setAttribute("aria-expanded", open); });
document.addEventListener("click", e => {
  const o = e.target.closest(".opt, .legbtn[data-f]"); if (o) { const s = S.F[o.dataset.f]; s.has(o.dataset.v) ? s.delete(o.dataset.v) : s.add(o.dataset.v);
    if (s.size === optsOf(o.dataset.f).length) s.clear(); renderRank(); save(); return; }
  const rm = e.target.closest("[data-rm]"); if (rm) { const [k, v] = rm.dataset.rm.split("|"); S.F[k].delete(v); renderRank(); save(); return; }
  if (e.target.id === "fClear") { for (const k in S.F) S.F[k].clear(); renderRank(); save(); return; }
  const a = e.target.closest("[data-add]"); if (a) { e.preventDefault(); toggleCmp(a.dataset.add); return; }
});
function toggleCmp(c) {
  if (S.cmp.includes(c)) S.cmp = S.cmp.filter(x => x !== c); else if (S.cmp.length < 5) S.cmp.push(c);
  save();
  if (view === "rank" || view === "banking") renderRank();
  if (view === "compare") renderCompare();
  if (view === "country") renderCountry(true);
}

/* compare + requirements rows */
const ATTRS = [
  { g: "Charity registration" },
  { k: "difficulty", label: "Registration difficulty", note: d => d.bottleneck },
  { k: "no_presence", label: "Remote founding", note: d => d.requirements },
  { k: "fee_bin", label: "Registration fee", x: d => feeTxt(d), note: d => d.fee_usd },
  { k: "time_bin", label: "Time to register", x: d => timeTxt(d), note: d => d.time_to_reg },
  { k: "funding_cat", label: "Foreign funding", note: d => d.donor_restr },
  { k: "gfn", label: "Google for Nonprofits" },
  { g: "Banking" },
  { k: "bank_cat", label: "Charity bank account", note: d => d.bank_access },
  { k: "pb_status", label: "Personal account (non-resident)", note: d => d.pb_banks },
  { k: "pb_method", label: "Personal account opening", note: d => d.pb_docs },
  { k: "pb_res", label: "Residence for account", note: d => d.pb_restr },
  { k: "pb_cost_bin", label: "Personal account fees", x: d => d.pb_year ? usd(d.pb_year) + "/yr" : null, note: d => d.pb_costnote },
  { k: "pb_dep_bin", label: "Minimum deposit", x: d => d.pb_mindep ? dep(d.pb_mindep) : null, note: d => d.pb_dep },
  { g: "Research" },
  { k: "confidence", label: "Research confidence", note: d => d.pb_conf ? `Personal-banking research confidence: ${d.pb_conf}.` : "" },
];
const TEXTS = [["entity", "Entity to register"], ["bottleneck", "Main bottleneck"], ["requirements", "Local requirements"], ["cost_time", "Cost and time in practice"],
  ["tax_exempt", "Tax-exempt status"], ["deduction", "Donor tax deductions"], ["donor_restr", "Foreign funding rules"], ["compliance", "Annual compliance"],
  ["pb_banks", "Banks for non-residents"], ["pb_alt", "Banking alternatives"]];
const NOTES = [];
const cellHTML = (a, d) => { const [l] = cat(a.k, d), x = a.x?.(d), n = a.note?.(d);
  let i = -1; if (n) { i = NOTES.length; NOTES.push([`${d.country}: ${a.label}`, n]); }
  return `<span class="pill"><span class="sym">${SYM[cat(a.k, d)[1]]}</span>${esc(l)}</span>${x && x !== "—" && x !== l ? `<span class="pill x">${esc(x)}</span>` : ""}${i >= 0 ? `<button type="button" class="info" data-note="${i}" aria-label="Details">i</button>` : ""}`; };
function renderCompare() {
  NOTES.length = 0;
  const cs = S.cmp.map(c => byName.get(c)), slots = [...cs, ...Array(5 - cs.length).fill(null)];
  const counts = d => COLORS.map(c => ATTRS.filter(a => a.k && cat(a.k, d)[1] === c).length);
  const t = ($("cmpFind")?.value || "").trim().toLowerCase();
  const visible = a => {
    if (t && !a.label.toLowerCase().includes(t)) return false;
    if (S.hide.size && cs.length && cs.every(d => S.hide.has(cat(a.k, d)[1]))) return false;
    if (S.diffOnly && cs.length > 1 && new Set(cs.map(d => d[a.k])).size === 1) return false;
    return true; };
  let h = `<colgroup><col class="lab">${slots.map(() => "<col>").join("")}</colgroup><thead><tr><th class="lab"><div class="colordots">${COLORS.map(c =>
      `<button type="button" data-hide="${c}" style="background:var(--${c})" aria-pressed="${!S.hide.has(c)}" aria-label="Show ${c} rows"></button>`).join("")}<button type="button" class="diff" data-diff aria-pressed="${S.diffOnly}" aria-label="Show differences only" title="Differences only"></button></div></th>`
    + slots.map(d => `<th>${d ? `<div class="hscore">${cover(d)}<div><b><span class="sb bg-${d.band} ${d.band}" style="font-weight:600">${d.cs}</span></b><div class="dots">${counts(d).map((n, i) => `<span><i style="background:var(--${COLORS[i]})"></i>${n}</span>`).join("")}</div></div></div>`
      : `<div class="hscore"><div><span class="ph">Charity score</span><div class="dots">${COLORS.map(() => `<span><i class="ph"></i></span>`).join("")}</div></div></div>`}</th>`).join("") + `</tr><tr><th class="lab" style="padding:0"><div class="cfilt">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="color:var(--muted)" aria-hidden="true"><path d="M3 4h18l-7 8.5V19l-4 2v-8.5z"/></svg><input id="cmpFind" type="search" placeholder="Filter rows…" aria-label="Filter rows" value="${esc(t)}"></div></th>`
    + slots.map((d, i) => `<th><div class="cname">${d ? `<a href="#/country/${slug(d.country)}" style="color:inherit;text-decoration:none">${esc(d.country)}</a><button type="button" data-add="${esc(d.country)}" aria-label="Remove ${esc(d.country)}">×</button>`
      : `<input list="allC" data-slot="${i}" placeholder="🔍 Select country…" aria-label="Add a country to compare">`}</div></th>`).join("") + `</tr></thead><tbody>`;
  let grp = null;
  for (const a of ATTRS) {
    if (a.g) { grp = a.g; continue; }
    if (!visible(a)) continue;
    if (grp) { h += `<tr class="cgroup"><td class="lab">${esc(grp)}</td>${slots.map(() => "<td></td>").join("")}</tr>`; grp = null; }
    h += `<tr><td class="lab">${esc(a.label)}</td>${slots.map(d => d ? `<td class="cell ${cat(a.k, d)[1]}">${cellHTML(a, d)}</td>` : `<td class="cell blank"></td>`).join("")}</tr>`;
  }
  const tx = TEXTS.filter(([, l]) => !t || l.toLowerCase().includes(t));
  if (tx.length) h += `<tr class="cgroup"><td class="lab">Details (click to expand)</td>${slots.map(() => "<td></td>").join("")}</tr>`
    + tx.map(([k, l]) => `<tr class="textrow"><td class="lab">${esc(l)}</td>${slots.map(d => d ? `<td class="txt"><div class="clamp">${esc(d[k] || "—")}</div></td>` : `<td class="cell blank"></td>`).join("")}</tr>`).join("");
  $("cmp").innerHTML = h + `</tbody>` + `<datalist id="allC">${DATA.filter(d => !S.cmp.includes(d.country)).map(d => `<option value="${esc(d.country)}">`).join("")}</datalist>`;
  const hh = "#/compare/" + S.cmp.map(c => slug(c)).join(",");
  if (location.hash !== hh && view === "compare") history.replaceState(null, "", hh);
}
$("cmp").addEventListener("change", e => { const i = e.target.closest("[data-slot]"); if (i && byName.has(i.value)) toggleCmp(i.value); });
$("cmp").addEventListener("input", e => {
  if (e.target.id === "cmpFind") { const pos = e.target.selectionStart; renderCompare(); const f = $("cmpFind"); f.focus(); f.setSelectionRange(pos, pos); }
  const i = e.target.closest("[data-slot]"); if (i && byName.has(i.value)) toggleCmp(i.value); });
$("cmp").addEventListener("click", e => {
  const hb = e.target.closest("[data-hide]"); if (hb) { const c = hb.dataset.hide; S.hide.has(c) ? S.hide.delete(c) : S.hide.add(c); renderCompare(); return; }
  if (e.target.closest("[data-diff]")) { S.diffOnly = !S.diffOnly; renderCompare(); return; }
  const tr = e.target.closest("tr.textrow"); if (tr) tr.querySelectorAll("td.txt").forEach(td => td.classList.toggle("open"));
});

/* notes popover */
function openNote(btn) { const [t, n] = NOTES[+btn.dataset.note] || []; if (!n) return; const box = $("note");
  box.innerHTML = `<b>${esc(t)}</b>${esc(n)}`; box.hidden = false; const r = btn.getBoundingClientRect();
  box.style.left = Math.max(8, Math.min(r.right - box.offsetWidth, innerWidth - box.offsetWidth - 8)) + "px";
  box.style.top = (r.bottom + 8 + box.offsetHeight > innerHeight ? r.top - box.offsetHeight - 8 : r.bottom + 8) + "px"; }
function closeNote() { $("note").hidden = true; }
document.addEventListener("click", e => { const b = e.target.closest("[data-note]"); if (b) { e.preventDefault(); e.stopPropagation(); openNote(b); } else if (!e.target.closest("#note")) closeNote(); }, true);
addEventListener("scroll", closeNote, { passive: true });

/* country dashboard */
let reqHide = new Set();
function renderCountry(keepMap) {
  NOTES.length = 0;
  const d = byName.get(country), plist = rankOf("power").list, i = plist.indexOf(d);
  const prev = plist[(i - 1 + plist.length) % plist.length], next = plist[(i + 1) % plist.length], inC = S.cmp.includes(d.country);
  const notes = (d.notes || "").split(/\s+\|\s+/).filter(Boolean);
  const srcs = s => (s || "").split(/\s*;\s*/).filter(x => /^https?:\/\//.test(x));
  const link = s => `<a href="${esc(s)}" target="_blank" rel="noopener">${esc(s.replace(/^https?:\/\/(www\.)?/, "").slice(0, 80))}</a>`;
  const sec = (t, b) => b ? `<div class="s"><h3>${esc(t)}</h3><p>${esc(b)}</p></div>` : "";
  let req = "", grp = null;
  for (const a of ATTRS) {
    if (a.g) { grp = a.g; continue; }
    if (reqHide.has(cat(a.k, d)[1])) continue;
    if (grp) { req += `<div class="reqgrp">${esc(grp)}</div>`; grp = null; }
    req += `<div class="req" data-lbl="${esc(a.label.toLowerCase())}"><div class="rl">${esc(a.label)}</div><div class="rc ${cat(a.k, d)[1]}">${cellHTML(a, d)}</div></div>`;
  }
  $("dash").innerHTML = `
    <div class="dleft">${cover(d)}
      <div class="acts"><button type="button" data-add="${esc(d.country)}">${inC ? "Remove" : "Compare"}</button><button type="button" id="goCmp">View compare</button></div>
      <dl class="kv">
        <div><dt>Charity score</dt><dd>${badge(d)}</dd></div>
        <div><dt>Charity power rank</dt><dd>${powerRank(d)}</dd></div>
        <div><dt>Banking rank</dt><dd>${rankOf("pbank").pos.get(d.country) ?? "—"}</dd></div>
        <div><dt>Registration fee</dt><dd>${esc(feeTxt(d))}</dd></div>
        <div><dt>Time to register</dt><dd>${esc(timeTxt(d))}</dd></div>
        <div><dt>Remote founding</dt><dd class="sm">${esc(cat("no_presence", d)[0])}</dd></div>
        <div><dt>Personal account</dt><dd class="sm">${esc(cat("pb_status", d)[0])}</dd></div>
        <div><dt>Account fees / yr</dt><dd>${esc(d.pb_year == null ? "—" : usd(d.pb_year))}</dd></div>
        <div><dt>Google for Nonprofits</dt><dd>${d.gfn === "Yes" ? "Yes" : "No"}</dd></div>
        <div><dt>Region</dt><dd class="sm">${esc(d.region)}</dd></div>
      </dl>
    </div>
    <div class="dmid">
      <h1>${flag(d)}${esc(d.country)} charity dashboard <span class="arrows"><a href="#/country/${slug(prev.country)}" aria-label="Previous: ${esc(prev.country)}" title="${esc(prev.country)}">‹</a><a href="#/country/${slug(next.country)}" aria-label="Next: ${esc(next.country)}" title="${esc(next.country)}">›</a></span></h1>
      <div class="mapbox" id="dMapBox"><div class="zoom"><button type="button" data-z="in" aria-label="Zoom in">+</button><button type="button" data-z="out" aria-label="Zoom out">−</button></div>
        <svg id="dMap" viewBox="0 0 960 500" role="img" aria-label="Map highlighting ${esc(d.country)}"></svg><div class="tip" id="dTip" hidden></div></div>
      ${sbar(d)}
      <div class="seglg">${GROUPS.map(([g], i) => `<span><i style="background:var(--s${i + 1})"></i>${esc(g)} ${Math.round(d.grp[i])}</span>`).join("")}</div>
      <div class="bk"><h2>Score breakdown · ${d.cs} / 100</h2>${FACTORS.map(([k, l, mx]) => `<div class="bkrow"><span>${esc(l)}</span><span class="tr"><i style="width:${100 * d.pts[k] / mx}%;background:var(--s${GROUPS.findIndex(([, ks]) => ks.includes(k)) + 1})"></i></span><b>${Math.round(d.pts[k] * 10) / 10}/${mx}</b></div>`).join("")}</div>
      <div class="dsec"><h2>Registering a charity</h2>
        ${sec("Entity to register", d.entity)}${sec("Main bottleneck", d.bottleneck)}${sec("Local requirements", d.requirements)}${sec("Cost and time in practice", d.cost_time)}
        ${sec("Charity bank account", d.bank_access)}${sec("Tax-exempt status", d.tax_exempt)}${sec("Donor tax deductions", d.deduction)}${sec("Foreign funding rules", d.donor_restr)}${sec("Annual compliance", d.compliance)}
        ${notes.length ? `<div class="s"><h3>Research notes</h3><ul>${notes.map(n => `<li>${esc(n)}</li>`).join("")}</ul></div>` : ""}
        ${srcs(d.sources).length ? `<div class="s"><h3>Sources</h3><ul>${srcs(d.sources).map(s => `<li>${link(s)}</li>`).join("")}</ul></div>` : ""}
      </div>
      <div class="dsec"><h2>Personal bank account as a non-resident</h2>
        ${sec("Documents", d.pb_docs)}${sec("Banks", d.pb_banks)}${sec("Deposit and fees", d.pb_dep)}${sec("Cost figures", d.pb_costnote)}${sec("Restrictions", d.pb_restr)}${sec("Alternatives", d.pb_alt)}
        ${sec("Research confidence", d.pb_conf)}
        ${srcs(d.pb_src).length ? `<div class="s"><h3>Sources</h3><ul>${srcs(d.pb_src).map(s => `<li>${link(s)}</li>`).join("")}</ul></div>` : ""}
      </div>
    </div>
    <div class="dright">
      <h2>${esc(d.country)} requirements</h2>
      <div class="reqtools"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" style="color:var(--muted)" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input id="reqFind" type="search" placeholder="Find a requirement…" aria-label="Find a requirement">
        <div class="colordots">${COLORS.map(c => `<button type="button" data-rhide="${c}" style="background:var(--${c})" aria-pressed="${!reqHide.has(c)}" aria-label="Show ${c} rows"></button>`).join("")}</div></div>
      <div class="reqhead"><span>Requirement</span><span>Status</span></div>
      <div id="reqRows">${req}</div>
    </div>`;
  dMap = makeMap($("dMap"), $("dTip"), c => go("#/country/" + slug(c)));
  dMap.tip(x => `<b>${esc(x.country)}</b><br>Charity score ${x.cs} · rank ${powerRank(x)}`);
  dMap.paint(catFill("band"), () => false, d.country);
  $("dMap").querySelectorAll("path.cty:not(.sel), circle.dot:not(.sel)").forEach(p => p.style.opacity = .7);
  dMap.focus(d.country);
}
$("dash").addEventListener("click", e => {
  if (e.target.id === "goCmp") { if (!S.cmp.includes(country) && S.cmp.length < 5) S.cmp.push(country); go("#/compare/" + S.cmp.map(slug).join(",")); return; }
  const b = e.target.closest("[data-rhide]"); if (b) { const c = b.dataset.rhide; reqHide.has(c) ? reqHide.delete(c) : reqHide.add(c); renderCountry(); }
});
$("dash").addEventListener("input", e => { if (e.target.id !== "reqFind") return; const t = e.target.value.trim().toLowerCase();
  document.querySelectorAll("#reqRows .req").forEach(r => r.hidden = t && !r.dataset.lbl.includes(t)); });

/* modals: find + checker */
function modal(html) { $("mbox").innerHTML = `<button type="button" class="x" id="mClose" aria-label="Close">×</button>` + html; $("modal").hidden = false; }
function closeModal() { $("modal").hidden = true; }
$("modal").addEventListener("click", e => { if (e.target.id === "modal" || e.target.id === "mClose" || e.target.closest(".results a")) closeModal(); });
addEventListener("keydown", e => { if (e.key === "Escape") { closeModal(); closeNote(); } });
function openFind() {
  modal(`<h2 id="mTitle">Find a country</h2><p class="serif">Type a name, region or anything in the research text.</p><input class="big" id="fq" type="search" placeholder="e.g. Estonia, Pacific, foundation…" aria-label="Search countries"><div class="results" id="fres"></div>`);
  const draw = () => { const t = $("fq").value.trim().toLowerCase();
    const r = DATA.filter(d => !t || d.country.toLowerCase().includes(t) || HAY.get(d.country).includes(t))
      .sort((a, b) => (b.country.toLowerCase().startsWith(t) - a.country.toLowerCase().startsWith(t)) || a.country.localeCompare(b.country)).slice(0, 40);
    $("fres").innerHTML = r.map(d => `<a href="#/country/${slug(d.country)}">${flag(d)}${esc(d.country)}<small>${d.cs}</small></a>`).join("") || `<p class="empty">No match.</p>`; };
  $("fq").addEventListener("input", draw); draw(); $("fq").focus();
}
$("checkerBtn").addEventListener("click", () => {
  const opts = [...DATA].sort((a, b) => a.country.localeCompare(b.country)).map(d => `<option value="${esc(d.country)}">${esc(d.country)}</option>`).join("");
  modal(`<h2 id="mTitle">Charity Checker</h2><p class="serif">Can I set up a charity there from Australia, and can I bank there?</p>
    <label for="ckFrom">I live in</label><select id="ckFrom" disabled><option>Australia</option></select>
    <label for="ckTo">I want to register in</label><select id="ckTo"><option value="">Choose a country…</option>${opts}</select><div class="verdict" id="ckOut"></div>`);
  $("ckTo").addEventListener("change", () => { const d = byName.get($("ckTo").value); if (!d) { $("ckOut").innerHTML = ""; return; }
    const row = (k, label, val) => { const [l, c] = cat(k, d); return `<div class="vrow ${c}"><span>${esc(label)}</span><b>${esc(val ?? l)}</b></div>`; };
    $("ckOut").innerHTML = row("difficulty", "Registration difficulty") + row("no_presence", "Can I found it remotely?") + row("fee_bin", "Registration fee", feeTxt(d))
      + row("time_bin", "Time to register", timeTxt(d)) + row("bank_cat", "Charity bank account") + row("pb_status", "Personal account as a non-resident")
      + row("pb_method", "Open it without visiting?") + row("gfn", "Google for Nonprofits")
      + `<p style="margin:6px 0 0;font-size:13.5px"><b>Main bottleneck:</b> ${esc(d.bottleneck)}</p>
         <div style="display:flex;gap:10px;margin-top:8px"><a class="goldbtn fill" href="#/country/${slug(d.country)}" onclick="document.getElementById('modal').hidden=true">Open dashboard</a>
         <button type="button" class="goldbtn" data-add="${esc(d.country)}">Add to compare</button></div>`; });
  $("ckTo").focus();
});

/* menu + theme */
$("moreBtn").addEventListener("click", e => { e.stopPropagation(); const open = $("menu").hidden; $("menu").hidden = !open; $("moreBtn").setAttribute("aria-expanded", open); });
document.addEventListener("click", e => { if (!e.target.closest(".more")) { $("menu").hidden = true; $("moreBtn").setAttribute("aria-expanded", "false"); } });
function applyTheme() {
  document.documentElement.setAttribute("data-theme", S.theme);
  $("themeBtn").textContent = S.theme === "dark" ? "Switch to light theme" : "Switch to dark theme";
}
$("themeBtn").addEventListener("click", () => { S.theme = S.theme === "dark" ? "light" : "dark"; applyTheme(); save(); route(); });
applyTheme();
route();
</script>
"""

if __name__ == "__main__":
    main()
