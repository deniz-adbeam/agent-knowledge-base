---
name: kb-lint
description: Use when asked to lint, validate, or health-check this repo's knowledge base — "lint the knowledge base", "check OKF conformance", "find broken links", "validate the notes". Runs tools/okf-lint.py and interprets the findings, proposing fixes.
---

# kb-lint — validate the knowledge base against OKF v0.1

Runs the deterministic OKF conformance linter and helps fix what it finds.

## Workflow

1. **Run the linter:**
   ```bash
   python3 tools/okf-lint.py
   ```
   (Optionally pass a bundle root: `python3 tools/okf-lint.py <path>`.)

2. **Interpret the output.** Findings are grouped per concept with a severity:
   - **ERROR** — breaks OKF conformance. Must be fixed. Two cases:
     - *missing or unparseable YAML frontmatter* → add a proper `---` … `---` block.
     - *missing required `type`* → add a `type:` field.
   - **WARN** — quality/consistency issues, do not block:
     - missing `title` / `description` / `timestamp` → add the recommended field.
     - `timestamp` not ISO-8601 → use e.g. `2026-01-01T00:00:00Z`.
     - *relation target not found* / *broken link* → fix the path, or leave it if it is
       intentional not-yet-written knowledge (OKF tolerates broken links).
     - *relation has no |type* → add `|<relation-type>` so the edge is typed.
     - *`type` not in okf-types.json* → either add the type to `okf-types.json` (if it's a
       genuinely new category) or fix a typo in the frontmatter.

3. **Propose fixes** for ERRORs (and WARNs worth fixing). For edits to concept content,
   follow the `kb-save` conventions (OKF frontmatter, typed `relations`, PII redaction).

4. **Re-run** the linter until ERRORs are zero, then `python3 tools/build-graph.py` to
   regenerate the graph and indexes.

## Exit code

`okf-lint.py` exits **1** if any ERROR is present, **0** otherwise — so it can gate a CI
pipeline.
