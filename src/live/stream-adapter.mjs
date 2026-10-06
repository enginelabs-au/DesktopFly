/**
 * Validated live stream adapter for pose / health / control frames.
 * Browser-safe ESM; no neural authority.
 */

export const PROTOCOL_VERSION = 1;

export function validateLiveFrame(frame) {
  if (!frame || typeof frame !== "object") throw new Error("frame must be object");
  if (frame.protocolVersion !== PROTOCOL_VERSION) {
    throw new Error("unsupported protocolVersion");
  }
  if (typeof frame.sessionId !== "string" || !frame.sessionId) {
    throw new Error("sessionId required");
  }
  if (typeof frame.runId !== "string" || !frame.runId) {
    throw new Error("runId required");
  }
  if (!Number.isFinite(frame.sequence) || frame.sequence < 0) {
    throw new Error("sequence must be finite >= 0");
  }
  if (!Number.isFinite(frame.simTimeS)) throw new Error("simTimeS must be finite");
  return frame;
}

export class LiveStreamAdapter {
  constructor({ maxQueue = 8 } = {}) {
    this.maxQueue = maxQueue;
    this.queue = [];
    this.latest = null;
    this.lastSequence = -1;
  }

  push(raw) {
    const frame = validateLiveFrame(raw);
    if (frame.sequence <= this.lastSequence) {
      throw new Error("out-of-order or duplicate sequence");
    }
    this.lastSequence = frame.sequence;
    this.latest = frame;
    this.queue.push(frame);
    while (this.queue.length > this.maxQueue) this.queue.shift();
    return frame;
  }

  clear() {
    this.queue = [];
    this.latest = null;
    this.lastSequence = -1;
  }
}
