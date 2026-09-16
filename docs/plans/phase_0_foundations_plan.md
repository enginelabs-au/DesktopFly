---
plan: phase_0_foundations
status: complete
created: 2026-09-16
updated: 2026-09-16
owner: lead-agent
source_phase: none
workstream: docs/workstreams/20260916-desktopfly-foundations/manifest.md
blueprint: docs/blueprints/2026-09-16_desktopfly.md
---

# Phase 0: Foundations

## 1. Objective

Establish the DesktopFly repository so later phases can implement the macOS desktop pet without reinventing safety, layout, or dataset rules. Phase 0 maps the full product and installs only foundational files: planning artifacts, the fly-simulation rule, committed directory layout, frozen policy with the neural graph **off**, and a pinned anatomy-template SHA.

## 2. Relation to project end-state

End-state: a frameless, click-through MaleCNS-attributed fly on Cam’s Apple Silicon Mac. While Q-012 remains a release requirement, the live controller is authored animation plus anatomy viewing. Handover phases 1–4 are later implementation gates. This phase does not ship the pet.

## 3. Entry criteria and inherited evidence

- Launch authorized by Cam; previous owner `bc-dab50473` archived; branch `cursor/phase-0-foundations-6edd` never pushed.
- `main` @ `61c436f` includes `LAUNCH.md`.
- Preflight was `MATERIALIZATION_REQUIRED` (`docs/blueprints` missing). Bootstrap `bash .cursor/scripts/bootstrap.sh` then reported `READY`.
- Spec: `docs/handover/fruit-fly-cursor-handover.md`.
- Decisions: neural sim disabled; MaleCNS v1.0; Electron + Swift.

## 4. Scope

- Blueprint, this plan, decisions, workstream + role artifacts
- `.cursor/rules/fly-simulation.mdc` (exact handover policy)
- Directory skeleton: `backend/`, `src/`, `desktop/`, `native/`, `config/`, `data/`, `reports/`, `provenance/`
- `config/policy.json` with `real_graph_enabled: false`
- Template pin in `provenance/template.json`
- Policy parse test that fails if the graph flag is true
- STATE / memory / README updates
- Linux-runnable validation only

## 5. Non-goals

- Clone or vendor the full cobanov template
- Download MaleCNS weights
- Implement LIF, Electron, or Swift
- Enable the neural worker
- Mac overlay / MPS / Accessibility certification
- Public Lab copy or growth campaigns
- Resolve Q-012

## 6. Current-state audit

Control plane + handover only. No `backend/`, `src/`, `desktop/`, `native/`, `data/`, or product `config/`. Preflight READY after bootstrap. This environment is Linux; Apple Silicon gates cannot run here.

## 7. Assumptions, constraints, risks, and decisions

| Item | Kind | Note |
|---|---|---|
| Q-012 remains a release requirement | verified constraint | Neural sim stays disabled |
| MaleCNS v1.0 default | accepted | FlyWire is a later adapter |
| Electron + Swift, not Tauri | accepted | Distinct from Papership |
| Template HEAD `38f55332055328d38c29e72474c4ad5b6876101f` | provisional pin | Re-check before vendoring; license not legally reviewed |
| Linux CI ≠ Mac proof | verified | Defer native gates |
| Lead materializes role artifacts | provisional | Stay on Fly; no separate role processes this run |

Risks: template license, invented cell-type lists, claiming Mac results from Linux.

## 8. Dependencies

Phase 0 → 1 (ingest/synthetic fixture) → 2 (authored motion; LIF code inert) → 3 (Electron/Swift) → 4 (health/supervisor) → final checklist. Mac hardware is required from phase 3. Q-012 blocks *enabling* LIF, not writing gated code.

## 9. Architecture and affected systems

See blueprint §10. Phase 0 only commits the tree and policy. One presentation clock later; no second production neural clock while the flag is false.

## 10. Files and paths in scope

- `docs/blueprints/2026-09-16_desktopfly.md`
- `docs/plans/phase_0_foundations_plan.md`
- `docs/decisions/2026-09-16-neural-sim-disabled-q012.md`
- `docs/decisions/2026-09-16-malecns-default-dataset.md`
- `docs/decisions/2026-09-16-electron-swift-shell.md`
- `docs/workstreams/20260916-desktopfly-foundations/**`
- `.cursor/rules/fly-simulation.mdc`
- `config/policy.json`, `config/desktop-pet.json`, `config/capabilities.json`, `config/state-contract.json`, `config/recovery-profiles.json`
- `provenance/template.json`
- `backend/`, `src/`, `desktop/`, `native/DesktopContext/`, `data/raw/`, `data/derived/`, `data/reviews/`, `reports/`
- `scripts/check-foundations.mjs`
- `README.md`, `.gitignore`, `.cursor/STATE.md`, `.cursor/memory/**`

## 11. Supporting documents to create or update

Blueprint (done), this plan, three product decisions (done), workstream, fly rule, policy/provenance, README.

## 12. Ordered implementation tasks

### T0.1 Bootstrap and control plane
- **Status:** complete
- **Evidence:** bootstrap exit 0; preflight `READY`

### T0.2 Strategy and decisions
- **Status:** complete
- **Files:** blueprint + three decisions

