"""One explicitly authorized consequence-only continuation layer for Horus v0.14."""
from copy import deepcopy
import json
from pathlib import Path

from experiments.base_framework_v0.framework import ACTION_ORDER
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS

from .core import MAPPING,digest
from .grounded_exploration import ExplorerConfidenceStore,GroundedExplorer
from .grounded_learning import file_hash
from .live import CONSEQUENCE_SYSTEM,ModelClient,SessionStore,_canonical,_plain
from .problem_manager import ProblemManager,ProblemOwnershipRuntime
from .relation_routing import RelationEvidenceStore,relation_routed_clients
from .routing import RoutingError

POLICY_PATH=Path(__file__).with_name("one_step_value_policy.json")

def compare_pairs(primary:dict,secondary:dict)->dict:
    actions=list(primary)
    if len(actions)!=2: raise RoutingError("one-step route requires exactly two actions")
    if primary[actions[0]]!=primary[actions[1]]:
        selected=max(actions,key=lambda a:primary[a])
        return dict(outcome="PRIMARY_ALREADY_DISTINGUISHES",selected_action=selected,
                    secondary_consulted=False)
    if secondary[actions[0]]==secondary[actions[1]]:
        return dict(outcome="STILL_TIED_AT_ONE_STEP",selected_action=None,
                    secondary_consulted=True)
    return dict(outcome="ONE_STEP_DISTINGUISHES",
        selected_action=max(actions,key=lambda a:(primary[a],secondary[a])),
        secondary_consulted=True)

def grounded_transitions(problem:dict)->dict:
    result={}
    for action in problem["scope"]["tied_action_set"]:
        rows=problem.get("probe_evidence",{}).get(action,[])
        if not rows or rows[-1].get("receipt_is_authenticated") is not True:
            raise RoutingError("MISSING_GROUNDED_TRANSITION")
        row=rows[-1]
        result[action]=dict(primary_value=row["realized_consequence"],
            continuation_state=row["realized_next_state"],
            receipt_identity=row["receipt_identity"],grounded=True)
    return result

def _payload(history,state,action):
    alias=next(k for k,v in MAPPING.items() if v==action)
    rows=[dict(epoch=r["receipt"]["epoch"],transaction_id=r["receipt"]["transaction_id"],
        surface_action=alias,next_state=r["receipt"]["next_state"],
        consequence=r["receipt"]["realized_consequence"]) for r in history
        if r["receipt"]["pre_state"]==state and r["receipt"]["action"]==action]
    return dict(state=state,target_action=alias,VERIFIED_CHRONOLOGICAL_HISTORY=rows)

def downstream_forecasts(store,specialists,routing,states,identity):
    history=store.imported_history(); work=[]
    # Freeze every consequence-only request before any response is obtained.
    for state in states:
        for action in ACTION_ORDER:
            payload=_payload(history,state,action); prompt=_canonical(payload)
            for specialist in ("G2","G3"):
                client=specialists[specialist]
                request=dict(model=client.model_id,system=CONSEQUENCE_SYSTEM,prompt=prompt,
                    stream=False,options=dict(OPTIONS["Map"]),
                    horus_model_identity=_plain(client.horus_model_identity))
                call_id=f"{identity}:s{state}:{action}:{specialist}"
                intent=store.append("calls","REQUEST_INTENT",dict(call_id=call_id,
                    role=f"one-step-consequence:{specialist}",request=request,
                    request_sha256=digest(request),consequence_only=True,
                    predicted_next_state_present=False,independent_of_other_specialist=True,
                    model_generation_identity=client.horus_model_identity))
                work.append(dict(state=state,action=action,specialist=specialist,
                                 client=client,request=request,intent=intent))
    values={}; public=[]
    for item in work:
        response=item["client"].generate(item["request"])
        response_env=store.append("calls","RESPONSE",dict(call_id=item["intent"]["record"]["call_id"],
            response=response,response_sha256=digest(response)))
        parsed=None; error=response.get("transport_error")
        if error is None:
            try: parsed=parse_consequence(response["raw_output"],"C")
            except (ValueError,TypeError,json.JSONDecodeError) as exc: error=type(exc).__name__
        parsed_env=store.append("calls","PARSED",dict(call_id=item["intent"]["record"]["call_id"],
            parsed=parsed,parse_error=error))
        value=None if parsed is None else parsed["consequence"]
        values[(item["state"],item["action"],item["specialist"])]=value
        public.append(dict(state=item["state"],action=item["action"],specialist=item["specialist"],
            consequence=value,valid=parsed is not None,request_sha256=digest(item["request"]),
            request_sequence=item["intent"]["sequence"],response_sequence=response_env["sequence"],
            parsed_sequence=parsed_env["sequence"]))
    routed={}; selections={}
    for state in states:
        routed[state]={}; selections[state]={}
        for action in ACTION_ORDER:
            selected=routing.preview(state,action)["selected_specialist"]
            selections[state][action]=selected
            routed[state][action]=values[(state,action,selected)]
    valid=all(row["valid"] for row in public)
    return dict(predictions=public,routed=routed,selections=selections,all_valid=valid,
        calls=len(work),horizon_layers=1,recursive_calls=0,predicted_next_state_inputs=0)

