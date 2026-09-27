"""Construct genuine CARRY/FRESH systems; audit before every read-only probe."""
from dataclasses import asdict
from pathlib import Path
import json
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController
from experiments.cross_episode_initialization_boundary_v1.campaign import step, snap, provenance, boundary_observer, encoded
from experiments.cross_episode_initialization_boundary_v1.projection import explorer_payload, map_payload, serialize
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
from experiments.model_proposal_role_composition_v2.protocol import schedule as old_schedule, MODEL, SYSTEMS, OPTIONS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).parent
CAMPAIGN='HORUS_CROSS_EPISODE_MODEL_TRANSFER_V0'
PARENT='9e2e70bcde58f8cfe5a76f0dd2d2a08c2ba617f8'

def canonical(v):return json.loads(encoded(v))

def frozen():
    reg=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for name,digest in reg['sha256'].items():assert file_digest(ROOT/name)==digest,name
    return reg

def schedule():
    out=[]
    for d in old_schedule():
        i=d['episode'];d={**d,'index':i,'base_seed':90001+d['mapping_index']}
        d['order']=['CARRY','FRESH'] if i%2==0 else ['FRESH','CARRY']
        out.append(d)
    return out

class Context:
    def __init__(self,d):
        self.d=d;self.mapping=d['mapping'];self.authentic={}
        self.carry=EpisodeController(f'{CAMPAIGN}:c{d["index"]:02d}:source')
        c=self.carry
        self.steps=[step(c,a,self.authentic) for a in ('HOLD','ADVANCE','RETREAT','RETREAT')]
        self.before=snap(c);self.packages=list(c._active.framework.packages);self.source=c._source
        assert [(r['receipt']['pre_state'],r['receipt']['next_state'],r['receipt']['realized_consequence']) for r in self.steps]==[(0,0,0),(0,1,1),(1,0,0),(0,3,-1)]
        with boundary_observer() as effects:self.boundary=c.start_episode(1002,0)
        self.effects=effects;self.after=snap(c)
        self.world=TestWorld(0,False)
        self.fresh_source=ExternalExecutionBoundary(self.world,f'{CAMPAIGN}:c{d["index"]:02d}:fresh')
        self.fresh=StatusBoundFramework(self.fresh_source.reader(),0,1002)
        self.fresh_initial=self.fresh_snap()
        self.receipt=self.packages[1].receipt
        self.audit()

    def fresh_snap(self):
        f=self.fresh
        return canonical(dict(protected=published(f),epoch=f.inner.epoch,world_state=self.world.oracle.state,
            world_executions=self.world.oracle.execution_count,last_actual=self.world.last_actual,
            source_event_count=self.fresh_source._ExternalExecutionBoundary__count,
            root_receipt=self.fresh_source.reader().current(),trace=f.inner.trace,metrics=f.inner.metrics))

    def audit(self):
        c=self.carry;s=snap(c);p=s['protected']
        assert s==self.after and self.fresh_snap()==self.fresh_initial
        assert self.before['world_state']==3 and s['world_state']==p['map']['state']==0
        assert s['epoch']==p['map']['epoch']==1002
        assert s['source_event_count']==s['world_executions']==4
        assert all(x==0 for x in self.effects.values())
        assert c._source is self.source and c._registered_source is self.source
        assert len(p['memory'])==len(c._active.framework.packages)==4
        assert all(p[k]==self.before['protected'][k] for k in ('memory','pairs','packages','commits'))
        assert all(x is y for x,y in zip(self.packages,c._active.framework.packages))
        assert [(r['epoch'],r['transaction_id']) for r in p['memory']]==[(1001,i) for i in range(1,5)]
        prov=provenance(c,self.authentic)
        self.fresh.assert_bounds();f=self.fresh_snap()
        assert f['epoch']==f['protected']['map']['epoch']==1002 and f['world_state']==f['protected']['map']['state']==0
        assert f['source_event_count']==f['world_executions']==0
        assert f['protected']['memory']==f['protected']['packages']==f['protected']['pairs']==[]
        assert self.source is not self.fresh_source
        views=self.views()
        assert [a['verified_outcomes'] for a in views['FRESH']['Explorer']['actions']]==['UNTRIED']*3
        assert {self.mapping[a['action']]:a['verified_outcomes'] for a in views['CARRY']['Explorer']['actions']}==dict(ADVANCE=[1],HOLD=[0],RETREAT=[-1])
        row=dict(epoch=1001,transaction_id=2,surface_action=next(k for k,v in self.mapping.items() if v=='ADVANCE'),next_state=1,consequence=1)
        assert views['CARRY']['Map']['VERIFIED_CHRONOLOGICAL_HISTORY']==[row]
        assert views['FRESH']['Map']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
        assert self.receipt is self.authentic[self.receipt.identity()]
        return canonical(dict(original_receipts=prov,zero_event_reset=self.effects,source_lifetime_unchanged=True,
            current_epoch=1002,current_state=0,retained_epoch=1001,read_only=True,fresh_actually_empty=True))

    def views(self):
        return {cond:dict(Explorer=explorer_payload(0,f.inner.memory.records,self.mapping),
            Map=map_payload(0,'ADVANCE',f.inner.memory.records,self.mapping))
            for cond,f in [('CARRY',self.carry._active.framework),('FRESH',self.fresh)]}

    def evidence(self):
        return canonical(dict(descriptor=self.d,steps=self.steps,before_boundary=self.before,boundary=self.boundary,
            after_boundary=self.after,fresh=self.fresh_initial,audit=self.audit(),views=self.views(),scoring_receipt=asdict(self.receipt)))

    def request(self,role,condition):
        self.audit()
        return dict(model=MODEL,system=SYSTEMS[role],prompt=serialize(self.views()[condition][role]),stream=False,
            options={**OPTIONS[role],'seed':self.d['base_seed']+(100 if role=='Map' else 0)})
