---
type: skill
title: kb-ingest skill — how external knowledge gets pulled in
description: The connector layer that acquires raw content from web, Confluence, Notion and other SaaS knowledge tools, filesystem, or code-repository sources and hands off to kb-save's existing workflow.
tags: [okf, tooling, skill]
timestamp: 2026-07-10T00:00:00Z
resource: .github/skills/kb-ingest/SKILL.md
relations:
  - /knowledge/kb-save-workflow|extends
  - /knowledge/agent-knowledge-base-toolchain|part-of
---
`kb-ingest` adds a "Step 0: acquire the content" in front of
[kb-save skill — how notes get written](/knowledge/kb-save-workflow.md)'s existing checklist —
everything from type selection onward is unchanged and not duplicated.

## Connectors (one skill file, not one per source)
- **Web** — `WebFetch` on a URL.
- **Confluence** — `mcp-atlassian` tools, optional: degrades to "tell the user" if unset.
- **SaaS knowledge tools (Notion, Slack, Jira/Linear, Google Drive, …)** — that tool's MCP
  server if configured (e.g. `mcp__notion__*`), optional and graceful-degrading like
  Confluence; falls back to **Web** when the source has a fetchable URL.
- **Filesystem** — `Read`/`Glob` on a local path; a cloned repo is just a path here.
- **Code repository (remote)** — `mcp__github__*` / `mcp__gitlab__*`, optional for the same
  reason as Confluence. Reading order: `README.md` → instructions file → `docs/`.

## Why no staging directory
Unlike a two-phase `ingest`/`compile` design, `kb-ingest` stays single-stage: no `sources/`
directory, no ingest manifest, no hash-based change detection. Provenance is carried by the
`resource:` frontmatter field each written concept already has; dedupe is a `resource:` search
against existing notes, not a separate index.
