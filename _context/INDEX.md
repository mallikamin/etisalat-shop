# etisalat-shop — Index

The wikipedia of this project. Read me first.

## What this project is

Etisalat number reseller marketing site (etisalat-shop.com / per `CNAME`). Static HTML with location pages (dubai/, abu-dhabi/, emirati/, etc.), blog content, plan comparison pages, and Python tooling for feed/page/asset generation. Sister/related project to `uaepremiumnumbers` and `goldennummbers` per memory.

<!-- TODO: confirm relationship to goldennummbers + uaepremiumnumbers -->

## Quick links

- Entry point: `index.html`
- 404 page: `404.html`
- **Current truth: root `STATE.md` — always read FIRST.** Dated files below are history.
- Most recent notes: `_files/2026-06-06/NOTES_2026-06-06_HOME_WIRELESS_LOCAL.md` (Home Wireless launch + checkout + 5.5G campaign + 21 local pages; resume checklist inside)
- Older: `NOTES_2026-05-31_CONSULTANT_BAR.md` → `_files/2026-05-26/PAUSE_CHECKPOINT_2026-05-26.md` → `CHECKPOINT_2026-04-08.md` → `PAUSE_CHECKPOINT_2026-02-22.md`
- NOTE: `CONTINUATION_2026-05-15_QUALITY_RED.md` is a MIRROR of the bilal-app WABA event, NOT this site's status (see STATE.md header)
- Domain migration notes: `DOMAIN_MIGRATION_2026-04-07.md`
- Error log: `ERROR_LOG.md`
- Documentation: `DOCUMENTATION.md`
- SEO/AI plan: `AI_SEO_EXECUTION_PLAN.md`
- Free backlink execution queue: `BACKLINK_EXECUTION_QUEUE.md`
- **Google Ads runbook: `GOOGLE_ADS_RUNBOOK.md`** (gitignored — local only) — GN VIP Search campaign LIVE 2026-06-24; account map, setup lessons (account-activation unlock), monitoring/read plan, + the API-automation plan
- GBP plans: `GBP_30_POSTS_2026-05-15.md`, `GBP_SEO_PLAN_2026-05-09.md`
- Generators: `generate_number_pages.py`, `generate_feed.py`, `generate_assets.py`, `generate_ads.py`
- Pipeline notes: `PIPELINE_BILAL_CRM.md`
- CNAME: `CNAME`
- Schema: ./SCHEMA.md (TODO)
- Infra: ./INFRA.md (TODO)
- Credentials: ./CREDENTIALS.md (gitignored)
- Verified facts: ./VERIFIED.md

## Architecture (verified only)

<!-- TODO — fill from a real audit. Observable top-level pages: dubai/, abu-dhabi/, emirati/, etisalat-plans-under-200-aed/, cheapest-etisalat-postpaid-plan/, best-etisalat-plan-for-family/, choose-number/, blog/, ar/, cards/, functions/. -->

## Current status

See root **`STATE.md`** (authoritative, overwritten in place). As of 2026-06-06: Home Wireless
product line live (/home-wireless/ EN+AR + 3 blogs + checkout + 5.5G campaign), 21 local
city/area pages live, sitemap 61 URLs, FAQ 126 Q&As, GSC resubmitted + priority URLs
request-indexed.

## People involved

- Malik Amin (owner)
- Bilal Khalid (UAE partner — per `memory/partners-trust-circle.md`)

## Reference material

Saved locally — see `notes/`, `screenshots/`, `refs/` subfolders.

