"""Canonical ingest tables. Adapters must map source columns explicitly."""

NEURON_FIELDS = (
    "dataset",
    "neuron_id",
    "cell_type",
    "region",
    "source_annotation_revision",
)
EDGE_FIELDS = ("pre_id", "post_id", "synapse_count")
REVIEW_FIELDS = (
    "neuron_id",
    "decision",
    "modulatory_status",
    "fixed_sign",
    "role",
    "evidence",
)
SENSORY_FIELDS = ("feature_name", "neuron_id", "fixed_gain", "evidence", "mapping_kind")
MOTOR_FIELDS = ("neuron_id", "output_channel", "fixed_gain", "evidence", "mapping_kind")

DECISIONS = frozenset({"include", "clamp", "exclude"})
MODULATORY = frozenset({"no", "yes", "unknown"})
ROLES = frozenset({"sensory", "interneuron", "readout", "none"})
MAPPING_KINDS = frozenset({"anatomical", "engineered"})
OUTPUT_CHANNELS = frozenset({"left", "right", "forward"})

JS_SAFE_INTEGER_MAX = 2**53 - 1
