# GPT review prompt (pack v1.4)

Copy everything below the line into ChatGPT. Attach or upload the folder `docs/handover/agentic-context-runbook/` (this pack). Do not paste secrets, MCP keys, or `.env` files. This prompt is not authorization to change configuration, spend money, or claim acceptance.

---

You are GPT. You authored the original context-optimization proposal (pack v1.1). Claude reviewed it and applied a bounded R0→R1 pass (v1.2). Cursor independently reviewed Claude, attempted native W1/W2 validation, applied R2 corrections, and canaried **DesktopFly** (v1.3), then snapshotted every in-repo artefact from that pass into this pack (v1.4). You now review **both** implementation passes against the objective and the evidence. Produce a design/evidence verdict. Do **not** claim final acceptance. Do **not** implement.

## Objective

Reduce irrelevant and repeated model context and total cost per accepted change while preserving capability availability, reliable discovery, correct execution, and necessary safeguards. Prefer selective activation over deletion. Optimize outcomes, not file length or tool counts. Stated subscriptions: Cursor US$200/month, ChatGPT Plus US$20, Claude Pro US$28, Gemini free. No new paid API spend. Distinguish plan allowances from API billing. Token and cash savings in this pack are **UNKNOWN**; do not invent percentages.

## What you have been given

One folder: `agentic-context-runbook` (pack **v1.4**). It is self-contained for this review.

**Pack root (read these):**

- `INDEX.md` — status, reading order, round table (entrypoint)
- `this-pass/README.md` — what the snapshot contains and what is still missing
- `GPT-REVIEW-PROMPT.md` — this prompt
- `10-CHANGE-LOG.md` — proposal vs applied ledgers A–E
- `11-IMPLEMENTATION-RECEIPT.md` — Claude R1
- `13-CURSOR-RECEIPT.md` — Cursor R2 / DesktopFly canary
- `12-REMAINING-WORK.md` — W1–W14 statuses
- `07-REVIEW-AND-CONTRACTS.md` — your review contract (priorities, evidence labels, required outputs)
- `evidence/cursor-phase1-review-2026-09-17.md`
- `evidence/cursor-phase2-observations-2026-09-17.md`
- `diffs/agent-instructions-r1.patch` (sha256 `48fe6d24df1bc5103b2724b45ed645711a2db32c6fa67fde6593ab68958aeb0c`)
- `pack-manifest.json`

**Also in this same folder (`this-pass/`):** copies of every other in-repo artefact Cursor worked on. Live canary files were **not** moved; these are snapshots.

- `this-pass/repo/` — DesktopFly canary files (root `AGENTS.md`, `.cursor/` contract/rules/validators/bootstrap/adapters/state, apply script, payloads, workstream, plans, decision, operator note)
- `this-pass/retired-rules/` — the eight always-on rules removed from `.cursor/rules/`
- `this-pass/FILE-MAP.tsv`, `this-pass/INVENTORY.json`, `this-pass/DELETED-PATHS.txt`
- `this-pass/desktopfly-outside-pack.patch`

`.cursor/README.md` inside `this-pass/repo/` is the control-plane readme, not the pack index. The pack index is `INDEX.md`. The snapshot guide is `this-pass/README.md`.

Chapters `01`–`09`, manifests, and older evidence remain at pack root. Read `04`–`06` and `08`–`09` only for sections a finding touches.

## What is not in this folder

Do not pretend you have inspected these:

- Claude’s private Mac rollback tarball
- Shared source working tree `/Users/camdouglas/agent-instructions`
- Owner `~/.cursor` MCP keys and other global client config
- A fresh-session Customize-panel W1 trace
- Measured token or cash bills

## Facts you must not upgrade

Treat these as already labelled. Challenge them only with pack-internal counter-evidence.

- W1 native always-on **injection** is **INCONCLUSIVE** (Cloud Agent had no Customize panel; the session prompt still listed the old 15 always-on rules). Disk after apply: 3 always-on + 6 Agent-Requested.
- W2: one `security-engineer-subagent` (`bc-c6911470-355b-51e6-a856-43a89b973cee`) safeguard **PASS**; it avoided TOOLS/LAUNCH/STRATEGY and other role sections; it still read INSTRUCTIONS, SUBAGENTS, and STATE (**PARTIAL** vs charter).
- W3 DesktopFly canary **implemented** via owner apply route `this-pass/repo/docs/handover/apply-context-optimization-r2.sh`. Hooks were not weakened.
- W4 unlinked project-local runbooks: warning, not failure.
- W5 key rotation: owner-only; **not** performed.
- Hooks, permissions, sandbox, `policy.mjs`: **unchanged**.
- Home-directory-as-workspace: **not** adopted.
- R3–R4 registries/adapters/runners: **deferred**.
- Shared source was **not** on the Cursor VM; 81/88 candidate hashes matched a reconstruction onto DesktopFly. Do not treat DesktopFly as a byte-identical copy of `agent-instructions`.

Branch: `cursor/context-optimization-r2-0433`. Consumer: `enginelabs-au/DesktopFly` PR 3.

## Reading order

1. `INDEX.md`
2. `this-pass/README.md`
3. `10-CHANGE-LOG.md`
4. `11-IMPLEMENTATION-RECEIPT.md`
5. `13-CURSOR-RECEIPT.md`
6. `12-REMAINING-WORK.md`
7. `evidence/cursor-phase1-review-2026-09-17.md`
8. `evidence/cursor-phase2-observations-2026-09-17.md`
9. `07-REVIEW-AND-CONTRACTS.md`
10. Then only the changed sections and `this-pass/repo/` files a finding needs. Use `this-pass/FILE-MAP.tsv` to locate snapshots.

## Your job

Follow `07-REVIEW-AND-CONTRACTS.md`. Review Claude’s design revisions **and** Cursor’s corrections/canary. Preserve sound decisions. Do not restart the research cycle. Do not propose registries, runners, new subscriptions, or credential operations.

Return:

1. **Verdict:** ready for a bounded pilot / revise before pilot / insufficient evidence for a specified decision. This is a design verdict, not implementation certification.
2. **Material findings:** location; issue; evidence or assumption; consequence; smallest correction; proposed validation. Separate defects from preferences.
3. **Change log** tagged retain / correct / simplify / add / defer.
4. **Updated remaining-work view** of W1–W14: keep Cursor’s statuses unless the pack contradicts them; say what the owner should do next (fresh chat W1, W5 if needed, optional copy to other consumers).
5. **Evidence ledger delta:** stale or overstated claims, missing primary sources, verification still required.

Use labels `OBSERVED`, `DOCUMENTED`, `INFERRED`, `PROPOSED`, `HISTORICAL`, `UNKNOWN` as defined in `01-CONTRACT.md`. Do not manufacture savings. Do not infer that a file on disk was injected by the client. Do not treat `this-pass/` snapshots as live apply authority.

## Hard limits

No purchases, account changes, deployments, secret handling, hook weakening, or further implementation. If information is missing, continue the review with explicit assumptions rather than requesting the whole filesystem or credentials.
