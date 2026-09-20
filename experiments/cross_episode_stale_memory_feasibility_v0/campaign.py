"""Frozen small histories, native stale predictions, provenance and FIFO controls."""
from copy import deepcopy
from dataclasses import asdict,replace
from pathlib import Path
import json
from unittest.mock import patch
from experiments.cross_episode_initialization_boundary_v1.campaign import step,snap,provenance,boundary_observer,encoded
from experiments.cross_episode_initialization_boundary_v1.projection import map_payload,explorer_payload,serialize
from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import observe
from experiments.model_proposal_role_composition_v2.protocol import schedule
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
from .fixture import Controller,target_law
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='eed191991087b0b47990091faf2a2cf156f40e87'
A='A — CROSS-EPISODE STALE-MEMORY FIXTURE FEASIBLE'
B='B — CROSS-EPISODE AUTHORITY / HISTORY FAILURE'
C='C — NOT ESTABLISHED'
OLD=('ADVANCE','RETREAT','ADVANCE')
NEW=('ADVANCE','RETREAT','ADVANCE','RETREAT')
GATES=('both_old_records_authentic','trusted_initialization','old_records_unchanged','external_change_without_history_rewrite',
 'first_contradiction_authorized','second_contradiction_authorized','control_histories_correct','changed_histories_correct',
 'current_probe_state_correct','cross_epoch_chronology','no_contradiction_rejection','commits_equal_receipts',
 'zero_protected_false_accepts','zero_receipt_prediction_history_rewrites','bounds_hold','exact_replay','historical_preservation')

class HistoryFailure(RuntimeError):pass

def check(condition,reason):
    if not condition:raise HistoryFailure(reason)
def plain(v):return json.loads(encoded(v))
def frozen():
    reg=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,d in reg['sha256'].items():assert file_digest(ROOT/n)==d,n
    return reg

def audit(c,authentic,executions):
    f=c._active.framework;f.assert_bounds();records=f.inner.memory.records;pairs=f.inner.pairs.decisions;packages=f.packages
    check(len(records)==len(pairs)==len(packages),'detached retained rings')
    rows=[]
    for r,p,q in zip(records,pairs,packages):
        receipt=q.receipt;actual=executions[receipt.identity()]
        check(receipt is authentic[receipt.identity()],'receipt object substitution')
        check(receipt.binding()[:6]==(actual['epoch'],actual['transaction_id'],actual['pre_state'],actual['action'],actual['next_state'],actual['consequence']),'receipt differs from actual execution')
        check((r.epoch,r.transaction_id,r.pre_state,r.action,r.next_state,r.consequence)==receipt.binding()[:6],'Memory differs from receipt')
        check(q.package_id==receipt.identity() and q.pair_decision_id==p.pair_decision_id==r.pair_decision_id and f.inner.memory.matches(r,p),'pair/package binding detached')
        rows.append(dict(memory=asdict(r),pair=asdict(p),package_id=q.package_id,receipt=asdict(receipt),actual_execution=actual,original_receipt_object=True,full_binding_verified=True))
    check(len({q.receipt.identity() for q in packages})==len(packages),'receipt identity collision')
    check(len({(r.epoch,r.transaction_id) for r in records})==len(records),'epoch/transaction collision')
    return plain(rows)

def execute(c,action,authentic,executions):
    originals={k:asdict(v) for k,v in authentic.items()}
    with observe(True) as observed:
        try:row=step(c,action,authentic)
        except AssertionError as exc:raise HistoryFailure('ordinary authenticated publication failed') from exc
    receipt=c._active.framework.packages[-1].receipt
    executions[receipt.identity()]=asdict(c._active.world.last_actual)
    check(all(asdict(authentic[k])==v for k,v in originals.items()),'historical receipt rewritten')
    check(row['pending']['prediction']==row['after']['prediction_at_begin'],'pre-execution prediction rewritten')
    if row['pending']['proposal_pre_state']==0 and action=='ADVANCE':
        check((row['pending']['prediction']['next_state'],row['pending']['prediction']['consequence'])==(1,1),'old target prediction not latched before execution')
    row.update(observed_recovery=observed,full_provenance=audit(c,authentic,executions),actual_execution=executions[receipt.identity()],
        receipt_rewritten=False,prediction_rewritten=False,historical_receipts_rewritten=False)
    return row

