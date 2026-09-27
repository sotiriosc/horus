"""Zero-inference OPTION_PROFILE_DOMINANCE evaluation for Horus v0.16."""
from copy import deepcopy
import json
from pathlib import Path

from experiments.base_framework_v0.framework import ACTION_ORDER

from .core import digest
from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import file_hash
from .live import SessionStore
from .problem_manager import ProblemManager
from .relation_routing import RelationEvidenceStore
from .routing import RoutingError

POLICY_PATH=Path(__file__).with_name("option_profile_policy.json")
V015_RESULTS=Path(__file__).resolve().parents[1]/"research/deeper-horizon-route-design-v0/results.json"
EXPECTED_PROVENANCE=dict(c0="AUTHENTICATED_RECEIPT",state1="AUTHENTICATED_RECEIPT",
    c1="MODEL_FORECAST",state2="MODEL_FORECAST",c2="MODEL_FORECAST")

def reconstruct_profiles(result:dict)->dict:
    if result.get("status")!="STILL_TIED_AT_DEPTH2" or result.get("maximum_depth")!=2:
        raise RoutingError("v0.15 result is not the registered complete depth-2 source")
    rows=result.get("branches")
    if not isinstance(rows,list): raise RoutingError("v0.15 branches missing")
    profiles={"ADVANCE":[],"RETREAT":[]}; identities=set()
    for row in rows:
        current=row.get("current_action"); second=row.get("second_action")
        sequence=row.get("sequence"); provenance=row.get("provenance")
        if current not in profiles or second not in ACTION_ORDER or \
                not isinstance(sequence,list) or len(sequence)!=3 or \
                any(type(value) is not int or value not in (-1,0,1) for value in sequence) or \
                provenance!=EXPECTED_PROVENANCE:
            raise RoutingError("invalid option-profile trajectory")
        identity=(current,second)
        if identity in identities: raise RoutingError("duplicate second-action identity")
        identities.add(identity)
        profiles[current].append(dict(current_action=current,second_action=second,
            sequence=list(sequence),provenance=deepcopy(provenance)))
    if any({row["second_action"] for row in profile}!=set(ACTION_ORDER)
           or len(profile)!=len(ACTION_ORDER) for profile in profiles.values()):
        raise RoutingError("option profile is incomplete")
    for current in profiles:
        profiles[current]=sorted(profiles[current],key=lambda row:
            (tuple(-value for value in row["sequence"]),ACTION_ORDER.index(row["second_action"])))
        for rank,row in enumerate(profiles[current],1): row["rank"]=rank
    return profiles

def compare_profiles(profiles:dict)->dict:
    left,right=profiles["ADVANCE"],profiles["RETREAT"]
    if len(left)!=len(right): raise RoutingError("profiles have unequal finite cardinality")
    comparisons=[]
    for a,b in zip(left,right):
        av,bv=tuple(a["sequence"]),tuple(b["sequence"])
        relation="EQUAL" if av==bv else ("ADVANCE_GREATER" if av>bv else "RETREAT_GREATER")
        comparisons.append(dict(rank=a["rank"],advance=list(av),retreat=list(bv),relation=relation))
    advance_dominates=all(row["relation"] in ("EQUAL","ADVANCE_GREATER") for row in comparisons) and \
        any(row["relation"]=="ADVANCE_GREATER" for row in comparisons)
    retreat_dominates=all(row["relation"] in ("EQUAL","RETREAT_GREATER") for row in comparisons) and \
        any(row["relation"]=="RETREAT_GREATER" for row in comparisons)
    if advance_dominates: outcome,selected="ADVANCE_PROFILE_DOMINATES","ADVANCE"
    elif retreat_dominates: outcome,selected="RETREAT_PROFILE_DOMINATES","RETREAT"
    elif all(row["relation"]=="EQUAL" for row in comparisons): outcome,selected="PROFILES_EQUAL",None
    else: outcome,selected="PROFILES_INCOMPARABLE",None
    return dict(outcome=outcome,selected_action=selected,rank_comparisons=comparisons,
        partial_order=True,scalar_value=None)

def load_policy():
    policy=json.loads(POLICY_PATH.read_text())
    for name,expected in policy["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.16 file changed: {name}")
    for path_key,hash_key in (("preregistration_path","preregistration_sha256"),
                              ("authorization_path","authorization_sha256")):
        if file_hash(Path(policy[path_key]))!=policy[hash_key]:
            raise RoutingError(f"v0.16 {path_key} changed")
    if file_hash(V015_RESULTS)!=policy["source_results_sha256"]:
        raise RoutingError("v0.15 source result changed")
    return policy

def run(session_path:Path,registry_root:Path)->dict:
    policy=load_policy(); source=json.loads(V015_RESULTS.read_text())
    profiles=reconstruct_profiles(source); comparison=compare_profiles(profiles)
    with SessionStore(session_path,True) as store,RelationEvidenceStore(registry_root) as routing,\
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        if store.checkpoint["attempted_decisions"]!=85 or len(store.records["events"])!=54 or \
                len(store.records["calls"])!=2394 or store.checkpoint["current_state"]!=2:
            raise RoutingError("v0.15 endpoint changed")
        manager.bind_session(store);routing.bind_session(store);confidence.bind_session(store)
        problem=manager.applicable(pre_state=2,tied_actions=["ADVANCE","RETREAT"])
        if not problem or problem["problem_id"]!="PR-0002": raise RoutingError("PR-0002 is not applicable")
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        manager.authorize_option_profile("PR-0002",policy["authorization_sha256"])
        evaluation=dict(profiles=profiles,comparison=comparison,
            source_results_sha256=policy["source_results_sha256"],model_calls=0,
            behavioral_executions=0,hidden_world_information_used=False,
            complete_multisets=True,duplicates_preserved=True,
            global_explorer_objective_changed=False)
        manager.record_option_profile(problem_id="PR-0002",outcome=comparison["outcome"],
            selected_action=comparison["selected_action"],evaluation=evaluation)
        store.append("training","OPTION_PROFILE_EVALUATION",evaluation)
        store.save(state=store.checkpoint["current_state"],next_transaction_id=store.checkpoint["next_transaction_id"])
        if manager.state["problems"]["PR-0003"]!=before_pr3: raise RoutingError("PR-0003 changed")
        return dict(identity=policy["mode"],status=comparison["outcome"],profiles=profiles,
            comparison=comparison,selected_action=comparison["selected_action"],model_calls=0,
            behavioral_executions=0,execution=None,final_problem=deepcopy(manager.state["problems"]["PR-0002"]),
            pr0003_unchanged=True,source_v015_unchanged=True)
