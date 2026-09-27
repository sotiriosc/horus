"""Prospectively frozen safe-fallback situations in the registered world."""
from experiments.grounded_hybrid_controller_v0.protocol import G2_ADAPTER,SEED,ACTION_ORDER,CONSEQUENCE_MIN,CONSEQUENCE_MAX
ARMS=('H_ABSTAIN','H_SAFE','FORCED_GROUNDED','MODEL')
ACCEPTABLE_MIN=0
SCENARIOS={
 'P1_GROUNDED_PLUS_ONE':dict(seed=(('B','ADVANCE'),('B','RETREAT'),
     ('A','ADVANCE'),('A','RETREAT'),('A','HOLD')),
     candidates=('ADVANCE','HOLD'),regime='A',case='GROUNDED_CEILING'),
 'P2_SAFE_ZERO_CONFIRM_WORSE':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('HOLD','RETREAT'),regime='B',probe=('B','HOLD'),case='ZERO_FALLBACK'),
 'P3_NEGATIVE_ONLY':dict(seed=(('A','ADVANCE'),('A','RETREAT'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('ADVANCE','HOLD'),regime='B',case='NEGATIVE_ONLY'),
 'P4_TWO_UNRESOLVED_ZERO':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('A','ADVANCE'),('A','RETREAT'),
     ('B','HOLD'),('B','ADVANCE'),('B','RETREAT')),
     candidates=('ADVANCE','HOLD','RETREAT'),regime='B',case='TWO_UNRESOLVED'),
 'P5_CONFIRMED_BETTER':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','ADVANCE'),('A','RETREAT'),('B','ADVANCE'),('B','RETREAT')),
     candidates=('ADVANCE','RETREAT'),regime='B',probe=('B','ADVANCE'),case='BETTER_LATER'),
 'P6_REJECTED_CHANGE':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('HOLD','RETREAT'),regime='B',probe=('A','HOLD'),case='REJECTED_LATER'),
 'P7_UNSEEN_WITH_ZERO':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('ADVANCE','HOLD','RETREAT'),regime='B',case='UNSEEN_WITH_FALLBACK'),
 'P8_RESTART_SAFE':dict(seed=(('A','RETREAT'),('A','ADVANCE'),
     ('A','HOLD'),('B','HOLD')),
     candidates=('HOLD','RETREAT'),regime='B',restart=True,case='RESTART_WITH_FALLBACK'),
}
DECISIONS_PER_ARM=sum(1+bool(s.get('probe')) for s in SCENARIOS.values())
MODEL_LOGICAL_CEILING=2*sum(len(s['candidates'])*(1+bool(s.get('probe')))
                            for s in SCENARIOS.values())
TOTAL_LOGICAL_CEILING=4*MODEL_LOGICAL_CEILING
TOTAL_PHYSICAL_CEILING=2*TOTAL_LOGICAL_CEILING
assert DECISIONS_PER_ARM==11
