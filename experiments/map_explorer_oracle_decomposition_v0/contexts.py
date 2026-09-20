"""Authenticated decision fixtures and detached, post-Map world evaluation."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
import json,hashlib
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController,EpisodePlan
from experiments.cross_episode_stale_memory_explorer_revision_v1.contexts import Context as D1Context
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import execute,audit,snap,plain
from experiments.map_guided_explorer_interface_v0.interface import AuthenticatedReader,ForecastCoordinator,ProposalFailure,MAP_SYSTEM,EXPLORER_SYSTEM
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.composition_input_bindings_v1.adapters import ACTIONS
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,MODEL,OPTIONS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='5781473435c1fc5eadf53e80edc44259796e6610'
CAMPAIGN='HORUS_MAP_EXPLORER_ORACLE_DECOMPOSITION_V0'
WORLDS=('W0','W1','W3','D1')
HISTORY={'W0':{'ADVANCE':[1],'HOLD':[0],'RETREAT':[-1]},'W1':{'ADVANCE':[-1],'HOLD':[1],'RETREAT':[0]},'W3':{'ADVANCE':[-1],'HOLD':[0],'RETREAT':[1]},'D1':{'ADVANCE':[-1],'HOLD':[1,-1,-1],'RETREAT':[0,0]}}
# Used only in construction tests, never to supply evaluator truth or a request.
EXPECTED={'W0':((1,1),(0,0),(3,-1)),'W1':((2,-1),(1,1),(0,0)),'W3':((0,-1),(3,0),(2,1)),'D1':((2,-1),(1,-1),(0,0))}
def schedule():
    out=[];ms=mappings()
    for w,world in enumerate(WORLDS):
        for j in range(6):
            for fi in ((0,1) if (w+j)%2==0 else (1,0)):
                out.append(dict(index=len(out),world=world,world_index=w,mapping_index=j,family=f'O{fi+1}',family_index=fi,
                    mapping=ms[fi*6+j]['mapping'],base_seed=96001+100*w+10*j))
    return out
def slots(d):
    return ['Map:ADVANCE','Map:HOLD','Map:RETREAT']+(['Oracle','Permutation'] if d['index']%2==0 else ['Permutation','Oracle'])+['ModelMap']
def seed(d,slot):return d['base_seed']+{'Map:ADVANCE':1,'Map:HOLD':2,'Map:RETREAT':3,'Oracle':4,'Permutation':5,'ModelMap':6}[slot]
def body(d,slot,payload):
    role='Map' if slot.startswith('Map:') else 'Explorer'
    return dict(model=MODEL,system=MAP_SYSTEM if role=='Map' else EXPLORER_SYSTEM,prompt=serialize(payload),stream=False,options={**OPTIONS[role],'seed':seed(d,slot)})
def request_hash(request):return hashlib.sha256(json.dumps(request).encode()).hexdigest()
def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r
class Context:
    def __init__(self,d):
        self.d=d;world=d['world']
        if world=='D1':
            old=D1Context(dict(index=4000+d['index'],schedule=d['mapping_index'],family=d['family'],family_index=d['family_index'],mapping_index=d['mapping_index'],mapping=d['mapping'],seed=seed(d,'Oracle'),arm='CHANGED',stage='P2',stage_index=2,role='Explorer'))
            self.c=old.c;self.authentic=old.authentic;self.executions=old.executions;self.rows=old.rows;self.boundary=old.boundary
        else:
            state={'W0':0,'W1':1,'W3':3}[world]
            self.c=EpisodeController(f'{CAMPAIGN}:source:{d["index"]:03d}',EpisodePlan(initial_state=state))
            self.authentic={};self.executions={};self.boundary=None
            actions=('HOLD','ADVANCE','RETREAT','RETREAT','ADVANCE') if world=='W0' else ('HOLD','RETREAT','ADVANCE','ADVANCE','RETREAT')
            self.rows=[execute(self.c,a,self.authentic,self.executions) for a in actions]
        self.original_snapshot=snap(self.c);self.source=self.c._source
        self.reader=AuthenticatedReader(self.c,self.authentic,self.executions)
        self.session=ForecastCoordinator(self.reader,d['mapping'],f'{CAMPAIGN}:{d["index"]}').begin()
        self.map_inputs=self.session.context['map_inputs'];self.map_requests={a:body(d,'Map:'+a,self.map_inputs[a]) for a in ACTIONS}
        self.oracle_evaluated=False;self.audit()
    def audit(self):
        s=snap(self.c);p=s['protected'];world=self.d['world'];n=8 if world=='D1' else 5
        assert s==self.original_snapshot and self.c._source is self.source
        assert s['world_state']==p['map']['state']=={'W0':0,'W1':1,'W3':3,'D1':1}[world]
        assert s['epoch']==(1002 if world=='D1' else 1001) and s['evictions']==0
        assert s['world_executions']==s['source_event_count']==n and all(len(p[k])==n for k in ('memory','pairs','packages'))
        for a in ACTIONS:
            view=self.map_inputs[a];h=view['VERIFIED_CHRONOLOGICAL_HISTORY']
            assert view==self.c.projections(self.d['mapping'])['Map'][a] and h
            assert [r['consequence'] for r in h]==HISTORY[world][a]
            assert set(view)=={'state','target_action','VERIFIED_CHRONOLOGICAL_HISTORY'}
            assert all(set(r)=={'epoch','transaction_id','surface_action','next_state','consequence'} for r in h)
        return dict(passed=True,provenance=audit(self.c,self.authentic,self.executions),Memory_length=n,no_eviction=True,all_actions_observed=True,original_world_executions=n)
    def collect(self,map_calls):
        assert len(map_calls)==3 and [r['slot'] for r in map_calls]==['Map:'+a for a in ACTIONS]
        index=0
        def source(system,prompt):
            nonlocal index
            row=map_calls[index];assert row['request']['system']==system and row['request']['prompt']==prompt;index+=1
            return row['response']['raw_output']
        try:view=self.session.collect(source);failure=None
        except ProposalFailure as exc:view=None;failure=str(exc)
        self.audit();return dict(view=view,failure=failure,binding_reads=index)
    def oracle(self,map_calls):
        # All three original requests/responses/parse results must already exist.
        assert len(map_calls)==3 and all(r['parsed_recorded'] for r in map_calls)
        assert not self.oracle_evaluated;self.audit();out={};evaluations=[]
        for action in ACTIONS:
            world=deepcopy(self.c._active.world);before=world.execution_count
            actual=world.execute(self.original_snapshot['epoch'],self.original_snapshot['next_transaction_id'],action)
            assert world.execution_count==before+1
            out[action]=dict(next_state=actual.next_state,consequence=actual.consequence)
            evaluations.append(dict(action=action,actual=asdict(actual),detached_world=True,receipt_minted=False))
        self.oracle_evaluated=True;self.audit()
        assert len([a for a in ACTIONS if out[a]['consequence']==max(v['consequence'] for v in out.values())])==1
        return dict(values=out,detached_evaluations=evaluations)
    def forecast_view(self,values):
        return dict(state=self.original_snapshot['world_state'],actions=[dict(action=k,map_prediction=dict(values[a])) for k,a in self.d['mapping'].items()])
    def evidence(self):return plain(dict(descriptor=self.d,setup_events=self.rows,boundary=self.boundary,snapshot=self.original_snapshot,map_inputs=self.map_inputs,map_requests=self.map_requests,audit=self.audit()))
def permute(view):
    v=deepcopy(view);ns=[r['map_prediction']['next_state'] for r in view['actions']]
    for i,r in enumerate(v['actions']):r['map_prediction']['next_state']=ns[(i+1)%3]
    return v
