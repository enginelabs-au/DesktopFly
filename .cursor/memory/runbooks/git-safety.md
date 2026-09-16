# Domain: Git safety

## Purpose

Record how anonymous git identity and secret blocking are installed and repaired.

## Procedure

- Required identity: `Cursor Agent <cursoragent@noreply.github.com>`. A `*@users.noreply.github.com` address is also allowed.
- Prefix commit-creating commands with `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and `GIT_COMMITTER_EMAIL`. Do not run `git config` to change identity.
- Install or repair protected files with `bash docs/handover/apply-git-safety.sh` or `bash docs/handover/apply-git-safety.sh /path/to/agent-instructions`.
- Bootstrap copies `.githooks/{pre-commit,commit-msg,pre-push}` into `.git/hooks/` without changing git config.
- `policy.mjs` must import `../skills/git-safety/scripts/git-safety.mjs`. A wrong relative import fail-closes every agent tool.

## Validation

- `node --test .cursor/hooks/policy.test.mjs .cursor/skills/git-safety/scripts/git-safety.test.mjs`
- `node .cursor/scripts/validate-agent-config.mjs`
- `node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs`
- Private-email `node .cursor/skills/git-safety/scripts/git-safety.mjs identity` exits 1.
- Cursor anonymous identity exits 0.
