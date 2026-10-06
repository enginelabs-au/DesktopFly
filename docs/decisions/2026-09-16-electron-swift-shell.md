# Decision: Electron overlay + Swift helper, not Papership Tauri

**Date:** 2026-09-16  
**Status:** accepted  
**Product:** DesktopFly (P-011)

## Decision

The desktop shell is Electron (transparent, frameless, click-through overlay) plus a Swift `DesktopContext` helper for AppKit, read-only Accessibility, and optional ScreenCaptureKit. This is not the Papership Tauri stack.

## Why

The handover specifies this split. Papership is a different product (P-009). Sharing a windowing toolkit would couple unrelated release trains and permissions.

## Consequences

- `desktop/` and `native/DesktopContext/` are first-class trees.
- Linux CI cannot certify overlay, focus, or permission behavior.
- Screen capture defaults off (`screen_capture_enabled: false`).
