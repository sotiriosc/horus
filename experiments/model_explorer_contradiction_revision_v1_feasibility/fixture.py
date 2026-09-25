"""External fixture/audit around the unchanged realized-event repair.

No regime flag, audit archive or expected history enters framework authority.
The profiling observer only reads original function returns; it supplies no input.
"""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict
import sys

from experiments.base_framework_v0.framework import MapModel
from experiments.base_framework_v1.framework import Recovery
from experiments.model_explorer_contradiction_revision_v0.preflight import SEQUENCE, STAGES
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework, evidence
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary

MAPPINGS = {"O1": {"ADVANCE": "K1", "HOLD": "K2", "RETREAT": "K3"},
            "O2": {"ADVANCE": "Q7", "HOLD": "M4", "RETREAT": "Z2"}}
EXPECTED = {
    "CONTROL/H0": {"HOLD": [1], "ADVANCE": [-1]},
    "SHIFT/H0": {"HOLD": [1], "ADVANCE": [-1]},
    "CONTROL/H1": {"HOLD": [1, 1], "ADVANCE": [-1, -1]},
    "SHIFT/H1": {"HOLD": [1, -1], "ADVANCE": [-1, 1]},
    "CONTROL/H2": {"HOLD": [1, 1, 1], "ADVANCE": [-1, -1]},
    "SHIFT/H2": {"HOLD": [1, -1, -1], "ADVANCE": [-1, 1]},
}


@contextmanager
def observe(enabled):
    events = []
    codes = {Recovery.state_candidate.__code__: "recovery_state_proposal",
             Recovery.measurement.__code__: "recovery_measurement",
             Recovery.memory_record.__code__: "recovery_memory",
             MapModel.quarantine_incumbent.__code__: "map_quarantine"}

    def callback(frame, event, value):
        if event == "return" and frame.f_code in codes:
            name = codes[frame.f_code]
            content = ([asdict(x) for x in frame.f_locals["self"].quarantine]
                       if name == "map_quarantine" else asdict(value) if value else None)
            events.append(dict(kind=name, value=content))

    previous = sys.getprofile()
    if enabled:
        if previous is not None:
            raise RuntimeError("existing profiling observer; cannot establish noninterference")
        sys.setprofile(callback)
    try:
        yield events
    finally:
        if enabled:
            sys.setprofile(previous)


def receipt_provenance(system, authentic):
    rows = []
    for record, pair, package in zip(system.inner.memory.records,
                                      system.inner.pairs.decisions, system.packages):
        root = authentic.get((record.epoch, record.transaction_id))
        same_object = package.receipt is root and root is not None
        content = root.binding()[:6] if root else None
        record_content = (record.epoch, record.transaction_id, record.pre_state,
                          record.action, record.next_state, record.consequence)
        ok = (same_object and content == record_content and package.package_id == root.identity()
              and package.pair_decision_id == pair.pair_decision_id
              and system.inner.memory.matches(record, pair))
        rows.append(dict(epoch=record.epoch, transaction_id=record.transaction_id,
                         pair_decision_id=pair.pair_decision_id, package_id=package.package_id,
                         receipt=asdict(package.receipt), exact_authentic_object=same_object,
                         full_binding_verified=ok))
    return rows


def projection(system, mapping):
    """Pure Memory projection; package supplies event ID only, never a new fact."""
    packages = {(p.receipt.epoch, p.receipt.transaction_id): p for p in system.packages}
    return [dict(epoch=r.epoch, transaction_id=r.transaction_id,
                 event_id=packages[(r.epoch, r.transaction_id)].receipt.event_id,
                 surface_action=mapping[r.action], consequence=r.consequence)
            for r in sorted(system.inner.memory.records, key=lambda r: (r.epoch, r.transaction_id))
            if r.authorization == "AUTHORIZED" and r.pre_state == 1
            and r.action in ("HOLD", "ADVANCE")]


