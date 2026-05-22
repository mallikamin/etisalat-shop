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
- Hosted on Cloudflare Pages (CNAME present). `git push origin main` triggers auto-deploy.

## Git practices

- Identity: `Malik Amin <amin@sitaratech.info>` (per `memory/execution-policy.md` — no Co-Authored-By/Claude/Anthropic).
- Stage specific paths, not `git add .`.
- Don't push without authorization for that scope.

## Full protocol

- `~/.claude/projects/C--Users-Malik/memory/project-context-folder-scaffold.md`
- `~/.claude/projects/C--Users-Malik/memory/project-files-hygiene-archive.md`
- `~/.claude/projects/C--Users-Malik/memory/execution-policy.md`
- `~/.claude/projects/C--Users-Malik/memory/MEMORY.md` (index)
