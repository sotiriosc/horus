"""Two stateless reducers over the existing authenticated exact-relation store."""
from collections import Counter
from .protocol import FALLBACK_CONSEQUENCE


def predict(memory, state, arm, action):
    if arm not in ('L', 'R3'):
        raise ValueError('unknown mechanical condition')
    rows = memory.rows(f'{state}:{action}')
    if not rows:
        return dict(next_state=state, consequence=FALLBACK_CONSEQUENCE,
            reason='COLD_START_NEUTRAL_ZERO_AND_IDENTITY_STATE',
            used_event_identities=[], history_count=0, window_consequences=[])
    if arm == 'L':
        selected = rows[-1:]
        consequence = selected[-1]['realized_consequence']
        reason = 'LATEST_AUTHENTICATED_EXACT_RELATION'
    else:
        selected = rows[-3:]
        counts = Counter(r['realized_consequence'] for r in selected)
        largest = max(counts.values())
        leaders = {value for value, count in counts.items() if count == largest}
        consequence = next(r['realized_consequence'] for r in reversed(selected)
                           if r['realized_consequence'] in leaders)
        reason = 'RECENT3_MAJORITY' if len(leaders) == 1 else 'RECENT3_TIE_MOST_RECENT'
    return dict(next_state=rows[-1]['realized_next_state'], consequence=consequence,
        reason=reason, used_event_identities=[r['event_identity'] for r in selected],
        history_count=len(rows),
        window_consequences=[r['realized_consequence'] for r in selected])
