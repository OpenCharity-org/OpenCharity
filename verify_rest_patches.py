"""Cell-level corrections from the verify-rest pass (verify-rest-out/v*.json).

Each entry: Country -> {column: new_value}. A special key "_note" is appended
to the Notes column; "_source" is appended to Sources if not already present.
Apply with: python3 apply_verify_rest.py
"""

P = {}

# ---- batch v1 ----
P["Canada"] = {
    "Est. cost & time": "C$300 (C$200 incorporation + C$100 charity registration); incorporation 2–4 weeks, CRA charity registration ~6–9 months (service standard: decision within 9 months of a complete application)",
    "Time to register": "6-10 months (incorporation 2-4 weeks; CRA charity registration ~6-9 months)",
    "_note": "verify-rest 2026-10: CRA processing corrected to the 2025-26 service standard (decision within 9 months)",
    "_source": "https://canada.ca/en/revenue-agency/services/charities-giving/charities/about-charities-directorate/report-on-charities-program/report-on-charities-program-2025-2026.html",
}
P["Trinidad & Tobago"] = {
    "Main charitable entity types": "Company limited by guarantee (Companies Act Chap. 81:01, Companies Registry); NPO registration under the Non-Profit Organisations Act 2019 (Act No. 7 of 2019); charitable/tax-exempt status by Ministry of Finance approval under the Income Tax Act Chap. 75:01.",
    "_note": "verify-rest 2026-10: law refs corrected (Companies Act Chap. 81:01, Income Tax Act Chap. 75:01; no 'Charities Act' — NPO Act 2019 registration applies)",
    "_source": "https://fiu.gov.tt/wp-content/uploads/Non-Profit-Organisations-Act-2019.pdf",
}
P["St. Lucia"] = {
    "Main charitable entity types": "Company limited by guarantee (Companies Act, Chapter 13.01 (1996), Commercial Registry Agency); domestic company; charitable status via Inland Revenue. (IBCs exist under the International Business Companies Act Cap. 12.14, but are not a charity vehicle.)",
    "_note": "verify-rest 2026-10: removed claim that IBCs are prohibited — IBC Act Cap. 12.14 remains in force (IBCs resident/taxable regime since 1 July 2021)",
    "_source": "https://saintluciaifc.com/legislative-update-july-2021",
}
P["Solomon Islands"] = {
    "Foreign founder (no local presence)": "partial",
    "Registration fee (USD)": "~$180 (SBD 1,500 incorporation)",
    "_note": "verify-rest 2026-10: foreign founders can incorporate via a local agent/resident secretary (SBD 1,500 fee, Company Haus) — presence downgraded no->partial",
    "_source": "https://www.investsolomons.gov.sb/step-by-step-guide-to-starting-a-business/step-2-incorporate-the-enterprise-with-company-haus",
}
P["Kiribati"] = {
    "Foreign founder (no local presence)": "partial",
    "_note": "verify-rest 2026-10: Companies Act 2021 replaced the 1979 Ordinance; at least one Kiribati-resident director is required, so a foreign founder can proceed via a local director (no->partial)",
    "_source": "https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/113886/KIR113886.pdf",
}
P["Tuvalu"] = {
    "Foreign founder (no local presence)": "partial",
    "Key local requirements": "Ministry of Finance accepts registrations from non-citizens/foreign-based businesses on application (business@gov.tv); local officers and office strongly advisable",
    "_note": "verify-rest 2026-10: Ministry of Finance states non-citizens/foreign-based businesses may register after contacting business@gov.tv (no->partial)",
    "_source": "https://finance.gov.tv/business",
}

# ---- batch v4 ----
P["Georgia"] = {
    "Est. cost & time": "State registration fee GEL 100 standard (~$37; faster tiers cost more); online filing at the National Agency of Public Registry, 1-10 days to certificate.",
    "Registration fee (USD)": "~$37 (GEL 100 standard registration)",
    "_note": "verify-rest 2026-10: NAPR non-entrepreneurial legal entity fee corrected to GEL 100",
    "_source": "https://legalese.ge/services/ngo-registration-in-georgia",
}
P["Azerbaijan"] = {
    "Est. cost & time": "State duty nominal (a few manat, ~$5-15), but real-world Ministry of Justice processing 1–3+ months with high rejection risk",
    "Registration fee (USD)": "~$5-15 (nominal state duty)",
    "_note": "verify-rest 2026-10: state duty for NGO registration is nominal (~USD 7 per GPEI), not ~USD 150",
}
P["Kazakhstan"] = {
    "Key local requirements": "Foreign citizens may found foundations (public associations are restricted to citizens/residents); a local registered address in Kazakhstan is required; filings in Kazakh (Russian accepted in practice).",
    "Est. cost & time": "State fee 6.5 MCI (~$50-60) for NPO registration; 5–10 business days via single-window registration",
    "Registration fee (USD)": "~$55 (6.5 MCI state fee)",
    "_note": "verify-rest 2026-10: NPO registration fee is 6.5 MCI; foreign founders realistic only via a foundation (public associations closed to foreigners)",
    "_source": "https://www.icnl.org/resources/civic-freedom-monitor/kazakhstan",
}
P["Cameroon"] = {
    "Main charitable entity types": "Association (Law 90/053 of 19 Dec 1990, amended by Laws 2020/009 and 2021/022) and ONG (Law 99/014 of 22 Dec 1999); ONGs need accreditation ('agrément') from the Interior Ministry.",
    "Est. cost & time": "Association declaration at the prefecture is free (legalisation/stamp costs a few thousand FCFA, ~$5-20); ONG accreditation is a discretionary Interior Ministry process of several months.",
    "Registration fee (USD)": "~$5-20 (declaration free; stamps/legalisation only)",
    "_note": "verify-rest 2026-10: no 2017 civil-society law exists — Law 90/053 amended by 2020/009 and 2021/022; declaration fee overstated",
}

# ---- batch v10 ----
P["Bhutan"] = {
    "Main charitable entity types": "Public Benefit Organization or Mutual Benefit Organization under the Civil Society Organizations Act of Bhutan 2007 (amended 2022), registered with the Civil Society Organizations Authority (CSOA); limited company (Companies Act 2016)",
    "Time to register": "6 weeks-6 months (CSOA may take up to 6 months to decide), if a local sponsor is secured",
    "_note": "verify-rest 2026-10: no 'NGO Act 2001' — CSOs are governed by the CSO Act 2007 (am. 2022) and registered by the CSOA",
    "_source": "https://www.icnl.org/wp-content/uploads/Bhutan_Civil-Society-Org-Act.pdf",
}
P["Afghanistan"] = {
    "Main charitable entity types": "Domestic NGO or registered foreign organisation under the de facto authorities' NGO procedure, administered by the Ministry of Economy (NGO Directorate)",
    "Key local requirements": "Registration, supervision and coordination of domestic and foreign NGOs by the de facto Ministry of Economy (NGO Directorate, ngo.gov.af); local office; effective operation requires local partners and security access.",
    "_note": "verify-rest 2026-10: registering body is the Ministry of Economy NGO Directorate (not an MFA committee); 2005 law/'Hezb and Foundations Act' references removed",
    "_source": "https://ngo.gov.af/en/?p=83",
}
P["Maldives"] = {
    "Main charitable entity types": "Association under the Associations Act (Law No. 3/2022, replacing the 2003 Act), registered with the Registrar of Associations; charitable/tax-exempt approval by MIRA under the Income Tax Act (Law 25/2019); private company (Companies Act, Law 7/2023)",
    "Key local requirements": "Association registration with the Registrar of Associations (decision within 30 days or deemed registered); MIRA (Maldives Inland Revenue Authority) grants charitable tax-exempt approval; practical need for resident local office-bearers and a Maldivian address.",
    "_note": "verify-rest 2026-10: Associations Act 3/2022 now governs; MIRA = Maldives Inland Revenue Authority (tax approval, not trust registration)",
    "_source": "https://www.ctlstrategies.com/latest/associations-act/",
}
P["Nigeria"] = {
    "Main charitable entity types": "Incorporated trustees (Companies and Allied Matters Act 2020, Part F ss. 823-850, CAC); company limited by guarantee (CAC); trust (deed, unregistered)",
    "Key local requirements": "CAC registration (incorporated trustees or CLG) with a Nigerian address, then mandatory free SCUML (EFCC) registration before banking; international NGOs also register with the National Planning Commission.",
    "Est. cost & time": "NGN 150,000-300,000 (~US$100-200) official fees; US$3k-8k all-in with agents; 3-9 months end-to-end incl. CAC and SCUML",
    "_note": "verify-rest 2026-10: 'NCMM' and 'Operational Readiness Certificate' layers unverifiable — replaced by SCUML + NPC; Foreign Aid Regulation Bill 2026 (SB.1034) is pending, not law",
    "_source": "https://www.efcc.gov.ng/news-and-information/news-release/9201-scuml-registration-is-free-efcc-2",
}
P["Ghana"] = {
    "Main charitable entity types": "Company limited by guarantee under Companies Act 2019 (Act 992) at ORC, then NPO licence from the NPO Secretariat (Ministry of Gender, Children and Social Protection) under the NPOs Policy/Directive 2020.",
    "Key local requirements": "Charitable/non-profit objects; NPO Secretariat licence (no Charities Act or Charities Commission exists — the NPO Bill is still pending); Ghana-located principal office (directors may be foreign)",
    "_note": "verify-rest 2026-10: there is no Ghana Charities Commission/Charities Act — licensing is by the NPO Secretariat; NPO Bill still pending",
    "_source": "https://npos.mogcsp.gov.gh/registration-and-licensing/",
}
P["Côte d'Ivoire"] = {
    "Key local requirements": "Declaration and inscription in the public register of OSCs under Ordonnance n° 2024-368 of 12 June 2024 (ratified by Parliament 2025); local office; foreign-funded NGOs also need Ministry of the Interior authorization",
    "_note": "verify-rest 2026-10: stale 'Law 2022-443' reference removed; Ordonnance 2024-368 ratified by National Assembly (Mar 2025) and Senate (Apr 2025)",
}
P["Benin"] = {
    "Key local requirements": "Online declaration via service-public.bj into the Registre des Associations et des Fondations (Loi n° 2025-19 of 22 July 2025; Décret 2025-575, effective 19 Dec 2025); local registered office; no local-national officer requirement",
    "Time to register": "2-10 weeks (receipt may take up to 60 days)",
    "_note": "verify-rest 2026-10: stale 'Law 2015-04' reference removed; declaration is now exclusively online under Décret 2025-575",
    "_source": "https://beninwebtv.bj/en/benin-the-register-of-associations-and-foundations-takes-effect-on-december-19/",
}
P["Togo"] = {
    "Key local requirements": "Declaration of an association at the Ministry of Territorial Administration (1901-law model); foreign NGOs need formal recognition of NGO status before signing partnership agreements (circular of 7 Oct 2024); local registered office; French-language documents",
    "_note": "verify-rest 2026-10: unverifiable 'Law 2000-17' removed; Oct 2024 circular requires foreign NGOs to obtain recognition (6-month regularisation window)",
    "_source": "https://fr.apanews.net/news/togo-nouvelles-regles-pour-les-ong-etrangeres/",
}
P["Burkina Faso"] = {
    "Main charitable entity types": "Association under Loi n° 011-2025/ALT of 17 July 2025 on freedom of association (replacing Loi 064-2015/CNT); ONGs need ministry approval and an accord-cadre with the state.",
    "Key local requirements": "Registration under Loi 011-2025/ALT with heavy state oversight; local office and resident leadership; in Apr 2026 the government dissolved 118 organisations and suspended 1,056 under the new law",
    "_note": "verify-rest 2026-10: Loi 064-2015 replaced by Loi 011-2025/ALT; unsupported '2018 constitutional amendment' claim removed",
    "_source": "https://www.icnl.org/resources/civic-freedom-monitor/burkina-faso",
}
P["Mali"] = {
    "Key local requirements": "Prior authorization and declaration under Loi n° 04-038 of 5 Aug 2004 as amended by Ordonnance 2024-008 (Mar 2024); local office; French-language filings",
    "_note": "verify-rest 2026-10: repealed Law 2001-019 reference removed",
}
P["Guinea"] = {
    "Key local requirements": "Declaration of an association under Loi L/2005/013/AN with the MATD; local registered office in Conakry; French-language documents",
    "Time to register": "4-10 weeks when approvals are open; MATD suspended agréments for 4 months in Sept 2024 and issuance has been irregular since",
    "_note": "verify-rest 2026-10: 'Law L/2010/004' removed; Sept 2024 suspension of NGO agréments noted",
    "_source": "https://guineenews.org/2024/09/02/guinee-le-gouvernement-suspend-la-delivrance-des-agrements-aux-ongs-et-mouvements-associatifs-decision/",
}
P["Guinea-Bissau"] = {
    "Key local requirements": "Notarial public deed under the Código Civil (10+ founders) plus registry at the Conservatória; local office; Portuguese-language filings",
    "_note": "verify-rest 2026-10: misattributed 'Lei 5/VI/96' (Cape Verde numbering) and Guinea-Conakry 'L/005/013/AN' references removed",
}
P["Senegal"] = {
    "Main charitable entity types": "Association under the Code des obligations civiles et commerciales arts. 811 ff. (Loi 68-08 of 26 Mar 1968, am. Loi 79-02) and Décret 76-040 of 16 Jan 1976 (declaration + récépissé); ONG under décret n° 96-103 du 8 février 1996 as modified by décret n° 2010-1490 du 10 novembre 2010.",
    "Key local requirements": "Declaration to the administrative authority (Ministry of Interior/préfecture), refusable only on legality grounds (COCC art. 812); local registered office; French-language documents",
    "_note": "verify-rest 2026-10: 'Loi 71-604' is not the associations law — COCC arts. 811 ff. + Décret 76-040 govern",
    "_source": "https://www.sports.gouv.sn/wp-content/uploads/2022/02/DECLARATION-ET-ENREGISTREMENT-DES-ASSOCIATIONS-SPORTIVES.pdf",
}
P["Gambia"] = {
    "Main charitable entity types": "Company limited by guarantee or registered association with the Registrar of Companies (Companies Act 2013); NGOs need clearance from the NGO Affairs Agency created by NGO Decree No. 81 of 1996; TIN certificate required.",
    "Key local requirements": "NGO Affairs Agency clearance certificate before incorporation; registration with the Registrar of Companies under the Companies Act 2013; local office; English-language filings",
    "_note": "verify-rest 2026-10: NGO Decree is No. 81 of 1996 (not 1993); Companies Act 2013 replaced the 1955 Act",
    "_source": "https://www.icnl.org/research/library/gambia_ngodec",
}
P["Sierra Leone"] = {
    "Registration fee (USD)": "~$20+ CAC fee plus ~$500 NGO registration (annual renewal); ~$800-2k all-in w/ agent",
    "Key local requirements": "Non-profit company limited by guarantee at the CAC, then annual NGO registration with the Ministry of Planning & Economic Development under the NGO Regulations (~US$500 + SLANGO membership); local registered office; English-language documents",
    "_note": "verify-rest 2026-10: Companies Act is 2009 (Act No. 5, am. 2014), not 2013; separate NGO registration (~US$500/yr) added",
    "_source": "https://www.jica.go.jp/sierraleone/office/others/ngo.html",
}
P["Liberia"] = {
    "Key local requirements": "Incorporation at the Liberia Business Registry, MFA endorsement, then accreditation under the National Aid & NGO Policy by the MFDP NGO Unit (online since Aug 2022); local principal officer and office",
    "Registration fee (USD)": "US$150 local / US$350 international accreditation (+ US$50/100 annual); ~$500-2k total with agent",
    "Est. cost & time": "Government incorporation fee ~US$50-550 (provider quotes); NGO accreditation US$150 (local) or US$350 (international), annual fee US$50/100; official time unpublished.",
    "_note": "verify-rest 2026-10: unverifiable 'NGO Act 2015' removed — accreditation is under the National Aid & NGO Policy (MFDP NGO Unit)",
    "_source": "https://www.mfdp.gov.lr/index.php/budget-planning/assistant-min-regional-sectoral/ngo-unit",
}
P["Niger"] = {
    "Key local requirements": "Declaration and prior authorization under Ordonnance 84-06 of 1 Mar 1984 (am. Ord. 84-50, Loi 91-006); local registered office; French-language filings; ~2,900 NGOs/associations suspended in 2025 and many dissolved by arrêté of 7 Jan 2026 (~1,809 remain authorised)",
    "_note": "verify-rest 2026-10: unverifiable 'Law 93-010' removed; 2025-26 crackdown added",
    "_source": "https://www.icnl.org/resources/library/ordonnance-no-84-06-portant-regime-des-associations",
}

