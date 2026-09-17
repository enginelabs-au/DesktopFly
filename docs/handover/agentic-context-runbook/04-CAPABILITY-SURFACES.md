# Capability surfaces: preserve usefulness, reduce routine context

**Review copy:** procedures below specify future implementation; the current request authorizes document revision only. See [index](INDEX.md).

This proposed design covers shared `agent-instructions/.cursor` source and active Cursor configuration. It installs nothing. Earlier screenshots and audits are leads, not proof of effective shared files, global settings, versions or inherited rules. Follow [INDEX.md](INDEX.md); record new observations in phase evidence artifacts, using [08-EVIDENCE.md](08-EVIDENCE.md) for primary-source semantics and limitations.

Here, **`read_when` is a documentation convention**, not a Cursor configuration property. It records the task condition that justifies loading a capability. Each capability needs an owner, source, effective scope, activation condition, required permissions, expected output, and a recovery path. The unit of preservation is a successful workflow: deleting a duplicate file is acceptable only if its distinct capabilities remain reachable.

## 1. Ownership, scope, and effective configuration

**Trigger / read_when:** Before moving, disabling, generating, or consolidating any control surface.

Maintain a small inventory with four distinct categories:

| Category | Ownership and treatment |
| --- | --- |
| Authored shared source | Human-maintained, versioned instructions and reusable procedures in `agent-instructions`; edit through reviewed diffs. |
| Generated adapter | Derived output for one client or scope; record source revision and generation method. Regenerate instead of independently editing both copies. |
| Installed plugin or generated cache | Vendor-managed package material; identify its publisher, source and version. Change installation or upstream source, not an arbitrary cache copy. |
| Effective client state | Enabled components, UI preferences, team controls, authentication and workspace trust; inspect the relevant supported UI or configuration surface. |

