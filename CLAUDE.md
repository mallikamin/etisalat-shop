# Claude — Project Instructions (etisalat-shop)

**Read `_context/INDEX.md` first.** It is the wikipedia of this project — purpose, quick links, architecture, current status, people.

## File hygiene (mandatory, no exceptions)

- **Daily scratch / handoff / checkpoint / draft / generated files** → `_files/YYYY-MM-DD/`, **not** project root. Project root is for shipped/canonical files only.
- **Any image / screenshot / call notes / chat export / PDF Malik shares with you** → save a local copy to `_context/screenshots/`, `_context/notes/`, or `_context/refs/`. Filename: `YYYY-MM-DD_<short-slug>.<ext>`. Log it in `_context/INDEX.md` "Reference material" table with date + one-sentence purpose.
- **Verified facts** (schema, infra, deploy topology) → write to the matching `_context/*.md` file, stamped with date + source command/file. Never guess.
- **Never commit** `_context/CREDENTIALS.md`, `*.env`, `_files/`, or `_archive/` — all gitignored. Check `git status` before any `git add`.
- **Never delete** old files — only rename + move to `_archive/` after Malik confirms per-file.

## Pre-flight checklist (every session)

1. Read `_context/INDEX.md` (project wikipedia)
2. Read `_context/VERIFIED.md` (what's confirmed + how fresh — treat >30d entries as stale)
3. Read the most recent `CONTINUATION_*.md` / `CHECKPOINT_*.md` / `PAUSE_CHECKPOINT_*.md` at project root if present
4. Read this `CLAUDE.md` for any project-specific updates
5. Before any DB/infra/credential reference: verify against the actual source this session (don't trust prior assumptions)

## Project-specific notes

- Partner: Bilal Khalid (UAE) — see `memory/partners-trust-circle.md` + `memory/feedback-partner-it-tailscale-no-drift.md`.
- Sister sites: `goldennummbers` (numbers-led, Etisalat-positioned) and `uaepremiumnumbers` (plan-led). Coordinate brand voice — never write "Du" or Du hashtags on Etisalat-positioned content per `memory/project-goldennummbers-etisalat-positioning.md`.
- ⚠ **Deployment: this is a Cloudflare WORKER with an assets binding, not Pages.** `wrangler.toml`
  binds `directory = "./"`, so a deploy is `wrangler deploy` from this folder with
  `CLOUDFLARE_API_TOKEN` from `C:\FBAI\.env`. (The old "Cloudflare Pages, `git push origin main`
  auto-deploys" note that used to sit here was wrong; corrected 2026-09-09 after an actual deploy.)

## Deploying this site (read before you deploy — 2026-09-09, rule 0 added 2026-09-10)

0. **THE SITE IS REDEPLOYED FROM GIT HEAD ON EVERY PUSH TO `main`** (`.github/workflows/deploy.yml`,
   and the `ccbw` card automation pushes several times a day). **A manual `wrangler deploy` of an
   UNCOMMITTED file is live only until the next push**, then CI silently puts HEAD's version back.
   That is how the chat gate was "verified live" on 09-07 and 09-09 and was gone both times within
   hours: `assets/chat.js` sat uncommitted for three days while 12 ccbw pushes each redeployed the
   old file. **Anything you deploy by hand must be committed and pushed in the same session**, and
   the CI run for that commit is the deploy that counts. Then run the verify script (rule 4).

`wrangler deploy` reads **17,015 asset files** and **intermittently dies with `fetch failed`**
partway through the upload. Seen 2026-09-07 (~15 min in) and again 2026-09-09 (12 min in, rc=1);
the retry then took 50 seconds. **A deploy that dies mid-upload leaves the OLD asset live.**

1. **`wrangler deploy` returning is not the asset being live.** Retry on `fetch failed`, then
   **fetch the deployed bytes and diff them against your local file** before saying anything shipped.
2. **Fetch the PLAIN URL, never `?v=<random>`.** A cache-busted request reached the origin and
   reported a fix live on 09-07 while the URL a browser actually loads was still stale at the edge.
3. **Send a browser `User-Agent` in any probe script.** Cloudflare's bot check answers
   `Python-urllib` with a bare 403 before the worker runs, which reads exactly like an origin denial.
4. **`assets/chat.js` is one half of a two-sided cutover with the `bilal-sales` worker.** Shipping
   one side alone breaks web chat for every visitor with no server-side error anywhere — it did, for
   two days, 09-07 to 09-09, costing every web lead in that window. After ANY deploy that touches it:
   `python verify_web_chat_live.py` in `C:\fbai\bilal-app`. Full write-up in that folder's
   `ERROR_LOG.md` and `STATE.md`, both dated 2026-09-09.

## Git practices

- Identity: `Malik Amin <amin@sitaratech.info>` (per `memory/execution-policy.md` — no Co-Authored-By/Claude/Anthropic).
- Stage specific paths, not `git add .`.
- Don't push without authorization for that scope.

## Full protocol

- `~/.claude/projects/C--Users-Malik/memory/project-context-folder-scaffold.md`
- `~/.claude/projects/C--Users-Malik/memory/project-files-hygiene-archive.md`
- `~/.claude/projects/C--Users-Malik/memory/execution-policy.md`
- `~/.claude/projects/C--Users-Malik/memory/MEMORY.md` (index)