# ---- batch v2 ----
P["Honduras"] = {
    "Main charitable entity types": "Fundación or asociación con personalidad jurídica (Ley Especial de Fomento para las ONGD, Decreto 32-2011), granted by the Secretaría de Gobernación, Justicia y Descentralización (SGJD) through DIRRSAC.",
    "Key local requirements": "Spanish articles, local registered office, SGJD/DIRRSAC registry filing for associations and ONGDs.",
    "_note": "verify-rest 2026-10: granting body is SGJD/DIRRSAC (not the Judiciary/Chancillería)",
    "_source": "https://www.sgjd.gob.hn/institucion/dependencias/subsecretaria-de-justicia/direccion-de-regulacion-registro-y-seguimiento-de-asociaciones-civiles-dirrsac",
}
P["Nicaragua"] = {
    "Main charitable entity types": "Asociación or fundación under Ley 1115 (Ley General de Regulación y Control de Organismos sin Fines de Lucro, 2022; reformed by Ley 1127/2022 and Ley 1212/2024), registered with the Ministerio de Gobernación; fideicomiso (Ley 741/2010).",
    "Key local requirements": "Spanish articles, local address, registration with the Ministerio de Gobernación (Dirección General de Registro y Control de OSFL), which now grants and cancels legal status directly; Ley 1040/2020 (Agentes Extranjeros) applies to foreign-funded entities.",
    "_note": "verify-rest 2026-10: Ley 1115 (2022, reformed 2022/2024) is now the controlling law; legal personality granted by Gobernación, not the National Assembly",
    "_source": "https://www.ey.com/es_ce/technical/tax/tax-alerts/nicaragua-entran-en-vigencia-reformas-al-marco-normativo-sobre-organismos",
}
P["Costa Rica"] = {
    "Main charitable entity types": "Asociación (Ley 218 de 1939); fundación (Ley de Fundaciones No. 5338 de 1973); fideicomiso — inscription at the Registro de Personas Jurídicas (Registro Nacional).",
    "Key local requirements": "Notarized Spanish articles, local registered office, Registro de Personas Jurídicas; 3+ members for an asociación; a fundación's Junta Administrativa must include one member appointed by the Executive and one by the cantonal municipality.",
    "_note": "verify-rest 2026-10: foundations governed by Ley 5338; registry is the Registro de Personas Jurídicas (not commercial registry/Education Ministry)",
    "_source": "https://costa-rica.justia.com/nacionales/leyes/ley-5338/gdoc",
}
P["Panama"] = {
    "Main charitable entity types": "Fundación de interés privado (Ley 25/1995; min endowment US$10,000); asociación sin fines de lucro (personería jurídica from the Ministerio de Gobierno); fideicomiso (Ley 21 of 10 May 2017, replacing Ley 1/1984).",
    "Registration fee (USD)": "~$400 (registry + government fees)",
    "_note": "verify-rest 2026-10: trust law is Ley 21/2017; FIP needs a Panamanian resident agent and a council of 3 natural persons or 1 legal entity",
}
P["Colombia"] = {
    "Main charitable entity types": "Fundación, asociación or corporación (personas jurídicas sin ánimo de lucro, Código Civil arts. 633-652) — registro ante Cámara de Comercio under Decreto 2150/1995 arts. 40-45 and Decreto 427/1996.",
    "Key local requirements": "No nationality requirement for board; Colombian registered address; constitution by private document with recognized signatures (public deed not required) registered at the Cámara de Comercio; filings in Spanish.",
    "_note": "verify-rest 2026-10: Civil Code articles corrected to 633-652; private document suffices for ESAL constitution",
    "_source": "https://www.ccb.org.co/servicios/registros-publicos/registro-de-entidades-sin-animo-de-lucro",
}
P["Venezuela"] = {
    "Main charitable entity types": "Fundación or asociación civil (Código Civil arts. 19-20), registered at the Registro Público (SAREN); subject to the Ley de Fiscalización, Regularización, Actuación y Financiamiento de las ONG y afines (2024).",
    "Key local requirements": "Local (Venezuelan) resident officers and registered office, Venezuelan lawyer, notarized deed; 2024 NGO law requires SAREN registration, declaration of foreign funding and donor identification, with dissolution powers; severe exchange and banking restrictions.",
    "_note": "verify-rest 2026-10: no 'Ley Orgánica de Fundaciones' — Civil Code arts. 19-20 govern; 2024 NGO oversight law added; CADIVI (abolished 2014) reference removed",
    "_source": "https://www.prensa-latina.cu/2024/08/15/sancionan-en-venezuela-ley-sobre-regularizacion-y-actuacion-de-ong/",
}
P["Ecuador"] = {
    "Main charitable entity types": "Fundación (1+ founders) or corporación (5+ members) under Decreto Ejecutivo 193/2017 (Reglamento para el Otorgamiento de Personalidad Jurídica a las Organizaciones Sociales), registered in SUIOS via the competent ministry",
    "Key local requirements": "Ecuadorian address and legal representative; Ecuadorian lawyer; registration in SUIOS with the competent ministry; ongoing reporting to the supervising ministry.",
    "Registration fee (USD)": "$0 government fee (lawyer/notary costs ~$150-400)",
    "_note": "verify-rest 2026-10: Decreto 193/2017 governs; unverifiable 'Ley 2023-13/COEP' removed; ministerial grant carries no government fee",
    "_source": "https://www.gob.ec/regulaciones/193-expidese-reglamento-otorgamiento-personalidad-juridica-organizaciones-sociales",
}
P["Peru"] = {
    "Main charitable entity types": "Asociación (Código Civil arts. 80-98), fundación (arts. 99-110) or comité (arts. 111-123) — registro en SUNARP; fundaciones also register with the Consejo de Supervigilancia de Fundaciones (Ministerio de Justicia).",
    "Registration fee (USD)": "~$20-60 SUNARP fees; ~$300-800 incl. notary/lawyer",
    "_note": "verify-rest 2026-10: Civil Code article numbers corrected; SUNARP fee is modest — the larger figure is notary/lawyer cost",
    "_source": "https://www.gob.pe/institucion/sunarp",
}
P["Bolivia"] = {
    "Main charitable entity types": "Fundación, ONG or entidad civil sin fines de lucro (Ley 351/2013 and DS 1597/2013) — personalidad jurídica from the Ministerio de la Presidencia (multi-department) or departmental Gobernación; cooperativa (Ley 356/2013).",
    "Key local requirements": "Resident (Bolivian) officers, local address, notarized deed; foreign-constituted NGOs must sign a framework cooperation agreement with the Ministerio de Relaciones Exteriores (Ley 351 art. 13); Spanish only.",
    "_note": "verify-rest 2026-10: registering authority corrected (not a 'Superintendencia de Compañías'); unverifiable 'Ley 1417/1475' references removed",
    "_source": "https://va.presidencia.gob.bo/images/personalidadesJuridicas/Normativa/1-ley-351_de_otorgacion_de_personalidades_jurdicas.pdf",
}
P["Paraguay"] = {
    "Main charitable entity types": "Asociación civil y fundación (Código Civil, Ley 1183/1985); cooperativa (Ley 438/94) — plus mandatory National Registry of Non-Profit Organizations (MEF) under Ley 7363/2024 and Decreto 4806/2025; Registro Administrativo de Personas y Estructuras Jurídicas (Ley 6446/2019).",
    "_note": "verify-rest 2026-10: unverifiable 'Ley 5833/2017' removed; Ley 7363/2024 control/transparency regime added",
    "_source": "https://www.lanacion.com.py/politica/2024/11/15/pena-promulgo-ley-de-control-y-transparencia-de-ong/",
}
P["Uruguay"] = {
    "Main charitable entity types": "Asociación civil or fundación (Ley 17.163/1999) — legal personality recognised by the Ministerio de Educación y Cultura (MEC).",
    "Est. cost & time": "US$200–600 incl. lawyer/notary; 2–6 weeks for MEC recognition. Notary ~US$100–200; official timelines unpublished; foreigners may found.",
    "_note": "verify-rest 2026-10: recognition is by the MEC (not the DGR); Ley 17.163 also governs foundations",
    "_source": "https://www.gub.uy/ministerio-educacion-cultura/institucional/normativa/ley-n-17163-fecha-01091999-asociaciones-civiles-fundaciones",
}
P["Argentina"] = {
    "Main charitable entity types": "Asociación civil (CCyC arts. 168-192); fundación (CCyC arts. 193-224 y Ley 19.836); fideicomiso (CCyC arts. 1666-1707); cooperativa (Ley 20.337) — registro ante la IGJ (CABA) o la Dirección de Personas Jurídicas provincial.",
    "Key local requirements": "Local registered office and resident director/legal rep; foreign founder/trustees allowed; IGJ RG 1/2020 allows constitution without escritura; Spanish filings.",
    "_note": "verify-rest 2026-10: legal bases corrected to CCyC + Ley 19.836; registry is IGJ/provincial DPJ, not the commercial registry",
    "_source": "https://abogados.com.ar/sobre-la-nueva-resolucion-12020-de-la-igj-y-el-modo-de-alivianar-cargas-en-la-constitucion-de-asociaciones-civiles/25290",
}
P["Chile"] = {
    "Main charitable entity types": "Asociación/corporación or fundación (Código Civil Título XXXIII, as amended by Ley 20.500/2011) — Registro Nacional de Personas Jurídicas sin Fines de Lucro (Registro Civil).",
    "Key local requirements": "Chilean registered office; board may include foreigners; legal representative should be resident in Chile; constitutive act deposited at the Secretaría Municipal (30-day objection period, CC art. 548); Spanish filings.",
    "Est. cost & time": "US$200–500 incl. lawyer; ~1–2 months (municipal 30-day review, then Registro Civil). Foreigners may found with a Chilean representative.",
    "Time to register": "1-2 months",
    "_note": "verify-rest 2026-10: 'Ley 20.839' is not the foundations law; filing is at the Secretaría Municipal with a 30-day objection window",
    "_source": "https://iura.cl/cc/548",
}
P["Japan"] = {
    "Registration fee (USD)": "~$700+ (¥60,000 registration licence tax + ~¥50,000 notary; Specified NPO certification free)",
    "Est. cost & time": "General incorporated association: ¥60,000 registration licence tax + ~¥50,000 notary certification (~US$700+) plus office costs, about 2–4 weeks; Specified-NPO certification is free but takes 3–6 months.",
    "_note": "verify-rest 2026-10: government cost corrected to registration licence tax ¥60,000 + notary",
    "_source": "https://www.moj.go.jp/MINJI/minji06_00106.html",
}
P["South Korea"] = {
    "Key local requirements": "Foreigners may establish non-profit corporations (Civil Act arts. 32-33; permission of the competent ministry), then register at the court registry within 3 weeks; needs a local office address and Korean-language constitution; foundations face a ministry-guideline endowment (often ~KRW 100M+, no statutory minimum).",
    "_note": "verify-rest 2026-10: legal basis is Civil Act arts. 32-33 with court-registry registration; KRW 100M endowment is an administrative guideline, not statutory",
    "_source": "https://www.law.go.kr/",
}
P["China"] = {
    "Main charitable entity types": "Public-fundraising foundation (公募基金会); Non-public-fundraising foundation (非公募基金会); Social service organization (社会服务机构, formerly private non-enterprise unit) — Charity Law 2016 (am. 2023)",
    "Key local requirements": "Registration requires a Chinese supervising/competent unit (主管单位), a Chinese registered address, and minimum original funds of RMB 8M (national public-fundraising), RMB 4M (local public-fundraising) or RMB 2M (non-public) foundation; foreign individuals generally cannot directly sponsor these entities.",
    "_note": "verify-rest 2026-10: foundation minimum funds corrected per Regulations on the Management of Foundations (2004) art. 8",
}

