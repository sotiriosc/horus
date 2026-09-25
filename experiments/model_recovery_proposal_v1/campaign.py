"""Fixed receipt-grounded fixtures; model only occupies the Recovery callback."""
from contextlib import contextmanager
from dataclasses import asdict
from itertools import permutations
import hashlib
import json
import sys

from experiments.base_framework_v0.framework import MapModel
from experiments.base_framework_v1.framework import Recovery, MeasureAuditor, CrossSourceStateAuthorizer
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.model_recovery_proposal_v0.diagnostic import world_registration, FixedExplorer, FixedPredictionMap
from experiments.model_map_proposal_v0.boundary import execute
from experiments.state_recovery_proposal_interface_v1 import campaign as synthetic
from experiments.state_recovery_proposal_interface_v1.framework import DecisionContext
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework, StatusBoundAuthorizer
from .adapter import RecoveryProposer, render, INVALID, parse


def encoded(data): return json.dumps(data,sort_keys=True,indent=2).encode()+b'\n'


def registration():
    fixtures=[]
    for d in world_registration():
        if d['action']=='HOLD': continue
        fixtures.append(dict(fixture_id=len(fixtures),pre_state=d['pre_state'],action=d['action'],
            actual_next_state=d['actual_next_state'],actual_consequence=d['actual_consequence'],
            wrong_next_state=(d['actual_next_state']+1)%4,predicted_consequence=d['actual_consequence']))
    plan=[]
    for f in fixtures:
        for j,perm in enumerate(permutations(('ADVANCE','HOLD','RETREAT'))):
            families=('O1','O2') if (f['fixture_id']+j)%2==0 else ('O2','O1')
            for family in families:
                tokens=('K1','K2','K3') if family=='O1' else ('Q7','M4','Z2')
                mapping=dict(zip(tokens,perm))
                context=DecisionContext(1001,1,0,f['pre_state'],f['action'],f['actual_next_state'],f['actual_consequence'],False)
                prompt=render(context,mapping)
                plan.append(dict(index=len(plan),fixture=f,family=family,mapping_index=j,mapping=mapping,
                    seed=70001+j,surface_action=next(k for k,v in mapping.items() if v==f['action']),
                    exact_prompt=prompt,prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()))
    assert len(plan)==96 and len(fixtures)==8
    return plan,encoded(plan)


@contextmanager
def observe(enabled):
    events=[]; previous=sys.getprofile()
    codes={RealizedEventFramework._check.__code__:'receipt',MeasureAuditor.verify.__code__:'measure',
           MapModel.quarantine_incumbent.__code__:'quarantine',Recovery.state_candidate.__code__:'native_attempt',
           RecoveryProposer.propose.__code__:'model_proposal',StatusBoundAuthorizer.authorize.__code__:'status_authorizer',
           CrossSourceStateAuthorizer.authorize.__code__:'ordinary_authorizer',MapModel.commit.__code__:'map_commit'}
    def callback(frame,event,value):
        kind=codes.get(frame.f_code)
        if not kind or event!=('call' if kind=='model_proposal' else 'return'): return
        loc=frame.f_locals;row=dict(kind=kind)
        if kind=='native_attempt': row.update(attempts=loc['self'].attempts,candidate=asdict(value),decision=asdict(loc['decision']))
        elif kind=='model_proposal': row['context']=asdict(loc['context'])
        elif kind.endswith('authorizer'):
            row.update(candidate=asdict(loc['candidate']),decision=asdict(loc['decision']),accepted=value)
            if kind=='status_authorizer': row['state_recovery']=loc['state_recovery']
        elif kind=='measure':row.update(verified=value,measurement=asdict(loc['measurement']))
        elif kind=='receipt':row['verified']=value is not None
        events.append(row)
    if enabled:
        if previous is not None: raise RuntimeError('observer installed')
        sys.setprofile(callback)
    try:yield events
    finally:
        if enabled:sys.setprofile(previous)


class FixedResponse:
    def __init__(self,raw,metadata=None):self.raw=raw;self.metadata=metadata or {'synthetic':True};self.requests=0
    def generate(self,prompt,seed):self.requests+=1;return self.raw,self.metadata


