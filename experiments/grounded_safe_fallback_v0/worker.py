"""Protected autonomous decisions from matched, receipt-seeded initial histories."""
from argparse import ArgumentParser
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import time
from horus.live import SessionStore,LiveController,_atomic_write,_plain
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical,file_hash
from experiments.grounded_uncertainty_state_v0.harness import capture,prepare_model
from experiments.grounded_uncertainty_state_v0.uncertainty import fold
from experiments.grounded_uncertainty_state_v0.worker import load_clients,new_controller
from experiments.grounded_uncertainty_state_v0.atomic import guarded_prepare
from .policy import choose
from .protocol import ARMS,SCENARIOS

def open_arm(root,arm):
    path=root/'work'/arm
    store=SessionStore(path/'session',True);memory=ModernMemory(path/'memory.sqlite3',False)
    memory.reconcile(store)
    if arm in ('H_ABSTAIN','H_SAFE','MODEL'):
        joint,g2,_=load_clients('M');g2=g2['G2']
    else:joint=g2=None
    return dict(arm=arm,root=path,store=store,memory=memory,joint=joint,g2=g2)

def close_arm(ctx):
    ctx['memory'].close();ctx['store'].close()

def snapshot(ctx):
    store=ctx['store'];memory=ctx['memory'];root=ctx['root']
    return dict(session_files_sha256={name:file_hash(root/'session'/name) for name in
        ('authority.key','checkpoint.json','events.jsonl','model-calls.private.jsonl','training-records.jsonl')},
        memory=memory.checkpoint(),current_state=store.checkpoint['current_state'],
        event_count=len(store.records['events']),grounded_states={relation:fold(memory.rows(relation))
        for relation in ('1:HOLD','1:RETREAT')})