# ---- batch v8 ----
P["Latvia"] = {
    "Main charitable entity types": "Associations (biedrības) and foundations (nodibinājumi) under the Associations and Foundations Law (adopted 30 Oct 2003, in force 1 Apr 2004), registered in the Enterprise Register via the e-portal.",
    "Key local requirements": "Latvian address and Latvian-language name/documents; e-filing via registrs.ur.gov.lv with a Latvian/EU e-signature needs no notary (paper filings need notarised signatures)",
    "Registration fee (USD)": "~$13 (EUR 11.38 state fee; 10% less online)",
    "_note": "verify-rest 2026-10: law date corrected to 2003/2004; no '2016 Nonprofit Organizations Law' exists; state fee EUR 11.38 (Cabinet Reg. 308)",
    "_source": "https://likumi.lv/ta/id/81050",
}
P["Lithuania"] = {
    "Main charitable entity types": "Association (asociacija, Law on Associations), public institution (viešoji įstaiga), charity and support foundation (labdaros ir paramos fondas)",
    "Key local requirements": "Lithuanian address, Lithuanian-language name and documents; board and min. 1–2 founders depending on form; registration via e-signature or notary with the Register of Legal Entities",
    "_note": "verify-rest 2026-10: 'NVO' is not a legal form — forms corrected",
}
P["Spain"] = {
    "Main charitable entity types": "Fundación (Ley 50/2002 state foundations, plus regional foundation laws; EUR 30,000 endowment), Asociación (Ley Orgánica 1/2002; legal personality from the founding act)",
    "_note": "verify-rest 2026-10: legal bases cited; 'unincorporated association' and 'SL/SA charitable societies' wording removed",
    "_source": "https://www.mjusticia.gob.es/en/ciudadania/registros/fundaciones-competencia/constitucion/dotacion",
}
P["Portugal"] = {
    "Main charitable entity types": "Fundação (private foundation recognised by the Presidency of the Council of Ministers under the Lei-Quadro das Fundações, Lei 24/2012) and Associação (association)",
    "Key local requirements": "Portuguese registered office and a locally-based responsible party/director; notarised foundation deed; patrimonial sufficiency presumed only above the Portaria 75/2013 threshold (reported as EUR 250,000 for national-scope foundations)",
    "_note": "verify-rest 2026-10: 'no statutory minimum endowment' corrected — Portaria 75/2013 sufficiency threshold applies; 'Instituto' is not a separate private form",
    "_source": "https://diariodarepublica.pt/dr/detalhe/portaria/75-2013-258694",
}
P["Italy"] = {
    "Key local requirements": "Italian registered office, a founder who may be foreign (no citizenship/residency requirement), and minimum patrimony of EUR 30,000 for a fondazione (EUR 15,000 for an associazione) attested by the notary for legal personality via RUNTS (CTS art. 22)",
    "Est. cost & time": "€3,000–€6,000 professional costs plus the €30,000 foundation patrimony (€15,000 for associations); ~2–4 months for notarisation and RUNTS entry",
    "Registration fee (USD)": "none (registry nominal; ~$3,300-6,600 professional fees plus EUR 30,000 foundation patrimony)",
    "_note": "verify-rest 2026-10: minimum patrimony corrected to EUR 30,000 (foundations) / 15,000 (associations) per D.Lgs. 117/2017 art. 22",
    "_source": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2017-07-03;117",
}
P["Israel"] = {
    "Main charitable entity types": "Amuta (non-profit association, 2+ founders, Amutot Law 5740-1980) registered with the Registrar of Amutot (Israeli Corporations Authority); public-benefit company (company limited by guarantee).",
    "Key local requirements": "2+ founders over 18 (Israeli citizenship NOT required), local Israeli registered address, founding declaration and bylaws; Hebrew filings (attorney commonly used)",
    "_note": "verify-rest 2026-10: Amutot Law requires only two founders",
}
P["Jordan"] = {
    "Main charitable entity types": "Registered society (jam'iyya) under the Law on Societies No. 51 of 2008 (am. Law 22/2009), National Registry of Societies at the Ministry of Social Development; charitable trust (less common)",
    "Key local requirements": "Minimum 7 founders (except closed societies), Jordanian nationals 18+; Jordanian local address; Arabic documents; foreign funding requires Council of Ministers approval; foreign founder can only be a non-board supporter",
    "_note": "verify-rest 2026-10: registry is in the Ministry of Social Development; 7-founder minimum",
    "_source": "https://www.icnl.org/post/analysis/jordanian-law-on-societies-amended",
}
P["Lebanon"] = {
    "Main charitable entity types": "Associations under the Ottoman Law of Associations of 3 Aug 1909 (notification 'ilm wa khabar' to the Ministry of Interior and Municipalities, Circular 10/AM/2006); foundations.",
    "Key local requirements": "Foreigners may participate, but foreign-controlled associations may be treated as foreign associations needing separate authorization; local registered office, Arabic founding documents and a local signatory; notification regime, not pre-approval",
    "_note": "verify-rest 2026-10: 'no nationality rule' softened — foreign-controlled associations may require authorization",
    "_source": "https://www.icnl.org/research/library/lebanon_10-am-2006-en/",
}
P["Syria"] = {
    "Main charitable entity types": "Association or private institution under Law No. 93 of 1958 (am. Legislative Decree 224/1969), registered with the Ministry of Social Affairs and Labor",
    "Key local requirements": "Local registration, local address and signatories; MoSAL directive of 1 Oct 2025 requires prior approval for foreign affiliations/funding; replacement associations law still only a draft; in-person steps in Syria; sanctions complicate cross-border funding",
    "_note": "verify-rest 2026-10: no new associations law enacted — Law 93/1958 still governs",
    "_source": "https://stj-sy.org/wp-content/uploads/2026/09/From-State-Control-to-Safeguarding-Independence-Essential-Safeguards-for-Syrias-New-Law-on-Associations.pdf",
}
P["Iraq"] = {
    "Main charitable entity types": "Non-governmental organisations under Law 12 of 2010, registered with the NGOs Department of the Secretariat General of the Council of Ministers (Kurdistan Region: KRG Law 1/2011).",
    "Key local requirements": "Application signed by at least 3 founders who are Iraqi nationals or Iraq residents (foreigners need a valid residence card); local address; Arabic filings",
    "Est. cost & time": "Fees low, but registration requires Iraqi-national or Iraq-resident founders, so non-resident foreigners cannot found directly. Official processing times unpublished.",
    "_note": "verify-rest 2026-10: registering body is the Council of Ministers Secretariat NGO Department; no 10-founder minimum (3 resident/national founders)",
    "_source": "https://www.icnl.org/research/library/iraq_12-2010-reg-en/",
}
P["Saudi Arabia"] = {
    "Main charitable entity types": "Civil association or foundation under the Law of Associations and Foundations (Royal Decree M/8, in force 17 Mar 2016), administered by MHRSD / National Center for Non-Profit Sector Development; foreign NGO partnership only",
    "_note": "verify-rest 2026-10: no '2024 Civil Society Law (M/111)' exists — the 2015/16 Royal Decree M/8 law governs",
    "_source": "https://www.icnl.org/resources/civic-freedom-monitor/saudi-arabia",
}
P["Kuwait"] = {
    "Main charitable entity types": "Association (jam'iyya) under Law 24/1962 on Clubs and Public Welfare Societies (Ministry of Social Affairs; 2025 Ministerial Decision 90 cut charitable-association founders to 10 Kuwaitis); representative office of foreign NGO",
    "Key local requirements": "Founders (min. 10, Kuwaiti, 21+) and board must be Kuwaiti citizens; local address; Arabic filings; foreign individuals cannot form an NGO",
    "_note": "verify-rest 2026-10: governing law Law 24/1962 cited; 2025 founder rule added",
    "_source": "https://www.icnl.org/research/library/kuwait_24-62-en/",
}
P["Qatar"] = {
    "Main charitable entity types": "Private association or institution under Decree-Law No. 21 of 2020 (replacing Law 12/2004); charitable activity regulated by Law No. 15 of 2014 and the Regulatory Authority for Charitable Activities (RACA); partnership with an existing charity",
    "_note": "verify-rest 2026-10: no '2023 philanthropy law' — Decree-Law 21/2020 + Law 15/2014 govern",
    "_source": "https://www.shura.qa/en/Pages/MediaCenter/News/14122020",
}
P["United Arab Emirates"] = {
    "Main charitable entity types": "Non-profit organisation (public benefit association, civil society foundation, etc.) under Federal Decree-Law No. 50 of 2023 (which repealed Federal Law 2/2008); Dubai charities also under Dubai Law 12/2017 (IACAD/DCC); private foundations at free-zone level (DIFC, ADGM)",
    "Key local requirements": "Foundation (DIFC/ADGM): 1-3 founders, 100% foreign ownership allowed, local service provider; federal NPO: founder/board nationality rules per FDL 50/2023 executive regulations; local office address; English accepted",
    "_note": "verify-rest 2026-10: FL 2/2008 was repealed (not amended) by FDL 50/2023; the old 70% UAE-national board rule came from the repealed law",
    "_source": "https://www.lexismiddleeast.com/law/UnitedArabEmirates/DecreeLaw_50_2023/en",
}
P["Oman"] = {
    "Main charitable entity types": "Civil society institution (association, foundation) under the Civil Society Institutions Law (Royal Decree 64/2026, in force 15 Jun 2026, repealing RD 14/2000); branch of foreign NGO",
    "_note": "verify-rest 2026-10: RD 64/2026 replaced the Civil Associations Law; executive regulations due within a year — founder/nationality rules may change",
    "_source": "https://decree.om/2026/rd20260064/",
}
P["Bahrain"] = {
    "Key local requirements": "Founders must be Bahraini citizens (min. ~10 adults under Decree-Law 21/1989 as amended); Bahraini-controlled board; local address; Arabic filings",
    "Est. cost & time": "Registration is effectively out of reach for foreigners: Decree-Law 21/1989 requires Bahraini founders (~10 minimum). Official processing time unpublished.",
    "_note": "verify-rest 2026-10: founder minimum corrected to ~10; 'Law 19/2006' founder-rule reference removed",
    "_source": "https://www.lloc.gov.bh/FullEn/L2189.docx",
}
P["Palestine"] = {
    "Key local requirements": "Minimum 7 founders (application signed by at least 3); registration with the Ministry of Interior, which must decide within 2 months; local (Ramallah/West Bank) address; Arabic filings",
    "_note": "verify-rest 2026-10: registration is with the Ministry of Interior; founder minimum is 7 (not ~15)",
    "_source": "https://security-legislation.ps/latest-laws/law-no-1-of-2000-concerning-charitable-associations-and-civil-society-organisations/",
}
P["Egypt"] = {
    "Main charitable entity types": "Association or foundation under Law No. 149 of 2019 on Regulating the Practice of Civil Work (replacing Law 70/2017; executive regulations PM Decree 104/2021); nonprofit company",
    "Key local requirements": "Formation by notification to the Ministry of Social Solidarity; local registered office; founders may include foreigners with legal residence in Egypt; Arabic documents.",
    "_note": "verify-rest 2026-10: Law 70/2017 replaced by Law 149/2019; ministry is Social Solidarity (not Youth & Sports)",
    "_source": "https://eg.andersen.com/ngo-registration-in-egypt/",
}

