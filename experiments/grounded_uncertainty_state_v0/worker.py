from argparse import ArgumentParser
import json
from hashlib import sha256
from pathlib import Path
import time
from horus.live import SessionStore, LiveController, ModelClient, _atomic_write
from horus.grounded_learning import QwenConsequenceClient
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, file_hash
from .atomic import flush,guarded_prepare,publish_snapshot,verify_triple
from .harness import prepare_model,prepare_mechanical,publish
from .protocol import ARMS,SCHEDULES,RESTART,PERTURBATION,G2_ADAPTER
from .uncertainty import fold


def load_clients(condition):
    if condition!='M':raise RuntimeError('model may only serve M')
    artifact=sha256(G2_ADAPTER.read_bytes()).hexdigest()
    identity=dict(specialist_id='G2',generation=2,artifact_sha256=artifact,
        global_lifecycle_status='ACTIVE',routing_eligibility='BASELINE')
    specialist=QwenConsequenceClient(G2_ADAPTER,device='cuda',model_identity=identity)
    specialist.model_id=f'modern-G2:{artifact}'
    return ModelClient(),{'G2':specialist},None


def new_controller(store,regime):
    current=store.checkpoint.get('external_regime_version')
    store.configure_regime(regime,allow_transition=current is not None and current!=regime)
    epoch,source=store.begin_runtime()
    return LiveController(source,store.checkpoint['current_state'],epoch,regime)


def open_arm(schedule_root,arm):
    root=schedule_root/'work'/arm
    store=SessionStore(root/'session',True)
    memory=ModernMemory(root/'memory.sqlite3',False)
    joint,g2,_=load_clients('M') if arm=='M' else (None,None,None)
    return dict(arm=arm,root=root,store=store,memory=memory,
                joint=joint,g2=None if g2 is None else g2['G2'])


def close_arm(context):
    context['memory'].close();context['store'].close()


def checkpoint(context):
    root=context['root'];store=context['store'];memory=context['memory']
    return dict(session_files_sha256={name:file_hash(root/'session'/name) for name in
        ('authority.key','checkpoint.json','events.jsonl',
         'model-calls.private.jsonl','training-records.jsonl')},
        memory=memory.checkpoint(),current_state=store.checkpoint['current_state'],
        events=len(store.records['events']),calls=len(store.records['calls']),
        training=len(store.records['training']),
        grounded_state=fold(memory.rows('1:HOLD')) if context['arm']=='U' else None)


