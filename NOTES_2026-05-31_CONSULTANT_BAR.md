# Notes — Etisalat Authorized Consultant bar + logo + schema (2026-05-31)

## What shipped
Added a site-wide **Authorized Consultant top bar** (logo + tagline) and an
**Organization JSON-LD with logo** to the 35 main customer pages, and patched the
number-page generator so future regens carry the same.

- **Bar content:** `etisalat by e&` logo (white chip) + tagline
  *"Etisalat Authorized Consultant · Postpaid Plans · VIP Gold & Platinum Numbers · Free Delivery Across UAE"*.
- **Logo asset:** `/etisalat-logo.png` — image #5 (`etisalat by e&` horizontal lockup),
  whitespace-trimmed to 540×156, rendered as a white rounded chip (22px desktop / 17px mobile)
  so the red/black mark reads cleanly on the dark bar.
- **Schema:** `Organization` block before `</head>` with `logo`/`image` = `logo-square.png`
  (the Golden Numbers UAE brand — correct for `Organization.logo`, since the entity is the shop,
  not Etisalat), `slogan`, and `alternateName: "Etisalat Authorized Consultant"`.

## How it's built (so it doesn't break again)
- The bar is **`position:fixed; top:0; z-index:2147483000`**. A tiny inline script measures the
  bar's rendered height and sets `--ec-bar-h` + `body.paddingTop` to it, then CSS offsets the page
  nav: `.navbar, body>nav, .nav { top: var(--ec-bar-h) }`.
- **Why:** the homepage/choose-number/emirati/ar navbars are `position:fixed` over the hero with no
  body padding. The first attempt injected the bar in normal flow → the fixed navbar painted over it
  (overlap bug). The measured-offset approach handles BOTH fixed navbars and sticky navs
  (dubai/sharjah/abu-dhabi/blogs/etc. use `position:sticky` and were already fine), and self-corrects
  when the tagline wraps on mobile.
- Verified with real Playwright screenshots (home desktop + mobile, dubai desktop) before shipping —
  see `_files/2026-05-31/shot-*.png`.

## Scope
- **In:** 35 hand-built customer pages (homepage, choose-number, cities, about, premium-numbers,
  etisalat-postpaid-plans-dubai, 3 question pages, legal, thank-you, 404, blogs EN+AR).
- **Out (by request):** the 3,366 generated `numbers/*` pages were NOT regenerated (a regen also
  re-syncs inventory from Google Sheets). The generator template **was** patched, so the next
  intentional regen picks up the bar + schema. Number pages use a sticky `.nav`, so the bar renders
  fine there with no fixed-overlap issue.
- **Excluded:** internal artifacts (zoop-*, speeddrive, eid-*, themes, print/banner mockups,
  partner-portal, partner-tracking-api, whatsapp-catalog).

## Mechanics / deploy
- Injector: `_files/2026-05-31/inject_consultant_bar.py` — idempotent, replaces any prior bar
  (markers `<!-- ec-bar -->`/`<!-- /ec-bar -->`), safe to re-run.
- Generator patched: `generate_number_pages.py` (both `page_html` and `hub_index_html` templates).
- Deploy: Cloudflare Workers static assets — `npx wrangler deploy` from repo root, with
  `CLOUDFLARE_API_TOKEN` loaded from `C:\FBAI\.env`. Live on https://goldennummbers.com/.

## Possible follow-ups
- Arabic pages currently show the English tagline.
- If desired, point schema `logo` to the e& logo too (kept as GN brand for correctness).
- Regenerate number pages when you want the bar on all 3,366 (deliberate — re-syncs the sheet).
