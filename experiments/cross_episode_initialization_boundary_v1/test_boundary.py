"""Meaningful boundary, isolation, projection and failure controls; zero inference."""
import unittest
from .boundary import EpisodeController,EpisodePlan
from .campaign import primary,failures,atomic_visibility,receipt_controls,contradiction,step,snap,MAPPING

class BoundaryTests(unittest.TestCase):
    def test_nonzero_reset_history_identity_and_ninth_fifo(self):
        p=primary();self.assertEqual(p['before']['world_state'],3);self.assertEqual(p['after']['world_state'],0)
        self.assertEqual(p['after']['protected']['memory'][-1]['next_state'],3)
        self.assertEqual(p['after']['protected']['map']['version'],0)
        self.assertEqual(p['after_ninth']['evictions'],1);self.assertEqual(len(p['rows']),9)
    def test_failure_paths_never_publish_partial_state(self):
        rows=failures();self.assertEqual(len(rows),24)
        self.assertTrue(all(r['rejected'] and r['no_partial_reset'] for r in rows))
    def test_staging_observations_see_old_joint_state(self):
        d=atomic_visibility();self.assertTrue(d['no_split_observed']);self.assertEqual(len(d['preparation_observations']),4)
    def test_receipt_replay_and_authorizer_limits(self):
        d=receipt_controls();self.assertEqual(len(d['receipt_cases']),4);self.assertEqual(len(d['authorizer_errors']),2)
    def test_existing_shift_fixture_keeps_differing_history_across_epochs(self):
        d=contradiction();self.assertEqual([r['epoch'] for r in d['projection']],[1001,1001,1001,1002])
        self.assertEqual([r['consequence'] for r in d['projection']],[1,1,-1,-1])
    def test_all_registered_start_states_and_detached_views(self):
        for initial in range(4):
            c=EpisodeController('DOMAIN_'+str(initial),EpisodePlan(initial_state=initial));step(c,'ADVANCE',{})
            c.start_episode(1002,initial);before=snap(c)
            self.assertEqual(before['world_state'],initial);self.assertEqual(before['protected']['map']['state'],initial)
            view=c.projections(MAPPING);view['Explorer']['state']=99
            snapshot=c.snapshot();snapshot['protected']['memory'].clear()
            self.assertEqual(snap(c),before)
            def values(x):
                if isinstance(x,dict):return all(values(v) for v in x.values())
                if isinstance(x,list):return all(values(v) for v in x)
                return type(x) in (str,int)
            self.assertTrue(values(c.projections(MAPPING)))
            self.assertFalse(hasattr(c._source.reader(),'start_episode'))

if __name__=='__main__':unittest.main()
