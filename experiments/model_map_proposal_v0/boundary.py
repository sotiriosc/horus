"""Read-only observation around the unchanged latch/execution/publication path."""
from copy import deepcopy
from dataclasses import asdict
from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import observe, receipt_provenance
from experiments.realized_event_grounding_v0.campaign import published
from experiments.realized_event_grounding_v0.framework import evidence


def execute(system, source, world, authentic, faults=None, instrument=True):
    before = published(system)
    metrics = deepcopy(system.inner.metrics)
    executions = world.oracle.execution_count
    root_absent = source.reader().current() is None
    pending = system.begin_step()  # deterministic Explorer, original Map.predict -> latch
    errors = []
    if not hasattr(pending,"prediction"):
        after = published(system)
        try: system.assert_bounds()
        except (AssertionError,ValueError,RuntimeError): errors.append("bound_violation")
        if before != after or world.oracle.execution_count != executions or source.reader().current() is not None:
            errors.append("malformed_proposal_publication")
        if pending.committed or pending.executed or pending.continued or system.inner.continuation_authorized:
            errors.append("failed_proposal_continuation")
        return dict(prediction=None, actual=None, receipt=None, before=before, after=after,
            authorization=asdict(pending), observations=[], provenance=receipt_provenance(system,authentic),
            commit_delta=after["commits"]-before["commits"], metric_delta={},
            latched_before_execution=False, prediction_unchanged=True, receipt_unchanged=True,
            old_history_unchanged=before["memory"]==after["memory"], measurement_matches=None,
            bounds=dict(memory=len(system.inner.memory.records),pairs=len(system.inner.pairs.decisions),
                packages=len(system.packages),trace=len(system.inner.trace),pending_authentic=0,
                map_quarantine=len(system.inner.map.quarantine),memory_quarantine=len(system.inner.memory.quarantine)),
            errors=errors)
    if published(system) != before:
        errors.append("direct_protected_mutation")
    prediction = asdict(pending.prediction)
    latched = (prediction==asdict(system.inner._prediction_at_begin) and root_absent
               and source.reader().current() is None and world.oracle.execution_count==executions)
    receipt = source.execute(pending.epoch,pending.transaction_id,pending.action)
    original_receipt = asdict(receipt);actual = asdict(world.last_actual)
    authentic[(receipt.epoch,receipt.transaction_id)] = receipt
    with observe(instrument) as observations:
        result = system.submit_package(evidence(receipt),**(faults or {}))
    after = published(system)
    provenance = receipt_provenance(system,authentic)
    prediction_unchanged = asdict(system.inner._prediction_at_begin)==prediction
    receipt_unchanged = source.reader().current() is receipt and asdict(receipt)==original_receipt
    old_unchanged = after["memory"][:len(before["memory"])]==before["memory"]
    expected = prediction["next_state"]==receipt.next_state and prediction["consequence"]==receipt.realized_consequence
    record = system.inner.memory.records[-1] if result.committed else None
    fields = ((record.epoch,record.transaction_id,record.pre_state,record.action,record.next_state,record.consequence)
              if record else None)
    actual_fields = tuple(actual[k] for k in ("epoch","transaction_id","pre_state","action","next_state","consequence"))
    for failed,name in (
        (not latched,"latch_not_before_execution"),
        (result.committed and fields!=actual_fields,"protected_false_accept"),
        (result.committed and fields!=receipt.binding()[:6],"receipt_mismatch_accept"),
        (result.committed and record.measurement_matches!=expected,"incorrect_measure_publication"),
        (not prediction_unchanged,"prediction_rewrite"),
        (not receipt_unchanged,"receipt_rewrite"),
        (not old_unchanged,"historical_receipt_rewrite"),
        (not all(p["exact_authentic_object"] and p["full_binding_verified"] for p in provenance),"provenance_failure"),
        (not result.committed and (after!=before or result.continued or system.inner.continuation_authorized),"atomicity_failure"),
    ):
        if failed: errors.append(name)
    try: system.assert_bounds()
    except (AssertionError,ValueError,RuntimeError): errors.append("bound_violation")
    row = dict(prediction=prediction,actual=actual,receipt=original_receipt,
        before=before,after=after,authorization=asdict(result),observations=observations,
        provenance=provenance,commit_delta=after["commits"]-before["commits"],
        metric_delta={k:system.inner.metrics[k]-v for k,v in metrics.items()},
        latched_before_execution=latched,prediction_unchanged=prediction_unchanged,
        receipt_unchanged=receipt_unchanged,old_history_unchanged=old_unchanged,
        measurement_matches=record.measurement_matches if record else None,
        bounds=dict(memory=len(system.inner.memory.records),pairs=len(system.inner.pairs.decisions),
            packages=len(system.packages),trace=len(system.inner.trace),pending_authentic=1,
            map_quarantine=len(system.inner.map.quarantine),memory_quarantine=len(system.inner.memory.quarantine)),errors=errors)
    source.release(receipt)
    return row
