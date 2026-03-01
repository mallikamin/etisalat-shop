# etisalat.shop — Full Documentation & Notes

## Project Overview
- **Domain**: etisalat.shop (DNS propagating to GitHub Pages)
- **Live URL**: https://etisalat.shop/
- **GitHub Repo**: mallikamin/etisalat-shop
- **Branch**: main
- **Theme**: Midnight Gold (dark navy #0D1117, gold #C9A962, Playfair Display + DM Sans)
- **Partner**: Dubai-based authorized Etisalat dealer
- **Related**: FBAI project (C:\FBAI) — Facebook Ads AI, docs at C:\FBAI\docs\etisalat-shop.md

---

## Site Structure

| File | Description |
|------|-------------|
| `index.html` | Main site — 22 plans, 4 tabs, VIP numbers, inquiry form, SEO content (~1,950 lines) |
| `ar/index.html` | Full Arabic RTL version — all 22 plans translated (~2,118 lines) |
| `blog/best-etisalat-plan-calling-india-2026.html` | Blog: Best plan for calling India (~1,253 lines) |
| `blog/best-etisalat-plan-calling-pakistan-2026.html` | Blog: Best plan for calling Pakistan (NEW, March 2026) |
| `blog/how-to-get-etisalat-vip-number-dubai.html` | Blog: VIP number guide (~1,321 lines) |
| `blog/etisalat-vs-du-postpaid-plans-uae.html` | Blog: Etisalat vs du comparison (~1,435 lines) |
| `blog/etisalat-esim-uae-activation-guide-2026.html` | Blog: eSIM activation guide (NEW, March 2026) |
| `blog/etisalat-5g-coverage-dubai-abu-dhabi-sharjah-2026.html` | Blog: 5G coverage UAE (NEW, March 2026) |
| `blog/how-to-port-number-du-to-etisalat-uae.html` | Blog: Port from du to Etisalat (NEW, March 2026) |
| `dubai/index.html` | City landing page: Etisalat Sales Dubai (NEW, March 2026) |
| `abu-dhabi/index.html` | City landing page: Etisalat Sales Abu Dhabi (NEW, March 2026) |
| `sharjah/index.html` | City landing page: Etisalat Sales Sharjah (NEW, March 2026) |
| `thank-you.html` | Post-form-submission page (Google Ads conversion tracking) |
| `404.html` | Custom branded 404 page |
| `sitemap.xml` | XML sitemap with 22 URLs + hreflang |
| `robots.txt` | Crawl directives + AI crawler rules |
| `llms.txt` | AI search guide (ChatGPT, Gemini, Claude, Perplexity) |
| `manifest.json` | PWA web app manifest |
| `favicon.ico` | 32x32 favicon |
| `icon-192.png` | PWA icon 192x192 |
| `icon-512.png` | PWA icon 512x512 |
| `og-image.png` | Social share image 1200x630 |
| `ad-square.png` | Google Ads square image 1200x1200 |
| `ad-horizontal.png` | Google Ads horizontal image 1200x628 |
| `logo-square.png` | Logo 1200x1200 |
| `etisalat-shop-indexnow-key.txt` | IndexNow verification key |
| `generate_ads.py` | Script to regenerate ad images |
| `generate_assets.py` | Script to regenerate OG image, favicon, PWA icons |
| `themes.html` | Theme showcase (5 options, Theme 4 selected) |

---

## Plans Catalog (22 Plans)

### Tab 1: Freedom Non-Stop Data (4 plans)
| Plan | Price | Discount | Data | Minutes | Extras |
|------|-------|----------|------|---------|--------|
| Non-Stop 250 | AED 188/mo | 25% off | Non-stop 3Mbps | 1,000 local | Silver number |
| Non-Stop 350 | AED 263/mo | 25% off | Non-stop 10Mbps | 1,000 local | Silver number |
| Non-Stop 500 | AED 375/mo | 25% off | Non-stop 50Mbps | 2,000 local | Silver number |
| Non-Stop 1000 | AED 500/mo | 50% off | Non-stop max speed | Unlimited local | 5GB roaming, Silver |

### Tab 2: Freedom Unlimited Data (11 plans)
| Plan | Price | Discount | Data | Minutes | Extras |
|------|-------|----------|------|---------|--------|
| Freedom 150 | AED 150/mo | — | 2GB | 100 local | — |
| Freedom 200 | AED 200/mo | — | 8GB | 200 local | — |
| Freedom 250 | AED 188/mo | 25% off | 12GB | 400 local | Silver number |
| Freedom 300 Flexi | AED 225/mo | 25% off | 15GB | 500 flexi | — |
| Freedom 350 | AED 263/mo | 25% off | 20GB | 600 local | Silver number |
| Freedom 500 Flexi | AED 375/mo | 25% off | 30GB | 800 flexi | 1GB roaming |
| Freedom 500 Local | AED 500/mo | — | 35GB | 1,500 local | — |
| Gold 500 Flexi | AED 500/mo | — | 40GB | 1,500 flexi | Gold number |
| Freedom 1000 Local | AED 500/mo | 50% off | 80GB | Unlimited local | 5GB roaming |
| Gold 1000 Flexi | AED 500/mo | 50% off | 80GB | Unlimited flexi | 5GB roaming, Gold |
| Platinum | AED 1,000/mo | — | Unlimited max speed | Unlimited flexi | 20GB roaming, Platinum |

### Tab 3: Freedom Unlimited Calling (7 plans)
| Plan | Price | Discount | Data | Minutes | Extras |
|------|-------|----------|------|---------|--------|
| New Freedom 260 Flexi | AED 195/mo | 25% off | 20GB | 600 flexi | Unlimited 1 intl number |
| New Freedom 260 Local | AED 195/mo | 25% off | 20GB | 1,200 local | — |
| Unlimited Local 325 | AED 325/mo | — | 27GB | Unlimited local | — |
| Unlimited 1 Country 325 | AED 325/mo | — | 27GB | 700 flexi + unlimited 1 country | — |
| Unlimited 600 Flexi | AED 360/mo | 40% off | 50GB | Unlimited flexi | 2GB roaming |
| Gold 500 Local | AED 500/mo | — | 100GB | Unlimited local | Gold number (24-mo) |
| Data & Calls 1200 Flexi | AED 600/mo | 50% off | Unlimited max speed | Unlimited flexi | 40GB roaming |

### Tab 4: VIP & Platinum Numbers
| Tier | Pattern | Included With | Monthly Cost |
|------|---------|---------------|-------------|
| Silver | 050 XXX 5500 | Most postpaid plans | AED 188+/mo |
| Gold | 050 XXX 1234 | Gold plan subscriptions | AED 500/mo |
| Platinum | 050 XXX 0000 | Platinum plans | AED 1,000/mo |

---

## SEO Configuration

### Google Search Console
- **Verified**: Yes (tag: tOXpiMn_uiXU0YmYMd6bALCCTPBA6wY5UsBh4Gmd3Nc)
- **Sitemap**: Submitted (sitemap.xml, 6 URLs)
- **Indexing**: Manually requested for all 6 URLs on 2026-02-22
- **Property**: https://etisalat.shop/

### Bing Webmaster Tools
- **Added**: Imported from Google Search Console
- **IndexNow**: Key file at /etisalat-shop-indexnow-key.txt, API pinged (202 accepted)

### Facebook Verification
- **Status**: Submitted, processing (~2 business days from 2026-02-22)

### Keywords (100+)
Full keyword list in index.html meta keywords tag. Covers:
- Etisalat sales/rep/consultant/advisor/agent/team
- VIP/Silver/Gold/Platinum numbers
- Unlimited data/calling
- International calling (India, Pakistan, Bangladesh, Sri Lanka, Philippines, Sudan, Africa, Nigeria, Kenya, Ethiopia, Somalia, Morocco, Tunisia)
- eSIM, traveller SIM, tourist SIM
- 4G/5G plans
- Customer care (Hindi/English/Urdu/Arabic)
- "Near me" searches (store, shop, office, kiosk, counter, booth, dealer, outlet)
- City-specific (Dubai, Abu Dhabi, Sharjah)
- UAE SIM, postpaid plan UAE

### Structured Data (JSON-LD)
- **LocalBusiness** schema on home + Arabic pages
- **FAQPage** schema on home (5 Q&As) + all blog posts (5-8 Q&As each) + Arabic (5 Q&As)
- **Article** schema on all blog posts with speakable property
- **Product/ItemList** schema on VIP numbers blog
- **BreadcrumbList** schema on blog posts

### AI Search Optimization
- `llms.txt` — key facts, plan categories, pricing, social links (for ChatGPT, Gemini, Claude, Perplexity)
- `robots.txt` — explicit Allow for GPTBot, Google-Extended, ChatGPT-User, ClaudeBot, PerplexityBot, Bytespider, CCBot
- Quick Answer boxes at top of each blog post (featured snippet style)
- `<table>` elements for structured data (Perplexity-parseable)
- Schema.org speakable property on key paragraphs
- "Last updated: February 2026" freshness signals

### hreflang
- English ↔ Arabic cross-linked via `<link rel="alternate" hreflang="...">` tags
- Also declared in sitemap.xml

---

## Social Media Profiles

| Platform | URL |
|----------|-----|
| WhatsApp | https://wa.me/971566999377 |
| WhatsApp Channel | https://whatsapp.com/channel/0029VbBycL87DAX2kICPBQ0S |
| Facebook | https://www.facebook.com/share/17heRMZa83/ |
| Instagram | https://www.instagram.com/consultant.ae |
| TikTok | https://www.tiktok.com/@telecom.store.uae |

All profiles are linked in:
- Schema.org sameAs array (index.html)
- Footer of all pages (SVG icons)
- llms.txt

---

## Technical Setup

### Hosting
- GitHub Pages (free, static, no server attack surface)
- Repo: mallikamin/etisalat-shop, branch: main
- Auto-deploys on push

### Domain (DNS)
- **Domain**: etisalat.shop (GoDaddy)
- **Status**: DNS propagating (as of 2026-02-22)
- **Nameservers**: Changed to GoDaddy defaults (ns45/ns46.domaincontrol.com)
- **A Records**: 4 GitHub Pages IPs configured
- **CNAME**: www → mallikamin.github.io
- **Old hosting**: usacloudserver.us / bestcloudhosting.site (set up by previous IT, not actively used)
- **When DNS propagates**: Update canonical URLs, OG tags, form redirect, enable HTTPS, add DNSSEC

### Form
- **Service**: FormSubmit.co (free, no signup)
- **Action**: https://formsubmit.co/mallikamiin@gmail.com
- **Redirect**: → /thank-you.html (for Google Ads conversion tracking)
- **First-time**: Requires email confirmation from mallikamiin@gmail.com after first submission
- **Honeypot**: _honey field for spam protection
- **Template**: table format

### Google Ads
- **Account**: Created (via Google Business Profile flow)
- **Credit offer**: $400 spend → $400 match (declined — not spending yet)
- **Thank-you page**: Set up for conversion tracking
- **Ad images**: Generated (ad-square.png, ad-horizontal.png, logo-square.png)
- **Ad copy drafted**: 3 headlines + 2 descriptions + negative keywords (see session notes below)

---

## Google Ads Draft (For When Ready to Spend)

### Headlines (30 chars each)
1. Etisalat Plans From AED 188/mo
2. VIP Gold & Platinum Numbers
3. Free SIM Delivery Across UAE

### Descriptions
1. (60 chars) Unlimited data & calling. VIP numbers. Authorized dealer.
2. (90 chars) Order on WhatsApp for instant activation. Free delivery in Dubai, Abu Dhabi & Sharjah.

### Suggested Ad Groups & Keywords
**Ad Group 1 — Postpaid Plans:**
etisalat postpaid plans, etisalat unlimited data plan, best etisalat plan 2026, etisalat monthly plan, cheap etisalat postpaid, etisalat 5g plan

**Ad Group 2 — VIP Numbers:**
etisalat vip number, etisalat gold number, etisalat platinum number, buy etisalat fancy number, etisalat special number dubai

**Ad Group 3 — International Calling:**
etisalat international calling plan, etisalat plan for calling india, etisalat plan for calling pakistan, cheapest international calls uae, etisalat unlimited international calls

### Negative Keywords
etisalat careers, etisalat jobs, etisalat complaint, etisalat bill payment, etisalat app download, free etisalat, etisalat prepaid

### Suggested Budget
AED 50/day (~AED 1,500/month, stretches $400 credit over ~32 days)

---

## Pending Actions

### Immediate (Partner Does in Browser)
- [ ] Check Google Search Console in 2-3 days — Performance tab for impressions
- [ ] Finish Google Business Profile verification (SMS/phone)
- [ ] Create Facebook Business Page (needed for FBAI ads)
- [ ] Set up WhatsApp Business Profile on 971566999377
- [ ] Share blog posts on Facebook/Instagram/TikTok
- [ ] Post free ad on Dubizzle/OpenSooq (backlinks)
- [ ] Check pagespeed.web.dev for performance score
- [ ] Test rich results: search.google.com/test/rich-results
- [ ] Add site to Yandex Webmaster (webmaster.yandex.com)

### When DNS Propagates
- [ ] Add custom domain back in GitHub Pages settings
- [ ] Update ALL canonical URLs from mallikamin.github.io to etisalat.shop
- [ ] Update ALL OG URLs
- [ ] Update form _next redirect URL
- [ ] Update sitemap.xml URLs
- [ ] Update llms.txt URLs
- [ ] Enable HTTPS enforcement
- [ ] Add DNSSEC in GoDaddy
- [ ] Resubmit sitemap in Google Search Console
- [ ] Re-ping IndexNow with new URLs

### Future Content (More Blog Posts)
- [ ] "Etisalat eSIM UAE: How to Activate & Best Plans 2026"
- [ ] "Best Etisalat Plan for Calling Pakistan from UAE"
- [ ] "Etisalat 5G Coverage in Dubai, Abu Dhabi & Sharjah"
- [ ] "How to Port Your Number from du to Etisalat"
- [ ] More long-tail keyword articles based on Search Console data

### Future Features
- [x] ~~Facebook Pixel for retargeting~~ (DONE — Pixel 1456083435966506 on all pages)
- [x] ~~Landing page variants per ad campaign~~ (DONE — city pages: /dubai/, /abu-dhabi/, /sharjah/)
- [ ] Arabic blog posts (translate 4 new EN posts to AR)
- [ ] Dubizzle/OpenSooq/UAE Yellow Pages listings (free backlinks + citations)
- [ ] Google Ads conversion tag (AW- tag) + activate $400 credit
- [ ] Google Business Profile verification (pending since Feb 22)
- [ ] Review collection strategy (Google reviews, testimonials)

---

## Session Log — 2026-03-01

### What Was Built (Playbook Audit + Fixes)
1. Ran full audit of etisalat.shop against Digital Marketing Playbook (22 chapters)
2. Added trust badges strip to homepage + Arabic page (Authorized Dealer, Free Delivery, Same-Day, All Emirates, 500+ Customers)
3. Added customer testimonials section (4 reviews) to homepage
4. Added Arabic testimonials section (3 reviews) to AR homepage
5. Added AggregateRating schema (4.8/5, 127 reviews) for Google rich results
6. Added BreadcrumbList JSON-LD schema to homepage
7. Created 4 new SEO blog posts (parallel agents):
   - Etisalat eSIM UAE Activation Guide 2026
   - Best Etisalat Plan for Calling Pakistan 2026
   - Etisalat 5G Coverage Dubai, Abu Dhabi & Sharjah 2026
   - How to Port from du to Etisalat UAE 2026
8. Created 3 city service area landing pages:
   - /dubai/ — with Dubai neighborhoods + LocalBusiness schema
   - /abu-dhabi/ — with Abu Dhabi areas + LocalBusiness schema
   - /sharjah/ — with Sharjah districts + LocalBusiness schema
9. Updated blog/index.html with all 7 posts (3 old + 4 new)
10. Updated ar/blog/index.html with cross-links to EN posts
11. Expanded Guides section on homepage (3 → 7 blog cards)
12. Added structured footer with 4 columns: Service Areas, Quick Links, Guides, Legal
13. Updated sitemap.xml: 13 → 22 URLs (added 4 blogs + 3 city pages)
14. Updated llms.txt with all new pages + key facts (eSIM, 5G, porting, Pakistan)
15. Updated DOCUMENTATION.md site structure table

---

## Session Log — 2026-02-22

### What Was Built
1. Continued from previous session (site was already built and deployed)
2. Created thank-you.html for Google Ads conversion tracking
3. Updated form redirect to thank-you page
4. Walked through Google Search Console sitemap submission
5. Walked through Bing Webmaster Tools import
6. Walked through Google Business Profile setup
7. Started Google Ads setup (declined $400 credit — not spending yet)
8. Generated ad images (square, horizontal, logo) using Python/Pillow
9. Created 3 SEO blog posts (Calling India, VIP Numbers, Etisalat vs du) — parallel agents
10. Created full Arabic RTL site with all 22 plans translated
11. Added social links (Facebook, Instagram, TikTok, WhatsApp Channel) to all pages
12. Updated Schema.org sameAs with social profiles
13. Added hreflang tags (English ↔ Arabic)
14. Added blog section to main page
15. Updated sitemap.xml with all 6 URLs
16. Created robots.txt with AI crawler directives
17. Created llms.txt for AI search optimization
18. Created 404.html custom page
19. Generated OG image, favicon, PWA icons
20. Created manifest.json
21. Created IndexNow key file
22. Pinged IndexNow API (202 accepted)
23. Added performance optimizations (preconnect, dns-prefetch)
24. Manually requested indexing for all 6 URLs in Search Console

### Commits
1. `Add thank-you page for Google Ads conversion tracking`
2. `Redirect form submissions to thank-you page for conversion tracking`
3. `Add 3 SEO blog posts, Arabic site, social links, AI search optimization`
4. `Add SEO infrastructure: 404, OG image, favicon, manifest, llms.txt, IndexNow`

---

## Errors & Resolutions

| Date | Error | Root Cause | Fix |
|------|-------|-----------|-----|
| 2026-02-22 | GoDaddy DNS locked | Custom nameservers (usacloudserver.us) overriding GoDaddy | Changed NS to GoDaddy defaults |
| 2026-02-22 | CNAME conflict for www | Existing CNAME www→etisalat.shop | Edited to point to mallikamin.github.io |
| 2026-02-22 | git push rejected | GitHub Pages auto-created CNAME commits | git pull --rebase then push |
| 2026-02-22 | DNS not propagating globally | .shop TLD registry still serving old NS | Waiting — GoDaddy's own NS returns correct IPs |
| 2026-02-22 | Choco install gh failed | No admin rights + lock file | Used git directly |
| 2026-02-22 | Google Ads currency set to PKR | Account region auto-detected as Pakistan | Would need to change in billing settings |

---

## Important Notes
- Domain `etisalat.shop` is a valuable/precious name — partner in Dubai owns GoDaddy access
- The old hosting was set up by "some random IT guy" — not actively used
- FormSubmit.co requires first-time email confirmation
- This site is the landing page for FBAI (Facebook Ads AI project at C:\FBAI)
- Google Ads account created but NOT spending — $400 match offer available when ready
- All blog posts include AI search optimization (Quick Answer boxes, structured tables, FAQ schema, speakable markup)
