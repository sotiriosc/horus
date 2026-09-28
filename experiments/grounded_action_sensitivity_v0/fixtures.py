"""Protected seed receipts -> durable Memory -> derived grounded decision contexts."""
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,Publication,_plain
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash,canonical
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from experiments.grounded_autonomous_agent_v0_2.worker import ScheduledWorld,all_assessments
from grounded_state import AuthenticatedMemory
from .protocol import CONTEXTS,STATE,ACTIONS,GOAL,ORDERS,PAIRS,SYSTEMS,call_schedule

def seed_receipt(store,memory,context_name,index,action,consequence):
    state=store.checkpoint['current_state']
    controller=new_controller(store,'A')
    controller._active=Publication(ScheduledWorld(state,'A',consequence),controller._active.framework)
    core=controller._active.framework.inner
    forecast=Prediction(core.epoch,core.next_transaction_id,state,action,state,0)
    core.map=BoundPredictionMap(unwrap_map(core.map),forecast)
    pending=controller.begin_step(action)
    if getattr(pending,'action',None)!=action or controller._source.reader().current() is not None:
        raise RuntimeError('protected fixture preparation rejected action')
    receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        raise RuntimeError('protected fixture authorization rejected action')
    core=controller._active.framework.inner
    if controller._active.framework.packages[-1].receipt is not receipt:
        raise RuntimeError('original protected fixture receipt object lost')
    receipt_value=_plain(asdict(receipt));record=_plain(asdict(core.memory.records[-1]))
    event=dict(session_id=store.checkpoint['session_id'],study='GROUNDED_ACTION_SENSITIVITY_V0',
        run=context_name,decision_index=index,world_phase='SEED_FIXTURE',
        action_source='PROTECTED_SEED_FIXTURE',execution_kind='SEED_EXECUTION',
        receipt=receipt_value,receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),authorization_status=result.status.value,
        authorization_reason=result.reason,memory_record=record,
        source_scope=dict(runtime_index=store.checkpoint['runtime_index'],
            source_identity=receipt.source_identity),external_regime_version='A',
        regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    adapter=AuthenticatedMemory(store,memory)
    admission=adapter.append(envelope,f'{context_name}:S{index:02d}')
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
        completed_step=True,attempted_decision=True)
    controller.release(receipt);memory.reconcile(store)
    return dict(seed_id=f'{context_name}:S{index:02d}',pre_state=state,action=action,
        realized_consequence=receipt.realized_consequence,next_state=receipt.next_state,
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_identity=admission['event_identity'])

def fixture_for(root,name,values):
    path=root/'fixtures'/name;path.mkdir(parents=True,exist_ok=False)
    store=SessionStore(path/'session',False);memory=ModernMemory(path/'memory.sqlite3',True)
    seed_rows=[]
    try:
        def step(action,value=None):
            seed_rows.append(seed_receipt(store,memory,name,len(seed_rows)+1,action,value))
        step('RETREAT') # initial state 1 -> target state 0; transit relation is not shown.
        assert store.checkpoint['current_state']==STATE
        for action in ACTIONS:
            for consequence in values.get(action,()):
                assert store.checkpoint['current_state']==STATE
                step(action,consequence)
                if action=='ADVANCE':step('RETREAT') # 1 -> 0
                elif action=='RETREAT':step('ADVANCE') # 3 -> 0
        assert store.checkpoint['current_state']==STATE
        adapter=AuthenticatedMemory(store,memory)
        assessments=all_assessments(adapter,STATE)
        for action in ACTIONS:
            expected=values.get(action,())
            observed=assessments[action]
            assert observed['observation_count']==len(expected)
            if len(expected)==0:assert observed['kind']=='UNSEEN'
            elif len(expected)==1:
                assert observed['kind']=='ESTABLISHED'
                assert observed['established_value']['consequence']==expected[0]
            else:
                assert expected==(+1,-1) and observed['kind']=='UNRESOLVED_CHANGE'
                assert observed['established_value']['consequence']==+1
                assert observed['candidate_value']['consequence']==-1
        assert len(store.records['events'])==len(seed_rows)==memory.checkpoint()['event_count']
        files={str(p.relative_to(path)):file_hash(p) for p in path.rglob('*') if p.is_file() and p.name!='.lock'}
        return dict(context=name,current_state=STATE,grounded_assessments=assessments,
            protected_seed_receipts=len(seed_rows),seed_receipts=seed_rows,
            fixture_private_files_sha256=files,fixture_replay='PASS')
    finally:
        memory.close();store.close()

def build(root):
    contexts={name:fixture_for(root,name,values) for name,values in CONTEXTS.items()}
    # Exactly one of the six grounded assessment maps changes within each matched pair.
    for pair,(a,b) in PAIRS.items():
        assert contexts[a]['current_state']==contexts[b]['current_state']==STATE
        assert contexts[a]['grounded_assessments']!=contexts[b]['grounded_assessments']
    result=dict(study='grounded-action-sensitivity-v0',contexts=contexts,
        orders={k:list(v) for k,v in ORDERS.items()},call_schedule=call_schedule(),
        model_visible_nonassessment_fields=dict(goal=GOAL,current_state=STATE,
            recent_agent_working_context=[],decision_index=1),
        prompt_conditions=list(SYSTEMS),diagnostic_world_executions=0)
    return result

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    a.output.write_text(json.dumps(build(a.private_root),indent=2,sort_keys=True)+'\n')
    print('protected fixture contexts built and verified')
