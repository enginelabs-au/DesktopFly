import test from "node:test";
import assert from "node:assert/strict";
import { LiveStreamAdapter, PROTOCOL_VERSION } from "./stream-adapter.mjs";

test("live adapter accepts monotonic frames", () => {
  const live = new LiveStreamAdapter({ maxQueue: 2 });
  live.push({
    protocolVersion: PROTOCOL_VERSION,
    sessionId: "s",
    runId: "r",
    sequence: 0,
    simTimeS: 0,
  });
  live.push({
    protocolVersion: PROTOCOL_VERSION,
    sessionId: "s",
    runId: "r",
    sequence: 1,
    simTimeS: 0.005,
  });
  assert.equal(live.queue.length, 2);
  assert.throws(() =>
    live.push({
      protocolVersion: PROTOCOL_VERSION,
      sessionId: "s",
      runId: "r",
      sequence: 1,
      simTimeS: 0.01,
    })
  );
});
