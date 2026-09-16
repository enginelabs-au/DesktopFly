---
schema_version: 1
task_id: 20260916-desktopfly-foundations
title: DesktopFly phase-0 foundations
source_request: Continue P-011 launch-pipeline; handover docs/handover/fruit-fly-cursor-handover.md
status: executing
risk_tier: high
created_at: 2026-09-16T12:03:00Z
updated_at: 2026-09-16T12:05:00Z
revision: 1
owner: lead-agent
active_role: software-engineer-subagent
current_gate: foundations-implementation
---

# Workstream Manifest: DesktopFly phase-0 foundations

## 1. Objective and requested outcome

Install phase-0 planning and repository foundations for DesktopFly. Neural simulation stays disabled while Q-012 is a release requirement.

## 2. Source request and project context

Cam authorized implementation. Previous owner archived without a pushed branch. Protocol: launch-pipeline → preflight → bootstrap → phase 0. P-011, MaleCNS v1.0, Electron + Swift.

## 3. Scope and non-goals

Scope: blueprint, phase-0 plan, decisions, role artifacts, fly rule, layout, policy, provenance, Linux check.  
Non-goals: LIF enable, template vendor, Mac certification, public launch.

## 4. Risk classification

- Impacted domains: product, UX, desktop, safety/ethics, local permissions later
- Product/user impact: defines the first shippable path (authored animation)
- Data/privacy: no user data in phase 0; later AX/ScreenCapture are sensitive
- Security/abuse: claim risk, capability isolation, no neural tool authority
- Production impact: none (local app, no deploy)
- Reversibility: high (docs + stubs)
- Release significance: sets the safety default for all later phases
- **Tier 3 — high:** Q-012 / sentience-claim surface plus future desktop permissions. Evidence: handover + working-constraints.

## 5. Role routing matrix

| Role ID | Required or skipped | Reason/evidence | Predecessor | Owned paths | Status | Handoff |
|---|---|---|---|---|---|---|
| `product-manager-subagent` | required | New product, DF-P01–P13, Q-012 release condition | intake | `docs/workstreams/20260916-desktopfly-foundations/product-manager-subagent/` | executing | `product-manager-subagent/handoff.md` |
| `ui-ux-developer-subagent` | required | Pet chrome, health language, a11y | PM | `.../ui-ux-developer-subagent/` | executing | `ui-ux-developer-subagent/handoff.md` |
| `software-engineer-subagent` | required | Rule, layout, policy, check script | UX | product trees in phase-0 plan §10 | executing | `software-engineer-subagent/handoff.md` |
| `security-engineer-subagent` | required | Tier 3; neural disable; isolation | SWE | read-only review | executing | `security-engineer-subagent/handoff.md` |
| `growth-marketing-subagent` | skipped | No acquisition, pricing, analytics taxonomy, or public launch in this task. First user is Cam. Lab article is deferred editorial (T-034). | — | — | skipped | none |
| `project-lead-subagent` | required | Tier 1–4 reconciliation | SEC | `delivery/` later | executing | `project-lead-subagent/handoff.md` |

## 6. Requirement traceability

| Requirement ID | Requirement | Source | Owner role | Acceptance evidence | Status |
|---|---|---|---|---|---|
| DF-P01 | Pet is default product | handover / blueprint | PM | blueprint §9 | specified |
| DF-P02 | Transparent click-through | handover | UX | UX charter | specified |
| DF-P03 | Follow window, no focus steal | handover | UX / SWE | later phase 3 | deferred |
| DF-P04 | MaleCNS v1.0 default | decision | SWE | decision file | accepted |
| DF-P05 | Neural sim disabled | Q-012 / Cam | PM / SEC | `real_graph_enabled: false` | implementing |
| DF-P06 | Authored animation live path | blueprint | SWE | phase map | specified |
| DF-P07 | No affect/needs/learning | handover rule | SEC | fly-simulation.mdc | implementing |
| DF-P08 | Supervisor latch; no neural tool auth | handover | SEC | rule + architecture | specified |
| DF-P09 | 2048 / 100000 caps | handover policy | SWE | policy.json | implementing |
| DF-P10 | Loopback runtime net | handover | SWE / SEC | policy `network_bind` | implementing |
| DF-P11 | Plain-language health | handover §4.1 | UX / PM | UX plan | specified |
| DF-P12 | Screen capture default off | policy | SEC / UX | policy.json | implementing |
| DF-P13 | Attribution | template license | PM | provenance/template.json | implementing |

## 7. Dependency and gate order

Intake → PM → UX → SWE implement foundations → SEC review → PL reconcile → owner PR review. Growth skipped.

## 8. Path and external-system ownership

| Path or system | Writer | Read-only reviewers | Allowed operation | Ownership window |
|---|---|---|---|---|
| `docs/blueprints/*` | lead | PM, PL | create/update | phase 0 |
| `docs/plans/phase_0_foundations_plan.md` | lead | all required roles | create/update | phase 0 |
| `docs/workstreams/20260916-desktopfly-foundations/**` | lead | roles (own dirs conceptually) | create/update | phase 0 |
| `.cursor/rules/fly-simulation.mdc` | SWE / lead | SEC | create | phase 0 |
| `config/**`, `provenance/**`, `scripts/check-foundations.mjs` | SWE / lead | SEC | create | phase 0 |
| `.cursor/STATE.md`, memory | lead | PL | update | continuous |
| GitHub `enginelabs-au/desktopfly` | lead | — | branch + PR | this task |
| Cam’s Mac / production | none | — | none | not in scope |

## 9. Tool and MCP constraints

No production APIs. Web search used for MaleCNS, template, desktop-pet substitutes. Git via anonymous identity. No Figma file supplied.

## 10. Decisions, clarifications, and provisional assumptions

- Neural disable: **verified** (Cam + Q-012).
- MaleCNS / Electron+Swift: **verified**.
- Template SHA: **provisional**.
- Lead-materialized roles: **provisional**.
- Q-012 scientific resolution: **not blocking** authored path; **blocking** neural enable.

## 11. Active blockers and remediation loops

None for phase 0. Q-012 is a later enable-gate, not a phase-0 blocker.

## 12. Artifact and evidence index

- Blueprint, phase-0 plan, three decisions
- Role files under this workstream
- `scripts/check-foundations.mjs` (after SWE)

## 13. Residual risks and human actions

Mac verification, template license, MaleCNS download, Q-012 reframing — deferred.

## 14. Owner decisions and approvals

Cam authorized implementation and continuation. No new Cam question this gate.

## 15. Closure

- Final verdict: open
- Owner handoff: not yet
- Remaining manual actions: see phase-0 deferred queue