# ---- batch v6 ----
P["South Africa"] = {
    "Main charitable entity types": "Non-profit company (NPC, Companies Act 71/2008); trust (Trust Property Control Act 57/1988); NPO (Nonprofit Organisations Act 71/1997); PBO tax status (Income Tax Act s.30, SARS)",
    "Key local requirements": "No foreign restrictions; NPO registration with the Department of Social Development (online) — mandatory since the General Laws Amendment Act 22/2022 for NPOs giving or serving outside South Africa; local office/registered agent; English filings.",
    "_note": "verify-rest 2026-10: NPO Act is 71/1997 (not 78/1997); DSD registration mandatory for cross-border NPOs since 2022",
    "_source": "https://www.cliffedekkerhofmeyr.com/news/publications/2023/Practice/Corporate/corporate-and-commercial-law-alert-20-september-recent-amendments-to-south-africas-non-profit-organisation-legislation-in-response-to-the-fatf-greylisting-",
}
P["Belgium"] = {
    "Key local requirements": "Belgian registered office (seat must be in Belgium); ASBL/VZW needs 2+ founders (CSA 2019) and may be formed by private deed filed via e-greffe; a foundation requires a notarial deed (no fixed statutory minimum endowment); French/Dutch-language statutes",
    "_note": "verify-rest 2026-10: ASBL needs 2+ founders (no 2024 one-founder reform); private deed suffices for an ASBL; no EUR 25,000 legal minimum for foundations",
    "_source": "https://justice.belgium.be/fr/themes_et_dossiers/societes_associations_et_fondations/associations/asbl",
}
P["Luxembourg"] = {
    "Main charitable entity types": "ASBL and fondation under the Law of 7 August 2023 on non-profit associations and foundations (replacing the 1928 law, in force 23 Sept 2023)",
    "Key local requirements": "Luxembourg registered office; ASBL needs 2+ founding members; foundation requires EUR 100,000 minimum endowment and authorisation; English widely accepted",
    "_note": "verify-rest 2026-10: 1928 law repealed and replaced by the Law of 7 Aug 2023; ASBL minimum is 2 founders",
    "_source": "https://gouvernement.lu/dam-assets/documents/actualites/2023/10-octobre/18-myasbl/flyer-myasbl.pdf",
}
P["Germany"] = {
    "Main charitable entity types": "Eingetragener Verein e.V. (BGB §§55-79); Gemeinnützige gGmbH (GmbHG §5); Stiftung (uniform federal foundation law, BGB §§80-88, since 1 July 2023); charitable (gemeinnützig) tax status (AO §§51-68)",
    "Registration fee (USD)": "~$100-150 (e.V.: EUR 75 register-court fee + notary signature certification)",
    "_note": "verify-rest 2026-10: e.V. court fee EUR 75 (GNotKG KV 13100) + notary certification; foundation law federalised in BGB since July 2023",
    "_source": "https://www.fimportal.de/api/v0/leistung-stammtexte/L100009/6000167-99119004060000/pvog/de/pdf",
}
P["Austria"] = {
    "Main charitable entity types": "Eingetragener Verein (Verein, Vereinsgesetz 2002/VerG); charitable foundation (Bundes-Stiftungs- und Fondsgesetz 2015, BGBl. I 160/2015, EUR 50,000 minimum assets) or Privatstiftung (PSG, BGBl. 694/1993); non-profit GmbH (GmbHG, charity tax status per KStG §7 (donations: EStG §18))",
    "_note": "verify-rest 2026-10: foundation law citations corrected (BStFG 2015 for charitable foundations; PSG 1993 for private foundations)",
    "_source": "https://www.ris.bka.gv.at/eli/bgbl/i/2015/160/P0/NOR40178270",
}
P["Switzerland"] = {
    "Key local requirements": "Foundation: no statutory minimum capital, but supervisory authorities generally expect ~CHF 50,000; Swiss seat, foundation council (at least 1 Swiss-domiciled member in practice); association needs a Swiss seat and statutes",
    "_note": "verify-rest 2026-10: CHF 50,000 is supervisory practice, not statutory (ZGB arts. 80-89; foundation law revised 1 Jan 2024)",
    "_source": "https://www.forvismazars.com/ch/en/insights/swiss-tax-newsletter/archive/swiss-tax-e-newsletter-june-2024/recent-developments-foundation-and-trust-law",
}
P["Liechtenstein"] = {
    "Main charitable entity types": "Stiftung (foundation, PGR Art. 552 §§1-41, totally revised 2008, LGBl. 2008/220, in force 1 Apr 2009); Verein (association, PGR Art. 246 ff.); Anstalt (foundation-like, PGR Art. 534-551)",
    "_note": "verify-rest 2026-10: foundation-law revision dated 2008/2009 (not 2002)",
    "_source": "https://www.grantthornton.ch/en/insights/overview-liechtenstein-foundation-stiftung/",
}
P["San Marino"] = {
    "Registration fee (USD)": "$0 registry (free per Art. 11); notary deed cost extra",
    "Time to register": "2-6 weeks (ATS decides within 10 days of application; notary deed beforehand)",
    "_note": "verify-rest 2026-10: fee/time columns reconciled with the law (free registration, 10-day ATS decision)",
    "_source": "https://www.consigliograndeegenerale.sm/on-line/home/documento17076457.html",
}
P["Poland"] = {
    "Registration fee (USD)": "~$200-475 for a fundacja (KRS court fee 250 PLN + notary deed ~500-1,500 PLN); stowarzyszenie: 0 PLN (Art. 17 ust. 3 fee exemption)",
    "_note": "verify-rest 2026-10: USD range recomputed from its PLN components",
    "_source": "https://arch-bip.ms.gov.pl/pl/rejestry-i-ewidencje/krajowy-rejestr-sadowy/oplaty-obowiazujace-w-postepowaniu-rejestrowym/",
}
P["Czechia"] = {
    "Main charitable entity types": "spolek (association), ústav (institute), nadace (foundation, CZK 500,000 min. endowment) or nadační fond (no minimum); optional public-benefit status (status veřejné prospěšnosti, Civil Code §§146-150) entered by the registry court",
    "Key local requirements": "Spolek needs 3+ founders with a common interest (foreigners allowed), a local registered office; nadace needs 1 founder, min. CZK 500,000 endowment (Civil Code §336), notarial deed; Czech-language statute.",
    "_note": "verify-rest 2026-10: nadace minimum endowment is CZK 500,000; 'OUK' mislabel removed; public-benefit status entered by the registry court, not the Interior Ministry",
    "_source": "https://www.icnl.org/resources/research/ijnl/structural-and-systemic-issues-surrounding-the-establishment-and-management-of-endowments-in-the-czech-and-slovak-republics",
}
P["Slovakia"] = {
    "Main charitable entity types": "Občianske združenie (civic association, Act 83/1990, Ministry of Interior); nadácia (foundation, Act 34/2002, endowment EUR 6,638); nezisková organizácia (public-benefit NO, Act 213/1997 as amended by Act 109/2025, district office)",
    "Key local requirements": "Civic association needs a preparatory committee of 3+ persons (one aged 18+), local office and Slovak-language statutes; foundation via notarized deed; no citizenship requirement.",
    "Registration fee (USD)": "~$70 (EUR 66 civic association; EUR 33 online)",
    "_note": "verify-rest 2026-10: civic association needs 3 founders, EUR 66 fee, ~10-15 days; Act 213/1997 amended by Act 109/2025 (Constitutional Court ruling PL. ÚS 11/2025)",
    "_source": "https://static.slov-lex.sk/static/SK/ZZ/2025/109/20260204.html",
}
P["Hungary"] = {
    "Foreign donor / donation restrictions": "No authorization regime: the 2017 foreign-funded NGO law (Act LXXVI/2017) was struck down by the CJEU (C-78/18) and repealed from 1 July 2021; under Act XLIX of 2021 the State Audit Office reviews NGOs 'capable of influencing public life'; Sovereignty Protection Act (Act LXXXVIII of 2023) adds scrutiny of foreign-funded political activity",
    "Main bottleneck (remote foreign founder)": "Local office and Hungarian-lawyer involvement typical; Hungarian-resident curator needed; foreign-funded NGOs face State Audit Office scrutiny",
    "_note": "verify-rest 2026-10: 2017 'Stop-Soros'/foreign-funding authorization law repealed in 2021 — replaced by Act XLIX of 2021 audit regime",
    "_source": "https://www.amnesty.org/en/latest/press-release/2021/05/hungary-lexngo-finally-repealed-but-a-new-threat-is-on-the-horizon/",
}
P["Croatia"] = {
    "Main charitable entity types": "udruga (association, Zakon o udrugama NN 74/14 as am. 70/17, 98/19, 151/22; public-benefit status available), zaklada (foundation, Zakon o zakladama NN 106/18, 98/19), neprofitna ustanova (nonprofit institution)",
    "Est. cost & time": "~EUR 70-200 fees + notary; ~1-3 months (statutory 30 days, often longer)",
    "_note": "verify-rest 2026-10: foundation is 'zaklada'; costs restated in EUR (HRK replaced 1 Jan 2023)",
    "_source": "https://www.zakon.hr/z/64/zakon-o-udrugama",
}

