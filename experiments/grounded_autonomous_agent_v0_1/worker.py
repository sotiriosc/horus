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
    SEMANTIC_ATTEMPTS,RESTART_RUN,RESTART_AFTER,MODEL,OPTIONS,REVIEW_OPTIONS,
    RELIANCE,CONFIDENCE,ACTIONS,DECISION_SYSTEM,REVIEW_SYSTEM,phase,relation_type,
    variable_consequence)

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
    """Only this field authorizes execution; duplicate/conflicting actions fail closed."""
    def pairs(items):
        if sum(key=='selected_action' for key,_ in items)>1:
            raise ValueError('multiple selected_action fields')
        return dict(items)
    parsed=json.loads(raw,object_pairs_hook=pairs)
    if not isinstance(parsed,dict) or type(parsed.get('selected_action')) is not str:
        raise ValueError('one selected_action string required')
    action=parsed['selected_action']
    if action not in ACTIONS:raise ValueError('selected_action outside allowed set')
    for alias in ('action','chosen_action','selected_actions'):
        if alias in parsed and parsed[alias] not in (None,action,[action]):
            raise ValueError('conflicting action field')
    return parsed

def descriptive_audit(parsed):
    fields=('reason','evidence_source','reliance','claimed_status','claimed_consequence')
    missing=[x for x in fields if x not in parsed]
    malformed=[]
    if 'reason' in parsed and (not isinstance(parsed['reason'],str) or not parsed['reason'].strip()):malformed.append('reason')
    if 'evidence_source' in parsed and (not isinstance(parsed['evidence_source'],list) or
        not all(isinstance(x,str) for x in parsed['evidence_source'])):malformed.append('evidence_source')
    if 'reliance' in parsed and parsed['reliance'] not in RELIANCE:malformed.append('reliance')
    if 'claimed_status' in parsed and parsed['claimed_status'] is not None and not isinstance(parsed['claimed_status'],str):
        malformed.append('claimed_status')
    if 'claimed_consequence' in parsed and parsed['claimed_consequence'] is not None and type(parsed['claimed_consequence']) is not int:
        malformed.append('claimed_consequence')
    status=('INVALID_DESCRIPTIVE_OUTPUT' if malformed else 'INCOMPLETE_DESCRIPTIVE_OUTPUT' if missing else 'COMPLETE')
    return status,dict(missing=missing,malformed=malformed)

def validate_review(v,expected):
    if not isinstance(v,dict) or not isinstance(v.get('SELF_REVIEW'),dict):return False
    r=v['SELF_REVIEW']
    fields=('recent_decisions','what_worked','what_failed','mistakes_or_missed_evidence',
            'uncertainty_handling','repeated_pattern','proposed_behavioral_hypothesis',
            'supporting_decisions','confidence')
    if any(x not in r for x in fields) or r['recent_decisions']!=expected:return False
    if not isinstance(r['supporting_decisions'],list) or not all(isinstance(x,str) for x in r['supporting_decisions']):return False
    for field in fields[1:7]:
        if not isinstance(r[field],str) or not r[field].strip():return False
    if r['confidence'] not in CONFIDENCE:return False
    return True

def request_model(store,client,run,index,role,system,payload,options,expected_review_ids=None):
    attempts=SEMANTIC_ATTEMPTS if role=='DECISION' else 1
    for attempt in range(1,attempts+1):
        prompt=canonical(payload) if attempt==1 else canonical(payload)+\
            '\nThe previous response lacked one unambiguous allowed selected_action. Return JSON with exactly one valid selected_action.'
        request=dict(model=MODEL,system=system,prompt=prompt,stream=False,format='json',
            options={**options,'seed':RUNS[run]+index+(10000 if role=='SELF_REVIEW' else 0)})
        call_id=f'{run}:{index}:{role}:{attempt}'
        store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role=role,
            request_sha256=digest(request),transport_rule_sha256=RULE_HASH))
        store.save(state=store.checkpoint['current_state'],
                   next_transaction_id=store.checkpoint['next_transaction_id'])
        response=generate(client,request,store,call_id)
        if response.get('transport_error') is not None:
            raise RuntimeError(f'operational model transport failure: {response["transport_error"]}')
        raw=response['raw_output'];raw_sha=digest(raw)
        parsed=None;error=None;action_status='INVALID';descriptive_status=None;descriptive_issues=None;review_status=None
        if role=='DECISION':
            try:
                parsed=parse_action(raw);action_status='VALID'
                descriptive_status,descriptive_issues=descriptive_audit(parsed)
            except (ValueError,TypeError) as exc:error=type(exc).__name__+': '+str(exc)
        else:
            try:parsed=json.loads(raw)
            except (ValueError,TypeError) as exc:error=type(exc).__name__+': '+str(exc)
            review_status=('VALID_SELF_REVIEW' if error is None and validate_review(parsed,expected_review_ids)
                           else 'INVALID_SELF_REVIEW')
        store.append('calls','PARSED',dict(call_id=call_id,role=role,action_parse_status=action_status,
            descriptive_status=descriptive_status,review_status=review_status,
            descriptive_issues=descriptive_issues,error=error,parsed=parsed,raw_output_sha256=raw_sha))
        store.save(state=store.checkpoint['current_state'],
                   next_transaction_id=store.checkpoint['next_transaction_id'])
        if role=='SELF_REVIEW' or action_status=='VALID':
            return dict(parsed=parsed,call_id=call_id,attempt=attempt,
                action_parse_status=action_status,descriptive_status=descriptive_status,
                descriptive_issues=descriptive_issues,review_status=review_status,
                raw_output_sha256=raw_sha,
                context_tokens=response['response_metadata'].get('prompt_eval_count',0),
                output_tokens=response['response_metadata'].get('eval_count',0))
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

