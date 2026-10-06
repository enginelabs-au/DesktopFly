# data

- `raw/` — immutable source downloads (not committed). Record URL, bytes, SHA-256, license, date.
- `derived/` — reviewed graph bundles.
- `reviews/` — allowlists, exclusions, signs, evidence.

Runtime must work without downloading. A missing source file fails setup, not the neural loop.

The default runtime graph is MaleCNS v1.0. FlyWire v783 is a separate,
female-brain dataset and is never auto-merged into MaleCNS. Run
`python scripts/download_flywire.py` to download the pinned proofread
connectivity and annotation releases, verify the source checksum, and write
canonical FlyWire parquet tables under `derived/`.
