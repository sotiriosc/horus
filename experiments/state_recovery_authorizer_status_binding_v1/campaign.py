"""Frozen status comparisons, inherited interface replay and atomicity controls."""
from contextlib import contextmanager
from dataclasses import asdict, replace
import inspect
import sys

from experiments.base_framework_v0 import framework as v0
from experiments.base_framework_v1 import framework as native
from experiments.realized_event_grounding_v0.framework import SharedReceiptPairGate, RealizedEventFramework
from experiments.state_recovery_proposal_interface_v1 import campaign as prior
from experiments.state_recovery_proposal_interface_v1.framework import RecoveryInterfaceCore, StateRecoveryFramework
from experiments.state_recovery_proposal_interface_v1.equivalence import run_case as default_case
from .framework import StatusBoundAuthorizer, StatusBoundCore, StatusBoundFramework
from .preflight import check as preflight

serialized = prior.serialized


def structure():
    old = inspect.getsource(RecoveryInterfaceCore._complete_pair)
    new = inspect.getsource(StatusBoundCore._complete_pair)
    assert new == old.replace('self.state_authorizer.authorize(selected, decision)',
           'self.state_authorizer.authorize(selected, decision, state_recovery=recovery_authorized)')
    assert StatusBoundCore._state_recovery_candidate is RecoveryInterfaceCore._state_recovery_candidate
    assert StatusBoundFramework.submit_package is RealizedEventFramework.submit_package
    assert StatusBoundAuthorizer.__bases__ == (native.CrossSourceStateAuthorizer,)
    return dict(only_callsite_change='trusted state_recovery=recovery_authorized keyword',
                sole_new_predicate='if state_recovery and candidate.status != RECOVERING: reject',
                proposal_helper_unchanged=True, publication_unchanged=True,
                remaining_predicates_inherited=True, epoch_reset_preserves_repaired_type=True)


def setup(fixture, name, source=None, factory=StatusBoundFramework):
    world = prior.TestWorld(fixture['pre_state'], False)
    boundary = prior.ExternalExecutionBoundary(world, 'INTERFACE_' + name)
    system = factory(boundary.reader(), fixture['pre_state'], 1001, source)
    return system, boundary, world


def compatibility(old, instrument):
    defaults = [default_case(r['fixture'], r['name'], r['failure_class'], r['mode'],
                instrument, r['only_consequence'], factory=StatusBoundFramework)
                for r in old['default_equivalence']['historical']['cases']]
    assert serialized(defaults) == serialized(old['default_equivalence']['new_cases'])
    rows = []
    for r in old['cases']:
        row, _ = prior.transaction(r['fixture'], r['name'], r['mode'], instrument,
                 r['failure_class'], r['only_consequence'], existing=setup(r['fixture'], r['name']))
        assert serialized(row) == serialized(r), r['name']
        rows.append(row)
    history = []
    for h in old['retained_history']:
        a, b = h['first'], h['second']
        first, system = prior.transaction(a['fixture'], a['name'], a['mode'], instrument,
                 a['failure_class'], a['only_consequence'], existing=setup(a['fixture'], a['name']))
        second, _ = prior.transaction(b['fixture'], b['name'], b['mode'], instrument,
                 b['failure_class'], b['only_consequence'], existing=system)
        row = dict(mode=h['mode'], first=first, second=second)
        assert serialized(row) == serialized(h)
        history.append(row)
    decisions = [native.PairDecision(**r['probe']['after']['pairs'][-1])
                 for r in rows[:16] if r['mode'] == 'correct']
    budgets = prior.budget_checks(decisions)
    assert budgets == old['budget_controls']
    identity = []
    for r in old['identity_controls']:
        decision = native.PairDecision(**r['decision'])
        candidate = native.StateCandidate(**r['candidate'])
        before = native.CrossSourceStateAuthorizer().authorize(candidate, decision)
        after = StatusBoundAuthorizer().authorize(candidate, decision)
        assert before == r['historical_accepted'] and not after
        identity.append(dict(field=r['field'], historical_accepted=before, repaired_accepted=after,
                             changed=before != after))
    assert sum(r['changed'] for r in identity) == 8
    return dict(default_cases=defaults, cases=rows, retained_history=history,
                budget_controls=budgets, identity_controls=identity,
                protected_evidence_byte_identical=True), decisions


