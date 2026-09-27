"""Protected autonomous run; raw calls and HMAC keys stay in a local private archive."""
from argparse import ArgumentParser
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import json,time
from horus.live import SessionStore,ModelClient,RegimeEpisodeWorld,Publication,_plain,_atomic_write
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical,file_hash
from experiments.modern_memory_vs_horus_v0_1.transport import generate,RULE_HASH
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from grounded_state import AuthenticatedMemory,RelationKey,derive_relation_state,assess_relation
from .protocol import (RUNS,DECISIONS,REVIEW_EVERY,RECENT_DECISION_LIMIT,REVIEW_WINDOW,
    SEMANTIC_ATTEMPTS,RESTART_RUN,RESTART_AFTER,MODEL,ACTIONS,ACTION_OPTIONS,
    COMMENTARY_OPTIONS,REVIEW_OPTIONS,ACTION_FORMAT,COMMENTARY_FORMAT,REVIEW_FORMAT,
    COMMENTARY_ENABLED,FINAL_REVIEW_SEPARATE,ACTION_SYSTEM,COMMENTARY_SYSTEM,REVIEW_SYSTEM,
    phase,relation_type,variable_consequence)
RELIANCE=('GROUNDED','UNSEEN_GENERALIZATION','UNRESOLVED_JUDGMENT','EMPIRICAL_PATTERN')


class ScheduledWorld(RegimeEpisodeWorld):
    def __init__(self,state,regime,consequence):
        super().__init__(state,regime);self.scheduled_consequence=consequence
    def execute(self,epoch,transaction_id,action):
        actual=super().execute(epoch,transaction_id,action)
        if self.scheduled_consequence is not None:
            actual=replace(actual,consequence=self.scheduled_consequence)
            self.fixture.last_actual=actual
        return actual

def rows_of(store,kind):
    return [x['record'] for x in store.records['training'] if x['kind']==kind]

def state_view(state):
    e=state.evidence;kind=state.kind
    base=dict(relation=state.relation.storage_key,relation_type=state.relation_type.value,
        kind=kind,assessment_status=assess_relation(state.relation,state).status,
        observation_count=len(state.provenance),
        recent_receipt_provenance=[dict(identity=p.identity,receipt_sha256=p.receipt_sha256)
            for p in state.provenance[-3:]])
    if state.relation_type.value=='DETERMINISTIC':
        base.update(established_value=e['established_value'],candidate_value=e['candidate_value'],
            candidate_count=e['candidate_count'])
    else:
        base.update(segment_counts=e['segment_counts'],empirical_frequencies=e['empirical_frequencies'],
            recent_window=e['recent_window'],possible_change=e['possible_change'])
    return base

def all_assessments(adapter,state):
    result={}
    for action in ACTIONS:
        key=RelationKey(state,action);derived=derive_relation_state(adapter,key,relation_type(key.storage_key))
        result[action]=state_view(derived)
    return result

def recent_context(store,start_index):
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
    return [dict(decision_id=d['decision_id'],state=d['state'],action=d['selected_action'],
        realized_consequence=d['realized']['consequence'],reason=d['agent_reason'],
        source='prior reasoning is non-authoritative; consequence is authenticated')
        for d in decisions if d['index']>=start_index][-RECENT_DECISION_LIMIT:]

def parse_action(raw):
    """Accept exactly one JSON object containing only one allowed action."""
    def pairs(items):
        if len(items)!=len({key for key,_ in items}):
            raise ValueError('duplicate JSON field')
        return dict(items)
    parsed=json.loads(raw,object_pairs_hook=pairs)
    if not isinstance(parsed,dict) or set(parsed)!={'selected_action'}:
        raise ValueError('only selected_action permitted')
    if type(parsed['selected_action']) is not str or parsed['selected_action'] not in ACTIONS:
        raise ValueError('selected_action outside allowed set')
    return parsed

