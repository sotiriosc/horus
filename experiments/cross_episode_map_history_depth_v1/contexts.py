"""Three ordinary systems: genuinely empty, one exact pair, two exact pairs."""
import json
from dataclasses import asdict
from pathlib import Path
from experiments.cross_episode_initialization_boundary_v1.boundary import EpisodeController
from experiments.cross_episode_initialization_boundary_v1.campaign import step,snap,provenance,boundary_observer,encoded
from experiments.cross_episode_initialization_boundary_v1.projection import map_payload,serialize
from experiments.realized_event_grounding_v0.campaign import TestWorld,published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
from experiments.model_proposal_role_composition_v2.protocol import schedule as old_schedule,MODEL,SYSTEMS,OPTIONS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).parent
CAMPAIGN='HORUS_CROSS_EPISODE_MAP_HISTORY_DEPTH_V1'
PARENT='148b760d7c97583142c7e7f6093aa0835f0d4a71'
DEPTHS=('D0','D1','D2')

def canonical(v):return json.loads(encoded(v))
def frozen():
    reg=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,d in reg['sha256'].items():assert file_digest(ROOT/n)==d,n
    return reg

def schedule():
    out=[]
    for old in old_schedule():
        i=old['episode'];rotation=i%3
        out.append(dict(index=i,family=old['family'],mapping_index=old['mapping_index'],mapping=old['mapping'],
            seed=91001+old['mapping_index'],order=list(DEPTHS[rotation:]+DEPTHS[:rotation])))
    return out

class Context:
    def __init__(self,d):
        self.d=d;self.mapping=d['mapping'];self.carries={}
        for cond,actions in [('D1',('ADVANCE',)),('D2',('ADVANCE','RETREAT','ADVANCE'))]:
            c=EpisodeController(f'{CAMPAIGN}:c{d["index"]:02d}:{cond}:source');authentic={}
            steps=[step(c,a,authentic) for a in actions];before=snap(c)
            assert before['world_state']==before['protected']['map']['state']==1
            packages=list(c._active.framework.packages);source=c._source
            with boundary_observer() as effects:boundary=c.start_episode(1002,0)
            self.carries[cond]=dict(controller=c,authentic=authentic,steps=steps,before=before,after=snap(c),
                packages=packages,source=source,boundary=boundary,effects=effects)
        self.world=TestWorld(0,False);self.fresh_source=ExternalExecutionBoundary(self.world,f'{CAMPAIGN}:c{d["index"]:02d}:D0:source')
        self.fresh=StatusBoundFramework(self.fresh_source.reader(),0,1002);self.fresh_initial=self.fresh_snap()
        self.receipt=self.carries['D1']['packages'][0].receipt
        self.audit()

    def fresh_snap(self):
        f=self.fresh
        return canonical(dict(protected=published(f),epoch=f.inner.epoch,world_state=self.world.oracle.state,
            world_executions=self.world.oracle.execution_count,last_actual=self.world.last_actual,
            source_event_count=self.fresh_source._ExternalExecutionBoundary__count,root_receipt=self.fresh_source.reader().current(),
            trace=f.inner.trace,metrics=f.inner.metrics))

    def views(self):
        fs={'D0':self.fresh,**{k:v['controller']._active.framework for k,v in self.carries.items()}}
        return {cond:map_payload(0,'ADVANCE',f.inner.memory.records,self.mapping) for cond,f in fs.items()}

    def audit(self):
        views=self.views();out={}
        for cond,v in self.carries.items():
            c=v['controller'];n=1 if cond=='D1' else 3;s=snap(c);p=s['protected']
            assert s==v['after'] and v['before']['world_state']==1
            assert s['world_state']==p['map']['state']==0 and s['epoch']==p['map']['epoch']==1002
            assert s['world_executions']==s['source_event_count']==n and all(x==0 for x in v['effects'].values())
            assert c._source is v['source'] and c._registered_source is v['source']
            assert all(p[k]==v['before']['protected'][k] for k in ('memory','pairs','packages','commits'))
            assert len(p['memory'])==len(c._active.framework.packages)==n
            assert all(a is b for a,b in zip(v['packages'],c._active.framework.packages))
            assert [(r['epoch'],r['transaction_id']) for r in p['memory']]==[(1001,i) for i in range(1,n+1)]
            prov=provenance(c,v['authentic'])
            relevant=[q.receipt for q in v['packages'] if q.receipt.pre_state==0 and q.receipt.action=='ADVANCE']
            assert len(relevant)==int(cond[-1])
            alias=next(k for k,a in self.mapping.items() if a=='ADVANCE')
            assert views[cond]['VERIFIED_CHRONOLOGICAL_HISTORY']==[dict(epoch=1001,transaction_id=r.transaction_id,surface_action=alias,next_state=1,consequence=1) for r in relevant]
            assert all(r.next_state==1 and r.realized_consequence==1 and r is v['authentic'][r.identity()] for r in relevant)
            out[cond]=dict(original_receipts=prov,zero_event_reset=v['effects'],source_lifetime_unchanged=True,
                retained_event_count=n,visible_exact_pair_count=len(relevant),current_epoch=1002,current_state=0,retained_epoch=1001)
        f=self.fresh_snap();self.fresh.assert_bounds()
        assert f==self.fresh_initial and f['world_state']==f['protected']['map']['state']==0
        assert f['epoch']==f['protected']['map']['epoch']==1002
        assert f['world_executions']==f['source_event_count']==0 and f['root_receipt'] is None
        assert f['protected']['memory']==f['protected']['pairs']==f['protected']['packages']==[]
        assert views['D0']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
        assert len({id(self.fresh_source),*[id(v['source']) for v in self.carries.values()]})==3
        base={k:v for k,v in views['D0'].items() if k!='VERIFIED_CHRONOLOGICAL_HISTORY'}
        assert all({k:v for k,v in view.items() if k!='VERIFIED_CHRONOLOGICAL_HISTORY'}==base for view in views.values())
        return canonical(dict(conditions=out,fresh_actually_empty=True,systems_read_only=True,only_visible_history_differs=True))

    def snapshots(self):return {'D0':self.fresh_initial,**{k:v['after'] for k,v in self.carries.items()}}
    def evidence(self):
        return canonical(dict(descriptor=self.d,conditions={k:{f:v[f] for f in ('steps','before','after','boundary','effects')} for k,v in self.carries.items()},
            fresh=self.fresh_initial,audit=self.audit(),views=self.views(),scoring_receipt=asdict(self.receipt)))
    def request(self,condition):
        self.audit()
        return dict(model=MODEL,system=SYSTEMS['Map'],prompt=serialize(self.views()[condition]),stream=False,options={**OPTIONS['Map'],'seed':self.d['seed']})
