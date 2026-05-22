# Project Context

Canonical, verified facts about this project. Read me before touching DB, infra, or credentials.

## Files

- **INDEX.md** — the wikipedia of this project. Start here.
- **SCHEMA.md** — verified DB structure (no guesses)
- **CREDENTIALS.md** — secrets (gitignored, never committed)
- **INFRA.md** — deployment topology, ports, services
- **VERIFIED.md** — append-only log of what was verified, when, how
- **DECISIONS.md** — chat-only architecture decisions not visible in code

## Subfolders

- **notes/** — meeting/call/chat notes Malik shared (saved locally, dated)
- **screenshots/** — every screenshot/image Malik shared (saved locally, dated)
- **refs/** — external docs/PDFs/links Malik provided as reference

## Rules

- Only write verified facts. If guessing, write a TODO instead.
- Stamp every entry with date + source command/file.
- Update VERIFIED.md every time something is confirmed or re-confirmed.
- CREDENTIALS.md is gitignored — never commit. Confirm `.gitignore` before any commit touching `_context/`.

Maintained by Claude + Malik per `memory/project-context-folder-scaffold.md`.
