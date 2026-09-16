/**
 * Bounded surface geometry / scene description for the pet.
 */

export function buildSceneSurfaces(windows, { maxWindows = 128 } = {}) {
  if (!Array.isArray(windows)) throw new Error("windows must be array");
  const clipped = windows.slice(0, maxWindows).map((w) => ({
    id: String(w.id),
    x: Number(w.x) || 0,
    y: Number(w.y) || 0,
    width: Math.max(0, Number(w.width) || 0),
    height: Math.max(0, Number(w.height) || 0),
    spaceId: w.spaceId == null ? null : String(w.spaceId),
  }));
  return {
    kind: "desktop_surfaces",
    count: clipped.length,
    truncated: windows.length > maxWindows,
    windows: clipped,
  };
}

export function openSpaceFallback(bounds) {
  return {
    kind: "open_space",
    bounds: {
      x: Number(bounds?.x) || 0,
      y: Number(bounds?.y) || 0,
      width: Number(bounds?.width) || 1440,
      height: Number(bounds?.height) || 900,
    },
  };
}
