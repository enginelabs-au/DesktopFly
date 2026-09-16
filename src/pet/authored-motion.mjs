/**
 * Portable authored-motion helpers for the pet renderer.
 * Presentation only — not neural evidence. Electron wires this in phase 3.
 */

export function scaleForDepth(depth01) {
  if (!Number.isFinite(depth01) || depth01 < 0 || depth01 > 1) {
    throw new Error("invalid depth01");
  }
  return 1 - 0.35 * depth01;
}

export function easeSmoothstep(t) {
  const x = Math.min(Math.max(t, 0), 1);
  return x * x * (3 - 2 * x);
}

export function wrapHeading(headingRad) {
  return ((headingRad + Math.PI) % (2 * Math.PI)) - Math.PI;
}

export function clampCursorYieldSpeed(vx, vy, maxSpeed) {
  const speed = Math.hypot(vx, vy);
  if (speed <= maxSpeed || speed === 0) return { vx, vy, speed };
  const scale = maxSpeed / speed;
  return { vx: vx * scale, vy: vy * scale, speed: maxSpeed };
}

/** Find-fly placement without a neural worker. */
export function findFlyPose({ hostRect, bounds, headingRad = 0 }) {
  let x;
  let y;
  let hostSurfaceId = null;
  if (hostRect) {
    x = hostRect.x + hostRect.width * 0.5;
    y = hostRect.y + hostRect.height * 0.15;
    hostSurfaceId = "host-window";
  } else {
    x = bounds.x + bounds.width * 0.5;
    y = bounds.y + bounds.height * 0.5;
  }
  x = Math.min(Math.max(x, bounds.x), bounds.x + bounds.width);
  y = Math.min(Math.max(y, bounds.y), bounds.y + bounds.height);
  return {
    x,
    y,
    headingRad,
    speedPointsS: 0,
    depth01: 0,
    locomotion: "idle",
    visible: true,
    hostSurfaceId,
    transitionSource: "operator",
  };
}
