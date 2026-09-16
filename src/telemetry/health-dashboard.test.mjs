import test from "node:test";
import assert from "node:assert/strict";
import { HEALTH_DISCLAIMER, buildHealthDashboard } from "./health-dashboard.mjs";

test("health dashboard uses plain language", () => {
  const view = buildHealthDashboard({ lifecycle: "RUNNING", quiet: true });
  assert.match(view.title, /Healthy/);
  assert.equal(view.disclaimer, HEALTH_DISCLAIMER);
  assert.match(view.quiet_note, /No food/);
  assert.doesNotMatch(view.title, /suffering|consciousness/i);
});

test("unknown lifecycle maps to review required", () => {
  const view = buildHealthDashboard({ lifecycle: "weird" });
  assert.equal(view.status, "review_required");
});
