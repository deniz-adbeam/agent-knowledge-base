---
type: skill
title: kb-lint skill — how conformance gets checked
description: Runs the OKF conformance linter (tools/okf-lint.py) and interprets ERROR vs. WARN findings.
tags: [okf, tooling, skill]
timestamp: 2026-07-10T00:00:00Z
resource: .github/skills/kb-lint/SKILL.md
relations:
  - /knowledge/okf-format|validates
  - /knowledge/agent-knowledge-base-toolchain|part-of
---
Invocation: `python3 tools/okf-lint.py [bundle-root]`. Findings are grouped per concept.

- **ERROR — blocks (exit code 1):**
  - missing or unparseable YAML frontmatter
  - missing required `type`
- **WARN — doesn't block (exit code 0 if no ERRORs):**
  - missing `title` / `description` / `timestamp`
  - `timestamp` not ISO-8601
  - a `relations` target that doesn't resolve (broken link — tolerated, may be
    intentional not-yet-written knowledge)
  - a relation with no `|relation-type`
  - a `type` not present in `okf-types.json`

The exit code (0 vs. 1) makes the linter CI-gateable — a CI workflow (e.g. GitHub Actions)
can fail a pipeline on ERRORs while leaving WARNs as advisory.
