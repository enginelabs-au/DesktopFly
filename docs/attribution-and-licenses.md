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

## Male CNS connectome data

- **Dataset:** Male CNS v1.0 (default connectome for the LIF graph path)
- **License:** [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)
- **Official statement:** [male-cns.janelia.org/download](https://male-cns.janelia.org/download/)
- **Notice in repo:** [`LICENSE.maleCNS`](../LICENSE.maleCNS)
- **Download provenance:** [`provenance/malecns-v1.0.json`](../provenance/malecns-v1.0.json) (written by `scripts/download_malecns.py`)

Feather files live under `data/raw/` and are gitignored. Redistributing those
files or substantial excerpts requires CC BY 4.0 compliance.

## Combined index

| Material | File |
|----------|------|
| Template license (full text) | `LICENSE.fly-connectome-template` |
| MaleCNS dataset license notice | `LICENSE.maleCNS` |
| Short third-party index | `NOTICE` |
