/**
 * Authenticated desktop-host lease. Independent of /health and /workbench visibility.
 * Loss of lease for host_stale_after_s pauses presentation; closing dashboards does not.
 */

export class HostLease {
  constructor({ staleAfterMs = 250, now = () => Date.now() } = {}) {
    if (!Number.isFinite(staleAfterMs) || staleAfterMs <= 0) {
      throw new Error("invalid staleAfterMs");
    }
    this.staleAfterMs = staleAfterMs;
    this.now = now;
    this._lastBeatMs = null;
    this._paused = false;
    this._reason = null;
  }

  /** Main-process heartbeat from the desktop host (not the renderer WebSocket). */
  beat() {
    this._lastBeatMs = this.now();
    if (
      this._paused &&
      (this._reason === "host_lease_stale" ||
        this._reason === "host_lease_missing")
    ) {
      this._paused = false;
      this._reason = null;
    }
  }

  /** Closing health/workbench must not revoke the lease. */
  onDashboardClosed() {
    // no-op by design
  }

  tick() {
    if (this._lastBeatMs == null) {
      this._paused = true;
      this._reason = "host_lease_missing";
      return this.status();
    }
    const age = this.now() - this._lastBeatMs;
    if (age > this.staleAfterMs) {
      this._paused = true;
      this._reason = "host_lease_stale";
    }
    return this.status();
  }

  status() {
    return {
      paused: this._paused,
      reason: this._reason,
      lastBeatMs: this._lastBeatMs,
      staleAfterMs: this.staleAfterMs,
    };
  }
}
