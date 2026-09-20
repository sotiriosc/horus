"""Meaningful zero-inference fixture and inherited authority checks."""
import unittest
from unittest.mock import patch
from .campaign import arm,matching,law_scope,negative_controls,initialize,intervene,execute,stage,snap
from .fixture import Controller
from experiments.cross_episode_initialization_boundary_v1.projection import map_payload
from experiments.model_proposal_role_composition_v2.protocol import schedule

class Tests(unittest.TestCase):
    def setUp(self):
        self.network=patch('socket.socket',side_effect=AssertionError('zero inference'));self.network.start();self.addCleanup(self.network.stop)
    def test_primary_contradictions_and_stale_prediction(self):
        for changed in (False,True):
            a=arm(changed)
            self.assertEqual([len(a['stages'][p]['snapshot']['protected']['memory']) for p in ('P0','P1','P2')],[3,5,7])
            self.assertEqual(a['stages']['P2']['target_consequences'],[1,1,-1,-1] if changed else [1,1,1,1])
            for i in (3,5):
                r=a['primary_rows'][i];self.assertEqual(r['pending']['prediction']['consequence'],1)
                self.assertTrue(r['result']['committed']);self.assertFalse(r['prediction_rewritten'])
                self.assertEqual(r['after']['protected']['memory'][-1]['measurement_matches'],not changed)
    def test_only_target_consequence_changes(self):
        rows=law_scope();self.assertEqual(len(rows),12)
        self.assertEqual(sum(r['original']!=r['after'] for r in rows),1)
        self.assertTrue(all(r['original']['next_state']==r['after']['next_state'] for r in rows))
    def test_invalid_receipt_substitutions_rejected(self):
        rows=negative_controls();self.assertEqual(len(rows),4)
        self.assertTrue(all(r['rejected'] and r['protected_unchanged'] for r in rows))
    def test_intervention_only_registered_window_no_pseudo_event(self):
        c=Controller('EARLY')
        with self.assertRaises(ValueError):c._active.world.change_target()
        c,_,_,_,_=initialize('WINDOW');before=snap(c);intervene(c);self.assertEqual(snap(c),before)
        with self.assertRaises(ValueError):intervene(c)
    def test_cross_epoch_sorting_matches_and_projection_only_difference(self):
        matching(arm(False),arm(True))
        c,a,e,_,_=initialize('SORT');intervene(c)
        for action in ('ADVANCE','RETREAT','ADVANCE','RETREAT'):execute(c,action,a,e)
        records=c._active.framework.inner.memory.records
        for d in schedule():self.assertEqual(map_payload(0,'ADVANCE',records,d['mapping']),map_payload(0,'ADVANCE',reversed(records),d['mapping']))
        stage(c,'P2',a,e,True)
    def test_fifo_separate_and_unknown_becomes_known(self):
        a=arm(True);v=a['eviction']
        self.assertEqual(a['primary_end']['evictions'],0);self.assertEqual(v['at_nine']['evictions'],1)
        self.assertEqual(v['evicted_record']['epoch'],1001);self.assertEqual(v['evicted_record']['transaction_id'],1)
        self.assertTrue(v['unknown_to_known_HOLD']);self.assertEqual(a['stages']['P2']['target_consequences'],[1,1,-1,-1])
if __name__=='__main__':unittest.main()
