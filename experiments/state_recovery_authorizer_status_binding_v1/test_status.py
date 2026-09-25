"""Status semantics, scope, inherited interface and transaction boundaries."""
import unittest
from experiments.base_framework_v1 import framework as native
from .campaign import run, protected_projection, serialized
from .framework import StatusBoundAuthorizer


class StatusBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.data = run()

    def test_complete_enum_matrix_and_old_negative(self):
        rows = self.data['status_matrix']
        self.assertEqual(len(rows), 136)
        self.assertEqual(sum(r['historical_accepted'] for r in rows), 136)
        self.assertEqual(sum(r['repaired_accepted'] for r in rows), 16)
        for r in rows:
            self.assertEqual(r['repaired_accepted'], r['status_name'] == 'RECOVERING')
        witness = [r for r in rows if r['status_enum'] == 'CrossAuthorityState' and r['status_name'] == 'REJECTED']
        self.assertEqual(len(witness), 8)
        self.assertTrue(all(r['historical_accepted'] and not r['repaired_accepted'] for r in witness))

    def test_existing_value_and_identity_checks(self):
        self.assertEqual(len(self.data['invalid_controls']), 40)
        self.assertTrue(all(not r['historical_accepted'] and not r['repaired_accepted']
                            for r in self.data['invalid_controls']))

    def test_scope_is_not_inferred_from_candidate_status(self):
        row = self.data['status_matrix'][0]
        candidate = native.StateCandidate(**row['candidate'])
        decision = native.PairDecision(**row['decision'])
        self.assertEqual(candidate.status, 'PROPOSED')
        self.assertFalse(StatusBoundAuthorizer().authorize(candidate, decision))
        # Ordinary transactions remain in their existing trusted coordinator scope.
        self.assertTrue(StatusBoundAuthorizer().authorize(candidate, decision, state_recovery=False))
        for r in self.data['atomic_status_cases']:
            event = next(e for e in r['events'] if e['kind'] == 'status_authorizer')
            self.assertTrue(event['state_recovery'])
            self.assertFalse(event['accepted'])

    def test_all_inherited_transactions_preserved(self):
        c = self.data['interface_compatibility']
        self.assertTrue(c['protected_evidence_byte_identical'])
        self.assertEqual(len(c['default_cases']), 32)
        self.assertEqual(len(c['cases']), 48)
        self.assertEqual(len(c['retained_history']), 2)
        self.assertEqual(sum(x['changed'] for x in c['identity_controls']), 8)

    def test_wrong_status_transaction_atomicity(self):
        for r in self.data['atomic_status_cases'] + [self.data['retained_history']['second']]:
            self.assertEqual(r['commit_delta'], 0)
            self.assertEqual(r['before'], r['after'])
            self.assertFalse(r['continuation_before_submit'])
            self.assertFalse(r['continuation_after_submit'])
            self.assertEqual(r['callback_count'], 1)
            self.assertTrue(r['no_second_callback'])
            self.assertTrue(r['receipt_unchanged'] and r['prediction_unchanged'])
            self.assertNotIn('inherited_authorizer', [e['kind'] for e in r['events']])

    def test_old_memory_survives_status_rejection(self):
        r = self.data['retained_history']['second']
        self.assertEqual(len(r['before']['memory']), 1)
        self.assertEqual(r['before']['memory'], r['after']['memory'])
        self.assertEqual(r['before']['packages'], r['after']['packages'])

    def test_duplicate_capacity_and_budget_unchanged(self):
        c = self.data['duplicate_capacity']
        self.assertEqual(c['historical'], c['repaired'])
        self.assertTrue(c['wrong_status_does_not_consume_identity'])
        for r in self.data['interface_compatibility']['budget_controls']:
            self.assertEqual(r['callback_count'], 1)
            self.assertEqual(r['counter_after_denial'], 2)
            self.assertTrue(r['second_candidate_denied'])

    def test_epoch_reset_and_ordinary_replacement(self):
        c = self.data['ordinary_epoch']
        self.assertTrue(c['byte_identical'] and c['repaired_type_after_epoch'])
        self.assertFalse(c['repaired']['first']['authorization']['recovery_authorized'])
        self.assertTrue(c['repaired']['second']['probe']['authorization']['recovery_authorized'])

    def test_observer_noninterference(self):
        self.assertEqual(serialized(protected_projection(self.data)),
                         serialized(protected_projection(run(False))))


if __name__ == '__main__': unittest.main()