def stage(c,name,authentic,executions,changed):
    before=snap(c);check(before['world_state']==before['protected']['map']['state']==0,'current state/history conflation')
    expected=[1,1]+([(-1 if changed else 1)]*dict(P0=0,P1=1,P2=2)[name])
    ids=[(1001,1),(1001,3),(1002,1),(1002,3)][:len(expected)]
    views=[]
    for d in schedule():
        mapping=d['mapping'];view=c.projections(mapping);rows=view['Map']['ADVANCE']['VERIFIED_CHRONOLOGICAL_HISTORY']
        check([r['consequence'] for r in rows]==expected,'target chronology/consequences incorrect')
        check([(r['epoch'],r['transaction_id']) for r in rows]==ids,'cross-epoch projection identity incorrect')
        check(all(set(r)=={'epoch','transaction_id','surface_action','next_state','consequence'} and r['next_state']==1 for r in rows),'projection schema changed')
        values={mapping[r['action']]:r['verified_outcomes'] for r in view['Explorer']['actions']}
        check(values=={'ADVANCE':expected,'HOLD':'UNTRIED','RETREAT':'UNTRIED'},'stale UNKNOWN contradiction')
        check(view['Map']['HOLD']['VERIFIED_CHRONOLOGICAL_HISTORY']==[] and view['Map']['RETREAT']['VERIFIED_CHRONOLOGICAL_HISTORY']==[],'untouched exact pairs not UNKNOWN')
        views.append(dict(family=d['family'],mapping_index=d['mapping_index'],mapping=mapping,Map=view['Map']['ADVANCE'],Explorer=view['Explorer']))
    check(snap(c)==before,'projection mutated state/history')
    check('UNTRIED' not in encoded(before['protected']),'absence marker stored as event')
    return plain(dict(stage=name,snapshot=before,provenance=audit(c,authentic,executions),views=views,target_consequences=expected,target_identities=ids,current_state=0))

def initialize(name):
    c=Controller(name);authentic={};executions={};rows=[execute(c,a,authentic,executions) for a in OLD]
    before=snap(c);packages=list(c._active.framework.packages);source=c._source
    check(before['world_state']==before['protected']['map']['state']==1,'episode 1 did not end nonzero')
    with boundary_observer() as effects:boundary=c.start_episode(1002,0)
    after=snap(c)
    check(all(v==0 for v in effects.values()),'reset produced execution/receipt authority activity')
    check(before['source_event_count']==after['source_event_count']==3 and before['world_executions']==after['world_executions']==3,'reset minted an event')
    check(after['world_state']==after['protected']['map']['state']==0 and after['epoch']==1002,'trusted fresh initialization failed')
    check(all(before['protected'][k]==after['protected'][k] for k in ('memory','pairs','packages','commits')),'reset rewrote history')
    check(c._source is source and c._registered_source is source and all(x is y for x,y in zip(packages,c._active.framework.packages)),'source/package identity changed across reset')
    return c,authentic,executions,rows,dict(before=before,after=after,boundary=boundary,effects=effects,same_source_lifetime=True,original_packages_retained=True)

def intervene(c):
    before=snap(c);check(before['epoch']==1002 and before['world_state']==0,'intervention timing incorrect')
    with boundary_observer() as effects:c._active.world.change_target()
    after=snap(c);check(before==after and all(v==0 for v in effects.values()),'world-law mutation rewrote history or generated pseudo-event')
    return dict(before=before,after=after,effects=effects,target_consequence=-1,external_intervention_count=c._active.world.intervention_count,
        after_episode_initialization=True,before_first_episode2_event=True)