### T0.3 Workstream and role artifacts
- **Status:** complete
- **Files:** `docs/workstreams/20260916-desktopfly-foundations/`

### T0.4 Fly-simulation rule
- **Status:** complete
- **File:** `.cursor/rules/fly-simulation.mdc` — exact handover body

### T0.5 Layout, policy, provenance
- **Status:** complete
- **Validation:** `node scripts/check-foundations.mjs` passed 2026-09-16

### T0.6 State/memory/README
- **Status:** complete

### T0.7 Commit, push, PR
- **Status:** complete
- **Evidence:** https://github.com/enginelabs-au/DesktopFly/pull/2

## 13. Adaptive role and delegation map

| Role ID | Required or skipped | Reason | Predecessor | Owned paths | Gate evidence | Status |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | New product scope, DF-P* requirements | intake | workstream PM dir; PRD in blueprint | charter/plan/evidence/handoff | planning |
| `ui-ux-developer-subagent` | required | Pet presentation, a11y, health language | PM | workstream UX dir | same | planning |
| `software-engineer-subagent` | required | Layout, policy, rule, check script | UX | product trees listed above | check-foundations + preflight | planning |
| `security-engineer-subagent` | required | Q-012, permissions, isolation | SWE | review only | security handoff | planning |
| `growth-marketing-subagent` | skipped | Local first-user pet; no acquisition/pricing this workstream | — | — | skip in manifest | skipped |
| `project-lead-subagent` | required | Tier 3 reconciliation | SEC | delivery notes | PL handoff | planning |

Parent lead materializes role files. Growth skip is recorded, not a missing row.

## 14. Test and validation matrix

| Requirement | Validation method | Expected evidence | Status |
|---|---|---|---|
| Bootstrap | preflight after bootstrap | `READY` | pass |
| Neural flag off | `scripts/check-foundations.mjs` | `real_graph_enabled === false` | pending |
| Fly rule present | file + frontmatter | exact policy text | pending |
| Template pin | JSON SHA | 40-char SHA | pending |
| No secrets | git-safety hooks | commit allowed | pending |
| Mac overlay | n/a this phase | deferred | deferred |

## 15. Security, privacy, reliability, accessibility, and performance checks

No screen capture, no raw connectome in git, loopback-only later, click-through specified not implemented, no performance claims.

## 16. Environment-variable registry

| Variable name | Purpose | Scope | Required by phase | Source | Status |
|---|---|---|---|---|---|
| `HERMES_HOME` | not used by DesktopFly | — | never | — | not applicable |
| `PYTORCH_ENABLE_MPS_FALLBACK` | must stay unset/off if LIF ever runs | Mac worker | phase 2+ | host | deferred; reject if `1` |
| `DESKTOPFLY_POLICY_PATH` | optional override for tests | local/CI | phase 1 | repo | not created yet |

No secret values. No credentials required for phase 0.

## 17. Deferred human-action queue

| Action | Why agent cannot | Earliest phase | Blocking now? | Final-checklist |
|---|---|---|---|---|
| Run overlay/permission matrix on Cam’s Mac | No Apple Silicon here | 3 | no | yes |
| Confirm template license for bundling | Legal acceptance | 3 | no | yes |
| Download MaleCNS weights | Large optional dataset; Q-012 off | 1 setup | no | yes |
| Reframe or close Q-012 | Owner decision | before neural enable | no for authored path | yes |
| Public Lab article | Editorial + evidence | after pet exists | no | yes |

## 18. Rollback and recovery

Revert the feature branch. Policy and rule are additive. Do not `git reset` user machines during later recovery (handover forbids that).

## 19. Acceptance criteria

- [x] Bootstrap followed and preflight READY
- [x] Blueprint and product decisions exist
- [x] Phase-0 plan + workstream + required role artifacts exist
- [x] Fly-simulation rule installed
- [x] Policy JSON frozen with graph disabled
- [x] Template SHA recorded
- [x] Foundations check passes on Linux
- [x] STATE/memory match reality
- [x] PR opened from this branch

## 20. Completion evidence

- `bash .cursor/scripts/bootstrap.sh` exit 0
- `node .cursor/skills/launch-pipeline/scripts/preflight.mjs` → `READY`
- `node scripts/check-foundations.mjs` → `foundations check passed`
- `node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs` → 91 control-plane files

## 21. Deviations and follow-ups

- Did not resume `cursor/phase-0-foundations-6edd` (absent on origin).
- Role work materialized by the lead in-repo rather than separate subagent VMs.

## 22. Next Plan Generation Prompt

Read `/AGENTS.md`, the complete core agent context, `/instructions/PROJECT_PLANNING.md`, `/instructions/ROLES.md`, this completed `docs/plans/phase_0_foundations_plan.md`, `docs/blueprints/2026-09-16_desktopfly.md`, `docs/workstreams/20260916-desktopfly-foundations/manifest.md` and role handoffs, all completion evidence, current repository state, and active blockers. Confirm phase 0 and every required role gate are implemented and validated. Then generate exactly one exhaustive next phase plan at `docs/plans/phase_1_safe_ingest_plan.md` for handover Phase 1 (MaleCNS-qualified ingest, synthetic fixture, `real_graph_enabled` remaining false). Derive it from this roadmap and verified current state. Do not implement phase 1 until that plan is written.
