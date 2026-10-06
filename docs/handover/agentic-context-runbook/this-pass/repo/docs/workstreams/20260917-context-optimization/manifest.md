# Workstream manifest

- Task ID: `20260917-context-optimization`
- Title: Context-loading R2 review, native validation, DesktopFly canary, pack v1.3
- Risk tier: Tier 3 — control-plane and git-safety adjacent; hooks/permissions/sandbox unchanged
- Mode: major change / resume of Claude R0→R1 plus Cursor second pass
- Status: implementation complete pending owner review of pack v1.3

## Objective

Reduce irrelevant and repeated context per accepted change through selective activation. Preserve capability, discovery, execution, and safeguards. Do not claim unmeasured token or cash savings. No new paid API spend.

## Required / skipped roles

| Role | Status | Reason |
|---|---|---|
| `product-manager-subagent` | skipped | No user-facing product, pricing, or acceptance-metric change |
| `ui-ux-developer-subagent` | skipped | No layout, interaction, or accessibility surface |
| `software-engineer-subagent` | required | Control-plane, validator, bootstrap, apply-route implementation |
| `security-engineer-subagent` | required | Independent check that hooks and git-safety were not weakened |
| `growth-marketing-subagent` | skipped | No positioning, acquisition, or experiment work |
| `project-lead-subagent` | required | Traceability, residual risk, owner handoff |

Routing decision by parent Agent on 2026-09-17 from `/instructions/ROLES.md` §3.3–3.4.

## Ownership

| Path | Writer | Reviewer |
|---|---|---|
| Protected control-plane files | parent via `docs/handover/apply-context-optimization-r2.sh` | `security-engineer-subagent` |
| Unprotected `.cursor/**` docs, templates, launch validator | parent / `software-engineer-subagent` | `security-engineer-subagent` |
| `docs/handover/agentic-context-runbook/` | parent | `project-lead-subagent` |
| `.cursor/STATE.md`, memory, workstream | parent | `project-lead-subagent` |

## Gates

- SWE implementation: validators and 23 tests pass after apply
- Security: hooks/permissions/sandbox byte-identity or equivalent; no secret in pack
- Project lead: pack labeled implemented/validated/proposed/deferred/blocked; no claimed savings

## Non-goals

- Registries, runners, provider adapters (R3–R4)
- Credential rotation (W5, owner-only)
- Global Cursor account/MCP/profile changes
- Opening the home directory as a workspace
- Weakening fail-closed hooks
