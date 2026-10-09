"""Add newly researched countries (research/new_countries/*.json) to the v2 CSV.

Each file is one row with exactly the CSV's 18 columns. Rows are validated
(enum columns, non-empty cells, http sources) and inserted or replaced by
Country, so re-running is idempotent.
"""
import csv
import glob
import json

PATH = "charities_by_country_v2.csv"
ENUMS = {
    "Google for Nonprofits eligible": {"Yes", "No"},
    "Difficulty (AU-resident foreign founder)": {"easy", "medium", "hard", "very hard"},
    "Foreign founder (no local presence)": {"yes", "partial", "no"},
    "Confidence": {"high", "med"},
}

with open(PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    rows = list(reader)
index = {r["Country"]: i for i, r in enumerate(rows)}

added = replaced = 0
for fp in sorted(glob.glob("research/new_countries/*.json")):
    with open(fp, encoding="utf-8") as f:
        rec = json.load(f)
    if set(rec) != set(cols):
        raise SystemExit(f"{fp}: columns differ: missing {set(cols) - set(rec)}, extra {set(rec) - set(cols)}")
    for col, ok in ENUMS.items():
        if rec[col] not in ok:
            raise SystemExit(f"{fp}: bad {col!r}: {rec[col]!r}")
    empty = [c for c in cols if not str(rec[c]).strip()]
    if empty:
        raise SystemExit(f"{fp}: empty cells {empty}")
    if not rec["Sources"].startswith("http"):
        raise SystemExit(f"{fp}: Sources must be URLs")
    row = {c: str(rec[c]).strip() for c in cols}
    if row["Country"] in index:
        if rows[index[row["Country"]]] != row:
            rows[index[row["Country"]]] = row
            replaced += 1
    else:
        index[row["Country"]] = len(rows)
        rows.append(row)
        added += 1

with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

print(f"{added} added, {replaced} replaced, {len(rows)} rows total")