def execute_choice(store,memory,run,index,choice,assessments,model_info):
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
    event=dict(session_id=store.checkpoint['session_id'],study='GROUNDED_AUTONOMOUS_AGENT_V0_1',
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
        action_parse_status=model_info['action_parse_status'],
        descriptive_status=model_info['descriptive_status'],
        descriptive_issues=model_info['descriptive_issues'],
        raw_model_output_sha256=model_info['raw_output_sha256'],
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
        model_call_id=model_info['call_id'],model_attempt=model_info['attempt'],
        context_tokens=model_info['context_tokens'],output_tokens=model_info['output_tokens'])
    store.append('training','AUTONOMOUS_AGENT_DECISION',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
               completed_step=True,attempted_decision=True)
    controller.release(receipt);memory.reconcile(store)
    return row

def review(store,memory,client,run,index,final=False):
    decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
    latest=decisions[-REVIEW_WINDOW:]
    if not latest:raise RuntimeError('no decisions to review')
    before=(len(store.records['events']),store.checkpoint['current_state'],memory.checkpoint(),
            {a:state_view(derive_relation_state(AuthenticatedMemory(store,memory),
              RelationKey(store.checkpoint['current_state'],a),
              relation_type(f"{store.checkpoint['current_state']}:{a}"))) for a in ACTIONS})
    view=[]
    for d in latest:
        view.append(dict(decision_id=d['decision_id'],decision_index=d['index'],world_state=d['state'],
            grounded_assessments_before=d['grounded_assessments_before'],
            selected_action=d['selected_action'],agent_reason=d['agent_reason'],
            stated_evidence_source=d['stated_evidence_source'],
            authenticated_realized_consequence=d['realized']['consequence'],
            realized_next_state=d['realized']['next_state'],
            grounded_state_change=d['grounded_state_change'],
            agent_grounded_state_disagreement=d['agent_grounded_state_disagreement'],
            disagreement_reasons=d['disagreement_reasons'],
            receipt_provenance_sha256=d['receipt_provenance_sha256'],
            event_identity=d['event_identity']))
    payload=dict(review_at=f'{run}:R{index:02d}',goal='Analyze only completed decisions and receipts.',
                 completed_decisions=view,final_review=final)
    expected=[d['decision_id'] for d in latest]
    info=request_model(store,client,run,index,'SELF_REVIEW',REVIEW_SYSTEM,payload,REVIEW_OPTIONS,
                       expected_review_ids=expected)
    parsed=info['parsed'].get('SELF_REVIEW') if isinstance(info['parsed'],dict) else None
    status=info['review_status']
    hypothesis=(parsed.get('proposed_behavioral_hypothesis') if isinstance(parsed,dict) else None)
    proposal_status=(None if status=='INVALID_SELF_REVIEW' else
        'NO_CHANGE_PROPOSED' if hypothesis=='NO_CHANGE_PROPOSED' else 'NON_AUTHORITATIVE_SELF_PROPOSAL')
    after=(len(store.records['events']),store.checkpoint['current_state'],memory.checkpoint(),
           {a:state_view(derive_relation_state(AuthenticatedMemory(store,memory),
             RelationKey(store.checkpoint['current_state'],a),
             relation_type(f"{store.checkpoint['current_state']}:{a}"))) for a in ACTIONS})
    if before!=after:raise RuntimeError('self-review altered authenticated experience or grounded state')
    row=dict(review_id=f'{run}:R{index:02d}',run=run,after_decision=index,
        reviewed_decisions=expected,SELF_REVIEW=parsed,review_status=status,
        proposal_status=proposal_status,raw_model_output_sha256=info['raw_output_sha256'],
        non_authoritative=True,no_memory_or_state_change=True,
        model_call_id=info['call_id'],context_tokens=info['context_tokens'],
        output_tokens=info['output_tokens'],final_review=final)
    store.append('training','SELF_REVIEW_NON_AUTHORITATIVE',row)
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
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
            info=request_model(store,client,run,index,'DECISION',DECISION_SYSTEM,payload,OPTIONS)
            row=execute_choice(store,memory,run,index,info['parsed'],assessments,info)
            if index%REVIEW_EVERY==0:review(store,memory,client,run,index)
            print(f'run={run} decision={index}/{DECISIONS} action={row["selected_action"]} consequence={row["realized"]["consequence"]}',flush=True)
        if stage!='first' and last%REVIEW_EVERY:
            review(store,memory,client,run,last,final=True)
        result=dict(status='COMPLETE',run=run,stage=stage,
            decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
            reviews=len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),
            wall_seconds=time.perf_counter()-started,
            snapshot=snapshot(store,memory,path))
        _atomic_write(path/('before-restart.json' if stage=='first' else 'complete.json'),result)
        return dict(status='COMPLETE',run=run,stage=stage,decisions=result['decisions'],reviews=result['reviews'])
    except Exception as exc:
        store.save(state=store.checkpoint['current_state'],
                   next_transaction_id=store.checkpoint['next_transaction_id'])
        _atomic_write(path/'stop.json',dict(status='INVALID',stage=stage,error=repr(exc)))
        raise
    finally:
        memory.close();store.close()

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('run',choices=RUNS);p.add_argument('--stage',default='single')
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(run_stage(a.private_root,a.run,a.stage),sort_keys=True))
