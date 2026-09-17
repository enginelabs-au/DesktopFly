# 12 · Remaining-work register

Status after Cursor v1.3 (2026-09-17). Labels: implemented / validated / proposed / deferred / blocked.

| ID | Status |
|---|---|
| W1 | **blocked** on a fresh Cursor session (Customize panel unavailable; this session injected pre-R1 rules). Planning cue strengthened. |
| W2 | **validated (partial)** — one security subagent; avoided TOOLS/LAUNCH/STRATEGY/other roles; still read INSTRUCTIONS/SUBAGENTS/STATE |
| W3 | **implemented** on owner-selected DesktopFly; papership not touched |
| W4 | **implemented** and validated with an unlinked runbook warning |
| W5 | **blocked** owner-only; surfaced, not performed |
| W6 | deferred (owner MCP UI; not this VM) |
| W7 | deferred (no `.agents/` in DesktopFly) |
| W8 | deferred (insufficient W2 evidence to split ROLES.md) |
| W9 | deferred (TOOLS.md was not loaded by W2) |
| W10 | deferred (owner decision on template history) |
| W11 | **implemented** for bootstrap + validate-agent-config payloads; other payload duplicates unchanged |
| W12–W14 | deferred |

Priority: P0 blocks promotion of the R1 batch; P1 is justified next work; P2 is conditional; P3 is owner-only or deferred. "Needs" states who can do it and what access it requires. Nothing here is authorized merely by being listed.

| ID | Priority | Item | Depends on | Rationale | Acceptance criteria | Verification / needs |
|---|---|---|---|---|---|---|
| W1 | P0 | Native loading validation of the candidate in a live Cursor session (fresh chat, candidate fixture or an owner-selected canary workspace) | none | Effective injection and reread compliance are `UNKNOWN`; deterministic checks cannot show them | (a) Fresh session shows the three always-on rules and root `AGENTS.md` applied and no others; (b) a routine bounded edit completes without reading `TOOLS.md`, `ROLES.md`, `LAUNCH.md`, `STRATEGY.md`; (c) second turn does not re-read the core files; (d) a "new project" request in natural language pulls in `project-planning.mdc` or routes to `PROJECT_PLANNING.md`; (e) a superficially similar request (e.g. "plan my weekend") does not; (f) `/launch-pipeline` still runs preflight first and does not auto-start from ambient wording | Cursor native session, Customize → Rules/Skills panel, the rule-usage indicator in chat; record observations verbatim in the pack's evidence folder. Model self-reports are proxies and must be labelled. |
| W2 | P0 | Subagent preload behaviour | W1 | Whether rules/AGENTS.md inject into subagents is undocumented (E08 UNKNOWN); adapters now say "read `.cursor/AGENTS.md` only if not already in context" | One read-only role (e.g. `security-engineer-subagent`) on a harmless fixture reads its charter, `ROLES.md` §1–3 and own section, returns the canonical handoff, and does not read other role sections or the seven core files | Cursor native subagent run; inspect the subagent transcript |
| W3 | P1 | Propagate the R1 batch to one owner-selected current-generation consumer (`DesktopFly` or `papership`) | W1, W2 pass | Shared-source changes are inert until copied; propagation is where real usage happens | Managed files copied (rules, `AGENTS.md`, `BOOTSTRAP.md`, `INSTRUCTIONS.md`, adapters, `ROLES.md` §3.2, scripts, templates, `README`s); project-local files preserved (`STATE.md`, `USER.md`, memory, extra rules such as `fly-simulation.mdc`, extra runbooks); validators pass; CI workflow passes; consumer's root `AGENTS.md` replaced by the seeded template only with owner consent | Cursor with owner selection; hooks protect these paths, so use the owner-authorized apply route |
| W4 | P1 | `validate-launch.mjs` rejects legitimate project-local additions (observed in `puffpuffstop`: unlinked runbook) | none | Validator coupling produces false failures in consumers | Project-local runbooks/memories are accepted when listed in `MEMORY.md` **or** a project index, or the orphan check downgrades to a warning for `memory/runbooks/` | unit test + run in `puffpuffstop` |
| W5 | P1 | Rotate the API key stored as a plaintext argument in `~/.cursor/mcp.json` and `~/.codex/config.toml`; move tokens to environment references where the client supports it | none | Key was echoed into a session log during inspection; prior audit reported the same class of exposure | New key issued, old key revoked, configs reference env vars or the client's secret store | **Owner only** (credential operation) |
| W6 | P2 | Scope or disable the global MCP servers bound to `/Users/camdouglas/quark` (`filesystem`, `cline`) and review the other nine global servers for per-project relevance | owner decision | Fixed bindings load unrelated tools in every workspace; R2 candidate | Servers needed per project are enabled per project or via profile; unrelated schemas absent in an unrelated workspace; no loss of the `quark` workflow | Cursor MCP settings UI; before/after tool counts in Customize |
| W7 | P2 | Resolve the template's untracked `.agents/skills` duplicates (Cursor scans `.agents/skills` first, then `.cursor/skills`) | owner decision | Duplicate catalog entries and drift between two copies | One canonical location per skill; if `.agents/skills` is kept for Codex compatibility, the `.cursor/skills` copy is removed or vice versa; validator checks for same-name skills across both directories | owner decides; validator change + fixture |
| W8 | P2 | Extract `ROLES.md` §3 (27 KB shared contract) into `instructions/ROLE-CONTRACT.md` so roles read ~9 KB instead of ~31 KB before their own section | W2 | Further per-role reduction; separate batch for attribution | All six adapters and `ROLES.md` cross-reference correctly; validator terms updated; role run reads the smaller set | fixture + one role run |
| W9 | P2 | Trim generic prose in `TOOLS.md` (purpose/update rules/entry format, ~4 KB) and `SKILLS.md` (~2 KB) that the model can already infer | W1 | Pack §04 §4/§11; on-demand now, so lower priority | Unique constraints (Supabase Gatekeeper note, Vercel `--prod` gating, Figma limits) preserved; validator terms still present | diff review |
| W10 | P2 | Template history hygiene: `memory/memories/2026-08-18-continuation.md` and `2026-09-17-continuation.md` are template-development history that every copy inherits | none | Pack §01 ownership rule (no task history into new projects) | Decide: keep in the template's own docs (outside `.cursor/`) or document "clear `memory/memories/` when copying" in README; bootstrap must not delete user files | owner decision |
| W11 | P2 | Consolidate git-safety `payloads/` duplicates (six byte-identical copies of canonical files) into a generated/checked artifact | none | Drift risk; no context cost | Either payloads are generated from canonical files by a script with a hash check in the validator, or the skill references canonical paths | validator + test |
| W12 | P3 | Provider routing (R3): Codex CLI repair, Claude Code `CLAUDE.md` adapter, Gemini adapter | R1 promoted | Nothing to route yet; two clients lack working adapters | Only if a measured need appears | defer |
| W13 | P3 | Cross-repo registry/runner (R4) | R3 | No evidence of need | defer | defer |
| W14 | P3 | Consumer drift: `puffpuffstop`/`context` root `AGENTS.md` reference `LAUCH.md` (typo) and lag the template; older consumers lack hooks entirely | W3 pattern | Correctness in live projects | Owner decides which consumers receive the batch | Cursor, per repository, with owner consent |

Blocked in this pass: W1, W2 (needed a live or authenticated Cursor session). Deferred by evidence: W6–W13. Owner-only: W5, and the consent points in W3, W7, W10, W14.
