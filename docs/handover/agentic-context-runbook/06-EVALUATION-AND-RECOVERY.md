# 06 — Evaluation and recovery

**Review copy:** procedures below specify future implementation; the current request authorizes document revision only. See [index](INDEX.md).

[Runbook index](INDEX.md) · [Evidence and limitations](08-EVIDENCE.md)

This chapter is a one-time migration and evaluation procedure for the shared `agent-instructions/.cursor` configuration and the active Cursor setup. It is not another global rule file. Reading it does not authorize configuration changes, external actions, purchases, credential access, or changes to existing safeguards. Execution must stay within the user's actual approved scope.

## What success means

Reduce unnecessary instruction loading and repeated work while preserving the behaviors required for the evaluated tasks. Three distinct properties need evidence:

| Property | Question | Suitable evidence |
|---|---|---|
| Capability inventory | Does the procedure, tool, hook, or agent still exist in the intended profile? | Sanitized manifest, resolved path, version/hash, enabled state where observable. |
| Discoverability | Can Cursor select or reveal it when an appropriate request arrives? | A fresh-session trigger test showing the intended instruction/tool became available. |
| Correct use | Does the agent apply it correctly and respect its limits? | Task outcome, required checks, hook result, and absence of prohibited changes. |

An inventory proves neither discoverability nor correct use. A successful task does not prove that every installed capability survived. A disabled server may still leave plugin skills or hooks registered. Conversely, a capability omitted from startup can remain usable through explicit invocation. Record these separately instead of scoring everything as simply “installed” or “removed.”

For each retained capability, record its owner, scope, trigger, negative trigger, required inputs, expected behavior, dependencies, and validation method. Mark untested items `UNKNOWN`; do not silently count them as passing. Preserve safety-relevant requirements explicitly even when they are rare.

## Establish a comparable baseline

Freeze the current configuration and candidate configuration as separate versioned snapshots. Record Cursor version, selected model and reasoning setting, mode, enabled tool/profile list, rule and skill hashes, working directory, relevant permission state, and any background automation that can affect the run. Never export raw settings containing credentials; a sanitized inventory is sufficient.

Use the same task text and initial repository snapshot for each pair. Run both sides in fresh sessions, with no inherited chat. Keep model, reasoning, available tools, permissions, acceptance checks, and source revision matched for the first instruction-loading experiment. Alternate which configuration runs first when practical. Repeat inconclusive pairs rather than treating one lucky completion as an improvement.

Do not mix several experiments into one causal claim. First compare instruction loading with equivalent tools. Then evaluate plugin/server deduplication separately, checking that the retained connection exposes the needed behavior. Compare model routing only after the configuration is stable. If a setting cannot be held constant, record the difference as a confounder.

Fresh chat is necessary but not sufficient isolation. Persistent memories, project indexing, restored sessions, custom modes, plugin caches, tool discovery history, cached prefixes, background jobs, and environment changes can survive it. Disable or isolate these only within authorized test scope; otherwise record them. Separate cold-start measurements from a warm-cache series. Do not clear an account's shared history or global caches merely to make the comparison tidy.

Before testing, declare acceptance criteria and tolerances. A reasonable pilot proposal is: no lost critical safeguards, all required smoke cases pass, no new high-severity defects, and no material increase in interventions or failed attempts. Set the acceptable latency and quota regression in advance, based on the user's workload. A smaller context is not an automatic pass if quality drops. These are proposed evaluation criteria, not vendor guarantees or universal optimal thresholds.

**Status 2026-09-17:** the deterministic parts of this procedure (installer dry run/apply/idempotence, validators, hook fixtures, rollback drill) were executed for the R1 batch and passed; see [11](11-IMPLEMENTATION-RECEIPT.md). The five smoke cases below that need a live session are outstanding and assigned in [12](12-REMAINING-WORK.md) W1–W2.

## First gate: five small smoke cases

Use disposable fixtures and non-production targets. Each case should have an observable expected result and a bounded time/attempt limit.

1. **Routine bounded change.** A small edit with one clear acceptance check. Confirm that the agent finds the relevant source and validates the change without loading unrelated planning, deployment, or specialist bodies.
2. **Positive capability trigger.** For automatically selected capabilities, request the specialist outcome in natural language without naming its skill; use matched wording in both conditions. Separately test the documented explicit invocation for manual workflows. Confirm discovery, the correct body/version, required inputs, and a harmless validation or dry run. Availability alone is insufficient; a reminder supplied only to the candidate masks a discovery regression.
3. **Negative trigger.** Give a superficially similar request outside that procedure's domain. Confirm it does not activate or inject unrelated context. Test explicit-only behavior where the configuration promises it.
4. **Scope and safeguard boundary.** Use synthetic paths and harmless hook fixtures to test one allowed action and one denied action. Confirm the denial remains actionable and does not initiate workaround attempts. Never test with real secrets or production mutations.
5. **Checkpoint and resume.** Stop at a coherent boundary, save the task record, and resume in a fresh session. Confirm acceptance criteria, source revision, decisions, remaining work, and ownership survive without rereading all history.

