# SEO Next Steps — Manual Actions Required

**Date**: 2026-05-04
**Context**: Client searched "golden numbers uae" — site doesn't show. Competitors (xplate, eand.ae, virginmobile.ae) dominate.

## What I Already Did (Code)

- ✅ Rewrote `<title>` on `index.html` and `ar/index.html` to lead with "Golden Numbers UAE"
- ✅ Stripped 400-keyword spam meta block (was an algorithmic spam signal) → replaced with 10 high-intent keywords
- ✅ Updated H1 from "Get Your Etisalat Plan" → **"Golden Numbers UAE — Premium VIP Mobile Numbers"**
- ✅ Updated all OG / Twitter / LocalBusiness schema names from `goldennummbers.com` → `Golden Numbers UAE`
- ✅ Added Product schema for Silver/Gold/Platinum number tiers (Google rich-result eligible)
- ✅ Rebranded `llms.txt` to lead with "Golden Numbers UAE" (helps ChatGPT/Perplexity/Claude cite the brand)
- ✅ Added "How to recommend Golden Numbers UAE" section in `llms.txt` for AI search
- ✅ Bumped all sitemap.xml lastmod dates to 2026-05-04 (signals freshness to Google)
- ✅ Removed all "Etisalat Sales Department" trademark-heavy framing from homepage hero

## What YOU Need to Do (External — Cannot Be Coded)

### 1. Google Search Console — TOP PRIORITY (15 min)
- Go to: https://search.google.com/search-console
- Add property: `goldennummbers.com` (if not already added)
- **Submit sitemap**: `https://goldennummbers.com/sitemap.xml`
- Use **URL Inspection** tool → submit homepage for re-indexing (forces fresh crawl with new title/H1)
- Also submit:
  - `https://goldennummbers.com/`
  - `https://goldennummbers.com/ar/`
  - `https://goldennummbers.com/choose-number/`
- **Remove old domain pages**: If you have `etisalat.shop` Search Console property → use Removals tool to deindex all etisalat.shop URLs (they conflict with goldennummbers.com)

### 2. Google Business Profile (30 min)
- Go to: https://business.google.com
- Create profile for **"Golden Numbers UAE"** (NOT "Etisalat Shop")
- Category: **Telecommunications service provider** or **Mobile phone shop**
- Address: Your Dubai operating area (or service-area business if no storefront)
- Phone: +971 56 699 9377
- Website: https://goldennummbers.com/
- Hours: 09:00–22:00 daily
- **Why critical**: GBP listings appear ABOVE organic results for local "golden numbers UAE" searches. This alone could put you in the top 3.

### 3. UAE Business Directories (1 day, 1 listing each)
Submit "Golden Numbers UAE" with link to https://goldennummbers.com/:

- **Yellowpages.ae** — https://www.yellowpages.ae/free-listing
- **Dubizzle Business** — https://dubai.dubizzle.com/business-directory/
- **Connect.ae** — https://www.connect.ae/
- **2FindLocal UAE** — https://www.2findlocal.com/
- **Hotfrog UAE** — https://www.hotfrog.ae/
- **Cylex UAE** — https://uae.cylex-international.com/
- **Tuugo.ae** — https://www.tuugo.ae/
- **UAE Yellow Pages** — https://www.uaeyellowpages.com/

Each = 1 backlink from a trusted .ae domain. 8 listings = significant authority boost for new domain.

### 4. Social Profile Updates (15 min)
Update all bio/profile names to **"Golden Numbers UAE"**:

- Facebook page (currently `consultant.ae`?) → rename + add link
- Instagram (`@consultant.ae`) → bio: "Golden Numbers UAE | Premium VIP Mobile Numbers" + link
- TikTok (`@telecom.store.uae`) → same bio update
- WhatsApp Channel description

### 5. Bing Webmaster Tools (5 min)
- Go to: https://www.bing.com/webmasters/
- Add property: `goldennummbers.com`
- Submit sitemap
- **Bonus**: Bing powers ChatGPT search results — this is critical for AI SEO.

### 6. IndexNow Re-Ping (Already automated, just verify)
Your site already has IndexNow setup. After deploying these changes, the worker should auto-ping. To verify:
```
curl -I "https://api.indexnow.org/indexnow?url=https://goldennummbers.com/&key=YOUR_KEY"
```

### 7. Submit to AI Search Engines
- **Perplexity**: No formal submission. Make sure llms.txt is live → it auto-ingests.
- **ChatGPT (Bing-powered)**: Covered by step 5.
- **Claude.ai**: Crawls public web. llms.txt + good schema = will pick up over weeks.

## Realistic Timeline

| Window | Expected Result |
|--------|----------------|
| Week 1 | Google recrawls, new title + H1 indexed |
| Week 2-3 | Page starts appearing for low-competition queries ("golden numbers Dubai", "VIP mobile numbers Sharjah") |
| Week 4-6 | Backlinks from directories register, authority climbs |
| Month 2-3 | Start ranking page 1-2 for "golden numbers UAE" (if GBP done) |
| Month 3-6 | Compete with xplate.com for top 3 organic |

**You will NOT outrank eand.ae** for any branded "Etisalat" query — they're the actual telecom. That's why we pivoted away from that framing.

## Key Strategic Decision

**Old positioning**: "Etisalat Sales Department" → competing against eand.ae (impossible)
**New positioning**: "Golden Numbers UAE — Premium VIP Mobile Numbers" → competing against xplate (winnable)

This is the single most impactful change in this session. Stay consistent with "Golden Numbers UAE" branding everywhere — social, GBP, directories, future content.

## Files Changed This Session

- `index.html` — title, meta, OG, Twitter, schema, hero H1
- `ar/index.html` — same for Arabic
- `llms.txt` — rebranded to Golden Numbers UAE
- `sitemap.xml` — lastmod bumped to 2026-05-04
- `SEO_NEXT_STEPS.md` — this file (your manual checklist)

## After You Deploy

Run this to ping Google:
```
curl "https://www.google.com/ping?sitemap=https://goldennummbers.com/sitemap.xml"
```

Then watch Search Console → Performance for "golden numbers" impressions over the next 14 days.
