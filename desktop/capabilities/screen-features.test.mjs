import test from "node:test";
import assert from "node:assert/strict";
import {
  ScreenFeatureCapture,
  extractCoarseScreenFeatures,
  validateCoarseScreenFeatures,
} from "./screen-features.mjs";

function bitmap(width, height, [b, g, r] = [40, 80, 160]) {
  const bytes = Buffer.alloc(width * height * 4);
  for (let i = 0; i < bytes.length; i += 4) {
    bytes[i] = b;
    bytes[i + 1] = g;
    bytes[i + 2] = r;
    bytes[i + 3] = 255;
  }
  return bytes;
}

test("coarse screen features contain bounded numeric values only", () => {
  const features = extractCoarseScreenFeatures({
    bitmap: bitmap(16, 16),
    width: 16,
    height: 16,
    capturedAtS: 10,
  });
  assert.deepEqual(Object.keys(features).sort(), [
    "ambient_drive",
    "brightness",
    "capturedAtS",
    "motion",
    "turn_bias",
  ]);
  assert.ok(features.ambient_drive >= 0 && features.ambient_drive <= 2);
  assert.ok(features.brightness >= 0 && features.brightness <= 1);
  assert.equal(features.motion, 0);
});

test("screen feature validation rejects stale, oversized, and raw fields", () => {
  const valid = {
    capturedAtS: 10,
    ambient_drive: 1,
    turn_bias: 1,
    brightness: 0.5,
    motion: 0,
  };
  assert.throws(
    () => validateCoarseScreenFeatures({ ...valid, ocr: "window title" }, { nowS: 10 }),
    /unsupported fields/,
  );
  assert.throws(
    () => validateCoarseScreenFeatures(valid, { nowS: 11, staleAfterS: 0.5 }),
    /stale/,
  );
  assert.throws(
    () =>
      extractCoarseScreenFeatures({
        bitmap: bitmap(129, 129),
        width: 129,
        height: 129,
        capturedAtS: 10,
      }),
    /exceeds coarse feature bounds/,
  );
});

test("screen capture remains disabled until explicit opt-in", async () => {
  let calls = 0;
  const capture = new ScreenFeatureCapture({
    desktopCapturer: {
      async getSources() {
        calls += 1;
        return [
          {
            thumbnail: {
              getSize: () => ({ width: 16, height: 16 }),
              toBitmap: () => bitmap(16, 16),
            },
          },
        ];
      },
    },
    systemPreferences: {
      getMediaAccessStatus: () => "granted",
    },
    now: () => 10_000,
  });
  assert.equal(await capture.sample(), null);
  assert.equal(calls, 0);
  const status = await capture.enable();
  assert.equal(status.enabled, true);
  assert.equal(status.permission, "granted");
  assert.equal(calls, 1);
  assert.equal(capture.latestIfFresh().motion, 0);
});

test("denied screen permission fails closed to no features", async () => {
  const capture = new ScreenFeatureCapture({
    desktopCapturer: {
      async getSources() {
        throw new Error("must not capture when denied");
      },
    },
    systemPreferences: {
      getMediaAccessStatus: () => "denied",
    },
  });
  const status = await capture.enable();
  assert.equal(status.enabled, false);
  assert.equal(status.permission, "denied");
  assert.equal(status.reason, "screen_recording_permission_denied");
  assert.equal(capture.latestIfFresh(), null);
});
