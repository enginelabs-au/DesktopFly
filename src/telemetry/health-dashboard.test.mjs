import test from "node:test";
import assert from "node:assert/strict";
import { HEALTH_DISCLAIMER, buildHealthDashboard, describeKeepingUp } from "./health-dashboard.mjs";

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

test("late timing moments are shown in plain language, never hidden", () => {
  assert.equal(describeKeepingUp(undefined), "on time");
  assert.equal(describeKeepingUp({ late_blocks_total: 0 }), "on time");
  const text = describeKeepingUp({
    late_blocks_total: 3,
    worst_late_block_s: 0.0063,
    late_block_max_in_a_row: 2,
  });
  assert.match(text, /3 brief late moments/);
  assert.match(text, /6 ms/);
  assert.match(text, /more than 2 in a row stops the fly/);
  const view = buildHealthDashboard({
    lifecycle: "RUNNING",
    health: { technical: { timing: { late_blocks_total: 1, worst_late_block_s: 0.005, late_block_max_in_a_row: 2 } } },
  });
  assert.match(view.cards.keeping_up, /1 brief late moment /);
});
