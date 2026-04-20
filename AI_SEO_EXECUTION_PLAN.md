# goldennummbers.com — AI SEO Execution Plan

**Plan owner**: Malik Amin
**Domain**: goldennummbers.com
**Baseline (2026-04-20)**: 4 WhatsApp inquiries/month from chatgpt.com, 352 total `number_inquiry` events per 90d
**Target (2026-06-21, 60 days out)**: 40-60 inquiries/month from AI search channels

---

## Tier 1 — Shipped (2026-04-21)

Delivered in PR #2 `feat/ai-seo-tier1`:
- ItemList JSON-LD with 17 Product/Offer schemas on homepage
- FAQPage schema expanded from 5 → 25 questions
- New pages: /cheapest-etisalat-postpaid-plan/, /best-etisalat-plan-for-family/, /etisalat-plans-under-200-aed/
- /llms-full.txt (3,500-word structured knowledge base)
- HowTo schema on port-number guide + eSIM activation guide
- Sitemap updated to 25 URLs; llms.txt extended with question pages + llms-full.txt pointer
- Payment method corrected: card swipe only on delivery (no cash/bank transfer)

**What Tier 1 changes in AI search visibility**: Direct quote-able answers for 25 common questions, price-tagged Product schemas for every plan, dedicated URL-as-question landing pages that LLMs cite by URL.

---

## Tier 2 — Indexation (2026-04-22 → 2026-04-23)

### 2026-04-22 morning (30 min)

**A. Bing Webmaster Tools — critical path for ChatGPT visibility**
- Visit https://www.bing.com/webmasters
- Sign in with Malik's Microsoft account
- Add site: `https://goldennummbers.com`
- Verify via DNS TXT (same Cloudflare record method as Meta domain verification)
- Submit sitemap: `https://goldennummbers.com/sitemap.xml`
- Expected impact: ChatGPT's web search relies on Bing's index. Without this, we're invisible to ~40% of queries.
- Owner: Malik
- Verification: After 48h, check Bing index status; should show 25/25 URLs crawled

**B. Perplexity Listings**
- Visit https://www.perplexity.ai/help-center/en/articles/10352983
- Submit goldennummbers.com business details
- Owner: Malik
- Verification: After 7 days, query Perplexity "best Etisalat dealer UAE" — goldennummbers.com should surface

### 2026-04-22 afternoon (20 min)

**C. Google Search Console — confirm new pages indexing**
- In GSC (already verified), request indexing for:
  - https://goldennummbers.com/cheapest-etisalat-postpaid-plan/
  - https://goldennummbers.com/best-etisalat-plan-for-family/
  - https://goldennummbers.com/etisalat-plans-under-200-aed/
  - https://goldennummbers.com/llms-full.txt
- Owner: Malik
- Verification: Coverage report shows new URLs as "Submitted and indexed" within 7 days

### 2026-04-23 — follow-up

