# Decision: neural / LIF simulation enabled (Cam override of Q-012 gate)

**Date:** 2026-09-16  
**Status:** accepted (supersedes `2026-09-16-neural-sim-disabled-q012.md`)  
**Product:** DesktopFly (P-011)

## Decision

Cam overruled the prior release gate that kept neural simulation off until absolute assurance of zero suffering (Q-012). Enable the neural graph / LIF simulation. `config/policy.json` ships with `real_graph_enabled: true`. Do **not** refuse LIF start for policy/Q-012 reasons.

## Technical blockers only

Keep LIF off only for hard technical failures (missing weights file, import/crash, invalid graph). Report the concrete error. Synthetic fixtures remain valid for development and CI when MaleCNS weights are not downloaded.

## Consequences

- Desktop shell and worker may start LIF.
- Authored animation remains a fallback / presentation aid, not the sole controller.
- Still: no affect/reward/learning machinery; neural output must not authorize connectors.
- Claims language: do not assert proof of non-consciousness.
