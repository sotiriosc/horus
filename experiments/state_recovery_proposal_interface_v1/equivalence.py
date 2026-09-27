"""Historical diagnostic case body with a factory parameter only."""
from experiments.model_recovery_proposal_v0.diagnostic import (
    TestWorld, ExternalExecutionBoundary, FixedExplorer, FixedPredictionMap,
    UnusedSlotProbe, observe, execute, published,
)
from .framework import StateRecoveryFramework


def run_case(d,name,cls='S',mode='native',instrument=True,only_consequence=False, factory=StateRecoveryFramework):
    state=d['pre_state'];action=d['action'];world=TestWorld(state,False)
    source=ExternalExecutionBoundary(world,'DIAG_'+name)
    system=factory(source.reader(),state,1001)
    wrong_consequence={-1:0,0:1,1:-1}[d['actual_consequence']]
    system.inner.explorer=FixedExplorer(action)
    system.inner.map=FixedPredictionMap(state,1001,
        d['actual_next_state'] if only_consequence else (d['actual_next_state']+1)%4,
        wrong_consequence if cls=='SC' or only_consequence else d['actual_consequence'])
    sentinel=UnusedSlotProbe();faults={}
    if mode=='unused_slot':system.inner.recovery=sentinel
    elif mode=='ordinary_candidate':faults['candidate_value']=0
    elif mode=='wrong_recovery':faults['failed_recovery']=True
    elif mode=='unsupported_keyword':faults['recovery_proposer']=sentinel.state_candidate
    with observe(instrument) as observations:
        event=execute(system,source,world,{},faults,instrument=False)
    expected_commit=mode not in ('wrong_recovery','unsupported_keyword')
    assert not event['errors'] and event['authorization']['committed']==expected_commit
    assert event['latched_before_execution'] and event['prediction_unchanged'] and event['receipt_unchanged']
    assert (event['receipt']['next_state'],event['receipt']['realized_consequence'])==(d['actual_next_state'],d['actual_consequence'])
    assert sentinel.calls==0
    if not expected_commit:
        assert event['commit_delta']==0 and event['before']==event['after']
        assert not event['authorization']['continued'] and not system.inner.continuation_authorized
        executions=world.oracle.execution_count;before=published(system)
        retried=system.begin_step()
        assert not retried.committed and not retried.executed and not retried.continued
        assert world.oracle.execution_count==executions and published(system)==before
    native=[e for e in observations if e['kind']=='native_recovery']
    auth=[e for e in observations if e['kind']=='state_authorization']
    if instrument:
        needed=d['actual_next_state']!=state
        assert len(native)==(1 if needed and mode!='unsupported_keyword' else 0)
        if native:
            assert native[0]['attempts']==1
            assert any(e['kind']=='map_quarantine' for e in observations)
            assert [e['kind'] for e in observations].index('map_quarantine')<[e['kind'] for e in observations].index('native_recovery')
            assert auth and auth[0]['authorized']==expected_commit
        if action=='HOLD':assert not native
        if mode in ('ordinary_candidate','unused_slot'):
            assert auth[0]['candidate']['value']==d['actual_next_state']==2
            assert auth[0]['candidate']['value']!=0
    return dict(name=name,fixture=d,failure_class=cls,mode=mode,only_consequence=only_consequence,
                sentinel_calls=sentinel.calls,native_observations=observations,probe=event)