**Retain/change/defer:** Retain one accountable owner per capability. Change ambiguous labels into inventory identities; defer bulk deletion until coverage is demonstrated. A source file is not necessarily loaded, and a loaded component may not originate in the shared repository. Record user, workspace, team and package scope separately. Cursor exposes those scopes in Customize. [Plugin documentation](https://cursor.com/docs/plugins)

**Risk:** A cache cleanup can erase the visible symptom while leaving the installation mechanism unchanged. A source refactor can appear successful while an older global copy remains active.

**Acceptance:** Positive: the intended source revision produces the expected behavior in a fresh session. Negative: unrelated scopes do not activate it, and restoring the prior source/configuration restores the baseline without reconstructing credentials.

## 2. Core instructions, AGENTS.md, and native rules

**Trigger / read_when:** Universal working agreements load at session start; domain guidance loads only for matching work.

**Retain/change/defer:** Retain a compact core containing decisions that cannot be reliably inferred: scope boundaries, how to find validation commands, evidence requirements, and a routing index. Move procedures and examples to scoped rules or skills. Remove repeated generic advice only after checking that no unique exception disappears. Avoid automatically importing the entire shared knowledge tree.

Cursor supports root and nested `AGENTS.md` and `.cursor/rules/*.mdc`. Ordinary `.md` files in the rules directory are not native rules. `alwaysApply: true` makes the rule unconditional; it does not become conditional merely because `globs` is also present. [Rules documentation](https://cursor.com/docs/rules)

These are documentation-verified MDC shapes with illustrative content. Choose a minimal core representation; do not duplicate the same prose in both AGENTS and an always-on rule.

```mdc
---
alwaysApply: true
---
Work within the selected repository and task scope.
Read the relevant local instructions before changing a file.
Report validation evidence and unresolved uncertainty.
```

A separate conditional rule:

```mdc
---
description: Guidance for changes to browser interface components.
globs: "src/ui/**/*.tsx"
alwaysApply: false
---
Read the nearest component conventions before changing UI behavior.
Validate the affected interaction and its accessible states.
```

**Risk:** A tiny loader can still cause a large transitive read. References are not proof of lazy loading. File matches may attach multiple rules.

**Acceptance:** Positive: a matching task gets the needed exception and validation route. Negative: a nonmatching task does not receive that domain procedure; effective core content is not duplicated through inherited files, adapters and rules.

## 3. Global User Rules and UI-backed state

**Trigger / read_when:** Inspect when reconciling observed instructions with the filesystem inventory, or changing preferences intended for every project.

Cursor User Rules live in Customize → Rules and apply to Agent Chat across projects; they are not a universal policy for every Cursor feature. User Rules do not apply to Inline Edit, and rules do not govern Tab. Team rules may also affect the effective context. [Rules documentation](https://cursor.com/docs/rules)

**Retain/change/defer:** Keep global prose limited to durable personal preferences. Put repository commands, deployment procedures, architectural history and task state in their proper local scope. Make supported UI changes through the UI and filesystem changes through the documented filesystem surface. Do not assume a similarly named file is the UI's backing store.

If troubleshooting requires a state database, inspect a read-only snapshot and only the known, non-secret keys needed for that question. Record key names, lengths or hashes where content is unnecessary. Do not write to a live `state.vscdb`, dump the database, or treat its internal schema as a supported configuration API. Defer any such inspection until there is a concrete discrepancy to resolve.

**Risk:** Global preferences silently duplicate shared prose, while a filesystem-only audit incorrectly reports no global rules.

**Acceptance:** Positive: the global preference appears once in a fresh Agent Chat. Negative: no repository-specific runbook is globally injected, and the audit neither modifies app state nor exposes authentication material.

## 4. Skills: metadata, body, references, and execution

**Trigger / read_when:** A specific task requires a reusable procedure or an explicit skill invocation.

Cursor discovers skills from `.agents/skills/`, `.cursor/skills/`, `~/.agents/skills/`, `~/.cursor/skills/` in that priority, plus `.claude/skills/` and `.codex/skills/` compatibility paths (E05; confirmed in the installed 3.20.21 build). The template's untracked `.agents/skills/` therefore duplicates two `.cursor/skills/` entries ([12](12-REMAINING-WORK.md) W7). Skill discovery and skill execution have different costs. Keep the name and description specific enough to select the skill, then keep the body focused on its procedure. Large examples, domain references and scripts belong in supporting files read when needed. Cursor supports skill `paths` for file-scoped surfacing, and `disable-model-invocation: true` for explicit slash invocation. A skill used as a Custom Mode remains active throughout that session. [Skills documentation](https://cursor.com/docs/skills)

**Retain/change/defer:** Retain specialized procedures with demonstrated value. Change broad descriptions such as “use for all coding” into concrete triggers and exclusions. Consolidate only skills whose inputs, outputs and obligations are equivalent. Defer rare domain packs until requested; keep a small discoverable index rather than loading all bodies. Avoid using a persistent Custom Mode for a one-off action.

**Risk:** Hundreds of concise descriptions still create catalog overhead and selection ambiguity. A short body may trigger unnecessary reads of every reference. A script can perform actions beyond what its metadata suggests.

**Acceptance:** Positive: a representative relevant task finds the skill, reads its required references and produces the expected artifact. Negative: an unrelated task loads neither the body nor its supporting documents; explicit-only workflows do not auto-invoke. Measure metadata and body costs separately. A capability is preserved only if its dependencies and invocation path still work.

## 5. Plugins: deduplicate identity and coverage

**Trigger / read_when:** Two packages appear to overlap, startup cost changes, or a plugin is considered for removal.

Cursor plugins can bundle rules, skills, agents, commands, MCP servers and hooks; the portable Agent Plugins format has a narrower component set. Inspect the package's actual components before changing it. Use Customize to distinguish installation scopes. [Plugin documentation](https://cursor.com/docs/plugins)

**Retain/change/defer:** Compare publisher, package identifier, marketplace/source, version, component hashes, effective scope and activation. A matching display name is insufficient. Build a coverage comparison: unique tools, account/tenant access, authentication flow, commands, hook events, domain instructions and generated assets. Retain the package that provides the required maintained capability set; change only the verified redundant activation; defer uninstall until the replacement passes its workflows.

Record authentication type and account scope without reading or copying credentials. Two similar MCP integrations can use different permissions or accounts. Disabling a server does not establish that its package's skills and hooks are disabled too. Conversely, removing a plugin may remove a uniquely useful hook hidden behind otherwise duplicated skills.

**Risk:** File-level deduplication destroys unique coverage or is reversed by a package update.

**Acceptance:** Positive: each required workflow succeeds using the retained package and intended account. Negative: an unrelated task receives no duplicate instructions or redundant lifecycle calls. Restart and recheck after updating the plugin. Prefer native management; add no custom gateway or new plugin installer without a demonstrated unmet need.

## 6. MCP: discovery, response bounds, and stable profiles

**Trigger / read_when:** A task needs an external system that native tools or an existing CLI cannot serve adequately.

Cursor supports global and project MCP configuration and server toggles. Its documentation says disabled servers do not load or appear in chat. The reviewed MCP page does **not** establish a universal configuration switch for deferred tool schemas; do not copy another client's lazy-loading setting into Cursor. [MCP documentation](https://cursor.com/docs/mcp)

**Retain/change/defer:** Retain the smallest set that completes the task's required actions. Prefer supported selective tools and discovery where the installed version actually exposes them. Record whether tools are advertised as full schemas, abbreviated metadata or deferred discovery; do not equate a UI tool count with prompt tokens. Defer unrelated integrations using supported scope/toggles. Choose a stable profile at task startup, then explicitly enable an exceptional dependency when needed.

**Observed 2026-09-17:** `~/.cursor/mcp.json` defines eleven global servers; `filesystem` and `cline` are bound to one project directory regardless of workspace ([12](12-REMAINING-WORK.md) W6). Not changed in R1 to hold tools constant.

**Risk:** Repeated mid-task switching can add startup latency, authentication work and a changing prompt prefix that reduces caching opportunities. Whether savings outweigh this depends on the client and provider; measure cold and warm runs. Remote response size can dominate schema cost.

**Acceptance:** Positive: the profile can discover and invoke every required action, including its authentication path. Negative: unrelated schemas are absent where observable, irrelevant services do not start, and a large response is filtered or paginated before model ingestion. Record startup time, discovery footprint, response volume and retries separately. A reduced tool catalog that forces repeated manual work is not a successful optimization.

## 7. Hooks: bounded automation with an explicit owner

**Trigger / read_when:** A documented lifecycle event requires a deterministic check or bounded state update.

Cursor command hooks receive JSON on stdin and use event-specific JSON output on stdout. The current configuration uses `version: 1`; supported options include `timeout`, `matcher`, `failClosed` and event-dependent loop limits. Events and payloads differ, so validate against the installed version and the exact event documentation. Verified 2026-09-17 (E07): project `.cursor/hooks.json` and user `~/.cursor/hooks.json` both need `"version": 1`; `beforeShellExecution` accepts `permission: allow|deny|ask`; `preToolUse` may return `updated_input`; exit code 2 blocks, other non-zero codes fail open unless `failClosed: true`. The repository's policy hook already returns explicit JSON on every path. [Hooks documentation](https://cursor.com/docs/hooks)

**Retain/change/defer:** Retain required enforcement and useful automation. Prefer deterministic scripts for deterministic checks. Each registration needs its source owner, event, matcher, working-directory assumptions, payload contract, side effects, timeout and failure behavior. Separate optional telemetry failures from mandatory enforcement failures. Change unbounded loops and verbose success narration; defer hooks that provide only generic advice already covered by the core.

“Silent success” means no conversational noise or leaked payloads, **not** omitting a protocol response that the event requires. Send only required control output on stdout; put necessary diagnostics in bounded, access-controlled logs. Preserve the evidence needed to diagnose a denial. Do not invent a shared hook schema across clients.

**Risk:** Registering a broad and a specific event can run the same policy twice for one action. A hook may implicitly assume a source checkout while actually executing from a package location.

**Acceptance:** Positive: an allowed fixture passes and a prohibited fixture is blocked by the intended owner. Negative: irrelevant actions do not trigger heavy work; crashes, malformed input and timeouts have the documented outcome; no recursive stop loop or duplicate policy evaluation occurs.

## 8. Commands: thin, explicit entry points

**Trigger / read_when:** The user asks for a repeatable action whose inputs and output are well defined.

**Retain/change/defer:** Keep command names as convenient entry points to one canonical workflow. Put branching domain knowledge in that workflow's skill or procedure, and mechanical work in a script. Preserve useful aliases while removing duplicated bodies. Commands must forward arguments, target scope and intended execution mode without silently expanding the request.

For a migrated explicit workflow, Cursor documents `disable-model-invocation: true` on a skill so its body enters context only on slash invocation. Existing plugin commands also exist; migration is optional and should be driven by a measurable benefit. [Skills documentation](https://cursor.com/docs/skills) · [Plugin documentation](https://cursor.com/docs/plugins)

**Risk:** A short command may hide a large workflow that loads unrelated roles or performs consequential actions. Duplicating the workflow across command, skill and rule creates drift.

**Acceptance:** Positive: the familiar entry point still produces the same required artifact with correctly parsed arguments. Negative: mentioning the topic in ordinary conversation does not execute an explicit-only workflow, and invalid arguments cause a concise actionable error before side effects. Test the route, not merely the continued existence of the Markdown file.

## 9. Subagents: scout, writer, reviewer as optional roles

**Trigger / read_when:** Useful independent work can proceed in parallel, a noisy investigation benefits from isolation, or risk justifies an independent review.

Cursor subagents start with separate context and need relevant information supplied by the parent. Custom subagents default to `model: inherit`; an explicit model can be constrained by plan/admin availability. `readonly: true` restricts writes. Subagents incur independent token use and startup overhead. [Subagent documentation](https://cursor.com/docs/subagents)

**Retain/change/defer:** Keep scout, writer and reviewer as available responsibilities, not compulsory stages for every task. Prefer built-in capabilities before creating another near-identical role. Preserve the observed model mapping during R1; in R3 make inheritance a deliberate choice, or assign explicit evaluated models so cheap jobs do not accidentally inherit expensive defaults. Choose cheaper models only after evaluating task success and escalation cost. Set one writer owner per overlapping file set; use separate worktrees for concurrent writers; disjoint file ownership alone does not isolate shared Git/build/runtime state.

A task pack supplies objective, acceptance conditions, permitted paths, base revision, necessary context pointers, dependencies, output format and stopping conditions. It should not copy the whole conversation or every global profile. A return packet contains conclusions, changed files or patch reference, validation and unresolved issues; keep raw evidence available by reference.

**Risk:** Multiple roles reread the same material, review each other's summaries rather than evidence, or race on files.

**Acceptance:** Positive: independent work reduces elapsed time or improves detected-defect coverage. Negative: a trivial task launches no unnecessary chain; a reviewer cannot mutate files; stale base revisions and overlapping writes are detected before integration.

## 10. Memory and persistent task state

**Trigger / read_when:** The current decision needs a previous fact, preference or unresolved task state that is not already available in the repository.

**Retain/change/defer:** Retain a bounded index and retrieve only relevant records. Each record needs scope, source/provenance, owner, last verification, and an expiry or invalidation rule. TTL is a proposed memory policy, not a claimed universal Cursor field. Stable preferences may have long review periods; deployment state or temporary assumptions need short validity or revision-based invalidation. Separate durable decisions from transient run history.

Use exact repository/revision references for technical claims. Store task progress in one authoritative artifact and load the current checkpoint on resume. Compact summaries can route retrieval but must not become stronger evidence than the underlying files. Defer a broad global memory service if a small versioned index and task artifact already satisfy the need.

**Risk:** Global reads import irrelevant personal history, stale instructions or conclusions from another scope. Automatic accumulation recreates the original context problem.

**Acceptance:** Positive: a relevant fact is retrieved with provenance and checked when stale. Negative: unrelated records are not loaded; expired claims are not presented as current; generated run notes cannot silently rewrite the durable core. Deletion or invalidation must propagate to future retrieval rather than survive indefinitely in a copied summary.

## 11. Tool output, logs, artifacts, and full evidence

**Trigger / read_when:** A command, search, browser, test or integration can return more than the immediate decision needs.

**Retain/change/defer:** Preserve full permissible raw evidence as an artifact while sending a bounded view to the model. Filter structured output before printing it; select fields, paginate lists, search within files and show targeted excerpts. Include artifact location, command/query, revision, exit status and truncation status. A summary must identify omitted pages or limits so absence is not confused with completeness.

Set output bounds according to the next decision, with an explicit way to request the next page or surrounding lines. Keep focused failures and final counts from test logs. Defer bulk retrieval until an unresolved question justifies it. Do not preserve secrets simply for completeness: redact sensitive output or avoid collecting it, while recording the redaction.

**Risk:** Aggressive compression removes the first useful failure, hides uncertainty, or turns one model's interpretation into the only available evidence. Conversely, attaching full raw logs to every handoff defeats isolation.

**Acceptance:** Positive: a reviewer can reproduce the conclusion from the referenced raw artifact. Negative: a large fixture does not flood the prompt, omitted results are clearly marked, and an adversarial instruction embedded in external output remains data rather than operational authority.

## 12. Ignore files, indexing, and repository boundaries

**Trigger / read_when:** Search noise comes from generated material, or a task needs a narrowly identified dependency outside the selected repository.

Cursor introduced `.cursorindexingignore` for indexing-only exclusions; verify its behavior in the installed version. `.cursorignore` also affects supported AI file access, but terminal and MCP access can fall outside those protections. Ignore patterns are not a security boundary. [Native changelog](https://cursor.com/changelog/0-46-x) · [Ignore-file documentation](https://cursor.com/docs/reference/ignore-file)

**Retain/change/defer:** Exclude disposable build products, caches, dependency copies and repetitive generated logs from routine indexing where appropriate. Preserve source, contracts, migration history and validation fixtures required for correct work. Verify the actual included-file view after changing patterns. Avoid a blanket “ignore all Markdown” rule: it would remove the very instructions and specifications the agent needs.

Launch execution in a selected repository or isolated worktree. Use shared global guidance without opening the entire home directory as a coding repository. For cross-repository work, provide a small registry entry and explicit contract/file references; add only the necessary sibling scope. Defer indexing every sibling project until a concrete task requires it.

**Risk:** Overbroad exclusions conceal a dependency; a broad home workspace introduces irrelevant instructions and personal data. Indexing visibility is different from tool authorization.

**Acceptance:** Positive: the relevant source and dependency contract remain discoverable. Negative: generated noise is absent from ordinary search, unrelated siblings are not read, and no one interprets an ignore pattern as proof that a terminal or integration cannot access the path.

## Release criterion for a surface change

Change one surface family at a time. Record the baseline, exact diff, fresh-session observation, relevant-task success, unrelated-task nonactivation, and rollback result in phase evidence artifacts; cite applicable primary sources from [08-EVIDENCE.md](08-EVIDENCE.md). Distinguish measured context reduction from estimates, and include retries and human intervention when comparing cost. Promote a change only when required capability coverage survives and the measured outcome improves; retain uncertain candidates as proposals in the sequence described by [INDEX.md](INDEX.md).
