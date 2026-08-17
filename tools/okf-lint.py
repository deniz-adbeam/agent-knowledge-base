#!/usr/bin/env python3
"""OKF v0.1 conformance linter for this repo's knowledge base.

Checks the concepts in knowledge/ and memory/ against Open Knowledge Format v0.1
(plus our typed-`relations` extension). ERRORS fail the run (exit 1); WARNINGS do not.

Usage:
  python3 tools/okf-lint.py [bundle_root]   # defaults to the repo root

What it checks (per OKF SPEC §9 + our conventions):
  ERROR  - non-reserved .md without a parseable YAML frontmatter block
  ERROR  - frontmatter without a non-empty `type`
  WARN   - missing recommended fields (title, description, timestamp)
  WARN   - timestamp not ISO-8601
  WARN   - relation without a |type, or whose target concept does not exist
  WARN   - body markdown link whose target concept does not exist
  WARN   - bundle-root index.md without an okf_version declaration
OKF is permissive on broken links (may be not-yet-written knowledge), so those are
warnings, not errors.
"""

import glob
import os
import re
import sys

DIRS = ["knowledge", "memory"]
RESERVED = {"index.md", "log.md"}
MD_LINK = re.compile(r"\]\((/[^)]+?\.md)\)")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}([T ]\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:?\d{2})?)?$")


def load_known_types(root):
  path = os.path.join(root, "okf-types.json")
  if not os.path.exists(path):
    return None  # no config found — skip the check rather than false-positive on every file
  import json
  with open(path, encoding="utf-8") as f:
    return set(json.load(f).keys())


def parse_frontmatter(text):
  """Return (meta, body). meta is None when no parseable frontmatter is present."""
  if not text.startswith("---"):
    return None, text
  lines = text.split("\n")
  end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
  if end is None:
    return None, text
  fm, body = lines[1:end], "\n".join(lines[end + 1:])
  meta = {}
  i = 0
  while i < len(fm):
    line = fm[i]
    if not line.strip() or line.lstrip().startswith("#"):
      i += 1
      continue
    m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
    if not m:
      i += 1
      continue
    key, val = m.group(1), m.group(2).strip()
    if val == "":
      items, j = [], i + 1
      while j < len(fm) and re.match(r"^\s*-\s+", fm[j]):
        items.append(re.sub(r"^\s*-\s+", "", fm[j]).strip())
        j += 1
      meta[key], i = items, j
    elif val.startswith("[") and val.endswith("]"):
      inner = val[1:-1].strip()
      meta[key] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
      i += 1
    else:
      meta[key], i = val, i + 1
  return meta, body


def main():
  root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  known_types = load_known_types(root)
  files = {}  # concept id -> (meta, body)
  findings = []  # (concept_id, severity, message)

  for d in DIRS:
    for path in sorted(glob.glob(os.path.join(root, d, "*.md"))):
      if os.path.basename(path) in RESERVED:
        continue
      cid = os.path.relpath(path, root)[:-3]
      with open(path, encoding="utf-8") as f:
        meta, body = parse_frontmatter(f.read())
      if meta is None:
        findings.append((cid, "ERROR", "missing or unparseable YAML frontmatter"))
        files[cid] = ({}, body)
        continue
      files[cid] = (meta, body)

  ids = set(files)
  basemap = {}
  for cid in ids:
    basemap.setdefault(cid.split("/")[-1], cid)

  def resolve(target):
    t = target.strip().lstrip("/")
    if t.endswith(".md"):
      t = t[:-3]
    if t in ids:
      return t
    return basemap.get(t.split("/")[-1])

  for cid, (meta, body) in sorted(files.items()):
    if not meta:
      continue
    t = str(meta.get("type", "")).strip()
    if not t:
      findings.append((cid, "ERROR", "missing required `type`"))
    elif known_types is not None and t not in known_types:
      findings.append((cid, "WARN", f"`type: {t}` is not in okf-types.json (falls back to the 'note' color/label)"))
    if not meta.get("title"):
      findings.append((cid, "WARN", "no `title` (consumers will derive it from the filename)"))
    if not meta.get("description"):
      findings.append((cid, "WARN", "no `description` (recommended)"))
    ts = meta.get("timestamp")
    if not ts:
      findings.append((cid, "WARN", "no `timestamp` (recommended)"))
    elif not ISO.match(str(ts)):
      findings.append((cid, "WARN", f"`timestamp` is not ISO-8601: {ts}"))
    rels = meta.get("relations") or []
    if isinstance(rels, str):
      rels = [rels]
    for entry in rels:
      raw, sep, etype = entry.partition("|")
      if not sep or not etype.strip():
        findings.append((cid, "WARN", f"relation '{entry}' has no |type (defaults to 'related')"))
      if resolve(raw) is None:
        findings.append((cid, "WARN", f"relation target not found: {raw.strip()}"))
    for m in MD_LINK.finditer(body):
      if resolve(m.group(1)) is None:
        findings.append((cid, "WARN", f"broken link: {m.group(1)}"))

  root_index = os.path.join(root, "index.md")
  if os.path.exists(root_index):
    with open(root_index, encoding="utf-8") as f:
      if "okf_version" not in f.read():
        findings.append(("index.md", "WARN", "bundle-root index.md has no okf_version declaration"))

  by_concept = {}
  for cid, sev, msg in findings:
    by_concept.setdefault(cid, []).append((sev, msg))
  for cid in sorted(by_concept):
    print(cid)
    for sev, msg in by_concept[cid]:
      print(f"  {sev:5}  {msg}")

  errors = sum(1 for _, s, _ in findings if s == "ERROR")
  warns = sum(1 for _, s, _ in findings if s == "WARN")
  print("─" * 40)
  print(f"{len(files)} concept(s) · {errors} error(s) · {warns} warning(s)")
  return 1 if errors else 0


if __name__ == "__main__":
  sys.exit(main())