# ---- batch v3 ----
P["Taiwan"] = {
    "Key local requirements": "Foreigners can form a private foundation under the Foundations Act (2018) with a local registered office; minimum endowment is set by each competent authority (e.g. Taipei City charity foundations: NT$10M cash; central-level foundations higher); after authority permission, register at the local District Court; documents in Chinese, board can include foreign directors.",
    "_note": "verify-rest 2026-10: endowment minimum varies by competent authority (no uniform NT$15M/30M tiers); court registration follows permission",
    "_source": "https://laws.gov.taipei/Law/LawSearch/LawArticleContent/FL043047",
}
P["Hong Kong"] = {
    "Key local requirements": "No nationality or residency requirement for directors/members; a Hong Kong registered office address (virtual office works) and a company secretary resident in HK (or an HK-based corporate secretary); tax-exempt charity status is a separate application to the Inland Revenue Department (s.88 IRO).",
    "Est. cost & time": "Companies Registry fee HK$155 (online)/HK$170 (paper) for a CLG with ≤25 members (~US$20); incorporation in 3–5 days; IRD s.88 tax-exempt recognition takes an additional 1–3+ months.",
    "Registration fee (USD)": "~$20 (HK$155 online CLG incorporation)",
    "Time to register": "3-5 days to incorporate; +1-3 months for IRD s.88 charitable status",
    "_note": "verify-rest 2026-10: s.88 tax-exempt status is granted by the IRD (not the HK Jockey Club); CLG fee is HK$155/170 (HK$1,545 is the share-company fee)",
    "_source": "https://www.cr.gov.hk/en/services/fees.htm",
}
P["Macau"] = {
    "Main charitable entity types": "Private foundation (Fundação) or association (社團) under Law 2/99/M and the Civil Code provisions on legal persons (arts. 140-172)",
    "Key local requirements": "No nationality bar; name-availability certificate from the Identification Services Bureau (DSI), notarised deed of establishment, publication in the Boletim Oficial, then DSI registration; local office address.",
    "_note": "verify-rest 2026-10: Civil Code articles and procedure corrected — registration runs through the DSI",
    "_source": "https://www.gov.mo/en/services/ps-1069/",
}
P["Singapore"] = {
    "Key local requirements": "Charity registration needs 3+ governing board members, at least 2 of whom are Singapore citizens or PRs (IPC status: at least half citizens); the CLG also needs 1 ordinarily resident director; local registered office (agent address OK); English-language constitution.",
    "_note": "verify-rest 2026-10: a registered charity needs at least 2 Singapore citizen/PR board members, not just one resident director",
    "_source": "https://ask.gov.sg/mccy-cu/questions/clpq9t4w3001i1xxmfdxxczl4",
}
P["Indonesia"] = {
    "Key local requirements": "Foreign-founded yayasan governed by PP 63/2008 as amended by PP 2/2013: at least one of chair/secretary/treasurer must be an Indonesian citizen; foreign officers need a KITAS; local notary deed required.",
    "Registration fee (USD)": "~$15 government (IDR 250,000 AHU PNBP); ~$400–1,600 incl. notary",
    "_note": "verify-rest 2026-10: government fee is ~IDR 250,000 (PP 28/2019; tariffs revised by PP 30/2026 from 1 Aug 2026) — the IDR 5-20M range is mostly notary cost",
    "_source": "https://portal.ahu.go.id/uploads/324489_Matriks%20Jenis%20dan%20Tarif%20PNBP%20Ditjen%20AHU%20PP%2028%202019.pdf",
}
P["Thailand"] = {
    "Main charitable entity types": "Foundation (มูลนิธิ, Civil and Commercial Code ss.110-136; endowment ~THB 200,000-500,000) and registered association (CCC ss.78-109), registered with the Ministry of Interior registrar (district office in Bangkok / Provincial Governor elsewhere).",
    "Key local requirements": "Thai-majority board expected in Interior Ministry vetting practice (not an express statutory quota); foreign directors vetted (passport, visa, work permit, embassy certificates); local registered office, Thai-language documents, in-person steps.",
    "_note": "verify-rest 2026-10: no 'Foundation Act B.E. 2550' — CCC governs; registrar is the Ministry of Interior, not Justice",
    "_source": "https://www.thailawonline.com/glossary/foundation-and-association/",
}
P["Vietnam"] = {
    "Main charitable entity types": "Association under Decree 126/2024/ND-CP (replacing Decree 45/2010); social/charity fund under Decree 03/2026/ND-CP with citizen founders; foreign NGOs only via a Representative Office under Decree 58/2022.",
    "_note": "verify-rest 2026-10: Decree 125/2020 (tax penalties) replaced by the correct associations decree 126/2024",
    "_source": "https://english.luatvietnam.vn/co-cau-to-chuc/decree-126-2024-nd-cp-on-the-organization-operation-and-management-of-associations-367881-d1.html",
}
P["Philippines"] = {
    "Key local requirements": "No general nationality quota for non-stock trustees (limits apply only in nationalised sectors such as education/media); the corporate secretary must be a Filipino citizen and resident and the treasurer a resident; local office address.",
    "Registration fee (USD)": "~$40 government (PHP 1,000 SEC filing + legal research fee); ~$1,100–2,800 incl. counsel",
    "_note": "verify-rest 2026-10: no two-thirds Filipino trustee rule; SEC filing fee PHP 1,000 (MC No. 3 s.2017)",
    "_source": "https://appointment.sec.gov.ph/wp-content/uploads/2020/01/2017MCno03-new2.pdf",
}
P["Cambodia"] = {
    "Main charitable entity types": "Association or domestic NGO under the Law on Associations and Non-Governmental Organizations (LANGO, 2015), registered with the Ministry of Interior; foreign NGOs sign an MoU with MOFAIC",
    "Key local requirements": "Domestic association: 3+ founding members aged 18+; domestic NGO: 3 Khmer-national founders; local office; foreign NGOs need an MOFAIC MoU and annual reporting.",
    "_note": "verify-rest 2026-10: LANGO dates from 2015 (not 2003); Khmer-nationality founder rule applies to domestic NGOs",
    "_source": "https://www.sithi.org/medias/files/projects/sithi/law/Unofficial-Translation-LANGO.pdf",
}
P["Laos"] = {
    "Main charitable entity types": "Association under Decree on Associations No. 238/GOV (2017); foundation under the foundations decree; INGO under Decree No. 126/GOV of 25 May 2026 (in force 15 Jul 2026, replacing PM Decree 013/2010)",
    "_note": "verify-rest 2026-10: no 'Law on Social Organisations and NGOs' — Decree 238/2017 governs associations; new INGO Decree 126/GOV (2026) requires prior MOFA approval for cooperation",
    "_source": "https://www.rajahtannasia.com/viewpoints/ingos-regulations-amended/",
}
P["Myanmar"] = {
    "Main charitable entity types": "Registered organisation under the Organization Registration Law 2022 (SAC Law No. 46/2022, repealing the 2014 Association Registration Law), via the Union Registration Board (Ministry of Home Affairs); INGO representative office",
    "Key local requirements": "Registration requires a local sponsor/contact and Burmese-language filings; INGOs need at least 40% Myanmar citizens on the executive committee; new registrations reportedly largely suspended; foreign individuals cannot form organisations directly.",
    "_note": "verify-rest 2026-10: registration body is the Union Registration Board under the 2022 law (no 'National Registration Bureau')",
    "_source": "https://www.dfdl.com/insights/legal-and-tax-updates/myanmar-new-organization-registration-law-enacted/",
}
P["Timor-Leste"] = {
    "_note": "verify-rest 2026-10: registration handled by the National Directorate for Registration and Notarial Services (DNRN), Ministry of Justice",
    "_source": "https://lpr.adb.org/resource/decree-law-no-52005-non-profit-corporate-bodies-timor-leste",
}
P["New Zealand"] = {
    "Main charitable entity types": "Incorporated society under the Incorporated Societies Act 2022 (in force 5 Oct 2023; re-registration of existing societies closed 5 Apr 2026) registered with the Companies Office; charitable status is a separate registration with Charities Services (DIA).",
    "Key local requirements": "Charities Services registration (free, online); at least 1 contact person ordinarily resident in NZ (s.114); no residency rule for officers",
    "Est. cost & time": "Registration fee NZ$88.89 plus GST (NZ$102.22, ~USD 60) under the Incorporated Societies Regulations 2023; processing usually a few days to weeks; foreign founders welcome, residency not required for officers.",
    "Registration fee (USD)": "~$60 (NZ$102.22 incl. GST)",
    "_note": "verify-rest 2026-10: Act in force since 5 Oct 2023; Charities Commission abolished 2012 (now Charities Services); fee NZ$102.22",
    "_source": "https://is-register.companiesoffice.govt.nz/help-centre/forms-and-fees/fees/",
}
P["Papua New Guinea"] = {
    "Main charitable entity types": "Company limited by guarantee under the Companies Act 1997 via the IPA registry; associations under the Associations Incorporation Act 2023 (commenced 1 July 2026, replacing the 1966 Act; existing associations re-register by 30 June 2027).",
    "_note": "verify-rest 2026-10: Associations Incorporation Act 2023 itself commenced 1 July 2026",
    "_source": "https://www.ipa.gov.pg/public/help.aspx?cn=NewAssociationsAct",
}
P["Tonga"] = {
    "_note": "verify-rest 2026-10: amendments to the Charitable Trusts Act 1993 under consultation (MCCTIL memo 21 July 2026), incl. trustee disclosure requirements",
    "_source": "https://businessregistries.gov.to/Documentation/TO/Consultation_Memo_Proposed_Amendments_CharitableTrustsAct_July_21_2026.pdf",
}

# ---- batch v5 ----
P["Kyrgyzstan"] = {
    "Est. cost & time": "State fee ~100 KGS (~US$1-2) for non-commercial organisations (Cabinet Resolution No. 470 of 23 Aug 2022 as amended by No. 560); ~5 business days, e-filing via State Registration Portal",
    "Registration fee (USD)": "~$1-2 (100 KGS NCO state fee; expedited costs more)",
    "_note": "verify-rest 2026-10: NCO registration fee is 100 KGS per Resolution 470/560 (2022); 2024 'Foreign Representatives' amendments apply to foreign-funded NCOs doing 'political activity'",
    "_source": "https://gratanet.com/news/on-reducing-the-amount-of-fees-for-state-registration-re-registration-of-legal-entities",
}
P["Gabon"] = {
    "_note": "verify-rest 2026-10: Law 35/62 still governs associations ('loi 001/2011' unsupported); NGO bill adopted by the National Assembly 16 May 2025, Senate vote/promulgation pending",
    "_source": "https://gabonmediatime.com/gabon-que-prevoit-la-loi-sur-les-ong-portee-par-foumboula/",
}
P["Rwanda"] = {
    "Main charitable entity types": "National NGO (Law N°04/2012) or international NGO (Law N°05/2012), registered with the Rwanda Governance Board (RGB) - certificate of legal personality; a consolidated NGO bill was tabled in 2024.",
    "Est. cost & time": "Registration fee 300,000 RWF (~$210), non-refundable, paid electronically at e-imiryango.rgb.rw; RGB statutory decision window 60-90 days.",
    "Registration fee (USD)": "~$210 (300,000 RWF non-refundable)",
    "_note": "verify-rest 2026-10: no 'Law 01/2016' — NGOs governed by Laws 04/2012 and 05/2012; 300,000 RWF ≈ US$210 (not ~$24)",
    "_source": "https://www.rgb.rw/1/civil-society-faith-based-and-political-organisations/non-governmental-organisations",
}
P["Burundi"] = {
    "Main charitable entity types": "Non-profit association under Law 1/02 of 27 Jan 2017 (Interior Ministry); foreign NGOs under Law 1/01 of 23 Jan 2017 (amending Law 1/011 of 1999 on cooperation with foreign NGOs).",
    "_note": "verify-rest 2026-10: foreign-NGO route is governed by Law 1/01 of 2017",
    "_source": "https://presidence.gov.bi/wp-content/uploads/2017/04/loi-02-2017.pdf",
}
P["Tanzania"] = {
    "Main charitable entity types": "NGO under the NGO Act No. 24 of 2002 (Cap. 56, amended by Act No. 9 of 2019), registered at district/regional/national level with the NGO Registrar; INGOs at national level.",
    "Key local requirements": "Local NGO: 5+ founders, all Tanzanian; international NGO: 5+ founders including at least 2 Tanzanians; local office.",
    "Est. cost & time": "National-level fee TZS 115,000 (~$45) + TZS 1,500 stamp duty; INGO USD 350 + TZS 4,500 stamp duty; online via nis.jamii.go.tz; processing time unpublished.",
    "Registration fee (USD)": "~$45 local NGO (TZS 115k); USD 350 + stamp duty for an INGO",
    "_note": "verify-rest 2026-10: NGO Act is No. 24 of 2002 (am. 2019); INGO fee USD 350; founder rules corrected",
    "_source": "https://www.jamii.go.tz/services/ngos-registration",
}
P["Kenya"] = {
    "Main charitable entity types": "Public Benefit Organization under the PBO Act 2013 (in force 14 May 2024, repealing the NGO Co-ordination Act 1990), regulated by the PBO Regulatory Authority (PBORA); company limited by guarantee; trust.",
    "Key local requirements": "One-third of directors must be Kenyan nationals resident in Kenya; international PBOs need an authorised agent who is a resident Kenyan citizen and a Kenyan office.",
    "Est. cost & time": "PBO Regulations 2026: KES 25,000 (~US$195) national PBO / KES 45,000 (~US$350) international PBO; processing time unpublished; foreign founders allowed with resident Kenyan directors.",
    "Registration fee (USD)": "~$195 national / ~$350 international PBO (KES 25,000 / 45,000)",
    "_note": "verify-rest 2026-10: PBO Act 2013 in force since 14 May 2024 (NGO Board/KES 100,000 deposit route obsolete); PBO Regulations 2026 fees",
    "_source": "https://cms.law/en/ken/news-information/salient-provisions-of-the-public-benefits-organizations-regulations-2026",
}
P["Mozambique"] = {
    "_note": "verify-rest 2026-10: 'Lei 31/2002' unsupported — Lei 8/91 + Decreto 55/98 remain operative; the 2022 OSFL bill was dropped from Parliament's agenda in Apr 2023",
    "_source": "https://www.dlapiperafrica.com/pt/mozambique/insights/legislation-series/associations-and-ngos/associations-and-ngos.html",
}
P["Angola"] = {
    "Main charitable entity types": "Associação registada (civil association, Lei 6/12 de 18 de Janeiro — Lei das Associações Privadas); ONG nacional (Lei 2/26 art. 5); ONG estrangeira registered in Angola with mandatory prior habilitação (Lei 2/26 arts. 4-6)",
    "_note": "verify-rest 2026-10: Lei 14/91 replaced by Lei 6/12; Lei 2/26 (2 Mar 2026) replaced PD 74/15 for NGOs — existing NGOs adapt by Sept 2026",
    "_source": "https://www.plmj.com/en/knowledge/informative-notes/New-NGO-law-Key-changes/34394/",
}
P["Botswana"] = {
    "Key local requirements": "Board of at least 3 members, local office; at least two-thirds of office bearers must reside in Botswana with security clearance (Societies Act 2022); English filings.",
    "_note": "verify-rest 2026-10: Societies Act 2022 two-thirds resident office-bearer rule",
    "_source": "https://www.dlapiperafrica.com/en/botswana/insights/2023/new-societies-act-2022-of-botswana.html",
}
P["Namibia"] = {
    "Main charitable entity types": "Non-profit company (Sec. 21 \"company not for gain\", Companies Act 28 of 2004, BIPA); registered society (Societies Act); trust registered with the Master of the High Court (Trust Administration Act 11 of 2023); NamRA welfare-organisation tax status",
    "_note": "verify-rest 2026-10: trusts register with the Master under the Trust Administration Act 11 of 2023 (not the Deeds Registries Act)",
    "_source": "https://www.lac.org.na/laws/annoSTAT/Trust%20Administration%20Act%2011%20of%202023.pdf",
}
P["Zimbabwe"] = {
    "Registration fee (USD)": "US$150 local / US$250 international PVO (+ legal/agent US$100-500)",
    "Time to register": "up to ~3 months (90-day statutory provisional decision; deemed provisional registration otherwise)",
    "_note": "verify-rest 2026-10: PVO (General) Regulations 2026 (SI 97/2026) set fees and a 90-day decision deadline; international PVOs need an authorised local agent",
    "_source": "https://www.mmmlawfirm.co.zw/the-private-voluntary-organisations-board-and-general-regulations-2026-a-guide-to-registration-governance-and-regulatory-oversight/",
}

