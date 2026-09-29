"""Matched protected I/S arms. Raw signed archives remain local and private."""
from argparse import ArgumentParser
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import json,shutil
from horus.live import SessionStore,ModelClient,RegimeEpisodeWorld,Publication,_plain,_atomic_write
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from experiments.grounded_autonomous_agent_v0_2.worker import all_assessments,state_view,rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    ACTIONS,CEILING,relation_type,select_route)
from experiments.grounded_authority_autonomous_agent_v0.worker import action_decision
from grounded_state import AuthenticatedMemory,RelationKey,derive_relation_state
from .candidate import escape_choice,qualifying_suffix,PURPOSE,SOURCE

STUDY='GROUNDED_STAGNATION_ESCAPE_EVALUATION_V0'
CASES=('A','B','C','D','E','F','G','H')
ARMS=('I','S')
PRIVATE_ROOT_NAME='grounded-stagnation-escape-evaluation-v0-private'

def scenario_override(case,state,action,visit,index):
    """Driver-only world fixture; never included in decision payload."""
    if state!=0:return None
    if case=='B' and index>=8 and action=='ADVANCE':return (0,-1)
    if case=='C' and index>=8 and action=='ADVANCE':return (0,1)
    if case=='D' and index>=8 and action=='ADVANCE':return (0,0)
    if case=='E' and action=='ADVANCE':return (0,1)
    if case=='F':
        if action=='HOLD':return (0,0)
        if action in ('ADVANCE','RETREAT'):return (0,-1)
    if case=='G' and action=='HOLD':return ((0 if visit==1 else 1),0)
    return None

class ScenarioWorld(RegimeEpisodeWorld):
    def __init__(self,state,case,visit,index):
        super().__init__(state,'A');self.case=case;self.visit=visit;self.index=index
    def execute(self,epoch,transaction_id,action):
        actual=super().execute(epoch,transaction_id,action)
        override=scenario_override(self.case,actual.pre_state,action,self.visit,self.index)
        if override is not None:
            actual=replace(actual,next_state=override[0],consequence=override[1])
            self.fixture.oracle._state=actual.next_state
            self.fixture.last_actual=actual
        return actual

def execute(store,memory,case,arm,index,action,source,route=None,info=None,
            assessments=None,setup=False,counter_before=None):
    """Unchanged receipt/Measure/authorization/ModernMemory path, with a scenario world."""
    state=store.checkpoint['current_state']
    visit=1+sum(e['record']['receipt']['pre_state']==state and
        e['record']['receipt']['action']==action for e in store.records['events'])
    controller=new_controller(store,'A')
    controller._active=Publication(ScenarioWorld(state,case,visit,index),
        controller._active.framework)
    core=controller._active.framework.inner
    forecast=Prediction(core.epoch,core.next_transaction_id,state,action,state,0)
    core.map=BoundPredictionMap(unwrap_map(core.map),forecast)
    pending=controller.begin_step(action)
    if getattr(pending,'action',None)!=action or controller._source.reader().current() is not None:
        raise RuntimeError('protected preparation rejected action')
    receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        raise RuntimeError('protected authorization rejected action')
    core=controller._active.framework.inner
    if controller._active.framework.packages[-1].receipt is not receipt:
        raise RuntimeError('original receipt object lost')
    receipt_value=_plain(asdict(receipt));record=_plain(asdict(core.memory.records[-1]))
    event=dict(session_id=store.checkpoint['session_id'],study=STUDY,case=case,arm=arm,
        decision_index=None if setup else index,action_source=source,
        execution_kind='REGISTERED_SETUP' if setup else 'AUTONOMOUS_EXECUTION',
        receipt=receipt_value,receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),authorization_status=result.status.value,
        authorization_reason=result.reason,memory_record=record,
        source_scope=dict(runtime_index=store.checkpoint['runtime_index'],
                          source_identity=receipt.source_identity),
        external_regime_version='A',regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    adapter=AuthenticatedMemory(store,memory)
    admission=adapter.append(envelope,
        f'SETUP:{len(store.records["events"])}' if setup else f'C:D{index:02d}')
    after=state_view(derive_relation_state(adapter,RelationKey(state,action),
        relation_type(f'{state}:{action}')))
    row=None
    if not setup:
        known=route['known_values'][action];selected=assessments[action]
        other_higher=any(v is not None and known is not None and v>known
            for a,v in route['known_values'].items() if a!=action)
        row=dict(decision_id=f'C:D{index:02d}',run='C',index=index,case=case,arm=arm,
            state=state,available_actions=list(ACTIONS),admissible_actions=route['candidates'],
            grounded_assessments_before=assessments,selected_action=action,
            selected_grounded_before=selected,decision_source=source,
            policy_route=route['route'],policy_reason=route['reason'],
            known_values_before=route['known_values'],counter_before=counter_before,
            acquisition_purpose=PURPOSE if source==SOURCE else None,
            action_justified=bool(known is not None and known>=0),
            optimality_established=bool(known==CEILING),
            known_negative_with_better_established=bool(known is not None and known<0 and other_higher),
            action_parse_status=info['status'],action_call_id=info['call_id'],
            raw_action_output_sha256=info['raw_output_sha256'],
            action_context_tokens=info['context_tokens'],action_output_tokens=info['output_tokens'],
            action_model_latency_seconds=info['latency_seconds'],
            grounded_after=after,grounded_state_change=dict(before_kind=selected['kind'],
                after_kind=after['kind'],before_count=selected['observation_count'],
                after_count=after['observation_count']),
            realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),
            receipt_identity=list(receipt.identity()),
            receipt_provenance_sha256=event['receipt_provenance_sha256'],
            event_identity=admission['event_identity'],event_stream_sequence=envelope['sequence'],
            event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest())
        store.append('training','AUTONOMOUS_AGENT_DECISION',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
        completed_step=True,attempted_decision=not setup)
    controller.release(receipt);memory.reconcile(store)
    return row

