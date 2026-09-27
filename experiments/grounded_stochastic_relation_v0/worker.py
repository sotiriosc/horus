"""Matched protected executions of prospectively fixed receipt outcomes."""
from argparse import ArgumentParser
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path
import json, time
from horus.live import SessionStore, RegimeEpisodeWorld, Publication, _atomic_write, _plain
from horus.core import BoundPredictionMap, digest, unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical, file_hash
from experiments.grounded_uncertainty_state_v0.harness import capture, prepare_model
from experiments.grounded_uncertainty_state_v0.uncertainty import fold as d_fold, predict as d_predict
from experiments.grounded_uncertainty_state_v0.worker import load_clients, new_controller
from .empirical import fold as e_fold, point as e_point
from .protocol import ARMS, SCHEDULES, RESTART_AFTER, MODEL_PROBES

class ScheduledWorld(RegimeEpisodeWorld):
    def __init__(self,state,consequence):
        super().__init__(state,'A');self.scheduled_consequence=consequence
    def execute(self,epoch,transaction_id,action):
        actual=super().execute(epoch,transaction_id,action)
        if self.scheduled_consequence is not None:
            actual=replace(actual,consequence=self.scheduled_consequence)
            self.fixture.last_actual=actual
        return actual

def open_arm(root,arm,create):
    path=root/'work'/arm;store=SessionStore(path/'session',not create)
    memory=ModernMemory(path/'memory.sqlite3',create);memory.reconcile(store)
    joint,g2,_=load_clients('M') if arm=='M' else (None,None,None)
    return dict(arm=arm,path=path,store=store,memory=memory,joint=joint,
                g2=None if g2 is None else g2['G2'])

def snapshot(ctx):
    path=ctx['path'];store=ctx['store'];memory=ctx['memory'];memory.reconcile(store)
    return dict(files={name:file_hash(path/'session'/name) for name in
        ('authority.key','checkpoint.json','events.jsonl','model-calls.private.jsonl','training-records.jsonl')},
        memory=memory.checkpoint(),current_state=store.checkpoint['current_state'],
        events=len(store.records['events']),states={r:dict(D=d_fold(memory.rows(r)),E=e_fold(memory.rows(r)))
            for r in ('1:HOLD','2:HOLD')})

def physical(ctx):
    return [dict(state=e['record']['receipt']['pre_state'],action=e['record']['receipt']['action'],
        consequence=e['record']['receipt']['realized_consequence'],
        next_state=e['record']['receipt']['next_state']) for e in ctx['store'].records['events']]

def verify(contexts,specs,count):
    histories=[physical(contexts[a]) for a in ARMS]
    if not all(len(h)==count and h==histories[0] for h in histories):
        raise RuntimeError('INVALID: unmatched protected receipts')
    for row,spec in zip(histories[0],specs[:count]):
        if row['state']!=spec['state'] or row['action']!=spec['action'] or (spec['consequence'] is not None
            and row['consequence']!=spec['consequence']):raise RuntimeError('INVALID: schedule mismatch')
    sessions=[contexts[a]['store'].checkpoint['session_id'] for a in ARMS]
    sources=[{e['record']['receipt']['source_identity'] for e in contexts[a]['store'].records['events']} for a in ARMS]
    if len(set(sessions))!=3 or any(sources[i]&sources[j] for i in range(3) for j in range(i)):
        raise RuntimeError('INVALID: shared receipt authority')

def prepare(ctx,controller,schedule,index,spec):
    store=ctx['store'];memory=ctx['memory'];action=spec['action'];state=spec['state']
    cap=capture(controller,store,memory,action)
    if cap['state']!=state:raise RuntimeError('INVALID: wrong scheduled state')
    relation=f'{state}:{action}';start=time.perf_counter()
    d=d_fold(memory.rows(relation));e=e_fold(memory.rows(relation))
    fold_seconds=time.perf_counter()-start
    model=None
    if ctx['arm']=='M' and action=='HOLD' and index in MODEL_PROBES[schedule]:
        model=prepare_model(ctx,controller,f'{schedule}:{index}',action)
        if not model['all_valid']:raise RuntimeError('INVALID: model preparation failed')
        forecast=model['prediction']
    elif ctx['arm']=='D':forecast=d_predict(memory,relation,state)['point']
    elif ctx['arm']=='E':forecast=e_point(e,state)
    else:forecast=dict(next_state=state,consequence=0)
    return dict(capture=cap,forecast=forecast,D=d,E=e,fold_seconds=fold_seconds,
        model=model,model_calls=0 if model is None else model['model_calls'],
        context_tokens=0 if model is None else model['context_tokens'])

