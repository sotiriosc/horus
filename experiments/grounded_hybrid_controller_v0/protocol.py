"""Prospectively frozen finite autonomous-control scenarios."""
from experiments.modern_memory_vs_horus_v0.protocol import G2_ADAPTER, SEED
ARMS=('HYBRID','MODEL','FORCED_GROUNDED')
ACTION_ORDER=('ADVANCE','HOLD','RETREAT')
CONSEQUENCE_MIN=-1
CONSEQUENCE_MAX=1
# Each seed item is (external regime, observation-controlled action).
SCENARIOS={
 'A_ALL_ESTABLISHED':dict(seed=(('A','HOLD'),('A','ADVANCE'),('A','RETREAT'),
     ('A','RETREAT'),('A','ADVANCE')),candidates=('ADVANCE','HOLD','RETREAT'),regime='A'),
 'B_ESTABLISHED_UNSEEN':dict(seed=(('A','HOLD'),),
     candidates=('ADVANCE','HOLD'),regime='A'),
 'C_ESTABLISHED_UNRESOLVED':dict(seed=(('B','ADVANCE'),('B','RETREAT'),
     ('A','ADVANCE'),('A','RETREAT'),('A','HOLD')),
     candidates=('ADVANCE','HOLD'),regime='A'),
 'D_UNRESOLVED_BEST':dict(seed=(('A','ADVANCE'),('A','RETREAT'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('ADVANCE','HOLD'),regime='B'),
 'E_MULTIPLE_UNSEEN':dict(seed=(),candidates=('ADVANCE','HOLD','RETREAT'),
     regime='A',second_decision=True),
 'F_CANDIDATE_CONFIRMED':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD'),('B','HOLD')),
     candidates=('HOLD','RETREAT'),regime='B'),
 'G_RESTORATION':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD'),('B','HOLD'),('A','HOLD'),('A','HOLD')),
     candidates=('HOLD','RETREAT'),regime='A'),
 'H_RESTART_UNRESOLVED':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('HOLD','RETREAT'),regime='B',restart=True),
 'I_ANOMALY_REJECTED':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD'),('A','HOLD')),
     candidates=('HOLD','RETREAT'),regime='A'),
}
MAX_DECISIONS=sum(1+bool(s.get('second_decision')) for s in SCENARIOS.values())
MODEL_LOGICAL_CEILING=2*sum(len(s['candidates'])*(1+bool(s.get('second_decision')))
                             for s in SCENARIOS.values())
# HYBRID may also query every candidate if still unseen; transport may repair once.
TOTAL_LOGICAL_CEILING=2*MODEL_LOGICAL_CEILING
TOTAL_PHYSICAL_CEILING=2*TOTAL_LOGICAL_CEILING
assert MAX_DECISIONS==10
