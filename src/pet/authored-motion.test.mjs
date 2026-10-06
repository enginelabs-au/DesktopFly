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

test("cursor and edges are measured as numbers and never move the fly by themselves", async () => {
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

test("world features describe the surroundings relative to the fly's heading", () => {
  const c = new AuthoredAnimationController({
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
  });
  // Heading east at the centre: south is the fly's right, north is its left.
  c.pose = { ...c.pose, x: 500, y: 400, headingRad: 0 };
  assert.deepEqual(c.worldSensoryFeatures(), {
    cursor_left: 0,
    cursor_right: 0,
    edge_left: 0,
    edge_right: 0,
  });
  c.setCursor({ x: 500, y: 500 });
  let f = c.worldSensoryFeatures();
  assert.ok(f.cursor_right > 0.3 && f.cursor_left === 0, JSON.stringify(f));
  c.setCursor({ x: 500, y: 300 });
  f = c.worldSensoryFeatures();
  assert.ok(f.cursor_left > 0.3 && f.cursor_right === 0, JSON.stringify(f));
  c.setCursor({ x: 500, y: 5000 });
  assert.equal(c.worldSensoryFeatures().cursor_right, 0, "out of range is zero");
  // Near the north edge while heading east: the edge is on the fly's left.
  c.setCursor(null);
  c.pose = { ...c.pose, y: 20 };
  f = c.worldSensoryFeatures();
  assert.ok(f.edge_left > 0.5 && f.edge_right === 0, JSON.stringify(f));
  // Facing the east edge: both sides see it.
  c.pose = { ...c.pose, x: 980, y: 400 };
  f = c.worldSensoryFeatures();
  assert.ok(f.edge_left > 0 && f.edge_right > 0 && f.edge_left === f.edge_right, JSON.stringify(f));
  for (const v of Object.values(f)) assert.ok(v >= 0 && v <= 1);
});

test("measured surroundings are sent to the connectome with each tick", async () => {
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
  motion.setCursor({ x: p.x, y: p.y + 100 });
  ms += 50;
  await motion.step({ neuralFeatures: { ambient_drive: 0.9 } });
  const f = seen.at(-1);
  assert.equal(f.ambient_drive, 0.9, "opt-in screen features still pass through");
  assert.ok(f.cursor_right > 0);
  assert.deepEqual(Object.keys(f).sort(), [
    "ambient_drive", "cursor_left", "cursor_right", "edge_left", "edge_right",
  ]);
});
