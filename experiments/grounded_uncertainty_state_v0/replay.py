"""Read-only replay of receipt, relation-state, model-call, and snapshot commitments."""
from argparse import ArgumentParser
import json
from pathlib import Path
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_reducer_vs_model_v0.atomic import scheduled_rows
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING
from .uncertainty import fold
from .reducer import predict as reducer_predict
from .analyze import analyze

class PrefixMemory:
    def __init__(self,rows):self._rows=rows
    def rows(self,relation):return [r for r in self._rows if r['relation']==relation]

def replay(output):
    saved=json.loads((output/'results.json').read_text());logical=physical=0;details={}
    for name,specs in SCHEDULES.items():
        root=output/'schedules'/name;histories=[];sessions=[];sources=[];details[name]={}
        for arm in ARMS:
            with SessionStore(root/arm/'session',True) as store,ModernMemory(root/arm/'memory.sqlite3',False) as memory:
                memory.reconcile(store);actual=scheduled_rows(store)
                if len(actual)!=len(specs):raise RuntimeError('incomplete schedule')
                for row,spec in zip(actual,specs):
                    if any(row[key]!=spec[key] for key in ('schedule','event','observation_id','phase','regime','action')):
                        raise RuntimeError('schedule/receipt mismatch')
                histories.append(actual);sessions.append(store.checkpoint['session_id'])
                sources.append({e['record']['receipt']['source_identity'] for e in store.records['events']})
                scored=[e['record'] for e in store.records['training'] if e['kind']=='GROUNDED_UNCERTAINTY_SCORED_EVENT']
                if len(scored)!=len(specs):raise RuntimeError('missing scored event')
                full=memory.rows();events={e['sequence']:e['record'] for e in store.records['events']}
                for i,row in enumerate(scored):
                    receipt=events[row['event_stream_sequence']]['receipt']
                    if row['realized']!=dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence']):
                        raise RuntimeError('score not bound to receipt')
                    relation=f"{row['state']}:{row['action']}"
                    if arm=='U':
                        before=fold([r for r in full[:i] if r['relation']==relation]);after=fold([r for r in full[:i+1] if r['relation']==relation])
                        if row['grounded_state_before']!=before or row['grounded_state_after']!=after or row['model_calls']!=0:
                            raise RuntimeError('U state not reconstructible from authorized receipts')
                    elif arm in ('L','R3'):
                        expected=reducer_predict(PrefixMemory(full[:i]),row['state'],arm,row['action'])
                        if row['prediction']!=dict(next_state=expected['next_state'],consequence=expected['consequence']) or row['model_calls']!=0:
                            raise RuntimeError('reducer not reconstructible')
                calls=store.records['calls'];intents=[e['record'] for e in calls if e['kind']=='REQUEST_INTENT']
                attempts=[e['record'] for e in calls if e['kind']=='TRANSPORT_ATTEMPT_INTENT']
                parsed={e['record']['call_id']:e['record'] for e in calls if e['kind']=='PARSED'}
                expected_calls=2*(len(specs)+(name=='SUSTAINED')) if arm=='M' else 0
                if len(intents)!=expected_calls or (arm!='M' and attempts):raise RuntimeError('model call budget')
                for row in scored if arm=='M' else ():
                    base=f"{row['observation_id']}:M:{row['action']}"
                    j,g=parsed[base+':J'],parsed[base+':G2']
                    if j['outcome']!='VALID' or g['outcome']!='VALID' or row['prediction']!=dict(next_state=j['parsed']['next_state'],consequence=g['parsed']['consequence']):
                        raise RuntimeError('M score not bound to parsed output')
                if any(not e['record']['experience_unchanged'] for e in calls if e['kind']=='PREPARATION_GUARD'):
                    raise RuntimeError('preparation altered experience')
                logical+=len(intents);physical+=len(attempts)
                details[name][arm]=dict(authenticated_events=len(actual),logical_calls=len(intents),physical_attempts=len(attempts))
        if not all(h==histories[0] for h in histories) or len(set(sessions))!=len(ARMS):
            raise RuntimeError('unmatched or shared arm experience')
        if any(sources[i]&sources[j] for i in range(len(ARMS)) for j in range(i)):
            raise RuntimeError('shared receipt source')
        for snapshot in (root/'triples').iterdir():
            if not (snapshot/'triple.json').exists():continue
            check=json.loads((snapshot/'triple.json').read_text())
            sh=[]
            for arm in ARMS:
                with SessionStore(snapshot/arm/'session',True) as store,ModernMemory(snapshot/arm/'memory.sqlite3',False) as memory:
                    memory.reconcile(store);sh.append(scheduled_rows(store))
            if not all(x==sh[0] for x in sh) or sh[0]!=check['matched_observations']:
                raise RuntimeError('unmatched committed snapshot')
    if logical!=MODEL_LOGICAL_CEILING or physical>MODEL_PHYSICAL_CEILING:raise RuntimeError('model budget')
    if analyze(output)!=saved:raise RuntimeError('analysis not reproducible')
    result=dict(status='PASS',conditions=details,logical_calls=logical,physical_attempts=physical,
        matched_observations=True,exact_U_reconstruction=True,model_output_commitments=True,
        exact_analysis_replay=True)
    (output/'replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(replay(p.parse_args().output),sort_keys=True))
