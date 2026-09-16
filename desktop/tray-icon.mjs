/**
 * Tray icon path resolution (pure; Electron loads in main).
 */

import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

/** Primary menu-bar icon (22pt logical; use @2x on Retina via Electron). */
export function trayIconPath(desktopDir = __dirname) {
  return join(desktopDir, "assets", "tray-fly.png");
}

export function trayIconPathOrThrow(desktopDir = __dirname) {
  const path = trayIconPath(desktopDir);
  if (!existsSync(path)) {
    throw new Error(`missing tray icon asset: ${path}`);
  }
  return path;
}