def arm(changed):
    name='STALE_MEMORY_SOURCE_'+('B' if changed else 'A')
    c,authentic,executions,rows,boundary=initialize(name)
    old=deepcopy(boundary['after']['protected']);stages={'P0':stage(c,'P0',authentic,executions,changed)}
    law_change=intervene(c) if changed else None
    for i,action in enumerate(NEW):
        rows.append(execute(c,action,authentic,executions))
        if i in (1,3):stages['P1' if i==1 else 'P2']=stage(c,'P1' if i==1 else 'P2',authentic,executions,changed)
        check(all(snap(c)['protected'][k][:3]==old[k] for k in ('memory','pairs','packages')),'old records changed before ordinary eviction')
    primary=snap(c);check(len(primary['protected']['memory'])==7 and primary['evictions']==0,'primary exceeded registered bound')
    primary_rows=deepcopy(rows)
    # Separate capacity/FIFO control only after frozen P2 was captured.
    rows.append(execute(c,'HOLD',authentic,executions));eight=snap(c)
    check(len(eight['protected']['memory'])==8 and eight['evictions']==0,'eighth event unexpectedly evicted')
    known=c.projections(schedule()[0]['mapping'])
    check(known['Explorer']['actions'][1]['verified_outcomes']==[0],'UNKNOWN did not disappear after authentic HOLD')
    rows.append(execute(c,'HOLD',authentic,executions));nine=snap(c)
    check(len(nine['protected']['memory'])==8 and nine['evictions']==1,'ordinary ninth FIFO incorrect')
    check(all(nine['protected'][k][:-1]==eight['protected'][k][1:] for k in ('memory','pairs','packages')),'paired FIFO rotation detached identity')
    check([r['receipt']['event_id'] for r in rows]==list(range(1,10)),'source event IDs reset or collided')
    return plain(dict(boundary=boundary,intervention=law_change,stages=stages,primary_rows=primary_rows,primary_end=primary,
        eviction=dict(eighth=rows[7],ninth=rows[8],at_eight=eight,at_nine=nine,evicted_record=eight['protected']['memory'][0],
            evicted_package=eight['protected']['packages'][0],ordinary_fifo=True,unknown_to_known_HOLD=True),
        source_identity=name,external_interventions=c._active.world.intervention_count,all_receipts_original=True))

def negative_controls():
    out=[]
    for name in ('old_receipt','equal_content_copy','old_consequence_fake_receipt','old_consequence_bindings'):
        c,authentic,executions,_,_=initialize('STALE_NEGATIVE_'+name);intervene(c)
        old=c._active.framework.packages[0].receipt;c.begin_step('ADVANCE');receipt=c.execute_pending()
        check(receipt.realized_consequence==-1,'negative fixture missing authentic changed event')
        package=evidence(old if name=='old_receipt' else replace(receipt) if name=='equal_content_copy' else replace(receipt,realized_consequence=1) if name=='old_consequence_fake_receipt' else receipt)
        if name=='old_consequence_bindings':
            a=list(package.a);a[5]=1;package=replace(package,a=tuple(a),b=tuple(a))
        before=snap(c)['protected'];result=c.submit_package(package);after=snap(c)['protected']
        check(not result.committed and not result.continued and before==after,'protected false accept/substitution')
        c.release(receipt)
        out.append(dict(case=name,actual=asdict(c._active.world.last_actual),original_receipt=asdict(receipt),supplied_package=asdict(package),
            result=asdict(result),rejected=True,protected_unchanged=True,before=before,after=after))
    return plain(out)

def law_scope():
    rows=[]
    for state in range(4):
        for action in ('ADVANCE','HOLD','RETREAT'):
            original=TrueWorldOracle(state).execute(1002,1,action);altered=target_law(original,-1)
            expected=replace(original,consequence=-1) if (state,action)==(0,'ADVANCE') else original
            check(altered==expected,'unrelated world relation changed')
            rows.append(dict(state=state,action=action,original=asdict(original),after=asdict(altered),only_registered_target_changed=True))
    return rows

def difference_paths(a,b,prefix=''):
    if type(a) is not type(b):return [prefix]
    if isinstance(a,dict):
        return [path for k in sorted(set(a)|set(b)) for path in ([prefix+'.'+k] if k not in a or k not in b else difference_paths(a[k],b[k],prefix+'.'+k))]
    if isinstance(a,list):
        if len(a)!=len(b):return [prefix+'.length']
        return [p for i,(x,y) in enumerate(zip(a,b)) for p in difference_paths(x,y,prefix+f'[{i}]')]
    return [] if a==b else [prefix]

