# Independent review notes — Cursor pass (Phase 1)

Shared source `/Users/camdouglas/agent-instructions` was **absent** on this VM. Review used the v1.2 pack patch + DesktopFly (21/25 baseline hashes matched).

## Ledger A (design) — retain

Claude's five disagreements with v1.1 are sound: consumers are hand copies; session-start/subagent loads dominated the seven-file count; seeding pulled forward; no native `~/.cursor/rules`; provider adapters are not ready.

## Ledger B (implementation) — verified on reconstructed tree

- 81/88 candidate hashes matched. Mismatches were consumer-local STATE/TOOLS/MEMORY/README/gitignore/LICENSE/LAUNCH (30 bytes).
- 8 retired rules removed; 3 always-on + 5 Agent-Requested as reported, plus Cursor R2 `cost-and-session.mdc`.
- Patch sha256 matches receipt `48fe6d24…`.
- Fixture bootstrap idempotent; 23 tests pass; eager-load guard fails on **unreplaced** consumer root `AGENTS.md` (W3 must replace it).

## Defects (smallest correction)

| ID | Location | Evidence | Consequence | Correction applied in R2? |
|---|---|---|---|---|
| D1 | `validate-agent-config.mjs` `alwaysOnRules` | omitted `karpathy-guidelines.mdc` | third always-on rule not enforced | yes |
| D2 | `.cursor/instructions/SUBAGENTS.md` | still mandated AGENTS/INSTRUCTIONS/ROLES/LAUNCH reads; not in eager-load scan | subagent preload regression | yes |
| D3 | git-safety `payloads/bootstrap.sh` and `payloads/validate-agent-config.mjs` | byte-stale vs R1 scripts | `apply-git-safety.sh` would revert R1 | yes |
| D4 | consumer root `AGENTS.md` | eager-load regex matches "On every substantive turn, read" | W3 validators fail until replaced | yes (owner-selected DesktopFly) |
| D5 | R1 removed Ask/ack exception | ping still implied preflight | cost regression vs objective | yes |
| D6 | `validate-launch.mjs` runbooks | unlinked runbook is an error | false failure in consumers (W4) | yes |

Inline adversarial review by Claude remains less independent than designed; Cursor security subagent provided one independent pass on DesktopFly.
