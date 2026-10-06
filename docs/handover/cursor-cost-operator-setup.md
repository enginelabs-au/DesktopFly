# Cursor cost and loading operator setup

Human-only Cursor client settings. This file does not authorize purchases, plan changes, credential operations, or production mutation. Agents must not store secret values here.

Measured token or cash savings remain `UNKNOWN` until the Usage dashboard is compared before and after.

## Do in Cursor Settings

- Put a short User Rule (under ~300 words) for cost policy: Ask default, no subagents unless permitted, no Cloud Agent unless requested, prefer named paths, new chat on topic change.
- Prefer an explicit low-cost model over Auto for budget-sensitive work. Confirm the model name and whether billing is plan credits or API tokens before treating a unit price as cash cost.
- Disable unused MCP servers and plugins for the active profile.
- Do not attach 16+ GitHub repos to one Cloud Environment. Use one repository per Cloud Agent run.
- Do not open `/camdouglas` (or another home directory) as the default workspace unless indexing exclusions are in place. Prefer one repository folder.
- Keep `~/.cursor/rules` empty of long always-on files. Deep procedures stay requestable in the repo.

## Do not

- Do not rotate credentials from this file. API-key rotation is owner-only (pack item W5).
- Do not add paid gateways or new API spend to measure tokens.
- Do not weaken repository hooks, permissions, or sandboxing to save tokens.

## Recommended session habit

1. Grok (or another cheap outer router) compresses the task to a repository, files, and acceptance checks.
2. A fresh local Cursor Ask chat answers from that brief.
3. Local Agent implements only when code must change.
4. Cloud Agent is reserved for unattended bounded work on a minimal environment.

## Related files

- `.cursor/rules/00-core-routing.mdc`
- `.cursor/rules/cost-and-session.mdc`
- `.cursor/USER.md`
- `docs/handover/apply-context-optimization-r2.sh`
- `docs/handover/agentic-context-runbook/`
