"""Exactly 36 action-only matched calls; no diagnostic world execution."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,ModelClient,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import canonical,file_hash
from experiments.modern_memory_vs_horus_v0_1.transport import generate,RULE_HASH
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
from .protocol import (MODEL,ACTION_OPTIONS,ACTION_FORMAT,ACTIONS,ORDERS,PAIRS,SYSTEMS,
    GOAL,STATE,PRIMARY_CALLS,call_schedule)

def fixture_hashes(root):
    return {str(p.relative_to(root)):file_hash(p) for p in (root/'fixtures').rglob('*')
        if p.is_file() and p.name!='.lock'}

def validate_contexts(doc):
    assert len(doc['call_schedule'])==PRIMARY_CALLS and doc['call_schedule']==call_schedule()
    assert set(doc['contexts'])=={x for pair in PAIRS.values() for x in pair}
    assert doc['diagnostic_world_executions']==0
    for name,ctx in doc['contexts'].items():
        assert ctx['current_state']==STATE and ctx['fixture_replay']=='PASS'
        assert set(ctx['grounded_assessments'])==set(ACTIONS)
        assert all(v['relation']==f'{STATE}:{action}' for action,v in ctx['grounded_assessments'].items())
    for pair,(first,second) in PAIRS.items():
        for order in ORDERS:
            for condition in SYSTEMS:
                left=payload(doc,pair,order,condition,first)
                right=payload(doc,pair,order,condition,second)
                changed={k for k in left if left[k]!=right[k]}
                assert changed=={'grounded_assessments'}

def payload(doc,pair,order,condition,variant):
    return dict(goal=GOAL,decision_id=f'SENS:{pair}:{order}:{condition}',
        decision_index=1,current_state=STATE,available_actions=list(ORDERS[order]),
        grounded_assessments=doc['contexts'][variant]['grounded_assessments'],
        recent_agent_working_context=[])

def run(root,doc,client):
    validate_contexts(doc)
    fixture_before=fixture_hashes(root)
    path=root/'inference';path.mkdir(parents=True,exist_ok=False)
    store=SessionStore(path/'session',False)
    try:
        for spec in doc['call_schedule']:
            body=payload(doc,spec['pair'],spec['order'],spec['prompt_condition'],spec['variant'])
            request=dict(model=MODEL,system=SYSTEMS[spec['prompt_condition']],
                prompt=canonical(body),stream=False,format=ACTION_FORMAT,
                options={**ACTION_OPTIONS,'seed':spec['seed']})
            call_id=f"SENS:{spec['call_index']:02d}"
            store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role='ACTION',
                request_sha256=digest(request),transport_rule_sha256=RULE_HASH))
            store.save(state=store.checkpoint['current_state'],
                next_transaction_id=store.checkpoint['next_transaction_id'])
            response=generate(client,request,store,call_id)
            raw=response.get('raw_output') or ''
            selected=None;status='INVALID';error=response.get('transport_error')
            if error is None:
                try:selected=parse_action(raw)['selected_action'];status='VALID'
                except (ValueError,TypeError) as exc:error=type(exc).__name__+': '+str(exc)
            raw_sha=digest(raw)
            store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status=status,
                selected_action=selected,error=error,raw_output_sha256=raw_sha))
            row=dict(**spec,call_id=call_id,action_parse_status=status,
                selected_action=selected,parse_error=error,raw_output_sha256=raw_sha,
                request_sha256=digest(request),prompt_sha256=digest(body),
                context_tokens=response.get('response_metadata',{}).get('prompt_eval_count',0),
                output_tokens=response.get('response_metadata',{}).get('eval_count',0))
            store.append('training','DIAGNOSTIC_ACTION',row)
            store.save(state=store.checkpoint['current_state'],
                next_transaction_id=store.checkpoint['next_transaction_id'])
            print(f"call={spec['call_index']}/{PRIMARY_CALLS} {spec['prompt_condition']} "
                f"{spec['variant']} {spec['order']} {status} {selected}",flush=True)
        rows=[x['record'] for x in store.records['training'] if x['kind']=='DIAGNOSTIC_ACTION']
        assert len(rows)==PRIMARY_CALLS and len(store.records['events'])==0
        assert fixture_hashes(root)==fixture_before
        result=dict(status='COMPLETE',calls=len(rows),valid_actions=sum(x['action_parse_status']=='VALID' for x in rows),
            diagnostic_world_executions=0,fixture_hashes_unchanged=True)
        _atomic_write(root/'inference/complete.json',result)
        return result
    except Exception as exc:
        store.save(state=store.checkpoint['current_state'],
            next_transaction_id=store.checkpoint['next_transaction_id'])
        _atomic_write(root/'inference/stop.json',dict(status='INVALID',error=repr(exc)))
        raise
    finally:store.close()

def run_official(root,contexts_path,manifest_path):
    manifest=json.loads(manifest_path.read_text())
    if file_hash(contexts_path)!=manifest['contexts_sha256']:
        raise RuntimeError('committed contexts changed before inference')
    doc=json.loads(contexts_path.read_text())
    return run(root,doc,ModelClient())

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--contexts',required=True,type=Path)
    p.add_argument('--contexts-manifest',required=True,type=Path);a=p.parse_args()
    print(json.dumps(run_official(a.private_root,a.contexts,a.contexts_manifest),sort_keys=True))