def status_matrix(decisions):
    rows = []
    for decision in decisions:
        good = native.Recovery().state_candidate(decision)
        for enum in (native.CrossAuthorityState, v0.AuthorityState):
            for status in enum:
                candidate = replace(good, status=status)
                historical = native.CrossSourceStateAuthorizer()
                repaired = StatusBoundAuthorizer()
                old = historical.authorize(candidate, decision)
                new = repaired.authorize(candidate, decision)
                eligible = status == native.CrossAuthorityState.RECOVERING
                assert old and new == eligible
                assert len(repaired.authorized) == int(eligible)
                rows.append(dict(decision=asdict(decision), candidate=asdict(candidate),
                    status_enum=enum.__name__, status_name=status.name,
                    historical_accepted=old, repaired_accepted=new,
                    authorized_identities=len(repaired.authorized), protected_publication=False))
    assert len(rows) == 136
    return rows


def invalid_controls(decisions):
    rows = []
    for decision in decisions:
        good = native.Recovery().state_candidate(decision)
        for field in ('epoch', 'transaction_id', 'pair_decision_id', 'value', 'value_and_status'):
            if field == 'value_and_status':
                bad = replace(good, value=(good.value + 1) % 4, status=native.CrossAuthorityState.REJECTED)
            else:
                bad = replace(good, **{field: (good.value + 1) % 4 if field == 'value' else getattr(good, field) + 1})
            old = native.CrossSourceStateAuthorizer().authorize(bad, decision)
            new = StatusBoundAuthorizer().authorize(bad, decision)
            assert not old and not new
            rows.append(dict(field=field, candidate=asdict(bad), decision=asdict(decision),
                             historical_accepted=old, repaired_accepted=new))
    return rows


@contextmanager
def observe(enabled):
    events = []; previous = sys.getprofile()
    codes = {StatusBoundAuthorizer.authorize.__code__: 'status_authorizer',
             native.CrossSourceStateAuthorizer.authorize.__code__: 'inherited_authorizer',
             native.Recovery.state_candidate.__code__: 'native_attempt',
             prior.SyntheticSource.propose.__code__: 'proposal',
             v0.MapModel.quarantine_incumbent.__code__: 'quarantine'}
    def callback(frame, event, value):
        kind = codes.get(frame.f_code)
        if not kind or event != ('call' if kind == 'proposal' else 'return'): return
        row = dict(kind=kind); loc = frame.f_locals
        if kind.endswith('authorizer'):
            row.update(candidate=asdict(loc['candidate']), accepted=value)
            if kind == 'status_authorizer': row['state_recovery'] = loc['state_recovery']
        elif kind == 'native_attempt': row.update(attempts=loc['self'].attempts, candidate=asdict(value) if value else None)
        events.append(row)
    if enabled:
        if previous is not None: raise RuntimeError('observer already installed')
        sys.setprofile(callback)
    try: yield events
    finally:
        if enabled: sys.setprofile(previous)


class StatusFaultCore(StatusBoundCore):
    """Test-only envelope corruption below the normal value-only interface."""
    def _state_recovery_candidate(self, decision, *, wrong=False):
        candidate = super()._state_recovery_candidate(decision, wrong=wrong)
        return replace(candidate, status=self.test_status)


class StatusFaultFramework(StatusBoundFramework):
    def __init__(self, receipt_port, initial_state=1, epoch=1001, proposal_source=None):
        super().__init__(receipt_port, initial_state, epoch, proposal_source)
        self.inner = StatusFaultCore(initial_state, epoch, proposal_source)
        self.inner._requires_package = True
        self.inner.pair_authorizer = SharedReceiptPairGate()


