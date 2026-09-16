#!/usr/bin/env node
import { readFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const errors = [];

function mustExist(rel) {
  if (!existsSync(join(root, rel))) errors.push(`missing ${rel}`);
}

function readJson(rel) {
  try {
    return JSON.parse(readFileSync(join(root, rel), "utf8"));
  } catch (err) {
    errors.push(`invalid JSON ${rel}: ${err instanceof Error ? err.message : err}`);
    return null;
  }
}

for (const rel of [
  ".cursor/rules/fly-simulation.mdc",
  "config/policy.json",
  "config/desktop-pet.json",
  "config/capabilities.json",
  "config/state-contract.json",
  "config/recovery-profiles.json",
  "provenance/template.json",
  "docs/blueprints/2026-09-16_desktopfly.md",
  "docs/plans/phase_0_foundations_plan.md",
  "docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md",
  "backend/flysim/__init__.py",
  "backend/flysim/ingest.py",
  "backend/flysim/review.py",
  "backend/flysim/clock.py",
  "backend/flysim/world.py",
  "backend/flysim/authored.py",
  "backend/flysim/lif.py",
  "backend/tests/fixtures/synthetic-tables.json",
  "reports/ingestion.json",
  "reports/authored-motion.json",
  "reports/desktop-shell.json",
  "docs/plans/phase_2_authored_motion_plan.md",
  "docs/plans/phase_3_electron_swift_shell_plan.md",
  "docs/plans/phase_4_supervisor_health_plan.md",
  "src/pet/authored-motion.mjs",
  "desktop/main.mjs",
  "desktop/preload.cjs",
  "desktop/pet-window.mjs",
  "desktop/host-lease.mjs",
  "desktop/menus.mjs",
  "desktop/focus.mjs",
  "desktop/policy-gate.mjs",
  "desktop/renderer/pet.html",
  "native/DesktopContext/Package.swift",
  "native/DesktopContext/ipc-protocol.json",
  "native/DesktopContext/Sources/DesktopContext/DesktopContextMain.swift",
  "backend/README.md",
  "src/README.md",
  "desktop/README.md",
  "native/DesktopContext/README.md",
  "data/raw/.gitkeep",
  "data/derived/.gitkeep",
  "data/reviews/.gitkeep",
  "reports/.gitkeep",
]) {
  mustExist(rel);
}

const policy = readJson("config/policy.json");
if (policy) {
  if (policy.real_graph_enabled !== true) {
    errors.push("config/policy.json real_graph_enabled must be true (Cam neural enable override)");
  }
  if (policy.dataset !== "male-cns:v1.0") errors.push("dataset must be male-cns:v1.0");
  if (policy.screen_capture_enabled !== false) errors.push("screen_capture_enabled must be false");
  if (policy.network_bind !== "127.0.0.1") errors.push("network_bind must be 127.0.0.1");
  if (policy.max_neurons_initial !== 2048) errors.push("max_neurons_initial must be 2048");
  if (policy.max_edges_initial !== 100000) errors.push("max_edges_initial must be 100000");
  if (policy.auto_restart_after_hard_fault !== false) {
    errors.push("auto_restart_after_hard_fault must be false");
  }
}

const capabilities = readJson("config/capabilities.json");
if (capabilities && capabilities.neural_output_may_invoke_connectors !== false) {
  errors.push("neural_output_may_invoke_connectors must be false");
}

const pet = readJson("config/desktop-pet.json");
if (pet) {
  if (pet.steal_focus !== false) errors.push("desktop-pet steal_focus must be false");
  if (pet.click_through !== true) errors.push("desktop-pet click_through must be true");
  if (pet.find_fly_available_without_neural_worker !== true) {
    errors.push("Find fly must remain available without a neural worker");
  }
}

const provenance = readJson("provenance/template.json");
if (provenance) {
  if (!/^[0-9a-f]{40}$/.test(provenance.git_sha || "")) {
    errors.push("provenance/template.json git_sha must be a 40-char commit");
  }
  if (provenance.vendored !== false) errors.push("template must not be marked vendored in phase 0");
}

const decision = existsSync(join(root, "docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md"))
  ? readFileSync(join(root, "docs/decisions/2026-09-16-neural-sim-enabled-cam-override.md"), "utf8")
  : "";
if (decision && !decision.includes("real_graph_enabled: true")) {
  errors.push("neural enable decision must record real_graph_enabled: true");
}

const rule = existsSync(join(root, ".cursor/rules/fly-simulation.mdc"))
  ? readFileSync(join(root, ".cursor/rules/fly-simulation.mdc"), "utf8")
  : "";
if (rule && !rule.includes("alwaysApply: true")) {
  errors.push("fly-simulation.mdc must set alwaysApply: true");
}
if (rule && !rule.includes("No neural output may authorize an app action")) {
  errors.push("fly-simulation.mdc is missing the neural-authority prohibition");
}

if (errors.length) {
  for (const error of errors) console.error(error);
  process.exit(1);
}

console.log("foundations check passed");
