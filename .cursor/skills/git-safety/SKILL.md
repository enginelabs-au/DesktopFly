---
name: git-safety
description: >-
  Enforce Cursor anonymous git identity and block secrets, credentials, and
  passwords from any git action.
---

# Git safety

## Purpose

Prevent private-email git attribution and keep secrets out of git in every project that uses this control plane.

## When to use

- Any `git commit`, merge, rebase, cherry-pick, pull that can create a commit, annotated tag, note, or push
- Any staging command that might include secret-bearing files
- Before installing or validating repository hooks

## Inputs

- Repository root
- Intended git command

## Tools used

- `scripts/git-safety.mjs`
- `scripts/git-safety.test.mjs`
- `payloads/policy.mjs`
- `payloads/policy.test.mjs`
- `payloads/bootstrap.sh`
- `payloads/validate-agent-config.mjs`
- `payloads/cli.json`
- `payloads/git-privacy-and-secrets.mdc`
- `payloads/agent-governance.yml`
- Repository `.githooks/pre-commit`, `.githooks/commit-msg`, and `.githooks/pre-push`

## Procedure

1. Never run `git config` to set `user.name` or `user.email`.
2. Never use the host private email. Always export the Cursor anonymous identity:

```bash
GIT_AUTHOR_NAME='Cursor Agent' \
GIT_AUTHOR_EMAIL='cursoragent@noreply.github.com' \
GIT_COMMITTER_NAME='Cursor Agent' \
GIT_COMMITTER_EMAIL='cursoragent@noreply.github.com' \
git commit -m "message"
```

3. A GitHub noreply address (`*@users.noreply.github.com`) is also allowed. Any other email is forbidden.
4. Do not stage, commit, or push `.env*`, keys, credential JSON, `.netrc`, `.npmrc`, `.pypirc`, or files whose contents match secret patterns.
5. If bootstrap has not copied hooks yet, copy `.githooks/*` into `.git/hooks/` without changing git config.
6. If a hook or policy denies the command, stop. Do not weaken the hook.

## Expected outcome

Every agent-created git object uses `cursoragent@noreply.github.com` or a GitHub noreply address, and no secret value or secret-bearing file enters git.

## Validation

```bash
node --test .cursor/skills/git-safety/scripts/git-safety.test.mjs
node --test .cursor/hooks/policy.test.mjs
```

## Failure modes / cautions

- Host `user.email` is not an authorization signal. If it is a personal inbox, ignore it.
- Do not print secret values when a scan fails. Report only the path and rule id.
- Do not use `--no-verify` or rewrite hooks to bypass this skill.

## Related files

- `/USER.md`
- `/hooks/policy.mjs`
- `.githooks/`
- `/rules/git-privacy-and-secrets.mdc`