def publish(ctx,controller,schedule,index,spec,batch):
    store=ctx['store'];memory=ctx['memory'];cap=batch['capture'];value=batch['forecast']
    core=controller._active.framework.inner
    core.map=BoundPredictionMap(unwrap_map(core.map),Prediction(cap['epoch'],cap['transaction_id'],
        cap['state'],spec['action'],value['next_state'],value['consequence']))
    pending=controller.begin_step(spec['action'])
    if getattr(pending,'action',None)!=spec['action'] or controller._source.reader().current() is not None:
        raise RuntimeError('INVALID: protected preparation')
    receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
    if not result.committed or not result.continued or result.status.value!='AUTHORIZED':
        raise RuntimeError('INVALID: unauthorized receipt')
    core=controller._active.framework.inner
    if controller._active.framework.packages[-1].receipt is not receipt:
        raise RuntimeError('INVALID: original receipt lost')
    receipt_value=_plain(asdict(receipt));relation=f"{cap['state']}:{spec['action']}"
    event=dict(session_id=store.checkpoint['session_id'],study='GROUNDED_STOCHASTIC_RELATION_V0',
        schedule=schedule,index=index,phase=spec['phase'],action_source='OBSERVATION_CONTROLLED',
        execution_kind='OBSERVATION_CONTROLLED_EXECUTION',receipt=receipt_value,
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=digest(receipt_value),
        authorization_status=result.status.value,authorization_reason=result.reason,
        memory_record=_plain(asdict(core.memory.records[-1])),
        source_scope=dict(runtime_index=store.checkpoint['runtime_index'],source_identity=receipt.source_identity),
        external_regime_version='A',regime_model_visible=False)
    envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
    admission=memory.record(store,envelope,f'{schedule}:{ctx["arm"]}:{index}')
    memory.reconcile(store)
    after_d=d_fold(memory.rows(relation));after_e=e_fold(memory.rows(relation))
    row=dict(arm=ctx['arm'],schedule=schedule,index=index,phase=spec['phase'],relation=relation,
        prediction=value,realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),
        D_before=batch['D'],E_before=batch['E'],D_after=after_d,E_after=after_e,
        receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],
        event_stream_sequence=envelope['sequence'],event_stream_head_sha256=sha256(canonical(envelope).encode()).hexdigest(),
        durable_admission=admission,model_calls=batch['model_calls'],context_tokens=batch['context_tokens'],
        model_ids=[] if batch['model'] is None else [p['call_id'] for p in batch['model']['parts']],
        fold_seconds=batch['fold_seconds'],serialized_e_bytes=len(canonical(after_e).encode()))
    store.append('training','STOCHASTIC_RELATION_SCORED_EVENT',row)
    store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,completed_step=True)
    controller.release(receipt)
    return row

def perturb(ctx):
    before=snapshot(ctx)
    try:ctx['memory'].record(ctx['store'],dict(record=dict(authorization_status='AUTHORIZED')),
                             'REGISTERED_NONCURRENT_ADMISSION')
    except RuntimeError as exc:rejection=type(exc).__name__
    else:raise RuntimeError('INVALID: noncurrent admission accepted')
    if snapshot(ctx)!=before:raise RuntimeError('INVALID: perturbation changed experience')
    return dict(status='PASS',operation='NONCURRENT_UNAUTHORIZED_MEMORY_ADMISSION',
                rejection=rejection,no_receipt_or_memory=True)

def stage(output,schedule,part):
    specs=SCHEDULES[schedule];root=output/'schedules'/schedule
    create=part!='G2';contexts={a:open_arm(root,a,create) for a in ARMS}
    start=time.perf_counter()
    try:
        if part=='G2':
            prior=json.loads((root/'before-restart.json').read_text())['conditions']
            current={a:snapshot(contexts[a]) for a in ARMS}
            if current!=prior:raise RuntimeError('INVALID: restart changed durable files or state')
            for a in ARMS:
                states=current[a]['states']
                if states['1:HOLD']['E']['kind']!='POSSIBLE_REGIME_CHANGE' or states['2:HOLD']['E']['kind']!='VARIABLE_RELATION':
                    raise RuntimeError('INVALID: wrong restart states')
            _atomic_write(root/'restart.json',dict(status='PASS',exact_file_and_state_match=True,
                supporting_receipts={a:current[a]['states'] for a in ARMS}))
            perturbation=perturb(contexts['E'])
            _atomic_write(root/'perturbation.json',perturbation)
            begin=RESTART_AFTER;end=len(specs)
        else:
            begin=0;end=RESTART_AFTER if part=='G1' else len(specs)
        verify(contexts,specs,begin)
        rows=[]
        for index in range(begin,end):
            spec=specs[index];controllers={};batches={}
            for arm in ARMS:
                ctx=contexts[arm];controller=new_controller(ctx['store'],'A')
                controller._active=Publication(ScheduledWorld(spec['state'],spec['consequence']),
                                                controller._active.framework)
                controllers[arm]=controller
                batches[arm]=prepare(ctx,controller,schedule,index,spec)
            for arm in ARMS:rows.append(publish(contexts[arm],controllers[arm],schedule,index,spec,batches[arm]))
            verify(contexts,specs,index+1)
            print(f'{schedule} {index+1}/{len(specs)}',flush=True)
        conditions={a:snapshot(contexts[a]) for a in ARMS}
        result=dict(status='COMPLETE',schedule=schedule,part=part,rows=rows,
            conditions=conditions,wall_seconds=time.perf_counter()-start)
        _atomic_write(root/('before-restart.json' if part=='G1' else 'complete.json'),result)
        return dict(status='COMPLETE',schedule=schedule,part=part,events=len(rows))
    except Exception as exc:
        _atomic_write(root/'stop.json',dict(status='INVALID',part=part,error=repr(exc)))
        raise
    finally:
        for ctx in contexts.values():ctx['memory'].close();ctx['store'].close()

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('schedule',choices=SCHEDULES);p.add_argument('--part',default='single');p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();print(json.dumps(stage(a.output,a.schedule,a.part),sort_keys=True))
