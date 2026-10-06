# 2026-10-06 continuation

## Branch consolidation and hook fix

- CODEOWNERS (`* @cam-douglas`) landed via PR #5. Ruleset deleted by the owner; PR #3 merged by the owner.
- PR #2 conflicts resolved by bringing `main` into its branch: `.cursor/STATE.md` merged by hand; DesktopFly plan and checklist stay at `docs/plans/`, control-plane versions moved to `docs/plans/context-optimization/`.
- Hook false positive: `isGitCommitCreating` matched `merge` inside `merge-base`, `merge-tree` and paths or branch names containing `-merge-`. Fixed token-aware in PR #6; real merges, commits, pulls and rebases are still detected, including in compound commands.
- PR #6 and PR #2 merged. PR #2 was a draft and was marked ready first.

## Validation on `main` (45dda91)

- Preflight READY; `validate-launch` PASS (89 files); `check-foundations` PASS.
- node tests: 45 pass, 0 fail. Backend `uv run --frozen pytest`: 52 passed, 2 skipped.
- Policy probe on merged `main`: `merge-base`, `merge-tree`, and `worktree add /tmp/x-merge-0433` allowed; plain `merge`, compound `merge-base && merge`, and `merge` with a private email denied; `merge` with the anonymous identity allowed.
- `validate-agent-config.mjs` is not runnable by the agent shell (protected path); CI ran it green on both PRs.

## Pre-push defect found and fixed (same PR as this log)

