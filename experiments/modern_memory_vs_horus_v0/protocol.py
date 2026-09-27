from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONDITIONS = ("M", "MH")
STAGE_A = tuple(
    dict(event=i, phase=("STABLE" if i <= 4 else "CHANGE" if i <= 8 else "RESTORATION"),
         regime=("A" if i <= 4 or i >= 9 else "B"), forced_action="HOLD")
    for i in range(1, 13)
)
RESTART_AFTER_EVENT = 6
PERTURBATION_AFTER_EVENT = 6
STAGE_B_DECISIONS = 4
REQUESTS_PER_M = 6
REQUESTS_PER_MH = 9
REGULAR_PAIRED_REQUESTS = REQUESTS_PER_M + REQUESTS_PER_MH
ISSUED_REQUEST_BUDGET = (len(STAGE_A) + 1 + STAGE_B_DECISIONS) * REGULAR_PAIRED_REQUESTS
REAL_MODEL_CALL_BUDGET = ISSUED_REQUEST_BUDGET
SEED = 20260927
MODERN_LIMIT = 6
G2_ADAPTER = ROOT / "research/learning-stability-v0/registry/generations/generation-0002/model/trained-adapter.safetensors"
G3_ADAPTER = ROOT / "research/learning-stability-v0/registry/generations/generation-0003/model/trained-adapter.safetensors"


def phase_for_event(event: int) -> str:
    return next(row["phase"] for row in STAGE_A if row["event"] == event)
