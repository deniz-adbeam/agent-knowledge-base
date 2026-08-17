---
name: kb-ingest
description: Use when the user wants to pull knowledge from outside the current conversation into this repo's knowledge base — a URL, a Confluence or Notion page, a SaaS knowledge tool (Slack, Jira/Linear, Google Drive, …), a local file/folder, or a code repository (cloned locally, or on GitHub/GitLab). Acquires the raw content via the matching connector, then hands off to the kb-save workflow (type selection, dedupe, PII redaction, human confirmation) to write a conforming OKF concept.
---

# kb-ingest — pull external knowledge into the OKF knowledge base

`kb-ingest` is "`kb-save`, but the raw material comes from outside the conversation." It only
adds a **Step 0: acquire the content** in front of `kb-save`'s existing checklist — type
selection, dedupe, PII redaction, the propose-and-confirm gate, writing, and linting are
unchanged and **not duplicated here**. Read `kb-save`'s `SKILL.md` for that part.

## Step 0 — acquire raw content (pick the matching connector)

1. **Detect the source type:**
   - `github.com` / `gitlab.*` URL, or the user says "repo"/"repository" → **Code repository
     (remote)**
   - `*.atlassian.net` URL or a Confluence page reference → **Confluence**
   - `notion.so` / `notion.site` URL, or the user names another SaaS knowledge tool
     (Notion, Slack, Jira, Linear, Google Drive, …) → **SaaS knowledge tool**
   - any other URL → **Web**
   - a local path → **Filesystem** (a locally cloned repo is just a path here — no special
     case needed)

2. **Web** — fetch the URL with the `WebFetch` tool.

3. **Confluence** — use `mcp-atlassian` tools (`confluence_search`, `confluence_get_page`). If
   these tools aren't available in this environment, **tell the user instead of failing**, and
   suggest pasting the content or giving a fetchable URL instead.

4. **Filesystem** — `Read`/`Glob` the given path(s). For a directory (including a cloned
   repo), start at `README.md`, then the instructions file (`AGENTS.md`/`CLAUDE.md`), then
   `docs/` — don't blindly read every file in the tree.

5. **Code repository (remote, not cloned)** — use `mcp__github__*` tools (`get_file_contents`,
   `search_code`) or `mcp__gitlab__*` tools (`get_repository_tree`,
   `get_file_contents`). Same graceful-degrade rule as Confluence if the relevant MCP isn't
   configured. Reading order: `README.md` → instructions file → `docs/`.

6. **SaaS knowledge tool (Notion, Slack, Jira/Linear, Google Drive, …)** — use that tool's MCP
   server if one is configured (e.g. `mcp__notion__*` for Notion pages/databases, or the
   equivalent for Slack, Jira/Linear, Google Drive). Same graceful-degrade rule as Confluence:
   if the relevant MCP isn't available, **tell the user instead of failing** and suggest
   pasting the content or giving a fetchable URL. Any SaaS source not covered by a configured
   MCP falls back to the **Web** connector when it has a fetchable URL.

7. **Fetch failure at this step** (404, auth error, missing file/page) — name the failing
   source, skip it, and continue with any other sources given in the same invocation. Never
   invent content for a source that failed to load.

## Step 1 onward — hand off to kb-save

Once raw content is in hand:

1. **Dedupe against existing notes** — search the `resource:` frontmatter values already
   present in `knowledge/`/`memory/` (or `graph.json` if generated) for this source. A match
   means the candidate is an **update** to that existing concept, not a new one.
2. **Extract 1–N OKF concept candidates** — essence, not a verbatim copy of the source, same
   as `kb-save`'s "don't duplicate `docs/`" principle. Set `resource:` to the source URL/path
   so provenance stays traceable.
3. Continue with `kb-save`'s workflow from its step 2 (pick `type`) through step 10 (commit
   only if asked) — including its mandatory **PII redaction** and **propose-to-human,
   wait-for-confirmation** gate. If one invocation ingested multiple sources, propose all
   resulting candidates together in a single batch.
4. **Regenerate and lint:** `python3 tools/build-graph.py` then `python3 tools/okf-lint.py`.

## Multiple sources in one run

Process sequentially, not in parallel — this keeps the human-confirmation gate simple (one
batch of candidates to review, not concurrent writers). If one source fails, continue with the
rest and report the failure at the end.
