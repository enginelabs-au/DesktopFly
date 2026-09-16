# STATE.md

## Current Objective

- Enforce Cursor anonymous git identity and keep secrets out of git in the DesktopFly control plane and the `agent-instructions` templates.

## Current Status

- Complete — git-safety rules, hooks, policy, skill, and validators are installed in both trees. Preflight is `READY`.

## Project Phase

- Repository initialized. Product implementation has not started.

## Active Plan

- None.

## Active Workstream

- None.

## Active Role and Gate

- None.
- Last integrated validation: `PASS`.

## Predecessor Handoff

- None.

## Pending Remediation

- None recorded.

## Owner Decision

- Git writes must use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Secrets, credentials, and passwords must never enter git.

## Active Instructions

- None.

## Active Items

- External controls in `docs/handover/agent-governance-operator-setup.md` remain owner-configured.
- Product implementation should start through `/launch-pipeline` using `docs/handover/fruit-fly-cursor-handover.md`.
- Owner requested commit and push of the git-safety controls.

## Files in Active Use

- `/AGENTS.md`
- `/USER.md`
- `/STATE.md`
- `/INSTRUCTIONS.md`
- `/SKILLS.md`
- `/TOOLS.md`
- `/memory/MEMORY.md`
- `/skills/git-safety/SKILL.md`
- `/rules/git-privacy-and-secrets.mdc`
- `/hooks/policy.mjs`
- `.githooks/`

## Open Blockers

- None.

## Attempts Performed

- Added `/skills/git-safety`, `.githooks`, standing USER/TOOLS/SKILLS directives, and secret-aware `.gitignore` entries in DesktopFly and `agent-instructions`.
- Applied protected policy, rule, bootstrap, validator, CLI, and workflow files via `docs/handover/apply-git-safety.sh`.
- First apply used a wrong relative import in `policy.mjs`; fail-closed hooks blocked all tools until the owner repaired the import to `/skills/git-safety/scripts/git-safety.mjs`.
- Revalidated: 16 policy/git-safety tests pass in both trees; DesktopFly bootstrap and preflight are `READY`; launch validation classifies 89 control-plane files. Private-email identity check exits 1; Cursor anonymous identity exits 0.

## Decisions and Assumptions

- Required agent git identity is `cursoragent@noreply.github.com`. `*@users.noreply.github.com` is also allowed. Any other inbox is forbidden.
- Agents must not run `git config` to change identity. Bootstrap copies `.githooks/` into `.git/hooks/` without changing git config.
- Secret-bearing paths and high-confidence secret content are blocked by policy, git hooks, CLI denials, and `.gitignore`.

## Current Working State

- DesktopFly hooks are installed at `.git/hooks/{pre-commit,commit-msg,pre-push}`.
- Template tree at `/Users/camdouglas/agent-instructions` contains the same skill, rules, policy, and `.githooks`.

## Next Actions

- Start product work with `/launch-pipeline` against `docs/handover/fruit-fly-cursor-handover.md`.

## Last Updated

- 2026-09-16 — installed git-safety anonymous-identity and secret-blocking controls.
