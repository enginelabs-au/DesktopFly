# 2026-09-16 continuation

## DesktopFly repository initialization

- User asked to init `https://github.com/enginelabs-au/DesktopFly.git`.
- Remote existed, was empty, and the caller has admin permission.
- Local folder had `.cursor/` plus `docs/fruit-fly-cursor-handover.md` and was not a git repository.
- Preflight: `BLOCKED` (missing root `AGENTS.md` and docs directories).
- Seeded README, `.gitignore`, operator handover, and the owner-run apply script.
- Applied protected files via `bash docs/handover/apply-missing-control-plane-files.sh`.
- Removed `.DS_Store` files that orphaned launch validation.
- Bootstrap and preflight: `READY`. Launch validation: 77 control-plane files.
- Assumption: init covers git remotes and control-plane materialization, not product implementation.
- First push was rejected by GitHub GH007 (private email). Rewrote the unpushed root commit with `132057194+cam-douglas@users.noreply.github.com` and pushed `main` as `579b284`.

## Git safety and anonymous identity

- User required templates and this repo to block private-email git writes and keep secrets out of git.
- Installed `/skills/git-safety`, `.githooks`, always-apply rule, policy checks, CLI denials, and secret `.gitignore` entries in DesktopFly and `/Users/camdouglas/agent-instructions`.
- Required identity: `Cursor Agent <cursoragent@noreply.github.com>`; GitHub noreply also allowed.
- Owner-run apply: `bash docs/handover/apply-git-safety.sh`.
- Broken `policy.mjs` import blocked fail-closed hooks; owner repaired import to `/skills/git-safety/scripts/git-safety.mjs`.
- Validation: 16/16 tests in both trees; DesktopFly bootstrap complete; preflight `READY`; later 90 control-plane files classified.
- Owner requested push of the git-safety controls.

## Rename launch instruction filename

- Owner superseded the old keep-the-misspelled-filename rule.
- `git mv` the launch-pipeline instruction file to `.cursor/instructions/LAUNCH.md` and updated every path/string that pointed at the old name.
- Validation: `node .cursor/skills/launch-pipeline/scripts/preflight.mjs` and launch/config validators after the rename.

## Phase 0 foundations (P-011 relaunch)

- Previous owner branch `cursor/phase-0-foundations-6edd` was never on origin. Continued from `main` @ `61c436f`.
- Preflight `MATERIALIZATION_REQUIRED` (missing `docs/blueprints`). Bootstrap `bash .cursor/scripts/bootstrap.sh` → READY.
- Wrote blueprint, phase-0 plan, Q-012 / MaleCNS / Electron decisions, workstream `20260916-desktopfly-foundations`, fly-simulation rule, layout, `config/policy.json` (`real_graph_enabled: false`), template pin `38f55332055328d38c29e72474c4ad5b6876101f`.
- Validation: `node scripts/check-foundations.mjs` passed; preflight READY; launch validation 91 files.
- Neural sim remains disabled. Next: PR, then phase 1 ingest plan only.

## Phase 1 ingest start

- Wrote `docs/plans/phase_1_safe_ingest_plan.md` after phase 0 PR #2.
- Implemented `backend/flysim/ingest.py` and synthetic three-node fixture. `PYTHONPATH=backend python3 -m pytest -q` → 7 passed.
- `real_graph_enabled` remains false. No MaleCNS download.

## Phase 2 authored motion (continuation `bc-a5af2fcb`)

- Prior owner `bc-f11a4081` unreachable; continued PR #2 @ `cb556da`.
- Wrote `docs/plans/phase_2_authored_motion_plan.md`; implemented `clock` / `world` / `authored` / inert `lif`.
- `src/pet/authored-motion.mjs` + node tests; `reports/authored-motion.json`.
- Validation: pytest 26 passed; node 3 passed; foundations check passed. Neural sim still off (Q-012).
- Next: phase-3 Electron/Swift plan only when starting that phase.
