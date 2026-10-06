"""Strict immutable policy validation (Pydantic)."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Literal

GraphMode = Literal["full", "reviewed_subset"]

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "config" / "policy.json"


class RecoveryPolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    enabled: bool
    known_conditions_only: bool
    max_attempts_per_incident: int = Field(ge=1)
    max_attempts_per_operator_session: int = Field(ge=1)
    operation_timeout_s: float = Field(gt=0)
    incident_timeout_s: float = Field(gt=0)
    verification_active_s: float = Field(gt=0)
    repeat_failure_window_s: float = Field(gt=0)
    checkpoint_min_age_before_warning_s: float = Field(ge=0)
    allow_repeated_failed_recipe: bool
    allow_runtime_weight_updates: bool
    allow_threshold_relaxation: bool
    allow_automatic_resume_after_user_pause: bool

    @field_validator(
        "operation_timeout_s",
        "incident_timeout_s",
        "verification_active_s",
        "repeat_failure_window_s",
        "checkpoint_min_age_before_warning_s",
        mode="before",
    )
    @classmethod
    def _finite_number(cls, value: Any) -> Any:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("must be a finite number, not bool")
        if not math.isfinite(float(value)):
            raise ValueError("must be finite")
        return value


class Policy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    schema_version: int = Field(ge=1)
    dataset: str
    real_graph_enabled: bool
    require_reviewed_subset: bool
    graph_mode: GraphMode = "full"
    max_neurons_initial: int = Field(ge=1, le=1_000_000)
    # Which reviewed subset files to load ("" = the original 256-neuron subset).
    reviewed_subset_name: str = Field(default="", pattern=r"^[a-z0-9-]{0,32}$")
    max_edges_initial: int = Field(ge=1, le=100_000_000)
    torch_lif_min_neurons: int = Field(ge=1, default=256)
    # Compiled parallel CPU kernel for graphs at or above this size (0 = never).
    fused_lif_min_neurons: int = Field(ge=0, le=10_000_000, default=0)
    fused_lif_threads: int = Field(ge=1, le=64, default=8)
    device: Literal["mps", "cpu"]
    allow_cpu_fallback: bool
    runtime_dtype: Literal["float32"]
    neural_dt_s: float
    neural_steps_per_block: int = Field(ge=1)
    physics_dt_s: float
    sensory_hz: float = Field(gt=0)
    telemetry_hz: float = Field(gt=0)
    render_target_hz: float = Field(gt=0)
    tau_m_s: float = Field(gt=0)
    rate_ema_tau_s: float = Field(gt=0)
    voltage_reset: float
    voltage_threshold: float
    voltage_min: float
    voltage_max: float
    external_input_max: float = Field(gt=0)
    incoming_absolute_weight_cap: float = Field(gt=0, le=1.1)
    max_spike_rate_hz: float = Field(gt=0)
    max_block_start_lateness_s: float = Field(gt=0)
    max_block_compute_s: float = Field(gt=0)
    # Owner-approved fixed tolerance for isolated late blocks. Defaults are the
    # strict behavior (any late block is a hard fault) so absence never relaxes.
    late_block_max_consecutive: int = Field(default=0, ge=0, le=4)
    late_block_max_per_second: int = Field(default=0, ge=0, le=12)
    late_block_hard_cap_s: float | None = Field(default=None, gt=0, le=0.25)
    # Owner decision: slow wall-clock blocks caused by the host OS are counted
    # and reported but are not a stop. Real compute time stays strictly checked.
    late_block_wall_fault: bool = Field(default=True, strict=True)
    # Owner decision (2026-10-06): behaviour comes from the network. The only
    # code-set inputs are a constant resting input and small bounded noise,
    # both fixed here and recorded as model assumptions.
    resting_drive: float = Field(default=0.0, ge=0, le=2.0)
    intrinsic_noise_amplitude: float = Field(default=0.0, ge=0, le=2.0)
    intrinsic_noise_seed: int = Field(default=0, ge=0, le=2**31 - 1)
    # Owner decision: planned clean start of neuron state after this much
    # simulated time. 0 disables it. Never used to recover from a fault.
    scheduled_state_reset_s: float = Field(default=0.0, ge=0, le=3600)
    heartbeat_timeout_s: float = Field(gt=0)
    cooperative_stop_grace_s: float = Field(gt=0)
    terminate_grace_s: float = Field(gt=0)
    sensor_stale_after_s: float = Field(gt=0)
    host_stale_after_s: float = Field(gt=0)
    checkpoint_interval_s: float = Field(gt=0)
    session_active_time_limit_s: float = Field(gt=0)
    auto_restart_after_hard_fault: bool
    recovery: RecoveryPolicy
    screen_capture_enabled: bool
    network_bind: Literal["127.0.0.1"]
    max_ws_message_bytes: int = Field(ge=256)
    max_displayed_neurons: int = Field(ge=1)
    source_kind: str

    @field_validator(
        "neural_dt_s",
        "physics_dt_s",
        "sensory_hz",
        "telemetry_hz",
        "render_target_hz",
        "tau_m_s",
        "rate_ema_tau_s",
        "voltage_reset",
        "voltage_threshold",
        "voltage_min",
        "voltage_max",
        "external_input_max",
        "incoming_absolute_weight_cap",
        "max_spike_rate_hz",
        "max_block_start_lateness_s",
        "max_block_compute_s",
        "heartbeat_timeout_s",
        "cooperative_stop_grace_s",
        "terminate_grace_s",
        "sensor_stale_after_s",
        "host_stale_after_s",
        "checkpoint_interval_s",
        "session_active_time_limit_s",
        mode="before",
    )
    @classmethod
    def _reject_bool_and_nonfinite(cls, value: Any) -> Any:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("must be a finite number, not bool")
        if not math.isfinite(float(value)):
            raise ValueError("must be finite")
        return float(value)

    @field_validator(
        "late_block_max_consecutive",
        "late_block_max_per_second",
        "late_block_hard_cap_s",
        "scheduled_state_reset_s",
        "resting_drive",
        "intrinsic_noise_amplitude",
        "intrinsic_noise_seed",
        mode="before",
    )
    @classmethod
    def _reject_bool_late_block(cls, value: Any) -> Any:
        if isinstance(value, bool):
            raise ValueError("must be a number, not bool")
        return value

    @model_validator(mode="after")
    def _cross_checks(self) -> Policy:
        expected_physics = self.neural_dt_s * self.neural_steps_per_block
        if abs(self.physics_dt_s - expected_physics) > 1e-12:
            raise ValueError("physics_dt_s must equal neural_dt_s * neural_steps_per_block")
        if self.max_spike_rate_hz > 1.0 / self.neural_dt_s + 1e-12:
            raise ValueError("max_spike_rate_hz must be <= 1/neural_dt_s")
        if not (self.voltage_min < self.voltage_reset < self.voltage_threshold < self.voltage_max):
            raise ValueError("invalid voltage ordering")
        if (
            self.late_block_hard_cap_s is not None
            and self.late_block_hard_cap_s < self.max_block_compute_s
        ):
            raise ValueError("late_block_hard_cap_s must be >= max_block_compute_s")
        if self.late_block_max_per_second < self.late_block_max_consecutive and (
            self.late_block_max_per_second != 0
        ):
            raise ValueError(
                "late_block_max_per_second must be >= late_block_max_consecutive"
            )
        if self.auto_restart_after_hard_fault is not False:
            raise ValueError("auto_restart_after_hard_fault must be false")
        if self.recovery.allow_runtime_weight_updates or self.recovery.allow_threshold_relaxation:
            raise ValueError("recovery must not relax weights or thresholds")
        if self.device == "mps" and self.allow_cpu_fallback:
            # Allowed by schema but production Mac profile should keep fallback false.
            pass
        return self


def load_policy(path: Path | None = None) -> Policy:
    raw = json.loads((path or POLICY_PATH).read_text(encoding="utf-8"))
    return Policy.model_validate(raw)


def load_policy_dict(path: Path | None = None) -> dict[str, Any]:
    return load_policy(path).model_dump()
