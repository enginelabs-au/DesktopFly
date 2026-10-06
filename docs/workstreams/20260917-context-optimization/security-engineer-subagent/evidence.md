# Security engineer evidence

W2 native subagent run: `security-engineer-subagent` Agent ID `bc-c6911470-355b-51e6-a856-43a89b973cee`, 2026-09-17. Parent materializes this file from the read-only return.

## Files the subagent reported reading

Charter-scoped: charter, plan, manifest, SWE handoff, ROLES.md §1–3 and own section, root `AGENTS.md`, `.cursor/AGENTS.md`, hooks.json, permissions.json, sandbox.json, policy.mjs, git-privacy rule, apply script.

Out of charter (W2 loading defect / stale session injection): `.cursor/INSTRUCTIONS.md`, `.cursor/instructions/SUBAGENTS.md`, `.cursor/STATE.md`.

Not read (W2 success vs Claude baseline preload): `.cursor/TOOLS.md`, `.cursor/instructions/LAUNCH.md`, `.cursor/instructions/STRATEGY.md`, other role sections, `.cursor/SKILLS.md`, `.cursor/USER.md`.

## Verdict

`PASS` for safeguards. Loading behavior `PARTIAL`: extra core files were read despite the adapter. The subagent attributed this to this Cloud Agent session still injecting retired always-on per-turn rules that are gone from disk.

## Safeguard observations (verbatim claims checked by parent)

- Apply payload omits hooks.json, permissions.json, sandbox.json, policy.mjs
- git-privacy `alwaysApply: true`
- Root `AGENTS.md` has no per-turn read-all wording
- W5 owner-only residual

Parent did not re-run a Customize-panel observation (unavailable in this Cloud Agent).
