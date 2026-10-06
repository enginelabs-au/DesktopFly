# 2026-10-07 continuation

## Whole brain: compiled kernel, tables, measurement

- Owner: "do whatever needs to be done to give me a real simulation" (explore the screen, flee the cursor, groom). No scripted behaviour was added; the work was making the whole connectome runnable and measuring it.
- `backend/flysim/lif_fused.py`: numba kernel (serial compact of active neurons, parallel CSR propagation into per-thread partial rows with `parallel_chunksize(8)`, parallel LIF update that folds and zeroes partials and validates input codes). Equivalence test with the numpy reference over 120 steps (`tests/test_lif_fused.py`). Engine selection: `fused_lif_min_neurons` / `fused_lif_threads` in `config/policy.json` (100000 / 8), `start_fused_lif_worker`, status `numba-fused-8t`, warm-up compile at create (clock stays 0), `scheduled_reset` runs the full weight fingerprint.
- Whole-brain tables: `scripts/build_malecns_fullbrain.py` writes neurons/review parquet, `.npz` edge arrays, meta (lamina L1/L2/L3 by hex column as light decrement, VNC motor readout). `runtime_loader.py` loads `.npz` into `edge_arrays`; `review.py` compiles arrays vectorised (searchsorted body lookup, `np.unique` aggregation, CSR BFS reachability, label-propagation components). Row path unchanged; equality test added in `tests/test_ingest.py`.
- Measured (155,802 neurons, 23.5 M edges, cold start 18.6 s): engine block 2.1 ms dark, 3.5 ms one eye dark, 3.75 ms both eyes, worst 4.3–14.8 ms. Motor index cached in the engine (was 10 ms/block rebuilding a 155k dict).
- Behaviour with reviewed normalisation (incoming |w| = 1.1): inert past the lamina, motor neurons never fire.
- Per-synapse weights (w_s = threshold/25.5, uncapped): silent until any stimulus (even a 9-column spot), then ~1.5 % of neurons fire indefinitely, all motor channels saturated, 4.3 ms median. w_s 0.01 same at 0.65 %. Incoming caps 2/3/5/10 inert; cap 20 persistent again. No stimulus-driven regime without inventing cell-specific parameters. Not shipped; recorded in `reports/full-brain-spike-timing.json`.
- Default stays `reviewed_subset_name: live`. For the parallel kernel the strict 4 ms check uses wall time (`desktop_neural.py`).
- Evidence: backend 96 passed + 1 gated (`DESKTOPFLY_FULLBRAIN_TESTS=1` passes in 18 s). Node, foundations, launch validation: see end of this log.
- Honest limit restated: spontaneous exploration and grooming are not produced by a connectome point model without internal state and neuromodulation, which this project excludes by rule.