def atomic_status_case(fixture, name, status, instrument, existing=None):
    source = prior.SyntheticSource('correct')
    system, boundary, world = existing or setup(fixture, name, source, factory=StatusFaultFramework)
    system.inner._state_recovery_source = source
    system.inner.test_status = status
    prior.configure(system, fixture)
    authentic = {(p.receipt.epoch, p.receipt.transaction_id): p.receipt for p in system.packages}
    # Explicitly capture continuation just before submission, after begin_step.
    before = prior.published(system)
    pending = system.begin_step()
    before_submit = system.inner.continuation_authorized
    prediction = asdict(pending.prediction)
    receipt = boundary.execute(pending.epoch, pending.transaction_id, pending.action)
    receipt_copy = asdict(receipt)
    from experiments.realized_event_grounding_v0.framework import evidence
    with observe(instrument) as events:
        result = system.submit_package(evidence(receipt))
    after = prior.published(system)
    assert not result.committed and not result.continued
    assert before == after and system.inner.metrics['commits'] == before['commits']
    assert before_submit is False and system.inner.continuation_authorized is False
    assert boundary.reader().current() is receipt and asdict(receipt) == receipt_copy
    assert asdict(system.inner._prediction_at_begin) == prediction
    assert len(source.contexts) == 1
    system.assert_bounds()
    boundary.release(receipt)
    count = world.oracle.execution_count
    retried = system.begin_step()
    assert not retried.committed and not retried.executed and not retried.continued
    assert len(source.contexts) == 1 and world.oracle.execution_count == count
    assert prior.published(system) == before
    if instrument:
        kinds = [e['kind'] for e in events]
        assert kinds.count('native_attempt') == kinds.count('proposal') == 1
        assert 'inherited_authorizer' not in kinds
        auth = next(e for e in events if e['kind'] == 'status_authorizer')
        assert auth['state_recovery'] is True and auth['accepted'] is False
        assert auth['candidate']['status'] == status
        assert next(e for e in events if e['kind'] == 'native_attempt')['attempts'] == 1
        assert kinds.index('quarantine') < kinds.index('native_attempt') < kinds.index('proposal') < kinds.index('status_authorizer')
    return dict(name=name, status=status, fixture=fixture, result=asdict(result),
                before=before, after=after, continuation_before_submit=before_submit,
                continuation_after_submit=False, commit_delta=0, callback_count=len(source.contexts),
                receipt=receipt_copy, prediction=prediction, receipt_unchanged=True,
                prediction_unchanged=True, history_unchanged=True, no_second_callback=True, events=events)


def duplicate_capacity(decision):
    good = native.Recovery().state_candidate(decision)
    results = []
    for cls in (native.CrossSourceStateAuthorizer, StatusBoundAuthorizer):
        authorizer = cls()
        assert authorizer.authorize(good, decision)
        try: authorizer.authorize(good, decision)
        except RuntimeError as exc: duplicate = str(exc)
        else: raise AssertionError('duplicate allowed')
        full = cls()
        for i in range(native.AUTHORIZATION_LIMIT):
            d = replace(decision, transaction_id=i + 1, pair_decision_id=10000 + i)
            assert full.authorize(native.Recovery().state_candidate(d), d)
        extra = replace(decision, transaction_id=999, pair_decision_id=19999)
        try: full.authorize(native.Recovery().state_candidate(extra), extra)
        except RuntimeError as exc: capacity = str(exc)
        else: raise AssertionError('capacity exceeded')
        results.append(dict(duplicate=duplicate, capacity=capacity, identities=len(full.authorized)))
    assert results[0] == results[1]
    repaired = StatusBoundAuthorizer()
    assert not repaired.authorize(replace(good, status=native.CrossAuthorityState.REJECTED), decision)
    assert not repaired.authorized and repaired.authorize(good, decision)
    return dict(historical=results[0], repaired=results[1], wrong_status_does_not_consume_identity=True)


def ordinary_and_epoch(fixtures, instrument):
    d = next(d for d in fixtures if d['pre_state'] == 0 and d['action'] == 'ADVANCE')
    outputs = []
    for factory in (StateRecoveryFramework, StatusBoundFramework):
        system, boundary, world = setup(d, 'ordinary_epoch', factory=factory)
        system.inner.explorer = prior.historical.FixedExplorer(d['action'])
        # Accurate deterministic prediction exercises ordinary measured replacement.
        system.inner.map = prior.historical.FixedPredictionMap(0, 1001, d['actual_next_state'], d['actual_consequence'])
        first = prior.execute(system, boundary, world, {}, instrument=False)
        assert first['authorization']['committed'] and not first['authorization']['recovery_authorized']
        system.start_epoch(1002)
        assert system.inner.epochs_started == 2 and not system.inner.state_authorizer.authorized
        if factory is StatusBoundFramework: assert type(system.inner.state_authorizer) is StatusBoundAuthorizer
        next_d = next(x for x in fixtures if x['pre_state'] == world.oracle.state and x['action'] == 'ADVANCE')
        second, _ = prior.transaction(next_d, 'after_epoch', 'correct', instrument,
                                      existing=(system, boundary, world))
        assert second['probe']['authorization']['recovery_authorized']
        if factory is StatusBoundFramework:
            pair = native.PairDecision(**second['probe']['after']['pairs'][-1])
            # Bad status must be rejected even though the key is already present;
            # this also verifies the repaired type survived the epoch reset.
            assert not system.inner.state_authorizer.authorize(
                replace(native.Recovery().state_candidate(pair), status=native.CrossAuthorityState.REJECTED), pair)
        outputs.append(dict(first=first, second=second))
    assert serialized(outputs[0]) == serialized(outputs[1])
    return dict(byte_identical=True, repaired=outputs[1], repaired_type_after_epoch=True)