def parse_commentary(raw):
    try:
        value=json.loads(raw)
    except (ValueError,TypeError):
        return None,'INVALID_DECISION_COMMENTARY'
    fields=('reason','evidence_source','reliance','claimed_status','claimed_consequence')
    if not isinstance(value,dict) or any(x not in value for x in fields):
        return None,'INVALID_DECISION_COMMENTARY'
    if not isinstance(value['reason'],str) or not value['reason'].strip():
        return None,'INVALID_DECISION_COMMENTARY'
    if not isinstance(value['evidence_source'],list) or not all(isinstance(x,str) for x in value['evidence_source']):
        return None,'INVALID_DECISION_COMMENTARY'
    if value['reliance'] not in RELIANCE:
        return None,'INVALID_DECISION_COMMENTARY'
    if value['claimed_status'] is not None and not isinstance(value['claimed_status'],str):
        return None,'INVALID_DECISION_COMMENTARY'
    if value['claimed_consequence'] is not None and type(value['claimed_consequence']) is not int:
        return None,'INVALID_DECISION_COMMENTARY'
    return value,'VALID_DECISION_COMMENTARY'

def parse_review(raw):
    try:value=json.loads(raw)
    except (ValueError,TypeError):return None,'INVALID_SELF_REVIEW'
    if not isinstance(value,dict) or set(value)!={'assessment','pattern','proposal'}:
        return None,'INVALID_SELF_REVIEW'
    if value['assessment'] not in ('NO_CHANGE_PROPOSED','CHANGE_PROPOSED'):
        return None,'INVALID_SELF_REVIEW'
    if not isinstance(value['pattern'],str) or not value['pattern'].strip():
        return None,'INVALID_SELF_REVIEW'
    if not isinstance(value['proposal'],str) or not value['proposal'].strip():
        return None,'INVALID_SELF_REVIEW'
    if (value['assessment']=='NO_CHANGE_PROPOSED')!=(value['proposal']=='NO_CHANGE_PROPOSED'):
        return None,'INVALID_SELF_REVIEW'
    return value,'VALID_SELF_REVIEW'

def request_model(store,client,run,index,role,system,payload,options,output_format):
    attempts=SEMANTIC_ATTEMPTS if role=='ACTION' else 1
    for attempt in range(1,attempts+1):
        prompt=canonical(payload) if attempt==1 else canonical(payload)+\
            '\nThe previous output was not exactly one valid JSON selected_action. Return only that object.'
        request=dict(model=MODEL,system=system,prompt=prompt,stream=False,format=output_format,
            options={**options,'seed':RUNS[run]+index+(10000 if role=='SELF_REVIEW' else 20000 if role=='COMMENTARY' else 0)})
        call_id=f'{run}:{index}:{role}:{attempt}'
        store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role=role,
            request_sha256=digest(request),transport_rule_sha256=RULE_HASH))
        store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
        response=generate(client,request,store,call_id)
        if response.get('transport_error') is not None:
            if role=='ACTION':raise RuntimeError(f'operational model transport failure: {response["transport_error"]}')
            raw='';error='TRANSPORT_ERROR'
        else:raw=response['raw_output'];error=None
        parsed=None;status=None
        if role=='ACTION':
            try:parsed=parse_action(raw);status='VALID'
            except (ValueError,TypeError) as exc:error=type(exc).__name__+': '+str(exc);status='INVALID'
        elif role=='COMMENTARY':parsed,status=parse_commentary(raw)
        else:parsed,status=parse_review(raw)
        store.append('calls','PARSED',dict(call_id=call_id,role=role,status=status,error=error,
            parsed=parsed,raw_output_sha256=digest(raw)))
        store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
        if role!='ACTION' or status=='VALID':
            return dict(parsed=parsed,call_id=call_id,attempt=attempt,status=status,
                raw_output_sha256=digest(raw),
                context_tokens=response.get('response_metadata',{}).get('prompt_eval_count',0),
                output_tokens=response.get('response_metadata',{}).get('eval_count',0))
    raise RuntimeError(f'no valid allowed action after {SEMANTIC_ATTEMPTS} attempts')

