"""Prospective v0.13 continuation after canonical problem replay."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from .grounded_exploration import ExplorerConfidenceStore
from .grounded_learning import file_hash
from .live import ModelClient,SessionStore,_canonical
from .problem_manager import ProblemManager,ProblemOwnershipRuntime
from .relation_routing import RelationEvidenceStore,relation_routed_clients
from .routing import RoutingError

POLICY_PATH=Path(__file__).with_name("problem_ownership_run_policy.json")

class V013Runtime(ProblemOwnershipRuntime):
    """Preserve v0.11's sequence binding after the historical repaired batch."""
    def _next_batch(self):
        capture=self.reader.capture(); sequence=self.store.checkpoint["attempted_decisions"]+1
        decision_id=(f"{self.store.checkpoint['session_id']}:e{capture['epoch']}:"
                     f"problem-ownership:d{sequence}")
        return capture,self.map.forecasts(capture,decision_id),sequence,decision_id

def load_policy():
    policy=json.loads(POLICY_PATH.read_text())
    for name,expected in policy["frozen_sha256"].items():
        if file_hash(Path(__file__).with_name(name))!=expected:
            raise RoutingError(f"frozen v0.13 file changed: {name}")
    return policy

def classify(rows,route_exercised,operational_failure,maximum):
    if operational_failure: return "OPERATIONAL_FAILURE"
    if route_exercised and len(rows)>=2:
        last=rows[-1]
        same=(last["pre_state"]==1 and last["explorer"]["reason"]=="EXPLOIT_TIED_MAXIMUM")
        return "DEADLOCK_RETURNED_AFTER_ALLOWANCE" if same else "ROUTE_EXECUTED_NORMAL_OPERATION_RESUMED"
    if len(rows)==maximum: return "ROUTE_NEVER_ELIGIBLE"
    return None

def run(session_path:Path,registry_root:Path,joint_client=None,specialist_clients=None):
    policy=load_policy(); prereg_hash=file_hash(Path(policy["preregistration_path"]))
    if prereg_hash!=policy["preregistration_sha256"]: raise RoutingError("preregistration hash changed")
    if specialist_clients is None:
        specialist_clients,relation_registry=relation_routed_clients(registry_root,device="cuda")
    else:
        from .relation_routing import load_relation_routing_registry
        relation_registry=load_relation_routing_registry(registry_root)
    joint=joint_client or ModelClient(); before=joint.requests
    specialist_before={k:v.requests for k,v in specialist_clients.items()}
    with SessionStore(session_path,True) as session,RelationEvidenceStore(registry_root) as routing, \
            ExplorerConfidenceStore(registry_root) as confidence,ProblemManager(registry_root) as manager:
        if session.checkpoint["attempted_decisions"]!=policy["source_attempted_decisions"] or \
                len(session.records["events"])!=policy["source_authorized_executions"] or \
                session.checkpoint["current_state"]!=1:
            raise RoutingError("v0.11 source endpoint changed")
        manager.bind_session(session)
        p=manager.applicable(pre_state=1,tied_actions=["ADVANCE","HOLD"])
        if not p or p["problem_id"]!="PR-0003" or p["lifecycle_state"]!="OPEN":
            raise RoutingError("retrospective state-1 problem is absent")
        if not manager.state["deadlock_route_enabled"]:
            manager.preregister_deadlock_route(prereg_hash)
        elif manager.state["deadlock_preregistration_sha256"]!=prereg_hash:
            raise RoutingError("different deadlock preregistration already bound")
        session.configure_regime("A",False)
        runtime=V013Runtime(session,joint,specialist_clients,relation_registry,
            routing,confidence,"A",problem_manager=manager)
        rows=[]; route_exercised=False; operational=None; status=None
        boundary=dict(runtime_index=session.checkpoint["runtime_index"],
            epoch=session.checkpoint["current_epoch"],
            source_identity=session.checkpoint["current_source_identity"])
        for _ in range(policy["maximum_fresh_decisions"]):
            row=runtime.execute_autonomous(); rows.append(row)
            if row["explorer"]["reason"]=="DEADLOCK_INFORMATION_PROBE": route_exercised=True
            if row["explorer"]["reason"]=="INVALID_MAP_COMPONENT":
                applicable=row["explorer"].get("problem_id")
                manager.attach_operational(decision_sequence=row["prediction_batch_sequence"],
                    problem_type="EXTERNAL_SERVICE_PROBLEM",
                    scope={"kind":"service","service_id":"MODEL_SERVICE"},owner="MODEL_SERVICE",
                    blocked_problem_id=applicable)
                operational={"decision_sequence":row["prediction_batch_sequence"],
                             "classification":"MODEL_SERVICE"}
            status=classify(rows,route_exercised,operational,policy["maximum_fresh_decisions"])
            if status: break
        calls=joint.requests-before+sum(v.requests-specialist_before[k]
                                       for k,v in specialist_clients.items())
        if calls!=9*len(rows) or calls>policy["maximum_model_calls"]:
            raise RoutingError("v0.13 call accounting violated")
        return dict(identity=policy["mode"],status=status,rows=_plain_rows(rows),
            fresh_decisions=len(rows),model_calls=calls,route_exercised=route_exercised,
            operational_failure=operational,runtime_boundary=boundary,
            final_checkpoint=deepcopy(session.checkpoint),problem_graph=deepcopy(manager.state),
            training_runs=0,objective_changed=False,models_changed=False,
            hidden_simulator_information_available_to_manager=False)

def _plain_rows(rows):
    result=[]
    for row in rows:
        receipt=row.get("receipt")
        # Authorized GroundedExplorationRuntime rows expose the captured state as
        # ``state``; abstention rows expose the same schema field as ``pre_state``.
        # Normalize only this public result view.  Durable behavioral records are
        # not rewritten.
        pre_state=row.get("pre_state",row.get("state"))
        if type(pre_state) is not int:
            raise RoutingError("runtime result lacks a valid pre-state")
        result.append(dict(decision_sequence=row["prediction_batch_sequence"],
            pre_state=pre_state,status=row["status"],action=row["explorer"].get("action"),
            reason=row["explorer"].get("reason"),problem_id=row["explorer"].get("problem_id"),
            capability_assessment=row["explorer"].get("capability_assessment"),
            realized_consequence=None if receipt is None else receipt["realized_consequence"],
            realized_next_state=None if receipt is None else receipt["next_state"],
            all_predictions_valid=all(v["valid"] for v in row["forecasts"].values())))
    return result
