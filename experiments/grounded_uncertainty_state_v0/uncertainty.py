"""Receipt-only exact-relation state. No model result can enter this fold."""
import time
from experiments.modern_memory_vs_horus_v0.storage import canonical

def value(row):
    return dict(next_state=row['realized_next_state'],consequence=row['realized_consequence'])

def fold(rows):
    state=dict(kind='UNSEEN',established_value=None,candidate_value=None,
        candidate_count=0,established_support=[],candidate_support=[],alternatives=[],
        receipt_provenance=[])
    for row in rows:
        if row['authorization_status']!='AUTHORIZED' or not row['event_identity'] or not row['receipt_provenance_sha256']:
            raise RuntimeError('unauthenticated state input')
        identity=row['event_identity'];observed=value(row)
        state['receipt_provenance'].append(dict(identity=identity,value=observed,
            receipt_sha256=row['receipt_provenance_sha256'],
            event_stream_sequence=row['event_stream_sequence']))
        if state['kind']=='UNSEEN':
            state.update(kind='ESTABLISHED',established_value=observed,established_support=[identity])
        elif state['kind']=='ESTABLISHED':
            if observed==state['established_value']:
                state['established_support'].append(identity)
            else:
                state.update(kind='UNRESOLVED_CHANGE',candidate_value=observed,
                    candidate_count=1,candidate_support=[identity],alternatives=[])
        elif observed==state['established_value']:
            state.update(kind='ESTABLISHED',candidate_value=None,candidate_count=0,
                candidate_support=[],alternatives=[],established_support=state['established_support']+[identity])
        elif observed==state['candidate_value']:
            state['candidate_count']+=1;state['candidate_support'].append(identity)
            state.update(kind='ESTABLISHED',established_value=observed,
                established_support=state['candidate_support'][:],candidate_value=None,
                candidate_count=0,candidate_support=[],alternatives=[])
        else:
            # A third value is never silently promoted. The most recent value
            # becomes candidate; displaced candidates retain receipt identities.
            prior=dict(value=state['candidate_value'],support=state['candidate_support'][:])
            state['alternatives'].append(prior)
            state.update(candidate_value=observed,candidate_count=1,candidate_support=[identity])
    return state

def predict(memory,relation,state_number):
    started=time.perf_counter();state=fold(memory.rows(relation))
    chosen=state['established_value']
    point=(chosen if chosen is not None else dict(next_state=state_number,consequence=0))
    return dict(state=state,point=point,rule=('UNSEEN_NEUTRAL_ZERO_AND_IDENTITY_STATE'
        if state['kind']=='UNSEEN' else 'GROUNDED_ESTABLISHED'
        if state['kind']=='ESTABLISHED' else 'UNRESOLVED_USE_PRIOR_ESTABLISHED'),
        used_event_identities=[r['identity'] for r in state['receipt_provenance']],
        update_seconds=time.perf_counter()-started,
        serialized_state_bytes=len(canonical(state).encode()))
