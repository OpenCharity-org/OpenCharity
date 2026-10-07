#!/usr/bin/env python3
"""Fold enrich-out/eNN.json payloads into the master table.

Reads:  charities_by_country.csv, enrich-out/e*.json
Writes: charities_by_country_v2.csv  (15 columns)
        (XLSX built separately by build_xlsx.py)

Enrichment schema per country:
  foreign_no_presence, local_bottleneck, fee_usd, time_to_register,
  deduction, foreign_donor_restriction, corrections, sources[], confidence
"""
import csv, json, glob, sys, os
from pathlib import Path

BASE = Path(__file__).parent
SRC = BASE / "charities_by_country.csv"
OUT = BASE / "charities_by_country_v2.csv"

NEW_COLS = [
    "Foreign founder (no local presence)",
    "Main bottleneck (remote foreign founder)",
    "Registration fee (USD)",
    "Time to register",
    "Charitable deduction regime",
    "Foreign donor / donation restrictions",
    "Confidence",
    "Sources",
]

def load_enrichment():
    """Return {country: enriched_dict}. Later files win (none expected)."""
    enrich = {}
    problems = []
    for f in sorted(glob.glob(str(BASE / "enrich-out" / "e*.json"))):
        try:
            data = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception as e:
            problems.append(f"{f}: JSON parse error: {e}")
            continue
        if not isinstance(data, list):
            problems.append(f"{f}: not a JSON array")
            continue
        for item in data:
            c = item.get("Country") or item.get("country")
            if not c:
                problems.append(f"{f}: item missing Country: {str(item)[:80]}")
                continue
            enrich[c] = item
    return enrich, problems

def main():
    rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
    enrich, problems = load_enrichment()

    print(f"base rows: {len(rows)} | enriched countries: {len(enrich)}")
    missing = [r["Country"] for r in rows if r["Country"] not in enrich]
    if missing:
        print(f"NOT YET ENRICHED ({len(missing)}): {missing}")

    out_rows = []
    for r in rows:
        e = enrich.get(r["Country"])
        new = dict(r)
        if e:
            new["Foreign founder (no local presence)"] = e.get("foreign_no_presence", "")
            new["Main bottleneck (remote foreign founder)"] = e.get("local_bottleneck", "")
            new["Registration fee (USD)"] = e.get("fee_usd", "")
            new["Time to register"] = e.get("time_to_register", "")
            new["Charitable deduction regime"] = e.get("deduction", "")
            new["Foreign donor / donation restrictions"] = e.get("foreign_donor_restriction", "")
            new["Confidence"] = e.get("confidence", "")
            new["Sources"] = "; ".join(e.get("sources", []))
            corr = e.get("corrections", "")
            if corr and corr.strip() and corr.strip().lower() != "confirm prior":
                new["Notes"] = (r["Notes"].rstrip() + " | " + corr.strip()) if r["Notes"].strip() else corr.strip()
        else:
            for c in NEW_COLS:
                new[c] = ""
        out_rows.append(new)

    header = list(rows[0].keys()) + NEW_COLS
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        w.writerows(out_rows)

    # stats
    filled = sum(1 for r in out_rows if r["Registration fee (USD)"])
    print(f"wrote {OUT}: {len(out_rows)} rows x {len(header)} cols | new cols filled: {filled}/{len(out_rows)}")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  ", p)

if __name__ == "__main__":
    main()
