# USER.md

Store durable user-specific instructions and preferences here. Add new durable items near the top without duplicating existing meaning.

## Standing directives

- Never perform git commit, merge, rebase, cherry-pick, pull-with-merge, annotated tag, or notes using a private inbox. Always set `GIT_AUTHOR_NAME`, `GIT_AUTHOR_EMAIL`, `GIT_COMMITTER_NAME`, and `GIT_COMMITTER_EMAIL` to the Cursor anonymous identity `Cursor Agent <cursoragent@noreply.github.com>`. A GitHub noreply address is also allowed. Never run `git config` to change identity. Follow `/skills/git-safety/SKILL.md`.
- Never stage, commit, or push secrets, credentials, passwords, tokens, private keys, or secret-bearing files. Never store secret values in markdown, plans, memory, logs, examples, or git history.
- Preserve the user's operational intent and all materially relevant requirements when improving instructions or files.
- Prefer direct execution over asking the user to perform agent-capable work.
- Operate autonomously unless blocked by credentials, permissions, a consequential design decision, destructive risk, or a material safety/security/privacy concern.
- For new projects and major implementations, use sequential phase planning beginning with `docs/plans/phase_0_foundations_plan.md`.
- Use `/launch-pipeline` and `/instructions/LAUCH.md` as the single practical entry point for raw ideas, major changes, workstream resumption, remediation, and final closure.
- Require `/launch-pipeline` to run read-only preflight first. Every pre-Build Cursor plan must close by suggesting `bash .cursor/scripts/bootstrap.sh` as the first post-Build action, then run that command after Build or explicit Agent-mode implementation authorization.
- Use the adaptive gated role pipeline for substantive multi-domain work: require exhaustive role planning before action, document required and skipped roles, and preserve evidence-backed handoffs under `docs/workstreams/`.
- Require independent security re-verification after blocking remediation and a project-lead owner handoff for consequential product or release work.
- Defer non-blocking manual actions, credentials, provider dashboard work, production DNS, and similar user-only tasks to the final phase and consolidate them into `docs/plans/final_implementation_checklist.md`.
- Keep instructions machine-readable, structured, copyable, and directly usable.
- Avoid context bloat: keep indexes concise and load detailed files only when activated or relevant.
- Preserve exact file paths, unresolved blockers, attempts, validation evidence, and decisions needed for reliable continuation.
- Keep secret values out of agent files and git; use environment-variable names only.

## Platform preferences

- Prefer commands that work on the current host operating system (Linux or macOS). Do not assume Homebrew, Gatekeeper, or a specific username.
- When a Vercel project is in scope: use `/skills/vercel-deploy-workflow/SKILL.md`; prefer Git/CLI/dashboard when MCP is unavailable.
- When a Supabase project is in scope: use `/skills/supabase-linked-migrations/SKILL.md`; use the host’s working CLI (`supabase` or `npx supabase`).
- Keep `STATE.md` and `memory/` scoped to the current workspace. Do not import another project’s memories, product names, or path conventions.
