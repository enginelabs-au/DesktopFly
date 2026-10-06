import test from "node:test";
import assert from "node:assert/strict";
import {
  AuthoredAnimationController,
  PresentationClock,
  clampCursorYieldSpeed,
  createPetMotionController,
  detectSurfaceContact,
  findFlyPose,
  scaleForDepth,
} from "./authored-motion.mjs";

test("scaleForDepth matches handover visual rule", () => {
  assert.equal(scaleForDepth(0), 1);
  assert.equal(scaleForDepth(1), 0.65);
});

test("cursor yield speed is capped", () => {
  const out = clampCursorYieldSpeed(100, 0, 40);
  assert.equal(out.speed, 40);
  assert.equal(out.vx, 40);
});

test("findFly works without neural worker", () => {
  const pose = findFlyPose({
    hostRect: { x: 100, y: 50, width: 200, height: 400 },
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
  });
  assert.equal(pose.visible, true);
  assert.equal(pose.transitionSource, "operator");
  assert.equal(pose.depth01, 0);
  assert.equal(pose.x, 200);
  assert.equal(pose.surfaceContact, "host-window-surface");
});

test("surface contact is bounded to screen and approved host geometry", () => {
  const bounds = { x: 0, y: 0, width: 1000, height: 800 };
  assert.equal(
    detectSurfaceContact({ pose: { x: 0, y: 400 }, bounds }),
    "screen-edge",
  );
  assert.equal(
    detectSurfaceContact({
      pose: { x: 200, y: 98 },
      bounds,
      hostRect: { x: 100, y: 50, width: 200, height: 400 },
    }),
    "host-window-surface",
  );
  assert.equal(
    detectSurfaceContact({ pose: { x: 500, y: 400 }, bounds }),
    "none",
  );
});

test("LIF presentation wanders in open space", () => {
  let ms = 0;
  const clock = new PresentationClock({ now: () => ms });
  const ctrl = new AuthoredAnimationController({
    clock,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    neuralWander: true,
  });
  const startX = ctrl.pose.x;
  for (let i = 0; i < 60; i += 1) {
    ms += 50;
    ctrl.step();
  }
  assert.ok(Math.abs(ctrl.pose.x - startX) > 8, "expected visible wander on x");
  assert.ok(ctrl.pose.speedPointsS > 0);
  assert.equal(ctrl.pose.locomotion, "flight");
});

test("with nothing to see, the fly holds a straight run instead of a timed wiggle", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    random: () => 0.999,
    connectomeDriver: {
      async step() {
        return { motor: { speed: 0, turn: 0 }, transition_source: "connectome" };
      },
    },
  });
  await motion.step();
  const start = { ...motion.getPose() };
  let end = start;
  for (let i = 0; i < 14; i += 1) {
    ms += 50;
    end = await motion.step();
  }
  assert.ok(Math.hypot(end.x - start.x, end.y - start.y) > 15);
  assert.ok(Math.abs(end.headingRad) < 0.25, `heading drifted to ${end.headingRad}`);
  assert.equal(end.locomotion, "crawl");
});

test("a feature just ahead makes the fly stop and groom", async () => {
  let ms = 0;
  const width = 40;
  const height = 30;
  const samples = new Array(width * height).fill(0.45);
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async step() {
        return { motor: { speed: 0, turn: 0 } };
      },
    },
  });
  await motion.step();
  const start = motion.getPose();
  const px = Math.floor(((start.x + 90) / 1000) * width);
  const py = Math.floor((start.y / 800) * height);
  samples[py * width + px] = 1;
  motion.setRetinaPlane({ width, height, samples, capturedAtS: 0 });
  let end = start;
  for (let i = 0; i < 6; i += 1) {
    ms += 50;
    end = await motion.step();
  }
  assert.equal(end.groom, 1);
  assert.equal(end.speedPointsS, 0);
  assert.equal(end.locomotion, "idle");
});