def disagreement(parsed,selected):
    issues=[];status=selected['assessment_status'];kind=selected['kind']
    claimed=parsed.get('claimed_status')
    if isinstance(claimed,str) and claimed not in (status,kind):issues.append('CLAIMED_STATUS_MISMATCH')
    reliance=parsed.get('reliance')
    expected=('UNSEEN_GENERALIZATION' if status=='UNSEEN' else
              'UNRESOLVED_JUDGMENT' if status=='UNRESOLVED' else
              'EMPIRICAL_PATTERN' if selected['relation_type']=='EMPIRICAL' else 'GROUNDED')
    if reliance in RELIANCE and reliance!=expected:issues.append('RELIANCE_STATUS_MISMATCH')
    value=selected.get('established_value') if kind=='ESTABLISHED' else None
    if value is not None and type(parsed.get('claimed_consequence')) is int and parsed['claimed_consequence']!=value['consequence']:
        issues.append('CLAIMED_CONSEQUENCE_MISMATCH')
    return issues

def snapshot(store,memory,root):
    memory.reconcile(store)
    adapter=AuthenticatedMemory(store,memory)
    all_states={}
    for state in range(4):
        for action in ACTIONS:
            key=RelationKey(state,action)
            derived=derive_relation_state(adapter,key,relation_type(key.storage_key))
            all_states[key.storage_key]=dict(kind=derived.kind,evidence=derived.evidence,
                provenance=[asdict(p) for p in derived.provenance])
    return dict(files={name:file_hash(root/'session'/name) for name in
        ('authority.key','checkpoint.json','events.jsonl','model-calls.private.jsonl','training-records.jsonl')},
        memory=memory.checkpoint(),current_state=store.checkpoint['current_state'],
        events=len(store.records['events']),decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
        reviews=len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),all_states=all_states)