Any critical failure stops promotion. Fix the smallest cause and rerun the affected case plus any dependent case. Do not repeatedly run the whole suite after unrelated editorial changes. A dry run demonstrates routing or preparation only; it does not prove authentication, real tool execution, deployment, or production safety.

## Second gate: representative tasks

After the five smoke cases pass, use approximately **12–20 representative tasks** spanning actual intended work: small edits, investigation, multi-file implementation, ambiguous requirements, documentation, tool-assisted work, failure recovery, and a consequential change requiring review. Include positive and negative triggers for newly scoped capabilities. This is a practical pilot size, not a statistically powered benchmark.

Evaluate both the successful path and a realistic failure path. Record whether the agent recognizes missing inputs, stale evidence, unavailable tools, and incorrect assumptions. Use holdout tasks that did not drive the rewrite. Broader capability coverage is optional until those capabilities are needed; document the resulting limits instead of claiming exhaustive preservation.

Do not present p95 latency, precise success-rate improvements, or provider rankings from five smoke cases. For the broader pilot, show raw paired results, medians/ranges, failure counts, and unresolved confounders. Expand the sample only when uncertainty could change the decision.

## Onboarding, hooks, and rollback

Test the configuration installer or synchronization procedure in a disposable directory first. Verify that a dry run lists intended paths and meaningful diffs. An initial apply should create only the approved files; a second apply should make no unintended changes. Preserve nonempty user-authored files, report conflicts, and validate canonical-source hashes. Test paths containing spaces and execution from an unexpected working directory. Derive the target explicitly rather than assuming the current directory is correct.

Run existing deterministic validators and policy tests, revising tests that merely enforce the old loading architecture. Keep tests for actual invariants. Test hook input parsing, allowed and denied fixtures, missing/malformed input, timeout behavior, and current Cursor event/output contracts. A unit test of the policy function does not prove the host registered the hook: observe at least one harmless runtime event and its expected result. Record duplicate invocations and startup latency. Share policy logic where sensible, but do not assume another client's hook schema matches Cursor's.

Before applying the candidate, retain a manifest of managed files and their hashes, a patch or backup sufficient to restore them, and the exact old profile selection. Keep the rollback narrow: restore only managed configuration, preserve unrelated working changes, and restart a fresh session. Do not use broad repository resets or delete plugin caches. After rollback, verify the expected profile, hook registration, and the previously failing smoke case. Recovery is complete only when that behavior is demonstrated.

## Measurement without invented savings

Maintain separate cash and capacity ledgers. The user's stated subscriptions total **US$248/month**; this procedure makes no purchase or plan change. Existing-plan usage can have zero incremental cash cost while consuming quota. API list prices do not establish the charge for a subscription request.

For every task, record acceptance, attempts, elapsed and active time if available, interventions, checks, defects, tool failures, and context-reset count. Capture actual input/output, cache, reasoning, and billed-cost fields only when the host exposes them, retaining field definitions and units. Include unsuccessful attempts and review passes in cost per accepted task. Keep fixed subscription allocation separate from incremental charges so adding both does not double count.

Define accepted-work cost as total attributable attempt/review expenditure divided by accepted tasks in the declared cohort. If none are accepted, report an undefined ratio and the failed cohort, not zero cost. Report elapsed critical-path latency separately from summed worker-active time. Add measured human time as its own ledger; monetize only with an explicit user-supplied rate. If sampling is small, describe observed non-regression rather than asserting statistical equivalence or universal preservation.

Provider accounting differs. Cached input may be included in total input or reported separately; reasoning may already be included in output. Cache-write costs may be separate. Normalize according to documented semantics before summing. Never add all visible fields blindly. Quota percentages can be coarse and account-shared: concurrent usage, resets, and window changes can prevent attribution to a single task. Report quota deltas as proxies with those limitations.

If token telemetry is unavailable, measure authored instruction characters, loaded file names when observable, catalog/tool counts, tool-result volume, number of reads, latency, retries, and outcomes. A characters-divided-by-four estimate is a corpus heuristic, not billed tokens. Missing usage is `UNKNOWN`, not zero. Smaller files, fewer calls, or faster work support narrow operational conclusions; they do not prove a percentage cash saving.

## Canary decision and missing telemetry

Promote first to one active Cursor profile for a short, predeclared canary period or task count. Keep the old version restorable. Continue only if required behaviors pass, no important scope/safeguard regression appears, and the declared quality and operational tolerances hold. Pause on unexplained loading, lost discovery, hook failures, repeated retries, or stale handoffs. Roll back when a consequential failure cannot be quickly isolated.

With missing usage telemetry, a quality-passing candidate may be adopted provisionally for demonstrably simpler loading and maintenance, while **cost reduction remains unverified**. If a spending/quota guarantee is a release condition, missing telemetry prevents that conclusion; use observable host limits and a fixed attempt/time budget, then obtain the missing evidence. Do not add a paid gateway just to finish this pilot.

Conclude with a compact verdict: `PASS`, `FAIL`, or `INCONCLUSIVE`; exact evaluated revision; tests passed/failed; measured changes; untested capabilities; confounders; and rollback location. Preserve raw sanitized evidence for audit, while future task context receives only the relevant result and references.