- With hooks installed, any new-branch push failed: `pre-push` scanned the full ancestry, which includes GitHub web-merge commits (committer `noreply@github.com`) and one historic `cursoragent@cursor.com` commit. Merging `main` into an existing branch hit the same problem.
- Fix: the push check now inspects only commits not on any remote ref (`<sha> --not --remotes`), and `noreply@github.com` (GitHub's web committer) is an allowed address. Private inboxes in new commits are still rejected. Regression test builds a temp repo (published private-email commit passes; new private-email commit fails).
- Node tests: 47 pass, 0 fail.

## Stale remote branches (completed)

- Deleted after verification: `cursor/rename-lauch-to-launch-8c4d`, `cursor/context-optimization-r2-0433`, `cursor/codeowners-latest-0433`, `fix/git-safety-merge-detection`, and `cursor/phase-0-foundations-a5d1`.
- Deleted as superseded: `cursor/codeowners-0433` (closed PR #4, old typo `@cam-dogulas`).
- Deleted after merge: `cursor/closeout-state-0433` (PR #7).

## Notes

- Local `main` is fast-forwarded to `9becc5b`; the shared `agent-instructions/.cursor` was synced from the fixed tree.

## Dataset integration

- MaleCNS v1.0 downloaded from the pinned Janelia GCS URLs. Full derived tables built locally: 211,577 neurons and 26,028,386 edges. Updated `provenance/malecns-v1.0.json`.
- FlyWire v783 proofread connectivity downloaded from Zenodo record `10676866` and verified against its published MD5. v3.2.0 annotations downloaded from the pinned FlyConnectome Git tag.
- FlyWire materialized tables: 15,091,983 aggregated neuron-pair rows and 139,248 annotations. Provenance: `provenance/flywire-v783.json`.
- `FlyWireAdapter` now loads the canonical derived parquet tables while preserving the `flywire:` namespace and keeping FlyWire out of the default MaleCNS runtime.
- Full backend suite: 55 passed. The full MaleCNS presentation test initially exposed zero motion with the downloaded graph; the derived map builder now selects connected pools and adds an explicit engineered sensory presentation bridge. Regression test passes.
- Changes were on `cursor/dataset-integration-0433`; PR #9 merged to `main` at `9becc5b`, and the remote branch was deleted. Raw and derived data remain gitignored and are reproducible through the downloader scripts.

## Guarded simulation readiness

- Full MaleCNS MPS timing measured approximately 60–175 ms per 5 ms block, missing the configured 4 ms budget.
- Added a deterministic reviewed-subset builder. The default runtime now uses 256 reviewed MaleCNS neurons and 2,021 edges; CPU NumPy is selected for this bounded graph, with CPU fallback disabled for the MPS full-graph profile.
- Added worker deadline enforcement, committed tick reporting, permanent fault handling, and Electron in-flight/heartbeat protection. A missed deadline or neural error stops the worker and cannot auto-resume.
- Timing report: `reports/connectome-timing.json`; 40 blocks passed with max 0.000333 s against the 0.004 s budget.
- Validation: backend 56 passed; Node 22 passed; foundations and launch validation passed; policy tests 19 passed; Electron 5-second smoke launch exited 0.
- Added `scripts/run-full-sim.sh` / `scripts/run_full_connectome.py` for bounded full-connectome diagnostics without changing the safe desktop policy. Verified full MaleCNS: 211,577 neurons, 25,074,842 synapses, 86.77 s load, 178.97 ms first block, and a 4 ms budget miss.
- Added policy-derived LIF timing and an MPS sparse-matvec operator. Full-graph steady-state timing improved to 43–46 ms per 5 ms block, still far above the 4 ms deadline; no guard was relaxed and the desktop default remains the reviewed subset.

## Screen-aware interaction implementation

- Added explicit opt-in coarse screen-feature capability with Screen Recording permission, bounded thumbnail input, staleness/size validation, and fail-closed geometry-only fallback. Raw pixels, OCR, text, titles, URLs, and plugin output remain outside neural state.
- Added bounded cursor yielding and neutral walking along screen edges or approved host-window surfaces; no needs, reward, collection, deprivation, or connector authority were introduced.
- Replaced the placeholder pet silhouette with an attributed procedural fly renderer while preserving transparent click-through behavior.
- Updated operator, configuration, attribution, and macOS verification documentation. Validation passed: backend 56, Node 28, policy tests 19, foundations/launch/config checks, and a 5-second Electron smoke launch. Owner-only manual Screen Recording permission checks remain.

## Cursor interaction correction

- Diagnosis: the desktop shell had a cursor-yield implementation but never supplied native cursor coordinates, so the running pet could not respond to the pointer. The connectome path also applied motor output without the geometry-only yield overlay.
- Fix `f9ec613`: poll `screen.getCursorScreenPoint()` on a bounded 50 ms timer outside the neural tick, normalize the point at the motion boundary, and apply the existing capped yield velocity to connectome presentation. No neural weights, graph, permissions, or app-action authority are changed.
- Validation: Node 30 passed; foundations and launch validation passed; updated Electron instance restarted successfully.

## Static-fly diagnosis (live observation)

- Symptom: fly moved briefly then sat static and ignored the cursor. Two independent causes found by running the real Node-to-Python pipeline, not by unit tests.
- Cause 1, motion shape: the motor decoder only produced left/right/forward and `dy` was always 0, so the pet slid on one horizontal line and flipped heading 180 degrees. Fix: `MotorCommand.turn` (bounded +/-3 rad/s, normalized right-minus-left imbalance x fixed gain, existing gains only, no new circuit mapping); the presentation integrates heading from it and steers back inward near screen edges (geometry rule). A 20 s live run covered x 327 / y 359 points and moved 99 percent of ticks.
- Cause 2, cursor: configured flee was 40 pt radius / 40 pt/s / 250 ms (about 10 points of movement). Now 140 pt / 150 pt/s (cap 160) / 600 ms / 200 ms cooldown, still bounded and still geometry-only.
- Cause 3, freeze: the hard 4 ms block-deadline latch trips and permanently stops the worker (by design). Measured block time: 0.19 ms median back-to-back (max <1 ms, GC off), but with the idle gaps of the real app the median is 0.5-0.8 ms and about 0.02-0.17 percent of blocks exceed 4 ms (occasional 8-31 ms). The Python cyclic GC was one spike source (82 ms seen); the worker now disables it outside timed blocks (gen-0 collect every 200 blocks, outside timing). A macOS USER_INTERACTIVE QoS hint was tested and made no difference, so it was not added.
- Residual: the latch still trips within seconds to about a minute. The guard was NOT relaxed. Relaxing it (for example tolerating isolated late blocks without catching up simulated time) is an owner decision recorded as an open item.
- Validation: Node 32 passed, backend 59 passed, foundations and launch validation passed. One combined shell command including the protected policy-test paths was blocked by the policy hook and was not retried; those files were not modified.

## Owner-approved late-block tolerance (implemented)

- Decision: Cam chose to tolerate isolated late blocks (option 2) after the evidence above. Implemented as a fixed, validated, static policy (`late_block_max_consecutive=2`, `late_block_max_per_second=6`, `late_block_hard_cap_s=0.05`); defaults when absent are strict (zero tolerance). Pure guard in `backend/flysim/deadline.py`; wired in `desktop_neural.py`; policy schema bounds in `config.py` (consecutive <= 4, per-second <= 12, cap <= 0.05 s, cap >= budget, booleans rejected).
- Unchanged: the 4 ms per-block budget, permanent stop with no automatic resume, `auto_restart_after_hard_fault=false`, `recovery.allow_threshold_relaxation=false` (that flag forbids automatic runtime relaxation; this is a reviewed static owner decision). Nothing adapts or widens after a fault. Simulated time is not caught up for a late block (presentation clock caps catch-up at 50 ms).
- Visibility: worker status now carries `timing` (late total, in a row, last second, worst, limits); the Health card says "on time, with N brief late moments so far (longest X ms); more than 2 in a row stops the fly".
- Evidence: backend 70 passed, JS 33 passed. Live Node-to-Python run for 120 s: no fault, moving 100 percent of ticks, track 404 x 415 points, 1 late block (4.7 ms) tolerated and reported.
- Not verified: behavior over multi-hour sessions; behavior under heavy system load (a genuinely sustained slowdown is expected to hard-fault, by design).

## Second owner decision: no wall-clock stop, planned 5-minute clean start

- Evidence: 172 s soak stopped on 3 late blocks in a row (10 ms vs 4 ms) with CPU time under budget; host load average about 6 (Cursor renderer and Trend Micro each near 100 percent of a core).
- Cam chose: no cap on the fly, with a reset after 5 minutes of its own clock. Implemented as `late_block_wall_fault=false` plus `scheduled_state_reset_s=300` in `config/policy.json` (schema: strict bool, 0..3600 s). Slow blocks stay counted and shown. Kept: strict CPU-time fault, Electron 0.25 s tick supervisor, stop latch, no auto-resume, `auto_restart_after_hard_fault=false`. The reset restores the reviewed initial neuron state only (weights untouched), runs between requests, never after a fault, and is not a recovery step.
- Also done: ~60 Hz window glide in `desktop/main.mjs` (extrapolates the last pose, cosmetic only), renderer gait/wings/grooming in `desktop/renderer/pet.js`, dashboard wording for non-fatal late blocks.
- Evidence: backend 80 passed (includes a 300-simulated-second worker reset test), Node 36 passed, foundations and launch validation PASS, 330 s live soak no fault (13 slow blocks, worst 6.95 ms), screenshot shows the rendered fly turning between frames.
- Not verified: owner's visual judgement of realism and cursor chase; multi-hour runs; behavior of the reset visible on screen (fly may briefly settle after each reset).