def run_stage(output,stage):
    schedule_name='SUSTAINED' if stage in ('SUSTAINED1','SUSTAINED2') else stage
    schedule_root=output/'schedules'/schedule_name
    specs=SCHEDULES[schedule_name]
    contexts={arm:open_arm(schedule_root,arm) for arm in ARMS}
    started=time.perf_counter()
    try:
        restart=None;perturbation=None
        if stage=='SUSTAINED1':
            publish_snapshot(schedule_root,contexts,'initial',())
            todo=specs[:4]
        elif stage=='SUSTAINED2':
            prior=json.loads((schedule_root/'before-restart.json').read_text())
            observed={arm:checkpoint(contexts[arm]) for arm in ARMS}
            if observed!=prior['conditions']:
                raise RuntimeError('INVALID: fresh-process restart hash mismatch')
            verify_triple(contexts,specs[:4])
            if observed['U']['grounded_state']['kind']!='UNRESOLVED_CHANGE' or observed['U']['grounded_state']['candidate_count']!=1:
                raise RuntimeError('INVALID: restart did not recover unresolved U state')
            restart=dict(status='PASS',exact_file_and_memory_hash_match=True,
                         exact_uncertainty_state_and_supporting_receipt_match=True,
                         conditions=observed)
            # Fresh runtime boundary for every arm; none executes an event.
            perturb_controllers={arm:new_controller(contexts[arm]['store'],'B') for arm in ARMS}
            before={arm:(len(ctx['store'].records['events']),ctx['memory'].checkpoint()['event_store_sha256'],
                        fold(ctx['memory'].rows('1:HOLD')) if arm=='U' else None)
                    for arm,ctx in contexts.items()}
            batch=guarded_prepare(contexts['M'],perturb_controllers['M'],
                lambda:prepare_model(contexts['M'],perturb_controllers['M'],
                    'SUSTAINED:PERTURBATION','HOLD',perturb=True))
            mechanical={arm:guarded_prepare(contexts[arm],perturb_controllers[arm],
                lambda arm=arm:prepare_mechanical(contexts[arm],perturb_controllers[arm],arm,'HOLD'))
                for arm in ('L','R3','U')}
            joint,g2=batch['parts']
            if (batch['all_valid'] or joint['outcome']!='MODEL_OUTPUT_INVALID' or
                joint['error'] not in ('JSONDecodeError','ValueError') or g2['outcome']!='VALID' or
                any(not row['all_valid'] for row in mechanical.values())):
                raise RuntimeError('INVALID: perturbation did not fail closed or transport failed')
            after={arm:(len(ctx['store'].records['events']),ctx['memory'].checkpoint()['event_store_sha256'],
                        fold(ctx['memory'].rows('1:HOLD')) if arm=='U' else None)
                   for arm,ctx in contexts.items()}
            if after!=before:raise RuntimeError('INVALID: perturbation changed protected experience')
            perturbation=dict(status='PASS',model_parser_rejected=True,
                no_receipt_or_memory=True,mechanical_learning=False,
                model_calls=2,context_tokens=batch['context_tokens'],
                model_seconds=batch['model_seconds'],logical_call_ids=[p['call_id'] for p in batch['parts']],
                transport_distinct=True)
            _atomic_write(schedule_root/'perturbation.json',perturbation)
            todo=specs[4:]
        elif stage in ('ANOMALY','EXCURSION','NOISE_THEN_CHANGE'):
            publish_snapshot(schedule_root,contexts,'initial',())
            todo=specs
        else:raise RuntimeError('unknown worker stage')
        controllers={};prior_regime={};rows=[]
        for spec in todo:
            active={};batches={}
            for arm in ARMS:
                context=contexts[arm]
                if arm not in controllers or prior_regime[arm]!=spec['regime']:
                    controllers[arm]=new_controller(context['store'],spec['regime'])
                    prior_regime[arm]=spec['regime']
                controller=controllers[arm];active[arm]=controller
                forecast=(lambda ctx=context,c=controller:
                    prepare_model(ctx,c,spec['observation_id'],spec['action'])) if arm=='M' else (
                    lambda ctx=context,c=controller,a=arm:prepare_mechanical(ctx,c,a,spec['action']))
                batches[arm]=guarded_prepare(context,controller,forecast)
            if not all(b['all_valid'] for b in batches.values()):
                _atomic_write(schedule_root/'stop.json',dict(status='PREPARATION_FAILED',
                    observation_id=spec['observation_id'],
                    matched_before=verify_triple(contexts,specs[:spec['event']-1])))
                publish_snapshot(schedule_root,contexts,
                    f'failed-{spec["event"]:02d}',specs[:spec['event']-1])
                raise RuntimeError('PREPARATION_FAILED')
            verify_triple(contexts,specs[:spec['event']-1])
            event_rows={}
            for arm in ARMS:
                event_rows[arm]=publish(contexts[arm],active[arm],batches[arm],spec)
            verify_triple(contexts,specs[:spec['event']])
            publish_snapshot(schedule_root,contexts,f'event-{spec["event"]:02d}',
                             specs[:spec['event']])
            rows.append(event_rows)
            print(f'schedule={schedule_name} event={spec["event"]}/{len(specs)}',flush=True)
        prefix=specs[:4] if stage=='SUSTAINED1' else specs
        publish_snapshot(schedule_root,contexts,f'checkpoint-{stage}',prefix)
        result=dict(status='COMPLETE',stage=stage,schedule=schedule_name,
            conditions={arm:checkpoint(contexts[arm]) for arm in ARMS},
            rows=rows,restart=restart,perturbation=perturbation,
            wall_seconds=time.perf_counter()-started)
        _atomic_write(schedule_root/('before-restart.json' if stage=='SUSTAINED1'
                                     else f'stage-{stage.lower()}.json'),result)
        return dict(status='COMPLETE',stage=stage,events=len(rows),
                    wall_seconds=result['wall_seconds'])
    except Exception as exc:
        for context in contexts.values():flush(context['store'])
        if not (schedule_root/'stop.json').exists():
            _atomic_write(schedule_root/'stop.json',dict(status='INVALID',
                stage=stage,error=repr(exc)))
        raise
    finally:
        for context in contexts.values():close_arm(context)

if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('stage',choices=('SUSTAINED1','SUSTAINED2','ANOMALY','EXCURSION','NOISE_THEN_CHANGE'))
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run_stage(args.output,args.stage),sort_keys=True))
