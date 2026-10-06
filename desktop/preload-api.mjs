/**
 * Narrow preload channel names and payload validators.
 */

export const IPC = Object.freeze({
  GET_STATUS: "fly:get-status",
  FIND_FLY: "fly:find-fly",
  FIND_CURSOR: "fly:find-cursor",
  SET_MODE: "fly:set-mode",
  OPEN_HEALTH: "fly:open-health",
  OPEN_WORKBENCH: "fly:open-workbench",
  ENABLE_VISION: "fly:enable-vision",
  DISABLE_VISION: "fly:disable-vision",
  HOST_LEASE_BEAT: "fly:host-lease-beat",
  POSE_FRAME: "fly:pose-frame",
});

const MODES = new Set(["follow_my_window", "explore_and_hide"]);

export function validateMode(mode) {
  if (!MODES.has(mode)) throw new Error("invalid mode");
  return mode;
}

export function validatePoseFrame(frame) {
  if (!frame || frame.version !== 1 || frame.type !== "pose") {
    throw new Error("invalid pose frame");
  }
  const p = frame.pose;
  if (!p) throw new Error("missing pose");
  for (const key of ["x", "y", "headingRad", "speedPointsS", "depth01"]) {
    if (!Number.isFinite(p[key])) throw new Error(`non-finite ${key}`);
  }
  if (p.depth01 < 0 || p.depth01 > 1) throw new Error("depth01 out of range");
  if (!["idle", "crawl", "flight"].includes(p.locomotion)) {
    throw new Error("invalid locomotion");
  }
  if (
    p.surfaceContact !== undefined &&
    !["none", "screen-edge", "host-window-surface"].includes(p.surfaceContact)
  ) {
    throw new Error("invalid surface contact");
  }
  if (!["authored-animation", "lif"].includes(frame.controller)) {
    throw new Error("unknown controller");
  }
  if (!["stopped", "running", "unavailable", "starting"].includes(frame.neuralWorker)) {
    throw new Error("invalid neuralWorker status");
  }
  return frame;
}

/** API surface exposed to the sandboxed pet renderer via contextBridge. */
export function preloadApiShape() {
  return [
    "getStatus",
    "findFly",
    "findCursor",
    "setMode",
    "openHealth",
    "openWorkbench",
    "enableVision",
    "disableVision",
    "onPoseFrame",
  ];
}
