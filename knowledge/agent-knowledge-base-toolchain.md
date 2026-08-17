---
type: system
title: Agent Knowledge Base toolchain (this repo)
description: This repo's own OKF tooling — build-graph.py, okf-lint.py, kb.sh, and the kb-save/kb-lint skills — dogfooded as the worked example for adopting teams.
tags: [okf, tooling, knowledge-base]
timestamp: 2026-07-08T00:00:00Z
relations:
  - /knowledge/copy-paste-distribution|governed-by
  - /knowledge/configurable-type-vocabulary|implements
---
The system this template ships, documented about itself instead of a fictional example.

- **`tools/build-graph.py`** — parses `knowledge/`+`memory/` OKF Markdown into `graph.json`
  (machine-readable) and `graph.html` (a self-contained canvas viewer: drag/zoom/pan, click a
  node for its connections, and a live search box filtering by title/tag/id).
- **`tools/okf-lint.py`** — OKF v0.1 conformance linter. ERRORs (missing frontmatter/`type`)
  fail the run; WARNs (missing recommended fields, broken links, a `type` not in
  `okf-types.json`) don't.
- **`kb.sh`** — one command from a fresh clone to an open graph: `./kb.sh`.
- **`.github/skills/`** — the `kb-save`/`kb-lint`/`kb-ingest` skill content, plain Markdown at
  GitHub Copilot CLI's discovery path. Readable and followable by any agent, not just Copilot.

## Not duplicated here
This note states the essence; the fuller rationale is spread across its sibling notes in
`knowledge/` — browse them in the graph (`./kb.sh`).
