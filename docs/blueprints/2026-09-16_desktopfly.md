# DesktopFly product blueprint

**Date:** 2026-09-16  
**Slug:** desktopfly  
**Status:** accepted for phase-0 planning  
**Owner:** Cam Douglas (one-operator studio)  
**Workstream:** `docs/workstreams/20260916-desktopfly-foundations/manifest.md`

## 1. Executive decision

Build a **local macOS desktop pet**: a frameless, transparent, click-through fruit fly that follows the selected window. Movement is **connectome-informed** in architecture, but **neural simulation stays disabled** while Q-012 (absolute proof of zero possible suffering) remains a release requirement. First shippable slice is anatomy viewing plus an **explicitly authored animation controller**. Do not describe the app as an uploaded fly, a conscious organism, or a faithful whole-nervous-system reproduction.

Default anatomy: **MaleCNS v1.0**. Shell: **Electron + Swift helper**, not Papership Tauri. First user: Cam on Apple Silicon.

**Build.** The product is a specific, integratable system with a hard safety contract. It is not a generic AI wrapper. Public marketing and Lab copy wait until the local pet exists and claim language is reviewed.

## 2. Evidence and research method

Inspected this run (16 Sep 2026):

- Repository `enginelabs-au/desktopfly` `main` @ `61c436f` (LAUNCH.md rename). Previous `cursor/phase-0-foundations-6edd` was never pushed; no product source.
- Canonical spec: `docs/handover/fruit-fly-cursor-handover.md` (16 Sep 2026).
- Engine Labs context: P-011, working constraints, Q-012.
- Public sources retrieved this session:
  - [MaleCNS project](https://www.janelia.org/project-team/flyem/male-cns-connectome), [downloads](https://male-cns.janelia.org/download/), [explore](https://male-cns.janelia.org/explore/) — v1.0 released 8 Jun 2026; CC-BY.
  - [cobanov/fly-connectome-template](https://github.com/cobanov/fly-connectome-template) HEAD `38f55332055328d38c29e72474c4ad5b6876101f` — anatomy/model-output starter; custom license requires web UI and repository attribution.
  - Electron transparent / click-through window APIs.
  - Desktop-pet substitutes: [OpenPet](https://github.com/dengyie/OpenPet), [Desktop Pet Mitarashi](https://github.com/Sunwood-ai-labs/desktop-pet-mitarashi).
  - [Butlin et al. consciousness-indicator framework](https://arxiv.org/abs/2308.08708) (handover citation; not a software test of absence).

No user interviews, analytics warehouse, or Mac runtime were available in this environment. Do not treat this as market validation of demand.

## 3. Intelligence report

Repeated needs in the handover and Cam’s constraints:

- An unobtrusive companion that does not steal focus or block clicks.
- Scientific honesty: structural connectome as input to a simplified controller, not a sentience claim.
- Operator-readable health: software limits, not feelings.
- Hard stop latches; neural output never grants tool authority.

Workarounds today: research viewers (Neuroglancer, neuPrint, VVDViewer, navis) or generic desktop pets. None combine MaleCNS-qualified IDs, a fail-closed no-affect contract, and a native-feeling overlay.

## 4. User / problem definition

**Primary user:** Cam, working on an Apple Silicon Mac.

**Job:** Keep a visually precise fly on the desktop that follows the current window without interrupting typing, without inventing biology, and without implying the software can suffer or need care.

**Success:** The pet stays usable over browser, editor, and Finder; menus and a menu-bar status exist; workbench/health open only on request; claims stay within implementation facts.

## 5. Competitive landscape and gap

| Alternative | Job | Why it fails this brief |
|---|---|---|
| Do nothing | No overlay | No product |
| Neuroglancer / neuPrint / VVDViewer / navis | Inspect MaleCNS / FlyWire | Research tools, not a click-through pet |
| OpenPet | Electron pet + AI chat + plugins | Opposite safety posture: plugins, chat, growth loops |
| Mitarashi / Neko / Shimeji | Cute overlay | Authored sprites only; no connectome contract |
| Papership Tauri shell | Company OS | Different product; do not share the window stack |

**Gap:** a macOS pet whose *architecture* can later attach a reviewed MaleCNS subset, while *release* currently forbids enabling that controller.

## 6. Unique value proposition and wedge

A MaleCNS-attributed desktop fly with an enforceable no-affect / no-learning / no-needs contract, defaulting to authored motion until Q-012 is resolved. Wedge is **constraint fidelity**, not “more alive.”

## 7. Validation experiments and thresholds

| Assumption | Cheap test | Pass |
|---|---|---|
| Transparent click-through overlay works on Cam’s Mac | Phase 3 native matrix on real hardware | Text selection and drag work through the backing surface |
| Authored motion is enough for a useful pet | Phase 2/3 demo without neural worker | Cam can leave it running during ordinary work |
| Template attribution is satisfiable | Pin commit + license review | Credits in UI and `provenance/template.json` |
| Neural disable is load-bearing | Config + tests | `real_graph_enabled=false`; worker never starts LIF |
| Q-012 stays blocking for neural enable | Recorded decision | No enable without owner change |

This environment cannot run Mac-only gates. Those stay deferred, not claimed.

## 8. Product requirements

| ID | Requirement | Owner |
|---|---|---|
| DF-P01 | Default product is the desktop pet, not the workbench | product |
| DF-P02 | Frameless, transparent, click-through; no permanent dashboard | ux |
| DF-P03 | Follow selected window without taking keyboard focus | ux / swe |
| DF-P04 | MaleCNS v1.0 default; FlyWire v783 is a separate adapter | swe |
| DF-P05 | Neural sim disabled while Q-012 is a release requirement | product / sec |
| DF-P06 | Authored animation + anatomy viewer are the live path | swe |
| DF-P07 | No affect, needs, reward, learning, or self-modification | sec |
| DF-P08 | Supervisor owns stop latches; neural output never authorizes tools | sec |
| DF-P09 | Caps: 2,048 neurons / 100,000 edges when a graph exists | swe |
| DF-P10 | Loopback IPC only at runtime; downloads are setup-only | swe / sec |
| DF-P11 | Plain-language health; “Healthy” = checked software limits | ux / pm |
| DF-P12 | Screen capture off by default; denial is a usable fallback | sec / ux |
| DF-P13 | Preserve template and dataset attribution | pm |

## 9. MVP scope and non-goals

**Version 1 (shippable while Q-012 is open):**

- Control-plane + fly-simulation rule + policy files
- Template pin and directory layout
- Anatomy / authored-animation pet on macOS
- Menu bar, Find fly, on-demand health/workbench
- Supervisor and stop latch for the *process*, even with LIF off

**Later, only after Q-012 is withdrawn or reframed:**

- Reviewed MaleCNS subset, LIF worker, real-graph enable

**Excluded:** food/sleep/affect/learning; Papership embedding; Windows/Linux v1; public Lab claims; capability connectors that write to other apps; FlyWire as default.

## 10. System architecture and data model

```text
Electron shell ── Swift DesktopContext (AX / optional ScreenCaptureKit)
       │
       ├── pet renderer (authored animation; template assets)
       ├── on-demand workbench / health
       └── capability broker (user-invoked; isolated; no neural authority)

Optional later (disabled):
  supervisor ── spawn worker (LIF / MPS) ── loopback WebSocket bridge
```

**Authoritative clock:** one simulation/presentation clock. Authored animation uses the presentation clock; a future LIF worker must not create a second production clock.

**Data:**

- Immutable `data/raw/` downloads (URL, bytes, SHA-256, license, date)
- Derived `data/derived/` graphs only after review
- `config/policy.json` frozen at startup; `real_graph_enabled: false`
- Neuron IDs remain dataset-qualified strings

Rejected alternatives: Tauri (handover + product boundary), CUDA/GNN training stack, Brian2 as production clock, dense N×N matrices.

## 11. Interfaces and integrations

- Local WebSocket `127.0.0.1` only, when a worker exists
- Swift helper: read-only Accessibility; ScreenCaptureKit optional
- Future connectors: explicit user request, isolated process, never driven by spikes
- No cloud backend, no telemetry vendor, no Hermes/Papership runtime coupling

## 12. Security, privacy, reliability, compliance

- Secrets: none required for v1 local run. Env names only if later connectors appear.
- Screen content is optional and local; default off.
- Accessibility is read-only window geometry, not keylogging.
- Hard fault → latched stop; no auto-restart.
- License: MaleCNS CC-BY; template custom attribution; record both before bundling assets.
- Claims: never publish proof of non-consciousness.

## 13. Delivery phase map

| Phase | Purpose |
|---|---|
| 0 | Foundations: layout, policy, fly rule, pin, CI-local checks, planning artifacts |
| 1 | Safe ingest/filter/synthetic fixture; `real_graph_enabled` remains false |
| 2 | Authored pet motion + world/clock; LIF module exists but cannot start |
| 3 | Electron overlay, Swift helper, menus, click-through, IPC |
| 4 | Health language, supervisor, kill switches, recovery recipes |
| Final | Mac verification, attribution UI, owner checklist |

Handover phases 1–4 remain the scientific/product gates. Phase 0 is the missing repository foundation.

## 14. Cultural go-to-market

Not a growth workstream. First audience is Cam. Public Lab article is later editorial (T-034), only with evidence and honest claim language. No Reddit launch, no plugin marketplace, no “alive pet” positioning. If a public note is written later: problem-first (desktop companions vs research viewers), transparent constraints, and a useful resource (MaleCNS attribution + what the software does *not* claim).

## 15. Risks, pivots, and no-build criteria

| Risk | Handling |
|---|---|
| Q-012 never resolves | Keep authored-animation product; do not enable LIF |
| Template license blocks bundling | Anatomy-only fallback or link-out; do not strip credits |
| Linux CI cannot prove Mac overlay | Separate `macos_only` gates; never claim them from Linux |
| Invented cell-type safety lists | Fail closed; synthetic fixture only |
| Desktop-pet market is crowded | Accept; this is a studio experiment, not a TAM play |

**No-build if:** Cam withdraws the pet, or requires a sentience guarantee the project cannot make *and* refuses the authored-animation alternative. Current instruction is the alternative: ship with neural sim off.

## 16. Sources and research limitations

- Handover is implementation spec, not a completed app.
- Template HEAD pin is a git SHA, not a license legal review.
- Competitive scan used public GitHub/docs this session; not exhaustive app-store research.
- This VM is Linux; Electron/Swift/MPS were not executed.

## 17. Handoff into phase 0

Create and execute `docs/plans/phase_0_foundations_plan.md`. First mutations after bootstrap: fly-simulation rule, committed directory layout, `config/policy.json` with `real_graph_enabled: false`, provenance pin, and workstream role artifacts.
