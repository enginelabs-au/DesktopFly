# Software engineer charter

- Role: `software-engineer-subagent`
- Task: `20260917-context-optimization`
- Mode: write within delegated paths
- Non-goals: hook/permission/sandbox edits; credential handling; consumer repos other than DesktopFly

## Scope

- Reconstruct and review Claude R1 against `candidate-source-manifest.json`
- Apply R1 plus Cursor R2 corrections to DesktopFly via the owner apply route
- W4 launch-validator project-local runbooks
- Sync git-safety payloads for bootstrap and config validator
- Pack v1.3 evidence

## Validation

- `node .cursor/scripts/validate-agent-config.mjs`
- `node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs`
- `node .cursor/skills/launch-pipeline/scripts/preflight.mjs`
- `node --test` policy, git-safety, preflight (23)
