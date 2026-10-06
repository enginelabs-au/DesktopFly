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

test("cursor yield is applied to connectome-driven presentation", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async step() {
        return {
          motor: { dx: 0, dy: 0 },
          transition_source: "connectome",
        };
      },
    },
  });
  motion.setCursor({ x: 490, y: 400 }, { moving: true });
  await motion.step();
  ms = 50;
  const pose = await motion.step();
  assert.ok(pose.speedPointsS > 0);
  assert.equal(pose.transitionSource, "geometry");
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

test("a moving cursor makes the fly visibly flee within bounded speed", async () => {
  let ms = 0;
  const motion = createPetMotionController({
    petConfig: {
      cursor_yield_radius_points: 140,
      cursor_yield_max_speed_points_s: 150,
      cursor_yield_duration_ms: 600,
      cursor_yield_cooldown_ms: 200,
      max_speed_points_s: 160,
    },
    controllerKind: "lif",
    now: () => ms,
    bounds: { x: 0, y: 0, width: 1000, height: 800 },
    connectomeDriver: {
      async step() {
        return { motor: { dx: 0, dy: 0, speed: 0, turn: 0 }, transition_source: "connectome" };
      },
    },
  });
  const start = motion.getPose();
  motion.setCursor({ x: start.x - 60, y: start.y }, { moving: true });
  await motion.step();
  let maxSpeed = 0;
  let sawGeometry = false;
  for (let i = 0; i < 12; i += 1) {
    ms += 50;
    const p = await motion.step();
    maxSpeed = Math.max(maxSpeed, p.speedPointsS);
    if (p.transitionSource === "geometry") sawGeometry = true;
  }
  const end = motion.getPose();
  const before = Math.hypot(start.x - (start.x - 60), 0);
  const after = Math.hypot(end.x - (start.x - 60), end.y - start.y);
  assert.ok(after - before > 40, `expected to move away, delta ${after - before}`);
  assert.ok(maxSpeed <= 160 + 1e-6, `speed ${maxSpeed} exceeds cap`);
  assert.ok(sawGeometry, "cursor yield should drive the pose while active");
});
