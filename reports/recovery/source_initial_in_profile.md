# Recovery recipe: source_initial_in_profile

Status: scaffold acceptance for Phase 4.

- Does not mutate neural weights, dt, caps, or watchdog limits.
- Selected only while neural execution is paused.
- Missing or failed evidence disables automatic use.
