#!/usr/bin/env python3
"""Build the enriched XLSX deliverable from charities_by_country_v2.csv.

Sheets:
  1. Master            — all columns, difficulty heat + GfN highlight, filters, frozen header
  2. Top-10 Shortlist  — ranked jurisdictions for an AU-resident foreign founder
  3. Regional Summary  — per-region aggregates
  4. Methodology       — how the table was built, schema legend, caveats
"""
import csv, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = Path(__file__).parent
SRC = BASE / "charities_by_country_v2.csv"
OUT = BASE / "charities_by_country_v2.xlsx"

DIFF_FILL = {
    "easy":      PatternFill("solid", start_color="C6EFCE"),
    "medium":    PatternFill("solid", start_color="FFEB9C"),
    "hard":      PatternFill("solid", start_color="FFD1A6"),
    "very hard": PatternFill("solid", start_color="F4B8B8"),
}
GFN_YES = PatternFill("solid", start_color="DDEBF7")
HEADER_FILL = PatternFill("solid", start_color="305496")
HEADER_FONT = Font(color="FFFFFF", bold=True)
THIN = Border(*[Side(style="thin", color="D0D0D0")]*4)

REGION = {
    "AU_OCE": ["Australia","New Zealand","Fiji","Papua New Guinea","Samoa","Tonga","Vanuatu","Solomon Islands","Kiribati","Nauru","Tuvalu","Marshall Islands","Micronesia","Palau"],
    "AS_EAST": ["Mongolia","Japan","South Korea","North Korea","China","Taiwan","Hong Kong","Macau"],
    "AS_SOUTHEAST": ["Singapore","Malaysia","Indonesia","Thailand","Vietnam","Philippines","Cambodia","Laos","Myanmar","Brunei","Timor-Leste"],
    "SA": ["India","Pakistan","Bangladesh","Sri Lanka","Nepal","Bhutan","Afghanistan","Maldives"],
    "ME": ["Israel","Jordan","Lebanon","Syria","Iraq","Saudi Arabia","Kuwait","Qatar","United Arab Emirates","Oman","Bahrain","Yemen","Palestine"],
    "CA": ["Turkey","Georgia","Armenia","Azerbaijan","Kazakhstan","Uzbekistan","Turkmenistan","Tajikistan","Kyrgyzstan","Iran"],
    "NA": ["Egypt","Sudan","Libya","Algeria","Tunisia","Morocco","Mauritania","Western Sahara","Ethiopia","Eritrea","Djibouti","Somalia","Somaliland","South Sudan","Seychelles","Mauritius"],
    "WA": ["Nigeria","Ghana","Côte d'Ivoire","Benin","Togo","Burkina Faso","Mali","Guinea","Guinea-Bissau","Senegal","Gambia","Sierra Leone","Liberia","Niger","Cabo Verde"],
    "CA2": ["Cameroon","Central African Republic","Chad","Republic of the Congo","Congo (DRC)","Gabon","Equatorial Guinea","Sao Tome & Principe","Rwanda","Burundi","Uganda","Tanzania","Kenya","Comoros","Madagascar","Zambia","Malawi","Mozambique","Angola","Botswana","Namibia","Zimbabwe","Eswatini","Lesotho","South Africa"],
    "EU_N": ["Ireland","United Kingdom","Iceland","Greenland","Norway","Finland","Sweden","Denmark","Estonia","Latvia","Lithuania"],
    "EU_B": ["Netherlands","Belgium","Luxembourg","France","Germany","Austria","Switzerland","Liechtenstein","Monaco","San Marino","Andorra"],
    "EU_C": ["Poland","Czechia","Slovakia","Hungary","Slovenia","Croatia","Bosnia & Herzegovina","Serbia","Montenegro","North Macedonia","Albania","Kosovo","Moldova","Ukraine","Belarus","Russia","Romania","Bulgaria","Greece","Cyprus","Malta"],
    "EU_S": ["Spain","Portugal","Italy","Vatican City"],
    "AM_CARIB": ["Canada","United States","Cuba","Jamaica","Bahamas","Barbados","Trinidad & Tobago","Antigua & Barbuda","Grenada","St. Kitts & Nevis","St. Lucia","St. Vincent & Grenadines","Dominica","Dominican Republic","Haiti"],
    "AM_CENTRAL": ["Mexico","Guatemala","Belize","El Salvador","Honduras","Nicaragua","Costa Rica","Panama"],
    "AM_SOUTH": ["Colombia","Venezuela","Ecuador","Peru","Bolivia","Guyana","Suriname","Brazil","Paraguay","Uruguay","Argentina","Chile"],
}
COUNTRY_REGION = {c: r for r, cs in REGION.items() for c in cs}

