# This-pass artefact snapshot (DesktopFly canary)

Pack version 1.4 snapshots every in-repo file from Cursor’s second pass into this folder so GPT review can use **one directory**. Live canary files stay at their original repository paths. Do not apply this snapshot; use `docs/handover/apply-context-optimization-r2.sh` for protected files.

| Path | Contents |
|---|---|
| `repo/` | Copies of every added or modified PR file that lived **outside** `docs/handover/agentic-context-runbook/`, plus the two unchanged always-on rules (`git-privacy-and-secrets.mdc`, `karpathy-guidelines.mdc`) so `.cursor/rules/` in the snapshot is the complete post-R2 set |
| `retired-rules/` | Pre-R1 always-on rule files deleted from `.cursor/rules/` (blobs from `origin/main`) |
| `DELETED-PATHS.txt` | Paths removed in this PR |
| `FILE-MAP.tsv` | `original_path<TAB>snapshot_path` |
| `desktopfly-outside-pack.patch` | `git diff origin/main...HEAD` excluding this pack directory |
| `INVENTORY.json` | Machine-readable list of copied, deleted, and still-out-of-repo items |

Chapters, evidence, manifests, `GPT-REVIEW-PROMPT.md`, and `diffs/agent-instructions-r1.patch` at the pack root are already part of this folder.

**Not available on this VM (cannot be snapshotted):**

- Claude’s private Mac rollback tarball
- Shared source `/Users/camdouglas/agent-instructions`
- Owner `~/.cursor` MCP keys and other global client config
- Fresh-session Customize-panel W1 traces
- Measured token or cash bills
