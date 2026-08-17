# Contributing

Thanks for your interest in improving **agent-knowledge-base**! This repo is a copy-paste
template for a coding agent's knowledge & memory base (OKF-format Markdown, an interactive
graph viewer, a conformance linter, and the `kb-save` / `kb-lint` / `kb-ingest` skills).

## Getting started

Prerequisites: **Python 3.8+** (standard library only — nothing to `pip install` for the KB
tools) and **Node.js** only if you want the commit/release tooling.

```bash
./kb.sh            # check prerequisites, build the graph, lint, open graph.html
./kb.sh help       # list subcommands (check / build / lint / open)
```

Useful commands:

- `python3 tools/build-graph.py` — regenerate `graph.json`, `graph.html`, and the OKF
  `index.md` files.
- `python3 tools/okf-lint.py` — validate OKF conformance (errors fail, warnings are advisory).

## Making changes

- Keep knowledge notes to the **essence** and link to full design docs — don't duplicate
  document content into the KB.
- **Redact PII** (`[REDACTED]`) before committing anything: personal names, e-mails,
  credentials, tokens.
- Extend the type vocabulary in `okf-types.json` rather than hardcoding new types.
- After editing notes, run `okf-lint.py` and regenerate the graph so `index.md` stays in sync.
- Do **not** commit generated artifacts (`graph.json`, `graph.html`) — they are git-ignored.

## Commit messages

This repo uses **[Conventional Commits](https://www.conventionalcommits.org/)**, enforced by
`commitlint`. Use the interactive helper if you have Node.js installed:

```bash
npm install
npm run commit     # guided Conventional Commit via commitizen
```

Format: `type(scope): summary` — e.g. `feat(kb-lint): add relation-type check` or
`docs(readme): clarify quickstart`. Releases and the changelog are generated automatically
from commit types via semantic-release.

## Pull requests

1. Fork and create a feature branch.
2. Make focused changes; keep the KB lint clean (`python3 tools/okf-lint.py`).
3. Use Conventional Commit messages.
4. Open a PR describing **what** changed and **why**; link any related issue.

## Reporting issues

For bugs and feature ideas, open a GitHub issue. For security-sensitive reports, follow
[`SECURITY.md`](SECURITY.md) instead of opening a public issue.
