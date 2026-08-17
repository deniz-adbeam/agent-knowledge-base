# Security Policy

## Reporting a vulnerability

Please report security vulnerabilities **privately** — do not open a public issue for
anything security-sensitive.

Use GitHub's private reporting: go to the repository's **Security** tab →
**Report a vulnerability** (GitHub Security Advisories). This keeps the report confidential
until a fix is available.

Please include:

- a description of the issue and its potential impact,
- steps to reproduce (or a proof of concept), and
- the affected file(s)/version if known.

## Scope

This project is a copy-paste template consisting of Markdown notes and small, dependency-free
Python tooling (`tools/build-graph.py`, `tools/okf-lint.py`) plus a shell helper (`kb.sh`).
The most relevant concerns are:

- accidental inclusion of secrets or PII in committed knowledge/memory notes, and
- unsafe handling of untrusted input by the tooling.

The generated artifacts (`graph.json`, `graph.html`) are self-contained and meant to be viewed
locally or served as static files.

## Response

We aim to acknowledge a valid report within a reasonable time, agree on a disclosure timeline,
and credit reporters who wish to be credited once a fix is released.
