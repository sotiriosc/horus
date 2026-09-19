"""Small deterministic repair campaign; external audit is separate from authority."""
from copy import deepcopy
from dataclasses import asdict, replace

from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.model_explorer_contradiction_revision_v0.overlay import changed_consequence
from .framework import RealizedEventFramework, evidence
from .receipt import ExternalExecutionBoundary


class TestWorld:
    """External fixture: same old transition law, registered consequence shift."""
    def __init__(self, state=1, shift=True):
        self.oracle = TrueWorldOracle(state)
        self.shift = shift
        self.last_actual = None

    def execute(self, epoch, transaction_id, action):
        original = self.oracle.execute(epoch, transaction_id, action)
        self.last_actual = changed_consequence(original, self.shift and self.oracle.execution_count > 3)
        return self.last_actual


class LyingRoot(ExternalExecutionBoundary):
    def _reported_event(self, actual):
        # OUT-OF-MODEL ROOT FAILURE: deliberately corrupt the trusted emitter.
        return replace(actual, consequence=1) if actual.action == "HOLD" else actual


def setup(name, state=1, shift=True, lying=False):
    world = TestWorld(state, shift)
    source = (LyingRoot if lying else ExternalExecutionBoundary)(world, "EXTERNAL_" + name)
    system = RealizedEventFramework(source.reader(), state)
    return system, source, world


def published(system):
    core = system.inner
    return dict(map=asdict(core.map.current), map_quarantine=[asdict(x) for x in core.map.quarantine],
                memory=[asdict(x) for x in core.memory.records],
                memory_quarantine=[asdict(x) for x in core.memory.quarantine],
                pairs=[asdict(x) for x in core.pairs.decisions],
                packages=[asdict(x) for x in system.packages], commits=core.metrics["commits"])


def execute(system, source, world, action):
    assert source.reader().current() is None
    old = deepcopy(system.inner.memory.records)
    pending = system.begin_step(forced_action=action)
    assert source.reader().current() is None, "receipt existed at proposal time"
    prediction = deepcopy(pending.prediction)
    receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
    actual = world.last_actual
    before = published(system)
    result = system.submit_package(evidence(receipt))
    system.assert_bounds()
    record = system.inner.memory.records[-1] if result.committed else None
    actual_tuple = (actual.epoch, actual.transaction_id, actual.pre_state, actual.action,
                    actual.next_state, actual.consequence)
    record_tuple = None if record is None else (record.epoch, record.transaction_id,
        record.pre_state, record.action, record.next_state, record.consequence)
    retained = [r for r in system.inner.memory.records if (r.epoch, r.transaction_id) in
                {(x.epoch, x.transaction_id) for x in old}]
    expected_retained = old[-7:] if len(old) == 8 else old
    row = dict(action=action, prediction=asdict(prediction), receipt=asdict(receipt),
               actual=asdict(actual), result=asdict(result),
               record=asdict(record) if record else None,
               receipt_mismatch_accept=bool(result.committed and record_tuple != receipt.binding()[:6]),
               actual_mismatch_accept=bool(result.committed and record_tuple != actual_tuple),
               prediction_unchanged=prediction == system.inner._prediction_at_begin,
               old_records_unchanged=retained == expected_retained,
               commit_delta=system.inner.metrics["commits"] - before["commits"],
               memory_size=len(system.inner.memory.records), pair_size=len(system.inner.pairs.decisions),
               package_size=len(system.packages), trace_size=len(system.inner.trace),
               pending_root_count=int(source.reader().current() is not None),
               published=published(system))
    source.release(receipt)
    return row, receipt


