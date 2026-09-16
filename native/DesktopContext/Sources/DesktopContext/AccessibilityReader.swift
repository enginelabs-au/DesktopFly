import Foundation

/// Read-only Accessibility geometry. Disabled unless the operator enables it.
struct AccessibilityReader {
  var enabled: Bool = false

  func focusedWindowRect() -> (x: Double, y: Double, width: Double, height: Double)? {
    guard enabled else { return nil }
    // Mac implementation uses AXUIElement / AXObserver. Linux CI cannot link AppKit.
    return nil
  }
}
