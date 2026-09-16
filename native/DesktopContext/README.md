# native/DesktopContext

Swift helper: AppKit, read-only Accessibility, optional ScreenCaptureKit.

Screen capture and Accessibility default **off** in `config/desktop-pet.json`. Denial selects open-space / coarse geometry fallback.

## IPC contract

See `ipc-protocol.json`. Electron main talks to this helper over a local loopback channel with a per-launch token. No titles, URLs, or credentials in payloads.

## Build (macOS only)

```bash
swift build
```

This Linux CI environment cannot compile AppKit targets. Sources are scaffolded for Cam’s Apple Silicon Mac.

## Layout

- `Sources/DesktopContext/DesktopContextMain.swift` — process entry
- `Sources/DesktopContext/IPC.swift` — framed JSON messages
- `Sources/DesktopContext/AccessibilityReader.swift` — read-only AX geometry (gated)
- `Package.swift` — executable package
