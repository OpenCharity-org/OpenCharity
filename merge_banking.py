#!/usr/bin/env python3
"""Merge research/banking/batch_*.json into banking_by_country.csv.

One row per jurisdiction in charities_by_country_v2.csv: can a NON-RESIDENT foreign
individual (Australian resident, no local visa/address) open a PERSONAL bank account?
Validates enums, non-empty text and http sources; fails if any country is missing,
unknown or duplicated. Schema: research/banking/SCHEMA.md.
"""
import csv
import json
import sys
from pathlib import Path

BASE = Path(__file__).parent
SRC = BASE / "charities_by_country_v2.csv"
IN = BASE / "research" / "banking"
OUT = BASE / "banking_by_country.csv"

ENUMS = {
    "nonresident_personal": ["yes", "limited", "no"],
    "opening_method": ["remote", "in-person", "not available"],
    "residence_required": ["no", "often", "yes"],
    "difficulty": ["easy", "medium", "hard", "very hard"],
    "confidence": ["high", "medium", "low"],
}
TEXT = ["documents", "min_deposit_fees", "banks", "restrictions", "alternatives"]
# json key -> csv column
COLS = [
    ("country", "Country"),
    ("nonresident_personal", "Non-resident personal account"),
    ("opening_method", "Opening method"),
    ("residence_required", "Local residence required"),
    ("difficulty", "Banking difficulty"),
    ("documents", "Documents required"),
    ("min_deposit_fees", "Minimum deposit & fees"),
    ("banks", "Banks accepting non-residents"),
    ("restrictions", "Restrictions"),
    ("alternatives", "Alternatives (fintech / regional)"),
    ("confidence", "Confidence"),
    ("sources", "Sources"),
]


def main():
    countries = [r["Country"] for r in csv.DictReader(open(SRC, encoding="utf-8"))]
    known = set(countries)
    got, errs = {}, []
    for f in sorted(IN.glob("batch_*.json")):
        for o in json.loads(f.read_text(encoding="utf-8")):
            c = (o.get("country") or "").strip()
            where = f"{f.name}:{c or '?'}"
            if c not in known:
                errs.append(f"{where}: unknown country")
                continue
            if c in got:
                errs.append(f"{where}: duplicate")
            for k, allowed in ENUMS.items():
                if o.get(k) not in allowed:
                    errs.append(f"{where}: {k}={o.get(k)!r}")
            for k in TEXT:
                if not str(o.get(k) or "").strip():
                    errs.append(f"{where}: empty {k}")
            src = o.get("sources") or []
            if isinstance(src, str):
                src = [s.strip() for s in src.split(";")]
            src = [s for s in src if s.startswith(("http://", "https://"))]
            if not src:
                errs.append(f"{where}: no http source")
            o["sources"] = "; ".join(src)
            got[c] = o
    missing = [c for c in countries if c not in got]
    if missing:
        errs.append(f"missing {len(missing)}: {', '.join(missing)}")
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow([col for _, col in COLS])
        for c in countries:
            o = got[c]
            w.writerow([" ".join(str(o[k]).split()) for k, _ in COLS])
    tally = {v: sum(o["nonresident_personal"] == v for o in got.values()) for v in ENUMS["nonresident_personal"]}
    print(f"wrote {OUT.name}: {len(countries)} rows; non-resident personal account {tally}")


if __name__ == "__main__":
    main()
