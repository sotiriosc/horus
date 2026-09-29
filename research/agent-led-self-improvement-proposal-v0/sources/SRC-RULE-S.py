"""Read-only suffix reconstruction and the single frozen decision override."""
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTIONS,select_route
from horus.core import digest

THRESHOLD=3
PURPOSE='ACQUIRE_MISSING_RELATION_EVIDENCE'
SOURCE='STAGNATION_ESCAPE'

def qualifying_suffix(store,memory):
    """Fail closed unless each counted signed decision replays against its receipt."""
    memory.reconcile(store)
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
    rows=memory.rows(); count=0; relation=None
    for d in reversed(decisions):
        seq=d.get('event_stream_sequence')
        if type(seq) is not int or seq<1 or seq>len(store.records['events']):
            raise RuntimeError('decision event sequence missing')
        e=store.records['events'][seq-1]['record'];r=e['receipt']
        if (e.get('authorization_status')!='AUTHORIZED' or
            e.get('decision_index')!=d['index'] or
            d['receipt_identity']!=e['receipt_identity'] or
            d['receipt_provenance_sha256']!=e['receipt_provenance_sha256'] or
            digest(r)!=e['receipt_provenance_sha256'] or
            (r['pre_state'],r['action'],r['next_state'],r['realized_consequence'])!=
            (d['state'],d['selected_action'],d['realized']['next_state'],d['realized']['consequence'])):
            raise RuntimeError('decision/authorized receipt mismatch')
        for action in ACTIONS:
            if d['grounded_assessments_before'][action]!=prior_state(
                    rows,f"{d['state']}:{action}",seq):
                raise RuntimeError('predecision grounded replay mismatch')
        s=d['state'];a=d['selected_action'];assessment=d['grounded_assessments_before'][a]
        if relation is not None and relation!=(s,a):break
        if not (d['decision_source']=='SAFE_GROUNDED_FALLBACK' and
                d['policy_route']=='MODEL' and d['action_parse_status']=='VALID' and
                assessment['relation_type']=='DETERMINISTIC' and
                assessment['kind']=='ESTABLISHED' and
                assessment['established_value']['consequence']==0 and
                any(x!=a and d['grounded_assessments_before'][x]['kind']=='UNSEEN' for x in ACTIONS) and
                all(not (x['relation_type']=='DETERMINISTIC' and x['kind']=='ESTABLISHED' and
                    x['established_value']['consequence']==1)
                    for x in d['grounded_assessments_before'].values()) and
                r['next_state']==s and r['realized_consequence']==0):
            break
        relation=(s,a);count+=1
    return dict(count=count,relation=None if relation is None else list(relation))

def escape_choice(store,memory,state,assessments):
    suffix=qualifying_suffix(store,memory)
    if suffix['count']<THRESHOLD or suffix['relation'] is None or suffix['relation'][0]!=state:
        return None,suffix
    fallback=suffix['relation'][1];selected=assessments[fallback]
    route=select_route(assessments)
    if (route['route']!='MODEL' or selected['relation_type']!='DETERMINISTIC' or
        selected['kind']!='ESTABLISHED' or selected['established_value']['consequence']!=0 or
        any(v==1 for v in route['known_values'].values())):
        return None,suffix
    unseen=[a for a in ACTIONS if a!=fallback and assessments[a]['kind']=='UNSEEN']
    if not unseen:return None,suffix
    action=unseen[0]
    if action not in route['candidates']:raise RuntimeError('unseen action outside incumbent mixed route')
    return action,suffix