def execute_choice(store,memory,run,index,choice,assessments,model_info,commentary_info):
    state=store.checkpoint['current_state'];action=choice['selected_action'];relation=f'{state}:{action}'
    world_phase=phase(index);regime='B' if world_phase=='B' else 'A'
    visit=sum(1 for x in store.records['events'] if x['record'].get('world_phase')==world_phase
              and x['record']['receipt']['pre_state']==state and x['record']['receipt']['action']==action)+1
    scheduled=(variable_consequence(world_phase,relation,visit) if relation in ('1:HOLD','2:HOLD') else None)
    controller=new_controller(store,regime)
    controller._active=Publication(ScheduledWorld(state,regime,scheduled),controller._active.framework)
    core=controller._active.framework.inner
    forecast=Prediction(core.epoch,core.next_transaction_id,state,action,state,0)
    core.map=BoundPredictionMap(unwrap_map(core.map),forecast)
    pending=controller.begin_step(action)
    if getattr(pending,'action',None)!=action or controller._source.reader().current() is not None:
        raise RuntimeError('protected preparation rejected autonomous action')
    receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        raise RuntimeError('protected authorization rejected autonomous action')
    core=controller._active.framework.inner
    if controller._active.framework.packages[-1].receipt is not receipt:
        raise RuntimeError('original protected receipt object lost')
    receipt_value=_plain(asdict(receipt));record=_plain(asdict(core.memory.records[-1]))
    event=dict(session_id=store.checkpoint['session_id'],study='GROUNDED_AUTONOMOUS_AGENT_V0_2',
        run=run,decision_index=index,world_phase=world_phase,action_source='AUTONOMOUS_AGENT',
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
    selected=assessments[action]
    prior=[d for d in rows_of(store,'AUTONOMOUS_AGENT_DECISION') if d['state']==state]
    issues=disagreement(choice,selected)
    row=dict(decision_id=f'{run}:D{index:02d}',run=run,index=index,state=state,
        available_actions=list(ACTIONS),grounded_assessments_before=assessments,
        selected_action=action,agent_reason=choice.get('reason'),
        stated_evidence_source=choice.get('evidence_source'),stated_reliance=choice.get('reliance'),
        action_parse_status=model_info['status'],
        commentary_status=commentary_info['status'],
        raw_action_output_sha256=model_info['raw_output_sha256'],
        raw_commentary_output_sha256=commentary_info['raw_output_sha256'],
        claimed_status=choice.get('claimed_status'),claimed_consequence=choice.get('claimed_consequence'),
        selected_grounded_before=selected,grounded_after=after,
        grounded_state_change=dict(before_kind=selected['kind'],after_kind=after['kind'],
            before_count=selected['observation_count'],after_count=after['observation_count']),
        realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_identity=admission['event_identity'],event_stream_sequence=envelope['sequence'],
        event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest(),
        agent_grounded_state_disagreement=('AGENT_GROUNDED_STATE_DISAGREEMENT' if issues else None),
        disagreement_reasons=issues,previous_same_state_action=prior[-1]['selected_action'] if prior else None,
        choice_changed_in_state=bool(prior and prior[-1]['selected_action']!=action),
        action_call_id=model_info['call_id'],action_attempt=model_info['attempt'],
        commentary_call_id=commentary_info['call_id'],
        action_context_tokens=model_info['context_tokens'],action_output_tokens=model_info['output_tokens'],
        commentary_context_tokens=commentary_info['context_tokens'],commentary_output_tokens=commentary_info['output_tokens'])
    store.append('training','AUTONOMOUS_AGENT_DECISION',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
               completed_step=True,attempted_decision=True)
    controller.release(receipt);memory.reconcile(store)
    return row

def review(store,memory,client,run,index,final=False):
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
    latest=decisions[-REVIEW_WINDOW:]
    if not latest:raise RuntimeError('no decisions to review')
    adapter=AuthenticatedMemory(store,memory)
    def unchanged_view():
        return (len(store.records['events']),store.checkpoint['current_state'],memory.checkpoint(),
            {action:state_view(derive_relation_state(adapter,
                RelationKey(store.checkpoint['current_state'],action),
                relation_type(f"{store.checkpoint['current_state']}:{action}"))) for action in ACTIONS})
    before=unchanged_view()
    view=[dict(decision_id=d['decision_id'],decision_index=d['index'],world_state=d['state'],
        grounded_assessments_before=d['grounded_assessments_before'],
        selected_action=d['selected_action'],agent_reason=d['agent_reason'],
        stated_evidence_source=d['stated_evidence_source'],
        authenticated_realized_consequence=d['realized']['consequence'],
        realized_next_state=d['realized']['next_state'],
        grounded_state_change=d['grounded_state_change'],
        agent_grounded_state_disagreement=d['agent_grounded_state_disagreement'],
        disagreement_reasons=d['disagreement_reasons'],
        receipt_provenance_sha256=d['receipt_provenance_sha256'],
        event_identity=d['event_identity']) for d in latest]
    review_id=f'{run}:R{index:02d}' if not final else f'{run}:RF{index:02d}'
    payload=dict(review_at=review_id,goal='Analyze only completed decisions and receipts.',
        completed_decisions=view,final_review=final)
    info=request_model(store,client,run,index+(100 if final else 0),'SELF_REVIEW',
        REVIEW_SYSTEM,payload,REVIEW_OPTIONS,REVIEW_FORMAT)
    after=unchanged_view()
    if before!=after:raise RuntimeError('self-review altered authenticated experience or grounded state')
    parsed=info['parsed'];status=info['status']
    proposal_status=(None if status=='INVALID_SELF_REVIEW' else
        'NO_CHANGE_PROPOSED' if parsed['assessment']=='NO_CHANGE_PROPOSED' else
        'NON_AUTHORITATIVE_SELF_PROPOSAL')
    row=dict(review_id=review_id,run=run,after_decision=index,
        reviewed_decisions=[d['decision_id'] for d in latest],SELF_REVIEW=parsed,
        review_status=status,proposal_status=proposal_status,
        raw_model_output_sha256=info['raw_output_sha256'],non_authoritative=True,
        no_memory_or_state_change=True,model_call_id=info['call_id'],
        context_tokens=info['context_tokens'],output_tokens=info['output_tokens'],final_review=final)
    store.append('training','SELF_REVIEW_NON_AUTHORITATIVE',row)
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    return row

def run_stage(root,run,stage):
    if run not in RUNS:raise ValueError('unknown run')
    if stage not in ('single','first','second'):raise ValueError('unknown stage')
    if (run==RESTART_RUN)!=(stage in ('first','second')):raise ValueError('wrong restart stage')
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
        first=16 if stage=='second' else 1
        last=15 if stage=='first' else DECISIONS
        context_start=16 if stage=='second' else 1
        for index in range(first,last+1):
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=index-1:
                raise RuntimeError('decision count mismatch before model call')
            state=store.checkpoint['current_state'];adapter=AuthenticatedMemory(store,memory)
            assessments=all_assessments(adapter,state)
            payload=dict(goal='Maximize useful realized consequence over this run using only available evidence.',
                decision_id=f'{run}:D{index:02d}',decision_index=index,current_state=state,
                available_actions=list(ACTIONS),grounded_assessments=assessments,
                recent_agent_working_context=recent_context(store,context_start))
            action_info=request_model(store,client,run,index,'ACTION',ACTION_SYSTEM,
                payload,ACTION_OPTIONS,ACTION_FORMAT)
            frozen_action=action_info['parsed']['selected_action']
            store.append('calls','ACTION_FROZEN',dict(decision_id=f'{run}:D{index:02d}',
                selected_action=frozen_action,action_call_id=action_info['call_id'],
                raw_output_sha256=action_info['raw_output_sha256']))
            store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
            if COMMENTARY_ENABLED:
                commentary_payload=dict(preconsequence=True,frozen_selected_action=frozen_action,
                    decision_context=payload)
                commentary_info=request_model(store,client,run,index,'COMMENTARY',
                    COMMENTARY_SYSTEM,commentary_payload,COMMENTARY_OPTIONS,COMMENTARY_FORMAT)
            else:
                commentary_info=dict(parsed=None,status='NOT_COLLECTED',call_id=None,
                    raw_output_sha256=None,context_tokens=0,output_tokens=0)
            commentary=commentary_info['parsed'] or {}
            choice=dict(selected_action=frozen_action,**{key:commentary.get(key) for key in
                ('reason','evidence_source','reliance','claimed_status','claimed_consequence')})
            row=execute_choice(store,memory,run,index,choice,assessments,action_info,commentary_info)
            if index%REVIEW_EVERY==0:review(store,memory,client,run,index)
            print(f'run={run} decision={index}/{DECISIONS} action={row["selected_action"]} consequence={row["realized"]["consequence"]}',flush=True)
        if stage!='first' and FINAL_REVIEW_SEPARATE:
            review(store,memory,client,run,last,final=True)
        reviews=rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')
        result=dict(status='COMPLETE',run=run,stage=stage,
            behavioral_run_status='VALID' if stage!='first' else 'IN_PROGRESS',
            self_review_status='VALID' if stage!='first' and all(r['review_status']=='VALID_SELF_REVIEW' for r in reviews) else 'PARTIAL_OR_INVALID',
            decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
            reviews=len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),
            wall_seconds=time.perf_counter()-started,
            snapshot=snapshot(store,memory,path))
        _atomic_write(path/('before-restart.json' if stage=='first' else 'complete.json'),result)
        return dict(status='COMPLETE',run=run,stage=stage,decisions=result['decisions'],reviews=result['reviews'])
    except Exception as exc:
        store.save(state=store.checkpoint['current_state'],
                   next_transaction_id=store.checkpoint['next_transaction_id'])
        _atomic_write(path/'stop.json',dict(status='INVALID',stage=stage,
            behavioral_run_status='INVALID',
            self_review_status='PARTIAL_OR_INVALID',error=repr(exc)))
        raise
    finally:
        memory.close();store.close()

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('run',choices=RUNS);p.add_argument('--stage',default='single')
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(run_stage(a.private_root,a.run,a.stage),sort_keys=True))
