---
name: kb-save
description: Use when the user wants to capture knowledge or a design/clarification episode into this repo's knowledge base — "save this", "remember this", or when recording a decision, verified fact, system, datastore, or runbook. Writes a conforming Open Knowledge Format (OKF) concept into knowledge/ or memory/, redacts PII, links it into the graph, regenerates, and lints.
---

# kb-save — capture knowledge & memory as OKF concepts

This skill turns an insight, decision, or design-session outcome into a **conforming OKF
concept** (Markdown + YAML frontmatter) in the knowledge base, so it becomes immediately
wiki-capable and graph-capable, and the agent can reuse it in future sessions. This is the
**producer** side of OKF (the consumer side is `tools/build-graph.py`).

> **Curation rule (this repo):** the agent **proposes** the concept and waits for the human
> to **confirm** before writing. Commit only when the user explicitly asks.

## Workflow (checklist)

1. **Decide the folder.**
   - `knowledge/` — durable, generalizable: a system, datastore, decision, concept,
     runbook, or reference. Slow-changing.
   - `memory/` — a concrete, dated episode (one design session, verification run, or
     clarification outcome: what was asked, what was measured/decided, what was learned).

2. **Pick the `type`** (free string, but reuse the project's vocabulary for consistent graph
   colors — see `okf-types.json` at the repo root). Starter set: `system` · `datastore` ·
   `decision` · `concept` · `runbook` · `reference` · `case`.

3. **Resolve entities (avoid duplicates, create links).** Before writing, read
   `knowledge/index.md` and `memory/index.md` (or `graph.json` if present) to see which
   concepts already exist. **Reuse existing concept ids** instead of minting near-duplicates,
   and link the new concept to the ones it touches via typed `relations`.

4. **Redact PII (mandatory).** Before writing anything to this shared, git-tracked base,
   replace personal/sensitive data with `[REDACTED]`: names of individuals, email addresses,
   phone numbers, customer/personal identifiers, passwords, API keys, tokens, credentials.
   Keep enough context that the knowledge stays actionable. Ticket ids, page ids, and system
   names are fine to keep.

5. **Do not duplicate `docs/`.** Design documents elsewhere (e.g. `docs/`, Confluence) remain
   the source of truth for full designs — a KB concept states the essence and **links** to
   them (relative repo path or external page id), it does not copy their content.

6. **Write the concept file** in OKF format (see template). Naming:
   - knowledge: `knowledge/<kebab-slug>.md` (e.g. `knowledge/agent-knowledge-base-toolchain.md`)
   - memory: `memory/<YYYY-MM-DD>-<kebab-slug>.md`

7. **Propose to the human, get confirmation**, then write the file.

8. **Regenerate** the graph + indexes: `python3 tools/build-graph.py`

9. **Lint** (recommended): `python3 tools/okf-lint.py` — fix any ERRORs before finishing.

10. **Commit only if the user asks.**

## OKF concept template

```markdown
---
type: <system|datastore|decision|concept|runbook|reference|case>   # REQUIRED — see okf-types.json
title: <Human-readable display name>
description: <One sentence summary>
tags: [your-project, your-domain, ...]
timestamp: <ISO 8601, e.g. 2026-01-01T00:00:00Z>
resource: <optional canonical URI — design doc, ticket, or repo path>
relations:                       # typed edges (OKF extension): /dir/target|relation
  - /knowledge/<other-concept>|<relation-type>
---
Body in structured markdown. Reference other concepts with standard markdown links —
[Other Concept](/knowledge/<other-concept>.md) — which render on GitLab/GitHub AND become
graph edges. Prefer headings/lists over prose.

# Citations            # optional — external sources backing the claims
[1] [Source title](https://...)
```

For a **memory episode**, structure the body around: **What happened / was verified**,
**Outcome / decision**, and **Learning** (what to reuse next time). Link it to the decisions
it produced (`produced`), the systems it touched (`concerns`), and prior episodes it builds
on (`follows`).

See the notes already in `knowledge/` for worked examples — they document this template's own
tooling.
