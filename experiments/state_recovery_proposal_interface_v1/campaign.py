"""Bounded synthetic value-interface tests. No model transport or inference."""
from contextlib import contextmanager
from dataclasses import asdict, replace
import inspect
import json
import sys

from experiments.base_framework_v1 import framework as native
from experiments.base_framework_v0.framework import MapModel
from experiments.model_recovery_proposal_v0 import diagnostic as historical
from experiments.model_map_proposal_v0.boundary import execute
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from .framework import (StateRecoveryFramework, RecoveryInterfaceCore,
                        RecoveryOpportunity, DecisionContext)
from .equivalence import run_case as equivalent_case


def serialized(value):
    return json.dumps(value, sort_keys=True, indent=2).encode() + b'\n'


class IntSubclass(int):
    pass


class SyntheticSource:
    """Deterministic values and observation-only telemetry; no core references."""
    def __init__(self, mode='correct'):
        self.mode = mode
        self.contexts = []

    def __deepcopy__(self, memo):
        # Only this fixture's input observations survive staging; no protected
        # state or capability is reachable from the synthetic source.
        return self

    def propose(self, context):
        self.contexts.append(asdict(context))
        assert type(context) is DecisionContext
        assert all(type(v) in (int, str, bool) for v in asdict(context).values())
        if self.mode in ('exception', 'never'):
            raise LookupError('synthetic proposal source failure')
        if self.mode == 'no_return':
            return
        if self.mode == 'correct':
            return context.next_state
        if self.mode == 'wrong':
            return (context.next_state + 1) % 4
        if self.mode.startswith('extra_'):
            return {'value': context.next_state, self.mode[6:]: True}
        values = {'negative': -1, 'high': 4, 'bool': True, 'float': 1.0,
                  'none': None, 'string': '2', 'list': [2, 3], 'tuple': (2, 3),
                  'object': object(), 'int_subclass': IntSubclass(2),
                  'candidate': native.StateCandidate(context.epoch, context.transaction_id,
                         context.pair_decision_id, context.next_state, native.CrossAuthorityState.AUTHORIZED)}
        return values[self.mode]


@contextmanager
def observe(enabled):
    events = []
    previous = sys.getprofile()
    codes = {RealizedEventFramework._check.__code__: 'authentic_receipt',
             native.MeasureAuditor.verify.__code__: 'measure',
             MapModel.quarantine_incumbent.__code__: 'quarantine',
             native.Recovery.state_candidate.__code__: 'native_attempt',
             SyntheticSource.propose.__code__: 'proposal',
             native.CrossSourceStateAuthorizer.authorize.__code__: 'authorize',
             MapModel.commit.__code__: 'map_commit',
             RealizedEventFramework.submit_package.__code__: 'publication'}

    def callback(frame, event, value):
        kind = codes.get(frame.f_code)
        if not kind or event != ('call' if kind == 'proposal' else 'return'):
            return
        loc = frame.f_locals
        row = {'kind': kind}
        if kind == 'native_attempt':
            row.update(attempts=loc['self'].attempts, candidate=asdict(value) if value else None,
                       decision=asdict(loc['decision']))
        elif kind == 'proposal':
            row['context'] = asdict(loc['context'])
        elif kind == 'authorize':
            row.update(candidate=asdict(loc['candidate']), decision=asdict(loc['decision']), accepted=value)
        elif kind == 'measure':
            row.update(verified=value, measurement=asdict(loc['measurement']))
        elif kind == 'publication':
            row['committed'] = bool(value and value.committed)
        elif kind == 'authentic_receipt':
            row['verified'] = value is not None
        events.append(row)

    if enabled:
        if previous is not None:
            raise RuntimeError('existing profile observer')
        sys.setprofile(callback)
    try:
        yield events
    finally:
        if enabled:
            sys.setprofile(previous)


