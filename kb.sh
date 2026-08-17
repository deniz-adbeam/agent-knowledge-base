#!/usr/bin/env bash
# Agent Knowledge Base helper — one command from fresh clone to interactive graph.
#
# Usage:
#   ./kb.sh            check prerequisites, build graph, lint, open graph.html
#   ./kb.sh build      check + build only (no browser)
#   ./kb.sh lint       check + lint only
#   ./kb.sh open       open the graph (builds first if missing)
#   ./kb.sh check      prerequisites check only
#   ./kb.sh help       this help

set -euo pipefail

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YELLOW=$'\033[33m'; RESET=$'\033[0m'
ok()   { echo "  ${GREEN}✓${RESET} $*"; }
fail() { echo "  ${RED}✗${RESET} $*"; }
info() { echo "${BOLD}$*${RESET}"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MIN_PY_MINOR=8   # python >= 3.8 (stdlib only, no pip installs needed)

check() {
  info "Checking prerequisites…"
  local errors=0

  # 1. Repo layout — are we where we think we are?
  if [[ -f tools/build-graph.py && -d knowledge && -d memory ]]; then
    ok "repository layout (tools/, knowledge/, memory/)"
  else
    fail "this doesn't look like an agent-knowledge-base repo root (missing tools/build-graph.py, knowledge/ or memory/)"
    errors=$((errors+1))
  fi

  # 2. Python 3 present?
  if command -v python3 >/dev/null 2>&1; then
    local ver major minor
    ver="$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    major="${ver%%.*}"; minor="${ver##*.}"
    if [[ "$major" -eq 3 && "$minor" -ge $MIN_PY_MINOR ]]; then
      ok "python3 $ver (need >= 3.$MIN_PY_MINOR, stdlib only — no pip install required)"
    else
      fail "python3 $ver found, but >= 3.$MIN_PY_MINOR required"
      errors=$((errors+1))
    fi
  else
    fail "python3 not found — install it via https://www.python.org/downloads/ (macOS: 'brew install python3')"
    errors=$((errors+1))
  fi

  # 3. Knowledge content present? (knowledge/ + memory/)
  local count
  count="$(find knowledge memory -name '*.md' ! -name 'index.md' ! -name 'log.md' 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "$count" -gt 0 ]]; then
    ok "$count knowledge/memory concepts found"
  else
    fail "no concepts found in knowledge/ or memory/ — is the clone complete?"
    errors=$((errors+1))
  fi

  if [[ $errors -gt 0 ]]; then
    echo
    echo "${RED}${BOLD}$errors problem(s) found — fix the above and re-run.${RESET}"
    exit 1
  fi
  echo
}

template_notice() {
  if [[ -f .okf-template-version ]]; then
    local v; v="$(cat .okf-template-version)"
    echo "${BOLD}This repo is a copy of agent-knowledge-base@${v}${RESET} — changelog: https://github.com/deniz-adbeam/agent-knowledge-base/blob/main/CHANGELOG.md"
    echo
  fi
}

build() {
  info "Building graph…"
  python3 tools/build-graph.py
  echo
}

lint() {
  info "Linting (OKF conformance)…"
  if python3 tools/okf-lint.py; then
    ok "knowledge base is conformant"
  else
    echo "${YELLOW}Lint reported ERRORs — see output above (WARNs are fine).${RESET}"
    exit 1
  fi
  echo
}

open_graph() {
  if [[ ! -f graph.html ]]; then
    build
  fi
  info "Opening graph.html…"
  case "$(uname -s)" in
    Darwin) open graph.html ;;
    Linux)  xdg-open graph.html >/dev/null 2>&1 || echo "  open graph.html manually in your browser" ;;
    MINGW*|MSYS*|CYGWIN*) start graph.html 2>/dev/null || echo "  open graph.html manually in your browser" ;;
    *) echo "  open graph.html manually in your browser" ;;
  esac
}

case "${1:-all}" in
  all)   template_notice; check; build; lint; open_graph
         echo "${GREEN}${BOLD}Done.${RESET} Drag nodes, scroll to zoom, click a node for details." ;;
  build) check; build ;;
  lint)  check; lint ;;
  open)  open_graph ;;
  check) check; echo "${GREEN}${BOLD}All good.${RESET}" ;;
  help|-h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//' | sed -n '2,10p' ;;
  *) echo "Unknown command: $1 (try: ./kb.sh help)"; exit 1 ;;
esac
