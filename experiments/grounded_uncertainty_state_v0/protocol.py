"""Prospectively frozen observation schedules and scoring semantics."""
from experiments.modern_memory_vs_horus_v0.protocol import G2_ADAPTER, SEED
ARMS = ('M','L','R3','U')
FALLBACK_CONSEQUENCE = 0
RESTART = ('SUSTAINED',4)
PERTURBATION = RESTART

def rows(name, steps):
    return tuple(dict(schedule=name,event=i,observation_id=f'{name}:{i:02d}:{action}',
        regime=regime,phase=phase,action=action,isolated_noise=phase=='NOISE')
        for i,(regime,phase,action) in enumerate(steps,1))

def h(regimes,phases):
    return [(regime,phase,'HOLD') for regime,phase in zip(regimes,phases)]

SCHEDULES = {
 'SUSTAINED':rows('SUSTAINED',h('AAABBBBAAA',
     ('STABLE',)*3+('CHANGE',)+('PERSISTENCE',)*3+('RESTORATION',)*3)),
 'ANOMALY':rows('ANOMALY',h('AAABAAAA',
     ('STABLE',)*3+('NOISE',)+('RECOVERY',)*4)),
 'EXCURSION':rows('EXCURSION',h('AAABBAAA',
     ('STABLE',)*3+('EXCURSION',)*2+('RESTORATION',)*3)),
 'NOISE_THEN_CHANGE':rows('NOISE_THEN_CHANGE',
     h('AAAB AABBBB AAA'.replace(' ',''),
       ('STABLE',)*3+('NOISE',)+('RECOVERY',)*2+('CHANGE',)+('PERSISTENCE',)*3+('RESTORATION',)*3)
       + [('A','NEW_RELATION','ADVANCE'),('A','NEW_RELATION','HOLD')]),
}
EVENTS_PER_ARM=sum(map(len,SCHEDULES.values()))
MODEL_LOGICAL_CEILING=2*(EVENTS_PER_ARM+1)
MODEL_PHYSICAL_CEILING=2*MODEL_LOGICAL_CEILING
assert len(SCHEDULES['NOISE_THEN_CHANGE'])==15
assert EVENTS_PER_ARM==41
