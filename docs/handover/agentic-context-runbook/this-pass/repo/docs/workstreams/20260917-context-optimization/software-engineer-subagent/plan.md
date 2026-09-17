# Software engineer plan

1. Reconstruct R1 from the v1.2 patch onto a DesktopFly-matching tree; hash-compare to `candidate-source-manifest.json`.
2. Recreate a disposable fixture, bootstrap twice, run validators/tests.
3. Record Phase 1 defects; do not revert sound R1 decisions.
4. Stage R2 corrections in `/tmp/r2-staging`; copy unprotected files; apply protected files with `docs/handover/apply-context-optimization-r2.sh`.
5. Prove W4 with a temporary unlinked runbook, then delete it.
6. Update pack, state, memory, operator handover.
7. Do not edit `hooks/policy.mjs`, `hooks.json`, `permissions.json`, or `sandbox.json`.
