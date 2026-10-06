/**
 * Pet BrowserWindow options — frameless, transparent, click-through, no focus steal.
 * Pure factory so Linux unit tests do not need Electron installed.
 */

export function petWindowOptions(preloadPath, overlaySizePoints = 256) {
  if (typeof preloadPath !== "string" || !preloadPath) {
    throw new Error("preloadPath required");
  }
  const size = Number(overlaySizePoints);
  if (!Number.isFinite(size) || size < 64 || size > 512) {
    throw new Error("overlay_size_points out of range");
  }
  return {
    width: size,
    height: size,
    show: false,
    frame: false,
    transparent: true,
    backgroundColor: "#00000000",
    hasShadow: false,
    focusable: false,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    alwaysOnTop: true,
    skipTaskbar: true,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      backgroundThrottling: false,
      devTools: false,
    },
  };
}

/** Apply native click-through and Mission Control hide after construction. */
export function applyPetWindowChrome(pet) {
  if (!pet || typeof pet.setIgnoreMouseEvents !== "function") {
    throw new Error("invalid pet window");
  }
  pet.setIgnoreMouseEvents(true, { forward: true });
  if (typeof pet.setAlwaysOnTop === "function") {
    pet.setAlwaysOnTop(true, "floating");
  }
  if (typeof pet.setVisibleOnAllWorkspaces === "function") {
    pet.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  }
  if (typeof pet.setHiddenInMissionControl === "function") {
    pet.setHiddenInMissionControl(true);
  }
  if (pet.webContents) {
    pet.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
    pet.webContents.on("will-navigate", (event) => event.preventDefault());
  }
  return pet;
}

/** Show without activating the app or stealing keyboard focus. */
export function showPetInactive(pet) {
  if (typeof pet.showInactive === "function") {
    pet.showInactive();
  } else if (typeof pet.show === "function") {
    pet.show();
  }
  if (typeof pet.focus === "function") {
    // Never focus the pet for ordinary follow/show.
  }
}
