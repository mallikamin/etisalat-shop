# Verification Log

Append-only log of what was verified, when, and how. Newest at top.

<!-- Template:
## YYYY-MM-DD — <short title>
- **Category**: schema / infra / credentials / code
- **What**: <thing verified>
- **How**: <command or file read>
- **Result**: <what it actually was>
-->

## 2026-05-30 — Sitemap pruned 3,366 → 100 to break crawl-budget starvation

- **Category**: code / SEO
- **What**: GSC showed `sitemap-numbers.xml`'s number pages stuck in **"Discovered – currently not indexed" (Last crawled: N/A)** — AND real money pages (`/emirati/`, `/blog/how-to-port-number-du-to-etisalat-uae.html`, both in `sitemap.xml` for months) were crawl-starved in the same queue. Diagnosis: 3,365 thin near-duplicate URLs diluting crawl budget on a DR-0 domain.
- **How**: Ranked the *deployed* `numbers/etisalat-*/` pages (3,365) by `analyze()` pattern score via `_files/2026-05-30/prune_number_sitemap.py` (ranks deployed pages, not a fresh Sheets fetch → zero 404 risk). Kept top 100 (score 51→29 cutoff) + `/numbers/` hub. Added `lastmod 2026-05-30`. Commit `163dde4`, pushed.
- **Result**: Live sitemap = 101 `<loc>` (verified via curl). **GSC re-read same day → 101 discovered pages, Status Success** (screenshot confirmed). The 109 already-indexed number pages stay indexed; pages remain live/reachable via `/numbers/`. Prune is reversible — bump `TOP_N` in the script to widen. **Watch (≤2 wks):** money pages' "Last crawled" should flip N/A→real date; "Discovered – not indexed" pile should shrink. If money pages still uncrawled after that, it's purely authority → citations.

## 2026-05-30 — AR "etisalat vs du" page: CTR + freshness + dead-CTA fix

- **Category**: code / SEO
- **What**: `ar/blog/etisalat-vs-du-postpaid-plans-uae.html` — GSC's "fewer impressions" recommendation (↓68%) + an Arabic `e&` vs `du` comparison query cluster pulling 50–63 impressions each at **0 clicks**. Page also had **every WhatsApp CTA pointing to the dead `wa.me/message/J33IA2UOJ6CLM1` short link** (6 instances) and stale Feb dates.
- **How**: CTR-rewrote title/meta/OG/Twitter/Article-schema/H1 to include Latin `e&`/`du` + "أيهما أفضل وأرخص" intent; `dateModified`→2026-05-30 (datePublished kept Feb 22) + in-body dates → مايو; replaced 6 dead CTAs → live `wa.me/971569028087` (Arabic prefill); WhatsApp-labeled `9377` voice line → `8087` conversion number; escaped `e&`→`e&amp;` in 6 HTML contexts (JSON-LD left raw). Commit `e21e2e7`, pushed. **Du-content kept per Malik's explicit call 2026-05-30** (defensible informational comparison positioning e& as winner — overrides the usual Du-silence rule for THIS page only).
- **Result**: Verified live via curl (new title, 6×8087 links, 0 dead links, May-30 date). GSC URL Inspection: **"URL is on Google → Page is indexed"** — Request-Indexing pending to refresh snippet.

## 2026-05-22 — Scaffold created

- **Category**: meta
- **What**: `_context/` + `_files/` + `_archive/` scaffolded per `memory/project-context-folder-scaffold.md`
- **How**: automated scaffold from Claude session
- **Result**: empty templates; awaiting first verified entries
