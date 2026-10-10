# Foreigner bank-account research — one JSON object per country

Perspective: a NON-RESIDENT foreign individual (e.g. an Australian resident, no local visa,
residence permit, address or employment) wanting to open a PERSONAL bank account in the country.
As of 2026. Banks only (licensed local banks); fintech/EMI options go in "alternatives".

{
  "country": "<exact name as given>",
  "nonresident_personal": "yes" | "limited" | "no",
      // yes = several mainstream banks routinely open accounts for non-residents
      // limited = only a few banks / premium or private-banking tiers / big deposit / case-by-case
      // no = effectively requires local residence/permit, or banking closed to foreigners
  "opening_method": "remote" | "in-person" | "not available",
      // remote = at least one bank opens non-resident accounts without a visit (online/video/courier/embassy)
  "residence_required": "no" | "often" | "yes",
  "difficulty": "easy" | "medium" | "hard" | "very hard",
  "documents": "<passport, proof of foreign address, reference letter, TIN, local address/phone, visa, etc.>",
  "min_deposit_fees": "<typical minimum opening deposit / monthly fees for non-residents, with currency; 'not published' if unknown>",
  "banks": "<named banks known to accept non-residents, or 'none known'>",
  "restrictions": "<sanctions, capital/currency controls, FATCA/CRS, USD access, de-risking, account types limited to e.g. foreign-currency only>",
  "alternatives": "<fintech/EMI or regional options, e.g. Wise local details, Revolut, mobile money; 'none' if none>",
  "confidence": "high" | "medium" | "low",
  "sources": ["https://...", "..."]   // 1-4 URLs actually consulted, prefer bank or regulator pages
}

## Cost fields (pass 2, added to every object)

  "opening_fee_usd": <number or null>,   // one-off fee to open a basic personal account as a non-resident (0 if free)
  "min_deposit_usd": <number or null>,   // minimum opening deposit / balance required (your money, not a fee; 0 if none)
  "monthly_fee_usd": <number or null>,   // typical monthly maintenance fee for that account (0 if free / waived by default)
  "cost_note": "<one sentence: which bank/account the figures are for, the original local-currency amounts, and the FX rate used>"

Figures are for the cheapest realistic non-resident option at a bank named in "banks". Convert to USD at
approximate Oct-2026 rates and round sensibly. null = genuinely not published (say so in cost_note). Where
non-residents cannot open accounts at all ("no" / "not available"), use null for all three and explain in cost_note.
