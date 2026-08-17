# Knowledge

## Concepts

* [Configurable OKF type vocabulary (okf-types.json)](/knowledge/configurable-type-vocabulary.md) — 2026-07-08 — Why build-graph.py/okf-lint.py read type labels/colors/order from okf-types.json instead of hardcoding them.
* [Open Knowledge Format (OKF) v0.1](/knowledge/okf-format.md) — 2026-07-10 — The Markdown+YAML spec this repo's KB is written in — a required `type`, recommended fields, and a typed `relations` extension that becomes graph edges.

## Decisions

* [Copy-paste template, not a git submodule or package](/knowledge/copy-paste-distribution.md) — 2026-07-08 — How this repo reaches adopting teams — copied into their repo, not pulled via submodule/npm/pip — with semantic-release + tagged versions so a later diff against a newer version is still possible.

## Systems

* [Agent Knowledge Base toolchain (this repo)](/knowledge/agent-knowledge-base-toolchain.md) — 2026-07-08 — This repo's own OKF tooling — build-graph.py, okf-lint.py, kb.sh, and the kb-save/kb-lint skills — dogfooded as the worked example for adopting teams.

## References

* [AGENTS.md — how the agent instructions are organized](/knowledge/agents-md-structure.md) — 2026-07-10 — Structure of this repo's provider-agnostic agent instructions file, imported natively into CLAUDE.md for Claude Code.

## Skills

* [kb-ingest skill — how external knowledge gets pulled in](/knowledge/kb-ingest-workflow.md) — 2026-07-10 — The connector layer that acquires raw content from web, Confluence, Notion and other SaaS knowledge tools, filesystem, or code-repository sources and hands off to kb-save's existing workflow.
* [kb-lint skill — how conformance gets checked](/knowledge/kb-lint-workflow.md) — 2026-07-10 — Runs the OKF conformance linter (tools/okf-lint.py) and interprets ERROR vs. WARN findings.
* [kb-save skill — how notes get written](/knowledge/kb-save-workflow.md) — 2026-07-10 — The producer-side workflow that turns an insight, decision, or episode into a conforming OKF concept file, gated by human confirmation.
