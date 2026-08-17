# Agent Knowledge Base

A copy-paste template for a coding agent's knowledge & memory base: OKF-format Markdown as
source of truth, a self-contained interactive graph viewer, a conformance linter, and two
agent skills (`kb-save`, `kb-lint`).

> Built and maintained by **[ADBEAM](https://adbeam.dev)**. The thinking behind it — why an AI
> agent needs a queryable map of your systems — is written up in
> [Stop guessing: give your AI agents a map of your systems](https://adbeam.dev/blog/give-your-ai-agents-a-map-of-your-systems).
> Free to use and adapt under the [MIT License](LICENSE).

## 3 steps to your own KB

1. **Copy this repo's tree** into your target repo (skip `.git/`, `CHANGELOG.md`, and the
   `release` job in `.github/workflows/ci.yml` if your repo already has its own CI setup).
   Record the version you copied in `.okf-template-version` (plain text, e.g. `0.1.0`) so
   `kb.sh` can remind you later.
2. **Run `./kb.sh check`** — verifies Python 3.8+ is available (stdlib only, nothing to
   `pip install`) and the repo layout looks right.
3. **Replace the starter KB** — the notes already in `knowledge/` document *this template's own
   tooling* (dogfooded as the worked example, not fiction). Delete them once you've used them
   to understand the OKF pattern, then use the `kb-save` skill (or write your own OKF Markdown
   by hand) to add your first real note about your own project. Extend `okf-types.json` with
   any project-specific types as they come up.

## What's in here

| Path | Purpose |
|---|---|
| `knowledge/`, `memory/` | Your OKF Markdown — durable facts vs. dated episodes |
| `okf-types.json` | Type vocabulary (label/color/order per type) driving the graph and indexes |
| `tools/build-graph.py` | Regenerates `graph.json` + `graph.html` (interactive, searchable, offline) |
| `tools/okf-lint.py` | OKF conformance linter — errors fail, warnings don't |
| `kb.sh` | One command from fresh clone to graph: `./kb.sh` |
| `.github/skills/` | `kb-save` / `kb-lint` / `kb-ingest` agent skills (plain Markdown, readable by any agent) |
| `AGENTS.md` | Provider-agnostic agent instructions |

## Viewing the graph

Run `./kb.sh` to rebuild and open `graph.html` locally — a self-contained, searchable,
offline viewer (no server, no clone-of-a-clone needed). CI (`.github/workflows/ci.yml`)
regenerates the graph on every push/PR via the `build-graph-check` job to catch breakage,
but does not publish it anywhere. If you want an always-browsable hosted graph, add a GitHub
Pages job that runs `python3 tools/build-graph.py` and uploads `graph.html`/`graph.json`.

## Keeping up to date

This is a **copy**, not a submodule — there's no auto-update. To see what changed since you
copied: `git diff v<your-version>..v<latest> -- tools/ .github/skills/` against this repo. See
`CHANGELOG.md` for the human-readable version.

## Design

The design rationale lives as OKF notes in `knowledge/` — start with
`knowledge/agent-knowledge-base-toolchain.md` and browse the rest in the graph via `./kb.sh`.

## Contributing

Contributions are welcome — see [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup, conventions,
and the PR workflow. For security-sensitive reports, follow [`SECURITY.md`](SECURITY.md).

## License

Released under the [MIT License](LICENSE).

---

Made by [ADBEAM](https://adbeam.dev) — custom software and AI automation.

