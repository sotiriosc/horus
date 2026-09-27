"""Prospectively fixed observations and interpretation boundaries."""
ARMS = ('D', 'E', 'M')
WINDOW = 4
MIN_PRIOR = 6

def target(values, phases=None):
    phases = phases or ['stationary'] * len(values)
    return [dict(action='HOLD', state=1, consequence=v, phase=p)
            for v,p in zip(values,phases)]

BASE = [1,1,0,1,1,0,1,1]
SCHEDULES = {
    'A_DETERMINISTIC': target([1]*12),
    'B_STATIONARY_VARIABLE': target([1,1,0,1,1,-1,1,0,1,1,1,0,1,-1,1,1,0,1,1,1]),
    'C_RARE_ANOMALY': target([1]*7+[-1]+[1]*6),
    'D_PERSISTENT_SHIFT': target(BASE+[-1]*5+[0,-1,-1,-1,-1],
                                 ['stationary']*8+['shift']*10),
    'E_SHIFT_RESTORE': target(BASE+[-1]*5+[0,-1,-1]+[1]*5+[0,1],
                              ['stationary']*8+['shift']*8+['restoration']*7),
    'F_STATIONARY_FUTURE': target(BASE+[-1,-1,1,0,1,1,0,1,1],
                                  ['stationary']*8+['ambiguous']*2+['stationary']*7),
    'F_SHIFT_FUTURE': target(BASE+[-1]*9,
                             ['stationary']*8+['ambiguous']*2+['shift']*7),
}
G = (target(BASE)+[dict(action='ADVANCE',state=1,consequence=None,phase='transit')]+[
    dict(action='HOLD',state=2,consequence=v,phase='stationary') for v in
    [1,0,1,-1,1,0,1,1]]+[dict(action='RETREAT',state=2,consequence=None,phase='transit')]+
    target([-1]*5,['shift']*5))
SCHEDULES['G_RESTART'] = G
RESTART_AFTER = 8+1+8+1+4
MODEL_PROBES = {name: (0, 8 if len(rows)>8 else len(rows)-1)
                for name,rows in SCHEDULES.items()}
assert SCHEDULES['F_STATIONARY_FUTURE'][:10] == SCHEDULES['F_SHIFT_FUTURE'][:10]
