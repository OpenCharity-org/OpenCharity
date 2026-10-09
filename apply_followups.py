"""Apply targeted follow-up research to the v2 CSV.

Inputs: verify-rest-out/followup_*.json, then round-2 re-verification
verify-rest-out/r2/result_*.json (later files win on the same cell).
Each item: {id, country, verdict, finding, source, cell_edits}.
Only verdict == "corrected" items have their cell_edits applied (minus SKIP).
Every confirmed/corrected item gets a short dated note and its source(s).
NOTE_FIX rewrites earlier notes that a follow-up showed to be wrong.
"""
import csv
import glob
import json
import re

PATH = "charities_by_country_v2.csv"
ENUMS = {
    "Foreign founder (no local presence)": {"yes", "partial", "no"},
    "Confidence": {"high", "med"},
    "Difficulty (AU-resident foreign founder)": {"easy", "medium", "hard", "very hard"},
}

# follow-up ids whose cell edits are rejected on review: {id: reason}
SKIP = {}
# per-cell overrides on review: {id: {column: text}}
OVERRIDE = {
    # residence permit required to found -> not possible without local presence
    "R204-11": {"Foreign founder (no local presence)": "no"},
    # MoF accepts non-citizen applications; no longer an effective bar
    "R204-4": {"Difficulty (AU-resident foreign founder)": "hard"},
}
# superseded claims left in other columns after r2: {country: {column: [(old, new)]}}
CELL_FIX = {
    "Mongolia": {"Annual compliance & reporting": [("Law on Associations (1997)", "Law on Non-Governmental Organizations (1997)")]},
    "Gambia": {
        "Foreign donor / donation restrictions": [("2022 NGO Bill pending, so 1972 Societies Act regime applies", "NGO Bill pending, so the NGO Decree No. 81 of 1996 regime applies")],
        "Notes": [("2022 NGO Bill has been in draft years without enactment, so the old 1972 Societies Act still applies", "NGO Bill has been in draft for years without enactment, so the NGO Decree No. 81 of 1996 still applies")],
    },
    "Iraq": {"Foreign donor / donation restrictions": [("with MoSAL approvals", "with approvals from the Council of Ministers NGO Department")]},
    "Ethiopia": {
        "Foreign donor / donation restrictions": [("the CSO Agency/ACSO channel", "the ACSO (Authority for Civil Society Organizations) channel")],
        "Annual compliance & reporting": [("to the CSO Agency", "to ACSO")],
    },
    "Laos": {"Notes": [("Decree 238/2017 governs associations;", "Decree 238/2017 then governed associations (since replaced by Decree 536/2025);")]},
    "Ecuador": {"Notes": [("Decreto 193/2017 governs;", "Decreto 193/2017 then governed (repealed by Decreto 191/2025);")]},
    "El Salvador": {"Notes": [("fundacion (Ley 2011)", "fundacion (D.L. 894/1996)")]},
    "Belize": {
        "Foreign donor / donation restrictions": [("need an Attorney General NGO license (Non-Governmental Organizations Act)", "must be registered as an NGO with the FSC Registrar (NGO Act Cap. 315)")],
        "Notes": [("charity status is a later AG licensing step", "NGO/NPO registration with the FSC Registrar is a later step"),
                  ("Verified: NPO status must be separately registered with the Attorney General's Ministry after incorporation", "NPO status must be separately registered (FSC Registrar) after incorporation")],
    },
    "Austria": {"Notes": [("Genehmigung), 3 founders", "Genehmigung), 2 founders")]},
    "Latvia": {"Notes": [("Real barriers: Latvian-resident board requirement plus local address and e-ID", "Real barriers: local address and e-ID (no board-residence rule in law)")]},
    "Taiwan": {"Notes": [("NT$15m (local) / NT$30m (central) minimum capital", "minimum endowment set per competent authority (e.g. Taipei social-welfare foundations NT$10m cash)")]},
    "Costa Rica": {"Notes": [("asociacion requires 5+ founders (Ley 218), not 3+", "asociacion requires 10+ founders (Ley 218 art. 18) and a 5+ member board")]},
    "Suriname": {"Notes": [("new Civil Code (in force 2013) modernized foundation law", "new Civil Code Book 2 (in force 1 May 2025) modernized foundation law"),
                           ("[verified] Stichtingenwet 1968 has no", "[verified, pre-2025 law] Stichtingenwet 1968 had no")]},
    "Uzbekistan": {"Notes": [("(simplified one-stop process, e-filing), making formation the easiest phase", "(e-filing), but Ministry of Justice registration takes a legal month, often extended")]},
    "Serbia": {"Notes": [("fees ~2,000-5,000 RSD plus docs", "APR fee RSD 6,500 plus docs")]},
    "Vanuatu": {"Notes": [("; 1+ resident director required", "; no resident-director rule in the Companies Act 2012 (registered office required)")]},
}
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
for fp in sorted(glob.glob("verify-rest-out/followup_*.json")) + sorted(
    glob.glob("verify-rest-out/r2/result_*.json")
):
    with open(fp, encoding="utf-8") as f:
        for it in json.load(f):
            it.setdefault("country", it.pop("Country", None))
            items.append(it)

for it in items:
    r = by_name[it["country"]]
    if it["verdict"] == "corrected" and it["id"] not in SKIP:
        edits = dict(it.get("cell_edits") or {})
        edits.update(OVERRIDE.get(it["id"], {}))
        for col, val in edits.items():
            if col not in cols or col in ("Notes", "Sources", "Country"):
                raise SystemExit(f"{it['id']}: bad column {col!r}")
            if col in ENUMS and val not in ENUMS[col]:
                raise SystemExit(f"{it['id']}: bad value {val!r} for {col!r}")
            if r[col] != val:
                r[col] = val
                changed += 1
    if it["verdict"] in ("confirmed", "corrected"):
        tag = "verify-r2" if it["id"].startswith("R2") else "verify-followup"
        note = f"{tag} 2026-10 ({it['verdict']}): {first_sentence(it['finding'])}"
        if note not in r["Notes"]:
            r["Notes"] = f"{r['Notes']} | {note}" if r["Notes"] else note
            changed += 1
        for src in re.split(r"\s*;\s+", it.get("source", "")):
            if src.startswith("http") and src not in r["Sources"]:
                r["Sources"] = f"{r['Sources']}; {src}" if r["Sources"] else src
                changed += 1

for country, fixes in CELL_FIX.items():
    r = by_name[country]
    for col, pairs in fixes.items():
        for old, new in pairs:
            if old in r[col]:
                r[col] = r[col].replace(old, new)
                changed += 1
            elif new not in r[col]:
                raise SystemExit(f"CELL_FIX {country}/{col}: text not found: {old!r}")

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