DIFF_SCORE = {"easy": 0, "medium": 1, "hard": 2, "very hard": 3, "": 2}
PRES_SCORE = {"yes": 0, "partial": 1, "no": 3, "": 2}

def score(r):
    s = DIFF_SCORE.get(r.get("Difficulty (AU-resident foreign founder)", "").lower(), 2) * 2
    s += PRES_SCORE.get(r.get("Foreign founder (no local presence)", "").lower(), 2) * 2
    if r.get("Google for Nonprofits eligible", "") == "Yes":
        s += 0
    else:
        s += 3
    conf = r.get("Confidence", "").lower()
    s += {"high": 0, "med": 1, "low": 2}.get(conf, 2)
    return s

def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    header = list(rows[0].keys())
    wb = Workbook()

    # ---------- Sheet 1: Master ----------
    ws = wb.active
    ws.title = "Master"
    ws.append(header)
    for r in rows:
        ws.append([r[c] for c in header])
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(vertical="center", wrap_text=True)
    diff_idx = header.index("Difficulty (AU-resident foreign founder)") + 1
    gfn_idx = header.index("Google for Nonprofits eligible") + 1
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.border = THIN
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        d = row[diff_idx - 1].value
        if d in DIFF_FILL:
            row[diff_idx - 1].fill = DIFF_FILL[d]
        if (row[gfn_idx - 1].value or "").startswith("Yes"):
            row[gfn_idx - 1].fill = GFN_YES
    widths = {0: 26, 1: 12, 2: 30, 3: 12, 4: 42, 5: 22, 6: 46, 7: 14, 8: 30, 9: 14, 10: 24, 11: 26, 12: 26, 13: 10, 14: 46, 15: 40, 16: 40, 17: 40}
    for i in range(len(header)):
        ws.column_dimensions[get_column_letter(i+1)].width = widths.get(i, 24)
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions

    # ---------- Sheet 2: Top-10 Shortlist ----------
    ranked = sorted(rows, key=lambda r: (score(r), r["Country"].lower()))
    top = ranked[:10]
    ws2 = wb.create_sheet("Top-10 Shortlist")
    cols2 = ["Rank", "Country", "Difficulty", "No-presence feasible?", "Fee (USD)", "Time", "GfN eligible", "Why it ranks here", "Sources"]
    ws2.append(cols2)
    for cell in ws2[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    for i, r in enumerate(top, 1):
        why = (f"difficulty={r.get('Difficulty (AU-resident foreign founder)','?')}, "
               f"no-presence={r.get('Foreign founder (no local presence)','?')}, "
               f"GfN={r.get('Google for Nonprofits eligible','?')}, "
               f"confidence={r.get('Confidence','?')}")
        ws2.append([i, r["Country"], r.get("Difficulty (AU-resident foreign founder)"),
                    r.get("Foreign founder (no local presence)"), r.get("Registration fee (USD)"),
                    r.get("Time to register"), r.get("Google for Nonprofits eligible"), why, r.get("Sources", "")])
    for i, w in enumerate([6, 24, 12, 16, 12, 12, 12, 52, 60], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w
    for row in ws2.iter_rows(min_row=2):
        for cell in row:
            cell.border = THIN
            cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws2.freeze_panes = "A2"

    # ---------- Sheet 3: Regional Summary ----------
    ws3 = wb.create_sheet("Regional Summary")
    cols3 = ["Region", "Countries", "GfN-eligible", "easy", "medium", "hard", "very hard", "No-presence 'yes'"]
    ws3.append(cols3)
    for cell in ws3[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
    for region, countries in REGION.items():
        rs = [r for r in rows if r["Country"] in countries]
        cnt = lambda key, val: sum(1 for r in rs if r.get(key, "").lower() == val)
        ws3.append([region, len(rs),
                    sum(1 for r in rs if (r.get("Google for Nonprofits eligible") or "").startswith("Yes")),
                    cnt("Difficulty (AU-resident foreign founder)", "easy"),
                    cnt("Difficulty (AU-resident foreign founder)", "medium"),
                    cnt("Difficulty (AU-resident foreign founder)", "hard"),
                    cnt("Difficulty (AU-resident foreign founder)", "very hard"),
                    sum(1 for r in rs if (r.get("Foreign founder (no local presence)") or "").lower() == "yes")])
    for i, w in enumerate([14, 10, 12, 8, 8, 8, 10, 18], 1):
        ws3.column_dimensions[get_column_letter(i)].width = w
    for row in ws3.iter_rows():
        for cell in row:
            cell.border = THIN
    ws3.freeze_panes = "A2"

    # ---------- Sheet 4: Methodology ----------
    ws4 = wb.create_sheet("Methodology")
    ws4.column_dimensions["A"].width = 34
    ws4.column_dimensions["B"].width = 110
    def put(row_, a, b):
        ws4.cell(row=row_, column=1, value=a).font = Font(bold=True)
        c = ws4.cell(row=row_, column=2, value=b)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    rr = 1
    put(rr, "Purpose", "Charity-registration viability per country for a founder residing in AUSTRALIA (no other country ties). Built for choosing where to register a charity and assessing Google for Nonprofits eligibility."); rr += 2
    put(rr, "Primary columns", "Country; GfN eligible (186-name authoritative Google for Nonprofits list); main charitable entity types; difficulty (easy/medium/hard/very hard) for a remote AU-resident foreign founder; key local requirements; est. cost & time; notes."); rr += 2
    put(rr, "Enrichment columns", "Foreign founder (no local presence) = yes/partial/no; main bottleneck; registration fee USD; realistic time; local charitable-deduction regime; foreign-donor/donation restrictions (FCRA-style); annual compliance & reporting (ongoing filings, audit, consequences); tax-exempt status & benefits (recognition pathway, tax benefits); bank account remote feasibility (online / local visit / local agent / blocked); confidence (high/med/low); source URLs."); rr += 2
    put(rr, "Method", f"{len(rows)} jurisdictions researched via DSH subagent fan-out (16 regional batches, 196 countries + North Korea/Russia extras; Palau, Kosovo and Cabo Verde added Oct 2026), then enrichment passes 2 (32 agents x ~6 countries), 2b (141 gap-filler deep-dives), 3 (annual compliance), 4 (tax-exemption) and 5 (bank-access feasibility) with fresh web research against official registries, tax authorities and NGO-law guides. All rows reached high/med confidence (zero 'low' remaining). Costs in USD approximations; times are realistic end-to-end durations for a foreign founder."); rr += 2
    put(rr, "Caveats", "Fees/times are official-fee approximations and exclude agent/lawyer costs (remote registration usually adds 1-3x). Confidence reflects source quality: 'low' = background knowledge, official registry not located. Verify against the cited sources before committing. Not legal advice."); rr += 2
    _non = sorted(r["Country"] for r in rows if r.get("Google for Nonprofits eligible") != "Yes")
    put(rr, "GfN list", f"186 authoritative names tokenized from the Google for Nonprofits program list; {len(rows) - len(_non)} of {len(rows)} countries qualify. The {len(_non)} not on the list: {', '.join(_non)}."); rr += 2
    put(rr, "Reproducibility", "merge.py regenerates v1; merge_enrich.py folds enrich-out/e*.json into charities_by_country_v2.csv; this script builds the XLSX. Run in order after any data change.")

    wb.save(OUT)
    print(f"wrote {OUT}: 4 sheets, master {len(rows)} rows x {len(header)} cols")
    print("top-10:", [r["Country"] for r in top])

if __name__ == "__main__":
    main()
