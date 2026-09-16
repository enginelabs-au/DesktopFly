# Agent governance operator setup

Human-only controls that sit outside the in-repo agent policy. Agents must not request secret values here.

## GitHub

- Protect the default branch.
- Require the `agent-governance` workflow to pass before merge.
- Restrict who can edit `AGENTS.md`, `.cursor/hooks/`, `.cursor/cli.json`, `.cursor/permissions.json`, `.cursor/sandbox.json`, `.cursorignore`, and `.github/workflows/agent-governance.yml`.

## macOS signing and notarization

Deferred until a signed desktop build is required. Record names only. Values stay in the owner's secret manager.

- `APPLE_DEVELOPER_TEAM_ID`
- `APPLE_ID`
- `APPLE_APP_SPECIFIC_PASSWORD`
- `APPLE_SIGNING_IDENTITY`

## Optional later integrations

No production deploy or remote schema mutation is authorized by this file.

- Vercel: optional if a hosted workbench is added later
- Supabase: optional if cloud accounts or telemetry are added later
