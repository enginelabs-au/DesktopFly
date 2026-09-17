# 11 · Implementation receipt — R0→R1 first pass

Phase: R0 (identify) and R1 (loading experiment), first implementation pass. Executor: Claude Code 2.1.117 (model claude-fable-5-1) on macOS 25.6.0, 2026-09-17. Nothing in this receipt is an acceptance verdict; Cursor reviews next, then GPT.

## Active paths and versions

| Item | Value |
|---|---|
| Shared source | `/Users/camdouglas/agent-instructions` (Git HEAD `cc2f6cd`; changes applied to the working tree, **not committed**) |
| Consumers touched | none |
| Global client config touched | none |
| Cursor desktop / CLI | 3.20.21 / 2026.07.23 (`agent about`: "User Email: Not logged in") |
| Node | v25.6.1 |
| Claude Code / Codex / Gemini | 2.1.117 / CLI binary broken (ENOENT) / 0.29.5 |
| Pre-change manifest | [baseline-source-manifest.json](baseline-source-manifest.json), hashes matched the tree 25/25 before edits |
| Post-change manifest | [candidate-source-manifest.json](candidate-source-manifest.json) (88 files, excludes `.git`, `.agents`, OS metadata) |
| Sanitized diff | [diffs/agent-instructions-r1.patch](diffs/agent-instructions-r1.patch), 1,012 lines, sha256 `48fe6d24df1bc5103b2724b45ed645711a2db32c6fa67fde6593ab68958aeb0c`; secret-pattern scan: no matches |

## Rollback

Private snapshot (outside the pack, mode 0700): `/Users/camdouglas/.agent-instructions-rollback/20260917T125715Z/` containing `agent-instructions-worktree.tar.gz` (sha256 `dcfb3b109457df98cfd94184f6671398662dfd187f7177bba66df1af58f3d3df`), `sha256-before.txt` (102 files), `HEAD.txt`, `git-status-before.txt`, `uncommitted-vs-HEAD-before.patch`, and the original v1.1 zip. Drill performed: extracting the tarball into a temporary directory reproduced every pre-change hash (102/102). Live restore was **not** executed (it would undo the batch). Procedure:

```bash
cd /Users/camdouglas/agent-instructions
rm -f .cursor/rules/00-core-routing.mdc .cursor/templates/root-agents.md .cursor/templates/cursorignore .cursor/templates/agent-governance-operator-setup.md .cursor/memory/memories/2026-09-17-continuation.md
tar -xzf /Users/camdouglas/.agent-instructions-rollback/20260917T125715Z/agent-instructions-worktree.tar.gz
find . -type f -not -path './.git/*' -not -name '.DS_Store' -print0 | sort -z | xargs -0 shasum -a 256 | diff - /Users/camdouglas/.agent-instructions-rollback/20260917T125715Z/sha256-before.txt && echo restored
```

Per-item reversal without a full restore: each row of change-log ledger B maps to a contiguous hunk set in the patch; `git apply -R` on the relevant files of the sanitized patch reverses one item.

## Validation commands and outcomes

| Where | Command | Outcome |
|---|---|---|
| Template repo | `node .cursor/scripts/validate-agent-config.mjs` | 6 errors, all "template is not a consumer" (root `AGENTS.md`, `.cursorignore`, `docs/…`, CI workflow missing); identical set before and after the batch; **no rule or eager-load errors** |
| Template repo | `node .cursor/skills/launch-pipeline/scripts/validate-launch.mjs` | same consumer-only errors; `.DS_Store` orphan error removed by B8 |
| Template repo | `node --test` policy (11), git-safety (5), preflight (7) | 23 pass, 0 fail |
| Candidate fixture (fresh copy, path with a space, `git init`) | preflight before bootstrap | `BLOCKED`, missing `AGENTS.md`, bootstrap required |
| Candidate fixture | `bash .cursor/scripts/bootstrap.sh` ×2 | run 1 seeded root `AGENTS.md`, `.cursorignore`, `.githooks/`, `docs/`, handover, CI workflow, `settings.json` link; run 2 produced a byte-identical tree (sha256 of every file) |
| Candidate fixture | both validators, preflight, 23 tests | all pass; preflight `READY`, mode hint `undetermined` |
| Candidate fixture | seeded `.githooks/*` vs template repo's own `.githooks/*` | byte-identical |
| Candidate fixture | commit with a private email / with the anonymous identity | blocked by commit-msg hook / accepted |
| Baseline fixture (rollback tar + an existing consumer's root files) | old validators | pass; 15 always-on rules, 6,843 bytes |
| Both fixtures | `agent -p --mode ask --trust --output-format json …` diagnostic | **blocked**: "Authentication required. Please run 'agent login' first"; login is an interactive user action, not performed |
| Rollback drill | tar → temp dir → sha256 compare | 102/102 match |
| Pack | internal link check, JSON parse, code-fence balance | see [pack-manifest.json](pack-manifest.json) |

Raw outputs: [evidence/validators-template-repo.txt](evidence/validators-template-repo.txt), [evidence/validators-candidate-fixture.txt](evidence/validators-candidate-fixture.txt), [evidence/validators-baseline-fixture.txt](evidence/validators-baseline-fixture.txt), [evidence/headless-cli-attempt.txt](evidence/headless-cli-attempt.txt), [evidence/primary-source-verification-2026-09-17.json](evidence/primary-source-verification-2026-09-17.json).

## Measured versus estimated

| Claim | Class | Basis |
|---|---|---|
| Always-on rule bytes 6,843 → 4,027 (−41%) | OBSERVED (authored bytes) | file sizes; injection not traced |
| Mandated per-turn re-reads 45,966 bytes → 0 | OBSERVED (authored policy) | contract text; agent compliance not observed |
| Mandated session-start reads ~101 KB → 0; root `AGENTS.md` +0.5–1.6 KB versus consumer routers | OBSERVED (authored bytes) | file sizes |
| Subagent preload ~110 KB → ~36 KB per role | ESTIMATED | section sizes of `ROLES.md`; no role was run |
| Token or cash saving per accepted change | UNKNOWN | no telemetry; not inferred from bytes |
| Discovery of the five Agent-Requested rules in natural-language tasks | UNKNOWN | requires a live session |
| Unrelated-task non-activation | UNKNOWN | requires a live session |
| Capability inventory preserved | OBSERVED (deterministic) | validators, tests, hooks; skills/agents/hooks files unchanged or byte-identical |

## Limitations and deviations

- Three adversarial review agents could not start (Claude plan monthly spend limit reached mid-run); the review was performed inline by the executor. Primary-source verification (six pages) completed. Treat the inline review as less independent than designed.
- Fresh-session context traces were not captured; `agent` print mode needs a fresh login and the desktop client exposes no export.
- The executor was not subject to the repository's Cursor hooks; several edited files (`AGENTS.md`, `INSTRUCTIONS.md`, `ROLES.md`, `agents/`, `rules/`, `scripts/`) are hook-protected inside Cursor. Cursor's pass must use the owner-authorized apply route for further edits to those files.
- During inspection a plaintext API key argument in two MCP configuration files was echoed into this session's tool output; it is not reproduced in the pack. Rotation is listed in [12](12-REMAINING-WORK.md).
- The patch leaves the working tree uncommitted, consistent with the repository's prior state; no commit or push was made.
