"""Protected three-run autonomous campaign with mechanical authority for exact known facts."""
from argparse import ArgumentParser
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import json,time
from horus.live import SessionStore,ModelClient,Publication,_plain,_atomic_write
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical,file_hash
from experiments.modern_memory_vs_horus_v0_1.transport import generate,RULE_HASH
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from grounded_state import AuthenticatedMemory,RelationKey,derive_relation_state
from experiments.grounded_autonomous_agent_v0_2.worker import (
    ScheduledWorld,all_assessments,state_view,rows_of,snapshot,parse_action)
from .protocol import (RUNS,DECISIONS,REVIEW_EVERY,REVIEW_WINDOW,RECENT_DECISION_LIMIT,
    RESTART_RUN,RESTART_AFTER,MODEL,ACTIONS,ACTION_OPTIONS,ACTION_FORMAT,
    REVIEW_OPTIONS,REVIEW_FORMAT,ACTION_SYSTEM,REVIEW_SYSTEM,GOAL,CEILING,
    phase,relation_type,variable_consequence,select_route,source_for_model_choice)

STUDY='GROUNDED_AUTHORITY_AUTONOMOUS_AGENT_V0'

def call_model(store,client,run,index,role,system,payload,options,output_format):
    request=dict(model=MODEL,system=system,prompt=canonical(payload),stream=False,
        format=output_format,options={**options,'seed':RUNS[run]+index+(10000 if role=='SELF_REVIEW' else 0)})
    call_id=f'{run}:{index}:{role}:1'
    store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role=role,
        request_sha256=digest(request),transport_rule_sha256=RULE_HASH))
    store.save(state=store.checkpoint['current_state'],
        next_transaction_id=store.checkpoint['next_transaction_id'])
    started=time.perf_counter()
    response=generate(client,request,store,call_id)
    latency=time.perf_counter()-started
    raw=response.get('raw_output') or ''
    transport_error=response.get('transport_error')
    return dict(call_id=call_id,raw=raw,transport_error=transport_error,
        raw_output_sha256=digest(raw),request_sha256=digest(request),
        context_tokens=response.get('response_metadata',{}).get('prompt_eval_count',0),
        output_tokens=response.get('response_metadata',{}).get('eval_count',0),
        latency_seconds=latency)

def parse_review(raw):
    try:value=json.loads(raw)
    except (ValueError,TypeError):return None,'INVALID_SELF_REVIEW'
    if not isinstance(value,dict):return None,'INVALID_SELF_REVIEW'
    if set(value)=={'assessment'} and value['assessment']=='NO_CHANGE_PROPOSED':
        return value,'VALID_SELF_REVIEW'
    if set(value)=={'pattern','proposal'} and all(isinstance(value[k],str) and value[k].strip() for k in value):
        return value,'VALID_SELF_REVIEW'
    return None,'INVALID_SELF_REVIEW'

def decision_history(store,start_index):
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
    return [dict(decision_id=d['decision_id'],state=d['state'],action=d['selected_action'],
        authenticated_consequence=d['realized']['consequence'],
        source=d['decision_source']) for d in decisions if d['index']>=start_index][-RECENT_DECISION_LIMIT:]

def action_decision(store,client,run,index,state,assessments,context_start):
    route=select_route(assessments)
    payload=dict(goal=GOAL,decision_id=f'{run}:D{index:02d}',decision_index=index,
        current_state=state,available_actions=route['candidates'],
        grounded_assessments=assessments,
        recent_agent_working_context=decision_history(store,context_start))
    if route['route']=='MECHANICAL':
        action=route['action'];info=dict(call_id=None,raw_output_sha256=None,
            request_sha256=None,context_tokens=0,output_tokens=0,latency_seconds=0,
            status='NOT_CALLED')
    else:
        info=call_model(store,client,run,index,'ACTION',ACTION_SYSTEM,payload,
            ACTION_OPTIONS,ACTION_FORMAT)
        if info['transport_error'] is not None:
            raise RuntimeError('action transport failure: '+str(info['transport_error']))
        try:
            action=parse_action(info['raw'])['selected_action']
            if action not in route['candidates']:raise ValueError('action outside admissible candidates')
            status='VALID'
        except (ValueError,TypeError) as exc:
            action=None;status='INVALID';info['parse_error']=repr(exc)
        info['status']=status
        store.append('calls','PARSED',dict(call_id=info['call_id'],role='ACTION',
            status=status,selected_action=action,error=info.get('parse_error'),
            raw_output_sha256=info['raw_output_sha256']))
        store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
        if status!='VALID':raise RuntimeError('invalid authoritative action: '+info['parse_error'])
    source=(route['source'] if route['route']=='MECHANICAL'
            else source_for_model_choice(route,assessments,action))
    store.append('calls','ACTION_FROZEN',dict(decision_id=f'{run}:D{index:02d}',
        selected_action=action,decision_source=source,action_call_id=info['call_id'],
        raw_output_sha256=info['raw_output_sha256']))
    store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
    return action,source,route,info

