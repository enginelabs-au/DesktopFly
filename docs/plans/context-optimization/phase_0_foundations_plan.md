# Phase 0 — context-loading optimization foundations

- Status: implemented on DesktopFly canary (2026-09-17)
- Task: `20260917-context-optimization`

## Objective

Selective activation of control-plane context. Preserve git-safety and fail-closed hooks. No unmeasured savings claims. No new paid API spend.

## End-state map

| Phase | Intent |
|---|---|
| 0 (this) | R1 reconstruction, R2 fixes, DesktopFly canary, pack v1.3 |
| 1 | Fresh-session W1 on DesktopFly; copy to shared source Mac if hashes should match |
| 2 | Optional papership / other consumers after W1 |
| 3 | Owner W5/W6/W7/W10 only |

## Role matrix

See `docs/workstreams/20260917-context-optimization/manifest.md`.

## Next plan generation prompt

Only after a fresh Cursor session records W1 (a)(d)(e)(f) with Customize-panel or rule-indicator evidence: create `docs/plans/phase_1_fresh_session_w1_plan.md` listing exact prompts and pass/fail. Do not generate it speculatively.
