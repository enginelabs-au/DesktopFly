/**
 * Map authored pose (screen points) to pet BrowserWindow bounds.
 * Pure helpers for unit tests without Electron.
 */

export function overlayBoundsForPose(pose, overlaySizePoints, screenBounds) {
  const size = Number(overlaySizePoints);
  if (!Number.isFinite(size) || size < 64) {
    throw new Error("overlaySizePoints out of range");
  }
  const bounds = normalizeScreenBounds(screenBounds);
  const half = size / 2;
  const cx = Number(pose?.x);
  const cy = Number(pose?.y);
  if (!Number.isFinite(cx) || !Number.isFinite(cy)) {
    throw new Error("pose x/y required");
  }
  let x = Math.round(cx - half);
  let y = Math.round(cy - half);
  const maxX = bounds.x + bounds.width - size;
  const maxY = bounds.y + bounds.height - size;
  x = Math.min(Math.max(x, bounds.x), maxX);
  y = Math.min(Math.max(y, bounds.y), maxY);
  return { x, y, width: size, height: size };
}

export function normalizeScreenBounds(screenBounds) {
  const b = screenBounds || { x: 0, y: 0, width: 1440, height: 900 };
  const width = Number(b.width);
  const height = Number(b.height);
  if (!Number.isFinite(width) || !Number.isFinite(height) || width < 1 || height < 1) {
    throw new Error("invalid screen bounds");
  }
  return {
    x: Number(b.x) || 0,
    y: Number(b.y) || 0,
    width,
    height,
  };
}
