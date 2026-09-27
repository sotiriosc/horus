"""Missing-interface checks must not be reported as a passing model gate."""
import unittest
from .diagnostic import run


class InterfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=run()

    def test_missing_interface_and_ignored_alternatives(self):
        d=self.data
        self.assertEqual(d['summary']['interface_gate'],'BLOCKED_MISSING_PROPOSAL_INTERFACE')
        self.assertEqual(d['summary']['actual_model_calls'],0)
        self.assertFalse(d['interface']['instance_has_recovery_component'])
        cases={r['name']:r for r in d['cases']}
        slot=cases['unused_slot']
        self.assertEqual(slot['sentinel_calls'],0)
        self.assertTrue(slot['probe']['authorization']['committed'])
        ordinary=cases['ordinary_candidate']
        auth=next(x for x in ordinary['native_observations'] if x['kind']=='state_authorization')
        self.assertEqual(auth['candidate']['value'],2)
        self.assertFalse(cases['unsupported_keyword']['probe']['authorization']['committed'])

    def test_genuine_matrix_and_no_recovery_controls(self):
        s=self.data['summary']
        self.assertEqual(s['primary_native_recovery_commits'],16)
        self.assertEqual(s['primary_incumbent_retained_without_recovery'],8)
        self.assertEqual(s['primary_recovery_target_states'],[0,1,2,3])
        for row in self.data['cases'][-4:]:
            self.assertTrue(row['probe']['authorization']['committed'])
            self.assertFalse(row['probe']['measurement_matches'])
            self.assertFalse(any(x['kind']=='native_recovery' for x in row['native_observations']))
            self.assertEqual(row['probe']['after']['memory'][-1]['consequence'],row['probe']['receipt']['realized_consequence'])

    def test_native_rejection_is_atomic_and_preserves_evidence(self):
        row=next(r for r in self.data['cases'] if r['name']=='wrong_recovery')
        p=row['probe']
        self.assertEqual(p['commit_delta'],0)
        self.assertEqual(p['before'],p['after'])
        self.assertFalse(p['authorization']['continued'])
        self.assertTrue(p['prediction_unchanged'] and p['receipt_unchanged'])
        kinds=[x['kind'] for x in row['native_observations']]
        self.assertLess(kinds.index('map_quarantine'),kinds.index('native_recovery'))
        auth=next(x for x in row['native_observations'] if x['kind']=='state_authorization')
        self.assertFalse(auth['authorized'])

    def test_native_budget_is_object_local(self):
        b=self.data['budget']
        self.assertEqual(b['limit'],1)
        self.assertEqual(b['attempts_after_first'],1)
        self.assertTrue(b['second_call_rejected'])
        self.assertEqual(b['attempt_counter_after_rejection'],2)

if __name__=='__main__':unittest.main()
