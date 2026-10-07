#!/usr/bin/env python3
"""Build a self-contained interactive web app (single HTML file) from the master CSV.

Reads  charities_by_country_v2.csv  (falls back to charities_by_country.csv if absent)
Writes webapp/index.html  — zero-dependency, opens by double-click.

Features: full-text search, faceted filters (difficulty / GfN / no-presence / region),
sort, per-country detail panel, and aggregate stats. Data is embedded as JSON.
"""
import csv, json, sys
from pathlib import Path

BASE = Path(__file__).parent
V2 = BASE / "charities_by_country_v2.csv"
V1 = BASE / "charities_by_country.csv"
SRC = V2 if V2.exists() else V1
OUT = BASE / "webapp" / "index.html"
DATA_JSON = BASE / "webapp" / "data.json"

REGION = {
    "AU & Oceania": ["Australia","New Zealand","Fiji","Papua New Guinea","Samoa","Tonga","Vanuatu","Solomon Islands","Kiribati","Nauru","Tuvalu","Marshall Islands","Micronesia"],
    "East Asia": ["Mongolia","Japan","South Korea","China","Taiwan","Hong Kong","Macau"],
    "Southeast Asia": ["Singapore","Malaysia","Indonesia","Thailand","Vietnam","Philippines","Cambodia","Laos","Myanmar","Brunei","Timor-Leste"],
    "South Asia": ["India","Pakistan","Bangladesh","Sri Lanka","Nepal","Bhutan","Afghanistan","Maldives"],
    "Middle East": ["Israel","Jordan","Lebanon","Syria","Iraq","Saudi Arabia","Kuwait","Qatar","United Arab Emirates","Oman","Bahrain","Yemen","Palestine"],
    "Central Asia & Caucasus": ["Turkey","Georgia","Armenia","Azerbaijan","Kazakhstan","Uzbekistan","Turkmenistan","Tajikistan","Kyrgyzstan","Iran"],
    "North Africa": ["Egypt","Sudan","Libya","Algeria","Tunisia","Morocco","Mauritania","Western Sahara","Ethiopia","Eritrea","Djibouti","Somalia","Somaliland","South Sudan","Seychelles","Mauritius"],
    "West Africa": ["Nigeria","Ghana","Côte d'Ivoire","Benin","Togo","Burkina Faso","Mali","Guinea","Guinea-Bissau","Senegal","Gambia","Sierra Leone","Liberia","Niger"],
    "Central & S. Africa": ["Cameroon","Central African Republic","Chad","Republic of the Congo","Congo (DRC)","Gabon","Equatorial Guinea","Sao Tome & Principe","Rwanda","Burundi","Uganda","Tanzania","Kenya","Comoros","Madagascar","Zambia","Malawi","Mozambique","Angola","Botswana","Namibia","Zimbabwe","Eswatini","Lesotho","South Africa"],
    "Northern Europe": ["Ireland","United Kingdom","Iceland","Norway","Finland","Sweden","Denmark","Estonia","Latvia","Lithuania"],
    "Western Europe": ["Netherlands","Belgium","Luxembourg","France","Germany","Austria","Switzerland","Liechtenstein","Monaco","San Marino","Andorra"],
    "Central & E. Europe": ["Poland","Czechia","Slovakia","Hungary","Slovenia","Croatia","Bosnia & Herzegovina","Serbia","Montenegro","North Macedonia","Albania","Moldova","Ukraine","Belarus","Romania","Bulgaria","Greece","Cyprus","Malta"],
    "Southern Europe": ["Spain","Portugal","Italy","Vatican City"],
    "Caribbean & N. America": ["Canada","United States","Cuba","Jamaica","Bahamas","Barbados","Trinidad & Tobago","Antigua & Barbuda","Grenada","St. Kitts & Nevis","St. Lucia","St. Vincent & Grenadines","Dominica","Dominican Republic","Haiti"],
    "Central America": ["Mexico","Guatemala","Belize","El Salvador","Honduras","Nicaragua","Costa Rica","Panama"],
    "South America": ["Colombia","Venezuela","Ecuador","Peru","Bolivia","Guyana","Suriname","Brazil","Paraguay","Uruguay","Argentina","Chile"],
    "Other": ["North Korea","Russia"],
}
COUNTRY_REGION = {c: r for r, cs in REGION.items() for c in cs}

