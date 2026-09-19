"""Ordinary frozen execution plus external diagnostic audit; no model transport."""

from dataclasses import asdict
import copy

from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.base_framework_v2.campaign import make_evidence, independently_separate
from experiments.base_framework_v2.witness_c import encode_relation
from experiments.model_explorer_integration_v0.campaign import protected_state
from .overlay import ConsequenceOverlay

SEQUENCE = ("HOLD", "ADVANCE", "RETREAT", "HOLD", "ADVANCE", "RETREAT", "HOLD")
STAGES = {3: "H0", 6: "H1", 7: "H2"}
IDENTITY = ("epoch", "transaction_id", "pre_state", "action", "next_state", "consequence")


def chronological_projection(state, records, mapping):
    """Pure projection of retained records, not a model adapter or new authority."""
    inverse = {action: token for token, action in mapping.items()}
    return [dict(transaction_id=r["transaction_id"], surface_action=inverse[r["action"]],
                 consequence=r["consequence"])
            for r in sorted(records, key=lambda r: (r["epoch"], r["transaction_id"]))
            if r["authorization"] == "AUTHORIZED" and r["pre_state"] == state
            and r["action"] in ("HOLD", "ADVANCE")]


def step(system, world, action):
    before = protected_state(system)
    metrics_before = copy.deepcopy(system.inner.metrics)
    begun = system.begin_step(forced_action=action)
    if not hasattr(begun, "prediction"):
        raise RuntimeError("preflight proposal rejected before world execution")
    latched = asdict(begun.prediction)
    actual = world.execute(begun.epoch, begun.transaction_id, begun.action)
    original, _, regime = world.events[-1]
    rounds = []
    while True:
        a, b, c = make_evidence(system, actual, "clean", begun.reobservations > 0)
        rounds.append(dict(a=asdict(a), b=asdict(b), c=asdict(c)))
        result = system.submit_package(a, b, c)
        system.assert_bounds()
        if not result.needs_reobservation:
            break
        begun = system.pending
        if begun is None or len(rounds) >= 2:
            raise RuntimeError("unexpected reobservation boundary")
    after = protected_state(system)
    event = asdict(actual)
    committed = after["memory"][-1] if result.committed else None
    false_accept = bool(committed and any(committed[k] != event[k] for k in IDENTITY))
    retained = { (r["epoch"], r["transaction_id"]): r for r in after["memory"] }
    old_preserved = all(retained.get((r["epoch"], r["transaction_id"])) == r for r in before["memory"])
    evidence_matches = (
        all(getattr(x.receipt, "observed_next_state") == actual.next_state and
            getattr(x.receipt, "observed_consequence") == actual.consequence for x in (a,b))
        and c.relation_code == encode_relation(actual.next_state, actual.consequence)
    )
    unchanged_prediction = asdict(system.inner._prediction_at_begin) == latched
    prediction_matches_actual = all(latched[k] == event[k] for k in IDENTITY)
    identities = [(r["epoch"], r["transaction_id"]) for r in after["memory"]]
    fresh_identity = all(x.receipt.epoch == actual.epoch and x.receipt.transaction_id == actual.transaction_id for x in (a,b)) and c.epoch == actual.epoch and c.transaction_id == actual.transaction_id
    errors = []
    if false_accept: errors.append("committed_memory_disagrees_with_actual_event")
    if not evidence_matches: errors.append("frozen_evidence_does_not_authenticate_actual_consequence")
    if not result.committed: errors.append("actual_event_not_authorized")
    if not old_preserved: errors.append("old_history_changed_or_evicted")
    if not unchanged_prediction: errors.append("prediction_latch_rewritten")
    if len(set(identities)) != len(identities): errors.append("duplicate_authorization")
    if not fresh_identity: errors.append("stale_provenance")
    metric_delta = {k: system.inner.metrics[k]-v for k,v in metrics_before.items()}
    return dict(action=action, regime=regime, original_frozen_event=asdict(original), actual_event=event,
        prediction_at_begin=latched, prediction_after=asdict(system.inner._prediction_at_begin),
        prediction_matches_actual=prediction_matches_actual, prediction_latch_unchanged=unchanged_prediction,
        before=before, evidence_rounds=rounds, authorization=asdict(result), after=after,
        external_false_accept=false_accept, evidence_matches_actual=evidence_matches,
        old_records_preserved=old_preserved, fresh_identity=fresh_identity,
        declared_process_separation=independently_separate(system.registry,(a.process_id,b.process_id,c.process_id)),
        inner_metric_delta=metric_delta, inner_metrics=copy.deepcopy(system.inner.metrics),
        package_metrics=copy.deepcopy(system.metrics), trace=[asdict(r) for r in system.trace],
        package_trace=list(system.package_trace), map_quarantine=[asdict(r) for r in system.map.quarantine],
        memory_quarantine=[asdict(r) for r in system.memory.quarantine],
        recovery_authorized=result.recovery_authorized, incumbent_retained=result.incumbent_retained,
        integrity_errors=errors, bounds=dict(memory=len(system.memory.records), pairs=len(system.pairs.decisions),
            packages=len(system.packages), trace=len(system.trace), package_trace=len(system.package_trace),
            staged=len(system.staged), map_quarantine=len(system.map.quarantine), memory_quarantine=len(system.memory.quarantine)))


