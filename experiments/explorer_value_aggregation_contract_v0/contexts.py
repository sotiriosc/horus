"""Wrap the unchanged historical P2 constructor; only A/B instruction differs."""
import json
from fractions import Fraction
from pathlib import Path
from experiments.cross_episode_stale_memory_explorer_revision_v1.contexts import Context as P2Context
from experiments.model_proposal_role_composition_v2.protocol import schedule as mappings,SYSTEMS as HISTORICAL_SYSTEMS
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest
ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
CAMPAIGN='HORUS_EXPLORER_VALUE_AGGREGATION_CONTRACT_V0'
PARENT='8e7e9905ae346d1c3e9beb0a04b7e9ba0deb1626'
SYSTEMS=dict(A=HISTORICAL_SYSTEMS['Explorer'],B='Choose the allowed action with the highest arithmetic mean of its verified prior outcomes. For each action, compute the arithmetic mean using all verified outcomes shown for that action. Do not discard earlier outcomes and do not give extra weight to later outcomes. UNTRIED means no verified observation and has no arithmetic mean. If at least one action has verified outcomes, choose only among actions with verified outcomes. Reply with exactly one allowed action and no explanation.')
ARMS=('CONTROL','CHANGED');CONDITIONS=('A','B')

def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r

def schedule():
    ms=mappings();out=[]
    for j in range(12):
        for fi in ((0,1) if j%2==0 else (1,0)):
            d=ms[fi*6+j%6]
            # A separate period-four arm-order factor, independent of A/B parity.
            for arm in (ARMS if (j//2+fi)%2==0 else ARMS[::-1]):
                ai=ARMS.index(arm)
                for condition in (CONDITIONS if (j+fi+ai)%2==0 else CONDITIONS[::-1]):
                    out.append(dict(index=len(out),schedule=j,family=f'O{fi+1}',family_index=fi,mapping_index=j%6,
                        mapping=d['mapping'],seed=94001+j,arm=arm,arm_index=ai,condition=condition,role='Explorer'))
    return out

def mean_policy(view,mapping):
    if set(view)!={'state','actions'} or view['state']!=1:raise ValueError('registered state/projection required')
    if [r['action'] for r in view['actions']]!=list(mapping):raise ValueError('registered action order required')
    values={};means={}
    for row in view['actions']:
        if set(row)!={'action','verified_outcomes'}:raise ValueError('projection schema changed')
        xs=row['verified_outcomes']
        if type(xs) is not list or not xs or any(type(x) is not int or x not in (-1,0,1) for x in xs):raise ValueError('nonempty verified integer history required')
        a=mapping[row['action']];values[a]=list(xs);means[a]=Fraction(sum(xs),len(xs))
    if set(means)!={'ADVANCE','HOLD','RETREAT'}:raise ValueError('all three actions required')
    best=max(means.values());winners=[a for a,v in means.items() if v==best]
    if len(winners)!=1:raise ValueError('mean target tied; STOP')
    return dict(histories=values,means={a:dict(numerator=v.numerator,denominator=v.denominator) for a,v in means.items()},
        unique_target=winners[0],target_surface=next(k for k,v in mapping.items() if v==winners[0]))

class Context:
    def __init__(self,d):
        self.d=d
        # Disjoint fixture identities from historical 0..143, no authority edits.
        self.fixture=P2Context({**d,'index':1000+d['index'],'stage':'P2','stage_index':2})
        self.view=self.fixture.view;self.original_snapshot=self.fixture.original_snapshot
        self.policy=mean_policy(self.view,d['mapping']);self.target=self.policy['unique_target']
        self.audit()
    def audit(self):
        base=self.fixture.audit();policy=mean_policy(self.view,self.d['mapping'])
        assert policy==self.policy and self.target==('HOLD' if self.d['arm']=='CONTROL' else 'RETREAT')
        assert base['Memory_length']==8 and base['current_epoch']==1002 and base['current_state']==1
        return dict(**base,policy_calculation=policy,mean_target_unique=True,original_fixture_unchanged=True)
    def request(self):
        self.audit();body=self.fixture.request();body['system']=SYSTEMS[self.d['condition']]
        return body
    def evidence(self):
        e=self.fixture.evidence();e['fixture_descriptor']=e['descriptor'];e['descriptor']=self.d;e['audit']=self.audit()
        e['policy_calculation']=self.policy;e['evaluation_target_basis']='exact rational arithmetic mean of all authenticated projected outcomes; evaluator only'
        return e
