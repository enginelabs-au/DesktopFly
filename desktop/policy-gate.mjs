/**
 * Policy gates for the desktop shell. Neural enabled per Cam override (2026-09-16).
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

export function loadPolicy(path = join(root, "config", "policy.json")) {
  return JSON.parse(readFileSync(path, "utf8"));
}

export function loadDesktopPetConfig(path = join(root, "config", "desktop-pet.json")) {
  return JSON.parse(readFileSync(path, "utf8"));
}

export function assertNeuralWorkerMayStart(policy = loadPolicy()) {
  if (policy.real_graph_enabled !== true) {
    throw new Error(
      "LIF/worker cannot start while real_graph_enabled is false (set true in config/policy.json)",
    );
  }
  return true;
}

export function assertDesktopPetDefaults(pet = loadDesktopPetConfig()) {
  if (pet.steal_focus !== false) throw new Error("steal_focus must be false");
  if (pet.click_through !== true) throw new Error("click_through must be true");
  if (pet.find_fly_available_without_neural_worker !== true) {
    throw new Error("Find fly must work without neural worker");
  }
  if (pet.open_workbench_by_default !== false) {
    throw new Error("workbench must not open by default");
  }
  if (pet.screen_capture_enabled !== false) {
    throw new Error("screen_capture_enabled must be false by default");
  }
  return true;
}

export function defaultControllerKind(policy = loadPolicy()) {
  return policy.real_graph_enabled === true ? "lif" : "authored-animation";
}
