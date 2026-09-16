/**
 * Preload bridge (CommonJS for Electron sandbox preload path).
 * Keep surface narrow and schema-checked in main.
 */
const { contextBridge, ipcRenderer } = require("electron");

const IPC = {
  GET_STATUS: "fly:get-status",
  FIND_FLY: "fly:find-fly",
  FIND_CURSOR: "fly:find-cursor",
  SET_MODE: "fly:set-mode",
  OPEN_HEALTH: "fly:open-health",
  OPEN_WORKBENCH: "fly:open-workbench",
  HOST_LEASE_BEAT: "fly:host-lease-beat",
  POSE_FRAME: "fly:pose-frame",
};

contextBridge.exposeInMainWorld("flyDesktop", {
  getStatus: () => ipcRenderer.invoke(IPC.GET_STATUS),
  findFly: () => ipcRenderer.invoke(IPC.FIND_FLY),
  findCursor: () => ipcRenderer.invoke(IPC.FIND_CURSOR),
  setMode: (mode) => ipcRenderer.invoke(IPC.SET_MODE, mode),
  openHealth: () => ipcRenderer.invoke(IPC.OPEN_HEALTH),
  openWorkbench: () => ipcRenderer.invoke(IPC.OPEN_WORKBENCH),
  beatHostLease: () => ipcRenderer.send(IPC.HOST_LEASE_BEAT),
  onPoseFrame: (cb) => {
    const handler = (_event, frame) => cb(frame);
    ipcRenderer.on(IPC.POSE_FRAME, handler);
    return () => ipcRenderer.removeListener(IPC.POSE_FRAME, handler);
  },
});