function steeredController(motorFn) {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 2000, height: 1200 },
    connectomeDriver: {
      async step() {
        return { motor: motorFn(), transition_source: "connectome" };
      },
    },
  });
  return { motion, tick: async () => { ms += 50; return motion.step(); }, start: () => motion.step() };
}

test("batched driver is used when available and applies every block", async () => {
  let ms = 0;
  const requests = [];
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 2000, height: 1200 },
    connectomeDriver: {
      async stepBlocks(_dt, blocks) {
        requests.push(blocks);
        return {
          motors: Array.from({ length: blocks }, () => ({ speed: 80, turn: 0 })),
          transition_source: "connectome",
        };
      },
      async step() {
        throw new Error("per-block path must not be used");
      },
    },
  });
  await motion.step();
  for (let i = 0; i < 6; i += 1) {
    ms += 50;
    await motion.step();
  }
  assert.ok(requests.length >= 1 && requests.length <= 6, "one request per tick");
  assert.ok(requests.every((n) => n === 10), `blocks per tick ${requests}`);
  assert.ok(motion.getPose().speedPointsS > 0);
});

test("a nearby cursor makes the fly leave, whatever the network readout is", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 2000, height: 1200 },
    petConfig: { cursor_yield_radius_points: 220, max_speed_points_s: 160, cruise_speed_points_s: 80 },
    connectomeDriver: {
      async stepBlocks(_dt, blocks) {
        return { motors: Array.from({ length: blocks }, () => ({ speed: 0, turn: 0 })) };
      },
    },
  });
  await motion.step();
  const start = { ...motion.getPose() };
  motion.setCursor({ x: start.x + 40, y: start.y }, { moving: false });
  let end = start;
  for (let i = 0; i < 8; i += 1) {
    ms += 50;
    end = await motion.step();
  }
  const before = 40;
  const after = Math.hypot(end.x - (start.x + 40), end.y - start.y);
  assert.ok(after > before + 40, `distance ${before} -> ${after}`);
  assert.equal(end.locomotion, "flight");
  assert.equal(end.takeoff, 1);
  assert.ok(end.depth01 > 0.4, `depth ${end.depth01}`);
  assert.ok(end.speedPointsS > 200);
});

test("two takeoffs do not last the same time", async () => {
  async function flightSpan(random) {
    let ms = 0;
    const motion = createPetMotionController({
      controllerKind: "lif",
      now: () => ms,
      random,
      petConfig: { cursor_yield_radius_points: 220 },
      bounds: { x: 0, y: 0, width: 2000, height: 1200 },
      connectomeDriver: {
        async step() {
          return { motor: { speed: 0, turn: 0 } };
        },
      },
    });
    await motion.step();
    const start = motion.getPose();
    motion.setCursor({ x: start.x + 40, y: start.y });
    ms += 50;
    const pose = await motion.step();
    assert.equal(pose.bout, "fly");
    return pose.boutS;
  }
  const mid = await flightSpan(() => 0.5);
  const tail = await flightSpan(() => 0.05);
  assert.ok(Math.abs(mid - tail) > 2, `spans ${mid} and ${tail}`);
  assert.ok(mid < 4 && tail > 8);
});

test("the fly turns back before it can leave the screen", async () => {
  const { motion, tick, start } = steeredController(() => ({ speed: 0, turn: 0 }));
  await start();
  let last = null;
  for (let i = 0; i < 80; i += 1) last = await tick();
  const b = { x: 0, y: 0, width: 2000, height: 1200 };
  assert.ok(last.x >= b.x && last.x <= b.x + b.width);
  assert.ok(last.y >= b.y && last.y <= b.y + b.height);
  assert.ok(motion.getPose().speedPointsS >= 0);
});

