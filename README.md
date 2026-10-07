# OpenCharity — Charity Registration Atlas (198 Countries)

A fully researched, source-cited dataset on **registering a charity in every
country of the world**, written specifically for a founder residing in
Australia with no ties to the target country.

## What it covers (17 columns per country)

| # | Column | What it tells you |
|---|--------|-------------------|
| 1 | Country | Jurisdiction (198) |
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
| 16 | Confidence | high / med / low (all 198 rows reached high/med) |
| 17 | Sources | URLs of the laws, gazettes and registry pages used |

## Deliverables

- **`charities_by_country_v2.csv`** — the master dataset (198 × 17).
- **`charities_by_country_v2.xlsx`** — styled workbook: Master (heat-mapped
  difficulty, GfN highlights, filters, frozen header), Top-10 Shortlist
  (score-ranked easiest full-remote jurisdictions), Regional Summary,
  Methodology.
- **`webapp/index.html`** — a zero-dependency, single-file interactive app
  (works from `file://` — all data is embedded). Search, filter by
  difficulty / GfN / no-presence feasibility / region, sort, and open a
  full dossier drawer for any country. To serve it:
  `python3 -m http.server 8734 --directory webapp`.

## Current Top-10 (score-ranked, full-remote friendly)

Czechia, Estonia, Kyrgyzstan, Netherlands, Poland, Seychelles, South Africa,
United Kingdom, United States, Belize.

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

GfN eligibility is computed by exact longest-match tokenization against the
186-name authoritative Google for Nonprofits program list (183 of 198
qualify; the 15 that do not: Belarus, China, Cuba, Georgia, Iran,
Liechtenstein, Myanmar, Nepal, North Korea, Russia, Somaliland, South Sudan,
Sudan, Syria, Western Sahara).

## Reproducing / extending

```
python3 merge.py            # regenerate v1 from workflow-result.json
python3 merge_enrich.py     # fold enrich-out/*.json into v2
python3 build_xlsx.py       # build the styled workbook
python3 build_webapp.py     # rebuild webapp/index.html from the CSV
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
