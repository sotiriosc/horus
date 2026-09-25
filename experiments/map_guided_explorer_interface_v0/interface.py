"""Read-only forecast/choice binding. No transport, executor or authorizer here."""
from dataclasses import dataclass,asdict
import hashlib,json
from experiments.base_framework_v0.framework import Prediction
from experiments.model_map_proposal_v0.adapter import parse as parse_map
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.composition_input_bindings_v1.adapters import checked_mapping,ACTIONS
from experiments.cross_episode_initialization_boundary_v1.projection import map_payload,serialize
from experiments.cross_episode_stale_memory_feasibility_v0.campaign import audit,plain
from experiments.realized_event_grounding_v0.campaign import published
from experiments.model_proposal_role_composition_v2.protocol import SYSTEMS
EXPLORER_SYSTEM='Choose the allowed action whose current Map prediction has the highest predicted consequence. Reply with exactly one allowed action and no explanation.'
MAP_SYSTEM=SYSTEMS['Map']

def digest(value):return hashlib.sha256(serialize(value).encode()).hexdigest()

class ProposalFailure(RuntimeError):
    """Bounded code only, never raw source/error text."""
    pass

@dataclass(frozen=True)
class CurrentActionForecast:
    action_alias:str
    underlying_action:str
    proposal_id:str
    epoch:int
    state:int
    decision_id:str
    memory_sha256:str
    snapshot_sha256:str
    input_sha256:str
    prediction:Prediction

@dataclass(frozen=True)
class ExplorerProposal:
    action_alias:str
    underlying_action:str
    epoch:int
    state:int
    decision_id:str
    selected_forecast:CurrentActionForecast
    # No receipt, authorization, verified outcome, state/Memory writer or capability.

class AuthenticatedReader:
    """Trusted caller-owned reader. Sources receive serialized values only.

    Verifies already realized historical evidence, never queries future truth.
    This is not a hostile same-process Python sandbox or cryptographic attestation.
    """
    def __init__(self,controller,authentic,executions):
        self._controller=controller;self._authentic=authentic;self._executions=executions;self._source=controller._source
    def capture(self,mapping):
        c=self._controller;f=c._active.framework;core=f.inner
        if c._source is not self._source or c._registered_source is not self._source:raise ProposalFailure('SOURCE_CHANGED')
        if core.pending is not None or c._source.reader().current() is not None:raise ProposalFailure('IN_FLIGHT_EVENT')
        if not core.continuation_authorized or not core.map.current.valid:raise ProposalFailure('NO_CURRENT_STATE')
        proof=audit(c,self._authentic,self._executions)
        snapshot=plain(dict(protected=published(f),epoch=core.epoch,next_transaction_id=core.next_transaction_id,source_identity=c._source_identity,
            source_event_count=c._source._ExternalExecutionBoundary__count))
        state=core.map.current.state
        return dict(snapshot=snapshot,snapshot_sha256=digest(snapshot),memory_sha256=digest(snapshot['protected']['memory']),
            state=state,epoch=core.epoch,transaction_id=core.next_transaction_id,provenance=proof,
            map_inputs={a:map_payload(state,a,core.memory.records,mapping) for a in ACTIONS})

class ForecastCoordinator:
    """Trusted proposal-stage owner: one live decision; no cross-decision cache."""
    def __init__(self,reader,mapping,scope):
        if not isinstance(scope,str) or not scope:raise ValueError('non-model decision scope required')
        self.reader=reader;self.mapping=checked_mapping(mapping);self.scope=scope;self.generation=0;self.active=None
    def begin(self):
        self.generation+=1;self.active=None
        session=ForecastSession(self,f'{self.scope}:d{self.generation:06d}');self.active=session
        return session

