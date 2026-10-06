/**
 * Opt-in local screen sensing.
 *
 * Raw thumbnails exist only during `sample()` in the Electron main process.
 * The returned object is a small numeric feature vector; pixels, text, and
 * window content never cross the neural-worker boundary.
 */

const FEATURE_KEYS = Object.freeze([
  "capturedAtS",
  "ambient_drive",
  "turn_bias",
  "brightness",
  "motion",
]);

const PERMISSIONS = new Set([
  "not-determined",
  "granted",
  "denied",
  "restricted",
  "unknown",
]);

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function finite(value, name) {
  if (!Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
}

export function validateCoarseScreenFeatures(features, {
  nowS = Date.now() / 1000,
  staleAfterS = 0.5,
} = {}) {
  if (!features || typeof features !== "object" || Array.isArray(features)) {
    throw new Error("screen features must be an object");
  }
  const keys = Object.keys(features).sort();
  const expected = [...FEATURE_KEYS].sort();
  if (keys.length !== expected.length || keys.some((key, i) => key !== expected[i])) {
    throw new Error("screen features contain unsupported fields");
  }
  const capturedAtS = finite(Number(features.capturedAtS), "capturedAtS");
  const ageS = nowS - capturedAtS;
  if (!Number.isFinite(ageS) || ageS < -0.05 || ageS > staleAfterS) {
    throw new Error("screen features are stale or from the future");
  }
  const normalized = {
    capturedAtS,
    ambient_drive: clamp(finite(Number(features.ambient_drive), "ambient_drive"), 0, 2),
    turn_bias: clamp(finite(Number(features.turn_bias), "turn_bias"), 0, 2),
    brightness: clamp(finite(Number(features.brightness), "brightness"), 0, 1),
    motion: clamp(finite(Number(features.motion), "motion"), 0, 1),
  };
  return Object.freeze(normalized);
}

export function extractCoarseScreenFeatures({
  bitmap,
  width,
  height,
  capturedAtS = Date.now() / 1000,
  previousBrightness = null,
}) {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1) {
    throw new Error("screen dimensions must be positive integers");
  }
  if (width > 128 || height > 128 || width * height > 16384) {
    throw new Error("screen thumbnail exceeds coarse feature bounds");
  }
  if (!bitmap || typeof bitmap.length !== "number" || bitmap.length !== width * height * 4) {
    throw new Error("screen bitmap shape is invalid");
  }

  let brightnessTotal = 0;
  let redTotal = 0;
  let blueTotal = 0;
  let samples = 0;
  // Electron NativeImage.toBitmap() is BGRA on macOS.
  for (let offset = 0; offset < bitmap.length; offset += 16) {
    const blue = bitmap[offset] / 255;
    const green = bitmap[offset + 1] / 255;
    const red = bitmap[offset + 2] / 255;
    const luma = 0.114 * blue + 0.587 * green + 0.299 * red;
    brightnessTotal += luma;
    redTotal += red;
    blueTotal += blue;
    samples += 1;
  }
  if (samples === 0) throw new Error("screen thumbnail has no samples");

  const brightness = brightnessTotal / samples;
  const colorBias = clamp(1 + (redTotal - blueTotal) / samples, 0, 2);
  const motion =
    previousBrightness == null
      ? 0
      : clamp(Math.abs(brightness - Number(previousBrightness)) * 4, 0, 1);
  return validateCoarseScreenFeatures({
    capturedAtS,
    ambient_drive: clamp(0.35 + brightness * 1.65, 0, 2),
    turn_bias: colorBias,
    brightness,
    motion,
  }, { nowS: capturedAtS });
}

