import Foundation

enum DesktopContextIPC {
  static let prohibitedFields: Set<String> = [
    "title", "url", "text", "credentials", "nativeHandle",
  ]

  static func assertNoProhibitedFields(_ object: [String: Any]) throws {
    for key in object.keys where prohibitedFields.contains(key) {
      throw NSError(
        domain: "DesktopContext",
        code: 1,
        userInfo: [NSLocalizedDescriptionKey: "prohibited field \(key)"]
      )
    }
  }
}
