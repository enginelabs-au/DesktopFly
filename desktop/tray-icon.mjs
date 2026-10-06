/**
 * Tray icon path resolution (pure; Electron loads in main).
 */

import { existsSync, readFileSync } from "node:fs";
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

/** @param {typeof import("electron").nativeImage} nativeImage */
function loadTrayImage(nativeImage, absolutePath) {
  let image = nativeImage.createFromPath(absolutePath);
  if (image.isEmpty()) {
    image = nativeImage.createFromBuffer(readFileSync(absolutePath));
  }
  return image;
}

/** @param {typeof import("electron").nativeImage} nativeImage */
export function createTrayNativeImage(nativeImage, desktopDir = __dirname) {
  const path = trayIconPathOrThrow(desktopDir);
  const retinaPath = join(desktopDir, "assets", "tray-fly@2x.png");
  let loadPath =
    process.platform === "darwin" && existsSync(retinaPath) ? retinaPath : path;
  let image = loadTrayImage(nativeImage, loadPath);
  if (image.isEmpty() && loadPath !== path) {
    loadPath = path;
    image = loadTrayImage(nativeImage, loadPath);
  }
  if (image.isEmpty()) {
    throw new Error(`tray icon failed to load: ${loadPath}`);
  }
  if (process.platform === "darwin") {
    const { width, height } = image.getSize();
    if (width !== 18 || height !== 18) {
      image = image.resize({ width: 18, height: 18, quality: "best" });
    }
    if (image.isEmpty()) {
      throw new Error(`tray icon empty after resize: ${loadPath}`);
    }
    image.setTemplateImage(true);
  }
  return image;
}
