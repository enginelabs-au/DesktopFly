# data

- `raw/` — immutable source downloads (not committed). Record URL, bytes, SHA-256, license, date.
- `derived/` — reviewed graph bundles.
- `reviews/` — allowlists, exclusions, signs, evidence.

Runtime must work without downloading. A missing source file fails setup, not the neural loop.
