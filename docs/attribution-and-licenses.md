# Attribution and licenses

DesktopFly depends on two attribution-sensitive upstream sources. This document
is the canonical index; the root [README](../README.md) summarizes the same
obligations for repository visitors.

## fly-connectome-template

- **Upstream:** [cobanov/fly-connectome-template](https://github.com/cobanov/fly-connectome-template)
- **License:** Cobanov Template Attribution License 1.0 — [upstream LICENSE](https://github.com/cobanov/fly-connectome-template/blob/main/LICENSE)
- **Copy in repo:** [`LICENSE.fly-connectome-template`](../LICENSE.fly-connectome-template)
- **Pin:** [`provenance/template.json`](../provenance/template.json)

### Required credit

In this repository README and in any distributed web UI (workbench, health views):

Built with [fly-connectome-template](https://github.com/cobanov/fly-connectome-template) by [Mert Cobanov](https://github.com/cobanov).

Modified versions must state that modifications were made. See
[ATTRIBUTION.md](https://github.com/cobanov/fly-connectome-template/blob/main/ATTRIBUTION.md)
for UI placement rules.

The current desktop pet image is an original procedural canvas rendering in
`desktop/renderer/pet.js`; it uses no untracked third-party image asset. The
repository still preserves the required template credit because the project
is a modified derivative.

## Male CNS connectome data

- **Dataset:** Male CNS v1.0 (default connectome for the LIF graph path)
- **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Official statement:** [male-cns.janelia.org/download](https://male-cns.janelia.org/download/)
- **Notice in repo:** [`LICENSE.maleCNS`](../LICENSE.maleCNS)
- **Download provenance:** [`provenance/malecns-v1.0.json`](../provenance/malecns-v1.0.json) (written by `scripts/download_malecns.py`)

Feather files live under `data/raw/` and are gitignored. Redistributing those
files or substantial excerpts requires CC BY 4.0 compliance.

## FlyWire v783 connectome data

- **Dataset:** FlyWire FAFB v783.0 proofread connections and v3.2.0 annotations
- **License:** CC BY 4.0
- **Connectivity source:** [FlyWire Whole-brain Connectome Connectivity Data](https://zenodo.org/records/10676866)
- **Annotation source:** [flyconnectome/flywire_annotations v3.2.0](https://github.com/flyconnectome/flywire_annotations/releases/tag/v3.2.0)
- **Download provenance:** [`provenance/flywire-v783.json`](../provenance/flywire-v783.json) (written by `scripts/download_flywire.py`)

FlyWire is a female adult brain atlas with a separate `flywire:` identifier
namespace. It is available through `FlyWireAdapter`, but is not the default
runtime graph and must not be mixed with MaleCNS identifiers.

## Looming-escape circuit: published sources and model assumptions

The reviewed escape subset (`scripts/build_malecns_escape_subset.py`) uses MaleCNS v1.0
data (see above). Which cells are looming detectors and which neuron is the giant fiber
follows the published literature; this project does not claim to have discovered it.

- Ache et al. 2019, "Neural basis for looming size and velocity encoding in the
  Drosophila giant fiber escape pathway", Current Biology.
- von Reyn et al. 2017, "Feature integration drives probabilistic behavior in the
  Drosophila escape response", Neuron.
- Wu et al. 2016, "Visual projection neurons in the Drosophila lobula link feature
  detection to distinct behavioral programs", eLife.
- Klapoetke et al. 2017, "Ultra-selective looming detection from radial motion
  opponency", Nature.
- Card and Dickinson 2008, "Visually mediated motor planning in the escape response of
  Drosophila", Current Biology (motivates turning away from a looming object).

Model assumptions made by this project (not findings): neurotransmitter signs follow the
MaleCNS `consensus_nt` label (acetylcholine +1, GABA -1, glutamate -1; unclear or
modulatory neurons are excluded); the left/right/forward readout over descending neurons
and its contralateral steering convention are engineered; the cursor is treated as a
fixed-size object whose visual angle and expansion rate are fed equally to every looming
detector on that eye (the data has no per-neuron field position); the constant intrinsic
noise (`config/policy.json`) is applied to central neurons only. None of this is a claim
about subjective experience.

## Combined index

| Material | File |
|----------|------|
| Template license (full text) | `LICENSE.fly-connectome-template` |
| MaleCNS dataset license notice | `LICENSE.maleCNS` |
| Short third-party index | `NOTICE` |
