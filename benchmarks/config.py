"""H2 V0.1 frozen measurement + development defaults.

Changing frozen fields is a protocol change (H2 V0.2).
Candidate hyperparameters below are DEVELOPMENT defaults only —
configuration freeze is GOVERNANCE step 4 and has not occurred.
"""

PROTOCOL_VERSION = "H2-V0.1"
PRECISION = "fp32"
DTYPE_BYTES = 4

# Frozen model / task (shared by reference and both candidates).
# Single-head content addressing. ATTN_BETA sharpens softmax so a bound
# key match is not washed out over 32k–64k positions.
D_MODEL = 64
N_HEADS = 1
N_LAYERS = 2
D_HEAD = D_MODEL // N_HEADS
ATTN_BETA = 16.0

WEIGHT_SEED = 0xC15A1001
DEV_CORPUS_SEED = 0xC15A2001
VAL_CORPUS_SEED = 0xC15A2002
# Independent seed family. Do not use until the immutable final test.
FINAL_CORPUS_SEED = 0xC15A2F01

FIDELITY_LENGTHS = (32768, 65536)
QUESTIONS_PER_LENGTH = 1000
QUESTION_CLASSES = (
    "single_distant_fact",
    "two_source",
    "cross_context_composition",
    "distractor_discrimination",
    "position_balanced",
)

BUCKETS = (
    ("local", 1, 8192),
    ("near", 8192, 32768),
    ("medium", 32768, 131072),
    ("long", 131072, 262144),
    ("very_long", 262144, 524288),
    ("extreme", 524288, 1_048_576),
)

# Development defaults — not frozen candidate configs
CANDIDATE_A_DEV = {
    "block_size": 1024,
    "local_window": 2,
    "global_summaries": 1,
    "cross_block_selections": 16,
    "selection_frequency": "every_layer",
}

CANDIDATE_B_DEV = {
    "leaf_block": 1024,
    "summary_levels": 2,
    "retrieved_blocks": 16,
    "refinement_stages": 2,
    "group_size": 4,
}

# Development-sweep subsample of the development partition.
# Not the 1000-item primary set. Not validation. Not final.
SWEEP_QUESTIONS_PER_LENGTH = 100
SWEEP_LENGTHS = FIDELITY_LENGTHS
