"""Preregistered paired protected executions; no action-model client is created."""
from pathlib import Path
from hashlib import sha256
from contextlib import contextmanager
from itertools import permutations
from dataclasses import asdict, replace
import json, os, subprocess, sys
from horus.core import digest, BoundPredictionMap, unwrap_map
from horus.live import SessionStore, Publication, _plain, _atomic_write
from grounded_state import AuthenticatedMemory, RelationKey, RelationType, derive_relation_state
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical, file_hash
from experiments.grounded_autonomous_agent_v0_2.worker import state_view
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as protected
from experiments.empirical_evidence_acquisition_evaluation_v0 import worker as previous
from experiments.empirical_evidence_acquisition_proposal_v0 import candidate as frozen
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence

ROOT=Path(__file__).resolve().parents[2]
PUBLIC=ROOT/'research/empirical-evidence-acquisition-replication-v0'
SHA='fcef478a02beb69a1d29988c5ce12929ad2ba077591131e0dcd114e7ccab99b4'
A=frozen.ACTIONS

def read(p): return json.loads(p.read_text())
def write(p,v): _atomic_write(p,v)
def require(v,msg):
    if not v: raise RuntimeError('INVALID: '+msg)
def preflight():
    require(file_hash(ROOT/'experiments/empirical_evidence_acquisition_proposal_v0/candidate.py')==SHA,'frozen candidate digest')
    m=read(PUBLIC/'source-manifest.json')
    for p,h in m['sha256'].items(): require(file_hash(ROOT/p)==h,'source freeze '+p)
    # Protocol must already be committed before any execution.
    for p in ('preregistration.md','case-definitions.json','source-manifest.json'):
        rel=str((PUBLIC/p).relative_to(ROOT))
        require(subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)==(PUBLIC/p).read_bytes(),'uncommitted registration '+p)
    return read(PUBLIC/'case-definitions.json')

def relation_type(spec,key):
    return RelationType.EMPIRICAL if key in spec['empirical_relations'] else RelationType.DETERMINISTIC

@contextmanager
def configured(spec):
    old=(protected.STUDY,protected.scenario_override,protected.relation_type)
    def schedule(case,state,action,visit,index):
        values=spec['world_outcomes'].get(f'{state}:{action}',[])
        require(0<visit<=len(values),'unregistered world visit')
        v=values[visit-1]; return v['next_state'],v['consequence']
    protected.STUDY='EMPIRICAL_EVIDENCE_ACQUISITION_REPLICATION_V0'
    protected.scenario_override=schedule
    protected.relation_type=lambda key:relation_type(spec,key)
    try: yield
    finally: protected.STUDY,protected.scenario_override,protected.relation_type=old

def assessments(store,memory,spec):
    adapter=AuthenticatedMemory(store,memory); state=store.checkpoint['current_state']
    return {a:state_view(derive_relation_state(adapter,RelationKey(state,a),relation_type(spec,f'{state}:{a}'))) for a in A}

def history(store):
    h=previous.event_projection(store)
    rejects=[x['record'] for x in store.records['training'] if x['kind']=='REGISTERED_REJECTED_ATTEMPT']
    for r in rejects:
        receipt=r['receipt']; at=r['after_authorized_event_count']
        h.insert(at,dict(authorization_status=r['authorization_status'],event_identity=canonical(r['receipt_identity']),receipt_identity=r['receipt_identity'],receipt_sha256=r['receipt_sha256'],state=receipt['pre_state'],action=receipt['action'],next_state=receipt['next_state'],consequence=receipt['realized_consequence']))
    for i,e in enumerate(h,1):e['event_stream_sequence']=i
    return h

def evaluate(state,aa,h,spec,fault=False,order=None):
    supplied=h[1:] if fault and spec['fault']=='OMIT_FIRST' else h
    try:
        value=frozen.evaluate(state,list(order or spec['candidate_input_order']),aa,supplied)
        return dict(output=value,error=None)
    except ValueError as exc:
        if not (fault and spec['fault']=='OMIT_FIRST'): raise
        return dict(output=dict(eligible=False,target_action=None,source=None,reason='INVALID_PROJECTION_FAIL_CLOSED'),error=str(exc))