def structural_checks():
    old = inspect.getsource(native.CrossSourceFramework._complete_pair)
    new = inspect.getsource(RecoveryInterfaceCore._complete_pair)
    expected = old.replace('Recovery().state_candidate(decision, wrong=failed_recovery)',
                           'self._state_recovery_candidate(decision, wrong=failed_recovery)')
    assert old != expected and expected == new
    oldcase = inspect.getsource(historical.run_case)
    newcase = inspect.getsource(equivalent_case)
    expectedcase = oldcase.replace('only_consequence=False):',
                        'only_consequence=False, factory=StateRecoveryFramework):').replace(
                        'system=RealizedEventFramework(source.reader(),state,1001)',
                        'system=factory(source.reader(),state,1001)')
    assert expectedcase == newcase
    core = RecoveryInterfaceCore()
    assert type(core.state_authorizer) is native.CrossSourceStateAuthorizer
    assert StateRecoveryFramework.submit_package is RealizedEventFramework.submit_package
    assert StateRecoveryFramework.begin_step is RealizedEventFramework.begin_step
    for method in ('submit_receipt', '_reject', 'assert_bounds', '_recover_memory', 'begin_step'):
        assert getattr(RecoveryInterfaceCore, method) is getattr(native.CrossSourceFramework, method)
    return dict(single_expression_change_verified=True, historical_case_body_verified=True,
                unchanged_authorizer=True, inherited_atomic_wrapper=True,
                context_fields=list(DecisionContext.__dataclass_fields__),
                proposal_fields=['replacement_state_value'], native_limit=native.RECOVERY_LIMIT)


def default_equivalence(instrument):
    old = historical.run(instrument)
    newrows = [equivalent_case(row['fixture'], row['name'], row['failure_class'],
               row['mode'], instrument, row['only_consequence']) for row in old['cases']]
    assert serialized(old['cases']) == serialized(newrows), 'default path differs'
    return dict(historical=old, new_cases=newrows, case_count=len(newrows), byte_identical=True)


def setup(fixture, name, source):
    world = TestWorld(fixture['pre_state'], False)
    boundary = ExternalExecutionBoundary(world, 'INTERFACE_' + name)
    system = StateRecoveryFramework(boundary.reader(), fixture['pre_state'], 1001, source)
    return system, boundary, world


def configure(system, fixture, cls='S', only_consequence=False):
    system.inner.explorer = historical.FixedExplorer(fixture['action'])
    # Preserve existing protected Map state/version/quarantine on sequential runs.
    prior = system.inner.map
    model = historical.FixedPredictionMap(prior.current.state, system.inner.epoch,
              fixture['actual_next_state'] if only_consequence else (fixture['actual_next_state'] + 1) % 4,
              {-1: 0, 0: 1, 1: -1}[fixture['actual_consequence']]
              if cls == 'SC' or only_consequence else fixture['actual_consequence'])
    model.current, model.quarantine = prior.current, prior.quarantine
    system.inner.map = model


