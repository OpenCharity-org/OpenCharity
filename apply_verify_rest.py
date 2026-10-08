"""Apply verify_rest_patches.P to charities_by_country_v2.csv in place."""
import csv

from verify_rest_patches import P

PATH = "charities_by_country_v2.csv"

with open(PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    cols = reader.fieldnames
    rows = list(reader)

by_name = {r["Country"]: r for r in rows}
missing = [c for c in P if c not in by_name]
if missing:
    raise SystemExit(f"unknown countries: {missing}")

changed = 0
for country, patch in P.items():
    r = by_name[country]
    for col, val in patch.items():
        if col == "_drop":
            # remove superseded " | "-separated Notes segments containing any of these substrings
            segs = r["Notes"].split(" | ")
            kept = [s for s in segs if s.startswith("verify-rest") or not any(sub in s for sub in val)]
            if len(kept) != len(segs):
                r["Notes"] = " | ".join(kept)
                changed += 1
        elif col == "_prose":
            # corrected rewrite of a dropped lead note, placed first
            if val not in r["Notes"]:
                r["Notes"] = f"{val} | {r['Notes']}" if r["Notes"] else val
                changed += 1
        elif col == "_note":
            if val not in r["Notes"]:
                r["Notes"] = f"{r['Notes']} | {val}" if r["Notes"] else val
                changed += 1
        elif col == "_source":
            if val not in r["Sources"]:
                r["Sources"] = f"{r['Sources']}; {val}" if r["Sources"] else val
                changed += 1
        else:
            if col not in cols:
                raise SystemExit(f"{country}: unknown column {col!r}")
            if r[col] != val:
                r[col] = val
                changed += 1

with open(PATH, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)

print(f"{len(P)} countries patched, {changed} cells changed")
