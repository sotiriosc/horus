"""String-only role routing around frozen binding and authority components."""
from contextlib import contextmanager
from dataclasses import asdict
import json
import sys
from types import SimpleNamespace

from experiments.composition_input_bindings_v1.adapters import (
    ExplorerBinding, MapBinding, explorer_payload, map_payload, serialize)
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.model_map_proposal_v0.adapter import parse as map_parse
from experiments.model_recovery_proposal_v1.adapter import render as recovery_render, parse as recovery_parse
from experiments.model_map_proposal_v0.boundary import execute
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.base_framework_v0.framework import MapModel
from experiments.base_framework_v1.framework import Recovery, MeasureAuditor, CrossSourceStateAuthorizer
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework, StatusBoundAuthorizer
from .protocol import MODEL, SYSTEMS, OPTIONS, ACTIONS, seed


def records(snapshot): return [SimpleNamespace(**r) for r in snapshot['memory']]


def views(state, snapshot, mapping):
    assert 'UNTRIED' not in json.dumps(snapshot), 'UNKNOWN entered protected storage'
    rs=records(snapshot); e=explorer_payload(state,rs,mapping)
    maps={a:map_payload(state,a,rs,mapping) for a in ACTIONS}
    for item in e['actions']:
        action=mapping[item['action']]
        matching=sorted((r for r in rs if r.pre_state==state and r.action==action),key=lambda r:(r.epoch,r.transaction_id))
        values=item['verified_outcomes']
        assert values==([r.consequence for r in matching] if matching else 'UNTRIED'), 'stale UNKNOWN'
        assert len(maps[action]['VERIFIED_CHRONOLOGICAL_HISTORY'])==len(matching)
        assert all(type(x) is int for x in values) if isinstance(values,list) else values=='UNTRIED'
    return dict(Explorer=e,Map=maps)


class Broker:
    def __init__(self, client, emit=None):
        self.client,self.emit,self.calls=client,emit,[]

    def request(self, descriptor, decision, role, snapshot, prompt, context=None):
        assert len(self.calls)<288
        assert sum(x['role']==role for x in self.calls)<96
        mapping=descriptor['mapping']; state=snapshot['map']['state']
        payload=json.loads(prompt); visible=views(state,snapshot,mapping)
        if role=='Explorer': assert payload==visible['Explorer']
        elif role=='Map':
            admitted=mapping[payload['target_action']]
            assert payload==visible['Map'][admitted]
        else:
            assert context is not None
            assert prompt==recovery_render(context,mapping)
        call=dict(index=len(self.calls),episode=descriptor['episode'],decision=decision,role=role,
            family=descriptor['family'],mapping=mapping,current_state=state,memory=snapshot['memory'],
            model=MODEL,system=SYSTEMS[role],options={**OPTIONS[role],'seed':seed(descriptor,decision,role)},
            input=payload,exact_prompt=prompt,raw_output=None,parsed=None,parse_error=None,
            transport_error=None,response_metadata={})
        result=self.client.generate(call)
        call.update(result)
        if not call['transport_error']:
            try:
                if role=='Explorer':
                    surface,action,error=parse_surface(call['raw_output'],dict(surface_option_order=list(mapping),surface_to_underlying=mapping))
                    call['parsed']=dict(surface=surface,action=action) if not error else None
                    call['parse_error']=error
                else: call['parsed']=(map_parse if role=='Map' else recovery_parse)(call['raw_output'])
            except ValueError as exc:call['parse_error']=str(exc)
        self.calls.append(call)
        if self.emit:self.emit(call)
        if call['transport_error']:raise ValueError('role transport failed; no retry')
        return call['raw_output'],call['response_metadata']


class RoleTransport:
    def __init__(self,broker,descriptor,decision,role,snapshot):
        self.broker,self.descriptor,self.decision,self.role,self.snapshot=broker,descriptor,decision,role,snapshot
        self.context=None

    def generate(self,prompt,role_seed):
        assert role_seed==seed(self.descriptor,self.decision,self.role)
        return self.broker.request(self.descriptor,self.decision,self.role,self.snapshot,prompt,self.context)


class LiveRecovery:
    """Same value-only interface; input comes solely from genuine callback context."""
    def __init__(self,transport,mapping,role_seed):
        self.transport,self.mapping,self.seed=transport,mapping,role_seed
        self.invocations=0

    def __deepcopy__(self,memo):return self

    def propose(self,context):
        self.invocations+=1
        if self.invocations!=1:raise ValueError('no second Recovery request')
        assert context.measurement_matches is False
        self.transport.context=context
        raw,_=self.transport.generate(recovery_render(context,self.mapping),self.seed)
        return recovery_parse(raw)


@contextmanager
def observe():
    events=[]; previous=sys.getprofile();assert previous is None
    codes={RealizedEventFramework._check.__code__:'receipt',MeasureAuditor.verify.__code__:'measure',
        MapModel.quarantine_incumbent.__code__:'quarantine',Recovery.state_candidate.__code__:'native_attempt',
        LiveRecovery.propose.__code__:'proposal',StatusBoundAuthorizer.authorize.__code__:'status_authorizer',
        CrossSourceStateAuthorizer.authorize.__code__:'ordinary_authorizer',MapModel.commit.__code__:'map_commit'}
    def callback(frame,event,value):
        kind=codes.get(frame.f_code)
        if not kind or event!=('call' if kind=='proposal' else 'return'):return
        loc=frame.f_locals;row=dict(kind=kind)
        if kind=='native_attempt':row.update(attempts=loc['self'].attempts,candidate=asdict(value),decision=asdict(loc['decision']))
        elif kind=='proposal':row['context']=asdict(loc['context'])
        elif kind.endswith('authorizer'):
            row.update(candidate=asdict(loc['candidate']),accepted=value,decision=asdict(loc['decision']))
            if kind=='status_authorizer':row['scope']=loc['state_recovery']
        elif kind=='measure':row.update(verified=value,measurement=asdict(loc['measurement']))
        elif kind=='receipt':row['verified']=value is not None
        events.append(row)
    sys.setprofile(callback)
    try:yield events
    finally:sys.setprofile(previous)


