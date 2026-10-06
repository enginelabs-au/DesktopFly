// swift-tools-version: 5.9
import PackageDescription

let package = Package(
  name: "DesktopContext",
  platforms: [.macOS(.v13)],
  products: [
    .executable(name: "DesktopContext", targets: ["DesktopContext"])
  ],
  targets: [
    .executableTarget(
      name: "DesktopContext",
      path: "Sources/DesktopContext"
    )
  ]
)
