# Decision: MaleCNS v1.0 is the default dataset

**Date:** 2026-09-16  
**Status:** accepted  
**Product:** DesktopFly (P-011)

## Decision

Default anatomy and any future graph ingest use **MaleCNS v1.0** (`male-cns:v1.0`). Starting weights file: `connectome-weights-male-cns-v1.0-minconf-0.5.feather`. FlyWire v783 is a separate adapter with its own atlas and IDs. Do not mix identifier spaces.

## Why

The cobanov template atlas uses MaleCNS. Official downloads and CC-BY licensing are documented at [male-cns.janelia.org](https://male-cns.janelia.org/). FlyWire FAFB is a female brain dataset and does not supply the complete nerve-cord/muscle controller used by that atlas.

## Consequences

- Neuron IDs remain dataset-qualified strings.
- Downloads are setup-only; runtime networking is loopback IPC.
- Caps for any later real graph: 2,048 neurons, 100,000 edges.
