import test from "node:test";
import assert from "node:assert/strict";
import { shouldMountWorkbench, workbenchRoutes } from "./workbench.mjs";

test("workbench is separate from pet route", () => {
  const routes = workbenchRoutes();
  assert.equal(routes.pet, "/pet");
  assert.equal(shouldMountWorkbench("/pet"), false);
  assert.equal(shouldMountWorkbench("/workbench"), true);
});
