import test from "node:test";
import assert from "node:assert/strict";
import {
  clampCursorYieldSpeed,
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
});
