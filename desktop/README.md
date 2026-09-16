# desktop

Electron main process: transparent click-through overlay, menus, status icon, narrow IPC.

Neural / LIF is **enabled** (`real_graph_enabled: true`). Authored animation remains available for Find fly / presentation. MaleCNS feather weights are a separate download; CI uses the synthetic graph.

## Linux-safe checks

```bash
node --test desktop/desktop.test.mjs
```

## macOS GUI (requires Electron install)

```bash
cd desktop && npm install
npm start
```

After pulling tray/pet fixes, quit DesktopFly completely (tray **Quit** or `Cmd+Q`), then restart:

```bash
cd desktop && npm start
```

You should see a **Fly** silhouette in the menu bar and the desktop pet overlay (not Health by default). Use tray or menu **Find fly** if the pet is off-screen. Open **Health…** from the menu when you need the dashboard.

Not Papership Tauri.
