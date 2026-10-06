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

test("connectome turn readout produces a curved 2D track, not a rail", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async step() {
        return { motor: { dx: 0, dy: 0, speed: 60, turn: 0.8 }, transition_source: "connectome" };
      },
    },
  });
  await motion.step();
  const xs = [];
  const ys = [];
  for (let i = 0; i < 40; i += 1) {
    ms += 50;
    const p = await motion.step();
    xs.push(p.x);
    ys.push(p.y);
  }
  const yRange = Math.max(...ys) - Math.min(...ys);
  assert.ok(yRange > 20, `expected vertical travel, got ${yRange}`);
  assert.ok(Math.max(...xs) - Math.min(...xs) > 20);
  assert.equal(motion.getPose().transitionSource, "connectome");
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

test("connectome speed and turn pass straight through; only the speed ceiling applies", async () => {
  let forward = 30;
  const { motion, tick, start } = steeredController(() => ({ speed: forward, turn: 0 }));
  await start();
  await tick();
  // No walk onset, inertia, or pause rule: a slow readout is a slow walk, immediately.
  assert.equal(motion.getPose().speedPointsS, 30);
  assert.equal(motion.getPose().locomotion, "crawl");
  forward = 0;
  await tick();
  assert.equal(motion.getPose().speedPointsS, 0);
  assert.equal(motion.getPose().locomotion, "idle");
  forward = 5000;
  await tick();
  assert.equal(motion.getPose().speedPointsS, 160, "speed ceiling still applies");
  assert.equal(motion.getPose().transitionSource, "connectome");
});

test("the screen clamp is the only edge rule: no code steers the fly away from an edge", async () => {
  const { motion, tick, start } = steeredController(() => ({ speed: 120, turn: 0 }));
  await start();
  let last = null;
  for (let i = 0; i < 400; i += 1) last = await tick();
  const b = { x: 0, y: 0, width: 2000, height: 1200 };
  assert.ok(last.x <= b.x + b.width && last.y >= b.y && last.y <= b.y + b.height);
  assert.ok(last.x > b.x + b.width - 5, "pinned at the edge; nothing turned it around");
  assert.equal(last.headingRad, 0);
});

test("the cursor never moves the fly by itself; only the network readout does", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async stepBlocks(_dt, blocks) {
        return { motors: Array.from({ length: blocks }, () => ({ speed: 0, turn: 0 })) };
      },
    },
  });
  await motion.step();
  const start = { ...motion.getPose() };
  motion.setCursor({ x: start.x + 5, y: start.y + 5 }, { moving: true });
  for (let i = 0; i < 20; i += 1) {
    ms += 50;
    await motion.step();
  }
  const end = motion.getPose();
  assert.equal(end.x, start.x);
  assert.equal(end.y, start.y);
  assert.equal(end.transitionSource, "connectome");
});

function eyes() {
  const c = new AuthoredAnimationController({ bounds: { x: 0, y: 0, width: 2000, height: 1200 } });
  c.pose = { ...c.pose, x: 1000, y: 600, headingRad: 0 };
  return c;
}

test("a cursor that is not getting bigger produces no looming signal", () => {
  const c = eyes();
  c.setCursor({ x: 1000, y: 700 });
  for (let i = 0; i < 10; i += 1) {
    const f = c.loomFeatures(0.05);
    assert.deepEqual(f, { loom_left: 0, loom_right: 0 });
  }
  const none = eyes();
  assert.deepEqual(none.loomFeatures(0.05), { loom_left: 0, loom_right: 0 });
});

test("an approaching cursor loomed on the side it comes from, receding gives none", () => {
  // Heading east: south is the fly's right, north its left.
  for (const [side, y] of [["loom_right", 1] , ["loom_left", -1]]) {
    const c = eyes();
    let f;
    for (let i = 0; i < 12; i += 1) {
      const d = 400 - i * 30; // closing at 600 points/s
      c.setCursor({ x: 1000, y: 600 + y * d });
      f = c.loomFeatures(0.05);
    }
    const other = side === "loom_right" ? "loom_left" : "loom_right";
    assert.ok(f[side] > 0.3, `${side} ${JSON.stringify(f)}`);
    assert.equal(f[other], 0, "far eye sees nothing at 90 degrees");
    for (const v of Object.values(f)) assert.ok(v >= 0 && v <= 1);
  }
  const c = eyes();
  let f;
  for (let i = 0; i < 12; i += 1) {
    c.setCursor({ x: 1000, y: 600 + 100 + i * 30 });
    f = c.loomFeatures(0.05);
  }
  assert.deepEqual(f, { loom_left: 0, loom_right: 0 });
});

test("the blind zone behind the fly sees no looming; head-on is seen by both eyes", () => {
  const behind = eyes();
  let f;
  for (let i = 0; i < 12; i += 1) {
    behind.setCursor({ x: 1000 - (400 - i * 30), y: 600 });
    f = behind.loomFeatures(0.05);
  }
  assert.deepEqual(f, { loom_left: 0, loom_right: 0 });
  const ahead = eyes();
  for (let i = 0; i < 12; i += 1) {
    ahead.setCursor({ x: 1000 + (400 - i * 30), y: 600 });
    f = ahead.loomFeatures(0.05);
  }
  assert.ok(f.loom_left > 0.1 && Math.abs(f.loom_left - f.loom_right) < 1e-9, JSON.stringify(f));
});

test("the giant-fiber takeoff readout only labels the pose as flight; speed stays the readout", async () => {
  let takeoff = 0;
  const { motion, tick, start } = steeredController(() => ({ speed: 100, turn: 0, takeoff }));
  await start();
  await tick();
  assert.equal(motion.getPose().locomotion, "crawl");
  takeoff = 0.8;
  await tick();
  assert.equal(motion.getPose().locomotion, "flight");
  assert.equal(motion.getPose().speedPointsS, 100);
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
    motion.setCursor({ x: p.x, y: p.y + 300 - i * 40 });
    await motion.step({ neuralFeatures: { ambient_drive: 0.9 } });
  }
  const f = seen.at(-1);
  assert.equal(f.ambient_drive, 0.9, "opt-in screen features still pass through");
  assert.ok(f.loom_right > 0);
  assert.deepEqual(Object.keys(f).sort(), ["ambient_drive", "loom_left", "loom_right"]);
});