# ---- batch v7 ----
P["Serbia"] = {
    "Key local requirements": "Association needs 3+ founders, at least one with residence/seat in Serbia, and a Serbia-resident agent (zastupnik); local office, Serbian-language charter; foundation 1 founder, endowment per charter.",
    "Foreign founder (no local presence)": "partial",
    "Registration fee (USD)": "~$60 (RSD 6,500 APR fee; schedule revised 1 Jan 2026)",
    "_note": "verify-rest 2026-10: Law on Associations requires a Serbia-resident founder and agent (yes->partial); APR fee RSD 6,500",
    "_source": "https://apr.gov.rs/registers/associations/fees.1628.html",
}
P["North Macedonia"] = {
    "Key local requirements": "Association needs 5+ founders, 3 with domicile/seat in North Macedonia (Art. 15); foundation needs EUR 10,000 minimum endowment; local office, Macedonian-language charter.",
    "_note": "verify-rest 2026-10: founder rule corrected to 5 (3 local); foundation endowment EUR 10,000",
    "_source": "https://www.icnl.org/wp-content/uploads/Macedonia_zakon.pdf",
}
P["Albania"] = {
    "Main charitable entity types": "Non-profit associations (5+ natural or 2+ legal persons, Law 8788/2001 Art. 10; foreigners OK); foundations; NPO register kept by the Tirana first-instance court under Law 80/2021 (partly struck down by the Constitutional Court, Nov 2023); public-benefit status available.",
    "Key local requirements": "Association 5+ founders (foreigners allowed), local office, Albanian-language charter; registration with the Tirana court register (accepts applications by post/courier).",
    "_note": "verify-rest 2026-10: founder minimum is 5 natural/2 legal persons; register is held by the Tirana court, not the National Registration Center",
    "_source": "https://www.tatime.gov.al/eng/shkarko.php?id=5278",
}
P["Moldova"] = {
    "Main charitable entity types": "Public associations (2+ founders); foundations; registered by the Public Services Agency under Law 86/2020 on Non-commercial Organisations. Foreigners may found with local involvement.",
    "Key local requirements": "Association 2+ founders (natural or legal persons; foreigners allowed), local office, Romanian-language charter (Russian widely used in practice); foundation 1 founder, endowment per charter.",
    "Time to register": "2-6 weeks (statutory registration term 15 days)",
    "_note": "verify-rest 2026-10: Law 86/2020 allows 2 founders; registration free with a 15-day statutory term",
    "_source": "https://asp.gov.md/en/intrebari-frecvente/persoane-juridice/0041",
}
P["Ukraine"] = {
    "Main charitable entity types": "Hromadska orhanizatsiia (public association, Law 4572-VI); blahodiinyi fond (charitable foundation, Law 5073-VI on Charitable Activities and Charitable Organizations); non-profit status via the tax register",
    "Key local requirements": "Organization 2+ founders (foreign individuals must be lawfully staying in Ukraine), local office, Ukrainian-language documents; online registration.",
    "Est. cost & time": "State registration of a public association is free; translations/notary extra; statutory review ~3 working days, ~1-2 weeks total",
    "Registration fee (USD)": "$0 (registration free of charge)",
    "_note": "verify-rest 2026-10: no state duty for public-association registration; 'fundatsiia' replaced with blahodiinyi fond",
    "_source": "https://kyivcity.gov.ua/news/yak_zareyestruvati_gromadsku_organizatsiyu_pokrokova_instruktsiya/",
}
P["Belarus"] = {
    "Key local requirements": "Public association needs 10+ founders (local) or 50+ (republican) under the Law on Public Associations (1994, as amended 2023); local office; Russian- or Belarusian-language charter; foreign-funded NGOs face heavy restrictions.",
    "_note": "verify-rest 2026-10: founder minimum is 10 (local) / 50 (republican)",
    "_source": "https://belhelcom.org/sites/default/files/10_right_to_freedom_of_association_2022.pdf",
}
P["Bulgaria"] = {
    "Key local requirements": "Foundation needs only 1 founder; association needs 3+ founders (7 natural or 3 legal persons for public-benefit) (NPLE Act Art. 19); foreigners allowed; local office; Bulgarian-language documents.",
    "Est. cost & time": "Registry Agency fee ~EUR 25 (euro since 1 Jan 2026) plus notary fees; statutory 30 days. Foreigners can found an NPLE; no residency requirement for the founding act itself.",
    "Registration fee (USD)": "~$30 (Registry Agency fee ~EUR 25)",
    "_note": "verify-rest 2026-10: association founder minimum is 3; Registry Agency fee ~EUR 25",
    "_source": "https://bcnl.org/en/category_legislation/basic-information",
}
P["Greece"] = {
    "Main charitable entity types": "Associations (somateio, min. 20 founders, Civil Code art. 78); foundations (Civil Code arts. 108-121 + Law 5259/2025, which repealed Law 4182/2013); general-benefit status via separate application.",
    "Key local requirements": "Association needs 20+ founders (foreigners allowed), Greek registered office, Greek-language charter registered by order of the Magistrates' Court (Eirinodikeio); foundation 1 founder, endowment per charter, notary deed.",
    "Registration fee (USD)": "~$100 government (court/stamp fees); ~$1,300 total incl. notary/legal",
    "_note": "verify-rest 2026-10: somateio needs 20 founders; registration via Magistrates' Court since 2016; Law 5259/2025 replaced 4182/2013",
    "_source": "https://www.e-nomothesia.gr/kat-oikonomia/nomos-5259-2025.html",
}
P["Cyprus"] = {
    "Main charitable entity types": "Charitable trust (unregistered); society (20+ founders) or institution (idryma, 1 founder) under the Societies and Institutions Law 104(I)/2017; company limited by guarantee with a Council of Ministers licence (Companies Law Cap. 113, s.20)",
    "Key local requirements": "A charitable trust needs only a settlor + trustee and no registration; a society needs 20+ founding persons and an institution 1 founder, plus a local address, registered with the District Officer/Registrar; English fully accepted.",
    "Time to register": "days-weeks (trust via solicitor); up to ~3 months (society/institution — Registrar has 3 months to examine)",
    "_note": "verify-rest 2026-10: society needs 20 founders under Law 104(I)/2017; Registrar may take up to 3 months",
    "_source": "https://mondaq.co.uk/cyprus/directors-and-officers/1229390/registration-and-establishment-of-societies-in-the-republic-of-cyprus",
}
P["Ireland"] = {
    "Main charitable entity types": "Companies limited by guarantee (most charities); incorporated associations; registered with the CRO and then with the Charities Regulator (Charities Act 2009).",
    "Key local requirements": "Irish registered office and at least one EEA-resident director (or a EUR 25,000 s.137 bond / s.140 certificate); every charity operating in Ireland must register with the Charities Regulator regardless of income",
    "Est. cost & time": "CRO incorporation about EUR 100; Charities Regulator registration is free; 4-8 weeks. Foreign directors permitted if the EEA-residency rule or bond is met.",
    "_note": "verify-rest 2026-10: no EUR 50k registration threshold; regulator is the Charities Regulator; s.137 requires an EEA-resident director or bond",
    "_source": "https://www.charitiesregulator.ie/",
}
P["United Kingdom"] = {
    "Key local requirements": "Charity must be established and administered in the UK (UK address, UK-law governing document); no trustee residency or citizenship requirement; Charity Commission registration required above GBP 5,000 income (CIOs register at any income)",
    "_note": "verify-rest 2026-10: no UK-resident trustee requirement; registration threshold GBP 5,000 (CIOs always register)",
    "_source": "https://www.gov.uk/setting-up-charity/register-your-charity",
}
P["Iceland"] = {
    "Main charitable entity types": "Associations / third-sector organisations (Act 110/2021); non-business foundations (sjálfseignarstofnanir, Act 19/1988 as am. by Act 112/2024; charter approved by the District Commissioner) or business foundations (Act 33/1999); tax-deductible status via Skatturinn's public-benefit register (almannaheillaskrá).",
    "_note": "verify-rest 2026-10: charitable foundations fall under Act 19/1988 (Act 33/1999 is for business foundations); third-sector Act 110/2021; RSK is now Skatturinn",
    "_source": "https://www.skatturinn.is/um-rsk/frettir-og-tilkynningar/almannaheillaskra",
}
P["Norway"] = {
    "Key local requirements": "Norwegian address for the association (min. 2 founders, no nationality rules); foundation needs NOK 100,000 capital (NOK 200,000 commercial) and incurs a registration fee (~NOK 2,656 online)",
    "_note": "verify-rest 2026-10: association needs 2 founders; foundation minimum capital NOK 100,000",
    "_source": "https://www.brreg.no/?p=31547",
}
P["Finland"] = {
    "Main charitable entity types": "Associations (yhdistys, 3+ founders, Associations Act 503/1989); foundations (säätiö, Foundations Act 487/2015, EUR 50,000 minimum capital); registered with PRH. Charitable status via the Tax Administration.",
    "Key local requirements": "Finnish address; association needs 3+ founding members; foundation needs EUR 50,000 minimum basic capital (PRH fee ~EUR 920) and an EEA-resident board",
    "_note": "verify-rest 2026-10: association needs 3 founders; foundation minimum capital EUR 50,000",
    "_source": "https://www.prh.fi/en/companiesandorganisations/saatiorekisteri/establishmentandregistration.html",
}
P["Sweden"] = {
    "Main charitable entity types": "Ideell förening (non-profit association; organisation number from Skatteverket, form SKV 8400, free); ekonomisk förening (registered at Bolagsverket); stiftelse (foundation, county administrative board).",
    "Registration fee (USD)": "$0 for an ideell förening (Skatteverket); ~$180-210 for an ekonomisk förening (SEK 1,900 online)",
    "_note": "verify-rest 2026-10: ideell förening gets its org. number from Skatteverket free; Bolagsverket fee applies only to economic associations",
    "_source": "https://www.skatteverket.se/foreningar/driva/ideellforening/",
}
P["Denmark"] = {
    "Main charitable entity types": "Voluntary associations (frivillige foreninger); foundations; associations registered with the CVR register. The Act on Foundations and Certain Associations (LBK nr. 2020 of 11/12/2020, as amended) applies to foundations.",
    "Key local requirements": "Danish address, min. 2 members, registered in the CVR register; Foundations Act (LBK 2020/2020) requires a Danish-resident board majority for foundations",
    "Est. cost & time": "Association registration at CVR is free; DKK 0-2,000 total with legal support; 2-6 weeks. Foundations Act (LBK 2020/2020) requires a Danish-resident board majority.",
    "_note": "verify-rest 2026-10: LB 938/2012 superseded by consolidated LBK nr. 2020 of 11/12/2020",
    "_source": "https://www.retsinformation.dk/api/pdf/209400",
}

