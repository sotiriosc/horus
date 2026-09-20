"""Same schedule, seeds and sampler; only Map system text differs from v1."""
from experiments.model_proposal_role_composition_v1.protocol import (
    MODEL, OPTIONS, ACTIONS, EXPLORER_SYSTEM, RECOVERY_SYSTEM, schedule, seed,
    SYSTEMS as V1_SYSTEMS)
from experiments.composition_empty_history_schema_contract_v0.protocol import SYSTEMS as CONTRACT_SYSTEMS

SYSTEMS = {**V1_SYSTEMS, 'Map': CONTRACT_SYSTEMS['B']}
