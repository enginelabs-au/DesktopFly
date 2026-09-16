# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. The workbench and health dashboard open only on request.

**Neural / LIF simulation is enabled** (Cam override 2026-09-16). Authored animation remains for Find fly / presentation fallback. MaleCNS weights under `data/raw/` are still a download prerequisite for the full connectome; CI uses the synthetic graph.

Default dataset: **MaleCNS v1.0**. Shell: **Electron + Swift helper**, not Papership Tauri.

## Start here

- Product spec: [`docs/handover/fruit-fly-cursor-handover.md`](docs/handover/fruit-fly-cursor-handover.md)
- Blueprint: [`docs/blueprints/2026-09-16_desktopfly.md`](docs/blueprints/2026-09-16_desktopfly.md)
- Phase 3: [`docs/plans/phase_3_electron_swift_shell_plan.md`](docs/plans/phase_3_electron_swift_shell_plan.md)
- Phase 4 plan: [`docs/plans/phase_4_supervisor_health_plan.md`](docs/plans/phase_4_supervisor_health_plan.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)
- Lifecycle: `/launch-pipeline`

## Local checks

```bash
node .cursor/skills/launch-pipeline/scripts/preflight.mjs
bash .cursor/scripts/bootstrap.sh
node scripts/check-foundations.mjs
PYTHONPATH=backend python3 -m pytest -q backend/tests
node --test src/pet/authored-motion.test.mjs desktop/desktop.test.mjs
```
