"""Finite, nonrecursive depth-2 trajectory comparison for Horus v0.15."""
from copy import deepcopy
import json
from pathlib import Path

from experiments.base_framework_v0.framework import ACTION_ORDER
from experiments.map_consequence_only_isolation_v0.protocol import parse as parse_consequence
from experiments.model_map_proposal_v0.adapter import MODEL,parse as parse_joint
from experiments.model_proposal_role_composition_v2.protocol import OPTIONS

from .core import digest
from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import file_hash
from .live import CONSEQUENCE_SYSTEM,JOINT_SYSTEM,ModelClient,SessionStore,_canonical,_plain
from .one_step_value import _payload,grounded_transitions
from .problem_manager import ProblemManager
from .relation_routing import RelationEvidenceStore,relation_routed_clients
from .routing import RoutingError

POLICY_PATH=Path(__file__).with_name("depth2_value_policy.json")
V014_RESULTS=Path(__file__).resolve().parents[1]/"research/bounded-longer-horizon-v0/results.json"

def analyze_max_compression(result:dict)->dict:
    routed={int(k):v for k,v in result["downstream_routed"].items()}
    transitions=result["grounded_transitions"]
    vectors={action:[routed[row["continuation_state"]][a] for a in ACTION_ORDER]
             for action,row in transitions.items()}
    maxima={action:max(values) for action,values in vectors.items()}
    distinct=len({tuple(v) for v in vectors.values()})>1
    compressed=len(set(maxima.values()))==1
    return dict(vectors=vectors,maxima=maxima,structures_distinct=distinct,
        maxima_identical=compressed,max_compression_discards_structure=distinct and compressed,
        added_layer_can_add_information=True,
        no_preference_inferred_from_structure=True,model_calls=0)

def compare_trajectories(candidates:dict)->dict:
    best={}; best_actions={}
    for current,rows in candidates.items():
        value=max(tuple(row["sequence"]) for row in rows)
        best[current]=list(value)
        best_actions[current]=[row["second_action"] for row in rows
                               if tuple(row["sequence"])==value]
    current_actions=list(best)
    if len(current_actions)!=2: raise RoutingError("depth-2 route requires two current actions")
    if best[current_actions[0]]==best[current_actions[1]]:
        return dict(outcome="STILL_TIED_AT_DEPTH2",selected_action=None,
                    best=best,best_second_actions=best_actions)
    return dict(outcome="DEPTH2_DISTINGUISHES",
        selected_action=max(current_actions,key=lambda a:tuple(best[a])),
        best=best,best_second_actions=best_actions)

def _joint_request(client,prompt):
    return dict(model=getattr(client,"model_id",MODEL),system=JOINT_SYSTEM,prompt=prompt,
                stream=False,options=dict(OPTIONS["Map"]))

def _consequence_request(client,prompt):
    return dict(model=client.model_id,system=CONSEQUENCE_SYSTEM,prompt=prompt,
        stream=False,options=dict(OPTIONS["Map"]),
        horus_model_identity=_plain(client.horus_model_identity))

def _freeze(store,*,call_id,role,request,metadata):
    return store.append("calls","REQUEST_INTENT",dict(call_id=call_id,role=role,
        request=request,request_sha256=digest(request),**metadata))

def _execute(store,item,parser):
    response=item["client"].generate(item["request"])
    response_env=store.append("calls","RESPONSE",dict(call_id=item["intent"]["record"]["call_id"],
        response=response,response_sha256=digest(response)))
    parsed=None; error=response.get("transport_error")
    if error is None:
        try: parsed=parser(response["raw_output"])
        except (ValueError,TypeError,json.JSONDecodeError) as exc: error=type(exc).__name__
    parsed_env=store.append("calls","PARSED",dict(call_id=item["intent"]["record"]["call_id"],
        parsed=parsed,parse_error=error))
    return parsed,dict(request_sequence=item["intent"]["sequence"],
        response_sequence=response_env["sequence"],parsed_sequence=parsed_env["sequence"],
        request_sha256=digest(item["request"]),valid=parsed is not None)

