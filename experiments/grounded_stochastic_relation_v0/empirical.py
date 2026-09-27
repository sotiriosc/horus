"""Receipt-only exact-relation empirical fold. No simulator metadata or model inputs."""
from collections import Counter
from experiments.grounded_uncertainty_state_v0.uncertainty import value
from .protocol import WINDOW, MIN_PRIOR

def key(v): return f"{v['next_state']}:{v['consequence']}"

def counts(values):
    tally=Counter(key(v) for v in values)
    return dict(sorted(tally.items()))

def modal(values):
    tally=Counter(key(v) for v in values)
    return max(tally, key=lambda k:(tally[k], -next(i for i,v in enumerate(values) if key(v)==k))) if values else None

def fold(rows):
    outcomes=[]; provenance=[]; segment_start=0; pending=None; confirmed=[]
    for row in rows:
        if (row['authorization_status']!='AUTHORIZED' or not row['event_identity']
                or not row['receipt_provenance_sha256'] or not row['event_stream_sequence']):
            raise RuntimeError('unauthenticated empirical input')
        observed=value(row); outcomes.append(observed)
        provenance.append(dict(identity=row['event_identity'],receipt_sha256=row['receipt_provenance_sha256'],
            event_stream_sequence=row['event_stream_sequence'],value=observed))
        if pending:
            if key(observed)==pending['challenger']:
                segment_start=pending['candidate_start']
                confirmed.append(dict(candidate_start=segment_start,confirmed_at=len(outcomes)-1,
                    support=[p['identity'] for p in provenance[segment_start:]]))
            pending=None
            continue
        segment=outcomes[segment_start:]
        if len(segment)<MIN_PRIOR+WINDOW:continue
        earlier=segment[:-WINDOW];recent=segment[-WINDOW:]
        challenger=key(recent[0])
        if (len(earlier)>=MIN_PRIOR and all(key(v)==challenger for v in recent)
                and challenger!=modal(earlier)):
            pending=dict(challenger=challenger,candidate_start=len(outcomes)-WINDOW,
                prior_counts=counts(earlier),recent_counts=counts(recent),
                recent_support=[p['identity'] for p in provenance[-WINDOW:]])
    current=outcomes[segment_start:]
    kind=('UNSEEN' if not outcomes else 'POSSIBLE_REGIME_CHANGE' if pending else
          'EMPIRICALLY_STABLE' if len(counts(current))==1 else 'VARIABLE_RELATION')
    return dict(kind=kind,observation_count=len(outcomes),outcome_counts=counts(outcomes),
        chronological_outcomes=outcomes,receipt_provenance=provenance,
        recent_window=outcomes[-WINDOW:],window_limit=WINDOW,
        segment_start=segment_start,segment_counts=counts(current),
        empirical_frequencies={k:dict(count=n,denominator=len(current)) for k,n in counts(current).items()},
        segment_mode=modal(current),possible_change=pending,confirmed_changes=confirmed)

def point(state, current_state):
    mode=state['segment_mode']
    if mode is None:return dict(next_state=current_state,consequence=0)
    next_state,consequence=map(int,mode.split(':'))
    return dict(next_state=next_state,consequence=consequence)
