"""Boundary, atomicity and known historical limitation regression tests."""
from dataclasses import FrozenInstanceError, replace
import unittest

from experiments.base_framework_v1.framework import PairDecision, CrossAuthorityState
from .campaign import run, protected_projection, serialized, SyntheticSource
from .framework import RecoveryOpportunity, DecisionContext


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = run()

    def test_default_full_evidence_equivalence(self):
        data = self.data['default_equivalence']
        self.assertEqual(len(data['new_cases']), 32)
        self.assertEqual(serialized(data['historical']['cases']), serialized(data['new_cases']))
        self.assertEqual(data['historical']['summary']['interface_gate'], 'BLOCKED_MISSING_PROPOSAL_INTERFACE')

    def test_only_external_value_changes_candidate(self):
        for row in self.data['cases'][:16]:
            events = row['events']
            native = next(e for e in events if e['kind'] == 'native_attempt')['candidate']
            selected = next(e for e in events if e['kind'] == 'authorize')
            for field in ('epoch', 'transaction_id', 'pair_decision_id', 'status'):
                self.assertEqual(native[field], selected['candidate'][field])
            self.assertEqual(selected['candidate']['status'], CrossAuthorityState.RECOVERING)
            self.assertEqual(selected['accepted'], row['mode'] == 'correct')
            self.assertEqual(len(row['callback_contexts']), 1)

    def test_malformed_and_exception_fail_before_authorization(self):
        rows = self.data['cases'][16:36]
        self.assertEqual(len(rows), 20)
        for row in rows:
            self.assertFalse(row['probe']['authorization']['committed'])
            self.assertEqual(row['probe']['before'], row['probe']['after'])
            self.assertNotIn('authorize', [e['kind'] for e in row['events']])
            self.assertEqual(row['denied_retry']['callback_count'], 1)

    def test_no_opportunity_for_valid_incumbent(self):
        rows = self.data['cases'][36:]
        self.assertEqual(len(rows), 12)
        for row in rows:
            self.assertEqual(row['callback_contexts'], [])
            self.assertFalse(row['probe']['measurement_matches'])
            self.assertTrue(row['probe']['authorization']['committed'])
            self.assertNotIn('native_attempt', [e['kind'] for e in row['events']])

    def test_budget_consumed_even_when_source_fails(self):
        decision = PairDecision(**self.data['cases'][0]['probe']['after']['pairs'][0])
        for mode in ('correct', 'wrong', 'exception', 'none'):
            source = SyntheticSource(mode)
            opportunity = RecoveryOpportunity()
            if mode in ('exception', 'none'):
                with self.assertRaises(ValueError):
                    opportunity.candidate(decision, source)
            else:
                opportunity.candidate(decision, source)
            self.assertEqual(opportunity._native.attempts, 1)
            with self.assertRaisesRegex(RuntimeError, 'recovery attempt bound exceeded'):
                opportunity.candidate(decision, source)
            self.assertEqual(len(source.contexts), 1)
            self.assertEqual(opportunity._native.attempts, 2)

    def test_context_is_frozen_scalars_without_capabilities(self):
        row = self.data['cases'][0]['callback_contexts'][0]
        context = DecisionContext(**row)
        with self.assertRaises(FrozenInstanceError):
            context.next_state = 3
        self.assertEqual(set(vars(context)), {'epoch', 'transaction_id', 'pair_decision_id',
                         'pre_state', 'action', 'next_state', 'consequence', 'measurement_matches'})
        self.assertTrue(all(type(v) in (int, str, bool) for v in vars(context).values()))

    def test_rejection_preserves_existing_memory_and_quarantines(self):
        row = next(h for h in self.data['retained_history'] if h['mode'] == 'wrong')['second']
        self.assertEqual(len(row['probe']['before']['memory']), 1)
        self.assertEqual(row['probe']['before'], row['probe']['after'])
        self.assertEqual(row['probe']['commit_delta'], 0)
        self.assertFalse(row['probe']['authorization']['continued'])
        self.assertTrue(row['probe']['prediction_unchanged'])
        self.assertTrue(row['probe']['receipt_unchanged'])

    def test_status_requirement_gap_is_not_hidden(self):
        rows = self.data['identity_controls']
        for row in rows:
            self.assertEqual(row['historical_accepted'], row['new_accepted'])
            self.assertEqual(row['new_accepted'], row['field'] == 'status')
        self.assertEqual(self.data['summary']['classification'], 'C — NOT ESTABLISHED')
        self.assertEqual(self.data['summary']['wrong_status_acceptances_new'], 8)

    def test_observer_does_not_change_outcomes(self):
        self.assertEqual(serialized(protected_projection(self.data)),
                         serialized(protected_projection(run(False))))


if __name__ == '__main__':
    unittest.main()
