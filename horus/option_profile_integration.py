"""One-use PR-0002 behavioral integration of the frozen v0.16 option profile."""
from copy import deepcopy
import json
from pathlib import Path

from .core import digest
from .grounded_exploration import GroundedExplorationRuntime, ExplorerConfidenceStore, GroundedExplorer
from .grounded_learning import file_hash
from .live import ModelClient, SessionStore
from .option_profile import V015_RESULTS, compare_profiles, reconstruct_profiles
from .problem_manager import ProblemManager, ProblemOwnershipRuntime
from .relation_routing import RelationEvidenceStore, relation_routed_clients
from .routing import RoutingError


POLICY_PATH=Path(__file__).with_name("option_profile_integration_policy.json")
V016_ROOT=Path(__file__).resolve().parents[1]/"research/option-profile-dominance-v0"
V016_RESULTS=V016_ROOT/"results.json"


def verify_v016_evidence(policy:dict)->dict:
    manifest=json.loads((V016_ROOT/"evidence-manifest.json").read_text())
    if file_hash(V016_ROOT/"evidence-manifest.json")!=policy["source_manifest_sha256"]:
        raise RoutingError("v0.16 evidence manifest changed")
    for name,expected in manifest["files"].items():
        if file_hash(V016_ROOT/name)!=expected:
            raise RoutingError(f"v0.16 evidence changed: {name}")
    if file_hash(V016_RESULTS)!=policy["source_results_sha256"]:
        raise RoutingError("v0.16 result changed")
    source=json.loads(V015_RESULTS.read_text()); retained=json.loads(V016_RESULTS.read_text())
    profiles=reconstruct_profiles(source); comparison=compare_profiles(profiles)
    if profiles!=retained["profiles"] or comparison!=retained["comparison"] or \
            comparison["outcome"]!="RETREAT_PROFILE_DOMINATES" or \
            comparison["selected_action"]!="RETREAT":
        raise RoutingError("v0.16 dominance does not reconstruct exactly")
    return dict(profiles=profiles,comparison=comparison,retained=retained,
        source_results_sha256=policy["source_results_sha256"],
        source_manifest_sha256=policy["source_manifest_sha256"])


def load_policy()->dict:
    policy=json.loads(POLICY_PATH.read_text())
    for name,expected in policy["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.17 file changed: {name}")
    for path_key,hash_key in (("preregistration_path","preregistration_sha256"),
                              ("authorization_path","authorization_sha256")):
        if file_hash(Path(policy[path_key]))!=policy[hash_key]:
            raise RoutingError(f"v0.17 {path_key} changed")
    if policy["maximum_fresh_decisions"]!=2 or policy["maximum_model_calls"]!=18:
        raise RoutingError("v0.17 live bounds changed")
    return policy


class OptionProfileIntegrationExplorer:
    def __init__(self,ordinary,manager,store,evidence):
        self.ordinary,self.manager,self.store,self.evidence=ordinary,manager,store,evidence
    def derive(self,**kwargs):
        ordinary=self.ordinary.derive(**kwargs)
        return self.manager.prepare_option_profile_integration(store=self.store,
            ordinary_decision=ordinary,pre_state=kwargs["pre_state"],forecasts=kwargs["forecasts"],
            problem_id="PR-0002",profiles=self.evidence["profiles"],
            result=self.evidence["comparison"]["outcome"],
            selected_action=self.evidence["comparison"]["selected_action"],
            profile_evidence_sha256=self.evidence["source_results_sha256"])


class OptionProfileIntegrationRuntime(ProblemOwnershipRuntime):
    def __init__(self,*args,evidence,**kwargs):
        super().__init__(*args,**kwargs)
        self.confidence_store.explorer=OptionProfileIntegrationExplorer(
            GroundedExplorer(self.confidence_store.registry["policy"]),
            self.problem_manager,self.store,evidence)
    def _next_batch(self):
        capture=self.reader.capture(); sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=(f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:"
                     f"option-profile-integration:d{sequence}")
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id

    def execute_ordinary_followup(self):
        self.confidence_store.explorer=GroundedExplorer(self.confidence_store.registry["policy"])
        return GroundedExplorationRuntime.execute_autonomous(self)


def _plain_row(row:dict)->dict:
    receipt=row.get("receipt"); pre_state=row.get("pre_state",row.get("state"))
    return dict(decision_sequence=row["prediction_batch_sequence"],pre_state=pre_state,
        status=row["status"],action=row["explorer"].get("action"),
        reason=row["explorer"].get("reason"),
        realized_consequence=None if receipt is None else receipt["realized_consequence"],
        realized_next_state=None if receipt is None else receipt["next_state"],
        receipt_identity=None if receipt is None else [receipt[k] for k in (
            "source_identity","event_id","epoch","transaction_id")],
        all_predictions_valid=all(v["valid"] for v in row["forecasts"].values()),
        model_calls=row["model_calls"])


