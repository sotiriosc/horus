"""Read-only exact replay, including three-arm receipts and predictor commitments."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.modern_memory_vs_horus_v0_1.transport import RULE_HASH
from .analyze import analyze
from .atomic import scheduled_rows
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING
from .reducer import predict as mechanical_predict

class PrefixMemory:
    def __init__(self,rows):self._rows=rows
    def rows(self,relation):return [r for r in self._rows if r['relation']==relation]


def replay(output):
    saved=json.loads((output/'results.json').read_text())
    total_logical=total_physical=0;details={};snapshots=[]
    for name,specs in SCHEDULES.items():
        root=output/'schedules'/name
        committed=(root/'current').resolve()
        arm_histories=[];sessions=[];sources=[];details[name]={}
        for arm in ARMS:
            with SessionStore(committed/arm/'session',True) as store, \
                 ModernMemory(committed/arm/'memory.sqlite3',False) as memory:
                memory.reconcile(store)
                rows=scheduled_rows(store)
                if len(rows)!=len(specs):raise RuntimeError('incomplete schedule')
                if any(r['observation_id']!=s['observation_id'] or
                    r['regime']!=s['regime'] or r['phase']!=s['phase'] or
                    r['action']!=s['action'] for r,s in zip(rows,specs)):
                    raise RuntimeError('scheduled observation changed')
                arm_histories.append(rows);sessions.append(store.checkpoint['session_id'])
                sources.append({e['record']['receipt']['source_identity'] for e in store.records['events']})
                scored=[e['record'] for e in store.records['training']
                    if e['kind']=='GROUNDED_REDUCER_SCORED_EVENT']
                if len(scored)!=len(specs):raise RuntimeError('scored event count')
                full_memory=memory.rows()
                events={e['sequence']:e['record'] for e in store.records['events']}
                for i,(score,spec) in enumerate(zip(scored,specs)):
                    original=events[score['event_stream_sequence']]['receipt']
                    if (score['event']!=spec['event'] or score['observation_id']!=spec['observation_id']
                        or score['realized']!=dict(next_state=original['next_state'],
                            consequence=original['realized_consequence'])
                        or score['consequence_correct']!=(score['prediction']['consequence']==original['realized_consequence'])
                        or score['exact_correct']!=(score['prediction']==score['realized'])):
                        raise RuntimeError('scoring/receipt mismatch')
                    if arm in ('L','R3'):
                        expected=mechanical_predict(PrefixMemory(full_memory[:i]),score['state'],arm)
                        if (score['prediction']!=dict(next_state=expected['next_state'],
                            consequence=expected['consequence']) or
                            score['used_event_identities']!=expected['used_event_identities'] or
                            score['rule']!=expected['reason'] or score['model_calls']!=0):
                            raise RuntimeError('mechanical prediction not reproduced from authenticated prior memory')
                calls=store.records['calls'];bykind={kind:[e['record'] for e in calls if e['kind']==kind]
                    for kind in ('REQUEST_INTENT','RESPONSE','PARSED',
                                 'TRANSPORT_ATTEMPT_INTENT','TRANSPORT_ATTEMPT_RESULT',
                                 'PREPARATION_GUARD')}
                logical=bykind['REQUEST_INTENT'];ids=[r['call_id'] for r in logical]
                if arm!='M' and (logical or bykind['TRANSPORT_ATTEMPT_INTENT']):
                    raise RuntimeError('mechanical condition made model calls')
                expected_logical=2*(len(specs)+(name=='A')) if arm=='M' else 0
                if len(logical)!=expected_logical or len(ids)!=len(set(ids)):
                    raise RuntimeError('logical call budget or duplicate')
                if (len(logical)!=len(bykind['RESPONSE']) or
                    len(logical)!=len(bykind['PARSED']) or
                    {r['call_id'] for r in bykind['RESPONSE']}!=set(ids) or
                    {r['call_id'] for r in bykind['PARSED']}!=set(ids)):
                    raise RuntimeError('logical call chain incomplete')
                parsed={r['call_id']:r for r in bykind['PARSED']}
                for score in scored if arm=='M' else ():
                    base=f"{specs[score['event']-1]['observation_id']}:M:HOLD"
                    j=parsed[base+':J'];g2=parsed[base+':G2']
                    if j['outcome']!='VALID' or g2['outcome']!='VALID' or score['prediction']!=dict(
                        next_state=j['parsed']['next_state'],consequence=g2['parsed']['consequence']):
                        raise RuntimeError('model prediction not bound to logged parsed output')
                injected=[r for r in bykind['RESPONSE'] if r.get('fault_injected')]
                if len(injected)!=(1 if arm=='M' and name=='A' else 0):
                    raise RuntimeError('registered perturbation count')
                if any(not r['experience_unchanged'] for r in bykind['PREPARATION_GUARD']):
                    raise RuntimeError('preparation mutated experience')
                for intent in logical:
                    cid=intent['call_id'];attempts=[r for r in bykind['TRANSPORT_ATTEMPT_INTENT'] if r['call_id']==cid]
                    results=[r for r in bykind['TRANSPORT_ATTEMPT_RESULT'] if r['call_id']==cid]
                    if len(attempts) not in (1,2) or len(attempts)!=len(results):
                        raise RuntimeError('physical attempt bound')
                    wire=attempts[0]['request_bytes_utf8']
                    if json.loads(wire)!=intent['request']:raise RuntimeError('wire/logical mismatch')
                    for i,(a,r) in enumerate(zip(attempts,results),1):
                        if (a['attempt']!=i or a['attempt_id']!=r['attempt_id'] or
                            a['request_bytes_utf8']!=wire or
                            a['request_bytes_sha256']!=sha256(wire.encode()).hexdigest() or
                            a['repair_rule_sha256']!=RULE_HASH):
                            raise RuntimeError('non-identical transport repair')
                    if len(attempts)==2 and not results[0]['repair_eligible']:
                        raise RuntimeError('semantic output was retried')
                total_logical+=len(logical)
                total_physical+=len(bykind['TRANSPORT_ATTEMPT_INTENT'])
                details[name][arm]=dict(authenticated_events=len(rows),
                    logical_calls=len(logical),physical_attempts=len(bykind['TRANSPORT_ATTEMPT_INTENT']),
                    mechanical_exact_reconstruction=arm in ('L','R3'))
        if not arm_histories[0]==arm_histories[1]==arm_histories[2]:
            raise RuntimeError('matched observations differ')
        if len(set(sessions))!=3 or any(sources[i]&sources[j] for i in range(3) for j in range(i)):
            raise RuntimeError('cross-arm state')
        for snapshot in sorted((root/'triples').iterdir()):
            if not (snapshot/'triple.json').exists():continue
            check=json.loads((snapshot/'triple.json').read_text())
            histories=[]
            for arm in ARMS:
                with SessionStore(snapshot/arm/'session',True) as store, \
                     ModernMemory(snapshot/arm/'memory.sqlite3',False) as memory:
                    memory.reconcile(store);histories.append(scheduled_rows(store))
            if not histories[0]==histories[1]==histories[2]==check['matched_observations']:
                raise RuntimeError('unmatched snapshot')
            snapshots.append(dict(schedule=name,snapshot=snapshot.name,matched_events=len(histories[0])))
    if total_logical!=MODEL_LOGICAL_CEILING or total_physical>MODEL_PHYSICAL_CEILING:
        raise RuntimeError('campaign call ceiling')
    if analyze(output)!=saved:raise RuntimeError('analysis not exactly reproducible')
    result=dict(status='PASS',conditions=details,logical_calls=total_logical,
        physical_attempts=total_physical,matched_snapshots=snapshots,
        exact_mechanical_reconstruction=True,model_output_commitments=True,
        identical_byte_bounded_repair=True,exact_analysis_replay=True,
        no_model_inference=True)
    (output/'replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(replay(p.parse_args().output),sort_keys=True))
