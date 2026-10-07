#!/usr/bin/env python3
"""Merge workflow research JSON + GfN eligibility list into master CSV/XLSX."""
import csv, json, sys
from pathlib import Path

WS = Path(__file__).parent
GFNP = set(l.strip() for l in (WS / "gfnp_clean.txt").read_text().splitlines() if l.strip())
assert len(GFNP) == 186, f"unexpected GfN list size: {len(GFNP)}"

# Batch-name -> GfN-list-name aliases
ALIASES = {"Turkey": "Turkiye",
           "Republic of the Congo": "Congo (Republic)",
           "Sao Tome & Principe": "São Tomé & Príncipe"}
# Subagent output-name -> canonical batch name
CANON = {"Micronesia (FSM)": "Micronesia"}
# Known non-GfN jurisdictions (verified absent from gfnp_clean.txt)
KNOWN_NO = {"Belarus","China","Cuba","Georgia","Iran","Liechtenstein","Myanmar","Nepal",
            "North Korea","Russia","Somaliland","South Sudan","Sudan","Syria","Western Sahara"}

def gfnp_status(country):
    g = ALIASES.get(country, country)
    if g in GFNP: return "Yes"
    if g in KNOWN_NO: return "No"
    return "No (not on GfN list)"

if len(sys.argv) < 2:
    print("usage: merge.py workflow-result.json", file=sys.stderr); sys.exit(1)
data = json.loads(Path(sys.argv[1]).read_text())
rows = data["rows"] if isinstance(data, dict) else data

# --- rows from subagents ---
out, seen = [], set()
for r in rows:
    c = r.get("country","").strip()
    if not c: continue
    c = CANON.get(c, c)
    if c in seen: continue
    seen.add(c)
    out.append({"Country": c,
        "Google for Nonprofits eligible": gfnp_status(c),
        "Main charitable entity types": r.get("entity_types",""),
        "Difficulty (AU-resident foreign founder)": r.get("difficulty",""),
        "Key local requirements": r.get("local_requirements",""),
        "Est. cost & time": r.get("cost_time",""),
        "Notes": r.get("notes","")})

# --- known gaps the subagents may miss (batches.json didn't include them) ---
EXTRA = {
 "North Korea": ("state-run public organization (no independent charitable sector)", "very hard",
   "no meaningful independent charity registration; foreign involvement barred in practice", "n/a",
   "No independent charitable pathway; no GfN. Excluded from any practical plan."),
 "Russia": ("public organization (NGO) / public foundation registered with Ministry of Justice", "hard",
   "Russian-language filings, foreign-agent law risks for foreign-linked orgs, sanctions on AU side", "n/a",
   "No GfN. Sanctions + foreign-agent regime make this unsuitable for an Australian founder."),
}
for c,(e,d,l,ct,n) in EXTRA.items():
    if c in seen: continue
    seen.add(c)
    out.append({"Country":c,"Google for Nonprofits eligible":gfnp_status(c),
                "Main charitable entity types":e,"Difficulty (AU-resident foreign founder)":d,
                "Key local requirements":l,"Est. cost & time":ct,"Notes":n})

# --- sort by batch order, then alphabetically within batch ---
BATCHES = json.loads((WS/"batches.json").read_text())
order = {}
for k,v in BATCHES.items():
    for i,c in enumerate(v): order[c.lower()] = (k, i, c.lower())
def key(r):
    k = order.get(r["Country"].lower())
    return k if k else ("zzz", 0, r["Country"].lower())
out.sort(key=key)

cols = ["Country","Google for Nonprofits eligible","Main charitable entity types",
        "Difficulty (AU-resident foreign founder)","Key local requirements","Est. cost & time","Notes"]
csv_path = WS / "charities_by_country.csv"
with open(csv_path,"w",newline="",encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(out)
print(f"CSV: {csv_path} ({len(out)} rows)", file=sys.stderr)

missing = [c for v in BATCHES.values() for c in v if c.lower() not in seen]
if missing: print("MISSING from subagent output:", missing, file=sys.stderr)

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); ws = wb.active; ws.title = "All countries"
    hf = PatternFill("solid", fgColor="1F4E79"); hfont = Font(bold=True, color="FFFFFF")
    dfill = {"easy":"C6EFCE","medium":"FFEB9C","hard":"FFC7CE","very hard":"F8CBAD"}
    ws.append(cols)
    for cell in ws[1]: cell.fill, cell.font = hf, hfont
    for r in out:
        ws.append([r[c] for c in cols])
        d = r["Difficulty (AU-resident foreign founder)"]
        if d in dfill: ws.cell(row=ws.max_row, column=4).fill = PatternFill("solid", fgColor=dfill[d])
        if r["Google for Nonprofits eligible"] == "Yes":
            ws.cell(row=ws.max_row, column=2).fill = PatternFill("solid", fgColor="E2EFDA")
    for i,wd in enumerate([24,18,40,16,46,18,54],1): ws.column_dimensions[chr(64+i)].width = wd
    ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
    xlsx_path = WS / "charities_by_country.xlsx"
    wb.save(xlsx_path)
    print(f"XLSX: {xlsx_path}", file=sys.stderr)
except ImportError as e:
    print(f"openpyxl unavailable ({e}); CSV only.", file=sys.stderr)
print("DONE", file=sys.stderr)
