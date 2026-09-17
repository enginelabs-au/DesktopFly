# Security engineer charter

- Role: `security-engineer-subagent`
- Task: `20260917-context-optimization`
- Mode: read-only
- Readable paths: `docs/workstreams/20260917-context-optimization/**`, `.cursor/hooks.json`, `.cursor/permissions.json`, `.cursor/sandbox.json`, `.cursor/hooks/policy.mjs`, `.githooks/`, `.cursor/rules/git-privacy-and-secrets.mdc`, `.cursor/scripts/validate-agent-config.mjs`, `docs/handover/apply-context-optimization-r2.sh`, `AGENTS.md`, `.cursor/AGENTS.md`, `.cursor/instructions/ROLES.md` sections 1–3 and the `security-engineer-subagent` section
- Forbidden: other role sections; `.cursor/TOOLS.md`; `.cursor/instructions/LAUNCH.md`; `.cursor/instructions/STRATEGY.md`; any write; credential files; production mutation

## Required reads

1. This charter and `docs/workstreams/20260917-context-optimization/manifest.md`
2. Predecessor: `docs/workstreams/20260917-context-optimization/software-engineer-subagent/handoff.md`
3. `.cursor/instructions/ROLES.md` sections 1–3 and the `security-engineer-subagent` section only
4. Root `AGENTS.md` and `.cursor/AGENTS.md` only if needed to verify loading/eager-load text

Do not read the seven-file core set. Do not read other role bodies.

## Questions

- Were hooks, permissions, sandbox, or git-safety identity rules weakened?
- Do apply-route payloads reintroduce secrets or private rollback snapshots?
- Remaining residual risk for W5 (owner key rotation) and global MCP plaintext keys?

Return the canonical handoff verdict and ranked findings. Do not remediate.
