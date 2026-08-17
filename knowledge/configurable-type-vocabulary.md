---
type: concept
title: Configurable OKF type vocabulary (okf-types.json)
description: Why build-graph.py/okf-lint.py read type labels/colors/order from okf-types.json instead of hardcoding them.
tags: [okf, tooling, concept]
timestamp: 2026-07-08T00:00:00Z
relations:
  - /knowledge/agent-knowledge-base-toolchain|applies-to
---
`okf-types.json` at the repo root defines `{type: {label, color, order}}` for every concept
type. Both tools read it instead of hardcoding a Python dict.

- **Why it matters:** every team's knowledge domain grows its own vocabulary over time (e.g. a
  team adds an `environment` or `runbook`-adjacent type). A config file lets a team extend the
  vocabulary without touching Python source.
- **Fallback behavior:** a `type` not present in `okf-types.json` still renders (gray `note`
  color in the graph) and only produces a linter **WARN**, never an ERROR — so a team can try a
  new type before formalizing it in the config.
- **Ships with 10 curated types:** `concept`, `decision`, `system`, `datastore`, `runbook`,
  `reference`, `skill`, `tool`, `case`, `note`.
