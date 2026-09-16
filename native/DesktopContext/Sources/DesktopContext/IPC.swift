import Foundation

/// Length-prefixed JSON IPC framing between Electron main and DesktopContext.
public enum DesktopContextIPC {
    public static let protocolVersion = 1

    public struct Envelope: Codable {
        public var protocolVersion: Int
        public var type: String
        public var payload: [String: String]

        public init(type: String, payload: [String: String] = [:]) {
            self.protocolVersion = DesktopContextIPC.protocolVersion
            self.type = type
            self.payload = payload
        }
    }

    public static func encode(_ envelope: Envelope) throws -> Data {
        try JSONEncoder().encode(envelope)
    }

    public static func decode(_ data: Data) throws -> Envelope {
        try JSONDecoder().decode(Envelope.self, from: data)
    }
}