def step(system, source, world, action, authentic, instrument):
    before = published(system)
    metrics = deepcopy(system.inner.metrics)
    root_absent_at_proposal = source.reader().current() is None
    pending = system.begin_step(forced_action=action)
    if not hasattr(pending, "prediction"):
        raise RuntimeError("proposal rejected before external execution")
    prediction = asdict(pending.prediction)
    root_absent_at_proposal &= source.reader().current() is None
    receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
    actual = asdict(world.last_actual)
    original_receipt = asdict(receipt)
    authentic[(receipt.epoch, receipt.transaction_id)] = receipt  # external audit only, ≤7
    package = evidence(receipt)
    root_valid_before = package.receipt is source.reader().current()
    with observe(instrument) as observations:
        result = system.submit_package(package)
    after = published(system)
    record = system.inner.memory.records[-1] if result.committed else None
    actual_fields = (actual["epoch"], actual["transaction_id"], actual["pre_state"],
                     actual["action"], actual["next_state"], actual["consequence"])
    record_fields = ((record.epoch, record.transaction_id, record.pre_state, record.action,
                      record.next_state, record.consequence) if record else None)
    old_unchanged = after["memory"][:len(before["memory"])] == before["memory"]
    prediction_unchanged = asdict(system.inner._prediction_at_begin) == prediction
    receipt_unchanged = (source.reader().current() is receipt and asdict(receipt) == original_receipt)
    provenance = receipt_provenance(system, authentic)
    prediction_conflict = prediction["consequence"] != receipt.realized_consequence
    history_conflict = any(r["pre_state"] == receipt.pre_state and r["action"] == receipt.action
                          and r["consequence"] != receipt.realized_consequence for r in before["memory"])
    contradiction_opportunity = prediction_conflict or history_conflict
    errors = []
    for failed, name in (
        (not root_absent_at_proposal or not root_valid_before or not receipt_unchanged, "receipt_origin_or_substitution"),
        (result.committed and record_fields != actual_fields, "protected_false_accept"),
        (result.committed and record_fields != receipt.binding()[:6], "receipt_mismatch_accept"),
        (not old_unchanged, "old_history_rewritten"),
        (not prediction_unchanged, "prediction_rewritten"),
        (not all(p["full_binding_verified"] for p in provenance), "provenance_failure"),
        (not result.committed, "authenticated_contradiction_rejected" if contradiction_opportunity else "clean_event_rejected"),
        (not result.committed and (before != after or result.continued or system.inner.continuation_authorized), "atomicity_failure"),
    ):
        if failed:
            errors.append(name)
    try:
        system.assert_bounds()
    except (AssertionError, ValueError, RuntimeError):
        errors.append("bounds_failure")
    bounds = dict(memory=len(system.inner.memory.records), pairs=len(system.inner.pairs.decisions),
                  packages=len(system.packages), pending_authentic=int(source.reader().current() is not None),
                  trace=len(system.inner.trace), map_quarantine=len(system.inner.map.quarantine),
                  memory_quarantine=len(system.inner.memory.quarantine))
    row = dict(action=action, prediction=prediction, actual=actual, receipt=original_receipt,
               submitted_package=asdict(package), authorization=asdict(result), before=before, after=after,
               provenance=provenance, observations=observations,
               metric_delta={k: system.inner.metrics[k]-v for k, v in metrics.items()},
               commit_delta=after["commits"]-before["commits"], prediction_unchanged=prediction_unchanged,
               receipt_unchanged=receipt_unchanged, old_history_unchanged=old_unchanged,
               prediction_conflict=prediction_conflict, history_conflict=history_conflict,
               contradiction_opportunity=contradiction_opportunity, bounds=bounds, errors=errors)
    source.release(receipt)
    return row


