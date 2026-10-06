/**
 * Capability broker rejects neural authorization.
 */

import test from "node:test";
import assert from "node:assert/strict";
import { CapabilityBroker } from "./broker.mjs";

test("broker blocks neural-authorized invokes", () => {
  const broker = new CapabilityBroker({
    neural_output_may_invoke_connectors: false,
    allowlist: [{ id: "local_summarize" }],
  });
  assert.equal(
    broker.requestInvoke({
      connectorId: "local_summarize",
      userInvoked: true,
      neuralAuthorized: true,
    }).ok,
    false
  );
  assert.equal(
    broker.requestInvoke({
      connectorId: "local_summarize",
      userInvoked: true,
    }).ok,
    true
  );
});
