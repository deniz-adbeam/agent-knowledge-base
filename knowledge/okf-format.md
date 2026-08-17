---
type: concept
title: Open Knowledge Format (OKF) v0.1
description: The Markdown+YAML spec this repo's KB is written in — a required `type`, recommended fields, and a typed `relations` extension that becomes graph edges.
tags: [okf, format, concept]
timestamp: 2026-07-10T00:00:00Z
resource: README.md
relations:
  - /knowledge/configurable-type-vocabulary|constrains
  - /knowledge/agent-knowledge-base-toolchain|consumed-by
---
Every KB note is a Markdown file with a YAML frontmatter block.

- **Required:** `type` — a free string, but graph color/grouping come from matching it against
  `okf-types.json`. Missing `type` is the only linter ERROR.
- **Recommended:** `title`, `description`, `timestamp` (ISO 8601), `tags`, `resource` (canonical
  URI back to a design doc, ticket, or repo path for the full write-up).
- **The OKF extension beyond plain frontmatter — typed `relations`:** a list of
  `/dir/target|relation-type` strings (e.g. `/knowledge/okf-format|constrains`).
  `tools/build-graph.py` parses these into typed graph edges. Standard markdown links in the
  body (e.g. a link to another `/knowledge/<slug>.md` note) also become edges, so linking
  naturally in prose is already graph-capable.
- **Two bundles:** `knowledge/` (durable facts/decisions/systems) and `memory/` (dated
  episodes) — each has its own `index.md`, and the bundle root `index.md` carries
  `okf_version: "0.1"`.
- **Origin:** independently built several times across other projects before being extracted
  into this template.