def run_preflight():
    rows = []; stages = {}; failed = None
    for arm in ("CONTROL", "SHIFT"):
        system = EvidenceProvenanceFramework(initial_state=1, epoch=1001)
        world = ConsequenceOverlay(arm)
        for number, action in enumerate(SEQUENCE, 1):
            row = step(system, world, action)
            row.update(arm=arm, setup_step=number)
            rows.append(row)
            if row["integrity_errors"]:
                failed = dict(arm=arm, transaction_id=number, action=action, errors=row["integrity_errors"])
                break
            if number in STAGES:
                stage = STAGES[number]
                assert system.map.current.state == world.state == 1
                records = row["after"]["memory"]
                stages[arm+"/"+stage] = dict(memory=records, protected_state=row["after"],
                    chronological_example=chronological_projection(1,records,{"K1":"ADVANCE","K2":"HOLD","K3":"RETREAT"}))
        if failed is not None:
            break
    feasible = failed is None and len(stages) == 6
    summary = dict(feasibility="FEASIBLE" if feasible else "INFEASIBLE_UNDER_FROZEN_FRAMEWORK",
        requested_world_change_integrity="PASS" if feasible else "FAIL", first_failure=failed,
        planned_real_model_calls=144, actual_real_model_calls=0, actual_parser_controls=0,
        behavioral_study="NOT_RUN", behavioral_revision="UNTESTED", overall_replication="NOT_ESTABLISHED",
        scripted_preflight_transactions=len(rows), ordinary_commits=sum(r["authorization"]["committed"] for r in rows),
        external_false_accepts=sum(r["external_false_accept"] for r in rows),
        changed_actual_events=sum(r["actual_event"] != r["original_frozen_event"] for r in rows),
        safely_authorized_changed_events=sum(r["actual_event"] != r["original_frozen_event"] and r["authorization"]["committed"] and not r["integrity_errors"] for r in rows),
        completed_safe_fixtures=list(stages), prediction_latch_rewrites=sum(not r["prediction_latch_unchanged"] for r in rows),
        old_history_rewrites_or_evictions=sum(not r["old_records_preserved"] for r in rows),
        recovery_authorizations=sum(r["recovery_authorized"] for r in rows),
        stopped_before_inference=True, no_model_transport_implemented=True,
        model_rates={f:dict(status="UNTESTED",opportunities=0,rate=None) for f in ("O1","O2")},
        maxima={k:max(r["bounds"][k] for r in rows) for k in rows[0]["bounds"]})
    return dict(summary=summary, stages=stages, steps=rows)
