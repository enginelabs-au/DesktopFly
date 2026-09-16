import test from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import { createDesktopSession } from "./main.mjs";
import { HostLease } from "./host-lease.mjs";
import { FocusTracker, SceneBuilder } from "./focus.mjs";
import { petWindowOptions, applyPetWindowChrome } from "./pet-window.mjs";
import { overlayBoundsForPose } from "./pet-placement.mjs";
import { trayIconPathOrThrow } from "./tray-icon.mjs";
import { buildApplicationMenuTemplate } from "./menus.mjs";
import {
  assertNeuralWorkerMayStart,
  defaultControllerKind,
  loadPolicy,
} from "./policy-gate.mjs";
import { validatePoseFrame } from "./preload-api.mjs";

test("policy enables neural graph", () => {
  const policy = loadPolicy();
  assert.equal(policy.real_graph_enabled, true);
  assert.equal(defaultControllerKind(policy), "lif");
  assert.equal(assertNeuralWorkerMayStart(policy), true);
});

test("pet window options are click-through and non-focusable", () => {
  const opts = petWindowOptions("/tmp/preload.cjs", 256);
  assert.equal(opts.frame, false);
  assert.equal(opts.transparent, true);
  assert.equal(opts.focusable, false);
  assert.equal(opts.alwaysOnTop, true);
  assert.equal(opts.webPreferences.contextIsolation, true);
  assert.equal(opts.webPreferences.nodeIntegration, false);
  let ignored = null;
  applyPetWindowChrome({
    setIgnoreMouseEvents(v, o) {
      ignored = { v, o };
    },
    setHiddenInMissionControl() {},
    webContents: {
      setWindowOpenHandler() {},
      on() {},
    },
  });
  assert.deepEqual(ignored, { v: true, o: { forward: true } });
});

test("host lease pauses when stale and ignores dashboard close", () => {
  let now = 1000;
  const lease = new HostLease({ staleAfterMs: 250, now: () => now });
  lease.beat();
  assert.equal(lease.tick().paused, false);
  lease.onDashboardClosed();
  now = 1300;
  assert.equal(lease.tick().reason, "host_lease_stale");
});

test("focus epoch increments on host change", () => {
  const focus = new FocusTracker();
  focus.setFocusedHost({
    id: "w1",
    rect: { x: 0, y: 0, width: 100, height: 80 },
  });
  const a = focus.snapshot().focusEpoch;
  focus.setFocusedHost({
    id: "w2",
    rect: { x: 10, y: 10, width: 100, height: 80 },
  });
  assert.equal(focus.snapshot().focusEpoch, a + 1);
});

test("desktop session find fly works and exposes LIF controller", () => {
  const session = createDesktopSession();
  assert.equal(session.status().controller, "lif");
  assert.equal(session.status().real_graph_enabled, true);
  session.focus.setFocusedHost({
    id: "host",
    rect: { x: 100, y: 50, width: 200, height: 400 },
  });
  const pose = session.actions.findFly();
  assert.equal(pose.visible, true);
  assert.equal(pose.transitionSource, "operator");
  const frame = session.poseFrame();
  assert.equal(validatePoseFrame(frame).controller, "lif");
});

test("menu template requires typed actions", () => {
  const session = createDesktopSession();
  const template = buildApplicationMenuTemplate(session.actions);
  assert.ok(template.some((item) => item.label === "View"));
});

test("scene builder caps windows", () => {
  const scene = new SceneBuilder({ maxWindows: 2 });
  scene.setWindows([
    { id: "a", rect: { x: 0, y: 0, width: 1, height: 1 } },
    { id: "b", rect: { x: 0, y: 0, width: 1, height: 1 } },
    { id: "c", rect: { x: 0, y: 0, width: 1, height: 1 } },
  ]);
  assert.equal(scene.snapshot().windows.length, 2);
});

test("overlay bounds center pose on screen", () => {
  const bounds = overlayBoundsForPose(
    { x: 500, y: 300 },
    256,
    { x: 0, y: 0, width: 1440, height: 900 },
  );
  assert.equal(bounds.width, 256);
  assert.equal(bounds.x, 500 - 128);
  assert.equal(bounds.y, 300 - 128);
});

test("desktop session open settings returns route metadata", () => {
  const session = createDesktopSession();
  assert.deepEqual(session.actions.openSettings(), { route: "/settings" });
});

test("tray icon asset exists", () => {
  const desktopDir = dirname(fileURLToPath(import.meta.url));
  const path = trayIconPathOrThrow(desktopDir);
  assert.ok(existsSync(path));
  assert.ok(readFileSync(path).length >= 80);
});