def context(store,memory,spec,fault=False):
    memory.reconcile(store); state=store.checkpoint['current_state']; aa=assessments(store,memory,spec); h=history(store)
    before=memory.checkpoint(); value=evaluate(state,aa,h,spec,fault)
    require(before==memory.checkpoint(),'candidate mutated Memory')
    return dict(state=state,assessments=aa,history=h,candidate=value,
        semantic=dict(state=state,assessments=previous.semantic_assessments(aa),admissible_actions=sorted(A),
            history=[{k:e[k] for k in ('state','action','next_state','consequence','authorization_status')} for e in h],candidate=value),
        provenance=digest([(e['receipt_identity'],e['receipt_sha256']) for e in h]))

def execute(store,memory,spec,case,arm,action,source,boundary=False):
    before=context(store,memory,spec)
    with configured(spec):
        result=previous.execute_registered(store,memory,case,arm,action,source,setup=not boundary,
            reason=frozen.TRIGGER_REASON if source==frozen.SOURCE else 'REGISTERED_CONTINUATION_CONTROL',assessments=before['assessments'])
    after=context(store,memory,spec)
    event=store.records['events'][-1]['record']
    audit=dict(sequence=len(store.records['events']),action=action,source=source,
        before=before['semantic'],after=after['semantic'],receipt_identity=event['receipt_identity'],receipt_sha256=event['receipt_provenance_sha256'])
    store.append('training','REPLICATION_ACTION_AUDIT',audit)
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    return audit

def rejection(store,memory,spec,case,arm):
    """Execute a genuine receipt, reject deliberately misbound evidence, admit nothing."""
    before=memory.checkpoint(); state=store.checkpoint['current_state']; action=spec['repeated_action']
    with configured(spec):
        controller=protected.new_controller(store,'A')
        visit=1+sum(e['record']['receipt']['pre_state']==state and e['record']['receipt']['action']==action for e in store.records['events'])
        controller._active=Publication(protected.ScenarioWorld(state,case,visit,0),controller._active.framework)
        core=controller._active.framework.inner
        core.map=BoundPredictionMap(unwrap_map(core.map),Prediction(core.epoch,core.next_transaction_id,state,action,state,0))
        pending=controller.begin_step(action); require(getattr(pending,'action',None)==action,'rejection preparation')
        receipt=controller.execute_pending(); package=evidence(receipt)
        bad=replace(package,c=('PREREGISTERED_INVALID_BINDING',))
        result=controller.submit_package(bad)
        require(result.status.value!='AUTHORIZED' and not result.committed,'malformed package accepted')
        require(before==memory.checkpoint(),'rejected receipt admitted')
        require(receipt.next_state==state,'rejected fixture changed state')
        value=_plain(asdict(receipt))
        record=dict(after_authorized_event_count=len(store.records['events']),receipt=value,receipt_identity=list(receipt.identity()),receipt_sha256=digest(value),
            authorization_status=result.status.value,authorization_reason=result.reason,memory_before=before,memory_after=memory.checkpoint(),committed=result.committed,
            malformed_c=list(bad.c),original_binding=list(package.c))
        store.append('training','REGISTERED_REJECTED_ATTEMPT',record)
        store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
    return record

def snapshot(store,memory,spec,fault=False):
    c=context(store,memory,spec,fault)
    return dict(context=c,memory=memory.checkpoint(),event_count=len(store.records['events']),calls=len(store.records['calls']))

def reopen_check(root,case,arm,label):
    data=preflight();spec=data['cases'][case];path=root/'cases'/case/arm
    expected=read(path/(label+'-before.json'))
    require(expected['pid']!=os.getpid(),'fresh-process restart required')
    with SessionStore(path/'session',True) as s, ModernMemory(path/'memory.sqlite3',False) as m:
        actual=snapshot(s,m,spec)
        require(actual==expected['snapshot'],'restart reconstruction mismatch')
        write(path/(label+'-after.json'),dict(status='PASS',previous_pid=expected['pid'],pid=os.getpid(),snapshot=actual))

def restart(root,case,arm,label):
    subprocess.run([sys.executable,'-m','experiments.empirical_evidence_acquisition_replication_v0.worker','restart',str(root),case,arm,label],cwd=ROOT,check=True)

def save_restart(path,s,m,spec,label):write(path/(label+'-before.json'),dict(pid=os.getpid(),snapshot=snapshot(s,m,spec)))

