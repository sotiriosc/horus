"""Independent measured contexts built through the unchanged feasibility fixture."""
import json
from pathlib import Path
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import initialize,intervene,execute,stage,audit,snap,plain
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,MODEL,SYSTEMS,OPTIONS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
CAMPAIGN='HORUS_CROSS_EPISODE_STALE_MEMORY_MAP_REVISION_V1'
PARENT='3e0c59bd8b92023a7d7f6388b5bd1f282bff17e7'
STAGES=('P0','P1','P2');ARMS=('CONTROL','CHANGED')

def frozen():
    reg=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,d in reg['sha256'].items():assert file_digest(ROOT/n)==d,n
    return reg

def schedule():
    ms=mappings();out=[]
    for j in range(12):
        for fi in ((0,1) if j%2==0 else (1,0)):
            d=ms[fi*6+j%6]
            for si,st in enumerate(STAGES):
                arms=ARMS if (j+fi+si)%2==0 else ARMS[::-1]
                for arm in arms:
                    out.append(dict(index=len(out),schedule=j,family=f'O{fi+1}',family_index=fi,mapping_index=j%6,
                        mapping=d['mapping'],seed=92001+j,stage=st,stage_index=si,arm=arm,role='Map'))
    return out

class Context:
    def __init__(self,d):
        self.d=d
        self.c,self.authentic,self.executions,self.rows,self.boundary=initialize(f'{CAMPAIGN}:source:{d["index"]:03d}')
        self.initial_stage=stage(self.c,'P0',self.authentic,self.executions,d['arm']=='CHANGED')
        self.intervention=intervene(self.c) if d['arm']=='CHANGED' else None
        for _ in range(d['stage_index']):
            self.rows.append(execute(self.c,'ADVANCE',self.authentic,self.executions))
            self.rows.append(execute(self.c,'RETREAT',self.authentic,self.executions))
        self.captured=stage(self.c,d['stage'],self.authentic,self.executions,d['arm']=='CHANGED')
        self.view=next(v['Map'] for v in self.captured['views'] if v['family']==d['family'] and v['mapping_index']==d['mapping_index'])
        self.original_snapshot=snap(self.c);self.source=self.c._source
        self.current_outcome=dict(next_state=1,consequence=self.c._active.world.target_consequence)
        self.audit()

    def audit(self):
        c=self.c;d=self.d;s=snap(c);p=s['protected'];n=3+2*d['stage_index']
        assert s==self.original_snapshot and c._source is self.source and c._registered_source is self.source
        assert s['epoch']==p['map']['epoch']==1002 and s['world_state']==p['map']['state']==0
        assert s['source_event_count']==s['world_executions']==n and len(p['memory'])==n and s['evictions']==0
        assert all(p[k][:3]==self.boundary['after']['protected'][k] for k in ('memory','pairs','packages'))
        assert c._active.world.target_consequence==(1 if d['arm']=='CONTROL' else -1)
        assert c._active.world.intervention_count==int(d['arm']=='CHANGED')
        provenance=audit(c,self.authentic,self.executions)
        views=c.projections(d['mapping']);assert views['Map']['ADVANCE']==self.view
        expected=[1,1]+[self.current_outcome['consequence']]*d['stage_index']
        history=self.view['VERIFIED_CHRONOLOGICAL_HISTORY']
        assert [r['consequence'] for r in history]==expected
        assert [(r['epoch'],r['transaction_id']) for r in history]==[(1001,1),(1001,3),(1002,1),(1002,3)][:2+d['stage_index']]
        assert set(self.view)=={'state','target_action','VERIFIED_CHRONOLOGICAL_HISTORY'} and history
        assert all(set(r)=={'epoch','transaction_id','surface_action','next_state','consequence'} for r in history)
        assert all(self.view['target_action']==r['surface_action'] and r['next_state']==1 for r in history)
        assert 'UNTRIED' not in serialize(self.view)
        native=sum(e['kind']=='recovery_state_proposal' for row in self.rows for e in row['observed_recovery'])
        assert native==(d['stage_index'] if d['arm']=='CHANGED' else 0)
        return dict(passed=True,full_provenance=provenance,current_state=0,current_epoch=1002,Memory_length=n,
            same_source_lifetime=True,old_records_present_unchanged=True,new_records_present_unchanged=True,
            native_state_Recovery_calls=native,measured_probe_read_only=True)

    def request(self):
        self.audit()
        return dict(model=MODEL,system=SYSTEMS['Map'],prompt=serialize(self.view),stream=False,options={**OPTIONS['Map'],'seed':self.d['seed']})
    def evidence(self):
        return plain(dict(descriptor=self.d,episode1_and_navigation=self.rows,boundary=self.boundary,initial_stage=self.initial_stage,
            intervention=self.intervention,stage=self.captured,audit=self.audit(),current_external_outcome=self.current_outcome,
            current_outcome_basis='external fixture law; P0 changed outcome is not a new observed Memory event',
            old_prerequisite_receipts=[self.rows[i]['receipt'] for i in (0,2)]))