| Date | File | Purpose |
|------|------|---------|
| 2026-06-26 | refs/2026-06-26_gsc-performance-3mo.xlsx (+ .md) | GSC 3-mo export to 06-24: 140 clicks / 18.6K impr / 0.8% CTR / pos 8.8; 28d 120 clicks ↑88%. Full Queries+Pages tables — the vanity (vs-du) vs buyer-page (homepage/choose-number/numbers) split |
| 2026-06-26 | refs/2026-06-26_googleads-search-terms.csv | Google Ads "GN VIP" search-terms (acct 933-774-7950): 32 clicks / 148 impr / 21.6% CTR / PKR 8,695 / 6 conv. "buy vip number" carries it; converting terms to add + wrong-geo to negative |
| 2026-06-26 | refs/2026-06-26_googleads-search-keywords.csv | Google Ads keyword-level report — "buy vip number" phrase = 27 clicks / 5 conv; rest barely served |
| 2026-05-26 | screenshots/2026-05-26_gsc-sitemaps-submitted.png | GSC Sitemaps page — /sitemap.xml (24 pages, last read May 22) + /sitemap-numbers.xml (3,366) both Success; baseline before the May 25 +10-URL update |
| 2026-05-26 | screenshots/2026-05-26_gsc-sitemap-34-processed.png | GSC re-read /sitemap.xml on 5/26 — 34 discovered pages, "processed successfully" (the +10 new URLs picked up) |
| 2026-05-29 | screenshots/2026-05-29_etisalat-booth-model-creative-ref.png | Creative reference — model at a vintage Etisalat payphone booth; brief for AI video-gen storyline ideas (goldennummbers social/ad content) |
| 2026-06-06 | screenshots/2026-06-06_home-wireless-advance-premium-en.png | Etisalat Home Wireless product cards (EN): Advance 206/mo 12-mo (was 229, 3-mo promo) · Premium 269/mo 24-mo (was 299, STARZPLAY + GoChat Premium) — source facts for /home-wireless/ build |
| 2026-06-06 | screenshots/2026-06-06_home-wireless-advance-premium-ar.png | Same cards in Arabic (واي فاي منزلي متقدم / مميز) — source for ar/home-wireless/ labels |
| 2026-06-08 | screenshots/2026-06-08_google-ai-overview-al-mamzar-cites-goldennumbers.png | PROOF — Google AI Overview cites "Golden Numbers UAE" by name as authorized dealer on a hyper-local (Al Mamzar) query; goldennummbers.com results in sidebar. The GEO target outcome |
| 2026-06-08 | screenshots/2026-06-08_chatgpt-how-to-order-al-mamzar-cites-goldennumbers.png | ChatGPT "How to Order in Al Mamzar" telling users to browse Golden Numbers UAE + WhatsApp — same hyper-local AI-citation win |
| 2026-06-08 | screenshots/2026-06-08_bing-places-golden-numbers-imported-pending-publish.png | Bing Places — Golden Numbers UAE imported from Google (NAP: Al Zarooni Building 1904 Al Mamzar, 056 699 9377), status Pending Publish. Directory walk #1 |
| 2026-06-11 | screenshots/2026-06-11_gsc-performance-3mo-51-clicks.png | GSC 3-mo performance: 51 clicks / 11.5K impr / pos 8.4, impressions climbing sharply since ~05-25 (June content pushes working at impression level) |
| 2026-06-11 | screenshots/2026-06-11_gsc-recommendation-ar-vs-du-657pct.png | GSC recommendation card: /ar/blog/etisalat-vs-du… +657% impressions — the CTR-fix target (2,308 impr / 1 click / pos 5.3) |
| 2026-06-11 | screenshots/2026-06-11_gsc-autocomplete-special-number-queries.png | Google autocomplete: "buy etisalat special number", "etisalat numbers list", "prepaid" phrasing — terminology gap ("special" vs our "VIP/Golden") |
| 2026-06-11 | screenshots/2026-06-11_gsc-shopping-product-snippets-merchant-invalid.png | GSC Shopping: Product snippets 25 valid/1 invalid · Merchant listings 22 valid/4 invalid — Malik to open detail in GSC |
| 2026-06-11 | screenshots/2026-06-11_gsc-insights-top-content-28d.png | GSC Insights 28d: 40 clicks +73%, 7.42K impr +45%; top = family-plan blog (+500%), vs-du blog, homepage (+400%) |
| 2026-06-11 | screenshots/2026-06-11_gsc-insights-queries-28d.png | GSC Insights 28d queries: "golden number", "etisalat gold number", "etisalat multi sim plans" newly clicking; full CSV export at _files/2026-06-11/gsc-export/ |
| 2026-06-13 | screenshots/2026-06-13_review-bawa-gold-raikot-5star.png | New 5★ Google review (Bawa Gold Raikot, 3h ago) — "got a new SIM through Bilal… professional, friendly… outstanding customer service." Source for /reviews/ page |
| 2026-06-13 | screenshots/2026-06-13_review-elizabeth-sabino-5star.png | New 5★ Google review (Elizabeth Sabino, 3h ago) — "Thanks Sir Bilal Khalid of Etisalat… 101% recommendable, fast processing and very accommodating." Source for /reviews/ page |
| 2026-06-13 | screenshots/2026-06-13_review-aby-almeria-5star.png | 5★ Google review (Aby Almeria, 1wk ago) — "Good service… accommodating agents… recommend this 100 percent." Source for /reviews/ page |
| 2026-06-14 | screenshots/2026-06-14_ai-mode-golden-numbers-uae-NOT-cited.png | Google AI Mode "Golden Numbers UAE" (PK-locale browser, rlz enPK) — 12-site carousel cites xplate (2×) + du Shop; goldennummbers.com NOT cited for its OWN brand term (ranks pos 26). GEO gap |
| 2026-06-14 | screenshots/2026-06-14_ai-mode-etisalat-postpaid-plan-ours-4-5-6.png | Google AI Mode "UAE Etisalat Postpaid plan" — all 3 cited are OURS: IG @postpaidplans (#4, verified ours — id 17841475956754325, postpaidplans/STATE.md) + goldennummbers.com ×2 (#5-6). Strong GEO win |
| 2026-06-14 | screenshots/2026-06-14_ai-mode-etisalat-vip-number-cites-us.png | Google AI Mode "etisalat vip number" — cites goldennummbers.com + uaepremiumnumbers.com (both ours). ⚠ IG @etisalat_golden_numbers cited here is NOT ours (Malik 06-14) — third-party near-name brand-confusion/impersonation risk. Our @goldennummbers absent. xplate also present |
| 2026-06-14 | screenshots/2026-06-14_review-fatma-alshehhi-5star-emirati-arabic.png | NEW 5★ Google review (Fatma Alshehhi — Emirati, Local Guide 134 reviews/268 photos): thanks Bilal for service before & after; bought 3 numbers (1 gold + 2 silver) for her son & daughter with the package. EN translation + Arabic original. Added to /reviews/ + homepage EN/AR; basis for the "trusted by Emirati nationals" Arabic-native social angle |
| 2026-06-14 | screenshots/2026-06-14_review-fatma-alshehhi-5star-arabic-new-badge.png | Same review, Arabic-only with the Google "NEW" badge — the hero asset for IG/FB Arabic posts + stories (signals "Arabic speakers trust us" with no copy) |
| 2026-06-28 | screenshots/2026-06-28_gbp-services-list.png | GBP → Edit Services panel: 3 live custom services (ETISALAT Golden Numbers From AED 188 · Silver Tier Postpaid From 188 · Gold Tier Postpaid From 500); primary cat Telecommunications service provider + additional cat Mobile Phone Shop. Baseline before the SEO/GEO/AEO services build |
| 2026-06-28 | screenshots/2026-06-28_gbp-edit-service-details-dialog.png | GBP "Edit service details" dialog — field limits: Service name 120 chars, Price = From + AED amount, Service description 300 chars. The authoring constraints for the GBP services rollout |
| 2026-06-28 | screenshots/2026-06-28_gbp-perf-interactions-302-6mo.png | GBP Performance Overview, 6mo (Jan–Jun 2026): 302 total Business Profile interactions. Curve Jan 0 → Feb ~35 → Mar ~70 → **Apr ~100 (peak)** → May ~38 (dip) → Jun ~62 (recovering) |
| 2026-06-28 | screenshots/2026-06-28_gbp-perf-calls-35-6mo.png | GBP Performance → Calls, 6mo: 35 total calls. Jan 0 → Feb 5 → **Mar ~18 (peak)** → Apr 7 → May 3 → Jun 2. The "March brought calls, declined since" signal Malik flagged (note: tiny absolute volumes; Mar peak ≈ Ramadan/Eid window) |
| 2026-06-28 | screenshots/2026-06-28_gbp-perf-website-clicks-7-6mo.png | GBP Performance → Website clicks, 6mo: 7 total. Flat ~0–1 through May, then **Jun spike to 6** — interaction type shifting from calls toward website clicks (consistent with the web/pick-first push) |
| 2026-06-28 | screenshots/2026-06-28_gbp-perf-chat-clicks-0-6mo.png | GBP Performance → Chat clicks, 6mo: **0 all months** — NOT a setup miss; Google discontinued GBP chat/messaging entirely on 2024-07-31. The metric is structurally dead. Scratch any "enable GBP chat" idea |
| 2026-06-28 | screenshots/2026-06-28_gbp-perf-directions-260-6mo.png | GBP Performance → Directions, 6mo: **260 total = 86% of all interactions** (Feb 30 → Mar 50 → **Apr 92 peak** → May 35 → Jun 52). Directions IS the Overview curve. The dominant action is the weakest one for a remote/WhatsApp-close number business; Website got only 7. Funnel routes discovery to "visit us" not "buy online" |
| 2026-06-29 | screenshots/2026-06-29_ai-overview-golden-number-marina-cites-gn.png | Google (UAE IP, Bilal) "golden number in marina": AI Overview 6-site sources panel cites **"Golden Numbers UAE — Authorized Etisalat dealer"**, and **goldennummbers.com is the #1 organic result** ("VIP Numbers Dubai", WhatsApp 8087 snippet). GEO win on a NEW area (Dubai Marina), replicating the 06-08 Al Mamzar AI-Overview proof |
| 2026-06-29 | screenshots/2026-06-29_chatgpt-buy-golden-number-cites-gn.png | ChatGPT (UAE) "I want to buy golden number etisalat": positions us as "authorized e& dealer (Gold/Silver/Platinum + postpaid)" — verbatim our entity/llms.txt positioning — with source chips **Etisalat + "Golden Numbers UAE" (+1)**. AEO citation on a head buyer query |
| 2026-06-29 | screenshots/2026-06-29_chatgpt-sources-gn-and-old-etisalat-shop.png | ChatGPT "2 Sources" expanded: BOTH labeled "Golden Numbers UAE", but one carries the **OLD etisalat.shop page title** ("Etisalat Sales \| VIP Numbers \| Calling Plans \| Etisalat Representative UAE") and one the current goldennummbers.com title. The stale etisalat.shop citation = ChatGPT training-data artifact (etisalat.shop is UAE-blocked + already 301→goldennummbers.com) |
| 2026-06-29 | refs/2026-06-29_xplate-ahrefs-backlinks.md | xplate.com Ahrefs teardown (the competitor that out-cites/out-ranks us): **own DR ≈ 4.2** yet most-cited in AI answers → DR isn't the lever. Top links = its own app-store listings + Alibaba UGC + a few DR 9–57 "named source" editorial placements. Fills the "no xplate teardown on file" gap; confirms beat-xplate-not-McKinsey + the OUTREACH package is the gap |
| 2026-07-02 | refs/2026-07-02_gads_*.csv (7 files) | Google Ads GN VIP full exports Jun 22–Jul 2 (search-terms, keywords, ads, ad-groups, assets, auction-insights, impressions-timeseries). Basis of the 07-02 read: "buy vip number" = 6/7 conv @ ≈AED 26; broads caused telco-auction drift (du/eand/virgin); 42% of spend in hidden "Other search terms". Full analysis: root STATE.md 2026-07-02 entry |
| 2026-07-02 | ../_files/2026-07-02/RESUME_GADS_OCI_2026-07-02.md | **LEAN RESUME DOC — Google Ads track.** Surgery executed (31 negatives, 29 broads paused, 6 phrases added); gclid→OCI pipeline LIVE (site beacon → CRM /api/gads-click → D1 gads_clicks → bilal-app/gads_oci_export.py → "CRM Sale" Secondary action); weekly upload routine; Jul-6 review checklist; session gotchas |
| 2026-07-18 | screenshots/2026-07-18_etisalat-business-pro-fiber-flyer.png | e& (etisalat and) "BUSINESS PRO FIBER CONNECTION" flyer — 6 B2B fibre tiers AED 1,095–3,375/mo (200→1000 Mbps down / 20→100 up; 1–10 voice lines; Cloud PABX / 1.ae domain; firewall; 1–2 free devices) + "3 Months Rental Free on FNP" + "Internet Pro 200/300 Mbps, 200 Mbps 15% off". Source flyer for the NEW Business Pro Fiber product-line launch (website/CTA/SEO/GBP/social) — spec captured in _files/2026-07-18/BUSINESS_PRO_FIBER_SPEC.md, PENDING Malik confirmation |
| 2026-07-20 | screenshots/2026-07-20_review-saud-alzarouni-5star.png | NEW 5★ Google review — Saud AlZarouni (Emirati name, Local Guide, 6 reviews), 5 days ago. **Rating-only, no text.** Owner reply posted. Part of the 6-review batch (Jun-28→Jul-15) added to /reviews/ + social |
| 2026-07-20 | screenshots/2026-07-20_review-ajeet-singh-5star.png | NEW 5★ Google review — Ajeet Singh (1 review), 6 days ago. **Rating-only, no text.** Owner reply posted |
| 2026-07-20 | screenshots/2026-07-20_review-mohamed-moinuddinn-5star.png | NEW 5★ Google review WITH TEXT — Mohamed Moinuddinn (Local Guide, 19 reviews/24 photos), 1 week ago: "Bilal khalid did an excellent job securing my VIP number and Delivery it on time. Keep up the good work". Highest-value of the batch (names the VIP-number product + on-time delivery) |
| 2026-07-20 | screenshots/2026-07-20_review-mohammed-sakeel-5star.png | NEW 5★ Google review — Mohammed Sakeel (Local Guide, 11 reviews/1 photo), 2 weeks ago. **Rating-only, no text** |
| 2026-07-20 | screenshots/2026-07-20_review-azion-technology-nakul-joshi-5star.png | TWO NEW 5★ Google reviews WITH TEXT — Azion Technology (business account, 1 review), 2 weeks ago: "Really good support by billal Bhai" (B2B social proof); Nakul Joshi (1 review), 3 weeks ago: "Good services" |
| 2026-07-22 | refs/2026-07-22_gsc-performance-export.zip (extracted → `_files/2026-07-22/gsc-export/`) | **The file that REFUTED the Bilal "ranking collapse" report.** GSC 3-mo Web export (Chart/Queries/Pages/Countries/Devices). Daily data to 07-20: WoW clicks 78→100, impr 4,002→5,690, position 9.54→9.03. 07-18 = 25 clicks = best day on record. UAE = 85% of clicks @ pos 9.44 |
| 2026-07-22 | screenshots/2026-07-22_gsc-perf-3mo-380clicks-pos9.png | GSC Performance 3-mo: 380 clicks / 34K impr / 1.1% CTR / pos 9. Clear sustained uptrend; terminal dip is the 07-20 partial-day data lag, not a crash |
| 2026-07-22 | screenshots/2026-07-22_gsc-perf-28d-258clicks-pos9.1.png | GSC 28d: 258 clicks / 16.7K impr / pos 9.1 — same position as the 7d view, i.e. no degradation |
| 2026-07-22 | screenshots/2026-07-22_gsc-perf-7d-93clicks-pos9.1.png | GSC 7d: 93 clicks / 5.03K impr / pos 9.1. 7d run-rate BEATS the 28d average on clicks (+44%) and impressions (+20%) |
| 2026-07-22 | screenshots/2026-07-22_gsc-queries-7d.png | GSC top queries 7d — `etisalat golden number` pos 2.8, `etisalat special number` 4.4, `050 vip number` 4.5. Head money terms on page 1 |
| 2026-07-22 | screenshots/2026-07-22_gsc-queries-28d.png | GSC top queries 28d — baseline for the 7d comparison: `etisalat golden number` 5.4 (→2.8 in 7d, improved), `golden numbers uae` pos 1.1, `golden number uae` 2.6. Weak tail: `vip numbers` 14.2, `054 du or etisalat` 30.8 |
| 2026-07-28 | screenshots/2026-07-28_gsc-overview-3mo.png | GSC Overview 3-mo (data to 07-25): growth Apr→mid-Jul, peaks 07-07 (~22) + 07-18 (25), then CLIFF from 07-20 — **the collapse the 07-22 session called "data lag" is confirmed real** |
| 2026-07-28 | screenshots/2026-07-28_gsc-perf-7d-daily.png | GSC Performance 7d daily (07-19→07-25): clicks 25 (-74%), impr 1.13K (-80%), position 8.4 INTACT. 07-19 ~16 clicks/~800 impr → 07-21..25 ≈ 0-3 clicks / ~30-50 impr/day. Six near-zero days = not lag |
| 2026-07-28 | screenshots/2026-07-28_gsc-insights-7d-content.png | GSC Insights 7d top content — homepage 10 clicks (-74%), calling-india 2 (-50%), esim-guide 2 (-33%), choose-number 2 (-75%) |
| 2026-07-28 | screenshots/2026-07-28_gsc-insights-7d-queries.png | GSC Insights 7d top queries — brand survives (`golden numbers uae` 3, up from 0), money terms down (`etisalat golden number` -75%, `buy etisalat special number online` -50%) |
| 2026-07-29 | screenshots/2026-07-29_ga4-src-medium-jul01-07.png | GA4 Traffic acq source/medium Jul 1-7: total 401, google/organic 86 (21.5%, ~12.3/day), google/cpc 125, chatgpt/ai-assistant 25 |
| 2026-07-29 | screenshots/2026-07-29_ga4-src-medium-jul08-15.png | GA4 source/medium Jul 8-15: total 833 (viral FB spike 359 referral), google/organic 104 (~13/day), google/cpc 129 |
| 2026-07-29 | screenshots/2026-07-29_ga4-src-medium-jul16-23.png | GA4 source/medium Jul 16-23: total 865, google/organic 122 (~15.3/day, RISING — best window), google/cpc 142, fb/paid 137, ig/paid 86 |
| 2026-07-29 | screenshots/2026-07-29_ga4-src-medium-jul24-29.png | **THE CLIFF IN GA4.** Jul 24-29: total 178 (~30/day, -72%), google/organic 4 sessions TOTAL (~0.7/day, -95%), google/cpc 16, fb/ig paid ≈0, direct 114 holds (tag alive). Refutes the 07-28 "GSC reporting anomaly" verdict |
| 2026-07-30 | screenshots/2026-07-30_gsc-manual-actions-clean.png | **GSC Manual actions RE-CHECK: "No issues detected"** — mid-collapse (07-30). Penalty hypothesis REFUTED |
| 2026-07-30 | screenshots/2026-07-30_gsc-security-issues-clean.png | GSC Security issues RE-CHECK: "No issues detected" (07-30). With Safe Browsing clean, security/domain-flag hypothesis refuted |
| 2026-07-30 | screenshots/2026-07-30_gsc-overview-3mo-384clicks.png | GSC Overview 3-mo (384 web clicks): full arc — growth Apr→mid-Jul, twin peaks 7/9 (~21) + 7/18 (25), then cliff to ~0-3 clicks/day from 07-20 through right edge |
| 2026-08-05 | screenshots/2026-08-05_gsc-insights-7d.png | **Post-remediation checkpoint**: GSC Insights 7d (≈07-27→08-02) = 6 clicks (−40%) / 269 impr (−25%) — still −94/−95% vs pre-cliff, but flat on the floor once the 07-20 cliff day is stripped from the comparison window. Homepage earns 0 clicks; all 6 come from price-index (5) + choose-number?ref=GBP (1) |
| 2026-08-05 | screenshots/2026-08-05_gsc-overview-shopping-enhancements.png | GSC Overview rich results: Product snippets 31 valid/1 invalid · Merchant listings 22 valid/**9 invalid** · Breadcrumbs 32/0 · Review snippets 6/0. The 9 invalid merchant listings are new to the record — worth one look, not a candidate cause of sitewide de-serving |
| 2026-08-05 | screenshots/2026-08-05_gsc-sitemaps-last-read.png | **Gate answered**: both sitemaps LAST READ Aug 4 2026, Success — `/sitemap-numbers.xml` 111 discovered, `/sitemap.xml` 79. Google HAS ingested the 07-30 remediation; "not seen yet" is dead as an explanation |
| 2026-08-05 | screenshots/2026-08-05_gsc-page-indexing-4220-indexed.png | **Strongest evidence in the collapse thread**: Indexed 4.22K / Not indexed 385. Chart shows the ~3.4K number pages sat GREY (not indexed) 05-17→05-27, then flipped GREEN (indexed) 06-06→06-16 — i.e. right after the 06-04 sitemap revert re-fed 3,066 URLs. ⚠ report "Last update 7/24/26" = PRE-FIX baseline |
| 2026-08-05 | screenshots/2026-08-05_gsc-page-indexing-reasons.png | Not-indexed breakdown (385 total): alternate-canonical 256 · discovered-not-indexed 83 · crawled-not-indexed 22 · 404 10 · redirect 9 · noindex 3 · 4xx 1 · **duplicate-different-canonical 1** · redirect-error 0. Confirms no technical exclusion problem and kills the cross-domain canonical hypothesis at scale |
| 2026-08-05 | screenshots/2026-08-05_gsc-sitemaps-removal-submitted.png | `/sitemap-numbers-removal.xml` submitted ahead of the build → "Couldn't fetch", 0 pages. Expected: the file did not exist yet |
| 2026-08-05 | screenshots/2026-08-05_gsc-sitemaps-removal-success-4247.png | **Remediation 3 accepted**: `/sitemap-numbers-removal.xml` last read Aug 5 2026, Success, **4,247 discovered pages**. Recrawl engine live. NOTE: parsed ≠ recrawled — the pages have not yet been revisited, so no `noindex` has been seen yet |
| 2026-08-07 | screenshots/2026-08-07_gsc-page-indexing-stale-724.png | Day-2 checkpoint: Page Indexing STILL "Last update 7/24/26" (14d stale) — Indexed 4.22K / Not indexed 385 unchanged. The progress bar has not refreshed; cannot yet measure the noindex fix |
| 2026-08-07 | screenshots/2026-08-07_gsc-sitemaps-all-read-aug7.png | All 3 sitemaps LAST READ Aug 7 2026, Success: removal 4,247 · `/sitemap-numbers.xml` now shows **12** discovered (was 111 stale read) · `/sitemap.xml` 79. Google fully current on the discovery layer |
| 2026-08-07 | screenshots/2026-08-07_gsc-removals-none.png | GSC Removals (never checked before): **"No requests submitted in the last 6 months"** on all 3 tabs' default view — existing-removal-request hypothesis RULED OUT |
| 2026-08-07 | screenshots/2026-08-07_gsc-performance-7d.png | Performance 7d (7/30→8/5): 7 clicks / 284 impr / CTR 2.5% / pos 14. Daily impressions flat ~35-45; clicks 0-4/day. Floor stable, no recovery, no further decline |
| 2026-08-07 | screenshots/2026-08-07_gsc-performance-28d.png | Performance 28d (7/9→8/5): 158 clicks / 8.82K impr. Full arc: healthy through 7/18-19 peak (25 clicks), cliff 7/20-21, flat near-zero floor since. Confirms collapse shape end-to-end |
| 2026-08-07 | screenshots/2026-08-07_gsc-urlinspect-0501450770-indexed.png | URL Inspection `/numbers/etisalat-0501450770/`: "Page is indexed", crawled copy still carries PRE-FIX `index, follow` tag → **not yet recrawled since the 08-05 noindex**. Live page curl-verified `noindex, follow` same session |
| 2026-08-07 | screenshots/2026-08-07_gsc-urlinspect-crawled-more-info.png | Crawled-page More Info: 200 OK, text/html, 6/10 page resources couldn't load (indexed snapshot, normal) |
| 2026-08-07 | screenshots/2026-08-07_gsc-urlinspect-enhancements-merchant-invalid.png | Same inspection, Enhancements: HTTPS OK · Product snippets 1 valid (non-critical) · **Merchant listings 1 invalid** (the known parked 08-05 finding) · Breadcrumbs 1 valid |
| 2026-08-07 | notes/2026-08-07_url-inspection-0501450770.md | Full verdict note for the URL Inspection spot-check + live-vs-crawled robots-tag comparison; live HTML snapshot at refs/2026-08-07_live-html-0501450770-noindex.html |
| 2026-08-07 | screenshots/2026-08-07_serp-golden-numbers-uae-domain-absent.png | Live SERP for brand query "golden numbers uae": xplate #1, own GBP panel + own Facebook page rank, **goldennummbers.com domain absent from visible top results** — the de-serving made visible; matches homepage 0 clicks |
| 2026-08-07 | screenshots/2026-08-07_serp-related-keywords.png | Related + long-tail keyword lists for "golden numbers uae" (vip number uae, 050 vip number, etisalat golden number…) — post-recovery content fodder, parked |
| 2026-08-07 | screenshots/2026-08-07_external-audit-choose-number-issues.png | External AI audit of /choose-number/ (6 issues). Fact-checked vs live curl: "no structured data" FALSE (4 JSON-LD blocks live), H1 fine, keywords/og cosmetic. One real find: 0 static number cards + empty ItemList `itemListElement` — parked as post-recovery |
| 2026-08-07 | screenshots/2026-08-07_external-audit-handoff-files.png | Same audit's handoff files (dev notes / schema / FAQ). NOT adopted — schema redundant, content changes mid-measurement would muddy attribution. See STATE 08-07 addendum 3 |
| 2026-08-07 | screenshots/2026-08-07_bilal-wa-more-content-theory.png | Bilal WhatsApp: "since home internet added we went down", "don't delete, more info = results", competitor examples (emiratesharaj, alnuaimigroup), suggests more blogs/links. Tested vs instruments — timeline refuted, competitor probe done. See STATE 08-07 addendum 4 |
| 2026-08-08 | screenshots/2026-08-08_gsc-links-internal-18447.png | GSC Links report: External 23 (trustpilot 20) · **Internal 18,447** — home 4,234 / choose-number 4,225 / numbers 4,162 / silver 3,419 / repeating-digit 1,625. Triggered the "are we spammed?" check. Verified 100% own generator × 4,259 thin pages. See STATE 08-08 (1) |
| 2026-08-08 | screenshots/2026-08-08_gsc-top-linking-text-external.png | GSC "Top linking text" (**external** panel, 23 links total): "golden numbers uae logo", "visit website", "bezoek de website", "siirry verkkosivulle", "visitar o site" — Trustpilot locale variants of one button, not spam anchors. Trustpilot 403s curl+WebFetch so label origin is inference. See STATE 08-08 (3) |
| 2026-08-08 | screenshots/2026-08-08_serp-choose-number-emdash-query.png | Bilal's SERP where our URL is "missing" — query is `—https://…/choose-number/` with a **leading em dash** (chat-paste artifact), so Google ran a literal string search and returned pages *mentioning* the URL (Instagram, blogspot). Not a valid de-indexing test. See STATE 08-08 (4) |
| 2026-08-08 | screenshots/2026-08-08_gbp-posts-scroll1-sept.png … `-scroll4-faq-oct.png` | **GBP Posts queue — 4 scrolls, HEALTHY.** Published: golden-number area posts (Sharjah, Abu Dhabi, Business Bay, Dubai Marina) + wireless (JBR, Business Bay). Scheduled: 13/20/27 Aug · 1/10/18/25 Sept (wireless area series) · 15/19/21 Oct (FAQ series, branded card images, **Call now** CTA). Cadence ~weekly, content mixed, voice compliant (digit-free, no hashtags). ⚠ My scroll-1-only read claimed a "3-week Aug gap" and "wireless-only" — **both WRONG, corrected by scrolls 2-4.** Posts need no work; the parked lever is GBP **Products** (26/76) |
| 2026-08-08 | screenshots/2026-08-08_gsc-page-indexing-refreshed-85.png | **Page Indexing finally refreshed: "Last update 8/5/26"** (was 7/24). Indexed 4.23K / Not indexed 399. Data window ends ON the fix day → contains zero post-fix recrawls; +10/+14 is noise. **Chart is the clearest proof of de-serving yet: indexed bars FLAT ~4.2K through 8/1 while impressions cliff at 7/20 to ~zero.** Also re-shows grey→green corpus flip ~06-06. See STATE 08-08 (6) |
| 2026-08-08 | screenshots/2026-08-08_serp-choose-number-clean-query-RESOLVED.png | **Same query re-run clean: `/choose-number/` is result #1, plus homepage + blog + bur-dubai + al-ain.** Money pages are indexed and servable; em dash was the whole explanation. Proves index presence only — NOT ranking. See STATE 08-08 (4b) |
| 2026-09-06 | screenshots/2026-09-06_chat-widget-live-choose-number.png | **Shipped state of the in-site chat on `/choose-number/`** — cards read "Chat with us", the widget opens with that exact number pre-typed, one bubble bottom-right. Verified against prod (30/30 Playwright checks). Malik's "why is there inquire on WhatsApp?" screenshot that started this is not archived (image cache expired); the before-state is commit `51a03011`, the after is `a41860e8` |

## Pending decisions / open questions

<!-- TODO -->