# canonical column keys -> csv header (v1 & v2)
FIELD_MAP = [
    ("country",        "Country"),
    ("gfn",            "Google for Nonprofits eligible"),
    ("entity",         "Main charitable entity types"),
    ("difficulty",     "Difficulty (AU-resident foreign founder)"),
    ("requirements",   "Key local requirements"),
    ("cost_time",      "Est. cost & time"),
    ("notes",          "Notes"),
    ("no_presence",    "Foreign founder (no local presence)"),
    ("bottleneck",     "Main bottleneck (remote foreign founder)"),
    ("fee_usd",        "Registration fee (USD)"),
    ("time_to_reg",    "Time to register"),
    ("deduction",      "Charitable deduction regime"),
    ("donor_restr",    "Foreign donor / donation restrictions"),
    ("compliance",     "Annual compliance & reporting"),
    ("tax_exempt",     "Tax-exempt status & benefits"),
    ("confidence",     "Confidence"),
    ("sources",        "Sources"),
]

def build_data():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    out = []
    for r in rows:
        rec = {}
        for key, col in FIELD_MAP:
            rec[key] = (r.get(col) or "").strip()
        rec["region"] = COUNTRY_REGION.get(rec["country"], "Other")
        out.append(rec)
    return out, SRC.name

def main():
    data, src_name = build_data()
    has_enrich = any(d["no_presence"] for d in data)
    DATA_JSON.parent.mkdir(parents=True, exist_ok=True)
    DATA_JSON.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__SRC__", src_name)
    html = html.replace("__HAS_ENRICH__", "1" if has_enrich else "0")
    OUT.write_text(html, encoding="utf-8")
    n = len(data)
    gfn = sum(1 for d in data if d["gfn"].lower().startswith("yes"))
    print(f"wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB) — {n} countries, GfN {gfn}, enriched={has_enrich}, src={src_name}")