def execute(ctx,controller,action,prediction,scenario,step,source,preparation=None):
    store=ctx['store'];memory=ctx['memory'];core=controller._active.framework.inner
    cap=capture(controller,store,memory,action)
    forecast=Prediction(cap['epoch'],cap['transaction_id'],cap['state'],action,
        prediction['next_state'],prediction['consequence'])
    core.map=BoundPredictionMap(unwrap_map(core.map),forecast)
    pending=controller.begin_step(action)
    if getattr(pending,'action',None)!=action or controller._source.reader().current() is not None:
        raise RuntimeError('protected preparation rejected selected action')
    receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        controller.release(receipt);raise RuntimeError('protected authorization rejected event')
    core=controller._active.framework.inner
    package,record=controller._active.framework.packages[-1],core.memory.records[-1]
    if package.receipt is not receipt:raise RuntimeError('original receipt object lost')
    receipt_value=_plain(asdict(receipt))
    event=dict(session_id=store.checkpoint['session_id'],study='GROUNDED_SAFE_FALLBACK_V0',
        scenario=scenario,step=step,action_source=source,
        execution_kind='AUTONOMOUS_EXECUTION' if source=='AUTONOMOUS_POLICY' else 'OBSERVATION_CONTROLLED_EXECUTION',
        receipt=receipt_value,receipt_identity=list(receipt.identity()),
        receipt_provenance_sha256=digest(receipt_value),authorization_status=result.status.value,
        authorization_reason=result.reason,memory_record=_plain(asdict(record)),
        source_scope=dict(runtime_index=store.checkpoint['runtime_index'],
            source_identity=receipt.source_identity),
        external_regime_version=controller._active.world.regime_version,regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    admission=memory.record(store,envelope,f'{scenario}:{ctx["arm"]}:{step}')
    row=dict(arm=ctx['arm'],scenario=scenario,step=step,action_source=source,
        pre_state=cap['state'],action=action,prediction=prediction,
        realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_stream_sequence=envelope['sequence'],event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest(),
        durable_admission=admission,preparation=preparation)
    store.append('training','SAFE_FALLBACK_EVENT',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,
               completed_step=True,attempted_decision=source=='AUTONOMOUS_POLICY')
    controller.release(receipt)
    memory.reconcile(store)
    return row

def seed_one(ctx,scenario,index,regime,action):
    controller=new_controller(ctx['store'],regime)
    cap=capture(controller,ctx['store'],ctx['memory'],action)
    neutral=dict(next_state=cap['state'],consequence=0)
    return execute(ctx,controller,action,neutral,scenario,f'SEED:{index:02d}' if isinstance(index,int) else index,
                   'OBSERVATION_CONTROLLED',preparation='NEUTRAL_PROTECTED_SEED')

def physical_prefix(ctx,count):
    events=ctx['store'].records['events'][:count]
    return [dict(pre_state=e['record']['receipt']['pre_state'],
        action=e['record']['receipt']['action'],next_state=e['record']['receipt']['next_state'],
        consequence=e['record']['receipt']['realized_consequence'],
        regime=e['record']['external_regime_version'],source=e['record']['action_source'])
        for e in events]

def verify_seed(contexts,spec):
    count=len(spec['seed']);prefixes=[physical_prefix(contexts[arm],count) for arm in ARMS]
    if not all(p==prefixes[0] for p in prefixes):raise RuntimeError('matched protected seed histories differ')
    if any(row['regime']!=regime or row['action']!=action or row['source']!='OBSERVATION_CONTROLLED'
           for row,(regime,action) in zip(prefixes[0],spec['seed'])):
        raise RuntimeError('seed schedule differs')
    if any(len(contexts[arm]['store'].records['events'])!=count for arm in ARMS):
        raise RuntimeError('unexpected predecision event')
    sessions=[contexts[a]['store'].checkpoint['session_id'] for a in ARMS]
    sources=[{e['record']['receipt']['source_identity'] for e in contexts[a]['store'].records['events']}
             for a in ARMS]
    if len(set(sessions))!=len(ARMS) or any(sources[i]&sources[j]
        for i in range(len(ARMS)) for j in range(i)):
        raise RuntimeError('cross-arm receipt source')
    return dict(status='PASS',matched_seed_receipts=prefixes[0],distinct_sessions=True,
                disjoint_sources=True)

def assess(ctx,controller,scenario,decision_index,action):
    started=time.perf_counter();arm=ctx['arm'];memory=ctx['memory']
    state=controller._active.framework.inner.map.current.state
    relation=f'{state}:{action}'
    t=time.perf_counter();grounded=fold(memory.rows(relation));mechanical=time.perf_counter()-t
    base=dict(action=action,relation=relation,grounded_state_kind=grounded['kind'],
        provenance=grounded['receipt_provenance'],model_calls=0,context_tokens=0,
        mechanical_seconds=mechanical,preparation_seconds=0.0,
        established_value=grounded['established_value'],candidate_value=grounded['candidate_value'],
        candidate_count=grounded['candidate_count'],
        established_support=grounded['established_support'],candidate_support=grounded['candidate_support'],
        serialized_grounded_state_bytes=len(canonical(grounded).encode()))
    if arm in ('H_ABSTAIN','H_SAFE') and grounded['kind']=='ESTABLISHED':
        return dict(**base,status='GROUNDED',value=grounded['established_value'],
            source='AUTHENTICATED_RECEIPT_STATE',assessment_seconds=time.perf_counter()-started)
    if arm in ('H_ABSTAIN','H_SAFE') and grounded['kind']=='UNRESOLVED_CHANGE':
        return dict(**base,status='UNRESOLVED',value=None,
            source='AUTHENTICATED_RECEIPT_STATE',assessment_seconds=time.perf_counter()-started)
    if arm=='FORCED_GROUNDED':
        rows=memory.rows(relation);latest=rows[-1] if rows else None
        point=(dict(next_state=latest['realized_next_state'],consequence=latest['realized_consequence'])
               if latest else dict(next_state=state,consequence=0))
        return dict(**base,status='FORCED_POINT',value=point,
            source='LATEST_AUTHENTICATED_RECEIPT' if latest else 'NEUTRAL_COLD_START',
            assessment_seconds=time.perf_counter()-started)
    batch=guarded_prepare(ctx,controller,lambda:prepare_model(ctx,controller,
        f'{scenario}:DECISION:{decision_index}:{arm}',action))
    if not batch['all_valid'] or batch['prediction'] is None:
        raise RuntimeError('invalid frozen model preparation')
    return dict(**{**base,'model_calls':batch['model_calls'],
        'context_tokens':batch['context_tokens'],'preparation_seconds':batch['model_seconds']},
        status='MODEL_GENERALIZATION' if arm in ('H_ABSTAIN','H_SAFE') else 'MODEL_POINT',
        value=batch['prediction'],source='FROZEN_JOINT_MAP_AND_G2_EXACT_RELATION',
        model_call_ids=[p['call_id'] for p in batch['parts']],
        model_retrieved_identities=batch['used_event_identities'],
        assessment_seconds=time.perf_counter()-started)

def decide(ctx,scenario,index,spec):
    started=time.perf_counter();store=ctx['store'];memory=ctx['memory'];memory.reconcile(store)
    controller=new_controller(store,spec['regime'])
    state=controller._active.framework.inner.map.current.state
    pre_count=len(store.records['events']);pre_hash=memory.checkpoint()['event_store_sha256']
    assessments=[assess(ctx,controller,scenario,index,a) for a in spec['candidates']]
    selection=choose(assessments,ctx['arm']);chosen=next((a for a in assessments
        if a['action']==selection['action']),None)
    event=(execute(ctx,controller,chosen['action'],chosen['value'],scenario,
           f'DECISION:{index}', 'AUTONOMOUS_POLICY',preparation=chosen['status'])
           if chosen is not None else None)
    record=dict(arm=ctx['arm'],scenario=scenario,index=index,pre_state=state,
        pre_event_count=pre_count,pre_memory_sha256=pre_hash,
        candidate_actions=list(spec['candidates']),assessments=assessments,
        selected_action=selection['action'],reason=selection['reason'],
        action_justified=selection['action_justified'],
        optimality_established=selection['optimality_established'],
        unresolved_relations=selection['unresolved_relations'],
        realized=None if event is None else event['realized'],
        authorized_event_sequence=None if event is None else event['event_stream_sequence'],
        model_calls=sum(a['model_calls'] for a in assessments),
        context_tokens=sum(a['context_tokens'] for a in assessments),
        mechanical_seconds=sum(a['mechanical_seconds'] for a in assessments),
        decision_seconds=time.perf_counter()-started)
    store.append('training','SAFE_FALLBACK_DECISION',record)
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    return record

def return_to_one(ctx,scenario,decision_index):
    state=ctx['store'].checkpoint['current_state']
    if state==1:return None
    action={2:'RETREAT',0:'ADVANCE'}[state]
    return seed_one(ctx,scenario,f'RETURN:{decision_index}',
                    ctx['store'].checkpoint['external_regime_version'],action)

def perturb(ctx):
    before=snapshot(ctx)
    forged=dict(record=dict(authorization_status='AUTHORIZED'))
    try:ctx['memory'].record(ctx['store'],forged,'REGISTERED_NONCURRENT_ADMISSION')
    except RuntimeError as exc:failure=type(exc).__name__
    else:raise RuntimeError('non-current memory admission unexpectedly accepted')
    after=snapshot(ctx)
    if before!=after:raise RuntimeError('failed operation changed state')
    result=dict(status='PASS',failed_operation='NONCURRENT_UNAUTHORIZED_MEMORY_ADMISSION',
        rejection=failure,no_receipt_or_memory=True,grounded_state_unchanged=True)
    _atomic_write(ctx['root'].parents[1]/'perturbation.json',result)
    return result

def predecision_status(ctx,spec):
    """Read-only decision reconstruction for the unresolved restart fixture."""
    state=ctx['store'].checkpoint['current_state'];assessments=[]
    for action in spec['candidates']:
        relation=f'{state}:{action}';grounded=fold(ctx['memory'].rows(relation))
        if grounded['kind']=='ESTABLISHED':
            assessments.append(dict(action=action,relation=relation,status='GROUNDED',
                value=grounded['established_value']))
        elif grounded['kind']=='UNRESOLVED_CHANGE':
            assessments.append(dict(action=action,relation=relation,status='UNRESOLVED',value=None))
        else:raise RuntimeError('restart status fixture contains unseen relation')
    result=choose(assessments,ctx['arm'])
    return dict(assessments=assessments,selection=result)

def run_stage(output,scenario,stage='single'):
    spec=SCENARIOS[scenario];root=output/'scenarios'/scenario
    contexts={arm:open_arm(root,arm) for arm in ARMS};started=time.perf_counter()
    try:
        if stage!='H2':
            for i,(regime,action) in enumerate(spec['seed'],1):
                for arm in ARMS:seed_one(contexts[arm],scenario,i,regime,action)
            matched=verify_seed(contexts,spec)
            _atomic_write(root/'matched-seed.json',matched)
            if stage=='H1':
                states=snapshot(contexts['H_SAFE'])['grounded_states']
                if states['1:HOLD']['kind']!='UNRESOLVED_CHANGE' or states['1:RETREAT']['kind']!='ESTABLISHED':
                    raise RuntimeError('restart epistemic state differs from registration')
                decision_status={arm:predecision_status(contexts[arm],spec)
                    for arm in ('H_ABSTAIN','H_SAFE')}
                if decision_status['H_ABSTAIN']['selection']['action'] is not None or \
                   decision_status['H_SAFE']['selection']['reason']!='SAFE_GROUNDED_FALLBACK':
                    raise RuntimeError('restart decision status differs from registration')
                checkpoint={arm:snapshot(contexts[arm]) for arm in ARMS}
                _atomic_write(root/'before-restart.json',dict(status='PASS',conditions=checkpoint,
                    decision_status=decision_status))
                return dict(status='COMPLETE',stage=stage,matched_seed=len(spec['seed']))
        else:
            prior=json.loads((root/'before-restart.json').read_text())
            observed={arm:snapshot(contexts[arm]) for arm in ARMS}
            status={arm:predecision_status(contexts[arm],spec)
                for arm in ('H_ABSTAIN','H_SAFE')}
            if observed!=prior['conditions'] or status!=prior['decision_status']:
                raise RuntimeError('fresh-process restart changed durable state or decision status')
            verify_seed(contexts,spec)
            before=status['H_SAFE'];perturbation=perturb(contexts['H_SAFE'])
            after=predecision_status(contexts['H_SAFE'],spec)
            if before!=after:raise RuntimeError('failed operation changed fallback eligibility')
            _atomic_write(root/'restart.json',dict(status='PASS',
                exact_durable_files_and_grounded_states=True,
                exact_decision_status_and_fallback_eligibility=True,
                conditions=observed,decision_status=status,perturbation=perturbation))
        decisions={arm:[decide(contexts[arm],scenario,1,spec)] for arm in ARMS}
        if spec.get('probe'):
            probe_regime,probe_action=spec['probe']
            for arm in ARMS:
                return_to_one(contexts[arm],scenario,1)
                seed_one(contexts[arm],scenario,'PROBE',probe_regime,probe_action)
                return_to_one(contexts[arm],scenario,2)
                decisions[arm].append(decide(contexts[arm],scenario,2,
                    {**spec,'regime':probe_regime}))
            for arm in ('H_ABSTAIN','H_SAFE'):
                second=decisions[arm][1]
                candidate=next(a for a in second['assessments'] if a['action']==probe_action)
                if candidate['status']!='GROUNDED':
                    raise RuntimeError('distinguishing receipt did not resolve relation')
        result=dict(status='COMPLETE',scenario=scenario,stage=stage,
            matched_seed=len(spec['seed']),decisions=decisions,
            conditions={arm:snapshot(contexts[arm]) for arm in ARMS},
            wall_seconds=time.perf_counter()-started)
        _atomic_write(root/'stage-complete.json',result)
        return dict(status='COMPLETE',scenario=scenario,decisions={a:len(v) for a,v in decisions.items()},
                    wall_seconds=result['wall_seconds'])
    except Exception as exc:
        _atomic_write(root/'stop.json',dict(status='INVALID',stage=stage,error=repr(exc)))
        raise
    finally:
        for ctx in contexts.values():close_arm(ctx)

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('scenario');p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stage',default='single');a=p.parse_args()
    print(json.dumps(run_stage(a.output,a.scenario,a.stage),sort_keys=True))
