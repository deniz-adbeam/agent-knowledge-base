---
type: decision
title: Copy-paste template, not a git submodule or package
description: How this repo reaches adopting teams — copied into their repo, not pulled via submodule/npm/pip — with semantic-release + tagged versions so a later diff against a newer version is still possible.
tags: [okf, distribution, decision]
timestamp: 2026-07-08T00:00:00Z
resource: README.md
relations:
  - /knowledge/agent-knowledge-base-toolchain|decided-for
---
**Decided 2026-07-08.** A team adopts this by copying the tree into their own repo — no git
submodule, no published npm/pip package.

- **Why not a submodule/package:** zero integration friction for adopting teams was prioritized
  over auto-updates; a submodule couples the adopter's repo history to this one, and a package
  registry is more infrastructure than a lightweight Markdown+script toolkit needs.
- **The drift trade-off, mitigated, not eliminated:** copies will diverge over time as each team
  edits its own tools locally. Mitigation: `semantic-release` tags every change (`vX.Y.Z`) with
  a generated `CHANGELOG.md`, so an adopting team can later run
  `git diff v<their-version>..v<latest> -- tools/ .github/skills/` against this repo to see
  exactly what to pull in by hand.
- **Alternative considered:** git submodule — rejected, forces adopting teams into submodule
  workflow discipline for a handful of scripts and Markdown files; not worth the friction.
