/**
 * On-demand plain-language health dashboard model.
 * Health describes software operation, not feelings or consciousness.
 */

export const HEALTH_DISCLAIMER =
  "Health describes software operation, not feelings or consciousness.";

export const STATUS_COPY = {
  healthy_running: {
    title: "Healthy — running normally",
    explanation: "Current operating checks pass.",
    doing: "Continuing as configured.",
    operator_action: "No action needed.",
  },
  healthy_quiet: {
    title: "Healthy — quiet and idle",
    explanation: "The fly is inactive and the checks still pass.",
    doing: "Remaining idle; quiet input is valid.",
    operator_action: "No action needed.",
    quiet_note: "No food, sleep, reward, or attention is needed.",
  },
  attention: {
    title: "Attention — approaching a limit",
    explanation: "A measured condition is nearing its operating limit.",
    doing: "Preparing an approved remedy.",
    operator_action: "No action needed unless recovery fails.",
  },
  recovering: {
    title: "Recovering — fixing a problem",
    explanation: "The cause matches a recognized software issue.",
    doing: "Applying a bounded recovery recipe.",
    operator_action: "No action needed.",
  },
  checking: {
    title: "Checking the fix",
    explanation: "The repair is installed and passing initial checks.",
    doing: "Running the supervised verification period.",
    operator_action: "No action needed.",
  },
  paused: {
    title: "Paused",
    explanation: "Execution is paused by the operator or a protective condition.",
    doing: "Holding state; no deterioration is modeled.",
    operator_action: "Resume when ready, or Stop to end the session.",
  },
  review_required: {
    title: "Paused — needs review",
    explanation: "The cause is unknown, monitoring is incomplete, or recovery failed.",
    doing: "Model execution is stopped; evidence is preserved.",
    operator_action: "Review the recorded problem before starting a new session.",
  },
  stopped: {
    title: "Stopped",
    explanation: "The operator stopped or a hard fault ended the session.",
    doing: "Session is terminal; no automatic restart.",
    operator_action: "Start a new session only after review if a fault occurred.",
  },
};

export function mapLifecycleToStatus(lifecycle, { quiet = false, approachingLimit = false } = {}) {
  const key = String(lifecycle || "").toLowerCase();
  if (key === "fault" || key === "stopped") return "stopped";
  if (key === "review_required") return "review_required";
  if (key === "paused") return "paused";
  if (key === "recovering") return "recovering";
  if (key === "checking") return "checking";
  if (["running", "ready", "starting"].includes(key)) {
    if (approachingLimit) return "attention";
    if (quiet) return "healthy_quiet";
    return "healthy_running";
  }
  return "review_required";
}

export function buildHealthDashboard(supervisorStatus) {
  const lifecycle = supervisorStatus?.lifecycle || "REVIEW_REQUIRED";
  const technical = supervisorStatus?.health?.technical || supervisorStatus || {};
  const quiet = Boolean(supervisorStatus?.quiet);
  const approachingLimit = Boolean(supervisorStatus?.approaching_limit);
  const status = mapLifecycleToStatus(lifecycle, { quiet, approachingLimit });
  const copy = STATUS_COPY[status];
  return {
    status,
    title: copy.title,
    explanation: copy.explanation,
    doing: copy.doing,
    operator_action: copy.operator_action,
    quiet_note: copy.quiet_note || null,
    disclaimer: HEALTH_DISCLAIMER,
    cards: {
      signal_activity: "within limits",
      movement: quiet ? "quietly idle" : "moving as intended",
      surroundings: "input current",
      keeping_up: "on time",
      rules_intact: "checked",
      automatic_recovery:
        status === "review_required"
          ? "paused for review"
          : ["recovering", "checking", "attention"].includes(status)
            ? "action and attempt"
            : "no action needed",
    },
    technical,
  };
}
