---
schema_version: 1
task_id: 20260916-desktopfly-foundations
role_id: software-engineer-subagent
status: executing
revision: 1
created_at: 2026-09-16T12:06:00Z
updated_at: 2026-09-16T12:06:00Z
predecessor_handoff: docs/workstreams/20260916-desktopfly-foundations/ui-ux-developer-subagent/handoff.md
---

# Role Charter: software-engineer-subagent

## 1. Role objective

Materialize phase-0 files: fly-simulation rule, directory layout, frozen policy (`real_graph_enabled: false`), template pin, and a Linux foundations check.

## 2. Inherited request and evidence

PM + UX PASS. Phase-0 plan T0.4–T0.6.

## 3. Scope, non-goals, and ownership

- Write: `.cursor/rules/fly-simulation.mdc`, `config/*`, `provenance/template.json`, layout READMEs, `scripts/check-foundations.mjs`, README/.gitignore as needed
- Non-goals: LIF, Electron, Swift, template clone, MaleCNS download
- Prohibited: setting `real_graph_enabled` true; secrets; `--no-verify`

## 4–12.

Gate: `node scripts/check-foundations.mjs` exit 0 and preflight READY. Downstream: security review.
