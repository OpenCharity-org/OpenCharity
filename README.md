# OpenCharity — Charity Registration Atlas (202 Countries)

A fully researched, source-cited dataset on **registering a charity in every
country of the world**, written specifically for a founder residing in
Australia with no ties to the target country.

## What it covers (18 columns per country)

| # | Column | What it tells you |
|---|--------|-------------------|
| 1 | Country | Jurisdiction (202) |
| 2 | Google for Nonprofits eligible | Y/N against the authoritative 186-name GfN list |
| 3 | Main charitable entity types | The entity form to register, with the governing law |
| 4 | Difficulty (AU-resident foreign founder) | easy / medium / hard / very hard |
| 5 | Key local requirements | Seat, resident officers, ID documents, etc. |
| 6 | Est. cost & time | Realistic end-to-end cost + duration for a foreign founder |
| 7 | Notes | Law citations, verified corrections, caveats |
| 8 | Foreign founder (no local presence) | yes / partial / no — can you do it fully remotely |
| 9 | Main bottleneck (remote foreign founder) | The single thing that blocks or slows you |
| 10 | Registration fee (USD) | Official fee approximation |
| 11 | Time to register | Realistic duration |
| 12 | Charitable deduction regime | Local donor-deduction regime |
| 13 | Foreign donor / donation restrictions | FCRA-style limits on inbound foreign funding |
| 14 | Annual compliance & reporting | Ongoing filings, audit duties, consequences of non-filing |
| 15 | Tax-exempt status & benefits | Pathway to tax-exempt/recognized status + benefits |
| 16 | Bank account (remote feasibility) | Online / local visit / local agent / blocked (KYC & AML constraints) |
| 17 | Confidence | high / med / low (all 202 rows reached high/med) |
| 18 | Sources | URLs of the laws, gazettes and registry pages used |

## Deliverables

- **`charities_by_country_v2.csv`** — the master dataset (202 × 18).
- **`charities_by_country_v2.xlsx`** — styled workbook: Master (heat-mapped
  difficulty, GfN highlights, filters, frozen header), Top-10 Shortlist
  (score-ranked easiest full-remote jurisdictions), Regional Summary,
  Methodology.
- **`webapp/index.html`** — a zero-dependency, single-file interactive app
  (works from `file://` — all data is embedded). Search, filter by
  difficulty / GfN / no-presence feasibility / region, sort, and open a
  full dossier drawer for any country. To serve it:
  `python3 -m http.server 8734 --directory webapp`.
- **Live site:** https://opencharity-org.github.io/OpenCharity/ (GitHub Pages,
  served from `docs/index.html`, which `build_atlas.py` writes).
- **`webapp/atlas.html`** — world-map atlas: every country coloured by
  difficulty (or remote founding / GfN / confidence), click for the full
  dossier, plus a searchable list. Built by `python3 build_atlas.py` from the
  CSV and `webapp/geo/countries-50m.json` (Natural Earth via world-atlas@2.0.2).

## Current Top-10 (score-ranked, full-remote friendly)

Australia, Czechia, Estonia, Kyrgyzstan, Netherlands, Poland, Seychelles,
South Africa, United Kingdom, United States.

## How it was built

1. **Pass 1** — 16 regional subagent batches researched all 198 jurisdictions.
2. **Pass 2** — 32 enrichment agents re-verified against official registries
   and NGO-law texts (entity types, fees, times, presence feasibility,
   deduction regimes, donor restrictions).
3. **Pass 2b** — 141 gap-filler deep-dives on the weakest rows; every
   low-confidence country was re-researched with primary sources (e.g.
   São Tomé & Principe Lei 8/2012, Mauritania law 2021-004). Result: **zero
   low-confidence rows remain**.
4. **Pass 3** — 10 agents added the annual-compliance dimension.
5. **Pass 4** — 10 agents added the tax-exemption dimension.
6. **Pass 5** — 10 agents added bank-account remote-feasibility (KYC/AML
   constraints for foreign founders).
7. **Verification passes** — citation check of every entity-type law (51
   fixes), dead-link replacement, fee/time normalisation, and a full
   198-row re-verification of law currency, fee, time and presence claims
   against official sources (131 rows corrected; see `verify-rest-out/` and
   `verify_rest_patches.py`, applied with `python3 apply_verify_rest.py`).
8. **Round-2 re-verification** — the 113 medium-confidence rows re-checked in
   10 batches (`verify-rest-out/r2/`): 56 corrected, 53 confirmed, 4
   unverifiable; plus targeted follow-ups (`verify-rest-out/followup_*.json`)
   and a sweep of superseded claims in other columns. Applied with
   `python3 apply_followups.py` (idempotent).
9. **Coverage completion** — Palau, Kosovo and Cabo Verde (the three
   sovereign states missing from the map) and Greenland researched from primary sources
   and added via `python3 add_countries.py` from `research/new_countries/`.
   Greenland was added as its own entry (self-governing, with its own
   legislature and tax system). Every sovereign state on the map now has a
   row; remaining grey shapes are dependent territories (Puerto Rico, Faroe
   Islands, etc.) that register under their parent country's law.

GfN eligibility is computed by exact longest-match tokenization against the
186-name authoritative Google for Nonprofits program list (185 of 202
qualify; the 17 that do not: Belarus, China, Cuba, Georgia, Greenland, Iran,
Kosovo, Liechtenstein, Myanmar, Nepal, North Korea, Russia, Somaliland,
South Sudan, Sudan, Syria, Western Sahara).

## Reproducing / extending

```
python3 merge.py            # regenerate v1 from workflow-result.json
python3 merge_enrich.py     # fold enrich-out/*.json into v2
python3 build_xlsx.py       # build the styled workbook
python3 build_webapp.py     # rebuild webapp/index.html from the CSV
python3 add_countries.py    # merge research/new_countries/*.json rows
python3 apply_followups.py  # apply follow-up + round-2 verification results
python3 build_atlas.py      # rebuild webapp/atlas.html (world map)
```

The `enrich*-out/` directories contain the raw per-agent JSON payloads used
to build v2; `research/`, `raw/` and the country-specific research folders
hold the underlying source material.

## Disclaimer

Fees and times are official-fee approximations; remote registration
typically adds professional costs of 1–3×. Verify against the cited sources
before committing. **Not legal advice.**

## License

MIT (data: CC BY 4.0 where sources are licensed that way). See `LICENSE`.