class OneStepExplorer:
    def __init__(self,ordinary,manager,store,problem_id,selected_action):
        self.ordinary,self.manager,self.store=ordinary,manager,store
        self.problem_id,self.selected_action=problem_id,selected_action
    def derive(self,**kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.manager.prepare_one_step_execution(store=self.store,
            ordinary_decision=ordinary,pre_state=kwargs["pre_state"],forecasts=kwargs["forecasts"],
            problem_id=self.problem_id,selected_action=self.selected_action)

class OneStepExecutionRuntime(ProblemOwnershipRuntime):
    def __init__(self,*args,problem_id,selected_action,**kwargs):
        super().__init__(*args,**kwargs)
        self.confidence_store.explorer=OneStepExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),
            self.problem_manager,self.store,problem_id,selected_action)
    def _next_batch(self):
        capture=self.reader.capture(); sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:one-step:d{sequence}"
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id

def load_policy():
    p=json.loads(POLICY_PATH.read_text())
    for name,expected in p["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.14 file changed: {name}")
    prereg=Path(p["preregistration_path"])
    if file_hash(prereg)!=p["preregistration_sha256"]: raise RoutingError("v0.14 preregistration changed")
    authorization=Path(p["authorization_path"])
    if file_hash(authorization)!=p["authorization_sha256"]:
        raise RoutingError("v0.14 authorization changed")
    return p

def run(session_path:Path,registry_root:Path,joint_client=None,specialists=None):
    policy=load_policy()
    if specialists is None: specialists,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    with SessionStore(session_path,True) as store,RelationEvidenceStore(registry_root) as routing,\
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        if store.checkpoint["attempted_decisions"]!=policy["source_attempted_decisions"] or \
                len(store.records["events"])!=policy["source_authorized_executions"] or \
                store.checkpoint["current_state"]!=policy["source_state"]:
            raise RoutingError("v0.13 endpoint changed")
        manager.bind_session(store); before_calls=sum(r["kind"]=="REQUEST_INTENT" for r in store.records["calls"])
        problem=manager.applicable(pre_state=2,tied_actions=["ADVANCE","RETREAT"])
        if not problem or problem["problem_id"]!="PR-0002": raise RoutingError("PR-0002 is not applicable")
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        transitions=grounded_transitions(problem)
        if len({row["primary_value"] for row in transitions.values()})!=1:
            raise RoutingError("one-step route requires a grounded immediate tie")
        manager.authorize_one_step("PR-0002",policy["authorization_sha256"])
        states=[transitions[a]["continuation_state"] for a in problem["scope"]["tied_action_set"]]
        downstream=downstream_forecasts(store,specialists,routing,states,
            f"{store.checkpoint['session_id']}:one-step-v014")
        if downstream["calls"]!=12: raise RoutingError("downstream call bound changed")
        if not downstream["all_valid"]:
            manager.attach_operational(decision_sequence=policy["source_attempted_decisions"],
                problem_type="EXTERNAL_SERVICE_PROBLEM",
                scope={"kind":"service","service_id":"CONSEQUENCE_SPECIALISTS"},owner="MODEL_SERVICE",
                blocked_problem_id="PR-0002")
            return dict(status="INVALID_DOWNSTREAM_PREDICTION",transitions=transitions,
                        downstream=downstream,model_calls=12,execution=None)
        primary={a:transitions[a]["primary_value"] for a in transitions}
        secondary={a:max(downstream["routed"][transitions[a]["continuation_state"]].values())
                   for a in transitions}
        result=compare_pairs(primary,secondary)
        evaluation=dict(primary=primary,secondary=secondary,
            pairs={a:[primary[a],secondary[a]] for a in primary},
            grounded_transitions=transitions,downstream=downstream,
            maximum_horizon_depth=1,downstream_values_are_predictions=True,
            continuation_states_are_authenticated_receipts=True)
        manager.record_one_step_evaluation(problem_id="PR-0002",outcome=result["outcome"],
            selected_action=result["selected_action"],evaluation=evaluation)
        store.append("training","ONE_STEP_CONTINUATION_EVALUATION",evaluation)
        store.save(state=store.checkpoint["current_state"],
                   next_transaction_id=store.checkpoint["next_transaction_id"])
        execution=None
        if result["outcome"]=="ONE_STEP_DISTINGUISHES":
            runtime=OneStepExecutionRuntime(store,joint_client or ModelClient(),specialists,
                relation_registry,routing,confidence,"A",problem_manager=manager,
                problem_id="PR-0002",selected_action=result["selected_action"])
            execution=runtime.execute_autonomous()
        total=sum(r["kind"]=="REQUEST_INTENT" for r in store.records["calls"])-before_calls
        if total>policy["maximum_model_calls"]: raise RoutingError("v0.14 call ceiling exceeded")
        if manager.state["problems"]["PR-0003"]!=before_pr3: raise RoutingError("PR-0003 changed")
        return dict(identity=policy["mode"],status=result["outcome"],model_calls=total,
            transitions=transitions,downstream=downstream,pairs=evaluation["pairs"],
            selected_action=result["selected_action"],execution=execution,
            final_problem=deepcopy(manager.state["problems"]["PR-0002"]),
            pr0003_unchanged=True,training_runs=0,maximum_horizon_depth=1)