class ForecastSession:
    def __init__(self,owner,decision_id):
        self.owner=owner;self.decision_id=decision_id;self.context=owner.reader.capture(owner.mapping)
        self._forecasts=[];self._issued={};self.phase='NEW';self.map_attempts=0;self.explorer_attempts=0
        self.map_requests=[];self.explorer_request=None;self.failure=None;self.proposal=None
    def stop(self,code):
        self.phase='FAILED';self.failure=code;raise ProposalFailure(code)
    def fresh(self):
        if self.owner.active is not self:self.stop('STALE_DECISION')
        try:now=self.owner.reader.capture(self.owner.mapping)
        except Exception:self.stop('CONTEXT_INVALID')
        if now['snapshot_sha256']!=self.context['snapshot_sha256']:self.stop('STALE_CONTEXT')
    def collect(self,source):
        if self.phase!='NEW':self.stop('COLLECTION_ALREADY_ATTEMPTED')
        self.phase='COLLECTING';self.fresh()
        for action in ACTIONS:  # Canonical underlying order independent of aliases.
            self.fresh();body=self.context['map_inputs'][action];prompt=serialize(body);pid=f'{self.decision_id}:Map:{action}'
            self.map_requests.append(dict(proposal_id=pid,action=action,system=MAP_SYSTEM,prompt=prompt));self.map_attempts+=1
            try:raw=source(MAP_SYSTEM,prompt)
            except Exception:self.stop('MAP_SOURCE_FAILURE')
            self.fresh()
            try:parsed=parse_map(raw)
            except (ValueError,TypeError):self.stop('INVALID_MAP')
            p=Prediction(self.context['epoch'],self.context['transaction_id'],self.context['state'],action,**parsed)
            forecast=CurrentActionForecast(body['target_action'],action,pid,self.context['epoch'],self.context['state'],self.decision_id,
                self.context['memory_sha256'],self.context['snapshot_sha256'],digest(body),p)
            self._forecasts.append(forecast);self._issued[action]=forecast
        self.phase='READY';return self.view()
    def view(self):
        self.fresh()
        if self.phase not in ('READY','DONE'):self.stop('FORECASTS_UNAVAILABLE')
        if len(self._forecasts)!=3 or {f.underlying_action for f in self._forecasts}!=set(ACTIONS):self.stop('MISSING_FORECAST')
        for f in self._forecasts:
            if type(f) is not CurrentActionForecast or self._issued.get(f.underlying_action) is not f:self.stop('FORECAST_IDENTITY')
            if (f.epoch,f.state,f.decision_id,f.memory_sha256,f.snapshot_sha256)!=(self.context['epoch'],self.context['state'],self.decision_id,self.context['memory_sha256'],self.context['snapshot_sha256']):self.stop('STALE_FORECAST')
            if self.owner.mapping.get(f.action_alias)!=f.underlying_action or f.prediction.action!=f.underlying_action:self.stop('ACTION_IDENTITY')
        by_action={f.underlying_action:f for f in self._forecasts}
        return dict(state=self.context['state'],actions=[dict(action=alias,map_prediction=dict(next_state=by_action[a].prediction.next_state,consequence=by_action[a].prediction.consequence)) for alias,a in self.owner.mapping.items()])
    def choose(self,source):
        if self.phase!='READY':self.stop('EXPLORER_UNAVAILABLE')
        view=self.view();values=[r['map_prediction']['consequence'] for r in view['actions']]
        # v0 scope: unique maxima only. Ties stop, no retry or hidden tie policy.
        if values.count(max(values))!=1:self.stop('TIED_MAXIMUM')
        prompt=serialize(view);self.explorer_request=dict(system=EXPLORER_SYSTEM,prompt=prompt);self.explorer_attempts+=1;self.phase='CHOOSING'
        try:raw=source(EXPLORER_SYSTEM,prompt)
        except Exception:self.stop('EXPLORER_SOURCE_FAILURE')
        self.fresh()
        _,action,_=parse_surface(raw,dict(surface_option_order=list(self.owner.mapping),surface_to_underlying=self.owner.mapping))
        if action is None:self.stop('INVALID_EXPLORER')
        f=self._issued[action]
        self.proposal=ExplorerProposal(f.action_alias,action,f.epoch,f.state,self.decision_id,f);self.phase='DONE'
        return self.proposal
    def validate(self,proposal):
        self.view()
        if self.phase!='DONE' or proposal is not self.proposal:self.stop('PROPOSAL_IDENTITY')
        return True  # Fresh proposal only; NOT execution or state authorization.
    def evidence(self):
        return dict(decision_id=self.decision_id,context=self.context,phase=self.phase,failure=self.failure,
            forecasts=[asdict(f) for f in self._forecasts],map_requests=self.map_requests,explorer_request=self.explorer_request,
            synthetic_Map_invocations=self.map_attempts,synthetic_Explorer_invocations=self.explorer_attempts,
            proposal=None if self.proposal is None else asdict(self.proposal))
