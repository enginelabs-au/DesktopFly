import Foundation

#if canImport(AppKit)
import AppKit
#endif

/// DesktopContext entry. AppKit is Mac-only; Linux CI compiles sources as documentation stubs.
@main
struct DesktopContextMain {
    static func main() {
        let protocolVersion = "1"
        fputs("DesktopContext ready protocol=\(protocolVersion)\n", stderr)
        #if canImport(AppKit)
        // Production Mac path: NSApplication + AX helpers. Not linked on Linux CI.
        #endif
        RunLoop.main.run(until: Date().addingTimeInterval(0.05))
    }
}
