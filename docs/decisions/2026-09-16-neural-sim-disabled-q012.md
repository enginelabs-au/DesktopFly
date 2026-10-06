# Decision: neural simulation stays disabled while Q-012 is a release requirement

**Date:** 2026-09-16  
**Status:** accepted  
**Product:** DesktopFly (P-011)

## Decision

Do not enable the neural / LIF simulation while Q-012 (absolute proof of zero possible suffering) remains a release requirement. The live controller is anatomy viewing plus an explicitly authored animation policy. `config/policy.json` must ship with `real_graph_enabled: false`. A future enable is an owner decision that invalidates this record.

## Why

The handover states that a literal proof of zero possible suffering is not scientifically available. Implementation facts (no affect, no learning, no neuromodulators) do not constitute that proof. Cam’s current instruction, via the Engine Labs queue and this launch, is to keep the sim disabled rather than invent a guarantee.

## Consequences

- Phase 1 may ingest and test synthetic fixtures; it must not start a production LIF worker.
- Phase 2–4 may implement LIF *code paths* behind the flag for later use; those paths stay unstarted.
- Operator copy must not imply a live connectome controller while the flag is false.
- Enabling the graph is out of scope until Q-012 is withdrawn or reframed by Cam.

## Non-decision

This does not resolve Q-012. It records the working release condition.
