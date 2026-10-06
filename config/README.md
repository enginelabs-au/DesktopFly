# config

Committed operational policy. `policy.json` is the frozen startup document. Changing numeric gates requires a new configuration hash and a repeat of affected tests.

`real_graph_enabled` is `true` under the recorded owner override
(`docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md`). This enables
the connectome-informed controller; it does not prove absence of consciousness
or suffering. MPS is required for the configured full-graph desktop run and
CPU fallback is disabled so a missed timing capability cannot be hidden.

Screen capture remains disabled by default. The desktop menu can make an
explicit runtime opt-in; only coarse numeric features are retained and
permission denial returns to geometry-only operation.
