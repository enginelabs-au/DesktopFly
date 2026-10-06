/**
 * Capability broker: user-invoked only. Neural output never authorizes actions.
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "../..");

export function loadCapabilitiesConfig() {
  return JSON.parse(readFileSync(join(root, "config/capabilities.json"), "utf8"));
}

export class CapabilityBroker {
  constructor(config = loadCapabilitiesConfig()) {
    if (config.neural_output_may_invoke_connectors !== false) {
      throw new Error("neural_output_may_invoke_connectors must be false");
    }
    this.config = config;
    this.allowlist = new Set((config.allowlist || []).map((x) => x.id || x));
  }

  /**
   * @param {{ connectorId: string, userInvoked: boolean, neuralAuthorized?: boolean }} request
   */
  requestInvoke(request) {
    if (request.neuralAuthorized) {
      return { ok: false, reason: "neural_output_cannot_authorize_connectors" };
    }
    if (!request.userInvoked) {
      return { ok: false, reason: "user_invocation_required" };
    }
    if (this.allowlist.size && !this.allowlist.has(request.connectorId)) {
      return { ok: false, reason: "connector_not_allowlisted" };
    }
    if (!this.allowlist.size) {
      return { ok: false, reason: "no_connectors_enabled" };
    }
    return { ok: true, connectorId: request.connectorId };
  }
}
