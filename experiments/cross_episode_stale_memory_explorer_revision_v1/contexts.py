"""Actual authenticated state-1 fixtures; measured proposals never execute."""
import json
from dataclasses import replace
from pathlib import Path
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeWorld,EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,audit,snap,plain,boundary_observer
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,MODEL,SYSTEMS,OPTIONS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
CAMPAIGN='HORUS_CROSS_EPISODE_STALE_MEMORY_EXPLORER_REVISION_V1'
PARENT='82e04f31a8a532547e4a1858ef22643dd1986843'
STAGES=('P0','P1','P2');ARMS=('CONTROL','CHANGED')
OLD=('HOLD','RETREAT','ADVANCE','ADVANCE','RETREAT','RETREAT')
OLD_EVENTS=((1,'HOLD',1,1),(1,'RETREAT',0,0),(0,'ADVANCE',1,1),(1,'ADVANCE',2,-1),(2,'RETREAT',1,1),(1,'RETREAT',0,0))

def target_law(actual,consequence):
    assert type(consequence) is int and consequence in (-1,1)
    return replace(actual,consequence=consequence) if (actual.pre_state,actual.action)==(1,'HOLD') else actual

class TargetWorld(EpisodeWorld):
    def __init__(self,state):
        super().__init__(state);self.target_consequence=1;self.intervention_count=0
    def change_target(self):
        if self.execution_count!=6 or self.state!=1 or self.intervention_count:raise ValueError('registered post-reset intervention only')
        self.target_consequence=-1;self.intervention_count+=1
    def execute(self,epoch,transaction_id,action):
        actual=super().execute(epoch,transaction_id,action)
        self.fixture.last_actual=target_law(actual,self.target_consequence)
        return self.fixture.last_actual
class Controller(EpisodeController):
    def _make_world(self,state):return TargetWorld(state)

def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r

def schedule():
    ms=mappings();out=[]
    for j in range(12):
        for fi in ((0,1) if j%2==0 else (1,0)):
            d=ms[fi*6+j%6]
            for si,st in enumerate(STAGES):
                for arm in (ARMS if (j+fi+si)%2==0 else ARMS[::-1]):
                    out.append(dict(index=len(out),schedule=j,family=f'O{fi+1}',family_index=fi,mapping_index=j%6,
                        mapping=d['mapping'],seed=93001+j,stage=st,stage_index=si,arm=arm,role='Explorer'))
    return out

class Context:
    def __init__(self,d):
        self.d=d;self.authentic={};self.executions={}
        self.c=c=Controller(f'{CAMPAIGN}:source:{d["index"]:03d}',EpisodePlan(initial_state=1))
        self.rows=[execute(c,a,self.authentic,self.executions) for a in OLD]
        assert [(r['receipt']['pre_state'],r['receipt']['action'],r['receipt']['next_state'],r['receipt']['realized_consequence']) for r in self.rows]==list(OLD_EVENTS)
        before=snap(c);packages=list(c._active.framework.packages);self.source=c._source
        assert before['world_state']==before['protected']['map']['state']==0
        with boundary_observer() as effects:boundary=c.start_episode(1002,1)
        after=snap(c)
        assert all(v==0 for v in effects.values())
        assert before['world_executions']==after['world_executions']==before['source_event_count']==after['source_event_count']==6
        assert after['world_state']==after['protected']['map']['state']==1 and after['epoch']==1002
        assert all(before['protected'][k]==after['protected'][k] for k in ('memory','pairs','packages','commits'))
        assert all(x is y for x,y in zip(packages,c._active.framework.packages)) and c._source is self.source
        self.boundary=dict(before=before,after=after,boundary=boundary,effects=effects,same_source_lifetime=True,original_packages_retained=True)
        self.initial_stage=dict(snapshot=after,Explorer=c.projections(d['mapping'])['Explorer'],provenance=audit(c,self.authentic,self.executions))
        self.intervention=None
        if d['arm']=='CHANGED':
            with boundary_observer() as effect:c._active.world.change_target()
            assert snap(c)==after and all(v==0 for v in effect.values())
            self.intervention=dict(before=after,after=snap(c),effects=effect,after_episode_initialization=True,before_first_episode2_event=True,external_intervention_count=1)
        for _ in range(d['stage_index']):self.rows.append(execute(c,'HOLD',self.authentic,self.executions))
        self.view=c.projections(d['mapping'])['Explorer'];self.original_snapshot=snap(c)
        self.current_best='HOLD' if d['arm']=='CONTROL' else 'RETREAT'
        self.captured=dict(snapshot=self.original_snapshot,Explorer=self.view,provenance=audit(c,self.authentic,self.executions))
        self.audit()

    def audit(self):
        c=self.c;d=self.d;s=snap(c);p=s['protected'];n=6+d['stage_index']
        assert s==self.original_snapshot and c._source is self.source and c._registered_source is self.source
        assert s['epoch']==p['map']['epoch']==1002 and s['world_state']==p['map']['state']==1
        assert s['source_event_count']==s['world_executions']==len(p['memory'])==n and s['evictions']==0
        assert all(p[k][:6]==self.boundary['after']['protected'][k] for k in ('memory','pairs','packages'))
        assert [(r['epoch'],r['transaction_id']) for r in p['memory']]==[(1001,i) for i in range(1,7)]+[(1002,i) for i in range(1,1+d['stage_index'])]
        assert c._active.world.target_consequence==(1 if d['arm']=='CONTROL' else -1)
        assert c._active.world.intervention_count==int(d['arm']=='CHANGED')
        provenance=audit(c,self.authentic,self.executions)
        assert c.projections(d['mapping'])['Explorer']==self.view
        expected=dict(HOLD=[1]+[c._active.world.target_consequence]*d['stage_index'],RETREAT=[0,0],ADVANCE=[-1])
        assert set(self.view)=={'state','actions'} and self.view['state']==1 and len(self.view['actions'])==3
        assert [r['action'] for r in self.view['actions']]==list(d['mapping'])
        assert all(set(r)=={'action','verified_outcomes'} for r in self.view['actions'])
        assert {d['mapping'][r['action']]:r['verified_outcomes'] for r in self.view['actions']}==expected
        assert 'UNTRIED' not in serialize(self.view)
        initial=self.initial_stage['Explorer'];assert {d['mapping'][r['action']]:r['verified_outcomes'] for r in initial['actions']}==dict(HOLD=[1],RETREAT=[0,0],ADVANCE=[-1])
        native=sum(e['kind']=='recovery_state_proposal' for row in self.rows for e in row['observed_recovery'])
        measure=sum(e['kind']=='recovery_measurement' for row in self.rows for e in row['observed_recovery'])
        return dict(passed=True,full_provenance=provenance,current_state=1,current_epoch=1002,Memory_length=n,
            same_source_lifetime=True,old_records_present_unchanged=True,new_records_present_unchanged=True,
            native_state_Recovery_calls=native,native_measurement_Recovery_calls=measure,measured_probe_read_only=True)

    def request(self):
        self.audit()
        return dict(model=MODEL,system=SYSTEMS['Explorer'],prompt=serialize(self.view),stream=False,options={**OPTIONS['Explorer'],'seed':self.d['seed']})
    def evidence(self):
        return plain(dict(descriptor=self.d,setup_events=self.rows,boundary=self.boundary,initial_stage=self.initial_stage,
            intervention=self.intervention,stage=self.captured,audit=self.audit(),current_best=self.current_best,
            current_best_basis='registered external fixture law; P0 hidden change is not a new Memory observation'))
