"""Prospectively frozen, separate observation-controlled schedules."""
from experiments.modern_memory_vs_horus_v0.protocol import G2_ADAPTER, SEED, MODERN_LIMIT

ARMS = ('M', 'L', 'R3')
FALLBACK_CONSEQUENCE = 0
ACTION = 'HOLD'
RESTART = ('A', 6)
PERTURBATION = ('A', 6)


def _rows(name, regimes, phases):
    return tuple(dict(schedule=name, event=i + 1, observation_id=f'{name}:{i+1:02d}:HOLD',
        regime=regime, phase=phase, action=ACTION,
        isolated_noise=phase == 'NOISE')
        for i, (regime, phase) in enumerate(zip(regimes, phases)))

SCHEDULES = {
    'A': _rows('A', 'A'*4+'B'*4+'A'*4,
               ('STABLE',)*4+('CHANGE',)+('PERSISTENCE',)*3+('RESTORATION',)*4),
    'B': _rows('B', 'A'*4+'B'+'A'*4,
               ('STABLE',)*4+('NOISE',)+('RECOVERY',)*4),
    'C': _rows('C', 'A'*4+'B'+'A'*3+'B'*4,
               ('STABLE',)*4+('NOISE',)+('RECOVERY',)*3+('CHANGE',)+('PERSISTENCE',)*3),
    'D': _rows('D', 'A'*4+'B'*6+'A'*4,
               ('STABLE',)*4+('CHANGE',)+('PERSISTENCE',)*5+('RESTORATION',)*4),
}
MODEL_LOGICAL_CEILING = 2 * (sum(map(len, SCHEDULES.values())) + 1)
MODEL_PHYSICAL_CEILING = 2 * MODEL_LOGICAL_CEILING
assert sum(map(len, SCHEDULES.values())) == 47
assert MODEL_LOGICAL_CEILING == 96
