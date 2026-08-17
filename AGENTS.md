# Agent Knowledge Base — Agent Instructions

Provider-agnostic, **project-scope** instructions for any coding agent working in a repo built
from this template. No user-scope install required.

## Knowledge base — how to work with it

- **Save** knowledge or a design/clarification episode → use the **`kb-save`** skill.
  Durable facts/decisions → `knowledge/`; dated episodes → `memory/`.
- **Ingest** knowledge from outside the conversation (a URL, a Confluence or Notion page, a
  SaaS knowledge tool, a local file/folder, or a code repository) → use the **`kb-ingest`**
  skill, which acquires the content and then hands off to `kb-save`.
- **Lint** → the **`kb-lint`** skill, or `python3 tools/okf-lint.py`.
- **Regenerate** the graph + indexes → `python3 tools/build-graph.py`
  (writes `graph.json`, `graph.html`, and the OKF `index.md` files).
- **Fresh clone / onboarding** → `./kb.sh` (checks prerequisites, builds, lints,
  opens the graph; `./kb.sh help` for subcommands).
- **Traverse / query** the KB programmatically → `graph.json` (all nodes + typed edges).
- **View** the knowledge graph → open `graph.html` (interactive, offline, no server; use the
  search box to find a node by title/tag/id).

## Knowledge-base-first — consult the KB before design work (non-negotiable)

Before answering design questions or re-deriving decisions, **first check the knowledge base**
for prior decisions and verified facts:

1. **Traverse `graph.json`** (regenerate if missing — it is derived & git-ignored) from the
   matching concept and follow the typed edges to decisions, episodes, and design docs.
   **Fallback:** the committed `knowledge/index.md` and `memory/index.md` catalogs.
2. **Grep `knowledge/` and `memory/`** for stable tokens.
3. **Reuse what you find:** a `decision` concept settles the question (do not re-litigate it —
   if new facts contradict it, propose a revision instead); a `case` episode provides measured
   facts and their date.

## Type vocabulary

Defined in `okf-types.json` — extend it with project-specific types as they emerge (see
`README.md`). `okf-lint.py` warns (does not error) on a `type` not listed there.

## Conventions

- Knowledge notes state the **essence** and link to full design docs elsewhere — never
  duplicate document content into the KB.
- **Only the best-fit solution is documented** — no alternative-option lists (rejected
  alternatives belong in an ADR's "alternatives considered" section, one line each).
- **PII redaction is mandatory** before saving anything (`[REDACTED]`): personal names,
  e-mails, credentials, tokens.
- Commit only when explicitly asked.

## Skills

Project skills live in `.github/skills/` (GitHub Copilot CLI's discovery path): **`kb-save`**,
**`kb-lint`**, **`kb-ingest`**. All three are plain Markdown — any agent can read and follow
them directly even without native skill-discovery support.