def primary():
    system, source, world = setup("PRIMARY")
    rows = []
    for action in ("HOLD", "ADVANCE", "RETREAT", "HOLD", "ADVANCE"):
        row, _ = execute(system, source, world, action)
        rows.append(row)
        assert row["result"]["committed"] and not row["actual_mismatch_accept"], rows
        assert row["prediction_unchanged"] and row["old_records_unchanged"]
    hold, advance = rows[3:]
    assert (hold["prediction"]["consequence"], hold["receipt"]["realized_consequence"],
            hold["record"]["consequence"]) == (1, -1, -1)
    assert (advance["prediction"]["consequence"], advance["receipt"]["realized_consequence"],
            advance["record"]["consequence"]) == (-1, 1, 1)
    assert not hold["record"]["measurement_matches"]
    assert not advance["record"]["measurement_matches"]
    assert advance["result"]["recovery_authorized"]
    assert [r.consequence for r in system.inner.memory.records if r.action == "HOLD"] == [1, -1]
    assert [r.consequence for r in system.inner.memory.records if r.action == "ADVANCE"] == [-1, 1]
    return rows


ATTACKS = (
    "stale_receipt", "wrong_transaction", "wrong_epoch", "wrong_pre_state", "wrong_action",
    "wrong_consequence", "wrong_event_id", "map_fake", "recovery_fake", "valid_substitution",
    "shared_descendant", "wrong_next_state", "wrong_source", "equal_content_forgery",
    "pre_execution", "failed_recovery", "execution_wrong_transaction", "execution_wrong_epoch",
    "execution_wrong_pre_state", "execution_wrong_action",
)


def attack(name):
    system, source, world = setup("ATTACK_" + name)
    history = []
    for action in ("HOLD", "ADVANCE", "RETREAT"):
        _, receipt = execute(system, source, world, action)
        history.append(receipt)
    if name == "failed_recovery":
        execute(system, source, world, "HOLD")
    pending = system.begin_step(forced_action="ADVANCE" if name == "failed_recovery" else "HOLD")
    receipt = None
    if name != "pre_execution":
        if name == "execution_wrong_pre_state":
            world.oracle = TrueWorldOracle(2)
        receipt = source.execute(pending.epoch + int(name == "execution_wrong_epoch"),
                                 pending.transaction_id + int(name == "execution_wrong_transaction"),
                                 "RETREAT" if name == "execution_wrong_action" else pending.action)
        package = evidence(receipt)
    else:
        package = None
    substitutions = {"wrong_transaction": (0 + 1, pending.transaction_id + 1),
        "wrong_epoch": (0, pending.epoch + 1), "wrong_pre_state": (2, 2),
        "wrong_action": (3, "RETREAT"), "wrong_consequence": (5, 1),
        "wrong_event_id": (6, 99), "wrong_next_state": (4, 2),
        "wrong_source": (7, "MAP")}
    if name in substitutions:
        index, value = substitutions[name]
        binding = list(package.a); binding[index] = value
        package = replace(package, a=tuple(binding), b=tuple(binding))
    if name == "stale_receipt":
        package = evidence(history[0])
    if name in ("map_fake", "recovery_fake", "shared_descendant"):
        # Recovery and Map carry proposals, never authentic event authority.
        fake = replace(receipt, realized_consequence=pending.prediction.consequence)
        package = evidence(fake)
    if name == "equal_content_forgery":
        package = evidence(replace(receipt))
    if name == "valid_substitution":
        other_world = TestWorld(1, False)
        other = ExternalExecutionBoundary(other_world, "EXTERNAL_OTHER_LIFETIME")
        other_receipt = other.execute(pending.epoch, pending.transaction_id, pending.action)
        assert other.reader().current() is other_receipt
        package = evidence(other_receipt)
    before = published(system)
    result = system.submit_package(package, **({"failed_recovery": True} if name == "failed_recovery" else {}))
    after = published(system)
    row = dict(name=name, authentic_receipt=asdict(receipt) if receipt else None,
               payload=asdict(package) if package else None,
               result=asdict(result), before=before, after=after,
               commit_delta=after["commits"] - before["commits"],
               atomic=before == after, continuation=system.inner.continuation_authorized)
    assert not result.committed and not result.continued and not row["continuation"], row
    assert row["atomic"] and row["commit_delta"] == 0, row
    system.assert_bounds()
    if receipt:
        source.release(receipt)
    return row