def setup(episode):
    world=TestWorld(0,False);boundary=ExternalExecutionBoundary(world,f'COMPOSITION_V1_{episode}')
    return StatusBoundFramework(boundary.reader(),0,1001),boundary,world,{}


def step(bundle,broker,descriptor,decision):
    system,boundary,world,authentic=bundle;before=published(system);mapping=descriptor['mapping']
    state=system.inner.map.current.state; before_views=views(state,before,mapping)
    transports={r:RoleTransport(broker,descriptor,decision,r,before) for r in SYSTEMS}
    recovery=LiveRecovery(transports['Recovery'],mapping,seed(descriptor,decision,'Recovery'))
    system.inner._state_recovery_source=recovery
    system.inner.explorer=ExplorerBinding(transports['Explorer'],mapping,seed(descriptor,decision,'Explorer'))
    base=system.inner.map.base if isinstance(system.inner.map,MapBinding) else system.inner.map
    system.inner.map=MapBinding(base,system.inner.memory,transports['Map'],mapping,seed(descriptor,decision,'Map'))
    start=len(broker.calls)
    with observe() as events:probe=execute(system,boundary,world,authentic,instrument=False)
    calls=broker.calls[start:];assert not probe['errors'],probe['errors']
    assert system.inner.map.memory is system.inner.memory
    after_views=views(state,probe['after'],mapping)
    assert all(x['verified'] for x in events if x['kind'] in ('receipt','measure'))
    roles=[x['role'] for x in calls]
    assert roles in (['Explorer'],['Explorer','Map'],['Explorer','Map','Recovery'])
    if any(c['transport_error'] for c in calls):termination='transport_failure'
    elif any(c['parse_error'] for c in calls):termination='malformed_'+next(c['role'] for c in calls if c['parse_error'])
    elif not probe['authorization']['committed']:termination='wrong_Recovery_rejected'
    else:termination=None
    if probe['authorization']['executed']:
        assert probe['latched_before_execution'] and probe['receipt_unchanged'] and probe['prediction_unchanged']
        ec,mc=calls[:2]
        assert ec['parsed']['action']==probe['prediction']['action']==probe['receipt']['action']
        assert mc['parsed']=={k:probe['prediction'][k] for k in ('next_state','consequence')}
    genuine=bool(probe['receipt'] and probe['receipt']['next_state']!=state and
        any(x['kind']=='measure' and x['measurement']['matches'] is False for x in events))
    assert recovery.invocations==int(genuine)==roles.count('Recovery')
    if genuine:
        kinds=[x['kind'] for x in events]
        positions=[kinds.index(x) for x in ('receipt','measure','quarantine','native_attempt','proposal')]
        assert positions==sorted(positions) and kinds.count('native_attempt')==kinds.count('proposal')==1
        native=next(x for x in events if x['kind']=='native_attempt')
        assert native['attempts']==1 and native['candidate']['status']=='RECOVERING'
        rc=calls[-1];auth=[x for x in events if x['kind']=='status_authorizer']
        valid=not rc['parse_error'] and not rc['transport_error']
        assert len(auth)==int(valid)
        if valid:
            correct=rc['parsed']==probe['receipt']['next_state']
            assert auth[0]['accepted']==correct==probe['authorization']['committed'] and auth[0]['scope']
            for field in ('epoch','transaction_id','pair_decision_id','status'):
                assert auth[0]['candidate'][field]==native['candidate'][field]
    if termination:
        assert not probe['authorization']['committed'] and probe['before']==probe['after']
        assert not probe['authorization']['continued']
        count=len(broker.calls);retry=system.begin_step()
        assert not retry.executed and not retry.committed and not retry.continued and len(broker.calls)==count
        assert published(system)==probe['after']
    transitions=[]
    if probe['authorization']['committed']:
        action=probe['receipt']['action']
        if not before_views['Map'][action]['VERIFIED_CHRONOLOGICAL_HISTORY']:
            alias=next(k for k,v in mapping.items() if v==action)
            old=next(x for x in before_views['Explorer']['actions'] if x['action']==alias)
            new=next(x for x in after_views['Explorer']['actions'] if x['action']==alias)
            assert old['verified_outcomes']=='UNTRIED' and new['verified_outcomes']==[probe['receipt']['realized_consequence']]
            transitions.append(dict(state=state,action=action,before_explorer=old,after_explorer=new,
                before_map=before_views['Map'][action],after_map=after_views['Map'][action]))
    return dict(episode=descriptor['episode'],decision=decision,descriptor=descriptor,call_indices=[c['index'] for c in calls],
        termination=termination,genuine_recovery=genuine,events=events,probe=probe,
        unknown_to_known=transitions,unknown_audit_pass=True)