TEMPLATE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Charity Registration Atlas — 198 Countries</title>
<style>
:root{
  --canvas:#010102;--surface-1:#0f1011;--surface-2:#141516;--surface-3:#18191a;--surface-4:#191a1b;
  --hairline:#23252a;--hairline-strong:#34343a;
  --ink:#f7f8f8;--ink-muted:#d0d6e0;--ink-subtle:#8a8f98;--ink-tertiary:#62666d;
  --primary:#5e6ad2;--primary-hover:#828fff;--on-primary:#fff;
  --success:#27a644;--danger:#e5484d;--warn:#e0a418;
  --font:-apple-system,BlinkMacSystemFont,"Inter","Manrope","Segoe UI",sans-serif;
  --mono:"SF Mono",ui-monospace,"JetBrains Mono",Menlo,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{background:var(--canvas);color:var(--ink);font-family:var(--font);font-size:13px;line-height:1.5;-webkit-font-smoothing:antialiased}
h1,h2,h3{font-weight:600;letter-spacing:-.4px;margin:0}
.mono{font-family:var(--mono)}
a{color:var(--primary-hover);text-decoration:none}
a:hover{text-decoration:underline}
.topbar{position:sticky;top:0;z-index:30;background:rgba(1,1,2,.82);backdrop-filter:blur(10px);border-bottom:1px solid var(--hairline)}
.tb-in{max-width:1440px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.brand{display:flex;align-items:baseline;gap:10px}
.brand .mark{font-size:16px;font-weight:600;letter-spacing:-.6px}
.brand .dot{width:7px;height:7px;border-radius:50%;background:var(--primary);display:inline-block;align-self:center}
.brand .sub{color:var(--ink-subtle);font-size:12px}
.search{flex:1;min-width:220px;max-width:520px}
.search input{width:100%;background:var(--surface-1);border:1px solid var(--hairline);color:var(--ink);
  border-radius:8px;padding:8px 12px;font-size:13px;font-family:var(--font);outline:none}
.search input:focus{border-color:var(--primary);box-shadow:0 0 0 2px rgba(94,106,210,.35)}
.stats{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}
.stat{background:var(--surface-1);border:1px solid var(--hairline);border-radius:8px;padding:6px 12px;min-width:74px}
.stat .n{font-family:var(--mono);font-size:16px;font-weight:600;letter-spacing:-.5px}
.stat .l{color:var(--ink-subtle);font-size:10.5px;text-transform:uppercase;letter-spacing:.04em}
.wrap{max-width:1440px;margin:0 auto;padding:18px 20px 80px;display:grid;grid-template-columns:250px 1fr;gap:20px}
aside{position:sticky;top:64px;align-self:start;max-height:calc(100vh - 80px);overflow:auto}
.fgroup{border:1px solid var(--hairline);border-radius:10px;background:var(--surface-1);margin-bottom:12px;padding:10px}
.fgroup h4{margin:0 0 8px;font-size:11px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-subtle);font-weight:600}
.chip{display:flex;align-items:center;gap:8px;padding:5px 8px;border-radius:7px;cursor:pointer;color:var(--ink-muted);user-select:none}
.chip:hover{background:var(--surface-2)}
.chip.on{background:var(--surface-4);color:var(--ink)}
.chip .cb{width:14px;height:14px;border-radius:4px;border:1px solid var(--hairline-strong);flex:none;display:grid;place-items:center;font-size:10px}
.chip.on .cb{background:var(--primary);border-color:var(--primary);color:#fff}
.chip .ct{flex:1}
.chip .cc{font-family:var(--mono);color:var(--ink-subtle);font-size:11px}
.clearbtn{width:100%;background:transparent;border:1px solid var(--hairline);color:var(--ink-subtle);border-radius:8px;padding:7px;cursor:pointer;font-size:12px;font-family:var(--font)}
.clearbtn:hover{background:var(--surface-2);color:var(--ink)}
main{min-width:0}
.toolbar{display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap}
.toolbar .count{color:var(--ink-subtle);font-size:12px}
.toolbar select{background:var(--surface-1);border:1px solid var(--hairline);color:var(--ink);border-radius:8px;padding:7px 10px;font-size:12px;font-family:var(--font);outline:none;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:12px}
.card{background:var(--surface-1);border:1px solid var(--hairline);border-radius:12px;padding:14px;cursor:pointer;transition:border-color .12s,background .12s;position:relative}
.card:hover{border-color:var(--hairline-strong);background:var(--surface-2)}
.card.sel{border-color:var(--primary);background:var(--surface-4)}
.card .top{display:flex;align-items:flex-start;gap:10px}
.card .name{font-size:14.5px;font-weight:600;letter-spacing:-.3px;flex:1}
.card .reg{color:var(--ink-tertiary);font-size:11px;margin-top:2px}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:10.5px;font-weight:600;padding:2px 8px;border-radius:20px;white-space:nowrap}
.badge .d{width:6px;height:6px;border-radius:50%}
.b-easy{color:var(--success);background:rgba(39,166,68,.1)}
.b-medium{color:var(--warn);background:rgba(224,164,24,.1)}
.b-hard{color:#f0883e;background:rgba(240,136,62,.1)}
.b-veryhard{color:var(--danger);background:rgba(229,72,77,.1)}
.b-none{color:var(--ink-tertiary);background:rgba(98,102,109,.12)}
.b-gfn{color:var(--primary-hover);background:rgba(94,106,210,.12)}
.b-nogfn{color:var(--ink-tertiary);background:rgba(98,102,109,.1)}
.b-yes{color:var(--success);background:rgba(39,166,68,.1)}
.b-partial{color:var(--warn);background:rgba(224,164,24,.1)}
.b-no{color:var(--danger);background:rgba(229,72,77,.1)}
.card .meta{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.card .blurb{color:var(--ink-subtle);font-size:12px;margin-top:10px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card .conf{position:absolute;top:14px;right:14px;font-size:9.5px;font-family:var(--mono);color:var(--ink-tertiary);border:1px solid var(--hairline);border-radius:4px;padding:1px 5px}
/* detail panel */
.drawer{position:fixed;top:0;right:0;height:100vh;width:min(560px,100vw);background:var(--surface-1);border-left:1px solid var(--hairline-strong);z-index:40;transform:translateX(100%);transition:transform .2s ease;overflow:auto}
.drawer.open{transform:none}
.drawer .dhead{position:sticky;top:0;background:var(--surface-1);border-bottom:1px solid var(--hairline);padding:18px 20px;display:flex;align-items:flex-start;gap:12px}
.drawer .dhead .ttl{flex:1}
.drawer .dhead h2{font-size:20px;letter-spacing:-.5px}
.drawer .dhead .sub{color:var(--ink-subtle);font-size:12px;margin-top:3px}
.x{background:transparent;border:1px solid var(--hairline);color:var(--ink-subtle);width:30px;height:30px;border-radius:8px;cursor:pointer;font-size:15px;flex:none}
.x:hover{background:var(--surface-2);color:var(--ink)}
.dbody{padding:18px 20px 60px}
.sec{margin-bottom:18px}
.sec .k{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-subtle);font-weight:600;margin-bottom:6px}
.sec .v{color:var(--ink-muted);font-size:13px;white-space:pre-wrap;word-break:break-word}
.kvgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.kv{background:var(--surface-2);border:1px solid var(--hairline);border-radius:9px;padding:10px 12px}
.kv .k{font-size:10px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-subtle);font-weight:600;margin-bottom:4px}
.kv .v{font-size:13px;color:var(--ink)}
.srclist a{display:block;font-family:var(--mono);font-size:11.5px;margin-bottom:4px;color:var(--primary-hover);word-break:break-all}
.scrim{position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:35;opacity:0;pointer-events:none;transition:opacity .2s}
.scrim.open{opacity:1;pointer-events:auto}
.empty{padding:60px 20px;text-align:center;color:var(--ink-subtle)}
.tagrow{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.tag{font-size:11px;color:var(--ink-subtle);background:var(--surface-2);border:1px solid var(--hairline);border-radius:6px;padding:2px 8px}
@media(max-width:900px){.wrap{grid-template-columns:1fr}aside{position:static;max-height:none}.stats{margin-left:0}}
</style></head>
<body>
<div class="topbar"><div class="tb-in">
  <div class="brand"><span class="dot"></span><span class="mark">Charity Registration Atlas</span><span class="sub">198 jurisdictions · AU-resident foreign founder</span></div>
  <div class="search"><input id="q" placeholder="Search countries, entity types, requirements, notes…"></div>
  <div class="stats" id="stats"></div>
</div></div>
<div class="wrap">
  <aside id="filters"></aside>
  <main>
    <div class="toolbar">
      <span class="count" id="count"></span>
      <div style="flex:1"></div>
      <label style="color:var(--ink-subtle);font-size:12px">Sort</label>
      <select id="sort">
        <option value="country">Country A–Z</option>
        <option value="difficulty">Easiest first</option>
        <option value="gfn">GfN-eligible first</option>
        <option value="noproblem">No-presence feasible first</option>
        <option value="fee">Fee low→high</option>
      </select>
    </div>
    <div class="grid" id="grid"></div>
  </main>
</div>
<div class="scrim" id="scrim"></div>
<div class="drawer" id="drawer"></div>
<script>
const DATA = __DATA__;
const HAS_ENRICH = __HAS_ENRICH__;
const SRC = "__SRC__";
const DIFF_ORDER = {"easy":0,"medium":1,"hard":2,"very hard":3};
const PRESENCE_ORDER = {"yes":0,"partial":1,"no":3,"":4};

const state = {q:"", difficulty:new Set(), gfn:new Set(), presence:new Set(), region:new Set(), sort:"country"};

function esc(s){return String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function norm(s){return (s??"").toLowerCase().trim();}
function diffBadge(d){const k=norm(d);const cls={"easy":"b-easy","medium":"b-medium","hard":"b-hard","very hard":"b-veryhard"}[k]||"b-none";return `<span class="badge ${cls}"><span class="d"></span>${esc(d||"n/a")}</span>`;}
function gfnBadge(g){const y=(g??"").toLowerCase().startsWith("yes");return `<span class="badge ${y?"b-gfn":"b-nogfn"}">${y?"GfN ✓":"no GfN"}</span>`;}
function presBadge(p){const k=norm(p);const cls={yes:"b-yes",partial:"b-partial",no:"b-no"}[k]||"b-none";return `<span class="badge ${cls}">${k?k:"?"}</span>`;}

function filtered(){
  const q=norm(state.q);
  let rows=DATA.filter(d=>{
    if(state.difficulty.size && !state.difficulty.has(norm(d.difficulty)))return false;
    if(state.gfn.size){const y=(d.gfn??"").toLowerCase().startsWith("yes")?"yes":"no";if(!state.gfn.has(y))return false;}
    if(state.presence.size && !state.presence.has(norm(d.no_presence)))return false;
    if(state.region.size && !state.region.has(d.region))return false;
    if(q){const hay=norm([d.country,d.entity,d.requirements,d.notes,d.cost_time,d.bottleneck,d.deduction,d.donor_restr,d.fee_usd].join(" "));if(!hay.includes(q))return false;}
    return true;
  });
  const s=state.sort;
  rows.sort((a,b)=>{
    if(s==="country")return a.country.localeCompare(b.country);
    if(s==="difficulty")return (DIFF_ORDER[norm(a.difficulty)]??9)-(DIFF_ORDER[norm(b.difficulty)]??9)||a.country.localeCompare(b.country);
    if(s==="gfn")return(((a.gfn||"").toLowerCase().startsWith("yes")?0:1)-((b.gfn||"").toLowerCase().startsWith("yes")?0:1))||a.country.localeCompare(b.country);
    if(s==="noproblem")return (PRESENCE_ORDER[norm(a.no_presence)]??9)-(PRESENCE_ORDER[norm(b.no_presence)]??9)||a.country.localeCompare(b.country);
    if(s==="fee")return feeNum(a.fee_usd)-feeNum(b.fee_usd)||a.country.localeCompare(b.country);
    return 0;
  });
  return rows;
}
function feeNum(f){if(!f)return 1e9;const m=String(f).replace(/[^0-9.]/g,"");if(!m)return 1e9;const v=parseFloat(m);return isNaN(v)?1e9:v;}

function facet(key,label,values,order){
  const counts={};DATA.forEach(d=>{const v=norm(d[key]);if(v)counts[v]=(counts[v]||0)+1;});
  const items=Object.entries(counts).sort((a,b)=>(order?(order[a[0]]??9)-(order[b[0]]??9)):a[0].localeCompare(b[0])).sort((a,b)=>{
    if(order){const oa=order[a[0]]??99,ob=order[b[0]]??99;if(oa!==ob)return oa-ob;}return b[1]-a[1];});
  let h=`<div class="fgroup"><h4>${label}</h4>`;
  items.forEach(([v,c])=>{
    const on=state[key].has(v)?"on":"";
    const disp=(v??"(none)").replace(/\b\w/g,m=>m.toUpperCase());
    h+=`<div class="chip ${on}" data-facet="${key}" data-val="${esc(v)}"><span class="cb">${on?"✓":""}</span><span class="ct">${esc(disp)}</span><span class="cc">${c}</span></div>`;
  });
  h+=`</div>`;return h;
}
function renderFilters(){
  const el=document.getElementById("filters");
  el.innerHTML=
    facet("difficulty","Difficulty",null,DIFF_ORDER)+
    facet("gfn","GfN eligibility",null,null)+
    (HAS_ENRICH?facet("no_presence","No-local-presence",null,PRESENCE_ORDER):"")+
    facet("region","Region",null,null)+
    `<button class="clearbtn" id="clear">Clear all filters</button>`;
  el.querySelectorAll("[data-facet]").forEach(ch=>ch.onclick=()=>{
    const k=ch.dataset.facet,v=ch.dataset.val;
    if(state[k].has(v))state[k].delete(v);else state[k].add(v);
    renderFilters();renderGrid();
  });
  document.getElementById("clear").onclick=()=>{state.difficulty.clear();state.gfn.clear();state.presence.clear();state.region.clear();state.q="";document.getElementById("q").value="";renderFilters();renderGrid();};
}
function renderStats(){
  const n=DATA.length,gfn=DATA.filter(d=>(d.gfn||"").toLowerCase().startsWith("yes")).length;
  const easy=DATA.filter(d=>norm(d.difficulty)==="easy").length;
  const nopres=DATA.filter(d=>norm(d.no_presence)==="yes").length;
  const st=document.getElementById("stats");
  const items=[["Countries",n],["GfN-eligible",gfn],["Easy",easy]];
  if(HAS_ENRICH)items.push(["No-presence OK",nopres]);
  st.innerHTML=items.map(([l,v])=>`<div class="stat"><div class="n">${v}</div><div class="l">${l}</div></div>`).join("");
}
function cardHTML(d){
  const sel=state.selected===d.country?"sel":"";
  const blurb=(d.entity||d.requirements||"").slice(0,160);
  let meta=diffBadge(d.difficulty)+gfnBadge(d.gfn);
  if(HAS_ENRICH&&d.no_presence)meta+=presBadge(d.no_presence);
  const conf=d.confidence?`<span class="conf">${esc(d.confidence)}</span>`:"";
  return `<div class="card ${sel}" data-c="${esc(d.country)}">${conf}
    <div class="top"><div class="name">${esc(d.country)}<div class="reg">${esc(d.region)}</div></div></div>
    <div class="meta">${meta}</div>
    ${d.fee_usd?`<div class="tagrow"><span class="tag">fee ${esc(d.fee_usd)}</span>${d.time_to_reg?`<span class="tag">${esc(d.time_to_reg)}</span>`:""}</div>`:""}
    <div class="blurb">${esc(blurb)}</div></div>`;
}
function renderGrid(){
  const rows=filtered();
  document.getElementById("count").textContent=`${rows.length} of ${DATA.length} countries`;
  const g=document.getElementById("grid");
  if(!rows.length){g.innerHTML=`<div class="empty">No countries match your filters.</div>`;return;}
  g.innerHTML=rows.map(cardHTML).join("");
  g.querySelectorAll(".card").forEach(c=>c.onclick=()=>{state.selected=c.dataset.c;renderGrid();openDrawer(c.dataset.c);});
}
function kv(k,v){if(!v)return "";return `<div class="kv"><div class="k">${k}</div><div class="v">${esc(v)}</div></div>`;}
function openDrawer(name){
  const d=DATA.find(x=>x.country===name);if(!d)return;
  const src=(d.sources||"").split(/;\s*/).filter(Boolean);
  const dr=document.getElementById("drawer");
  let h=`<div class="dhead"><div class="ttl"><h2>${esc(d.country)}</h2><div class="sub">${esc(d.region)}</div></div><button class="x" id="dx">✕</button></div><div class="dbody">`;
  h+=`<div class="sec"><div class="k">At a glance</div><div class="tagrow">${diffBadge(d.difficulty)}${gfnBadge(d.gfn)}${HAS_ENRICH?presBadge(d.no_presence):""}</div></div>`;
  h+=`<div class="sec"><div class="kvgrid">`;
  h+=kv("GfN eligible",d.gfn)+kv("Difficulty",d.difficulty)+kv("Registration fee",d.fee_usd)+kv("Time to register",d.time_to_reg);
  h+=kv("No-presence feasible",d.no_presence)+kv("Confidence",d.confidence)+`</div></div>`;
  if(d.bottleneck)h+=`<div class="sec"><div class="k">Main bottleneck (remote foreign founder)</div><div class="v">${esc(d.bottleneck)}</div></div>`;
  h+=`<div class="sec"><div class="k">Main charitable entity types</div><div class="v">${esc(d.entity)||"—"}</div></div>`;
  h+=`<div class="sec"><div class="k">Key local requirements</div><div class="v">${esc(d.requirements)||"—"}</div></div>`;
  h+=`<div class="sec"><div class="k">Est. cost &amp; time</div><div class="v">${esc(d.cost_time)||"—"}</div></div>`;
  if(d.compliance)h+=`<div class="sec"><div class="k">Annual compliance &amp; reporting</div><div class="v">${esc(d.compliance)}</div></div>`;
  if(d.tax_exempt)h+=`<div class="sec"><div class="k">Tax-exempt status &amp; benefits</div><div class="v">${esc(d.tax_exempt)}</div></div>`;
  if(HAS_ENRICH){
    h+=`<div class="sec"><div class="k">Charitable deduction regime</div><div class="v">${esc(d.deduction)||"—"}</div></div>`;
    h+=`<div class="sec"><div class="k">Foreign donor / donation restrictions</div><div class="v">${esc(d.donor_restr)||"—"}</div></div>`;
  }
  h+=`<div class="sec"><div class="k">Notes</div><div class="v">${esc(d.notes)||"—"}</div></div>`;
  if(src.length)h+=`<div class="sec"><div class="k">Sources</div><div class="srclist">${src.map(u=>`<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>`).join("")}</div></div>`;
  h+=`</div>`;
  dr.innerHTML=h;dr.classList.add("open");document.getElementById("scrim").classList.add("open");
  document.getElementById("dx").onclick=closeDrawer;
}
function closeDrawer(){document.getElementById("drawer").classList.remove("open");document.getElementById("scrim").classList.remove("open");}
document.getElementById("scrim").onclick=closeDrawer;
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeDrawer();});
document.getElementById("q").addEventListener("input",e=>{state.q=e.target.value;renderGrid();});
document.getElementById("sort").addEventListener("change",e=>{state.sort=e.target.value;renderGrid();});
renderStats();renderFilters();renderGrid();
</script>
</body></html>"""

if __name__ == "__main__":
    main()
