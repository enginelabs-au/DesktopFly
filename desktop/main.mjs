/**
 * Electron main entry (ESM). Imports electron only when launched as the app.
 * Pure modules remain unit-testable on Linux without Electron.
 */

import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { findFlyPose, scaleForDepth } from "../src/pet/authored-motion.mjs";
import { FocusTracker, LayerCoordinator, SceneBuilder } from "./focus.mjs";
import { HostLease } from "./host-lease.mjs";
import { buildApplicationMenuTemplate, buildTrayMenuTemplate } from "./menus.mjs";
import {
  applyPetWindowChrome,
  petWindowOptions,
  showPetInactive,
} from "./pet-window.mjs";
import {
  assertDesktopPetDefaults,
  assertNeuralWorkerMayStart,
  defaultControllerKind,
  loadDesktopPetConfig,
  loadPolicy,
} from "./policy-gate.mjs";
import { IPC, validateMode, validatePoseFrame } from "./preload-api.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const root = join(__dirname, "..");

export function createDesktopSession({
  policy = loadPolicy(),
  petConfig = loadDesktopPetConfig(),
  now = () => Date.now(),
} = {}) {
  assertDesktopPetDefaults(petConfig);
  const controller = defaultControllerKind(policy);
  let neuralStatus = "unavailable";
  let neuralError = null;
  try {
    assertNeuralWorkerMayStart(policy);
    neuralStatus = "running";
  } catch (err) {
    neuralStatus = "unavailable";
    neuralError = err instanceof Error ? err.message : String(err);
  }

  const lease = new HostLease({
    staleAfterMs: Math.round((policy.host_stale_after_s || 0.25) * 1000),
    now,
  });
  const focus = new FocusTracker();
  const scene = new SceneBuilder({ maxWindows: petConfig.max_windows || 128 });
  const layers = new LayerCoordinator();

  let mode = petConfig.default_mode || "follow_my_window";
  let paused = false;
  let pose = findFlyPose({
    hostRect: null,
    bounds: { x: 0, y: 0, width: 1440, height: 900 },
  });

  const actions = {
    openHealth() {
      return {
        route: "/health",
        path: join(root, "src/telemetry/health.html"),
      };
    },
    openWorkbench() {
      return {
        route: "/workbench",
        path: join(root, "src/workbench/workbench.mjs"),
      };
    },
    openSettings() {},
    openHelp() {
      return { path: join(root, "docs/handover/operator-runbook.md") };
    },
    exportDiagnostics() {
      return {
        controller,
        neuralStatus,
        neuralError,
        real_graph_enabled: policy.real_graph_enabled,
        lease: lease.status(),
      };
    },
    findFly() {
      const snap = focus.snapshot();
      const host = snap.host;
      pose = findFlyPose({
        hostRect: host
          ? {
              x: host.rect.x,
              y: host.rect.y,
              width: host.rect.width,
              height: host.rect.height,
            }
          : null,
        bounds: { x: 0, y: 0, width: 1440, height: 900 },
        headingRad: pose.headingRad,
      });
      return pose;
    },
    findCursor() {
      return { kind: "locator-ring", durationMs: 2000, clickThrough: true };
    },
    setExploreHide(enabled) {
      mode = enabled ? "explore_and_hide" : "follow_my_window";
      return mode;
    },
    pause() {
      paused = true;
    },
    resume() {
      if (neuralStatus === "unavailable" && controller === "lif") {
        throw new Error(neuralError || "cannot resume without LIF");
      }
      paused = false;
    },
    stop() {
      paused = true;
      neuralStatus = neuralStatus === "running" ? "stopped" : neuralStatus;
    },
    quit() {},
  };

  function status() {
    const leaseStatus = lease.tick();
    return {
      controller,
      mode,
      paused: paused || leaseStatus.paused,
      lease: leaseStatus,
      neuralWorker: neuralStatus,
      neuralError,
      real_graph_enabled: policy.real_graph_enabled === true,
      focus: focus.snapshot(),
      scene: scene.snapshot(),
      layer: layers.planPlacement({}),
      pose,
      scale: scaleForDepth(pose.depth01),
    };
  }

  function poseFrame() {
    const frame = {
      version: 1,
      type: "pose",
      controller,
      neuralWorker: neuralStatus,
      pose: {
        x: pose.x,
        y: pose.y,
        headingRad: pose.headingRad,
        speedPointsS: pose.speedPointsS,
        depth01: pose.depth01,
        locomotion: pose.locomotion,
      },
    };
    return validatePoseFrame(frame);
  }

  return {
    policy,
    petConfig,
    actions,
    lease,
    focus,
    scene,
    layers,
    status,
    poseFrame,
    setMode(next) {
      mode = validateMode(next);
      return mode;
    },
    menuTemplate: () => buildApplicationMenuTemplate(actions),
    trayTemplate: () =>
      buildTrayMenuTemplate(actions, {
        exploreHide: mode === "explore_and_hide",
        canResume: paused,
      }),
  };
}

