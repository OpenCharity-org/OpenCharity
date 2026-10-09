"""Apply targeted follow-up research (verify-rest-out/followup_*.json) to the v2 CSV.

Each follow-up item: {id, country, verdict, finding, source, cell_edits}.
Only verdict == "corrected" items have their cell_edits applied (minus SKIP).
Every confirmed/corrected item gets a short dated note and its source(s).
NOTE_FIX rewrites earlier notes that a follow-up showed to be wrong.
"""
import csv
import glob
import json
import re

PATH = "charities_by_country_v2.csv"

# follow-up ids whose cell edits are rejected on review: {id: reason}
SKIP = {}
# per-cell overrides on review: {id: {column: text}}
OVERRIDE = {}
# earlier note text proven wrong -> replacement
NOTE_FIX = {
    "trust law is Ley 21/2017;": "fideicomiso law is Ley 1/1984 as amended by Ley 21/2017 (trustee regulation);",
}

with open(PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    rows = list(reader)
by_name = {r["Country"]: r for r in rows}


def first_sentence(text, limit=240):
    s = re.split(r"(?<=[.;])\s", text.strip(), maxsplit=1)[0]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


changed = 0
items = []
for fp in sorted(glob.glob("verify-rest-out/followup_*.json")):
    with open(fp, encoding="utf-8") as f:
        items.extend(json.load(f))

for it in items:
    r = by_name[it["country"]]
    if it["verdict"] == "corrected" and it["id"] not in SKIP:
        edits = dict(it.get("cell_edits") or {})
        edits.update(OVERRIDE.get(it["id"], {}))
        for col, val in edits.items():
            if col not in cols or col in ("Notes", "Sources", "Country"):
                raise SystemExit(f"{it['id']}: bad column {col!r}")
            if r[col] != val:
                r[col] = val
                changed += 1
    if it["verdict"] in ("confirmed", "corrected"):
        note = f"verify-followup 2026-10 ({it['verdict']}): {first_sentence(it['finding'])}"
        if note not in r["Notes"]:
            r["Notes"] = f"{r['Notes']} | {note}" if r["Notes"] else note
            changed += 1
        for src in re.split(r"\s*;\s+", it.get("source", "")):
            if src.startswith("http") and src not in r["Sources"]:
                r["Sources"] = f"{r['Sources']}; {src}" if r["Sources"] else src
                changed += 1

for r in rows:
    for old, new in NOTE_FIX.items():
        if old in r["Notes"]:
            r["Notes"] = r["Notes"].replace(old, new)
            changed += 1

with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

print(f"{len(items)} follow-up items, {changed} cells changed")
