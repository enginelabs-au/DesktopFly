"""Dataset adapter package: raw export → canonical tables."""

from flysim.adapters.flywire import FlyWireAdapter
from flysim.adapters.malecns import MaleCNSAdapter

__all__ = ["MaleCNSAdapter", "FlyWireAdapter"]
