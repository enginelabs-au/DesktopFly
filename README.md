# DesktopFly

Connectome-informed macOS desktop pet: a frameless, transparent, click-through fly that follows the selected window. The workbench and health dashboard open only on request.

This repository is initialized with the agent control plane and the implementation handover. Application source is not implemented yet.

## Start here

- Product and implementation spec: [`docs/fruit-fly-cursor-handover.md`](docs/fruit-fly-cursor-handover.md)
- Agent entry: [`AGENTS.md`](AGENTS.md)
- Lifecycle: `/launch-pipeline`

## Local agent bootstrap

```bash
node .cursor/skills/launch-pipeline/scripts/preflight.mjs
bash .cursor/scripts/bootstrap.sh
```
