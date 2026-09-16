/**
 * Application + tray menu templates. Callbacks are typed actions, not eval.
 */

export function buildApplicationMenuTemplate(actions) {
  requireActions(actions);
  return [
    { role: "appMenu" },
    {
      label: "File",
      submenu: [
        { label: "Export diagnostics…", click: () => actions.exportDiagnostics() },
        { role: "close" },
      ],
    },
    { role: "editMenu" },
    {
      label: "View",
      submenu: [
        { label: "Find fly", click: () => actions.findFly() },
        { label: "Find cursor", click: () => actions.findCursor() },
        { label: "Health…", click: () => actions.openHealth() },
        { label: "Workbench…", click: () => actions.openWorkbench() },
        { label: "Settings…", click: () => actions.openSettings() },
      ],
    },
    { role: "windowMenu" },
    {
      role: "help",
      submenu: [{ label: "Fly help and credits", click: () => actions.openHelp() }],
    },
  ];
}

export function buildTrayMenuTemplate(actions, { exploreHide = false, canResume = false } = {}) {
  requireActions(actions);
  return [
    { id: "health", label: "Healthy — checks look normal", enabled: false },
    { label: "Find fly", click: () => actions.findFly() },
    { label: "Find cursor", click: () => actions.findCursor() },
    {
      label: "Explore and hide",
      type: "checkbox",
      checked: exploreHide,
      click: (item) => actions.setExploreHide(Boolean(item?.checked)),
    },
    { label: "Health…", click: () => actions.openHealth() },
    { label: "Settings…", click: () => actions.openSettings() },
    { type: "separator" },
    { id: "pause", label: "Pause", click: () => actions.pause() },
    {
      id: "resume",
      label: "Resume",
      enabled: canResume,
      click: () => actions.resume(),
    },
    { label: "Stop simulation", click: () => actions.stop() },
    { label: "Quit Fly", click: () => actions.quit() },
  ];
}

function requireActions(actions) {
  const required = [
    "openHealth",
    "openWorkbench",
    "openSettings",
    "openHelp",
    "exportDiagnostics",
    "findFly",
    "findCursor",
    "setExploreHide",
    "pause",
    "resume",
    "stop",
    "quit",
  ];
  for (const key of required) {
    if (typeof actions?.[key] !== "function") {
      throw new Error(`PetMenuActions missing ${key}`);
    }
  }
}