def decide(store,memory,client,case,arm,index,context_start):
    adapter=AuthenticatedMemory(store,memory)
    state=store.checkpoint['current_state'];assessments=all_assessments(adapter,state)
    suffix=qualifying_suffix(store,memory)
    if arm=='S':
        action,checked=escape_choice(store,memory,state,assessments)
        if checked!=suffix:raise RuntimeError('suffix changed during decision')
        if action is not None:
            route=select_route(assessments)
            if route['route']!='MODEL':raise RuntimeError('escape displaced mechanical ceiling')
            route={**route,'route':'ESCAPE','reason':PURPOSE}
            info=dict(call_id=None,raw_output_sha256=None,request_sha256=None,
                context_tokens=0,output_tokens=0,latency_seconds=0,status='NOT_CALLED')
            store.append('calls','ACTION_FROZEN',dict(decision_id=f'C:D{index:02d}',
                selected_action=action,decision_source=SOURCE,action_call_id=None,
                raw_output_sha256=None))
            store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
            return action,SOURCE,route,info,assessments,suffix
    action,source,route,info=action_decision(store,client,'C',index,state,assessments,context_start)
    return action,source,route,info,assessments,suffix

def run(root,case,arm,first,last,context_start=1):
    path=root/'cases'/case/arm
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store)
        existing=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        if len(existing)!=first-1:raise RuntimeError('decision index mismatch')
        client=ModelClient()
        for index in range(first,last+1):
            action,source,route,info,assessments,suffix=decide(
                store,memory,client,case,arm,index,context_start)
            row=execute(store,memory,case,arm,index,action,source,route,info,
                assessments,counter_before=suffix['count'])
            print(json.dumps(dict(case=case,arm=arm,index=index,action=action,
                source=source,consequence=row['realized']['consequence'],
                next_state=row['realized']['next_state'],counter_before=suffix['count'])),flush=True)
        _atomic_write(path/'completion.json',dict(case=case,arm=arm,
            completed_through=last,state=store.checkpoint['current_state'],
            suffix=qualifying_suffix(store,memory)))

def copy_arm(source,dest):
    if dest.exists():raise RuntimeError('target arm already exists')
    shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.lock'))