export class ScreenFeatureCapture {
  constructor({
    desktopCapturer,
    systemPreferences,
    enabledByUser = false,
    sampleHz = 5,
    staleAfterMs = 500,
    thumbnailSize = 64,
    now = () => Date.now(),
  } = {}) {
    if (!desktopCapturer || typeof desktopCapturer.getSources !== "function") {
      throw new Error("desktopCapturer capability is required");
    }
    if (!systemPreferences || typeof systemPreferences.getMediaAccessStatus !== "function") {
      throw new Error("systemPreferences capability is required");
    }
    if (!Number.isFinite(sampleHz) || sampleHz <= 0 || sampleHz > 10) {
      throw new Error("sampleHz must be between 0 and 10");
    }
    if (!Number.isFinite(staleAfterMs) || staleAfterMs <= 0 || staleAfterMs > 2000) {
      throw new Error("staleAfterMs must be between 0 and 2000");
    }
    if (!Number.isInteger(thumbnailSize) || thumbnailSize < 16 || thumbnailSize > 128) {
      throw new Error("thumbnailSize must be between 16 and 128");
    }
    this.desktopCapturer = desktopCapturer;
    this.systemPreferences = systemPreferences;
    this.sampleIntervalMs = 1000 / sampleHz;
    this.staleAfterMs = staleAfterMs;
    this.thumbnailSize = thumbnailSize;
    this.now = now;
    this.enabled = Boolean(enabledByUser);
    this.permission = "not-determined";
    this.lastSampleAtMs = 0;
    this.lastBrightness = null;
    this.latest = null;
    this.reason = this.enabled ? "user_opt_in_pending" : "disabled_by_default";
  }

  status() {
    const ageMs = this.latest ? this.now() - this.latest.capturedAtS * 1000 : null;
    return {
      enabled: this.enabled,
      permission: this.permission,
      stale: ageMs == null || ageMs > this.staleAfterMs,
      lastSampleAtS: this.latest?.capturedAtS ?? null,
      reason: this.reason,
    };
  }

  async enable() {
    this.enabled = true;
    this.reason = "user_opt_in_pending";
    this.permission = String(this.systemPreferences.getMediaAccessStatus("screen"));
    if (!PERMISSIONS.has(this.permission)) this.permission = "unknown";
    if (this.permission === "denied" || this.permission === "restricted") {
      this.reason = "screen_recording_permission_denied";
      this.enabled = false;
      return this.status();
    }
    try {
      await this.sample({ force: true });
    } catch (error) {
      this.reason = "screen_capture_unavailable";
      this.enabled = false;
      throw error;
    }
    this.reason = "active_coarse_features";
    return this.status();
  }

  disable() {
    this.enabled = false;
    this.latest = null;
    this.lastBrightness = null;
    this.reason = "disabled_by_user";
    return this.status();
  }

  async sample({ force = false } = {}) {
    if (!this.enabled) return null;
    const nowMs = this.now();
    if (!force && nowMs - this.lastSampleAtMs < this.sampleIntervalMs) {
      return this.latest;
    }
    this.lastSampleAtMs = nowMs;
    this.permission = String(this.systemPreferences.getMediaAccessStatus("screen"));
    if (this.permission === "denied" || this.permission === "restricted") {
      this.latest = null;
      this.reason = "screen_recording_permission_denied";
      return null;
    }
    const sources = await this.desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: { width: this.thumbnailSize, height: this.thumbnailSize },
      fetchWindowIcons: false,
    });
    const source = sources?.[0];
    const image = source?.thumbnail;
    if (!image || typeof image.getSize !== "function" || typeof image.toBitmap !== "function") {
      this.latest = null;
      this.reason = "no_screen_source";
      return null;
    }
    const size = image.getSize();
    const features = extractCoarseScreenFeatures({
      bitmap: image.toBitmap(),
      width: size.width,
      height: size.height,
      capturedAtS: nowMs / 1000,
      previousBrightness: this.lastBrightness,
    });
    this.lastBrightness = features.brightness;
    this.latest = features;
    this.permission = "granted";
    this.reason = "active_coarse_features";
    return features;
  }

  latestIfFresh() {
    if (!this.latest) return null;
    try {
      return validateCoarseScreenFeatures(this.latest, {
        nowS: this.now() / 1000,
        staleAfterS: this.staleAfterMs / 1000,
      });
    } catch {
      return null;
    }
  }
}
