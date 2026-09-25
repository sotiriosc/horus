"""Bounded deterministic evidence for initialization, identity and atomicity."""
from copy import deepcopy
from dataclasses import asdict,is_dataclass,replace
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from contextlib import contextmanager
import hashlib,json,sys
from experiments.base_framework_v0.framework import MapModel
from experiments.base_framework_v1.framework import Recovery,MeasureAuditor,StateCandidate
from experiments.realized_event_grounding_v0.framework import evidence,RealizedEventFramework
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.model_map_established_prior_revision_v1.fixture import HoldWorld
from experiments.composition_input_bindings_v1.adapters import map_payload as old_map,explorer_payload,serialize
from .boundary import EpisodeController,EpisodeWorld,EpisodePlan
from .projection import map_payload

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).parent
PARENT='b2306c917cfd8cdfc89d272e8f72fa1f01927605'
MAPPING={'K1':'ADVANCE','K2':'HOLD','K3':'RETREAT'}


def encoded(v):return json.dumps(v,sort_keys=True,indent=2,default=lambda o:asdict(o) if is_dataclass(o) else (_ for _ in ()).throw(TypeError(type(o).__name__)))+'\n'
def sha(b):return hashlib.sha256(b).hexdigest()
def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,d in r['sha256'].items():assert sha((ROOT/n).read_bytes())==d,n
    return r


def snap(c):
    s=c.snapshot();s['source_event_count']=c._source._ExternalExecutionBoundary__count
    return json.loads(encoded(s))


def provenance(c,authentic):
    f=c._active.framework;f.assert_bounds();out=[]
    for p,r in zip(f.packages,f.inner.memory.records):
        assert p.receipt is authentic[p.receipt.identity()]
        assert p.receipt.identity()==p.package_id
        assert p.receipt.epoch==r.epoch and p.receipt.transaction_id==r.transaction_id
        out.append(dict(package_identity=p.package_id,memory_identity=(r.epoch,r.transaction_id,r.pair_decision_id),
            original_receipt_object=True,full_binding_audit=True))
    return out


def step(c,action,authentic):
    before=snap(c);old_packages=list(c._active.framework.packages)
    pending=c.begin_step(action);assert pending.proposal_pre_state==before['protected']['map']['state']==before['world_state']
    assert c._source.reader().current() is None
    receipt=c.execute_pending();assert receipt.pre_state==pending.proposal_pre_state
    assert c._source.reader().current() is receipt
    result=c.submit_package(evidence(receipt));assert result.committed and result.continued
    authentic[receipt.identity()]=receipt
    assert c._active.framework.packages[-1].receipt is receipt
    assert (receipt.epoch,receipt.transaction_id,receipt.next_state,receipt.realized_consequence)==(
        c._active.framework.inner.memory.records[-1].epoch,c._active.framework.inner.memory.records[-1].transaction_id,
        c._active.framework.inner.memory.records[-1].next_state,c._active.framework.inner.memory.records[-1].consequence)
    expected=old_packages[-7:] if len(old_packages)==8 else old_packages
    assert all(p is q for p,q in zip(c._active.framework.packages[:-1],expected))
    c.release(receipt);after=snap(c);assert after['root_receipt'] is None
    return dict(before=before,pending=asdict(pending),receipt=asdict(receipt),result=asdict(result),after=after,provenance=provenance(c,authentic))


@contextmanager
def boundary_observer():
    previous=sys.getprofile();assert previous is None
    counts={'external_execute':0,'measure':0,'recovery':0,'package_admission':0}
    codes={ExternalExecutionBoundary.execute.__code__:'external_execute',MeasureAuditor.verify.__code__:'measure',
        Recovery.state_candidate.__code__:'recovery',RealizedEventFramework.submit_package.__code__:'package_admission'}
    def observe(frame,event,arg):
        if event=='call' and frame.f_code in codes:counts[codes[frame.f_code]]+=1
    sys.setprofile(observe)
    try:yield counts
    finally:sys.setprofile(previous)