def transaction(fixture, name, mode, instrument, cls='S', only_consequence=False, existing=None):
    source = SyntheticSource(mode)
    system, boundary, world = existing or setup(fixture, name, source)
    if existing:
        system.inner._state_recovery_source = source
    configure(system, fixture, cls, only_consequence)
    authentic = {(p.receipt.epoch, p.receipt.transaction_id): p.receipt for p in system.packages}
    with observe(instrument) as events:
        row = execute(system, boundary, world, authentic, instrument=False)
    needed = fixture['pre_state'] != fixture['actual_next_state']
    expected_commit = not needed or mode == 'correct'
    assert not row['errors'], (name, row['errors'])
    assert row['authorization']['committed'] == expected_commit, name
    assert row['prediction_unchanged'] and row['receipt_unchanged'] and row['old_history_unchanged']
    assert len(source.contexts) == int(needed), name
    retry = None
    if expected_commit:
        assert row['after']['map']['state'] == row['receipt']['next_state']
        assert row['after']['memory'][-1]['next_state'] == row['receipt']['next_state']
        assert row['after']['memory'][-1]['consequence'] == row['receipt']['realized_consequence']
    else:
        assert row['commit_delta'] == 0 and row['before'] == row['after']
        assert not row['authorization']['continued'] and not system.inner.continuation_authorized
        before = published(system)
        count = world.oracle.execution_count
        retried = system.begin_step()
        assert not retried.committed and not retried.executed and not retried.continued
        assert published(system) == before and world.oracle.execution_count == count
        assert len(source.contexts) == 1
        retry = dict(committed=False, executed=False, continued=False, callback_count=len(source.contexts))
    if instrument:
        kinds = [e['kind'] for e in events]
        attempts = [e for e in events if e['kind'] == 'native_attempt']
        auth = [e for e in events if e['kind'] == 'authorize']
        assert len(attempts) == int(needed) and kinds.count('proposal') == int(needed)
        if needed:
            assert attempts[0]['attempts'] == 1
            assert source.contexts[0]['measurement_matches'] is False
            ordered = ['authentic_receipt', 'measure', 'quarantine', 'native_attempt', 'proposal']
            positions = [kinds.index(k) for k in ordered]
            assert positions == sorted(positions)
            assert all(e['verified'] for e in events if e['kind'] in ('authentic_receipt', 'measure'))
            if mode in ('correct', 'wrong'):
                assert len(auth) == 1 and auth[0]['accepted'] == expected_commit
                assert kinds.index('proposal') < kinds.index('authorize') < kinds.index('publication')
                for key in ('epoch', 'transaction_id', 'pair_decision_id', 'status'):
                    assert auth[0]['candidate'][key] == attempts[0]['candidate'][key]
                value = source.contexts[0]['next_state']
                assert auth[0]['candidate']['value'] == (value if mode == 'correct' else (value + 1) % 4)
            else:
                assert not auth and 'map_commit' not in kinds
        else:
            assert not attempts and 'quarantine' not in kinds
            assert row['measurement_matches'] is False
        if expected_commit:
            assert kinds.index('authorize') < kinds.index('map_commit') < kinds.index('publication')
    return dict(name=name, mode=mode, fixture=fixture, failure_class=cls,
                only_consequence=only_consequence, callback_contexts=source.contexts,
                events=events, probe=row, denied_retry=retry), (system, boundary, world)


def budget_checks(decisions):
    rows = []
    for decision in decisions:
        source = SyntheticSource()
        opportunity = RecoveryOpportunity()
        first = opportunity.candidate(decision, source)
        assert len(source.contexts) == 1 and opportunity._native.attempts == 1
        try:
            opportunity.candidate(decision, source)
        except RuntimeError as exc:
            reason = str(exc)
        else:
            raise AssertionError('second opportunity allowed')
        assert len(source.contexts) == 1 and opportunity._native.attempts == 2
        rows.append(dict(decision=asdict(decision), first=asdict(first), callback_count=1,
                         counter_after_denial=2, second_candidate_denied=True, reason=reason))
    return rows


def identity_controls(decisions):
    rows = []
    for decision in decisions:
        good = native.Recovery().state_candidate(decision)
        for field in ('epoch', 'transaction_id', 'pair_decision_id', 'status'):
            wrong = native.CrossAuthorityState.REJECTED if field == 'status' else getattr(good, field) + 1
            forged = replace(good, **{field: wrong})
            old_authorizer = native.CrossSourceFramework().state_authorizer
            new_authorizer = RecoveryInterfaceCore().state_authorizer
            old = old_authorizer.authorize(forged, decision)
            new = new_authorizer.authorize(forged, decision)
            assert old == new, 'new low-level acceptance differs from historical'
            assert not new if field != 'status' else new
            rows.append(dict(field=field, candidate=asdict(forged), decision=asdict(decision),
                             historical_accepted=old, new_accepted=new, required_rejection_passed=not new,
                             protected_publication=False, scope='direct unchanged authorizer; below value-only API'))
    return rows