def evaluate_depth2(store,joint,specialists,routing,transitions,identity):
    history=store.imported_history(); work=[]; consequence_cache={}; second={}
    # Freeze all six joint and twelve independent consequence requests first.
    for current in transitions:
        state=transitions[current]["continuation_state"]
        for action in ACTION_ORDER:
            prompt=_canonical(_payload(history,state,action)); branch=(current,action)
            request=_joint_request(joint,prompt)
            intent=_freeze(store,call_id=f"{identity}:{current}:{action}:J",role="depth2-next-state",
                request=request,metadata=dict(consume_only="next_state",independent_of_consequence=True,
                    hidden_simulator_law_present=False))
            work.append(dict(layer=1,kind="joint",branch=branch,client=joint,request=request,intent=intent))
            for specialist in ("G2","G3"):
                client=specialists[specialist]; request=_consequence_request(client,prompt)
                intent=_freeze(store,call_id=f"{identity}:{current}:{action}:{specialist}",
                    role=f"depth2-consequence:{specialist}",request=request,
                    metadata=dict(consequence_only=True,predicted_next_state_present=False,
                        independent_of_joint_response=True,model_generation_identity=client.horus_model_identity))
                work.append(dict(layer=1,kind="consequence",branch=branch,specialist=specialist,
                                  state=state,action=action,client=client,request=request,intent=intent))
    for item in work:
        parser=(parse_joint if item["kind"]=="joint" else lambda raw:parse_consequence(raw,"C"))
        parsed,proof=_execute(store,item,parser); branch=item["branch"]
        row=second.setdefault(branch,dict(current_action=branch[0],second_action=branch[1]))
        if item["kind"]=="joint":
            row.update(predicted_second_state=None if parsed is None else parsed["next_state"],
                next_state_provenance="MODEL_FORECAST",joint=proof)
        else:
            row.setdefault("specialists",{})[item["specialist"]]=dict(
                consequence=None if parsed is None else parsed["consequence"],**proof)
            consequence_cache[_canonical(item["request"])]=dict(
                consequence=None if parsed is None else parsed["consequence"],proof=proof,
                source_layer=1)
    if any(row.get("predicted_second_state") is None or
           any(not row["specialists"][s]["valid"] for s in ("G2","G3")) for row in second.values()):
        return dict(all_valid=False,calls=len(work),second_branches=list(second.values()))
    for (current,action),row in second.items():
        selected=routing.preview(transitions[current]["continuation_state"],action)["selected_specialist"]
        row["selected_specialist"]=selected
        row["c1"]=row["specialists"][selected]["consequence"]
        row["c1_provenance"]="MODEL_FORECAST"
    # Construct all third-layer requests, reusing only byte-identical consequence requests.
    third_work=[]; third={}; deduplicated=[]
    predicted_states=sorted({row["predicted_second_state"] for row in second.values()})
    for state in predicted_states:
        third[state]={}
        for action in ACTION_ORDER:
            prompt=_canonical(_payload(history,state,action)); third[state][action]={}
            for specialist in ("G2","G3"):
                client=specialists[specialist]; request=_consequence_request(client,prompt)
                key=_canonical(request)
                if key in consequence_cache:
                    cached=consequence_cache[key]
                    third[state][action][specialist]=dict(consequence=cached["consequence"],valid=True,
                        deduplicated=True,exact_request_sha256=digest(request),
                        reused_request_sequence=cached["proof"]["request_sequence"])
                    deduplicated.append(dict(state=state,action=action,specialist=specialist,
                        exact_request_sha256=digest(request),
                        reused_request_sequence=cached["proof"]["request_sequence"]))
                else:
                    call_id=f"{identity}:third:s{state}:{action}:{specialist}"
                    intent=_freeze(store,call_id=call_id,role=f"depth2-third-consequence:{specialist}",
                        request=request,metadata=dict(consequence_only=True,predicted_next_state_field_present=False,
                            finite_terminal_layer=True,model_generation_identity=client.horus_model_identity))
                    third_work.append(dict(layer=2,kind="consequence",state=state,action=action,
                        specialist=specialist,client=client,request=request,intent=intent))
    for item in third_work:
        parsed,proof=_execute(store,item,lambda raw:parse_consequence(raw,"C"))
        third[item["state"]][item["action"]][item["specialist"]]=dict(
            consequence=None if parsed is None else parsed["consequence"],deduplicated=False,**proof)
    all_valid=all(value["valid"] for actions in third.values() for specialists_by_action in actions.values()
                  for value in specialists_by_action.values())
    routed_third={}; selections={}
    if all_valid:
        for state,actions in third.items():
            routed_third[state]={}; selections[state]={}
            for action,values in actions.items():
                selected=routing.preview(state,action)["selected_specialist"]
                selections[state][action]=selected; routed_third[state][action]=values[selected]["consequence"]
    candidates={action:[] for action in transitions}
    if all_valid:
        for (current,action),row in second.items():
            c0=transitions[current]["primary_value"]
            c2=max(routed_third[row["predicted_second_state"]].values())
            candidates[current].append(dict(current_action=current,second_action=action,
                sequence=[c0,row["c1"],c2],grounded_continuation_state=transitions[current]["continuation_state"],
                predicted_second_state=row["predicted_second_state"],provenance=dict(
                    c0="AUTHENTICATED_RECEIPT",state1="AUTHENTICATED_RECEIPT",
                    c1="MODEL_FORECAST",state2="MODEL_FORECAST",c2="MODEL_FORECAST")))
    return dict(all_valid=all_valid,calls=len(work)+len(third_work),second_branches=list(second.values()),
        predicted_states=predicted_states,third=third,routed_third=routed_third,
        third_selections=selections,deduplicated_requests=deduplicated,candidates=candidates,
        horizon_depth=2,recursive_calls=0,behavioral_authority=False,
        hidden_simulator_law_present=False)