def primary():
    c=EpisodeController('INITIALIZATION_PRIMARY');authentic={};rows=[]
    for a in ('HOLD','ADVANCE','ADVANCE','ADVANCE'):rows.append(step(c,a,authentic))
    before=snap(c);assert before['world_state']==before['protected']['map']['state']==3
    old=deepcopy(before['protected']);packages=list(c._active.framework.packages);source=c._source
    with boundary_observer() as effects:boundary=c.start_episode(1002,0)
    after=snap(c);views=c.projections(MAPPING)
    assert all(v==0 for v in effects.values())
    assert before['source_event_count']==after['source_event_count']==4
    assert before['world_executions']==after['world_executions']==4
    assert after['world_state']==after['protected']['map']['state']==0
    assert after['protected']['map']['epoch']==1002 and after['protected']['map']['version']==0
    assert after['protected']['memory'][-1]['next_state']==3
    assert all(old[k]==after['protected'][k] for k in ('memory','pairs','packages','commits'))
    assert all(p is q for p,q in zip(packages,c._active.framework.packages)) and c._source is source
    assert after['next_transaction_id']==1 and after['episode_steps']==0 and after['authorization_keys']==[]
    assert after['authorizer_type']=='StatusBoundAuthorizer'
    assert views['Explorer']['state']==views['Map']['HOLD']['state']==0
    assert views['Explorer']['actions'][1]['verified_outcomes']==[0]
    assert views['Explorer']['actions'][2]['verified_outcomes']=='UNTRIED'
    assert views['Map']['RETREAT']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
    assert views['Map']['HOLD']['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['epoch']==1001
    provenance(c,authentic)
    for a in ('HOLD','ADVANCE','RETREAT','HOLD'):rows.append(step(c,a,authentic))
    mixed=c.projections(MAPPING);eight=snap(c);assert len(eight['protected']['memory'])==8
    assert eight['protected']['memory'][:4]==old['memory']
    records=c._active.framework.inner.memory.records
    for action in MAPPING.values():
        assert serialize(map_payload(0,action,records,MAPPING))==serialize(map_payload(0,action,reversed(records),MAPPING))
        # Removing only epoch recovers the historical Map projection exactly.
        new=deepcopy(map_payload(0,action,records,MAPPING))
        for rec in new['VERIFIED_CHRONOLOGICAL_HISTORY']:del rec['epoch']
        assert new==old_map(0,action,records,MAPPING)
        for rec in map_payload(0,action,records,MAPPING)['VERIFIED_CHRONOLOGICAL_HISTORY']:
            assert set(rec)=={'epoch','transaction_id','surface_action','next_state','consequence'}
    assert mixed['Explorer']==explorer_payload(0,records,MAPPING)
    hold=mixed['Map']['HOLD']['VERIFIED_CHRONOLOGICAL_HISTORY']
    assert [(r['epoch'],r['transaction_id']) for r in hold]==[(1001,1),(1002,1),(1002,4)]
    rows.append(step(c,'HOLD',authentic));nine=snap(c)
    for key in ('memory','pairs','packages'):assert nine['protected'][key][:-1]==eight['protected'][key][1:]
    assert nine['evictions']==1 and len(nine['protected']['memory'])==8
    assert [r['receipt']['event_id'] for r in rows]==list(range(1,10))
    assert len({tuple(r['receipt'][k] for k in ('source_identity','event_id','epoch','transaction_id')) for r in rows})==9
    assert len({r['after']['protected']['memory'][-1]['pair_decision_id'] for r in rows})==9
    assert 'UNTRIED' not in encoded(nine['protected'])
    return dict(before=before,boundary=boundary,after=after,boundary_effects=effects,boundary_views=views,
        mixed_views=mixed,at_eight=eight,after_ninth=nine,evicted_record=eight['protected']['memory'][0],
        evicted_package=eight['protected']['packages'][0],rows=rows,historical_objects_preserved=True,
        shared_source_lifetime=True,projection_reverse_stable=True,old_projection_equivalence=True)


class FailingWorld(EpisodeWorld):
    failure=None
    def initialize_staged(self,state):
        if self.failure=='external_before':raise RuntimeError('injected external preparation failure')
        super().initialize_staged(state)
        if self.failure=='external_after':raise RuntimeError('injected external failure after staged reset')
        if self.failure=='external_wrong':self.fixture.oracle._state=3


class FailingController(EpisodeController):
    failure=None
    def _make_world(self,state):return FailingWorld(state)
    def _prepare_framework(self,active,epoch,state):
        if self.failure=='authorized_before':raise RuntimeError('injected authorized preparation failure')
        prepared=super()._prepare_framework(active,epoch,state)
        if self.failure=='authorized_after':raise RuntimeError('injected authorized failure after staged reset')
        if self.failure=='authorized_wrong':prepared.inner.map.current.state=3
        return prepared


def failures():
    cases=[]
    names=['pending_receipt','pending_transaction','same_epoch','third_epoch','bool_state','float_state','string_state',
        'negative_state','high_state','unregistered_state','bool_epoch','float_epoch','unregistered_epoch',
        'detached_pairs','detached_packages','corrupt_record','illegal_continuation','source_lifetime_changed',
        'external_before','external_after','external_wrong','authorized_before','authorized_after','authorized_wrong']
    for name in names:
        c=FailingController('FAILURE_'+name);authentic={}
        step(c,'HOLD',authentic);step(c,'ADVANCE',authentic)
        epoch,state=1002,0
        if name in ('pending_receipt','pending_transaction'):
            c.begin_step('HOLD')
            if name=='pending_receipt':c.execute_pending()
        elif name=='same_epoch':epoch=1001
        elif name=='third_epoch':c.start_episode(1002,0);epoch=1003
        elif name=='bool_state':state=False
        elif name=='float_state':state=0.0
        elif name=='string_state':state='0'
        elif name=='negative_state':state=-1
        elif name=='high_state':state=4
        elif name=='unregistered_state':state=1
        elif name=='bool_epoch':epoch=True
        elif name=='float_epoch':epoch=1002.0
        elif name=='unregistered_epoch':epoch=1003
        elif name=='detached_pairs':c._active.framework.inner.pairs.decisions=[]
        elif name=='detached_packages':c._active.framework.packages=[]
        elif name=='corrupt_record':
            memory=c._active.framework.inner.memory;memory.records[0]=replace(memory.records[0],consequence=1)
        elif name=='illegal_continuation':c.begin_step('INVALID')
        elif name=='source_lifetime_changed':
            other=EpisodeController('OTHER');c._source=other._source
        elif name.startswith('external_'):c._active.world.failure=name
        elif name.startswith('authorized_'):c.failure=name
        before=snap(c);publication=c._active;root=c._source.reader().current()
        try:c.start_episode(epoch,state)
        except (ValueError,RuntimeError) as exc:reason=str(exc)
        else:raise AssertionError('bad boundary accepted: '+name)
        after=snap(c)
        assert before==after and c._active is publication and c._source.reader().current() is root,name
        cases.append(dict(case=name,rejected=True,reason=reason,no_partial_reset=True,before=before,after=after))
    return cases


class ObservedController(EpisodeController):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.observed=[]
    def _prepare_framework(self,*args):
        self.observed.append(snap(self));result=super()._prepare_framework(*args);self.observed.append(snap(self));return result
    def _prepare_world(self,*args):
        self.observed.append(snap(self));result=super()._prepare_world(*args);self.observed.append(snap(self));return result


def atomic_visibility():
    c=ObservedController('VISIBILITY');step(c,'ADVANCE',{});before=snap(c)
    c.start_episode(1002,0);after=snap(c)
    assert len(c.observed)==4 and all(s==before for s in c.observed)
    assert after['world_state']==after['protected']['map']['state']==0
    return dict(preparation_observations=c.observed,before=before,after=after,single_publication=True,no_split_observed=True)


def receipt_controls():
    rows=[]
    for name in ('old_receipt','equal_copy','wrong_epoch','duplicate_current_package'):
        c=EpisodeController('RECEIPT_'+name);authentic={};step(c,'HOLD',authentic)
        old=c._active.framework.packages[0].receipt;c.start_episode(1002,0)
        pending=c.begin_step('HOLD')
        receipt=(c._source.execute(1001,pending.transaction_id,pending.action) if name=='wrong_epoch' else c.execute_pending())
        package=evidence(old if name=='old_receipt' else replace(receipt) if name=='equal_copy' else receipt)
        if name=='duplicate_current_package':assert c.submit_package(package).committed
        before=snap(c)['protected'];result=c.submit_package(package)
        assert not result.committed and before==snap(c)['protected']
        c.release(receipt)
        rows.append(dict(case=name,rejected=True,reason=result.reason,no_partial_publication=True))
    # Existing authorizer still enforces duplicate and capacity predicates.
    c=EpisodeController('AUTH_LIMIT');step(c,'HOLD',{});decision=c._active.framework.inner.pairs.decisions[-1]
    cls=type(c._active.framework.inner.state_authorizer);authorizer=cls()
    for n in range(1,25):
        d=replace(decision,transaction_id=n,pair_decision_id=n)
        candidate=StateCandidate(d.epoch,n,n,d.next_state)
        assert authorizer.authorize(candidate,d,state_recovery=False)
    errors=[]
    for n in (24,25):
        d=replace(decision,transaction_id=n,pair_decision_id=n)
        try:authorizer.authorize(StateCandidate(d.epoch,n,n,d.next_state),d,state_recovery=False)
        except RuntimeError as exc:errors.append(str(exc))
        else:raise AssertionError('authorizer bound failed')
    assert errors==['duplicate authorization','authorization identity bound exceeded']
    return dict(receipt_cases=rows,authorizer_errors=errors,authorization_capacity=24)


class HistoricalShiftWorld(EpisodeWorld):
    """Separate control reusing the already-registered HoldWorld switch rule.

    Shift happens before the boundary, after event 2, just as prior Map v1.
    No new regime law is invented and the primary world remains stationary.
    """
    def __init__(self,state):
        assert state==1;self.fixture=HoldWorld()
    def execute(self,*args):
        actual=self.fixture.execute(*args)
        if self.fixture.oracle.execution_count==2:self.fixture.switch()
        return actual


class HistoricalShiftController(EpisodeController):
    def _make_world(self,state):return HistoricalShiftWorld(state)


def contradiction():
    c=HistoricalShiftController('EXISTING_SHIFT_CONTROL',EpisodePlan(initial_state=1));authentic={};rows=[]
    for _ in range(3):rows.append(step(c,'HOLD',authentic))
    old=deepcopy(snap(c)['protected']);assert [r['consequence'] for r in old['memory']]==[1,1,-1]
    c.start_episode(1002,1);rows.append(step(c,'HOLD',authentic))
    projected=c.projections(MAPPING)['Map']['HOLD']['VERIFIED_CHRONOLOGICAL_HISTORY']
    assert [(r['epoch'],r['transaction_id'],r['consequence']) for r in projected]==[(1001,1,1),(1001,2,1),(1001,3,-1),(1002,1,-1)]
    assert snap(c)['protected']['memory'][:3]==old['memory']
    assert c._active.world.fixture.switch_count==1
    return dict(scope='Separate authenticated representation control reuses historical Map-prior HoldWorld; its existing switch occurs before initialization. Primary fixture is stationary; no transfer/model-performance claim.',
        projection=projected,rows=rows,old_history_unchanged=True,existing_shift_count=1)


def run():
    frozen()
    with patch('socket.socket',side_effect=AssertionError('ZERO MODEL CALLS: network forbidden')) as network:
        data=dict(primary=primary(),failure_atomicity=failures(),atomic_visibility=atomic_visibility(),
            receipt_controls=receipt_controls(),contradiction=contradiction())
        assert network.call_count==0
    gates={k:True for k in ('explicit_new_epoch','nonzero_to_registered_state','external_authorized_synchronized',
        'zero_realized_events_at_reset','history_rings_unchanged','provenance_traceable','identities_unique',
        'authorizer_reset_safe','known_pairs_not_UNKNOWN','untouched_pairs_UNKNOWN','epoch_visible_Map_identity',
        'chronological_append','ordinary_ninth_eviction','failure_atomicity','no_model_reset_capability','bounds_unchanged')}
    gates.update(exact_replay=None,historical_regressions=None)
    result=dict(study='cross-episode-initialization-boundary-v1',parent=PARENT,actual_model_calls=0,network_attempts=0,
        classification='C — NOT ESTABLISHED',eligible_classification='A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE',
        status='AWAITING_REPLAY_AND_REGRESSIONS',requirements=gates,prior_v0_result='C — NOT ESTABLISHED',
        primary_old_commits=4,primary_new_commits=4,ninth_commit=True,before_state=3,after_state=0,
        zero_event_boundary=data['primary']['boundary'],failure_cases=len(data['failure_atomicity']),
        failure_cases_atomic=sum(r['no_partial_reset'] for r in data['failure_atomicity']),
        receipt_rejections=len(data['receipt_controls']['receipt_cases']),authorizer_limit_controls=2,
        same_source_lifetime=True,source_event_ids=list(range(1,10)),ordinary_evictions=1,
        evicted_identity=[1001,1,data['primary']['evicted_record']['pair_decision_id']],
        bounds=dict(memory=8,pairs=8,packages=8,pending_authentic=1,trace=24,source_lifetime=24,epochs=2,authorizations_per_epoch=24),
        core_files_changed=False,historical_adapters_changed=False,Map_new_record_fields=['epoch','transaction_id','surface_action','next_state','consequence'],
        Explorer_schema_changed=False,contradiction_scope=data['contradiction']['scope'],details_sha256=sha(encoded(data).encode()))
    return result,data