def execute_choice(store,memory,run,index,action,source,route,info,assessments):
    state=store.checkpoint['current_state'];relation=f'{state}:{action}'
    world_phase=phase(index);regime='B' if world_phase=='B' else 'A'
    visit=sum(1 for x in store.records['events'] if x['record'].get('world_phase')==world_phase
        and x['record']['receipt']['pre_state']==state and x['record']['receipt']['action']==action)+1
    scheduled=(variable_consequence(world_phase,relation,visit)
        if relation in ('1:HOLD','2:HOLD') else None)
    controller=new_controller(store,regime)
    controller._active=Publication(ScheduledWorld(state,regime,scheduled),controller._active.framework)
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
        raise RuntimeError('original protected receipt object lost')
    receipt_value=_plain(asdict(receipt));record=_plain(asdict(core.memory.records[-1]))
    event=dict(session_id=store.checkpoint['session_id'],study=STUDY,run=run,
        decision_index=index,world_phase=world_phase,action_source=source,
        execution_kind='AUTONOMOUS_EXECUTION',receipt=receipt_value,
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=digest(receipt_value),
        authorization_status=result.status.value,authorization_reason=result.reason,
        memory_record=record,source_scope=dict(runtime_index=store.checkpoint['runtime_index'],
            source_identity=receipt.source_identity),external_regime_version=regime,
        regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    adapter=AuthenticatedMemory(store,memory)
    admission=adapter.append(envelope,f'{run}:D{index:02d}')
    after=state_view(derive_relation_state(adapter,RelationKey(state,action),relation_type(relation)))
    selected=assessments[action];known=route['known_values'][action]
    other_higher_known=any(v is not None and known is not None and v>known
        for a,v in route['known_values'].items() if a!=action)
    row=dict(decision_id=f'{run}:D{index:02d}',run=run,index=index,state=state,
        available_actions=list(ACTIONS),admissible_actions=route['candidates'],
        grounded_assessments_before=assessments,selected_action=action,
        selected_grounded_before=selected,decision_source=source,
        policy_route=route['route'],policy_reason=route['reason'],
        known_values_before=route['known_values'],
        action_justified=bool(known is not None and known>=0),
        optimality_established=bool(known==CEILING),
        known_negative_with_better_established=bool(known is not None and known<0 and other_higher_known),
        action_parse_status=info['status'],action_call_id=info['call_id'],
        raw_action_output_sha256=info['raw_output_sha256'],
        action_context_tokens=info['context_tokens'],action_output_tokens=info['output_tokens'],
        action_model_latency_seconds=info['latency_seconds'],
        grounded_after=after,grounded_state_change=dict(before_kind=selected['kind'],
            after_kind=after['kind'],before_count=selected['observation_count'],
            after_count=after['observation_count']),
        realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_identity=admission['event_identity'],event_stream_sequence=envelope['sequence'],
        event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest())
    store.append('training','AUTONOMOUS_AGENT_DECISION',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
        completed_step=True,attempted_decision=True)
    controller.release(receipt);memory.reconcile(store)
    return row

def review(store,memory,client,run,index,final=False):
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')[-REVIEW_WINDOW:]
    if len(decisions)!=REVIEW_WINDOW:raise RuntimeError('review window incomplete')
    before=(len(store.records['events']),store.checkpoint['current_state'],memory.checkpoint())
    view=[dict(decision_id=d['decision_id'],decision_index=d['index'],world_state=d['state'],
        action_assessments={a:dict(kind=x['kind'],relation_type=x['relation_type'],
            established_value=x.get('established_value'),
            recent_receipt_provenance=x['recent_receipt_provenance'])
            for a,x in d['grounded_assessments_before'].items()},
        selected_action=d['selected_action'],decision_source=d['decision_source'],
        authenticated_realized_consequence=d['realized']['consequence'],
        realized_next_state=d['realized']['next_state'],
        grounded_state_change=d['grounded_state_change'],
        receipt_provenance_sha256=d['receipt_provenance_sha256']) for d in decisions]
    review_id=f'{run}:RF{index:02d}' if final else f'{run}:R{index:02d}'
    payload=dict(review_at=review_id,completed_decisions=view,final_review=final)
    info=call_model(store,client,run,index+(100 if final else 0),'SELF_REVIEW',
        REVIEW_SYSTEM,payload,REVIEW_OPTIONS,REVIEW_FORMAT)
    parsed,status=(None,'INVALID_SELF_REVIEW') if info['transport_error'] else parse_review(info['raw'])
    store.append('calls','PARSED',dict(call_id=info['call_id'],role='SELF_REVIEW',
        status=status,parsed=parsed,raw_output_sha256=info['raw_output_sha256'],
        error=info['transport_error']))
    after=(len(store.records['events']),store.checkpoint['current_state'],memory.checkpoint())
    if before!=after:raise RuntimeError('review altered grounded experience')
    proposal_status=(None if status=='INVALID_SELF_REVIEW' else
        'NO_CHANGE_PROPOSED' if parsed.get('assessment')=='NO_CHANGE_PROPOSED'
        else 'NON_AUTHORITATIVE_SELF_PROPOSAL')
    row=dict(review_id=review_id,run=run,after_decision=index,
        reviewed_decisions=[d['decision_id'] for d in decisions],SELF_REVIEW=parsed,
        review_status=status,proposal_status=proposal_status,non_authoritative=True,
        no_memory_or_state_change=True,raw_model_output_sha256=info['raw_output_sha256'],
        model_call_id=info['call_id'],context_tokens=info['context_tokens'],
        output_tokens=info['output_tokens'],latency_seconds=info['latency_seconds'],
        final_review=final)
    store.append('training','SELF_REVIEW_NON_AUTHORITATIVE',row)
    store.save(state=store.checkpoint['current_state'],
        next_transaction_id=store.checkpoint['next_transaction_id'])
    return row

def run_stage(root,run,stage):
    if run not in RUNS or stage not in ('single','first','second'):
        raise ValueError('unknown run/stage')
    if (run==RESTART_RUN)!=(stage in ('first','second')):
        raise ValueError('wrong restart stage')
    path=root/'runs'/run;create=stage!='second';path.mkdir(parents=True,exist_ok=True)
    store=SessionStore(path/'session',not create);memory=ModernMemory(path/'memory.sqlite3',create)
    client=ModelClient();started=time.perf_counter()
    try:
        memory.reconcile(store)
        if stage=='second':
            expected=json.loads((path/'before-restart.json').read_text())['snapshot']
            actual=snapshot(store,memory,path)
            if actual!=expected:raise RuntimeError('fresh-process restart changed durable experience')
            _atomic_write(path/'restart-verdict.json',dict(status='PASS',exact_snapshot_match=True,
                grounded_memory_survived=True,agent_working_context_reset=True))
        first=RESTART_AFTER+1 if stage=='second' else 1
        last=RESTART_AFTER if stage=='first' else DECISIONS
        context_start=RESTART_AFTER+1 if stage=='second' else 1
        for index in range(first,last+1):
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=index-1:
                raise RuntimeError('decision count mismatch')
            state=store.checkpoint['current_state'];adapter=AuthenticatedMemory(store,memory)
            assessments=all_assessments(adapter,state)
            action,source,route,info=action_decision(store,client,run,index,state,
                assessments,context_start)
            row=execute_choice(store,memory,run,index,action,source,route,info,assessments)
            if index%REVIEW_EVERY==0:review(store,memory,client,run,index)
            print(f'run={run} decision={index}/{DECISIONS} source={source} '
                f'action={action} consequence={row["realized"]["consequence"]}',flush=True)
        if stage!='first':review(store,memory,client,run,last,final=True)
        result=dict(status='COMPLETE',run=run,stage=stage,
            behavioral_run_status='VALID' if stage!='first' else 'IN_PROGRESS',
            decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
            reviews=len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),
            wall_seconds=time.perf_counter()-started,snapshot=snapshot(store,memory,path))
        _atomic_write(path/('before-restart.json' if stage=='first' else 'complete.json'),result)
        return {k:result[k] for k in ('status','run','stage','decisions','reviews')}
    except Exception as exc:
        store.save(state=store.checkpoint['current_state'],
            next_transaction_id=store.checkpoint['next_transaction_id'])
        _atomic_write(path/'stop.json',dict(status='INVALID',stage=stage,error=repr(exc)))
        raise
    finally:
        memory.close();store.close()

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('run',choices=RUNS)
    p.add_argument('--stage',default='single',choices=('single','first','second'))
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(run_stage(a.private_root,a.run,a.stage),sort_keys=True))
