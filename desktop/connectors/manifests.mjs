/**
 * Isolated connector manifests. Future adapters stay disabled until reviewed.
 */

export const CONNECTOR_MANIFESTS = [
  {
    id: "local_summarize",
    title: "Local summarize",
    enabled: false,
    reason: "Not implemented; requires separate review before allowlisting",
  },
  {
    id: "local_verify",
    title: "Local verify",
    enabled: false,
    reason: "Not implemented; requires separate review before allowlisting",
  },
];

export function listEnabledConnectors() {
  return CONNECTOR_MANIFESTS.filter((c) => c.enabled);
}

export function getConnector(id) {
  return CONNECTOR_MANIFESTS.find((c) => c.id === id) || null;
}