def run_fixture(instrument=True):
    rows, stages, starts = [], {}, {}
    first_failure = None
    for index, arm in enumerate(("CONTROL", "SHIFT"), 1):
        world = TestWorld(1, arm == "SHIFT")
        source = ExternalExecutionBoundary(world, f"EXTERNAL_LIFETIME_{index}")
        system = RealizedEventFramework(source.reader(), 1, 1001)
        authentic = {}
        starts[arm] = published(system)
        for number, action in enumerate(SEQUENCE, 1):
            try:
                row = step(system, source, world, action, authentic, instrument)
            except Exception as exc:
                first_failure = dict(arm=arm, transaction_id=number, boundary=type(exc).__name__, reason=str(exc))
                break
            row.update(arm=arm, transaction_id=number)
            rows.append(row)
            if row["errors"]:
                first_failure = dict(arm=arm, transaction_id=number, errors=row["errors"])
                break
            if number in STAGES:
                key = arm + "/" + STAGES[number]
                history = {a: [r.consequence for r in system.inner.memory.records
                               if r.pre_state == 1 and r.action == a] for a in ("HOLD", "ADVANCE")}
                stages[key] = dict(history=history, protected=published(system),
                    provenance=receipt_provenance(system, authentic),
                    projection={family: projection(system, mapping) for family, mapping in MAPPINGS.items()},
                    current_state=system.inner.map.current.state)
                if history != EXPECTED[key] or system.inner.map.current.state != 1:
                    first_failure = dict(arm=arm, transaction_id=number, errors=["required_history_or_state_mismatch"])
                    break
        if first_failure:
            break
    matched, differences = [], []
    control = [r for r in rows if r["arm"] == "CONTROL"]
    shift = [r for r in rows if r["arm"] == "SHIFT"]
    for a, b in zip(control, shift):
        keys = ("epoch", "transaction_id", "pre_state", "action", "next_state", "event_id")
        same = all(a["receipt"][k] == b["receipt"][k] for k in keys)
        shape = (list(a["submitted_package"]) == list(b["submitted_package"])
                 and [len(a["submitted_package"][k]) for k in ("a", "b", "c")]
                 == [len(b["submitted_package"][k]) for k in ("a", "b", "c")])
        matched.append(dict(transaction_id=a["transaction_id"], identity_shape_matches=same, package_shape_matches=shape))
        differences.append(dict(transaction_id=a["transaction_id"],
            differing_receipt_fields=[k for k in a["receipt"] if a["receipt"][k] != b["receipt"][k]],
            control_map_version=a["after"]["map"]["version"], shift_map_version=b["after"]["map"]["version"],
            control_recovery=a["authorization"]["recovery_authorized"], shift_recovery=b["authorization"]["recovery_authorized"],
            control_measure=a["after"]["memory"][-1]["measurement_matches"], shift_measure=b["after"]["memory"][-1]["measurement_matches"]))
    errors = [e for r in rows for e in r["errors"]]
    # Step failures already occur in rows; do not count the stop summary twice.
    b_errors = {"receipt_origin_or_substitution", "protected_false_accept", "receipt_mismatch_accept",
                "old_history_rewritten", "prediction_rewritten", "provenance_failure", "authenticated_contradiction_rejected"}
    gate = "B" if b_errors.intersection(errors) else "C" if first_failure else "PASS_PENDING_REPLAY_AND_REGRESSIONS"
    if not first_failure and (len(rows) != 14 or len(stages) != 6 or starts["CONTROL"] != starts["SHIFT"]
                              or not all(m["identity_shape_matches"] and m["package_shape_matches"] for m in matched)):
        gate = "C"
    summary = dict(campaign_gate=gate, first_failure=first_failure, actual_model_calls=0, parser_controls=0,
        behavioral_revision="UNTESTED", transactions=len(rows), commits=sum(r["authorization"]["committed"] for r in rows),
        completed_stages=list(stages), histories={k:v["history"] for k,v in stages.items()},
        protected_false_accepts=errors.count("protected_false_accept"), receipt_mismatch_accepts=errors.count("receipt_mismatch_accept"),
        prediction_rewrites=sum(not r["prediction_unchanged"] for r in rows),
        history_rewrites=sum(not r["old_history_unchanged"] for r in rows),
        contradiction_opportunities=sum(r["contradiction_opportunity"] for r in rows),
        contradiction_accepts=sum(r["contradiction_opportunity"] and r["authorization"]["committed"] for r in rows),
        rejection_opportunities=sum(not r["authorization"]["committed"] for r in rows),
        provenance_stage_checks=sum(len(v["provenance"]) for v in stages.values()),
        visible_target_provenance_checks=sum(sum(p["receipt"]["pre_state"]==1 and p["receipt"]["action"] in ("HOLD","ADVANCE") for p in v["provenance"]) for v in stages.values()),
        maxima={k:max((r["bounds"][k] for r in rows),default=0) for k in ("memory","pairs","packages","pending_authentic","trace","map_quarantine","memory_quarantine")},
        recovery_authorizations=sum(r["authorization"]["recovery_authorized"] for r in rows),
        identity_matching=matched, arm_metadata=differences)
    return dict(summary=summary, starts=starts, stages=stages, steps=rows)