function dashboardWindowOptions(title) {
  return {
    width: 720,
    height: 640,
    show: true,
    title,
    frame: true,
    transparent: false,
    focusable: true,
    resizable: true,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      // Health/workbench are ordinary documents; pet preload is not attached.
      backgroundThrottling: true,
      devTools: false,
    },
  };
}

export async function launchElectronApp({ autoQuitMs = 0 } = {}) {
  const require = createRequire(import.meta.url);
  let electron;
  try {
    electron = require("electron");
  } catch (err) {
    throw new Error(
      `Electron not installed (technical blocker for GUI launch): ${
        err instanceof Error ? err.message : err
      }. Unit-tested shell modules are still available.`,
    );
  }

  const { app, BrowserWindow, Menu, Tray, ipcMain, nativeImage } = electron;
  const session = createDesktopSession();
  const preloadPath = join(__dirname, "preload.cjs");
  /** @type {import('electron').BrowserWindow | null} */
  let healthWin = null;

  function openHealthWindow() {
    const meta = session.actions.openHealth();
    if (healthWin && !healthWin.isDestroyed()) {
      healthWin.focus();
      return meta;
    }
    healthWin = new BrowserWindow(dashboardWindowOptions("DesktopFly Health"));
    healthWin.on("closed", () => {
      healthWin = null;
      // Closing Health must not revoke the host lease (handover §3.3).
      session.lease.onDashboardClosed?.();
    });
    healthWin.loadFile(meta.path);
    return meta;
  }

  const guiActions = {
    ...session.actions,
    openHealth: openHealthWindow,
    quit() {
      app.quit();
    },
  };

  await app.whenReady();
  const win = new BrowserWindow(
    petWindowOptions(preloadPath, session.petConfig.overlay_size_points || 256),
  );
  applyPetWindowChrome(win);
  await win.loadFile(join(__dirname, "renderer", "pet.html"));
  showPetInactive(win);

  Menu.setApplicationMenu(
    Menu.buildFromTemplate(buildApplicationMenuTemplate(guiActions)),
  );
  const icon = nativeImage.createEmpty();
  const tray = new Tray(icon);
  tray.setToolTip("Fly");
  tray.setContextMenu(
    Menu.buildFromTemplate(
      buildTrayMenuTemplate(guiActions, {
        exploreHide: session.status().mode === "explore_and_hide",
        canResume: session.status().paused,
      }),
    ),
  );

  ipcMain.handle(IPC.GET_STATUS, () => session.status());
  ipcMain.handle(IPC.FIND_FLY, () => session.actions.findFly());
  ipcMain.handle(IPC.FIND_CURSOR, () => session.actions.findCursor());
  ipcMain.handle(IPC.SET_MODE, (_e, mode) => session.setMode(mode));
  ipcMain.handle(IPC.OPEN_HEALTH, () => openHealthWindow());
  ipcMain.handle(IPC.OPEN_WORKBENCH, () => session.actions.openWorkbench());
  ipcMain.on(IPC.HOST_LEASE_BEAT, () => session.lease.beat());

  const timer = setInterval(() => {
    session.lease.beat();
    if (!win.isDestroyed()) {
      win.webContents.send(IPC.POSE_FRAME, session.poseFrame());
    }
  }, 50);

  app.on("before-quit", () => clearInterval(timer));

  if (autoQuitMs > 0) {
    setTimeout(() => {
      try {
        openHealthWindow();
        session.actions.findFly();
      } finally {
        setTimeout(() => app.quit(), 750);
      }
    }, Math.min(autoQuitMs, 2500));
  }

  return { app, win, tray, session, root, openHealthWindow };
}

// Electron loads package.json "main" with argv[1] === "." — do not require argv path match.
// Node unit tests import this module without process.versions.electron.
const isElectronMain =
  Boolean(process.versions?.electron) && process.type === "browser";
const isNodeDirect =
  !process.versions?.electron &&
  process.argv[1] &&
  fileURLToPath(import.meta.url) === process.argv[1];
if (isElectronMain || isNodeDirect) {
  const autoQuitMs = Number(process.env.DESKTOPFLY_AUTO_QUIT_MS || 0);
  const openHealthOnStart = process.env.DESKTOPFLY_OPEN_HEALTH !== "0";
  launchElectronApp({ autoQuitMs })
    .then(({ openHealthWindow, session }) => {
      session.actions.findFly();
      if (openHealthOnStart) openHealthWindow();
      console.error(
        "DesktopFly pet running — tray tooltip Fly; menu View → Health… / Find fly",
      );
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
