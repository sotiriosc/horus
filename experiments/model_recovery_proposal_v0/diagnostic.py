"""Read-only native-path diagnosis. No model transport or Recovery replacement."""
import ast
from contextlib import contextmanager
from dataclasses import asdict
import inspect
import sys
from experiments.base_framework_v0.framework import MapModel, Prediction
from experiments.base_framework_v1.framework import (CrossSourceFramework, Recovery,
    CrossSourceStateAuthorizer, MeasureAuditor, StateCandidate, RECOVERY_LIMIT)
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.model_map_proposal_v0.boundary import execute

ACTIONS=("ADVANCE","HOLD","RETREAT")


class FixedExplorer:
    def __init__(self,action):self.action=action
    def choose(self,state,records):return self.action


class FixedPredictionMap(MapModel):
    """Only a deterministic fixture prediction; inherited protected methods."""
    def __init__(self,state,epoch,next_state,consequence):
        super().__init__(state,epoch)
        self.proposed_next_state=next_state;self.proposed_consequence=consequence
    def predict(self,action,epoch,transaction_id):
        return Prediction(epoch,transaction_id,self.current.state,action,
                          self.proposed_next_state,self.proposed_consequence)


class UnusedSlotProbe:
    """Sentinel for a hypothesized component slot, NOT a working model adapter."""
    def __init__(self):self.calls=0
    def __deepcopy__(self,memo):return self  # counter only; owns no protected state
    def state_candidate(self,decision,wrong=False):
        self.calls+=1
        return StateCandidate(decision.epoch,decision.transaction_id,decision.pair_decision_id,0)


@contextmanager
def observe(enabled):
    events=[];previous=sys.getprofile()
    codes={Recovery.state_candidate.__code__:"native_recovery",
           CrossSourceStateAuthorizer.authorize.__code__:"state_authorization",
           MapModel.quarantine_incumbent.__code__:"map_quarantine",
           MeasureAuditor.verify.__code__:"measure_verification"}
    def callback(frame,event,value):
        if event!='return' or frame.f_code not in codes:return
        name=codes[frame.f_code];local=frame.f_locals
        if name=='native_recovery':
            data=dict(decision=asdict(local['decision']),candidate=asdict(value) if value else None,
                      attempts=local['self'].attempts)
        elif name=='state_authorization':
            data=dict(candidate=asdict(local['candidate']),decision=asdict(local['decision']),authorized=value)
        elif name=='map_quarantine':data=dict(quarantine=[asdict(x) for x in local['self'].quarantine])
        else:data=dict(measurement=asdict(local['measurement']),verified=value)
        events.append(dict(kind=name,**data))
    if enabled:
        if previous is not None:raise RuntimeError('existing observer')
        sys.setprofile(callback)
    try:yield events
    finally:
        if enabled:sys.setprofile(previous)


def world_registration():
    rows=[]
    for state in range(4):
        for action in ACTIONS:
            world=TestWorld(state,False)
            source=ExternalExecutionBoundary(world,f'REGISTER_{state}_{action}')
            receipt=source.execute(1001,1,action)
            assert receipt.binding()[:6]==tuple(asdict(world.last_actual).values())
            rows.append(dict(pre_state=state,action=action,receipt=asdict(receipt),
                actual_next_state=receipt.next_state,actual_consequence=receipt.realized_consequence))
            source.release(receipt)
    return rows


def run_case(d,name,cls='S',mode='native',instrument=True,only_consequence=False):
    state=d['pre_state'];action=d['action'];world=TestWorld(state,False)
    source=ExternalExecutionBoundary(world,'DIAG_'+name)
    system=RealizedEventFramework(source.reader(),state,1001)
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


def budget_test(decision):
    r=Recovery();first=r.state_candidate(decision);first_attempts=r.attempts
    try:r.state_candidate(decision)
    except RuntimeError as exc:reason=str(exc)
    else:raise AssertionError('native Recovery allowed second call on same object')
    assert first_attempts==RECOVERY_LIMIT==1 and r.attempts==2
    return dict(limit=RECOVERY_LIMIT,first=asdict(first),attempts_after_first=first_attempts,
                second_call_rejected=True,attempt_counter_after_rejection=r.attempts,reason=reason,
                scope='per Recovery object; counter increments before rejection, not an allowed second proposal')


