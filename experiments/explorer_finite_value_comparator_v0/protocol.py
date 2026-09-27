"""Pure detached finite forecasts; no world, Map proposal or Memory instance."""
from itertools import permutations
from pathlib import Path
from contextlib import contextmanager,ExitStack
from unittest.mock import patch
import json,hashlib
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,MODEL,OPTIONS
from experiments.map_guided_explorer_interface_v0.interface import EXPLORER_SYSTEM
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='2679cff20b28079b4358fe463f68e5822e5cc205'
CAMPAIGN='HORUS_EXPLORER_FINITE_VALUE_COMPARATOR_V0'
ACTIONS=('ADVANCE','HOLD','RETREAT');RELATIONS=('R1','R2','R3');CONDITIONS=('N','V')
ASSIGNMENT_INDICES=(0,3,2,0,3,2,4,1,5,5,4,1)
CONSEQUENCES=tuple(permutations((1,0,-1)));NEXT_STATES=tuple(permutations((0,1,2)))
PROHIBITED=('experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute',
 'experiments.cross_episode_initialization_boundary_v1.boundary.EpisodeController.__init__',
 'experiments.base_framework_v0.framework.MapModel.predict',
 'experiments.base_framework_v0.framework.OutcomeMemory.__init__',
 'experiments.base_framework_v1.framework.CrossMemory.__init__')
@contextmanager
def detached_only():
    with ExitStack() as stack:
        mocks={n:stack.enter_context(patch(n,side_effect=AssertionError('detached comparator: world/Map/Memory forbidden'))) for n in PROHIBITED}
        yield mocks
        assert all(m.call_count==0 for m in mocks.values())
def serialize(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def request_hash(value):return hashlib.sha256(json.dumps(value).encode()).hexdigest()
def schedule():
    out=[];ms=mappings()
    for ri,relation in enumerate(RELATIONS):
        for j in range(12):
            for fi in ((0,1) if (ri+j)%2==0 else (1,0)):
                for condition in (CONDITIONS if (ri+j+fi)%2==0 else CONDITIONS[::-1]):
                    out.append(dict(index=len(out),relation=relation,relation_index=ri,schedule=j,mapping_index=j%6,
                        family=f'O{fi+1}',family_index=fi,mapping=ms[fi*6+j%6]['mapping'],condition=condition,seed=97001+100*ri+j,
                        assignment_index=ASSIGNMENT_INDICES[j],varied_next_state_index=(j+1)%6,role='Explorer'))
    return out

def build(d):
    original=CONSEQUENCES[d['assignment_index']];best_index=original.index(1)
    cs=original if d['relation']=='R1' else tuple((1 if d['relation']=='R2' else 0) if i==best_index else -1 for i in range(3))
    ns=(1,1,1) if d['condition']=='N' else NEXT_STATES[d['varied_next_state_index']]
    values={a:dict(next_state=ns[i],consequence=cs[i]) for i,a in enumerate(ACTIONS)}
    view=dict(state=1,actions=[dict(action=alias,map_prediction=values[a]) for alias,a in d['mapping'].items()])
    target=ACTIONS[best_index];alias=next(k for k,v in d['mapping'].items() if v==target)
    return view,dict(underlying_action=target,alias=alias,consequence=max(cs),assignment=values)
def request(d):
    view,_=build(d)
    return dict(model=MODEL,system=EXPLORER_SYSTEM,prompt=serialize(view),stream=False,options={**OPTIONS['Explorer'],'seed':d['seed']})
def score(raw,d):
    alias,action,error=parse_surface(raw,dict(surface_option_order=list(d['mapping']),surface_to_underlying=d['mapping']))
    _,target=build(d)
    return dict(valid=action is not None,selected_alias=alias,selected_action=action,error=error,true_best=target['underlying_action'],true_best_alias=target['alias'],correct=action==target['underlying_action'])
def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r
