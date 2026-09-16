# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. The workbench and health dashboard open only on request.

While Q-012 (absolute proof of zero possible suffering) remains a release requirement, the **neural simulation stays disabled**. The live path is anatomy viewing plus an authored animation controller.

Default dataset: **MaleCNS v1.0**. Shell: **Electron + Swift helper**, not Papership Tauri.

## Start here

- Product spec: [`docs/handover/fruit-fly-cursor-handover.md`](docs/handover/fruit-fly-cursor-handover.md)
- Blueprint: [`docs/blueprints/2026-09-16_desktopfly.md`](docs/blueprints/2026-09-16_desktopfly.md)
- Phase 0: [`docs/plans/phase_0_foundations_plan.md`](docs/plans/phase_0_foundations_plan.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)
- Lifecycle: `/launch-pipeline`

## Local checks

```bash
node .cursor/skills/launch-pipeline/scripts/preflight.mjs
bash .cursor/scripts/bootstrap.sh
node scripts/check-foundations.mjs
```
