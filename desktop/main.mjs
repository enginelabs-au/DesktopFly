/**
 * Electron main entry (ESM). Imports electron only when launched as the app.
 * Pure modules remain unit-testable on Linux without Electron.
 */

import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  createPetMotionController,
  scaleForDepth,
} from "../src/pet/authored-motion.mjs";
import { startConnectomeDriver } from "../src/neural/connectome-driver.mjs";
import { ScreenFeatureCapture } from "./capabilities/screen-features.mjs";
import { FocusTracker, LayerCoordinator, SceneBuilder } from "./focus.mjs";
import { HostLease } from "./host-lease.mjs";
import { buildApplicationMenuTemplate, buildTrayMenuTemplate } from "./menus.mjs";
import {
  applyPetWindowChrome,
  petWindowOptions,
  showPetInactive,
} from "./pet-window.mjs";
import { overlayBoundsForPose, normalizeScreenBounds } from "./pet-placement.mjs";
import { createTrayNativeImage, trayIconPathOrThrow } from "./tray-icon.mjs";

/** Strong refs — macOS drops Tray if garbage-collected (handover §3.4c). */
let desktopTray = null;
/** @type {import("electron").BrowserWindow | null} */
let desktopPetWindow = null;
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
  connectomeDriver = null,
  screenFeatures = null,
} = {}) {
  assertDesktopPetDefaults(petConfig);
  const controller = defaultControllerKind(policy);
  let neuralStatus = "unavailable";
  let neuralError = null;
  let motionDriver = controller === "lif" ? "connectome-pending" : "authored-animation";
  let visionSampleInFlight = false;
  let connectomeTechnical = null;
  let latestScreenFeatures = null;
  let visionError = null;
  try {
    assertNeuralWorkerMayStart(policy);
    neuralStatus = connectomeDriver ? "running" : "starting";
  } catch (err) {
    neuralStatus = "unavailable";
    neuralError = err instanceof Error ? err.message : String(err);
    motionDriver = "unavailable";
  }

  const driverRef = { current: connectomeDriver };
  const driverProxy =
    controller === "lif"
      ? {
          step: (dtS, features = {}) => {
            if (!driverRef.current) {
              return Promise.reject(new Error("connectome worker not ready"));
            }
            return driverRef.current.step(dtS, features);
          },
          status: () => driverRef.current?.status?.() ?? connectomeTechnical,
        }
      : null;

  const lease = new HostLease({
    staleAfterMs: Math.round((policy.host_stale_after_s || 0.25) * 1000),
    now,
  });
  const focus = new FocusTracker();
  const scene = new SceneBuilder({ maxWindows: petConfig.max_windows || 128 });
  const layers = new LayerCoordinator();

  let mode = petConfig.default_mode || "follow_my_window";
  let paused = false;
  let presentationBounds = normalizeScreenBounds({
    x: 0,
    y: 0,
    width: 1440,
    height: 900,
  });
  const motion = createPetMotionController({
    petConfig,
    controllerKind: controller,
    bounds: presentationBounds,
    mode: petConfig.default_mode || "follow_my_window",
    now,
    connectomeDriver: driverProxy,
  });
  let pose = motion.getPose();

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
    openSettings() {
      return { route: "/settings" };
    },
    openHelp() {
      return { path: join(root, "docs/handover/operator-runbook.md") };
    },
    exportDiagnostics() {
      connectomeTechnical = motion.getConnectomeTechnical?.() ?? connectomeTechnical;
      return {
        controller,
        neuralStatus,
        neuralError,
        motionDriver,
        connectome: connectomeTechnical,
        real_graph_enabled: policy.real_graph_enabled,
        vision: screenFeatures?.status?.() || {
          enabled: false,
          permission: "unavailable",
          stale: true,
          lastSampleAtS: null,
          reason: "screen_capture_capability_unavailable",
        },
        visionError,
        lease: lease.status(),
      };
    },
    findFly() {
      motion.syncFocusSnapshot(focus.snapshot());
      motion.setBounds(presentationBounds);
      pose = motion.findFly();
      return pose;
    },
    findCursor() {
      return { kind: "locator-ring", durationMs: 2000, clickThrough: true };
    },
    async enableVision() {
      if (!screenFeatures) {
        return { ok: false, reason: "screen_capture_capability_unavailable" };
      }
      try {
        const vision = await screenFeatures.enable();
        latestScreenFeatures = screenFeatures.latestIfFresh?.() || null;
        visionError = null;
        return { ok: true, vision };
      } catch (error) {
        latestScreenFeatures = null;
        visionError = error instanceof Error ? error.message : String(error);
        return { ok: false, reason: "screen_capture_unavailable", error: visionError };
      }
    },
    disableVision() {
      latestScreenFeatures = null;
      visionError = null;
      return screenFeatures?.disable?.() || { enabled: false, reason: "already_disabled" };
    },
    setExploreHide(enabled) {
      mode = enabled ? "explore_and_hide" : "follow_my_window";
      motion.setMode(mode);
      return mode;
    },
    pause() {
      paused = true;
    },
    resume() {
      if (
        controller === "lif" &&
        (neuralStatus === "unavailable" || neuralStatus === "stopped")
      ) {
        throw new Error(neuralError || "cannot resume a stopped LIF session");
      }
      paused = false;
    },
    stop(reason = "operator stop latch") {
      paused = true;
      neuralError = neuralError || String(reason);
      driverRef.current?.shutdown?.();
      neuralStatus = controller === "lif" ? "stopped" : neuralStatus;
    },
    quit() {},
  };

  function status() {
    const leaseStatus = lease.tick();
    connectomeTechnical = motion.getConnectomeTechnical?.() ?? connectomeTechnical;
    if (connectomeTechnical?.faulted) {
      neuralStatus = "stopped";
      neuralError =
        neuralError || connectomeTechnical.faultReason || "connectome worker fault";
      motionDriver = "connectome-stopped";
    }
    return {
      controller,
      mode,
      paused: paused || leaseStatus.paused,
      lease: leaseStatus,
      neuralWorker: neuralStatus,
      neuralError,
      motionDriver,
      connectome: connectomeTechnical,
      real_graph_enabled: policy.real_graph_enabled === true,
      connectome_mode: Boolean(connectomeTechnical?.connectome_mode),
      vision: screenFeatures?.status?.() || {
        enabled: false,
        permission: "unavailable",
        stale: true,
        lastSampleAtS: null,
        reason: "screen_capture_capability_unavailable",
      },
      visionError,
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
        surfaceContact: pose.surfaceContact || "none",
        takeoff: Number.isFinite(Number(pose.takeoff)) ? Number(pose.takeoff) : 0,
        groom: pose.groom ? 1 : 0,
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
      motion.setMode(mode);
      return mode;
    },
    setPresentationBounds(bounds) {
      presentationBounds = normalizeScreenBounds(bounds);
      motion.setBounds(presentationBounds);
      return presentationBounds;
    },
    setCursorPoint(point, options) {
      motion.setCursor(point, options);
    },
    async tickPresentation() {
      const leaseStatus = lease.tick();
      if (paused || leaseStatus.paused) {
        return pose;
      }
      if (screenFeatures?.enabled) {
        const fresh = screenFeatures.latestIfFresh?.() || null;
        if (fresh) {
          latestScreenFeatures = fresh;
          visionError = null;
        }
        if (!visionSampleInFlight && typeof screenFeatures.sample === "function") {
          visionSampleInFlight = true;
          Promise.resolve(screenFeatures.sample())
            .then(() => {
              latestScreenFeatures = screenFeatures.latestIfFresh?.() || latestScreenFeatures;
              visionError = null;
            })
            .catch((error) => {
              visionError = error instanceof Error ? error.message : String(error);
            })
            .finally(() => {
              visionSampleInFlight = false;
            });
        }
      }
      motion.setBounds(presentationBounds);
      motion.setMode(mode);
      motion.setRetinaPlane?.(screenFeatures?.latestLumaIfFresh?.() || null);
      motion.syncFocusSnapshot(focus.snapshot());
      pose = await motion.step({
        neuralFeatures: latestScreenFeatures
          ? {
              ambient_drive: latestScreenFeatures.ambient_drive,
              turn_bias: latestScreenFeatures.turn_bias,
            }
          : {},
        screenFeatures: latestScreenFeatures,
      });
      return pose;
    },
    async attachConnectomeDriver(driver) {
      driverRef.current = driver;
      connectomeTechnical = driver.status?.() ?? null;
      motionDriver = connectomeTechnical?.motion_driver || "connectome-lif";
      neuralStatus = "running";
      neuralError = null;
    },
    async startConnectomeWorker() {
      if (controller !== "lif" || driverRef.current) {
        return status();
      }
      try {
        const driver = await startConnectomeDriver();
        await this.attachConnectomeDriver(driver);
      } catch (err) {
        neuralStatus = "unavailable";
        neuralError = err instanceof Error ? err.message : String(err);
        motionDriver = "connectome-unavailable";
      }
      return status();
    },
    getPresentationBounds() {
      return presentationBounds;
    },
    menuTemplate: () => buildApplicationMenuTemplate(actions),
    trayTemplate: () =>
      buildTrayMenuTemplate(actions, {
        exploreHide: mode === "explore_and_hide",
        canResume: paused,
        visionEnabled: Boolean(screenFeatures?.enabled),
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

  const {
    app,
    BrowserWindow,
    Menu,
    Tray,
    ipcMain,
    nativeImage,
    screen,
    desktopCapturer,
    systemPreferences,
  } = electron;
  const petConfig = loadDesktopPetConfig();
  const screenFeatures = new ScreenFeatureCapture({
    desktopCapturer,
    systemPreferences,
    sampleHz: petConfig.screen_feature_sample_hz,
    staleAfterMs: petConfig.screen_feature_stale_after_ms,
    thumbnailSize: petConfig.screen_feature_thumbnail_size,
  });
  const session = createDesktopSession({ petConfig, screenFeatures });
  await session.startConnectomeWorker();
  const preloadPath = join(__dirname, "preload.cjs");
  const overlaySize = session.petConfig.overlay_size_points || 256;
  /** @type {import('electron').BrowserWindow | null} */
  let healthWin = null;
  /** @type {import('electron').BrowserWindow | null} */
  let settingsWin = null;
  let lastCursorPoint = null;
  let cursorPollTimer = null;
  let glideTimer = null;

  function glidePetWindow() {
    const petWin = desktopPetWindow;
    const p = glide.pose;
    if (!petWin || petWin.isDestroyed() || !p || !(p.speedPointsS > 0.5)) return;
    if (session.status().paused) return;
    const dtS = Math.min(0.08, (Date.now() - glide.atMs) / 1000);
    petWin.setBounds(
      overlayBoundsForPose(
        {
          x: p.x + Math.cos(p.headingRad) * p.speedPointsS * dtS,
          y: p.y + Math.sin(p.headingRad) * p.speedPointsS * dtS,
        },
        overlaySize,
        session.getPresentationBounds(),
      ),
    );
  }

  function pollCursorPoint() {
    try {
      const point = screen.getCursorScreenPoint();
      const moving =
        lastCursorPoint == null ||
        Math.hypot(point.x - lastCursorPoint.x, point.y - lastCursorPoint.y) >= 1;
      session.setCursorPoint(point, { moving });
      lastCursorPoint = point;
    } catch {
      session.setCursorPoint(null, { moving: false });
    }
  }

  function refreshPresentationBounds() {
    const displays = screen.getAllDisplays();
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    for (const display of displays) {
      const b = display.bounds;
      minX = Math.min(minX, b.x);
      minY = Math.min(minY, b.y);
      maxX = Math.max(maxX, b.x + b.width);
      maxY = Math.max(maxY, b.y + b.height);
    }
    const bounds =
      Number.isFinite(minX) && maxX > minX
        ? { x: minX, y: minY, width: maxX - minX, height: maxY - minY }
        : screen.getPrimaryDisplay().bounds;
    session.setPresentationBounds(bounds);
    return bounds;
  }

  // Latest committed pose; the glide timer extrapolates it between 20 Hz ticks
  // so the window moves smoothly. Cosmetic only: it never feeds back into state.
  const glide = { pose: null, atMs: 0 };

  function syncPetWindow(petWin) {
    if (!petWin || petWin.isDestroyed()) return null;
    const current = session.status().pose;
    glide.pose = { ...current };
    glide.atMs = Date.now();
    const bounds = overlayBoundsForPose(
      current,
      overlaySize,
      session.getPresentationBounds(),
    );
    petWin.setBounds(bounds);
    showPetInactive(petWin);
    petWin.webContents.send(IPC.POSE_FRAME, session.poseFrame());
    return bounds;
  }

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

  function openSettingsWindow() {
    const meta = session.actions.openSettings();
    if (settingsWin && !settingsWin.isDestroyed()) {
      settingsWin.focus();
      return meta;
    }
    settingsWin = new BrowserWindow(dashboardWindowOptions("DesktopFly Settings"));
    settingsWin.on("closed", () => {
      settingsWin = null;
    });
    const snapshot = JSON.stringify(
      {
        mode: session.status().mode,
        paused: session.status().paused,
        petConfig: session.petConfig,
      },
      null,
      2,
    );
    settingsWin
      .loadFile(join(__dirname, "renderer", "settings.html"))
      .then(() =>
        settingsWin.webContents.executeJavaScript(
          `document.getElementById("cfg").textContent = ${JSON.stringify(snapshot)};`,
        ),
      )
      .catch((err) => {
        console.error("settings window failed to load", err);
      });
    return meta;
  }

  function findFlyAndShow(petWin) {
    session.actions.findFly();
    return syncPetWindow(petWin);
  }

  function refreshTrayMenu() {
    if (!desktopTray) return;
    const current = session.status();
    desktopTray.setContextMenu(
      Menu.buildFromTemplate(
        buildTrayMenuTemplate(guiActions, {
          exploreHide: current.mode === "explore_and_hide",
          canResume: current.paused,
          visionEnabled: Boolean(current.vision?.enabled),
        }),
      ),
    );
  }

  const guiActions = {
    ...session.actions,
    openHealth: openHealthWindow,
    openSettings: openSettingsWindow,
    findFly() {
      return findFlyAndShow(win);
    },
    async enableVision() {
      const result = await session.actions.enableVision();
      refreshTrayMenu();
      return result;
    },
    disableVision() {
      const result = session.actions.disableVision();
      refreshTrayMenu();
      return result;
    },
    quit() {
      app.quit();
    },
  };

  await app.whenReady();
  if (process.platform === "darwin" && typeof app.dock?.show === "function") {
    app.dock.show();
  }
  refreshPresentationBounds();
  pollCursorPoint();
  cursorPollTimer = setInterval(pollCursorPoint, 50);
  glideTimer = setInterval(glidePetWindow, 16);
  screen.on("display-metrics-changed", () => {
    refreshPresentationBounds();
    if (desktopPetWindow && !desktopPetWindow.isDestroyed()) {
      syncPetWindow(desktopPetWindow);
    }
  });

  const win = new BrowserWindow(petWindowOptions(preloadPath, overlaySize));
  desktopPetWindow = win;
  applyPetWindowChrome(win);
  await win.loadFile(join(__dirname, "renderer", "pet.html"));

  Menu.setApplicationMenu(
    Menu.buildFromTemplate(buildApplicationMenuTemplate(guiActions)),
  );
  const trayImage = createTrayNativeImage(nativeImage, __dirname);
  desktopTray = new Tray(trayImage);
  desktopTray.setToolTip("Fly");
  desktopTray.setContextMenu(
    Menu.buildFromTemplate(
      buildTrayMenuTemplate(guiActions, {
        exploreHide: session.status().mode === "explore_and_hide",
        canResume: session.status().paused,
        visionEnabled: Boolean(session.status().vision?.enabled),
      }),
    ),
  );

  ipcMain.handle(IPC.GET_STATUS, () => session.status());
  ipcMain.handle(IPC.FIND_FLY, () => {
    session.actions.findFly();
    syncPetWindow(win);
    return session.status().pose;
  });
  ipcMain.handle(IPC.FIND_CURSOR, () => session.actions.findCursor());
  ipcMain.handle(IPC.SET_MODE, (_e, mode) => session.setMode(mode));
  ipcMain.handle(IPC.OPEN_HEALTH, () => openHealthWindow());
  ipcMain.handle(IPC.OPEN_WORKBENCH, () => session.actions.openWorkbench());
  ipcMain.handle(IPC.ENABLE_VISION, () => session.actions.enableVision());
  ipcMain.handle(IPC.DISABLE_VISION, () => session.actions.disableVision());
  ipcMain.on(IPC.HOST_LEASE_BEAT, () => session.lease.beat());

  win.once("ready-to-show", () => {
    findFlyAndShow(win);
  });
  if (win.isVisible() || win.webContents.isLoading() === false) {
    findFlyAndShow(win);
  }

  const tickMs = Math.max(
    16,
    Math.round(1000 / (session.petConfig.geometry_poll_hz || 20)),
  );
  let tickInFlight = false;
  let tickStartedAt = 0;
  let stopLogged = false;
  // A stop is permanent by design; say why, once, so it is never silent.
  function logStopOnce() {
    if (stopLogged) return;
    const current = session.status();
    if (current.neuralWorker !== "stopped") return;
    stopLogged = true;
    console.error(
      `DesktopFly neural worker stopped permanently: ${current.neuralError || "unknown reason"}`,
      current.connectome?.timing ? JSON.stringify(current.connectome.timing) : "",
    );
  }
  const timer = setInterval(() => {
    session.lease.beat();
    if (tickInFlight) {
      const timeoutMs = Math.max(
        1,
        Math.round((session.policy.heartbeat_timeout_s || 0.25) * 1000),
      );
      if (Date.now() - tickStartedAt > timeoutMs) {
        session.actions.stop(
          `presentation tick took longer than ${timeoutMs} ms (heartbeat limit)`,
        );
        logStopOnce();
      }
      return;
    }
    tickInFlight = true;
    tickStartedAt = Date.now();
    void session.tickPresentation().then(() => {
      if (!win.isDestroyed()) {
        syncPetWindow(win);
      }
    }).catch((err) => {
      session.actions.stop(
        `neural loop error: ${err instanceof Error ? err.message : String(err)}`,
      );
      logStopOnce();
    }).finally(() => {
      tickInFlight = false;
      logStopOnce();
    });
  }, tickMs);

  app.on("before-quit", () => {
    clearInterval(timer);
    clearInterval(cursorPollTimer);
    clearInterval(glideTimer);
  });

  app.on("activate", () => {
    if (win && !win.isDestroyed()) {
      findFlyAndShow(win);
    }
  });

  if (autoQuitMs > 0) {
    setTimeout(() => {
      try {
        openHealthWindow();
        findFlyAndShow(win);
      } finally {
        setTimeout(() => app.quit(), 750);
      }
    }, Math.min(autoQuitMs, 2500));
  }

  return {
    app,
    win,
    tray: desktopTray,
    session,
    root,
    openHealthWindow,
    openSettingsWindow,
  };
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
  const petConfig = loadDesktopPetConfig();
  const openHealthOnStart =
    process.env.DESKTOPFLY_OPEN_HEALTH === "1" ||
    (process.env.DESKTOPFLY_OPEN_HEALTH === undefined &&
      petConfig.open_health_by_default === true);
  launchElectronApp({ autoQuitMs })
    .then(async ({ openHealthWindow, session }) => {
      if (openHealthOnStart) openHealthWindow();
      // Owner asked the pet to use the screen. Fails closed if permission is denied.
      await session.actions.enableVision().catch(() => {});
      console.error(
        "DesktopFly pet running — menu-bar Fly icon; tray/menu Find fly recenters the pet",
      );
    })
    .catch((err) => {
      console.error(err);
      process.exit(1);
    });
}
