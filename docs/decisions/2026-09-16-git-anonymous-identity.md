# Git anonymous identity and secret blocking

Date: 2026-09-16

## Decision

Agent git writes use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Private inboxes are forbidden. Secrets, credentials, passwords, tokens, and private keys must not enter git.

## Why

A host git inbox can be a private address. GitHub rejects those pushes, and the address should not appear in history. Secret-bearing files must be blocked by policy, hooks, and ignore rules, not by agent memory alone.

## Consequences

- Cursor policy denies commit-creating commands that omit the anonymous identity or name a secret path.
- Repository hooks refuse non-anonymous authors and staged secret files.
- Bootstrap installs hooks by copying files; it does not change git config.
- The same controls live in `/Users/camdouglas/agent-instructions` for future projects.

## Canonical procedure

`/skills/git-safety/SKILL.md`
