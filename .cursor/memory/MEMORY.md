# Working memory

## Durable directives

- DesktopFly default dataset is MaleCNS v1.0. FlyWire v783 is a separate adapter.
- Neural / LIF simulation stays disabled while Q-012 is a release requirement. Live path: anatomy + authored animation.
- Desktop shell is Electron + Swift helper, not Papership Tauri.
- Product spec: `docs/handover/fruit-fly-cursor-handover.md`. Blueprint: `docs/blueprints/2026-09-16_desktopfly.md`.
- Execute agent-capable work directly; do not delegate routine implementation or investigation to the user.
- Use the sequential planning lifecycle for new projects and major implementations: phase 0 maps the full project, each later phase plan is generated only after the previous phase is implemented and verified, and closure produces `docs/plans/final_implementation_checklist.md`.
- Defer non-blocking human-only actions and missing credential values to the final phase while completing all possible code, configuration, adapters, tests, documentation, and environment-variable wiring first.
- Read `/AGENTS.md` first on every substantive turn and route detailed instructions through `/INSTRUCTIONS.md`.
- Use `/launch-pipeline` and `/instructions/LAUNCH.md` as the linked entry point for a raw idea, major change, resume, remediation, or closure.
- Launch is preflight-first and bootstrap-gated: run read-only `/skills/launch-pipeline/scripts/preflight.mjs` before mode selection. Every pre-Build Cursor plan must close with `bash .cursor/scripts/bootstrap.sh` as the first post-Build action, then run that command after Build or explicit Agent-mode implementation authorization.
- Use adaptive role routing for substantive work: record required/skipped canonical roles, require role charters before action, and preserve evidence-backed handoffs under `docs/workstreams/`.
- Treat prompts and role identities as guidance, not production authorization; deterministic policy and external access controls govern sensitive actions.
- Never store passwords, tokens, private keys, or secret values in agent markdown, plans, memories, logs, or templates.
- Git writes must use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Never use a private inbox or `git config` identity changes. Canonical procedure: `/skills/git-safety/SKILL.md`.

## Memory role

This file is a concise durable memory and index. Store only standing directives, stable decisions, high-level architecture notes, and links to canonical detail.

Operational history belongs in `/memory/memories/YYYY-MM-DD-continuation.md` or a topic-specific memory. Unresolved issues belong in `blockers/`; exact procedures belong in `runbooks/`; stable repeatable procedures belong in `/skills/`.

## System index

- Operating contract: `/AGENTS.md`
- Startup: `/BOOTSTRAP.md` and `/scripts/bootstrap.sh`
- Instruction router: `/INSTRUCTIONS.md`
- Product lifecycle launcher: `/instructions/LAUNCH.md` and `/skills/launch-pipeline/SKILL.md`
- Project planning: `/instructions/PROJECT_PLANNING.md`
- Product strategy: `/instructions/STRATEGY.md`
- Sub-agent orchestration: `/instructions/SUBAGENTS.md`
- Canonical roles and stage gates: `/instructions/ROLES.md`
- Native role adapters: `/agents/`
- Live state: `/STATE.md`
- Plans: `docs/plans/`
- Strategic blueprints: `docs/blueprints/`
- Decisions: `docs/decisions/`
- Task workstreams and role handoffs: `docs/workstreams/`
- Agent role pipeline decision: `docs/decisions/2026-08-18-agent-role-pipeline.md`
- External governance setup: `docs/handover/agent-governance-operator-setup.md`
- Skills: `/SKILLS.md` and `/skills/`
- Git safety: `/skills/git-safety/SKILL.md` and `/memory/runbooks/git-safety.md`
- Git identity decision: `docs/decisions/2026-09-16-git-anonymous-identity.md`
- Neural-sim disable: `docs/decisions/2026-09-16-neural-sim-disabled-q012.md`
- MaleCNS default: `docs/decisions/2026-09-16-malecns-default-dataset.md`
- Electron/Swift shell: `docs/decisions/2026-09-16-electron-swift-shell.md`
- Phase 0: `docs/plans/phase_0_foundations_plan.md`
- Phase 1: `docs/plans/phase_1_safe_ingest_plan.md` (complete)
- Phase 2: `docs/plans/phase_2_authored_motion_plan.md`
- Workstream: `docs/workstreams/20260916-desktopfly-foundations/manifest.md`
- Tools: `/TOOLS.md`
- Active blockers: `/memory/blockers/`
- Runbooks: `/memory/runbooks/`
- Agent workspace layout: `/memory/runbooks/agent-workspace.md`
- Bootstrap procedure: `/memory/runbooks/agent-config-bootstrap.md`

## Repository

- Git remote: `https://github.com/enginelabs-au/DesktopFly.git`
- Product spec: `docs/handover/fruit-fly-cursor-handover.md`

## Existing workflow references

- Vercel: `/skills/vercel-deploy-workflow/SKILL.md` and `/memory/runbooks/vercel-workflow.md`
- Supabase: `/skills/supabase-linked-migrations/SKILL.md` and `/memory/runbooks/supabase-cli-macos.md`