# ---- batch v9 ----
P["Sudan"] = {
    "Key local requirements": "Sudanese founders/chair, local office, registration with the Humanitarian Aid Commission (HAC) Registrar General under the 2006 Act.",
    "Registration fee (USD)": "~$100-300 national NGO (nominal, when functional); INGO SDG 600,000 (~$1,050) + ~$700 annual renewal (CoM res. 3/2023)",
    "_note": "verify-rest 2026-10: registrar is HAC (not the Ministry of Culture & Information); 2023 HAC INGO fees added",
    "_source": "https://www.icnl.org/resources/library/the-voluntary-and-humanitarian-work-organization-act",
}
P["Libya"] = {
    "Main charitable entity types": "Non-governmental organisations under NGO Law No. 19 of 2001, re-applied since 2023 (High Judicial Council opinion of 8 Mar 2023; PM Circular No. 7 of 21 Mar 2023 requires regularisation via the Civil Society Commission); scope limited to social, cultural, sports, charitable and humanitarian work.",
    "_note": "verify-rest 2026-10: '2013 circulars' replaced by the 2023 HJC opinion and PM Circular 7 re-imposing Law 19/2001",
    "_source": "https://cihrs.org/libya-new-commission-to-apply-gaddafi-era-law-is-ominous-development-for-civil-society/?lang=en",
}
P["Algeria"] = {
    "Main charitable entity types": "Associations under Law 12-06 of 12 Jan 2012 (2020 Constitution art. 53 moved to a declaration principle; replacement bill still draft); associations d'intérêt général; registered with the wilaya (province) authorities.",
    "_note": "verify-rest 2026-10: Law 12-06 was not amended in 2020 — only the constitutional basis changed",
    "_source": "https://www.hrw.org/news/2025/09/25/algeria-lift-undue-restrictions-on-associations",
}
P["Tunisia"] = {
    "_note": "verify-rest 2026-10: governing text is Décret-loi 2011-88 (which repealed Law 59-154 of 1959); founders must be 16+ (13 is the member age floor); 2023 replacement bill still pending in the ARP",
    "_source": "https://juridoc.tn/document/decret-loi-n--2011-88-du-24-septembre-2011-portant-organisation-des-associations/13883",
}
P["Morocco"] = {
    "Main charitable entity types": "Association (Dahir 1-58-376 of 1958, am. Law 75-00 of 2002; declaration at prefecture); Cooperatives (Law 112-12, am. Law 74-16); foreign associations need Interior Ministry permit",
    "_note": "verify-rest 2026-10: cooperatives governed by Law 112-12 (not 19-00)",
    "_source": "https://adala.justice.gov.ma/api/uploads/2024/04/09/Cooperatives-1712660938413.pdf",
}
P["Ethiopia"] = {
    "Main charitable entity types": "Local CSO and foreign CSO/NGO (CSO Proclamation No. 1113/2019; registration with the Authority for Civil Society Organizations (ACSO); a restrictive 2025 amendment bill not known to be enacted)",
    "Key local requirements": "A local organization may be formed by Ethiopians and/or foreigners resident in Ethiopia; non-resident foreigners must work through a partner organization or a registered foreign CSO.",
    "_note": "verify-rest 2026-10: registrar is ACSO; resident foreigners may co-found local CSOs, non-residents cannot",
    "_source": "https://www.jurist.org/news/2025/08/ethiopia-urged-to-abandon-proposed-changes-to-civil-society-organization-law",
}
P["Somalia"] = {
    "Main charitable entity types": "NGO registered administratively with the Ministry of Planning, Investment and Economic Development (federal NGO Bill 2019 still a draft); national and international NGOs; domestic associations under regional law",
    "_note": "verify-rest 2026-10: federal 'NGO Act 2019' is still a draft bill — registration is administrative via MoPIED",
    "_source": "https://www.icnl.org/our-work/somalia",
}
P["Somaliland"] = {
    "Main charitable entity types": "Welfare (charitable) NGO under Law No. 43/2010 on Welfare NGOs (National and International), 5+ founders, nationals or foreigners; association",
    "Key local requirements": "Local registered office and local partner involvement; registration with the Ministry of National Planning and Development (sole NGO registrar; up to 2 weeks once complete; periodic renewal).",
    "_note": "verify-rest 2026-10: law is No. 43/2010 (not 'Decree 82/11'); registrar is the Ministry of National Planning and Development",
    "_source": "https://slministryofplanning.org/documents/Manual-for-International-Org.pdf",
}
P["South Sudan"] = {
    "Registration fee (USD)": "~$200-500 national NGO; ~$1,000-3,500 international NGO (RRC 2017 schedule; 2018 waiver with renewal fees)",
    "_note": "verify-rest 2026-10: RRC fees — 2017: US$500 national / US$3,500 international; 2018 waiver left US$200/1,000 renewal fees",
    "_source": "https://www.radiotamazuj.org/en/news/article/south-sudan-government-exempts-aid-agencies-from-registration-fees",
}
P["Seychelles"] = {
    "_note": "verify-rest 2026-10: local regime is the Associations Act 2022 (Act 8/2022, in force 14 Aug 2023, repealing Cap 201) — the 'NPO Act Cap. 741' claim is unsupported; Foundations Act 2009 route unaffected",
    "_source": "https://gazette.sc/sites/default/files/2023-08/SI%2054%202023%20-%20Associations%20Act%20%28Commencement%29%20Notice%202023.pdf",
}
P["Mauritius"] = {
    "Main charitable entity types": "NPO (Registration of Associations Act 1978, Registry of Associations); Foundation (Foundations Act 2012, Registrar of Foundations); Company Limited by Guarantee (Companies Act 2001)",
    "_note": "verify-rest 2026-10: foundation statute is the Foundations Act 2012 (not 2016)",
    "_source": "https://www.fscmauritius.org/media/ps0irpxm/foundations-act-2012.pdf",
}
P["Pakistan"] = {
    "Key local requirements": "2+ trustees with at least one Pakistani resident in practice, local registered office; Section 42 company needs at least one Pakistani resident director and local secretary, with an SECP licence (Companies Regulations 2024; 3-year renewable licence, incorporate within 60 days).",
    "Est. cost & time": "Trust: ~PKR 30,000-80,000, 2-8 weeks; Section 42 company: ~PKR 150,000-250,000, 4-8 weeks",
    "Registration fee (USD)": "~$100-300 (trust) to ~$600-900 (Section 42 company)",
    "Time to register": "4-12 weeks (trust 2-8; Section 42 4-8; FBR exemption separate)",
    "_note": "verify-rest 2026-10: 'Sec 21' corrected to Section 42 (Companies Act 2017); licensing now under Companies Regulations 2024",
    "_source": "https://www.secp.gov.pk/licensing/section-42-companies/",
}
P["Bangladesh"] = {
    "Main charitable entity types": "NGO (Voluntary Social Welfare Agencies Ordinance 1961, Department of Social Services); foreign-funded NGO registration with the NGO Affairs Bureau (Foreign Donations (Voluntary Activities) Regulation Act 2016); charitable trust (trust deed); company limited by guarantee (Companies Act 1994)",
    "Key local requirements": "Local office and local officers required; foreign-funded activity needs NGO Affairs Bureau registration; board composition largely Bangladeshi in practice.",
    "_note": "verify-rest 2026-10: 1978 Ordinance replaced by FDRA 2016; registrar is the NGO Affairs Bureau (not BIDA); two-thirds citizen board rule unverified and removed",
    "_source": "https://www.icnl.org/research/library/bangladesh_fdva/",
}
P["Sri Lanka"] = {
    "Main charitable entity types": "Public charitable trust (Trusts Ordinance Cap. 87, No. 9 of 1917; incorporation by Ministerial order under s.114; Registrar-General/Ministry of Justice); Company Limited by Guarantee (Companies Act 2007); association (Companies Act s.34)",
    "_note": "verify-rest 2026-10: Trusts Ordinance is Cap. 87; no 'Commissioner of Charities' exists",
    "_source": "https://www.documents.gov.lk/view/extra-gazettes/2023/9/2349-17_E.pdf",
}
P["Nepal"] = {
    "Main charitable entity types": "NGO/association (Associations Registration Act 2034 (1977), District Administration Office); trust (National Civil Code 2074 (2017) ss.314-351); Social Welfare Council affiliation",
    "Key local requirements": "NGO: 7+ founders who are Nepali citizens, registration at the District Administration Office plus Social Welfare Council affiliation; trust with a foreign settlor needs one-third Nepali-resident trustees and US$1M+ movable property remitted within 3 months (Civil Code ss.316, 320).",
    "_note": "verify-rest 2026-10: no general 'Trust Act 2000' — Civil Code 2017 governs trusts; foreign-settlor trust carries a US$1M threshold; NGO needs 7 Nepali founders",
    "_source": "https://nepallaws.com/Laws/the-national-civil-code-act-2074/part-4-laws-relating-to-property/chapter-6-provisions-relating-to-trusts/section-316-application-to-be-made-for-establishment-of-trust/",
}


# ==== consistency sweep: purge claims superseded above from other columns ====
def fix(country, cells):
    P.setdefault(country, {}).update(cells)

CA, TX, BN, FD, NT = ("Annual compliance & reporting", "Tax-exempt status & benefits",
                      "Main bottleneck (remote foreign founder)", "Foreign donor / donation restrictions", "_drop")

