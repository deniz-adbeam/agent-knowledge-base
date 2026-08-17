---
type: skill
title: kb-save skill — how notes get written
description: The producer-side workflow that turns an insight, decision, or episode into a conforming OKF concept file, gated by human confirmation.
tags: [okf, tooling, skill]
timestamp: 2026-07-10T00:00:00Z
resource: .github/skills/kb-save/SKILL.md
relations:
  - /knowledge/okf-format|produces
  - /knowledge/agent-knowledge-base-toolchain|part-of
---
`kb-save` is the **producer** side of OKF (the consumer side is
[Agent Knowledge Base toolchain](/knowledge/agent-knowledge-base-toolchain.md)'s
`build-graph.py`).

## Steps
1. **Decide the folder** — `knowledge/` for durable, generalizable facts; `memory/` for a
   concrete, dated episode.
2. **Pick the `type`** from the project's vocabulary (`okf-types.json`).
3. **Resolve entities first** — read `knowledge/index.md` / `memory/index.md` (or
   `graph.json`) before writing, to reuse existing concept ids instead of minting
   near-duplicates, and to link the new concept via typed `relations`.
4. **Redact PII (mandatory)** — names, emails, credentials become `[REDACTED]` before
   anything is written to this shared, git-tracked base.
5. **Don't duplicate `docs/`** — link to the full design doc instead of copying it.
6. **Write the concept file** from the OKF template.
7. **Propose to the human, wait for confirmation** — the curation gate: the agent never
   writes a concept silently.
8. **Regenerate** — `python3 tools/build-graph.py`.
9. **Lint** — `python3 tools/okf-lint.py`, see
   [kb-lint skill — how conformance gets checked](/knowledge/kb-lint-workflow.md).
10. **Commit only if the user asks.**
