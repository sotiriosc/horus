"""Focused tests for finite admission, staged references and audited experience."""
from copy import deepcopy
import unittest
from .adapters import ExplorerBinding, MapBinding, map_payload, explorer_payload
from .campaign import Tape, setup, ordinary, mappings, composed


class BindingTests(unittest.TestCase):
    def test_invalid_domains_never_request_text(self):
        mapping=mappings()[0][2]
        for state in (-1,4,True,0.0,'0'):
            with self.assertRaises(ValueError): explorer_payload(state,[],mapping)
            with self.assertRaises(ValueError): map_payload(state,'ADVANCE',[],mapping)
        for action in ('K1','INVALID','ADVANCE extra'):
            with self.assertRaises(ValueError): map_payload(0,action,[],mapping)
        for invalid in ({'K1':'ADVANCE'},dict(K1='ADVANCE',K2='HOLD',K3='HOLD'),
                        dict(A='ADVANCE',B='HOLD',C='RETREAT')):
            with self.assertRaises(ValueError): explorer_payload(0,[],invalid)

    def test_staging_uses_one_copied_memory_store(self):
        system,_,_,_=setup(0,'COPY_TEST');tape=Tape();mapping=mappings()[0][2]
        system.inner.map=MapBinding(system.inner.map,system.inner.memory,
            tape.source('copy','Map','{}'),mapping,1)
        staged=deepcopy(system.inner)
        self.assertIs(staged.map.memory,staged.memory)
        self.assertIsNot(staged.memory,system.inner.memory)
        self.assertIsNot(staged.map.base,system.inner.map.base)
        self.assertEqual(tape.calls,[])

    def test_existing_memory_repair_precedes_both_projections(self):
        bundle=setup(0,'AUDITED_HISTORY');ordinary(bundle,'HOLD')
        system=bundle[0]
        system.inner.memory.corrupt_consequence(1)
        tape=Tape();mapping=mappings()[0][2]
        # The before snapshot deliberately contains the corruption. The ordinary
        # core repairs it before either binding; inspect after begin directly.
        system.inner.explorer=ExplorerBinding(tape.source('audit','Explorer','K2'),mapping,1)
        system.inner.map=MapBinding(system.inner.map,system.inner.memory,
            tape.source('audit','Map','{"next_state":0,"consequence":0}'),mapping,2)
        pending=system.begin_step()
        self.assertTrue(hasattr(pending,'prediction'))
        self.assertEqual(tape.calls[0]['input']['actions'][1]['verified_outcomes'],[0])
        self.assertEqual(tape.calls[1]['input']['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['consequence'],0)
        self.assertIs(system.inner.map.memory,system.inner.memory)
        self.assertEqual(system.inner.metrics['memory_corruptions_detected'],1)
        self.assertEqual(len(system.inner.memory.quarantine),0)  # inherited successful repair clears it

    def test_full_record_chronology_and_exact_pair_filter(self):
        bundle=setup(0,'FILTER');mapping=mappings()[0][2]
        for action in ('HOLD','ADVANCE','RETREAT','HOLD'): ordinary(bundle,action)
        records=bundle[0].inner.memory.records
        before=deepcopy(records)
        payload=map_payload(0,'HOLD',reversed(records),mapping)
        self.assertEqual([r['transaction_id'] for r in payload['VERIFIED_CHRONOLOGICAL_HISTORY']],[1,4])
        self.assertEqual(records,before)
        self.assertEqual(map_payload(0,'RETREAT',records,mapping)['VERIFIED_CHRONOLOGICAL_HISTORY'],[])

    def test_invalid_action_stops_before_map_and_world(self):
        row=composed(setup(0,'ADMISSION'),Tape(),'ADMISSION',mappings()[0][2],
                     'ADVANCE',explorer_raw='K1 K2')
        self.assertEqual(row['calls'],dict(Explorer=1,Map=0,Recovery=0))
        self.assertFalse(row['probe']['authorization']['executed'])
        self.assertIsNone(row['probe']['receipt'])


if __name__=='__main__':unittest.main()
