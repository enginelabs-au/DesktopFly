---
schema_version: 1
task_id: 20260916-desktopfly-foundations
role_id: software-engineer-subagent
revision: 1
updated_at: 2026-09-16T12:08:00Z
---

# Role Evidence: software-engineer-subagent

## Evidence record

- Requirement ID: DF-P05
- Claim: Policy ships with the real graph disabled
- Evidence state: VERIFIED after `node scripts/check-foundations.mjs`
- Method: JSON parse + exact-key assertions
- Artifact: `config/policy.json`

## Evidence record

- Requirement ID: DF-P07
- Claim: Fly-simulation rule is installed with alwaysApply
- Evidence state: VERIFIED by file presence and required prohibition line
- Artifact: `.cursor/rules/fly-simulation.mdc`