def matching(control,changed):
    differences=[]
    for name in ('P0','P1','P2'):
        a,b=control['stages'][name],changed['stages'][name]
        check(len(a['snapshot']['protected']['memory'])==len(b['snapshot']['protected']['memory']),'unmatched depth')
        for x,y in zip(a['views'],b['views']):
            if name=='P0':check(x==y,'P0 projections not identical')
            cleaned=deepcopy(y)
            for row in cleaned['Map']['VERIFIED_CHRONOLOGICAL_HISTORY']:row['consequence']=1
            # For Map, only the actual post-boundary target consequences differ.
            check(cleaned['Map']==x['Map'],'unmatched Map field beyond target consequence')
        differences.append(dict(stage=name,Memory_length=len(a['snapshot']['protected']['memory']),current_state=0,
            target_identities=a['target_identities'],source_identities_differ=True,Map_projections_identical=name=='P0',
            only_Map_semantic_difference='none' if name=='P0' else 'authenticated episode-1002 consequence',
            actual_snapshot_difference_paths=difference_paths(a['snapshot'],b['snapshot'])))
    for x,y in zip(control['primary_rows'],changed['primary_rows']):
        ra,rb=x['receipt'],y['receipt']
        check(all(ra[k]==rb[k] for k in ('epoch','transaction_id','event_id','pre_state','action','next_state')),'event identity shape/sequence differs')
    return differences

def run():
    frozen()
    with patch('socket.socket',side_effect=AssertionError('ZERO MODEL CALLS: network forbidden')) as network:
        control=arm(False);changed=arm(True);negative=negative_controls();scope=law_scope();matched=matching(control,changed)
        check(network.call_count==0,'network attempt')
    gates={k:True for k in GATES};gates['exact_replay']=gates['historical_preservation']=None
    primary=[*control['primary_rows'],*changed['primary_rows']]
    recovery={name:sum(e['kind']=='recovery_state_proposal' for row in armdata['primary_rows'] for e in row['observed_recovery']) for name,armdata in [('CONTROL',control),('CHANGED',changed)]}
    details=dict(CONTROL=control,CHANGED=changed,negative_controls=negative,world_law_scope=scope,matching=matched)
    result=dict(study='cross-episode-stale-memory-feasibility-v0',parent=PARENT,actual_model_calls=0,network_attempts=0,
        classification=C,eligible_classification=A,status='AWAITING_EXACT_REPLAY_AND_PRESERVATION',requirements=gates,
        primary_commits=len(primary),primary_commits_per_arm=7,primary_Memory_size=7,primary_evictions=0,
        stages={armname:{k:dict(target_consequences=v['target_consequences'],target_identities=v['target_identities'],current_state=v['current_state'],
            Memory_length=len(v['snapshot']['protected']['memory'])) for k,v in ar['stages'].items()} for armname,ar in [('CONTROL',control),('CHANGED',changed)]},
        native_state_Recovery_calls=recovery,native_measurement_Recovery_calls=sum(e['kind']=='recovery_measurement' for row in primary for e in row['observed_recovery']),
        target_stale_prediction=[1,1],changed_target_receipt=[1,-1],prediction_receipt_mismatches=2,
        protected_false_accepts=0,receipt_mismatch_accepts=0,actual_execution_mismatch_accepts=0,
        historical_rewrites=0,prediction_rewrites=0,receipt_rewrites=0,contradiction_rejections=0,
        negative_controls=len(negative),negative_controls_rejected=sum(r['rejected'] for r in negative),
        separate_fifo_controls=2,fifo_evictions=2,law_scope_cases=len(scope),projection_mappings=12,
        bounds=dict(memory=8,pairs=8,packages=8,trace=24,source_lifetime=24,epochs=2),
        receipt_equality_across_systems=False,metadata_differences={r['stage']:r['actual_snapshot_difference_paths'] for r in matched},
        claim_scope='Authenticated contradictory histories across a trusted simulator initialization; no model behavior tested.')
    return result,plain(details)
