"""Outcome-aware tests: diagnostic success must not convert missing reset into A."""
import unittest
from .campaign import carry_fixture,state_reset_probe,guards,rejection_controls,lifetime_diagnostic

class BoundaryTests(unittest.TestCase):
    def test_same_lifetime_carry_and_ordinary_ninth_eviction(self):
        d=carry_fixture()
        self.assertEqual(len(d['rows']),9)
        self.assertFalse(d['complete_requested_reset_fixture'])
        self.assertEqual(d['after_ninth']['evictions'],1)
        self.assertTrue(d['historical_receipt_objects_survive'])
    def test_nonzero_state_not_reset_and_constructor_loses_history(self):
        d=state_reset_probe()
        self.assertFalse(d['fresh_zero_with_retained_history_supported'])
        self.assertEqual(d['after_epoch']['world_state'],1)
        self.assertEqual(d['after_epoch']['protected']['map']['state'],1)
        self.assertEqual(len(d['after_epoch']['protected']['memory']),2)
        self.assertEqual(d['fresh_instance']['protected']['memory'],[])
    def test_epoch_boundary_guards_leave_state_unchanged(self):
        rows=guards();self.assertEqual(len(rows),4)
        self.assertTrue(all(r['rejected'] and r['state_unchanged'] for r in rows))
    def test_receipt_replay_copy_and_detachment_reject_without_publication(self):
        rows=rejection_controls();self.assertEqual(len(rows),4)
        self.assertTrue(all(r['rejected'] and r['no_partial_publication'] for r in rows))
    def test_new_lifetime_partial_key_collision_is_not_safe_import(self):
        d=lifetime_diagnostic()
        self.assertTrue(d['core_memory_pair_key_would_collide_if_naively_combined'])
        self.assertTrue(d['complete_receipt_package_ids_differ'])
        self.assertFalse(d['histories_combined'])

if __name__=='__main__':unittest.main()
