#!/usr/bin/env node
import { existsSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createDesktopSession } from "../desktop/main.mjs";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const weightsRel = "data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather";
const weightsPath = join(root, weightsRel);

const session = createDesktopSession();
session.lease.beat();
session.focus.setFocusedHost({
  id: "demo-host",
  rect: { x: 200, y: 100, width: 640, height: 480 },
});
session.actions.findFly();

const report = {
  schema_version: 1,
  phase: 3,
  controller: session.status().controller,
  real_graph_enabled: session.status().real_graph_enabled,
  neural_worker: session.status().neuralWorker,
  host_lease: session.lease.status(),
  find_fly: session.status().pose,
  electron_modules: [
    "desktop/main.mjs",
    "desktop/preload.cjs",
    "desktop/pet-window.mjs",
    "desktop/host-lease.mjs",
    "desktop/menus.mjs",
    "desktop/focus.mjs",
  ],
  swift_scaffold: [
    "native/DesktopContext/Package.swift",
    "native/DesktopContext/Sources/DesktopContext/DesktopContextMain.swift",
  ],
  technical_blockers: {
    male_cns_weights_present: existsSync(weightsPath),
    male_cns_weights_path: weightsRel,
    electron_gui_launch: "optionalDependency; not required for Linux unit tests",
    appkit_compile: "macOS-only; Swift sources scaffolded",
  },
  notes:
    "Cam enabled neural sim. LIF policy flag is true. MaleCNS feather not downloaded — use synthetic graph for CI LIF. Electron GUI not launched on Linux.",
};

writeFileSync(join(root, "reports", "desktop-shell.json"), JSON.stringify(report, null, 2) + "\n");
console.log(join(root, "reports", "desktop-shell.json"));