def run(root):
    data=preflight();root.mkdir(parents=True,exist_ok=False)
    write(root/'registration.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_manifest_sha256=file_hash(PUBLIC/'source-manifest.json')))
    for case,spec in data['cases'].items():
        pathbase=root/'cases'/case
        for arm in data['arms']:
            path=pathbase/arm;path.mkdir(parents=True)
            with SessionStore(path/'session',False) as s,ModernMemory(path/'memory.sqlite3',True) as m:
                s.save(state=spec['initial_state'],next_transaction_id=1)
                prefix=spec['prefix'][:3] if spec['restart']=='THREE' else spec['prefix']
                for r in spec['setup']+prefix+spec['interrupt']:
                    require(s.checkpoint['current_state']==r['pre_state'],'registered pre-state')
                    audit=execute(s,m,spec,case,arm,r['action'],'REGISTERED_PREFIX')
                    receipt=s.records['events'][-1]['record']['receipt']
                    require((receipt['next_state'],receipt['realized_consequence'])==(r['next_state'],r['consequence']),'registered prefix outcome')
                if spec['restart']=='THREE':
                    require(context(s,m,spec)['candidate']['output']['suffix_count']==3,'suffix before restart')
                    save_restart(path,s,m,spec,'THREE')
                if spec['restart']=='ELIGIBLE':save_restart(path,s,m,spec,'ELIGIBLE')
            if spec['restart'] in ('THREE','ELIGIBLE'):
                restart(root,case,arm,spec['restart'])
            with SessionStore(path/'session',True) as s,ModernMemory(path/'memory.sqlite3',False) as m:
                if spec['restart']=='THREE': execute(s,m,spec,case,arm,spec['repeated_action'],'REGISTERED_FOURTH_AFTER_RESTART')
                if spec['fault']=='REJECTED_TAIL': rejection(s,m,spec,case,arm)
                c=context(s,m,spec,fault=True)
                order_checks=[]
                for order in permutations(A):
                    ordered={a:c['assessments'][a] for a in order}
                    outcome=evaluate(c['state'],ordered,c['history'],spec,True,order)
                    order_checks.append(dict(order=list(order),equal=outcome==c['candidate'],candidate=outcome))
                write(path/'boundary.json',dict(context=c,order_checks=order_checks))
        boundaries={a:read(pathbase/a/'boundary.json') for a in data['arms']}
        require(boundaries['C']['context']['semantic']==boundaries['E']['context']['semantic'],'matched semantic boundary')
        require(boundaries['C']['context']['provenance']!=boundaries['E']['context']['provenance'],'independent protected identities')
        # Behavioral mismatches are recorded as failures, never repaired or reclassified as integrity errors.
        for arm in data['arms']:
            path=pathbase/arm
            with SessionStore(path/'session',True) as s,ModernMemory(path/'memory.sqlite3',False) as m:
                c=boundaries[arm]['context']; candidate=c['candidate']['output']
                action=candidate['target_action'] if arm=='E' and candidate['eligible'] else spec['repeated_action']
                source=frozen.SOURCE if arm=='E' and candidate['eligible'] else 'REGISTERED_EMPIRICAL_CONTINUATION'
                audit=execute(s,m,spec,case,arm,action,source,True)
                write(path/'evaluation.json',dict(boundary=c,action=action,source=source,audit=audit,after=context(s,m,spec)))
                if arm=='E' and spec['restart']=='POST': save_restart(path,s,m,spec,'POST')
            if arm=='E' and spec['restart']=='POST':restart(root,case,arm,'POST')
            if arm=='E' and spec['fresh']:
                with SessionStore(path/'session',True) as s,ModernMemory(path/'memory.sqlite3',False) as m:
                    rows=[]
                    for value in spec['fresh']:
                        audit=execute(s,m,spec,case,arm,spec['repeated_action'],'REGISTERED_REQUALIFICATION')
                        require(s.records['events'][-1]['record']['receipt']['realized_consequence']==value,'requalification outcome')
                        rows.append(context(s,m,spec))
                    write(path/'requalification.json',rows)
        print(json.dumps(dict(case=case,expected=spec['expected_eligible'],observed=boundaries['E']['context']['candidate'])),flush=True)
    write(root/'complete.json',dict(status='COMPLETE',cases=len(data['cases'])))

if __name__=='__main__':
    command=sys.argv[1];root=Path(sys.argv[2])
    if command=='restart':reopen_check(root,*sys.argv[3:])
    else:
        try:run(root)
        except Exception as e:
            if root.exists():write(root/'stop.json',dict(classification='INVALID',error=repr(e)))
            raise
