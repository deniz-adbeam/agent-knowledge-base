---
type: reference
title: AGENTS.md — how the agent instructions are organized
description: Structure of this repo's provider-agnostic agent instructions file, imported natively into CLAUDE.md for Claude Code.
tags: [okf, agents, instructions]
timestamp: 2026-07-10T00:00:00Z
resource: AGENTS.md
relations:
  - /knowledge/agent-knowledge-base-toolchain|documents
  - /knowledge/okf-format|mandates
---
`AGENTS.md` is the single, provider-agnostic instructions file. `CLAUDE.md` is a 3-line shim
that `@AGENTS.md`-imports it, so Claude Code gets identical instructions natively; GitHub
Copilot CLI reads `AGENTS.md` directly.

## Sections
1. **"Knowledge base — how to work with it"** — maps an intent to a command/skill: save →
   `kb-save`, lint → `kb-lint` (or `tools/okf-lint.py`), regenerate → `tools/build-graph.py`,
   traverse programmatically → `graph.json`, view → `graph.html`.
2. **"Knowledge-base-first"** — a non-negotiable mandate to consult the KB (`graph.json`,
   falling back to the committed `knowledge/index.md` / `memory/index.md`) *before* design
   work: reuse a `decision` concept rather than re-litigating it (propose a revision instead
   if new facts contradict it); reuse a `case` episode's measured facts.
3. **"Type vocabulary"** — points to `okf-types.json` as the extensible source of truth,
   extended with project-specific types as they emerge.
4. **"Conventions"** — notes state the essence and link to full docs elsewhere (never
   duplicate document content); only the best-fit solution is documented (no
   alternative-option lists — those belong in an ADR's "alternatives considered"); PII
   redaction is mandatory; commit only when explicitly asked.
5. **"Skills"** — project skills live in `.github/skills/` (Copilot CLI's discovery path),
   plain Markdown so any agent can follow them without native skill-discovery support.