def _suffix_check(profiles:dict,row:dict)->dict|None:
    if row["status"]!="AUTHORIZED" or row.get("receipt") is None: return None
    action=row["explorer"].get("action")
    branch=next((r for r in profiles["RETREAT"] if r["second_action"]==action),None)
    if branch is None: return None
    realized=row["receipt"]["realized_consequence"]; predicted=branch["sequence"][1]
    return dict(label="OBSERVED_SUFFIX_PREFIX_CHECK",first_action="RETREAT",
        observed_follow_up_action=action,retained_predicted_c1=predicted,
        realized_follow_up_consequence=realized,match=predicted==realized,
        full_trajectory_validated=False,controls_behavior=False)


def run(session_path:Path,registry_root:Path,joint_client=None,specialists=None)->dict:
    policy=load_policy(); evidence=verify_v016_evidence(policy)
    if specialists is None: specialists,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    with SessionStore(session_path,True) as store,RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        expected=policy["source_checkpoint"]
        if store.checkpoint["attempted_decisions"]!=expected["attempted_decisions"] or \
                len(store.records["events"])!=expected["authorized_executions"] or \
                len(store.records["calls"])!=expected["call_stream_records"] or \
                store.checkpoint["current_state"]!=2:
            raise RoutingError("v0.16 endpoint changed")
        manager.bind_session(store); routing.bind_session(store); confidence.bind_session(store)
        applicable=manager.applicable(pre_state=2,tied_actions=["ADVANCE","RETREAT"])
        if not applicable or applicable["problem_id"]!="PR-0002":
            raise RoutingError("PR-0002 is not the applicable scoped problem")
        before_pr3=deepcopy(manager.state["problems"]["PR-0003"])
        before_calls=sum(r["kind"]=="REQUEST_INTENT" for r in store.records["calls"])
        before_training=len(store.records["training"])
        manager.authorize_option_profile_integration(problem_id="PR-0002",
            authorization_sha256=policy["authorization_sha256"],
            profile_evidence_sha256=policy["source_results_sha256"],
            result=evidence["comparison"]["outcome"],
            selected_action=evidence["comparison"]["selected_action"])
        runtime=OptionProfileIntegrationRuntime(store,joint_client or ModelClient(),specialists,
            relation_registry,routing,confidence,"A",problem_manager=manager,evidence=evidence)
        runtime_boundary=dict(runtime_index=store.checkpoint["runtime_index"],
            epoch=store.checkpoint["current_epoch"],
            source_identity=store.checkpoint["current_source_identity"])
        integration=runtime.execute_autonomous(); followup=None; suffix=None
        if integration["status"]=="AUTHORIZED":
            followup=runtime.execute_ordinary_followup(); suffix=_suffix_check(evidence["profiles"],followup)
            manager.record_option_profile_followup(store=store,row=followup,
                suffix_prefix_check=suffix)
        calls=sum(r["kind"]=="REQUEST_INTENT" for r in store.records["calls"])-before_calls
        decisions=1+(followup is not None)
        if calls!=9*decisions or calls>policy["maximum_model_calls"] or decisions>2:
            raise RoutingError("v0.17 call or decision accounting violated")
        if manager.state["problems"]["PR-0003"]!=before_pr3:
            raise RoutingError("PR-0003 changed")
        receipt=integration.get("receipt"); comparison=None
        if receipt is not None:
            comparison=dict(retained_consequence=1,retained_next_state=1,
                realized_consequence=receipt["realized_consequence"],
                realized_next_state=receipt["next_state"],
                consequence_match=receipt["realized_consequence"]==1,
                next_state_match=receipt["next_state"]==1,
                exact_match=(receipt["realized_consequence"],receipt["next_state"])==(1,1))
        final_problem=deepcopy(manager.state["problems"]["PR-0002"])
        return dict(identity=policy["mode"],status=final_problem.get(
            "option_profile_integration_result","INTEGRATION_FAILED_OPERATIONALLY"),
            behavioral_integration_authorization_sha256=policy["authorization_sha256"],
            profile_evidence_sha256=policy["source_results_sha256"],
            reconstructed_profiles=evidence["profiles"],dominance=evidence["comparison"],
            frozen_selected_action=integration["explorer"].get("action"),
            fresh_decisions=decisions,model_calls=calls,runtime_boundary=runtime_boundary,
            integration=_plain_row(integration),new_retreat_receipt=deepcopy(receipt),
            retained_reality_comparison=comparison,
            ordinary_follow_up=None if followup is None else _plain_row(followup),
            suffix_prefix_check=suffix,final_pr0002=final_problem,pr0003_unchanged=True,
            training_runs=0,training_records_added=len(store.records["training"])-before_training,
            global_explorer_changed=False,new_horizon_added=False,new_representation_added=False,
            counterfactual_advance_executed=False,maximum_decisions=2,maximum_model_calls=18,
            final_checkpoint=deepcopy(store.checkpoint),problem_graph=deepcopy(manager.state))
