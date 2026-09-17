# 13 · Implementation receipt — Cursor second pass (v1.3)

Phase: independent review of Claude R1, native validation attempt (W1/W2), R2 defect fixes, DesktopFly canary. Executor: Cursor Cloud Agent (model Cursor Grok 4.6) on Linux, 2026-09-17. Nothing in this receipt is an acceptance verdict; GPT reviews next.

## Active paths and versions

| Item | Value |
|---|---|
| Shared source | `/Users/camdouglas/agent-instructions` **not present** on this VM |
| Reconstruction | v1.2 patch sha256 `48fe6d24df1bc5103b2724b45ed645711a2db32c6fa67fde6593ab68958aeb0c` applied to DesktopFly (21/25 baseline hashes matched) |
| Consumer touched | `DesktopFly` (`/workspace`, remote `enginelabs-au/DesktopFly`) |
| Global client config touched | none |
| Branch | `cursor/context-optimization-r2-0433` |
| Apply route | `docs/handover/apply-context-optimization-r2.sh` |
| Pack | `docs/handover/agentic-context-runbook/` v1.3 |

## Rollback

Do not use Claude's private Mac tarball from this VM. DesktopFly rollback:

```bash
git checkout main -- AGENTS.md .cursorignore .cursor/
# or revert the PR
```

Protected files must be restored via git or a new owner apply script, not by weakening hooks.

## Validation

| Where | Command | Outcome |
|---|---|---|
| Reconstructed fixture `/tmp/r1-fresh-fixture` | bootstrap ×2 | idempotent hashes IDENTICAL; preflight READY |
| Fixture | validators + 23 tests | pass |
| Fixture identity | non-anonymous vs `cursoragent@noreply.github.com` | exit 1 / exit 0 |
| DesktopFly after apply | validate-agent-config, validate-launch (87 files), preflight READY, 23 tests | pass |
| W4 probe | unlinked runbook | warning, exit 0; probe deleted |
| W2 | `security-engineer-subagent` `bc-c6911470-355b-51e6-a856-43a89b973cee` | safeguard PASS; extra core reads PARTIAL |

## Measured versus estimated

| Claim | Class | Basis |
|---|---|---|
| Disk always-on rule count 15 → 3 (+ 6 Agent-Requested including cost) | OBSERVED | `.cursor/rules/*.mdc` after apply |
| Token or cash saving | UNKNOWN | no Usage telemetry in this run |
| Native always-on injection of the candidate | UNKNOWN / INCONCLUSIVE | session prompt still listed 15 old rules |
| Subagent avoided TOOLS/LAUNCH/STRATEGY/other roles | OBSERVED | W2 file list |
| Subagent avoided all extra core files | FAIL vs charter | read INSTRUCTIONS, SUBAGENTS, STATE |

## Limitations

- No Customize panel. Headless `agent` CLI not used (prior login blocker still applies).
- Shared-source working tree not on disk; do not treat DesktopFly as a byte-identical copy of `/Users/camdouglas/agent-instructions`.
- Home-directory-as-workspace was not implemented (likely expands search/index).
- W5 not performed.
- This session is a Cloud Agent run; that is more expensive than local Ask, which conflicts with the cost objective for future work but was required for this implementation request.