fix("Trinidad & Tobago", {
    CA: "Companies Act Chap. 81:01: annual return to the Companies Registry within 30 days of incorporation anniversary (directors, office, officers); NPOs also file under the NPO Act 2019. Late default: penalties. Accounts kept; audit where required. Non-filing: strike-off.",
    TX: "Ministry of Finance 'approved charity' status; donors deduct covenanted donations up to 15% of income; charity exempt from income tax (Income Tax Act Chap. 75:01). No deduction without approval. Time unpublished.",
})
fix("Cameroon", {NT: ["2017 civil-society law"], "_note2": None})
fix("Afghanistan", {
    CA: "NGOs file annual activity and financial reports to the Ministry of Economy (NGO Directorate); non-filing risks sanctions or deregistration.",
    TX: "NGO registered with the Ministry of Economy; NOT automatic - apply to the Revenue Authority for a tax-exemption certificate (income tax + business receipt tax); no donor deduction; ~30-90 days.",
})
fix("Nigeria", {
    NT: ["NCMM"],
    BN: "CAC incorporation (incorporated trustees or CLG), then SCUML registration before banking; international NGOs also register with the National Planning Commission",
    FD: "SCUML (EFCC) registration mandatory; international NGOs register with the National Planning Commission; a Foreign Aid Regulation Bill (2026) is pending",
    CA: "CAC annual returns + annual report for incorporated trustees (CAMA 2020) due within 6 months of fiscal year end; SCUML reporting; non-compliance risks fines and deregistration.",
    TX: "Incorporated trustee registered with CAC; tax exemption under CITA (non-profit organization) via separate FIRS application; no general donor income-tax deduction; time unpublished.",
})
fix("Ghana", {
    NT: ["Charities Commission registration has been operational"],
    "Est. cost & time": "ORC statutory fee ~GHS 490 (~$40, 2025) plus non-refundable licensing fee to the NPO Secretariat; provisional licence 3 months, official time unpublished.",
    BN: "Two-stage: ORC incorporation under Companies Act 992, then NPO Secretariat operating licence (NPOs Policy/Directive 2020)",
})
fix("Côte d'Ivoire", {})
fix("Benin", {FD: "Foreign NGOs need authorization under Loi 2025-19 + Decree 2025-636 (Oct 2025) to establish or act in Benin"})
fix("Burkina Faso", {
    NT: ["2018 constitutional ban"],
    CA: "Associations under Loi 011-2025/ALT; ONGs need ministry authorization; ongoing oversight, non-compliance risks administrative dissolution (118 organisations dissolved, 1,056 suspended in Apr 2026).",
    TX: "Association registered under Loi 011-2025/ALT; public-utility recognition by decree adds full tax benefits; association income tax-exempt when applied to its purposes; no donor deduction; time unpublished.",
})
fix("Guinea-Bissau", {NT: ["Prior cited Lei n. 5/VI/96"]})
fix("Senegal", {TX: "Association declared to the administrative authority (COCC arts. 811 ff.); income tax exemption automatic under CGI art.5(7) (since 2019) for non-profit entities without commercial activity; donors deduct gifts to public-utility orgs, cap 0.5%."})
fix("Gambia", {NT: ["Societies Act 1972"]})
fix("Sierra Leone", {NT: ["Companies Act 2013 CLG route"]})
fix("Liberia", {
    NT: ["NGO Act 2015 operative"],
    BN: "Liberian principal officer required to sign filings; local office; MFA endorsement plus MFDP NGO Unit accreditation with annual fees",
})
fix("Niger", {NT: ["Law 93-010"]})
fix("Honduras", {
    NT: ["Poder Judicial (Chancilleria)"],
    BN: "SGJD/DIRRSAC legal-personality filing plus local address/representative; all filings in Spanish.",
})
fix("Nicaragua", {CA: "Legal personality is granted and cancelled by the Ministerio de Gobernación (Ley 1115); entities file financial statements, donor lists and activity reports with Gobernación; non-compliance leads to cancellation."})
fix("Bolivia", {
    NT: ["Ley 1417"],
    BN: "Resident officers + local address, notarized deed; foreign-constituted NGOs need a framework agreement with the Foreign Ministry (Ley 351 art. 13)",
    FD: "Foreign-constituted NGOs must sign a framework cooperation agreement with the Ministerio de Relaciones Exteriores (Ley 351/2013) and report foreign funding",
})
fix("Paraguay", {CA: "Registration in the National Registry of Non-Profit Organizations (MEF) under Ley 7363/2024 and Decreto 4806/2025 with funding/beneficiary reporting; entities receiving state funds must publish accounts to the Contraloría."})
fix("Uruguay", {
    "Registration fee (USD)": "low (~US$10-30, MEC recognition + registry)",
    CA: "Associations and foundations are recognised and supervised by the MEC; foundations file annual accounts with the MEC; no published annual return deadline for associations.",
})
fix("Argentina", {NT: ["Ley 27.290 was absorbed"]})
fix("Chile", {
    NT: ["Ley 20.839/2015"],
    BN: "Chilean registered office and resident legal representative required; constitutive act deposited at the Secretaría Municipal (30-day review) then Registro Civil.",
})
fix("Latvia", {
    NT: ["2016 Nonprofit Organizations Law"],
    "Est. cost & time": "State fee EUR 11.38 (10% less online); total EUR 30-100; 1-4 weeks. E-filing with an e-signature avoids the notary step. A Latvian address is required.",
    TX: "Registration automatic; PBO status is a separate VID application (Public Benefit Organisation Law) - PBOs exempt from income tax. Donors: individuals 25.5% tax refund; corporate 5% of prior profit or CIT reduction.",
})
fix("Saudi Arabia", {
    NT: ["M/111"],
    FD: "Foreign funding only via approved partnership with Saudi entity; Law of Associations and Foundations (RD M/8, 2016) requires approval and oversight",
})
fix("Qatar", {NT: ["2023 philanthropy law"]})
fix("United Arab Emirates", {
    NT: ["association route is blocked for all-foreign boards"],
    BN: "Local service provider + UAE office required; federal NPOs subject to FDL 50/2023 nationality and approval rules, so foreign founders typically use a DIFC/ADGM foundation.",
})
fix("Oman", {CA: "Civil Society Institutions Law (RD 64/2026): ministry supervision includes inspection of annual audited accounts and verification of compliance with the constitution; executive regulations pending."})
fix("Syria", {NT: ["post-2025 regime unstable"]})
fix("Iraq", {
    CA: "NGO Law 12/2010 Art. 15: each NGO sends the NGOs Department (Council of Ministers Secretariat) a financial report on fund sources and transactions plus an activity report, for the prior year by 31 March; the Department can sanction.",
    TX: "NGOs registered with the NGOs Department: if classified as public utility, art. 17 of Law 12/2010 automatically exempts income tax, VAT, customs and sales tax; no separate application.",
})
fix("Egypt", {CA: "Law 149/2019: associations file an annual activity report and financial statements with the Ministry of Social Solidarity; larger ones must have accounts audited; risks suspension."})
fix("Bahrain", {
    NT: ["20 Bahraini founders"],
    CA: "Decree-Law 21/1989: each association keeps an annual budget; where revenues or expenses exceed BHD 10,000 the board must present final accounts audited by a licensed firm; the Ministry supervises and can sanction.",
})
fix("Jordan", {
    "Est. cost & time": "A$100-500 fees, 1-3 months (gated by finding 7+ Jordanian founders)",
    FD: "Foreign funding routed via registered local society; prior Council of Ministers approval + detailed reporting to the Ministry of Social Development",
    TX: "Registration with the Ministry of Social Development confers legal personality; the income-tax law exempts income of registered societies pursuing public-benefit purposes, and donations to them are deductible.",
})
fix("Italy", {
    NT: ["EUR 150,000 endowment", "€150,000"],
    BN: "EUR 30,000 patrimony for a fondazione (EUR 15,000 associazione) plus Italian registered office; foreign founders allowed with no residency rule.",
})
fix("Belgium", {NT: ["1 founder enough post-2024"]})
fix("Czechia", {NT: ["OUK min. endowment"]})
fix("Slovakia", {
    "Est. cost & time": "Civic association: EUR 66 Ministry of Interior fee (EUR 33 online), ~10-15 days; foundation: notary EUR 500-1,500 + registry; 1-2 months; foreign founders OK, Slovak charter + local address needed",
    BN: "Slovak-language charter, 3+ founders and local office; foreign founders need apostilled docs and certified translations",
})
fix("Hungary", {NT: ["Stop-Soros", "7.2M HUF"]})
fix("Croatia", {NT: ["500-1,500 HRK"]})
fix("Hong Kong", {
    NT: ["then HKJC charitable status", "HKJC charitable status separate"],
    "_note3": None,
})
fix("Macau", {
    NT: ["arts. 1642-1667", "DSAJ name-certificate"],
    BN: "Local office, Chinese/Portuguese documents, notarised deed, Boletim Oficial publication and DSI registration; limited English support",
    CA: "Private foundations and associations (Civil Code / Law 2/99/M): no routine financial-statement filing with the DSF and no published general annual-return requirement; registry updates with the DSI.",
})
fix("Cambodia", {NT: ["LANGO 2003"]})
fix("Myanmar", {CA: "Organisations registered with the Union Registration Board (Organization Registration Law 2022) must submit annual activity and audited financial reports; the Board may suspend or deregister for non-compliance."})
fix("Rwanda", {NT: ["Law 01/2016 governs"]})
fix("Tanzania", {
    NT: ["2021 amendments tightened", "No. 22 of 2002"],
    BN: "NGO Registrar registration requires a local office; international NGOs need 5+ founders incl. at least 2 Tanzanians",
    FD: "Foreign-funded NGOs disclose funding to the NGO Registrar/Board; funding and reporting monitored; no outright ban",
})
fix("Kenya", {
    NT: ["NGO Act 2003 was repealed"],
    "Bank account (remote feasibility)": "In-person at branch under CBK AML/KYC rules; PBO accounts require at least one Kenyan-resident director as signatory plus the PBORA registration certificate, so a local representative is needed.",
})
fix("Mozambique", {NT: ["Lei 31/2002"]})
fix("Angola", {CA: "Lei 6/12 (private associations) and Lei 2/26 (NGOs): the entity registers with the competent authority; NGOs face prior authorisation and oversight; no recurring annual filing regime is published; sanctions include dissolution/withdrawal of registration."})
fix("Gabon", {
    NT: ["loi n°001/2011 governs"],
    BN: "Interior accreditation (Law 35/62 declaration + ONG agrément), local rep, office; French filings; post-2023 transition adds uncertainty",
})
fix("Ukraine", {NT: ["state duty ~2,000 UAH"]})
fix("Greece", {
    NT: ["2019 law modernized foundations", "Association min 7 founders"],
    "Time to register": "2-4 months (notary + Magistrates' Court registration; slower for remote founders)",
})
fix("Cyprus", {
    NT: ["s.250 Companies Law"],
    "Est. cost & time": "Trust: ~500-2,000 EUR via solicitor, days; society/institution: ~100-500 EUR, up to ~3 months (Registrar review)",
})
fix("Iceland", {
    NT: ["reykjafrjálsefni"],
    "Charitable deduction regime": "Deductible if the organisation is on Skatturinn's public-benefit register (almannaheillaskrá); individuals deduct ISK 10,000-350,000/yr, companies up to 1.5% of income.",
})
fix("Libya", {NT: ["2013 circulars"]})
fix("Tunisia", {NT: ["Decree-Law 59-154"]})
fix("Ethiopia", {NT: ["1259/2021"]})
fix("Somalia", {CA: "Federal registration (MoPIED) requires annual financial and narrative reports including audit; registration renewal periodically; draft federal NGO Bill (2019) would formalise duties."})
fix("Somaliland", {CA: "Law 43/2010: the certificate is renewed periodically with the Ministry of National Planning and Development and annual NGO reports are assessed; NGOs that fail to renew are struck off the register."})
fix("Seychelles", {NT: ["NPO Act 2013", "Cap. 741"]})
fix("Pakistan", {BN: "Resident Pakistani director/secretary (Section 42 company) or trustee required; SECP licence then FBR tax-exempt status as separate steps."})
fix("Bangladesh", {CA: "NGO Affairs Bureau: registration valid ten years under FDRA 2016 and must be renewed; foreign-funded projects need prior approval; annual reports on donation receipt and utilisation; non-compliance can lead to suspension or deregistration."})
fix("Nepal", {NT: ["5 of 7 Nepali"]})
fix("Portugal", {NT: ["no statutory minimum endowment"]})
fix("Lebanon", {
    CA: "Ottoman Law of Associations (1909) declaration regime; detailed annual filing duties are unpublished, but undeclared associations are prohibited and the government can dissolve one.",
    TX: "Associations are valid by declaration to the Ministry of Interior (1909 Law); the income-tax code exempts income of public-benefit associations and institutions — no separate application; no donor-deduction regime.",
})
fix("Indonesia", {BN: "At least one of chair/secretary/treasurer must be an Indonesian citizen and foreign officers need a KITAS (PP 63/2008, PP 2/2013); in practice a local individual/PT is founder of record"})
fix("Germany", {"Est. cost & time": "e.V.: EUR 75 court fee + notary signature certification (~USD 100-150 total); gGmbH: capital USD 27,500 + notary/registry USD 700-1,200; Stiftung: endowment typically USD 55k+; registration 4-8 weeks; charity status timing unpublished"})
fix("Zimbabwe", {"Key local requirements": "Local PVOs register with the PVO Registrar (Ministry of Public Service, Labour and Social Welfare); international PVOs must name an authorised local agent; fees in USD."})
fix("Papua New Guinea", {NT: ["regulations commence 1 July 2026"]})
for _c in list(P):
    for _k in ("_note2", "_note3"):
        P[_c].pop(_k, None)

# corrected rewrites of lead notes dropped above
for _c, _t in {
    "Cameroon": "Heavy discretionary approval for ONG status; most expats partner with an existing Cameroonian association instead.",
    "Nigeria": "Most structured path in West Africa but multi-layered; CAC incorporation, SCUML and (for INGOs) National Planning Commission registration are the foreigner bottlenecks; English language; strong expat NGO sector in Lagos/Abuja",
    "Ghana": "Most foreigner-friendly framework in the region: no local-national director requirement under the Companies Act 2019 (Act 992); NPO licensing by the NPO Secretariat (NPO Bill pending); English language",
    "Burkina Faso": "High political risk: military rule since 2022, repeated suspensions of international NGOs (e.g. 2023–24 expulsions) and mass dissolutions under Loi 011-2025/ALT; effectively impractical for a foreign-funded charity",
    "Latvia": "Associations and foundations share one law (2003); e-filing with an EU e-signature avoids the notary, otherwise notarised signatures force an in-person visit or a local representative",
    "Italy": "Foreign (including Australian) founders can legally establish a fondazione — explicitly no nationality or residency requirement — with a minimum EUR 30,000 patrimony (EUR 15,000 for associations) for legal personality via RUNTS (Registro Unico Nazionale del Terzo Settore); the procedure is document-based and can be handled by a local notary/lawyer with a representative, avoiding in-person steps. Italian-language filings are mandatory.",
    "Saudi Arabia": "The 2016 Law of Associations and Foundations (RD M/8) keeps a Saudi-citizenship floor; the only realistic foreign route is a program partnership with a Saudi charity or a representative office for an existing foreign NGO; English widely used in government dealings",
    "Qatar": "State oversight of foreign-funded charitable work runs through RACA (Law 15/2014); standard foreign route is a partnership with Qatar Charity or an established Doha NGO, or a representative office approved by the relevant ministry",
    "United Arab Emirates": "Most accessible Gulf option for a foreign founder: a DIFC/ADGM foundation can be 100% foreign-held and run charitable activities; Dubai's IACAD/DCC also registers existing international charities; federal NPOs follow FDL 50/2023 approval rules; strong English-language support",
    "Hungary": "Foreign-funded NGOs face State Audit Office scrutiny (Act XLIX of 2021) and the 2023 Sovereignty Protection Act — politically sensitive; public-benefit (közhasznú) status is a separate, stricter regime; kft capital 3,000,000 HUF",
    "Hong Kong": "The most accessible route in this list; full English-language process; popular expat pathway is the company limited by guarantee, then IRD s.88 tax-exempt charity status; low political risk.",
    "Macau": "Formation under Law 2/99/M and the Civil Code (arts. 140-172) via DSI registration; a new associations law was in public consultation in 2026; documents in Chinese or Portuguese — English support is limited.",
    "Tanzania": "Foreign-funding disclosure and local-content expectations apply; English/Swahili; NGO Registrar oversight is strict.",
    "Greece": "Paper/notary-heavy process, Greek language required, no meaningful online registry; foundations now under Law 5259/2025; use a local lawyer.",
    "Iceland": "Documents in Icelandic; tax-deductible status requires registration on Skatturinn's public-benefit register; small bureaucracy but limited English support",
}.items():
    P[_c]["_prose"] = _t