def run(instrument=True):
    structure = structural_checks()
    default = default_equivalence(instrument)
    fixtures = default['historical']['registration']
    genuine = [d for d in fixtures if d['pre_state'] != d['actual_next_state']]
    assert len(genuine) == 8
    rows = []
    for d in genuine:
        for mode in ('correct', 'wrong'):
            row, _ = transaction(d, f"{d['pre_state']}_{d['action']}_{mode}", mode, instrument)
            rows.append(row)
    d = next(d for d in genuine if d['pre_state'] == 1 and d['action'] == 'ADVANCE')
    malformed = ('negative', 'high', 'bool', 'float', 'none', 'string', 'list', 'tuple', 'object',
                 *('extra_' + k for k in ('AUTHORIZED', 'verified', 'approved', 'receipt_id',
                                        'package_id', 'grant', 'continuation')),
                 'candidate', 'exception', 'no_return', 'int_subclass')
    assert len(malformed) == 20
    for mode in malformed:
        row, _ = transaction(d, 'admission_' + mode, mode, instrument)
        rows.append(row)
    for d in fixtures:
        if d['action'] != 'HOLD':
            continue
        for cls in ('S', 'SC'):
            row, _ = transaction(d, f"no_recovery_{d['pre_state']}_{cls}", 'never', instrument, cls)
            rows.append(row)
        row, _ = transaction(d, f"consequence_only_{d['pre_state']}", 'never', instrument, only_consequence=True)
        rows.append(row)
    history = []
    hold = next(d for d in fixtures if d['pre_state'] == 1 and d['action'] == 'HOLD')
    advance = next(d for d in genuine if d['pre_state'] == 1 and d['action'] == 'ADVANCE')
    for mode in ('correct', 'wrong'):
        first, system = transaction(hold, 'history_' + mode, 'never', instrument, only_consequence=True)
        second, _ = transaction(advance, 'retained_' + mode, mode, instrument, existing=system)
        assert len(second['probe']['before']['memory']) == 1
        assert second['probe']['old_history_unchanged']
        history.append(dict(mode=mode, first=first, second=second))
    decisions = [native.PairDecision(**r['probe']['after']['pairs'][-1]) for r in rows[:16] if r['mode'] == 'correct']
    budgets = budget_checks(decisions)
    identity = identity_controls(decisions)
    all_injected = rows + [r for h in history for r in (h['first'], h['second'])]
    protected_errors = [error for r in all_injected for error in r['probe']['errors']]
    assert not protected_errors
    lowlevel_gap = sum(r['new_accepted'] for r in identity)
    assert lowlevel_gap == 8
    summary = dict(actual_model_calls=0, classification='C — NOT ESTABLISHED',
        blocking_requirement='Required low-level wrong-status rejection fails in both historical and new unchanged authorizer.',
        interface_operational_checks='PASS', authorizer_regression=False,
        model_usefulness='UNTESTED', default_equivalence_cases=32, default_cases_byte_identical=True,
        genuine_fixtures=8, realized_targets=sorted({d['actual_next_state'] for d in genuine}),
        correct_injected_cases=8, correct_injected_authorizations=8,
        wrong_injected_cases=8, wrong_injected_rejections=8,
        admission_failure_controls=20, admission_failure_rejections_before_authorization=20,
        no_recovery_controls=12, no_recovery_callbacks=0,
        retained_history_sequences=2, retained_history_transactions=4,
        injected_path_transactions=len(all_injected),
        injected_path_callbacks=sum(len(r['callback_contexts']) for r in all_injected),
        injected_path_commits=sum(r['probe']['authorization']['committed'] for r in all_injected),
        injected_path_rejections=sum(not r['probe']['authorization']['committed'] for r in all_injected),
        budget_controls=len(budgets), second_callback_invocations=0,
        low_level_identity_controls=len(identity), identity_epoch_transaction_pair_rejections=24,
        wrong_status_acceptances_historical=8, wrong_status_acceptances_new=8,
        wrong_status_protected_publications=0,
        protected_false_accepts=0, receipt_rewrites=0, prediction_rewrites=0,
        protected_partial_publications=0, bound_violations=0,
        maximum_memory=max(r['probe']['bounds']['memory'] for r in all_injected),
        historical_checkpoint_still_blocked=True)
    return dict(summary=summary, structure=structure, default_equivalence=default,
                cases=rows, retained_history=history, budget_controls=budgets, identity_controls=identity)


def protected_projection(data):
    """Remove only profile observations, preserving every protected/event field."""
    if isinstance(data, dict):
        return {k: protected_projection(v) for k, v in data.items()
                if k not in ('events', 'native_observations')}
    if isinstance(data, list):
        return [protected_projection(v) for v in data]
    return data
