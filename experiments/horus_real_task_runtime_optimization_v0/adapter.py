"""Study task boundary; reuses exact promoted selectors and protected authority."""
from dataclasses import dataclass,asdict
import json
from .runtime import *
from horus.live import SessionStore,ModelClient,Publication,_plain
from horus.core import BoundPredictionMap,digest,unwrap_map
from experiments.base_framework_v0.framework import Prediction
from experiments.realized_event_grounding_v0.framework import evidence
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical
from experiments.grounded_uncertainty_state_v0.worker import new_controller
from experiments.grounded_autonomous_agent_v0_2.worker import all_assessments,state_view,rows_of
from grounded_state import AuthenticatedMemory,RelationKey,derive_relation_state
from grounded_agent.empirical_policy import integrated_decide
from grounded_agent.policy import promoted_decide
from grounded_agent.empirical_adapter import authenticated_projection,recommendation
from experiments.grounded_stagnation_escape_promotion_controlled_v0.worker import context
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import qualifying_suffix
from experiments.grounded_authority_autonomous_agent_v0.protocol import relation_type,ACTION_OPTIONS,MODEL as ORDINARY

def bind_task_metadata():
 # Only application relation typing is supplied. Every imported relation_type is the
 # identical function object and reads this one registry; S/E eligibility is untouched.
 from experiments.grounded_autonomous_agent_v0 import protocol
 protocol.EMPIRICAL_RELATIONS=tuple(f'{p}:{a}' for p in range(4) for a in CANDIDATES)
 assert all(relation_type(r).value=='EMPIRICAL' for r in protocol.EMPIRICAL_RELATIONS)

def consequence(measurement,reference_seconds,margin):
 if not measurement['valid'] or measurement.get('resource_violation') or measurement.get('error'):return -1
 ratio=measurement['wall_seconds']/reference_seconds
 return 1 if ratio<=1-margin else 0 if ratio<=1+margin else -1

def park_ordinary():
 value=http('/api/generate',dict(model=ORDINARY,stream=False,options={**ACTION_OPTIONS,'num_gpu':0}),timeout=180,base='http://127.0.0.1:11434')
 if not value.get('done') or value.get('response'):raise InfrastructureError('ordinary model load-only parking failed')
 idle()

@dataclass(frozen=True)
class ExecutedRuntimeEvent:
 epoch:int
 transaction_id:int
 pre_state:int
 action:str
 next_state:int
 consequence:int

class RuntimeWorld:
 def __init__(self,state,action,execute,reference_seconds,margin):
  self.state=state;self.action=action;self.execute_runtime=execute;self.reference_seconds=reference_seconds;self.margin=margin;self.measurement=None
 def execute(self,epoch,transaction_id,action):
  if action!=self.action or self.measurement is not None:raise RuntimeError('frozen action changed or repeated')
  # Only this completed real execution can produce a receipt outcome.
  self.measurement=self.execute_runtime(action)
  value=consequence(self.measurement,self.reference_seconds,self.margin)
  return ExecutedRuntimeEvent(epoch,transaction_id,self.state,action,self.state,value)

def execute_protected(store,memory,index,choice,world,global_index,workload):
 action,source,route,info,assessments,suffix=choice;state=store.checkpoint['current_state']
 controller=new_controller(store,'A');controller._active=Publication(world,controller._active.framework)
 core=controller._active.framework.inner
 # Neutral forecast is not evidence and is never put in durable Memory as an outcome.
 core.map=BoundPredictionMap(unwrap_map(core.map),Prediction(core.epoch,core.next_transaction_id,state,action,state,0))
 pending=controller.begin_step(action)
 assert pending.action==action and controller._source.reader().current() is None
 receipt=controller.execute_pending();result=controller.submit_package(evidence(receipt))
 if not result.committed or not result.continued or result.status.value!='AUTHORIZED':raise RuntimeError('protected authorization rejected actual execution')
 core=controller._active.framework.inner;assert controller._active.framework.packages[-1].receipt is receipt
 r=_plain(asdict(receipt));record=_plain(asdict(core.memory.records[-1]));m=world.measurement
 event=dict(study='HORUS_REAL_TASK_RUNTIME_OPTIMIZATION_V0',session_id=store.checkpoint['session_id'],decision_index=index,execution_kind='AUTONOMOUS_EXECUTION',action_source=source,receipt=r,receipt_identity=list(receipt.identity()),receipt_provenance_sha256=digest(r),authorization_status=result.status.value,authorization_reason=result.reason,memory_record=record,source_scope=dict(runtime_index=store.checkpoint['runtime_index'],source_identity=receipt.source_identity),runtime_measurement=m,measurement_sha256=digest(m),global_schedule_index=global_index,workload=workload)
 envelope=store.append('events','AUTHORIZED_REALIZED_EVENT',event)
 admission=AuthenticatedMemory(store,memory).append(envelope,f'C:D{index:02d}')
 after=state_view(derive_relation_state(AuthenticatedMemory(store,memory),RelationKey(state,action),relation_type(f'{state}:{action}')))
 row=dict(decision_id=f'C:D{index:02d}',index=index,state=state,selected_action=action,decision_source=source,policy_route=route['route'],policy_reason=route['reason'],admissible_actions=route['candidates'],grounded_assessments_before=assessments,selected_grounded_before=assessments[action],known_values_before=route['known_values'],action_parse_status=info['status'],action_call_id=info['call_id'],raw_action_output_sha256=info['raw_output_sha256'],action_model_latency_seconds=info['latency_seconds'],grounded_after=after,suffix_before=suffix,realized=dict(next_state=receipt.next_state,consequence=receipt.realized_consequence),receipt_identity=list(receipt.identity()),receipt_provenance_sha256=event['receipt_provenance_sha256'],event_identity=admission['event_identity'],event_stream_sequence=envelope['sequence'],measurement_sha256=digest(m))
 store.append('training','AUTONOMOUS_AGENT_DECISION',row)
 store.save(state=receipt.next_state,next_transaction_id=core.next_transaction_id,completed_step=True,attempted_decision=True)
 controller.release(receipt);memory.reconcile(store)
 return dict(decision=row,event=event,authenticated_event_envelope_sha256=digest(envelope),measurement=m)

def snapshot(store,memory):
 history=authenticated_projection(store,memory);i=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))+1;ctx=context(store,memory,i)
 return dict(checkpoint=store.checkpoint.copy(),stream_hashes={n:file_sha(store.directory/f) for n,f in store.STREAMS.items()},memory=memory.checkpoint(),state=store.checkpoint['current_state'],assessments=ctx['assessments'],suffix=qualifying_suffix(store,memory),e=recommendation(ctx,history),history_sha256=digest(history))