def inspect_interface():
    source=inspect.getsource(CrossSourceFramework)
    tree=ast.parse(source)
    inline=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
            and n.func.attr=='state_candidate' and isinstance(n.func.value,ast.Call)
            and isinstance(n.func.value.func,ast.Name) and n.func.value.func.id=='Recovery']
    attributes=sorted(vars(CrossSourceFramework()).keys())
    assert len(inline)==1 and 'recovery' not in attributes
    assert not inline[0].func.value.args and not inline[0].func.value.keywords
    return dict(constructor=str(inspect.signature(CrossSourceFramework)),
        proposal=str(inspect.signature(Recovery.state_candidate)),
        submit_receipt=str(inspect.signature(CrossSourceFramework.submit_receipt)),
        instance_has_recovery_component=False,inline_state_recovery_constructions=len(inline),
        call=ast.unparse(inline[0]),
        missing_interface='No configurable state-Recovery proposer/component/factory at the post-Measure, post-quarantine call site; the coordinator directly constructs native Recovery.',
        state_candidate_fields=list(StateCandidate.__dataclass_fields__),
        existing_recovery_input='PairDecision and the fixed wrong fault flag; not the latched Prediction')


def run(instrument=True):
    interface=inspect_interface();registration=world_registration();rows=[]
    for d in registration:
        for cls in ('S','SC'):
            rows.append(run_case(d,f"{d['pre_state']}_{d['action']}_{cls}",cls,instrument=instrument))
    d=next(d for d in registration if d['pre_state']==1 and d['action']=='ADVANCE')
    for mode in ('wrong_recovery','ordinary_candidate','unused_slot','unsupported_keyword'):
        rows.append(run_case(d,mode,mode=mode,instrument=instrument))
    for d in registration:
        if d['action']=='HOLD':rows.append(run_case(d,f"no_recovery_{d['pre_state']}",only_consequence=True,instrument=instrument))
    # Use a genuine receipt-bound decision from native execution, never an invented event.
    from experiments.base_framework_v1.framework import PairDecision
    decision=PairDecision(**rows[0]['probe']['after']['pairs'][0])
    budget=budget_test(decision)
    primary=rows[:24]
    if instrument:
        for a,b in zip(primary[::2],primary[1::2]):
            ra=[x['decision'] for x in a['native_observations'] if x['kind']=='native_recovery']
            rb=[x['decision'] for x in b['native_observations'] if x['kind']=='native_recovery']
            assert ra==rb, 'S/SC unexpectedly changed native Recovery input'
    summary=dict(interface_gate='BLOCKED_MISSING_PROPOSAL_INTERFACE',actual_model_calls=0,
        model_usefulness='UNTESTED',overall='MODEL RECOVERY PROPOSAL USEFULNESS NOT ESTABLISHED',
        native_authorization_integrity='PASS',model_adapter_authorization_integrity='UNTESTED',
        diagnostic_transactions=len(rows),primary_semantic_cases=24,
        primary_native_recovery_commits=sum(r['probe']['authorization']['recovery_authorized'] for r in primary),
        primary_incumbent_retained_without_recovery=sum(r['probe']['authorization']['incumbent_retained'] for r in primary),
        genuine_underlying_recovery_fixtures=8,non_recovery_hold_fixtures=4,
        primary_recovery_target_states=sorted({r['probe']['receipt']['next_state'] for r in primary if r['probe']['authorization']['recovery_authorized']}),
        focused_wrong_recovery_rejected=not rows[24]['probe']['authorization']['committed'],
        ordinary_candidate_value_ignored=True,attached_recovery_slot_invocations=rows[26]['sentinel_calls'],
        unsupported_callback_rejected=not rows[27]['probe']['authorization']['committed'],
        consequence_only_no_recovery_controls=4,model_self_certification_controls='NOT_RUN_INTERFACE_BLOCKED',
        malformed_model_candidate_admission='UNTESTED_NO_INTERFACE',
        protected_false_accepts=0,receipt_rewrites=0,prediction_rewrites=0,bound_violations=0,
        maximum_memory=max(r['probe']['bounds']['memory'] for r in rows),native_object_attempt_limit=RECOVERY_LIMIT,
        no_architecture_or_authorization_changes=True)
    return dict(summary=summary,interface=interface,registration=registration,budget=budget,cases=rows)
