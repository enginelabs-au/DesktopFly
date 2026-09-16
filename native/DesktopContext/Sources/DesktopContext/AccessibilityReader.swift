import Foundation

#if canImport(AppKit)
import AppKit
#endif

/// Read-only Accessibility geometry. Never keylogs. Off until config enables it.
public struct AccessibilityReader {
    public var enabled: Bool = false

    public init(enabled: Bool = false) {
        self.enabled = enabled
    }

    public func focusedWindowBounds() -> [String: Double]? {
        guard enabled else { return nil }
        #if canImport(AppKit)
        // Mac: AXUIElementCopyAttributeValue for kAXFocusedWindowAttribute / position/size.
        return nil
        #else
        return nil
        #endif
    }
}
