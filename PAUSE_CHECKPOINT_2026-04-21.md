# Pause Checkpoint — 2026-04-21

## Session scope
Ad performance analysis → Fix GA4/Meta tracking gaps → AI SEO Tier 1 execution → Bing Webmaster setup

---

## What was shipped (merged to main)

### PR #1: `fix/tracking-events-attribution` — merged 2026-04-20
- Shared helper `/assets/tracking.js` with `GN.trackWhatsAppClick`, `trackNumberInquiry`, `trackLead`, `trackPartnerScan`, `setUserIdentity`, `genEventId`
- Fixed broken GA4 param `value: <string>` on `number_inquiry` → now uses `number_id` / `number_category` (queryable)
- All pixel Contact/Lead events get unique `eventID` + `value: 500 AED` + `currency: AED` for dedup + AEM weight
- Manual Advanced Matching on form submit (name, phone, email → hashed by Meta)
- 17 pages migrated to shared helper (homepage, choose-number, 3 cities, emirati, thank-you, ar/index, 7 English blogs, 2 Arabic blogs)

### PR #2: `feat/ai-seo-tier1` — merged 2026-04-21
- Homepage `ItemList` JSON-LD with 17 Product/Offer schemas
- Homepage `FAQPage` schema grown 5 → 25 natural-language questions
- 3 new question-URL landing pages:
  - `/cheapest-etisalat-postpaid-plan/` (1,800 words, schemas)
  - `/best-etisalat-plan-for-family/` (1,800 words)
  - `/etisalat-plans-under-200-aed/` (1,500 words)
- `HowTo` schema on `/blog/how-to-port-number-du-to-etisalat-uae.html`
- `HowTo` schema on `/blog/etisalat-esim-uae-activation-guide-2026.html`
- `/llms-full.txt` (3,500-word LLM knowledge base)
- `/llms.txt` extended with question-URL pointers + payment note (card swipe only)
- `/sitemap.xml` → 25 URLs at priority 0.9

### Direct commits to main (verification artifacts)
- `BingSiteAuth.xml` — Bing Webmaster ownership token (`FB75C28E2BBCE9DF7516EC8D1093DAD5`)
- `2799c8ccc52e4ff1802fd861357e38cd.txt` — Bing-generated IndexNow key file

---

## Bing Webmaster Tools state

- Property: `https://goldennummbers.com` — **Verified ✅** (via XML file)
- Sitemap: `https://goldennummbers.com/sitemap.xml` — **Submitted, 23 URLs discovered**
- IndexNow key: `2799c8ccc52e4ff1802fd861357e38cd` (hex-compliant, hosted at root)
- Submissions pushed: **24 URLs at HTTP 202** (programmatic via `api.indexnow.org`)
- Legacy file `etisalat-shop-indexnow-key.txt` still at root (harmless, can delete later)
- Dashboard data will populate within 48h

Old Bing property `https://mallikamin.github.io/etisalat-shop/` still exists in the dashboard — harmless (GitHub Pages URL returns 404 since CNAME redirect is active). Can delete when convenient.

---

## Meta / Facebook state

| Item | Status | Notes |
|------|--------|-------|
| Long-lived token | ✅ Valid until 2026-06-02 | In `C:/fbai/.env` as `META_ACCESS_TOKEN` |
| goldennummbers.com domain verification | ✅ Done | Business "Etisalat" (ID 281900244999301) |
| AEM (Aggregated Event Measurement) priority events | ⚠️ PAUSED | Pending — needs 8-slot priority config with Contact at slot 1 |
| Pixel Contact events firing | ✅ Live (confirmed many/hour) | Events reach pixel; ad attribution pending AEM |
| Pixel `offsite_conversion.fb_pixel_contact` attribution | ❌ Still 0 in ad insights | Will start flowing after AEM priority set |
| Manual Advanced Matching code | ✅ Shipped via PR #1 | Will clear Diagnostics warning in 24-48h |
| Allow list | ✅ Set (goldennummbers.com + etisalat.shop) | |
| Automatic Advanced Matching | ✅ On (11 match fields) | |

---

## GA4 state

- Property ID: `525472644` (measurement ID `G-G34631QW03`)
- Service account: `ga4-reader@fbai-analytics.iam.gserviceaccount.com` (credentials at `C:/fbai/.creds/ga4-sa.json`)
- Data API: Enabled in project `fbai-analytics`
- Custom dimensions registered (user confirmed): `cta_context`, `event_id`, `interest_type`, `lead_token`, `number_id`, `number_category`, `page_context`, `ref_code`
- **Still missing in GA4**: `lead_source` (flag to register)

Last 30d baseline:
- 144 `number_inquiry` events (91% UAE, 96% mobile, 66% from paid FB/IG)
- 12 `contact` events (4 direct, 3 chatgpt, others)
- 163 total website→WhatsApp redirects

---

## Current live ad campaigns (Client 1 Etisalat.shop, `act_3210518205787184`)

As of 2026-04-20: 11 active, 49 paused.
- 6 × LINK_CLICKS → goldennummbers.com/choose-number/ (~3.70 AED/day each)
- 4 × OUTCOME_ENGAGEMENT (post boosts, 3.69-10 AED/day)
- 1 × MESSAGES (15 AED/day, started 2026-04-20, no spend yet)

Performance insight: engagement post boosts drive convos at **1.87 AED** vs LINK_CLICKS at **11.56 AED** (6× gap).

