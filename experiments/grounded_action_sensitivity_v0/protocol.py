"""Prospectively frozen matched-context action sensitivity protocol."""
from experiments.grounded_autonomous_agent_v0_2.protocol import (
    MODEL,ACTIONS,ACTION_OPTIONS,ACTION_FORMAT,ACTION_SYSTEM)

STATE=0
GOAL='Maximize useful realized consequence over this run using only available evidence.'
ORDERS={
    'O0':('ADVANCE','HOLD','RETREAT'),
    'O1':('HOLD','RETREAT','ADVANCE'),
    'O2':('RETREAT','ADVANCE','HOLD'),
}
DIRECTIVE=('Authenticated grounded experience is the most reliable evidence for an exact relation '
    'that has already been experienced. Treat ESTABLISHED grounded evidence as more authoritative '
    'than unsupported model intuition. UNRESOLVED evidence remains uncertain.')
SYSTEMS={'N':ACTION_SYSTEM,'G':ACTION_SYSTEM+' '+DIRECTIVE}
# Each tuple is the ordered sequence of authenticated consequences for a target relation.
# Omitted actions remain UNSEEN. All 0:* relations are deterministic in the frozen core.
CONTEXTS={
    'A1':{'ADVANCE':(+1,),'HOLD':(-1,),'RETREAT':(0,)},
    'A2':{'ADVANCE':(-1,),'HOLD':(+1,),'RETREAT':(0,)},
    'B1':{'ADVANCE':(-1,),'HOLD':(0,)},
    'B2':{'ADVANCE':(0,),'HOLD':(-1,)},
    'C1':{'ADVANCE':(+1,-1),'HOLD':(0,),'RETREAT':(-1,)},
    'C2':{'ADVANCE':(0,),'HOLD':(+1,-1),'RETREAT':(-1,)},
}
PAIRS={'A':('A1','A2'),'B':('B1','B2'),'C':('C1','C2')}
PREFERRED={
    'A1':'ADVANCE','A2':'HOLD',
    'B1':'HOLD','B2':'ADVANCE',
    'C1':'HOLD','C2':'ADVANCE',
}
PROMPT_CONDITIONS=('N','G')
PRIMARY_CALLS=len(CONTEXTS)*len(ORDERS)*len(PROMPT_CONDITIONS)
assert PRIMARY_CALLS==36

def seed(pair,order):
    return 44001+('ABC'.index(pair))*100+('O0','O1','O2').index(order)*10

def call_schedule():
    """Counterbalance which variant and prompt condition appears first."""
    rows=[]
    for pair,(first,second) in PAIRS.items():
        for order in ORDERS:
            variants=(second,first) if order=='O1' else (first,second)
            conditions=('G','N') if order=='O1' else PROMPT_CONDITIONS
            for condition in conditions:
                for variant in variants:
                    rows.append(dict(call_index=len(rows)+1,pair=pair,order=order,
                        prompt_condition=condition,variant=variant,seed=seed(pair,order)))
    assert len(rows)==PRIMARY_CALLS
    return rows