test("a contrasting spot on the screen is approached", async () => {
  let ms = 0;
  const width = 32;
  const height = 24;
  const samples = new Array(width * height).fill(0.5);
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async step() {
        return { motor: { speed: 0, turn: 0 } };
      },
    },
  });
  await motion.step();
  const start = motion.getPose();
  // Bright spot ahead and to the right of a heading of 0 (+x).
  const spotX = Math.floor(((start.x + 180) / 1000) * width);
  const spotY = Math.floor(((start.y + 140) / 800) * height);
  samples[spotY * width + spotX] = 1;
  motion.setRetinaPlane({ width, height, samples, capturedAtS: 0 });
  let end = start;
  for (let i = 0; i < 20; i += 1) {
    ms += 50;
    end = await motion.step();
  }
  const startBearing = Math.atan2(start.y + 140 - start.y, start.x + 180 - start.x);
  const headingErr = Math.atan2(Math.sin(end.headingRad - startBearing), Math.cos(end.headingRad - startBearing));
  assert.ok(Math.abs(headingErr) < 0.6, `heading ${end.headingRad} vs spot ${startBearing}`);
  assert.ok(end.x !== start.x || end.y !== start.y);
});

function eyes() {
  const c = new AuthoredAnimationController({ bounds: { x: 0, y: 0, width: 2000, height: 1200 } });
  c.pose = { ...c.pose, x: 1000, y: 600, headingRad: 0 };
  return c;
}

test("a still cursor is a bright spot in one eye's retinal grid", () => {
  const none = eyes();
  assert.deepEqual(none.retinaFeatures(), {});
  const right = eyes();
  right.setCursor({ x: 1000, y: 700 });
  const keys = Object.keys(right.retinaFeatures());
  assert.ok(keys.some((key) => key.startsWith("hex_R_")));
  assert.ok(keys.every((key) => key.startsWith("hex_R_")));
  const left = eyes();
  left.setCursor({ x: 1000, y: 500 });
  const leftKeys = Object.keys(left.retinaFeatures());
  assert.ok(leftKeys.some((key) => key.startsWith("hex_L_")));
  assert.ok(leftKeys.every((key) => key.startsWith("hex_L_")));
});

test("the blind zone is empty and head-on lights both eyes", () => {
  const behind = eyes();
  behind.setCursor({ x: 800, y: 600 });
  assert.deepEqual(behind.retinaFeatures(), {});
  const ahead = eyes();
  ahead.setCursor({ x: 1200, y: 600 });
  const keys = Object.keys(ahead.retinaFeatures());
  assert.ok(keys.some((key) => key.startsWith("hex_L_")) && keys.some((key) => key.startsWith("hex_R_")));
});

test("network takeoff does not fly the body; a close cursor does", async () => {
  const { motion, tick, start } = steeredController(() => ({ speed: 0, turn: 0, takeoff: 1 }));
  await start();
  await tick();
  assert.equal(motion.getPose().takeoff, 0);
  const p = motion.getPose();
  motion.setCursor({ x: p.x + 20, y: p.y });
  await tick();
  assert.equal(motion.getPose().takeoff, 1);
  assert.equal(motion.getPose().locomotion, "flight");
});

test("loom signals are sent to the connectome with each tick", async () => {
  let ms = 0;
  const seen = [];
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async stepBlocks(_dt, blocks, features) {
        seen.push(features);
        return { motors: Array.from({ length: blocks }, () => ({ speed: 0, turn: 0 })) };
      },
    },
  });
  await motion.step();
  const p = motion.getPose();
  for (let i = 0; i < 6; i += 1) {
    ms += 50;
    motion.setCursor({ x: p.x, y: p.y + 80 });
    await motion.step({ neuralFeatures: { ambient_drive: 0.9 } });
  }
  const f = seen.at(-1);
  assert.equal(f.ambient_drive, 0.9, "opt-in screen features still pass through");
  assert.ok(Object.keys(f).some((key) => key.startsWith("hex_R_")));
  assert.ok(Object.keys(f).every((key) => key === "ambient_drive" || key.startsWith("hex_")));
});