Analysis scripts:
- `C:/fbai/scripts/check_live_status.py` — current campaign state + 30d perf
- `C:/fbai/scripts/wa_redirects_from_site.py` — ad-driven WA redirect analysis
- `C:/fbai/scripts/ga4_wa_pull.py` — GA4 WA events
- `C:/fbai/scripts/ga4_deep_pull.py` — source/device/page breakdowns
- `C:/fbai/scripts/meta_pixel_diagnostic.py` — pixel health + attribution gaps
- `C:/fbai/scripts/verify_and_submit.py` — IndexNow + Bing ping

---

## Resume priorities (next session — pick top-down)

### 1. Finish Meta AEM setup (blocks ad→site→WA attribution)
- Path: https://business.facebook.com/wa/manage/home/?business_id=281900244999301 (or manually: Events Manager → Etisalat Shop Pixel → find "Aggregated Event Measurement" section)
- Set 8-slot priority: **Contact → Lead → CompleteRegistration → ViewContent → Search → InitiateCheckout → AddToCart → PageView**
- Then re-run `C:/fbai/scripts/meta_pixel_diagnostic.py` in 48h to confirm `offsite_conversion.fb_pixel_contact` starts flowing

### 2. GA4 — register `lead_source` custom dimension
- Admin → Custom Definitions → Custom Dimensions → Create: Event-scoped, parameter `lead_source`

### 3. Perplexity Listings submission (AI SEO Tier 2 continued)
- https://www.perplexity.ai/help-center/en/articles/10352983

### 4. GSC "Request Indexing" for 3 new pages (if not done)
- https://search.google.com/search-console → inspect each new URL → Request Indexing

### 5. Tier 3 content seeding (scheduled 2026-04-24 onwards per AI_SEO_EXECUTION_PLAN.md)
- Reddit answers on r/dubai, r/UAE, r/DubaiExpats (3 posts)
- Quora answers (5 questions)
- E-E-A-T author block
- YouTube demo video
- UAE business directories

### 6. Strategic ad reallocation (paused, not touched yet)
- Kill 3 worst-performing LINK_CLICKS campaigns
- Scale top engagement post boosts
- See analysis section of earlier session output (175 convos @ 1.87 AED on engagement vs 25 convos @ 11.56 AED on LINK_CLICKS)

---

## Measurement cadence

**Weekly (every Monday)**
Run: `python C:/fbai/scripts/ga4_wa_pull.py`
Metric: 7-day delta on `contact`, `number_inquiry`, `generate_lead` counts by source/medium
Flag: any decline in `chatgpt.com / (not set)` traffic

**30-day review: 2026-05-21**
Apply kill/scale rules from `AI_SEO_EXECUTION_PLAN.md`:
- If chatgpt.com > 15/mo → scale (3 more question pages + Arabic translations)
- If plateau at 4-8/mo → re-diagnose (Bing indexing, Perplexity, Reddit posts live?)
- If below baseline → investigate pixel regression or GA4 misconfig

**60-day target: 2026-06-21**
17 → 55-85 monthly inquiries total across AI search + organic.

---

## Critical credentials reference

| System | Key/ID | Location |
|--------|--------|----------|
| Meta access token | `META_ACCESS_TOKEN` | `C:/fbai/.env` (expires 2026-06-02) |
| Meta ad account (client 1) | `act_3210518205787184` | |
| Meta pixel ID | `1456083435966506` | Named "Etisalat Shop Pixel" |
| Meta business ID | `281900244999301` | Named "Etisalat" |
| GA4 property | `525472644` | Measurement ID: `G-G34631QW03` |
| GA4 service account | `ga4-reader@fbai-analytics.iam.gserviceaccount.com` | Key at `C:/fbai/.creds/ga4-sa.json` |
| Bing verification token | `FB75C28E2BBCE9DF7516EC8D1093DAD5` | At `/BingSiteAuth.xml` |
| IndexNow API key (active) | `2799c8ccc52e4ff1802fd861357e38cd` | At `/2799c8ccc52e4ff1802fd861357e38cd.txt` |
| WhatsApp business number | `+971 56 699 9377` | |
| TikTok pixel ID | `D7J1GQRC77UDQGOITA8G` | |

---

## Repo status

- Branch: `main`, up to date with origin
- Recent commits:
  - `50d618f` Add Bing-generated IndexNow API key
  - `a3a6980` Add Bing Webmaster Tools site verification token
  - `505a098` AI SEO Tier 1 (#2)
  - `764c897` Fix GA4/Meta pixel attribution for WhatsApp redirects (#1)
  - `dd0b9ba` Wire full TikTok funnel events (prior session)
- No open PRs
- No uncommitted changes to code (some untracked non-code files: `CHECKPOINT_*.md`, `PAUSE_CHECKPOINT_*.md`, zoop-* HTMLs, desktop artifacts)

---

## Open questions for resume

1. Meta AEM — why was it paused? User said "lets pause the Events management thing" — was it a UI blocker or intentional deprioritization?
2. Does existing Google Search Console have goldennummbers.com verified? (If yes, path to request-indexing is 1 click. If not, we need another DNS TXT.)
3. Is there a reason to keep the old `etisalat-shop-indexnow-key.txt` file around, or delete it?
4. Strategic decision pending: kill/scale current ad campaigns based on cost/convo gap (175 convos @ 1.87 AED vs 25 @ 11.56 AED).
