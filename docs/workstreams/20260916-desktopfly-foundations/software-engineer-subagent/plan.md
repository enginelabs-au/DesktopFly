---
schema_version: 1
task_id: 20260916-desktopfly-foundations
role_id: software-engineer-subagent
status: executing
revision: 1
created_at: 2026-09-16T12:06:00Z
updated_at: 2026-09-16T12:06:00Z
---

# Role Plan: software-engineer-subagent

1. Write fly-simulation.mdc with the handover policy verbatim.
2. Add layout directories + short READMEs (no empty untracked dirs).
3. Commit handover `policy.json` unchanged except it already has `real_graph_enabled: false`.
4. Add desktop-pet / capabilities / state-contract / recovery-profiles stubs that cannot enable the graph.
5. Pin template SHA `38f55332055328d38c29e72474c4ad5b6876101f`.
6. Add `scripts/check-foundations.mjs`.
7. Ignore `data/raw/*` payloads; keep `.gitkeep`.
8. Validate with the check script and preflight.