def probe(transport,d,emit=None,instrument=True):
    f=d['fixture'];world=synthetic.TestWorld(f['pre_state'],False)
    boundary=synthetic.ExternalExecutionBoundary(world,'MODEL_RECOVERY_'+str(d['index']))
    proposer=RecoveryProposer(transport,d,emit)
    system=StatusBoundFramework(boundary.reader(),f['pre_state'],1001,proposer)
    system.inner.explorer=FixedExplorer(f['action'])
    system.inner.map=FixedPredictionMap(f['pre_state'],1001,f['wrong_next_state'],f['predicted_consequence'])
    with observe(instrument) as events:
        row=execute(system,boundary,world,{},instrument=False)
    assert proposer.invocations==len(proposer.calls)==1
    call=proposer.calls[0]
    if call['transport_error']:raise RuntimeError('model transport failed; no retry')
    state=call['parsed_replacement_state']; valid=call['parser_error'] is None
    correct=valid and state==row['receipt']['next_state']
    assert row['prediction']['next_state']==f['wrong_next_state']
    assert row['prediction']['consequence']==f['predicted_consequence']
    assert (row['receipt']['pre_state'],row['receipt']['action'],row['receipt']['next_state'],row['receipt']['realized_consequence'])==(f['pre_state'],f['action'],f['actual_next_state'],f['actual_consequence'])
    assert f['pre_state']!=row['receipt']['next_state']
    assert row['authorization']['committed']==correct
    assert not row['errors'] and row['prediction_unchanged'] and row['receipt_unchanged']
    if not correct:
        assert row['before']==row['after'] and row['commit_delta']==0 and not row['authorization']['continued']
        retry=system.begin_step()
        assert not retry.executed and not retry.committed and not retry.continued
        assert proposer.invocations==len(proposer.calls)==1
    if instrument:
        kinds=[e['kind'] for e in events]
        order=['receipt','measure','quarantine','native_attempt','model_proposal']
        positions=[kinds.index(k) for k in order];assert positions==sorted(positions)
        assert kinds.count('native_attempt')==kinds.count('model_proposal')==1
        attempt=next(e for e in events if e['kind']=='native_attempt')
        assert attempt['attempts']==1 and attempt['decision']['measurement_matches'] is False
        assert all(e['verified'] for e in events if e['kind'] in ('receipt','measure'))
        auth=[e for e in events if e['kind']=='status_authorizer']
        ordinary=[e for e in events if e['kind']=='ordinary_authorizer']
        assert len(auth)==len(ordinary)==int(valid)
        if valid:
            assert auth[0]['state_recovery'] is True and auth[0]['accepted']==correct
            assert ordinary[0]['accepted']==correct and auth[0]['candidate']['value']==state
            for k in ('epoch','transaction_id','pair_decision_id','status'):
                assert auth[0]['candidate'][k]==attempt['candidate'][k]
            assert auth[0]['candidate']['status']=='RECOVERING'
            assert kinds.index('model_proposal')<kinds.index('ordinary_authorizer')<kinds.index('status_authorizer')
        assert kinds.count('map_commit')==int(correct)
    return dict(index=d['index'],descriptor=d,model_call=call,valid=valid,correct=correct,
                callback_count=proposer.invocations,events=events,probe=row)


def no_recovery():
    rows=[]
    for f in world_registration():
        if f['action']!='HOLD':continue
        for cls,only in (('S',False),('SC',False),('S',True)):
            world=synthetic.TestWorld(f['pre_state'],False)
            boundary=synthetic.ExternalExecutionBoundary(world,'NO_RECOVERY_'+str(f['pre_state'])+cls+str(only))
            system=StatusBoundFramework(boundary.reader(),f['pre_state'],1001)
            row,_=synthetic.transaction(f,'hold','never',True,cls,only,existing=(system,boundary,world))
            assert not row['callback_contexts']
            rows.append(row)
    return rows


def controls(plan):
    d=next(d for d in plan if d['fixture']['pre_state']==1 and d['fixture']['action']=='ADVANCE')
    rows=[]
    for i,raw in enumerate(INVALID):
        transport=FixedResponse(raw);row=probe(transport,d)
        assert not row['valid'] and not row['probe']['authorization']['committed']
        rows.append(dict(control_index=i,row=row))
    return dict(parser=rows,no_recovery=no_recovery())


def projection(value):
    if isinstance(value,dict):return {k:projection(v) for k,v in value.items() if k not in ('events','native_observations')}
    if isinstance(value,list):return [projection(v) for v in value]
    return value
