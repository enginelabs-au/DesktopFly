# 03 · First intervention: loading policy

**Status (2026-09-17):** the minimal patch below was applied to the shared source in a first implementation pass and validated on a disposable fixture; native loading behaviour in a live Cursor session was **not** observed. Details, evidence and limits: [11 receipt](11-IMPLEMENTATION-RECEIPT.md); open items: [12 remaining work](12-REMAINING-WORK.md). See [index](INDEX.md).

Read when: R1, or when reviewing the applied batch. Objective: smaller irrelevant/repeated input with the same tested capability. Mechanism details: [04](04-CAPABILITY-SURFACES.md); acceptance: [06](06-EVALUATION-AND-RECOVERY.md). R1 does not authorize the full architecture in later chapters.

**Why loading first (confirmed by inspection).** The pre-change contract mandated ~101 KB of session-start reads and ~46 KB of per-turn re-reads through the read tool, on top of ~7 KB of natively injected rules, and ~110 KB of preload per subagent start. Each tool read lands as a new tool result, so an N-turn session carried up to N copies of the seven core files. No tool-output or history source of comparable size was found in the authored surface; tool output volume remains unmeasured because no telemetry was accessible. H1 is therefore supported by direct inspection of the instructions, not by a runtime trace.

**Causal isolation.** Model, reasoning, subscriptions, MCP servers, hooks, permissions, sandbox and skill set were held constant. Only activation and reread text plus the validators, bootstrap seeding and documentation coupled to it changed. Substantive guidance was preserved: merged rule bodies were carried into the core rule; converted rule bodies are unchanged.

**Applied patch (summary; full diff in [diffs/agent-instructions-r1.patch](diffs/agent-instructions-r1.patch)).**

1. `.cursor/AGENTS.md` §2–3: session start = read once, run read-only preflight, inspect `STATE.md`; later turns = reuse instructions in context, re-read only after change, context loss/compaction, newly relevant scope, or when exact wording matters. The "read every file under `instructions/` and `rules/`" step was removed.
2. Rules: eight routing/state rules merged into `00-core-routing.mdc` (always-on); `git-privacy-and-secrets.mdc` and `karpathy-guidelines.mdc` unchanged and always-on; `project-planning`, `subagent-orchestration`, `blocker-governance`, `memory-governance`, `runbook-governance` converted to Agent-Requested (`alwaysApply: false` + description).
3. A seeded repository-root `AGENTS.md` template (compact core constraints, loading policy, routing index) replaces the consumer-specific routers; bootstrap also seeds `.cursorignore`, `.githooks/`, the operator-setup handover and the governance CI workflow when absent, so a fresh copy passes its own validators.
4. Subagent preload: adapters and `ROLES.md` §3.2 read the charter, manifest, predecessor handoff, `ROLES.md` §1–3 and the role's own section; other core files on demand.
5. Validator: rule modes accepted; core and git-safety rules must stay always-on; retired rule files rejected; an eager-load guard fails on reintroduced per-turn read-all phrasing in rules, `AGENTS.md`, `INSTRUCTIONS.md`, `BOOTSTRAP.md`, `MEMORY.md`, `ROLES.md`.
6. Coupled documentation (`README.md`, `.cursor/README.md`, `BOOTSTRAP.md`, `MEMORY.md`, runbook, launch skill/instruction, planning prompts) updated in the same batch; template `STATE.md` reset to a skeleton.

**Reread policy (as now written into the contract).** Reuse applicable instructions still present in context. Refresh on changed file, newly relevant scope, resumed/new session or compaction, or a specific need to verify exact wording. After compaction, restore from `STATE.md` and the files it lists. Never assume dropped material is remembered; never re-read the whole corpus to avoid that uncertainty. Live permission/authorization checks stay current.

**Fifteen shared rules: final dispositions.**

| Rule | v1.1 proposal | Applied |
|---|---|---|
| `00-read-agent-context-first` | replace with compact entry/router | merged into `00-core-routing.mdc`; file removed |
| `core-operating-context` | merge into one core | merged; removed |
| `instruction-routing` | one routing owner | merged; removed |
| `root-canonical` | consolidate ownership | merged; removed |
| `git-privacy-and-secrets` | preserve | unchanged, always-on, validator-required |
| `karpathy-guidelines` | retain useful constraints | unchanged, always-on |
| `skills-file` | native discovery + targeted references | merged (on-demand pointer); removed |
| `tools-file` | no per-turn tool manual | merged (on-demand pointer + tool-preference clause); removed |
| `project-planning` | activate for consequential planning | Agent-Requested; body unchanged |
| `subagent-orchestration` | activate for real delegation | Agent-Requested; body unchanged |
| `blocker-governance` | load for a persistent blocker | Agent-Requested; body unchanged |
| `memory-governance` | load for memory operations | Agent-Requested; body unchanged |
| `working-memory` | merge overlapping state instructions | merged; removed |
| `state-and-compactification` | checkpoint at boundaries | merged; removed |
| `runbook-governance` | load when using a procedure | Agent-Requested; body unchanged |

Every substantive constraint from the removed rules has a new owner in `00-core-routing.mdc`, `.cursor/AGENTS.md` §3/§9, or the file it governs. The five Agent-Requested rules duplicate obligations that also live in `.cursor/AGENTS.md` §5, §7, §9 and `INSTRUCTIONS.md`, so a discovery miss on a description-triggered rule does not remove the obligation; it removes a reminder. That fallback is deliberate and must be kept when editing those sections.

**Large role/tool bodies.** `ROLES.md` (57 KB) stays one file; roles are routed to §1–3 plus their own section. `TOOLS.md` (15.7 KB) is now on demand. Extracting §3 of `ROLES.md` into a separate shared-contract file would cut the per-role read further but was deferred as a separate, measurable batch ([12](12-REMAINING-WORK.md)).

**Dependent migration.** Validator assertions, bootstrap seeding, reachability classification (`validate-launch.mjs` now ignores OS metadata files), documentation and the template skeleton were updated together. No hook, permission, sandbox, or CI check was weakened.

**Canary.** A disposable fixture in a path containing a space was created from a fresh copy of the revised tree: preflight reported `BLOCKED` (missing root `AGENTS.md`) before bootstrap and `READY` after; bootstrap seeded the root files; validators and 23 unit tests passed; a second bootstrap produced a byte-identical tree; the seeded git hooks rejected a private-email commit and accepted the anonymous identity. A baseline fixture built from the rollback snapshot plus an existing consumer's root files passed the old validators, establishing a matched pair for the native A/B. No consumer repository was modified.

**Paired cases (status).** Deterministic cases (installer, validators, hooks, rollback) passed. The natural-language positive/negative trigger cases, the MCP-dependent case, the bounded subagent case and the checkpoint/resume case require a live Cursor session and are assigned to Cursor with acceptance criteria in [12](12-REMAINING-WORK.md). The headless CLI route was attempted and blocked on interactive login.

**Gate R1 (current standing).** Authored irrelevant loading is demonstrably lower on the inspected surface and deterministic checks show no regression. Effective loading, discovery of the Agent-Requested rules, and subagent behaviour are `UNKNOWN` until Cursor's native validation. Do not promote to consumers before those cases pass. If tool output or history turns out to dominate in live traces, keep this batch and redirect the next phase to that source.
