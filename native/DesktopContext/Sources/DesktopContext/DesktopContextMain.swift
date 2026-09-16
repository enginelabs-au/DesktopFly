import Foundation

@main
struct DesktopContextMain {
  static func main() {
    let protocolVersion = 1
    // Helper stays idle until Electron authenticates with a per-launch token.
    // Accessibility / ScreenCaptureKit stay off unless config enables them.
    fputs(
      "DesktopContext ready protocol=\(protocolVersion) capture=off ax=off\n",
      stderr
    )
    RunLoop.main.run(until: Date().addingTimeInterval(0.05))
  }
}
