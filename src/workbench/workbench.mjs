/**
 * Separately opened workbench shell (lazy; never mounted under transparent pet).
 */

export function workbenchRoutes() {
  return {
    pet: "/pet",
    health: "/health",
    workbench: "/workbench",
  };
}

export function shouldMountWorkbench(route) {
  return route === "/workbench";
}

export function workbenchPanels() {
  return [
    { id: "anatomy", title: "Anatomy viewer", lazy: true },
    { id: "activity", title: "Activity panel", lazy: true },
    { id: "diagnostics", title: "Diagnostics export", lazy: true },
  ];
}