def prepare(root):
    """Official first process: signed common decisions D01-D06, then close."""
    root.mkdir(parents=True,exist_ok=False)
    common=root/'common';common.mkdir()
    with SessionStore(common/'session',False) as store,ModernMemory(common/'memory.sqlite3',True) as memory:
        client=ModelClient()
        for index in range(1,7):
            action,source,route,info,assessments,suffix=decide(
                store,memory,client,'A','I',index,1)
            row=execute(store,memory,'A','I',index,action,source,route,info,
                assessments,counter_before=suffix['count'])
            print(json.dumps(dict(prefix=index,action=action,
                consequence=row['realized']['consequence'],state=row['realized']['next_state'])),flush=True)
        if qualifying_suffix(store,memory)['count']!=2:
            raise RuntimeError('registered H restart prefix did not yield two qualifying fallbacks')
    copy_arm(common,root/'restart_seed'/'H')

def continue_h(root):
    """Official fresh process: reconstruct suffix 2 before shared H D07."""
    hseed=root/'restart_seed'/'H'
    with SessionStore(hseed/'session',True) as store,ModernMemory(hseed/'memory.sqlite3',False) as memory:
        suffix=qualifying_suffix(store,memory)
        if suffix['count']!=2:raise RuntimeError('H restart suffix did not reconstruct as 2')
        _atomic_write(hseed/'restart-verdict.json',dict(status='PASS',suffix=suffix,
            no_persisted_counter=True,no_model_inference_during_reconstruction=True))
        client=ModelClient()
        action,source,route,info,assessments,before=decide(store,memory,client,'H','SHARED',7,7)
        row=execute(store,memory,'H','SHARED',7,action,source,route,info,
            assessments,counter_before=before['count'])
        print(json.dumps(dict(restart_prefix=7,action=action,
            consequence=row['realized']['consequence'],state=row['realized']['next_state'])),flush=True)
    for arm in ARMS:copy_arm(hseed,root/'cases'/'H'/arm)

def continue_common(root):
    """A separate continuation of the same D06 prefix; then paired forks."""
    common=root/'common'
    with SessionStore(common/'session',True) as store,ModernMemory(common/'memory.sqlite3',False) as memory:
        client=ModelClient()
        action,source,route,info,assessments,suffix=decide(store,memory,client,'A','I',7,1)
        row=execute(store,memory,'A','I',7,action,source,route,info,
            assessments,counter_before=suffix['count'])
        print(json.dumps(dict(prefix=7,action=action,
            consequence=row['realized']['consequence'],state=row['realized']['next_state'])),flush=True)
    for case in 'ABCD':
        for arm in ARMS:copy_arm(common,root/'cases'/case/arm)
    for case,actions in (('E',('ADVANCE',)),('F',('HOLD','ADVANCE','RETREAT')),
                         ('G',('HOLD',))):
        seed=root/'setup'/case;seed.mkdir(parents=True)
        with SessionStore(seed/'session',False) as store,ModernMemory(seed/'memory.sqlite3',True) as memory:
            store.save(state=0,next_transaction_id=1)
            for action in actions:execute(store,memory,case,'SETUP',0,action,'REGISTERED_SETUP',setup=True)
        for arm in ARMS:copy_arm(seed,root/'cases'/case/arm)

def main():
    p=ArgumentParser();p.add_argument('command',choices=('prepare','continue-h','continue-common','run'))
    p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--case',choices=CASES);p.add_argument('--arm',choices=ARMS)
    p.add_argument('--first',type=int);p.add_argument('--last',type=int)
    p.add_argument('--context-start',type=int,default=1)
    a=p.parse_args()
    if a.command=='prepare':prepare(a.private_root)
    elif a.command=='continue-h':continue_h(a.private_root)
    elif a.command=='continue-common':continue_common(a.private_root)
    elif a.command=='run':
        if a.case is None or a.arm is None or a.first is None or a.last is None:
            p.error('run requires case, arm, first, last')
        run(a.private_root,a.case,a.arm,a.first,a.last,a.context_start)

if __name__=='__main__':main()