def load_policy():
    policy=json.loads(POLICY_PATH.read_text())
    for name,expected in policy["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.15 file changed: {name}")
    for path_key,hash_key in (("preregistration_path","preregistration_sha256"),
                              ("authorization_path","authorization_sha256"),
                              ("analysis_path","analysis_sha256")):
        if file_hash(Path(policy[path_key]))!=policy[hash_key]:
            raise RoutingError(f"v0.15 {path_key} changed")
    return policy

def run(session_path:Path,registry_root:Path,joint=None,specialists=None):
    policy=load_policy(); v014=json.loads(V014_RESULTS.read_text())
    analysis=analyze_max_compression(v014)
    if not analysis["max_compression_discards_structure"]:
        return dict(status="STRUCTURAL_COMPRESSION_DIAGNOSIS",model_calls=0,analysis=analysis)
    if specialists is None: specialists,_=relation_routed_clients(registry_root,device="cuda")
    joint=joint or ModelClient()
    with SessionStore(session_path,True) as store,RelationEvidenceStore(registry_root) as routing,\
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        if store.checkpoint["attempted_decisions"]!=85 or len(store.records["events"])!=54 or \
                store.checkpoint["current_state"]!=2: raise RoutingError("v0.14 endpoint changed")
        manager.bind_session(store); routing.bind_session(store); confidence.bind_session(store)
        problem=manager.applicable(pre_state=2,tied_actions=["ADVANCE","RETREAT"])
        if not problem or problem["problem_id"]!="PR-0002": raise RoutingError("PR-0002 is not applicable")
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        transitions=grounded_transitions(problem)
        manager.authorize_depth2("PR-0002",policy["authorization_sha256"])
        manager.validate_depth2_design("PR-0002",policy["analysis_sha256"])
        before=sum(row["kind"]=="REQUEST_INTENT" for row in store.records["calls"])
        evaluation=evaluate_depth2(store,joint,specialists,routing,transitions,
            f"{store.checkpoint['session_id']}:depth2-v015")
        if evaluation["calls"]>policy["maximum_model_calls"]:
            raise RoutingError("v0.15 call ceiling exceeded")
        if not evaluation["all_valid"]:
            manager.attach_operational(decision_sequence=85,problem_type="EXTERNAL_SERVICE_PROBLEM",
                scope={"kind":"service","service_id":"DEPTH2_MODEL_SERVICE"},owner="MODEL_SERVICE",
                blocked_problem_id="PR-0002")
            return dict(status="INVALID_ROUTE",model_calls=evaluation["calls"],evaluation=evaluation)
        result=compare_trajectories(evaluation["candidates"])
        record=dict(analysis=analysis,transitions=transitions,evaluation=evaluation,
                    comparison=result,maximum_depth=2,training_runs=0,behavioral_executions=0)
        manager.record_depth2_evaluation(problem_id="PR-0002",outcome=result["outcome"],
            selected_action=result["selected_action"],evaluation=record)
        store.append("training","DEPTH2_TRAJECTORY_EVALUATION",record)
        store.save(state=store.checkpoint["current_state"],
                   next_transaction_id=store.checkpoint["next_transaction_id"])
        actual=sum(row["kind"]=="REQUEST_INTENT" for row in store.records["calls"])-before
        if actual!=evaluation["calls"]: raise RoutingError("v0.15 call accounting mismatch")
        if manager.state["problems"]["PR-0003"]!=before_pr3: raise RoutingError("PR-0003 changed")
        return dict(identity=policy["mode"],status=result["outcome"],model_calls=actual,
            analysis=analysis,grounded_transitions=transitions,evaluation=evaluation,
            comparison=result,selected_action=result["selected_action"],execution=None,
            final_problem=deepcopy(manager.state["problems"]["PR-0002"]),
            pr0003_unchanged=True,training_runs=0,behavioral_executions=0,maximum_depth=2)
