from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
from horus.live import SessionStore
from horus.relation_routing import RelationEvidenceStore
from .analyze import analyze
from .atomic import identities
from .storage import ModernMemory
from .protocol import STAGE_A, ISSUED_REQUEST_BUDGET, PHYSICAL_ATTEMPT_CEILING
from .transport import RULE, RULE_HASH


def replay(output):
    saved=json.loads((output/'results.json').read_text())
    checks={}; total_logical=total_physical=0
    pair_root=(output/'current').resolve()
    expected_count=json.loads((pair_root/'pair.json').read_text())['count']
    histories={}; keys=[]
    for arm in ('M','MH'):
        with SessionStore(pair_root/arm/'session',True) as store, ModernMemory(pair_root/arm/'memory.sqlite3',False) as memory:
            memory.reconcile(store);histories[arm]=identities(store)
            keys.append(store.key_path.read_text())
            if histories[arm] != [dict(event=s['event'],action=s['forced_action'],regime=s['regime']) for s in STAGE_A[:expected_count]]:
                raise RuntimeError('schedule replay mismatch')
            bykind={kind:[e['record'] for e in store.records['calls'] if e['kind']==kind] for kind in
                ('REQUEST_INTENT','RESPONSE','PARSED','TRANSPORT_ATTEMPT_INTENT','TRANSPORT_ATTEMPT_RESULT','PREPARATION_GUARD')}
            intents=bykind['REQUEST_INTENT'];ids=[r['call_id'] for r in intents]
            if len(ids)!=len(set(ids)): raise RuntimeError('duplicate logical request')
            if len(intents)!=len(bykind['RESPONSE']) or len(intents)!=len(bykind['PARSED']):
                raise RuntimeError('incomplete logical call chain')
            if {r['call_id'] for r in bykind['RESPONSE']}!=set(ids) or {r['call_id'] for r in bykind['PARSED']}!=set(ids):
                raise RuntimeError('response/parse identities mismatch')
            for intent in intents:
                cid=intent['call_id']
                attempts=[r for r in bykind['TRANSPORT_ATTEMPT_INTENT'] if r['call_id']==cid]
                results=[r for r in bykind['TRANSPORT_ATTEMPT_RESULT'] if r['call_id']==cid]
                if len(attempts) not in (1,2) or len(attempts)!=len(results): raise RuntimeError('transport bound')
                # JSON log serialization sorts dict keys, so use retained wire
                # bytes as authority and compare decoded logical request as well.
                wire=attempts[0]['request_bytes_utf8']
                if json.loads(wire)!=intent['request']: raise RuntimeError('wire/logical mismatch')
                for i,(a,r) in enumerate(zip(attempts,results),1):
                    if a['attempt']!=i or a['attempt_id']!=r['attempt_id'] or a['request_bytes_utf8']!=wire or a['request_bytes_sha256']!=sha256(wire.encode()).hexdigest() or a['repair_rule_sha256']!=RULE_HASH:
                        raise RuntimeError('transport identity/byte mismatch')
                if len(attempts)==2 and not results[0]['repair_eligible']:
                    raise RuntimeError('semantic or successful request retried')
            if any(not r['experience_unchanged'] for r in bykind['PREPARATION_GUARD']):
                raise RuntimeError('preparation mutated experience')
            total_logical+=len(intents);total_physical+=len(bykind['TRANSPORT_ATTEMPT_INTENT'])
            checks[arm]=dict(logical_calls=len(intents),physical_attempts=len(bykind['TRANSPORT_ATTEMPT_INTENT']),
                authenticated_events=len(store.records['events']),stage_a_events=len(histories[arm]))
        if arm=='MH':
            with RelationEvidenceStore(pair_root/arm/'registry') as routing:
                if len(routing.records)!=checks[arm]['authenticated_events']: raise RuntimeError('routing count')
    if histories['M']!=histories['MH'] or keys[0]==keys[1]: raise RuntimeError('matching/isolation failure')
    if total_logical>ISSUED_REQUEST_BUDGET or total_physical>PHYSICAL_ATTEMPT_CEILING: raise RuntimeError('call ceiling')
    if saved['status']=='COMPLETE' and (total_logical!=255 or expected_count!=12): raise RuntimeError('incomplete campaign')
    snapshot_checks=[]
    for snap in sorted((output/'pairs').iterdir()):
        if not (snap/'pair.json').exists(): continue  # unpublished incomplete transaction
        pairs=[]
        for arm in ('M','MH'):
            with SessionStore(snap/arm/'session',True) as store, ModernMemory(snap/arm/'memory.sqlite3',False) as memory:
                memory.reconcile(store);pairs.append(identities(store))
        if pairs[0]!=pairs[1]: raise RuntimeError('snapshot exposed unmatched history')
        snapshot_checks.append(dict(snapshot=snap.name,matched_events=len(pairs[0])))
    if analyze(output)!=saved: raise RuntimeError('analysis not exactly reproducible')
    result=dict(status='PASS',conditions=checks,logical_calls=total_logical,
        physical_attempts=total_physical,matched_snapshot_checkpoints=snapshot_checks,
        exact_analysis_replay=True,byte_identical_bounded_transport=True,
        repair_rule_sha256=RULE_HASH,no_model_inference=True)
    (output/'replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(replay(p.parse_args().output),sort_keys=True))
