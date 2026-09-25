"""Authenticated temporal fixtures; the seventh value is read only at execution."""
import json
from dataclasses import asdict,replace
from pathlib import Path
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeWorld,EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,audit,snap,plain
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,MODEL,SYSTEMS,OPTIONS
from experiments.model_map_proposal_v0.adapter import MapProposalAdapter,parse
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='24beb32ada2c1661ae31f067aebbe9b7b1939697'
CAMPAIGN='HORUS_MAP_TEMPORAL_RELATION_FORECAST_V0'
SEQUENCES={'S':(1,1,1,1,1,1,1),'F':(1,1,1,-1,-1,-1,-1),'T':(1,1,1,1,1,-1,1),'P':(1,-1,1,-1,1,-1,1)}
ARMS=tuple(SEQUENCES)
class TemporalWorld(EpisodeWorld):
    def __init__(self,state,sequence):
        super().__init__(state);self.__sequence=tuple(sequence);self.seventh_enabled=False;self.read_indices=[]
    def execute(self,epoch,transaction_id,action):
        i=self.execution_count
        assert action=='HOLD' and self.state==1 and epoch==1001 and transaction_id==i+1
        assert i<7 and (i<6 or self.seventh_enabled),'seventh event before parsed/latched prediction'
        actual=super().execute(epoch,transaction_id,action)
        self.read_indices.append(i)
        self.fixture.last_actual=replace(actual,consequence=self.__sequence[i])
        return self.fixture.last_actual
class Controller(EpisodeController):
    def __init__(self,name,sequence):self.sequence=sequence;super().__init__(name,EpisodePlan(initial_state=1))
    def _make_world(self,state):return TemporalWorld(state,self.sequence)
def schedule():
    ms=mappings();out=[]
    for j in range(12):
        order=ARMS[j%4:]+ARMS[:j%4]
        for position,fi in enumerate((0,1) if j%2==0 else (1,0)):
            for arm in (order if position==0 else order[::-1]):
                out.append(dict(index=len(out),schedule=j,family=f'O{fi+1}',mapping_index=j%6,
                    mapping=ms[fi*6+j%6]['mapping'],seed=95001+j,arm=arm,role='Map'))
    return out
def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r
class Context:
    def __init__(self,d):
        self.d=d;self.authentic={};self.executions={}
        self.c=Controller(f'{CAMPAIGN}:source:{d["index"]:03d}',SEQUENCES[d['arm']])
        self.rows=[execute(self.c,'HOLD',self.authentic,self.executions) for _ in range(6)]
        self.source=self.c._source;self.original_snapshot=snap(self.c)
        self.view=self.c.projections(d['mapping'])['Map']['HOLD'];self.audit()
    def audit(self):
        c=self.c;s=snap(c);p=s['protected'];h=self.view['VERIFIED_CHRONOLOGICAL_HISTORY']
        assert s==self.original_snapshot and c._source is self.source
        assert s['world_state']==p['map']['state']==1 and s['epoch']==1001
        assert s['world_executions']==s['source_event_count']==6 and s['evictions']==0
        assert all(len(p[k])==6 for k in ('memory','pairs','packages'))
        assert c._active.world.read_indices==list(range(6)) and not c._active.world.seventh_enabled
        alias=next(k for k,v in self.d['mapping'].items() if v=='HOLD')
        assert set(self.view)=={'state','target_action','VERIFIED_CHRONOLOGICAL_HISTORY'}
        assert self.view==c.projections(self.d['mapping'])['Map']['HOLD']
        assert h==[dict(epoch=1001,transaction_id=i+1,surface_action=alias,next_state=1,consequence=r['consequence']) for i,r in enumerate(p['memory'])]
        assert [r['consequence'] for r in h]==list(SEQUENCES[self.d['arm']][:6])
        return dict(passed=True,provenance=audit(c,self.authentic,self.executions),event_count=6,future_reads=0,Memory_length=6)
    def request(self):
        self.audit();return dict(model=MODEL,system=SYSTEMS['Map'],prompt=serialize(self.view),stream=False,options={**OPTIONS['Map'],'seed':self.d['seed']})
    def evidence(self):return plain(dict(descriptor=self.d,setup_events=self.rows,snapshot=self.original_snapshot,view=self.view,audit=self.audit()))
    def finish(self,raw,parsed,on_latched=lambda p:None):
        self.audit()
        if parsed is None:
            return dict(event=None,score=dict(valid=False,prediction=None,actual=None,exact_match=False,consequence_match=False,state_match=False),integrity=True)
        assert parse(raw)==parsed
        core=self.c._active.framework.inner;calls=[]
        def proposer(prompt,seed):
            assert prompt==serialize(self.view) and seed==self.d['seed'] and not calls
            calls.append(True);return raw
        core.map=MapProposalAdapter(core.map,proposer,serialize(self.view),self.d['seed'])
        # execute() begins through the ordinary framework path. Enable the world
        # only after begin_step returns its original immutable Prediction.
        original_begin=self.c.begin_step
        def begin(action):
            pending=original_begin(action)
            assert asdict(pending.prediction)==dict(epoch=1001,transaction_id=7,pre_state=1,action='HOLD',**parsed)
            assert self.c._active.world.read_indices==list(range(6))
            on_latched(asdict(pending.prediction))
            self.c._active.world.seventh_enabled=True
            return pending
        self.c.begin_step=begin
        event=execute(self.c,'HOLD',self.authentic,self.executions)
        after=snap(self.c);receipt=event['receipt']
        assert len(calls)==1 and after['world_state']==after['protected']['map']['state']==1
        assert self.c._active.world.read_indices==list(range(7)) and after['evictions']==0
        assert all(len(after['protected'][k])==7 and after['protected'][k][:6]==self.original_snapshot['protected'][k] for k in ('memory','pairs','packages'))
        assert event['pending']['prediction']==after['prediction_at_begin']
        actual=dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence'])
        ns=parsed['next_state']==actual['next_state'];co=parsed['consequence']==actual['consequence']
        assert event['full_provenance'][-1]['original_receipt_object']
        return dict(event=event,score=dict(valid=True,prediction=parsed,actual=actual,exact_match=ns and co,consequence_match=co,state_match=ns),integrity=True)