def run_campaign():
    # Primary exact failure MUST execute before any broader campaign.
    first = primary()
    stationary = []
    for state in range(4):
        for action in ("ADVANCE", "HOLD", "RETREAT"):
            system, source, world = setup(f"STATIONARY_{state}_{action}", state, False)
            row, _ = execute(system, source, world, action)
            assert row["result"]["committed"] and not row["actual_mismatch_accept"]
            assert row["record"]["measurement_matches"]
            stationary.append(row)
    attacks = [attack(name) for name in ATTACKS]
    system, source, world = setup("ROOT_FAILURE", lying=True)
    corrupt_root = [execute(system, source, world, action)[0]
                    for action in ("HOLD", "ADVANCE", "RETREAT", "HOLD")]
    assert corrupt_root[-1]["actual_mismatch_accept"]
    assert not corrupt_root[-1]["receipt_mismatch_accept"]
    system, source, world = setup("BOUNDS", shift=False)
    bounds = []
    for epoch in (1001, 1002):
        if epoch != 1001:
            system.start_epoch(epoch)
        for _ in range(12):
            row, _ = execute(system, source, world, "HOLD")
            bounds.append(row)
            assert row["result"]["committed"] and row["old_records_unchanged"]
    assert len({r["receipt"]["event_id"] for r in bounds}) == 24
    assert system.inner.memory.evictions == 16
    try:
        source.execute(1003, 1, "HOLD")
    except RuntimeError as exc:
        assert str(exc) == "external execution lifetime bound"
    else:
        raise AssertionError("root lifetime not bounded")
    system, source, world = setup("MEMORY", shift=False)
    memory_history = [execute(system, source, world, action)[0]
                      for action in ("HOLD", "ADVANCE", "RETREAT")]
    state = system.inner.map.current.state
    empty = system.inner.explorer.choose(state, [])
    chosen = system.begin_step().action
    assert empty == "ADVANCE" and chosen == "HOLD"
    memory = dict(state=state, without_history=empty, with_authorized_history=chosen,
                  allowed_actions=["ADVANCE", "HOLD", "RETREAT"], steps=memory_history)
    protected = first + stationary + bounds + memory_history
    assert not any(r["receipt_mismatch_accept"] or r["actual_mismatch_accept"] for r in protected)
    summary = dict(
        campaign="realized-event-grounding-v0", model_calls=0,
        campaign_gate="PASS; final classification requires historical regressions",
        primary_transactions=len(first), new_hold_prediction=1, new_hold_realized=-1,
        new_hold_authorized=-1, new_advance_prediction=-1, new_advance_realized=1,
        new_advance_authorized=1, contradictory_history_preserved=True,
        protected_clean_authorizations=len(protected), protected_false_accepts=0,
        protected_receipt_mismatch_accepts=0, prediction_rewrites=0,
        adversarial_cases=len(attacks), adversarial_rejections=len(attacks),
        atomic_rejections=len(attacks), stationary_cases=len(stationary), stationary_passes=len(stationary),
        bounded_rotation_transactions=len(bounds), memory_limit=8, pair_limit=8, package_limit=8,
        observed_memory_max=max(r["memory_size"] for r in protected),
        observed_pair_max=max(r["pair_size"] for r in protected),
        observed_package_max=max(r["package_size"] for r in protected),
        observed_trace_max=max(r["trace_size"] for r in protected),
        pending_root_limit=1, root_lifetime_limit=24, rotation_evictions=16,
        deterministic_memory_behavior_changed=empty != chosen,
        out_of_model_root_failure_cases=1, out_of_model_root_false_accepts=1,
        root_control_label="OUT-OF-MODEL ROOT FAILURE",
        model_contradiction_revision="UNTESTED")
    return dict(summary=summary, primary=first, stationary=stationary, attacks=attacks,
                root_corruption=corrupt_root, bounds=bounds, memory_causality=memory)
