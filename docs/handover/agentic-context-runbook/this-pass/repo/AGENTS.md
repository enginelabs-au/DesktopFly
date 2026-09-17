# AGENTS.md

Native project-wide instructions for this repository. Paths in this file are repository-relative. A leading `/` inside a `.cursor/` control file is relative to `.cursor/`, not to the filesystem root.

## Core constraints

- Git writes use `Cursor Agent <cursoragent@noreply.github.com>` or a GitHub noreply address. Never change git identity with `git config`; never use `--no-verify`.
- Never read, stage, commit, print, or store secrets, credentials, `.env*` (except `.env.example`), private keys, or credential JSON.
- Production deploys, remote database mutation, destructive git, protected control-plane edits, and state-changing MCP tools stay owner/CI-controlled. A hook denial is final: stop, do not work around it.
- Work within the task scope, inspect existing patterns first, make surgical changes, validate with the strongest available checks, and report what remains unverified.
- Operate autonomously; ask only for missing credentials or permissions, consequential decisions with no defensible default, destructive work beyond scope, or safety/privacy concerns.

## Loading policy

- Implementation, launch, resume, or other project-consequential work: read `.cursor/AGENTS.md` once, run `node .cursor/skills/launch-pipeline/scripts/preflight.mjs`, and check `.cursor/STATE.md` for active work.
- Ask-mode questions and pure acknowledgments skip preflight and extra control-plane reads.
- Later turns: reuse what is already in context. Re-read a control file only when it changed, after context loss or compaction, or when a new scope becomes relevant.
- An ordinary bounded change needs no workstream, role pipeline, or phase plan.
- Subagents run only when the user explicitly permits them, or when `/launch-pipeline` requires a named role.

## Routing index

| Need | Read |
|---|---|
| Detailed contract, precedence, autonomy limits, completion standard | `.cursor/AGENTS.md` |
| Which detailed mode applies (planning, strategy, sub-agents, roles) | `.cursor/INSTRUCTIONS.md` registry |
| New project, major feature, migration, sequential phases | `.cursor/instructions/PROJECT_PLANNING.md` |
| Raw idea, new product, major feature, migration, resume, remediation, closure | invoke `/launch-pipeline` explicitly; contract in `.cursor/instructions/LAUNCH.md` |
| Specialist selection, delegation, stage gates | `.cursor/instructions/ROLES.md` (sections 1–3 plus the relevant role section) |
| Repeatable procedures such as deploys, migrations, git safety | `.cursor/SKILLS.md` → `.cursor/skills/<skill-id>/SKILL.md` |
| Choosing deployment, database, or integration tooling | `.cursor/TOOLS.md` |
| Prior decisions, exact runbooks, unresolved blockers | `.cursor/memory/MEMORY.md` and the files it links |
| Task artifacts | `docs/plans/`, `docs/workstreams/<task-id>/` |

Role names and prompts do not grant authority. Hooks, permissions, sandboxing, CI, and explicit owner approval govern sensitive actions.
