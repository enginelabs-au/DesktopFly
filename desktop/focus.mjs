/**
 * Focus / scene tracking for follow-my-window. Geometry only; no titles or URLs.
 */

export class FocusTracker {
  constructor() {
    this.focusEpoch = 0;
    this._host = null;
  }

  /**
   * @param {{ id: string, rect: { x: number, y: number, width: number, height: number }, displayId?: string } | null} host
   */
  setFocusedHost(host) {
    if (host == null) {
      if (this._host != null) {
        this.focusEpoch += 1;
        this._host = null;
      }
      return this.snapshot();
    }
    validateHost(host);
    const changed =
      !this._host ||
      this._host.id !== host.id ||
      this._host.displayId !== (host.displayId || "primary");
    if (changed) this.focusEpoch += 1;
    this._host = {
      id: host.id,
      rect: { ...host.rect },
      displayId: host.displayId || "primary",
    };
    return this.snapshot();
  }

  snapshot() {
    return {
      focusEpoch: this.focusEpoch,
      host: this._host ? structuredClone(this._host) : null,
      preciseFocusAvailable: this._host != null,
    };
  }
}

export class SceneBuilder {
  constructor({ maxWindows = 128 } = {}) {
    this.maxWindows = maxWindows;
    this.sceneRevision = 0;
    this._windows = [];
  }

  setWindows(windows) {
    if (!Array.isArray(windows)) throw new Error("windows must be an array");
    const next = windows.slice(0, this.maxWindows).map((w) => {
      validateHost(w);
      return {
        id: w.id,
        rect: { ...w.rect },
        displayId: w.displayId || "primary",
        order: Number(w.order) || 0,
      };
    });
    if (JSON.stringify(next) !== JSON.stringify(this._windows)) {
      this.sceneRevision += 1;
      this._windows = next;
    }
    return this.snapshot();
  }

  snapshot() {
    return {
      sceneRevision: this.sceneRevision,
      windows: structuredClone(this._windows),
      truncated: false,
    };
  }
}

export class LayerCoordinator {
  /**
   * Prefer native ordering when a media source id exists; else visual-mask fallback label.
   */
  planPlacement({ hostMediaSourceId = null, strategy = "relative_order_with_mask_fallback" } = {}) {
    if (hostMediaSourceId) {
      return {
        strategy: "native_move_above",
        mediaSourceId: String(hostMediaSourceId),
        fallback: "visual_mask",
      };
    }
    return {
      strategy,
      mediaSourceId: null,
      fallback: "visual_mask_or_hide",
    };
  }
}

function validateHost(host) {
  if (!host || typeof host.id !== "string" || !host.id) {
    throw new Error("host id required");
  }
  const r = host.rect;
  if (
    !r ||
    ![r.x, r.y, r.width, r.height].every((n) => Number.isFinite(n)) ||
    r.width <= 0 ||
    r.height <= 0
  ) {
    throw new Error("invalid host rect");
  }
}