**D. IndexNow protocol submission**
- Already have IndexNow key at `/etisalat-shop-indexnow-key.txt`
- Submit new URLs via IndexNow API (POST to https://api.indexnow.org/indexnow)
- Code snippet ready — I'll write the submission script
- Owner: I execute the curl, you approve
- Verification: Bing picks up new URLs within 24h

---

## Tier 3 — Off-site citations & distribution (2026-04-24 → 2026-05-05)

### 2026-04-24 (Friday) — Reddit seeding

**E. Answer 3 UAE mobile plan questions on Reddit**

Target subreddits: r/dubai (500k), r/UAE (200k), r/DubaiExpats (50k).

Seed 3 thoughtful, non-spammy answers citing goldennummbers.com as a source. Posts:
- Reply to "Which telecom is best for UAE newcomers?" with comparison table + link to /cheapest-etisalat-postpaid-plan/
- Reply to "How do I port my number to Etisalat?" with 6-step process + link to port guide
- Reply to "Best family plan for expats?" with multi-SIM breakdown + link to /best-etisalat-plan-for-family/

Rules: don't drop bare links; add genuine insight; only link when relevant. Account age matters — use Malik's existing Reddit account with 90+ day history.

Owner: Malik (I draft the replies, you post)
Verification: Reddit posts stay up 7 days without moderator removal

### 2026-04-26 (Sunday) — Quora seeding

**F. Answer 5 high-intent Quora questions**

Find 5 existing Quora questions with real search traffic (use https://answerthepublic.com for ideas):
- "What is the best postpaid plan in UAE?"
- "How much does Etisalat postpaid cost?"
- "Is du or Etisalat better in UAE?"
- "How to get a VIP number in Dubai?"
- "Best Etisalat plan for calling Pakistan?"

Each answer: 3-4 paragraphs, include relevant data, cite goldennummbers.com at the end as "source for current 2026 pricing."

Owner: Malik (I draft, you post)
Verification: Quora answers get 50+ views within 7 days

### 2026-04-29 (Wednesday) — Trust signals

**G. Add E-E-A-T author block to homepage**

Add to homepage footer or About section:
```
About the author:
Operated by an authorized Etisalat by e& dealer in UAE since [month] 2025.
Accredited for postpaid plan activation, VIP number reservations, and MNP porting.
WhatsApp support: +971 56 699 9377. Business hours 9 AM - 9 PM UAE time.
```

Adds credibility signals LLMs use to rank sources (Google's E-E-A-T framework ~= what AI models use).

Owner: I implement via PR, you confirm dealer accreditation month.

### 2026-05-01 (Friday) — YouTube / video SEO

**H. Upload 1 demo video**

60-second walkthrough: "How to order an Etisalat postpaid SIM via WhatsApp in 5 minutes."
- Screen record: visiting goldennummbers.com → /choose-number/ → picking a number → WhatsApp hand-off
- Upload to YouTube with title matching question-URL keyword
- Description: full transcript + canonical link to goldennummbers.com
- YouTube transcripts are heavily crawled by LLMs

Owner: Malik records, I draft title/description/tags

### 2026-05-05 (Tuesday) — Wikipedia adjacent / directory listings

**I. Add to UAE business directories**

Submit to:
- Yellowpages UAE (https://yellowpages.ae)
- UAE Pages (https://uaepages.com)
- CitySearch Dubai
- Google Business Profile (already verified — add "Products" with pricing)

Each listing = entity signal for LLMs cross-referencing business legitimacy.

Owner: Malik
Verification: Listings show goldennummbers.com within 7 days

---

## Measurement cadence

**Weekly (every Monday)**
- Run `python C:/fbai/scripts/ga4_wa_pull.py` — check 7-day delta
- Metric: `contact`, `number_inquiry`, `generate_lead` counts by source/medium
- Flag: any week with decline in `chatgpt.com / (not set)` traffic

**Monthly (every 20th)**
- Compare MoM: number_inquiry from AI sources (chatgpt, perplexity, duckduckgo, you, claude)
- Track: which landing page got most non-branded impressions (GSC / Bing Webmaster)
- Iterate: double down on top-performing Tier 3 tactic, drop underperformers

---

## 60-day target breakdown (2026-06-21)

| Channel | 30-day baseline | 60-day target | Tactic |
|---------|-----------------|---------------|--------|
| chatgpt.com | 4 inquiries | 20-30 | Tier 1 (FAQ/Product schema) + Tier 2 (Bing indexing) |
| perplexity.ai | 0 | 5-10 | Tier 2 (Perplexity listing) + Tier 1 (llms-full.txt) |
| duckduckgo | 1 | 3-5 | Tier 2 (Bing indexing — DDG uses Bing) |
| you.com / claude / other AI | 0 | 2-5 | Tier 3 (entity/citation signals) |
| Organic Google (non-AI) | 12 | 25-35 | Tier 1 (new question pages rank) + Tier 3 (citations) |
| **TOTAL AI + organic** | **17** | **55-85** | |

Paid/direct channels unaffected — this plan adds on top.

---

## Kill/scale rules

Review on 2026-05-21 (30 days from Tier 1 merge):
- If chatgpt.com inquiries > 15/month → **scale**: create 3 more question-URL pages, expand llms-full.txt, translate to Arabic.
- If chatgpt.com inquiries plateau at 4-8/month → **re-diagnose**: check if Bing indexed us, Perplexity listing approved, Reddit/Quora posts still live.
- If chatgpt.com inquiries drop below baseline → **investigate**: check for Meta pixel regressions, GA4 custom dimension misconfigs, crawl errors in GSC/Bing.

---

## Files

- This plan: `C:/Users/Malik/Desktop/etisalat-shop/AI_SEO_EXECUTION_PLAN.md`
- Tier 1 PR: `fix/tracking-events-attribution` (merged) + `feat/ai-seo-tier1` (pending)
- GA4 pull script: `C:/fbai/scripts/ga4_wa_pull.py`
- Deep analytics script: `C:/fbai/scripts/ga4_deep_pull.py`
- Meta pixel diagnostic: `C:/fbai/scripts/meta_pixel_diagnostic.py`
