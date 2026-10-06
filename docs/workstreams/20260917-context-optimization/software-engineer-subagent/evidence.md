# Software engineer evidence

## Reconstruction

- Shared source `/Users/camdouglas/agent-instructions` is not on this Cloud Agent VM. Candidate rebuilt from `diffs/agent-instructions-r1.patch` (sha256 `48fe6d24df1bc5103b2724b45ed645711a2db32c6fa67fde6593ab68958aeb0c`, matches receipt) applied to DesktopFly, which matched 21/25 baseline hashes.
- Candidate manifest: 81/88 hashes matched. Mismatches were project-local `STATE.md`, `TOOLS.md`, `LAUNCH.md` (30 bytes), `MEMORY.md`, `.gitignore`, `LICENSE` (absent), `README.md` (product README).

## Fixture

- Path: `/tmp/r1-fresh-fixture` (root `AGENTS.md` omitted so bootstrap could seed it). A path with a space was attempted; combining `mv` with a `.cursor/rules` listing in one command was blocked by fail-closed policy, so the hyphenated path was used.
- Bootstrap ×2: idempotent file hashes identical.
- Validators pass; preflight `READY`; 23 tests pass.
- Identity script: non-anonymous email exit 1; `cursoragent@noreply.github.com` exit 0.
- Direct `git commit` with a private email in the shell command was blocked by the parent DesktopFly policy before fixture hooks ran.

## DesktopFly apply

- Route: `bash docs/handover/apply-context-optimization-r2.sh` (hooks denied direct edits to protected paths).
- After apply: validate-agent-config complete; validate-launch 87 files; preflight READY; 23 tests pass.
- W4: unlinked `unlinked-w4-probe.md` produced a warning and exit 0; probe deleted.

## Not measured

- Input/output tokens and cash cost: UNKNOWN.