def run(instrument=True):
    contract, old = preflight()
    if not instrument:
        old = prior.run(False)
    structural = structure()
    compatible, decisions = compatibility(old, instrument)
    matrix = status_matrix(decisions)
    invalid = invalid_controls(decisions)
    fixtures = old['default_equivalence']['historical']['registration']
    genuine = [d for d in fixtures if d['actual_next_state'] != d['pre_state']]
    atomic = [atomic_status_case(d, f"{d['pre_state']}_{d['action']}_{status.name}", status, instrument)
              for d in genuine for status in (native.CrossAuthorityState.REJECTED,
                  native.CrossAuthorityState.PROPOSED, native.CrossAuthorityState.AUTHORIZED)]
    hold = next(d for d in fixtures if d['pre_state'] == 1 and d['action'] == 'HOLD')
    first, existing = prior.transaction(hold, 'retained_status', 'never', instrument, only_consequence=True,
                      existing=setup(hold, 'retained_status', factory=StatusFaultFramework))
    advance = next(d for d in genuine if d['pre_state'] == 1 and d['action'] == 'ADVANCE')
    second = atomic_status_case(advance, 'retained_status_reject', native.CrossAuthorityState.REJECTED,
                                instrument, existing)
    assert len(second['before']['memory']) == 1
    limits = duplicate_capacity(decisions[0])
    epoch = ordinary_and_epoch(fixtures, instrument)
    summary = dict(actual_model_calls=0, campaign_checks='PASS',
        completion='FINAL_CLASSIFICATION_IN_VERIFICATION_AFTER_REPLAY_AND_REGRESSIONS', model_usefulness='UNTESTED',
        contract=contract['contract'], recovery_status='RECOVERING', trusted_scope_required=True,
        default_equivalence_cases=32, inherited_interface_transactions=52,
        inherited_budget_controls=8, inherited_identity_controls=32,
        correct_injected_authorizations=8, wrong_injected_rejections=8,
        malformed_failure_rejections=20, no_recovery_controls=12, no_recovery_callbacks=0,
        status_matrix_cells=len(matrix), historical_status_matrix_acceptances=sum(r['historical_accepted'] for r in matrix),
        repaired_recovering_acceptances=sum(r['repaired_accepted'] for r in matrix),
        repaired_wrong_status_rejections=sum(not r['repaired_accepted'] for r in matrix),
        original_rejected_witness_old_accepts=8, original_rejected_witness_repaired_rejects=8,
        identity_value_combined_controls=len(invalid), identity_value_combined_rejections=len(invalid),
        wrong_status_atomic_transactions=len(atomic) + 1, wrong_status_atomic_rejections=len(atomic) + 1,
        retained_history_preserved=True, duplicate_capacity_preserved=True, epoch_reset_preserved=True,
        normal_interface_changes=0, protected_false_accepts=0, receipt_rewrites=0,
        prediction_rewrites=0, retry_leaks=0, protected_publication_errors=0, bound_violations=0,
        historical_interface_classification='C — NOT ESTABLISHED', historical_recovery_v0='BLOCKED',
        maximum_memory=2)
    return dict(summary=summary, contract=contract, structure=structural,
        interface_compatibility=compatible, status_matrix=matrix, invalid_controls=invalid,
        atomic_status_cases=atomic, retained_history=dict(first=first, second=second),
        duplicate_capacity=limits, ordinary_epoch=epoch)


def protected_projection(data):
    return prior.protected_projection(data)
