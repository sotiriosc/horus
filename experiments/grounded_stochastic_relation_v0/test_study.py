import unittest
from .empirical import fold
from .protocol import BASE, SCHEDULES

def rows(values):
    return [dict(realized_next_state=1,realized_consequence=v,authorization_status='AUTHORIZED',
        event_identity=f'receipt-{i}',receipt_provenance_sha256=f'hash-{i}',event_stream_sequence=i+1)
        for i,v in enumerate(values)]

class EmpiricalStateTests(unittest.TestCase):
    def test_anomaly_does_not_signal_change(self):
        values=[1]*7+[-1]+[1]*6
        self.assertTrue(all(fold(rows(values[:i]))['kind']!='POSSIBLE_REGIME_CHANGE'
                            for i in range(1,len(values)+1)))

    def test_persistent_shift_and_restoration(self):
        values=BASE+[-1]*5+[0,-1,-1]+[1]*5
        self.assertEqual(fold(rows(values[:12]))['kind'],'POSSIBLE_REGIME_CHANGE')
        self.assertEqual(fold(rows(values[:13]))['segment_start'],8)
        self.assertEqual(fold(rows(values[:20]))['kind'],'POSSIBLE_REGIME_CHANGE')
        self.assertEqual(fold(rows(values[:21]))['segment_start'],16)

    def test_information_boundary_and_provenance(self):
        left=[x['consequence'] for x in SCHEDULES['F_STATIONARY_FUTURE'][:10]]
        right=[x['consequence'] for x in SCHEDULES['F_SHIFT_FUTURE'][:10]]
        self.assertEqual(left,right)
        self.assertEqual(fold(rows(left)),fold(rows(right)))
        self.assertEqual(fold(rows(left))['kind'],'VARIABLE_RELATION')
        self.assertEqual(len(fold(rows(left))['receipt_provenance']),10)

    def test_rejects_unauthed_row(self):
        bad=rows([1]);bad[0]['authorization_status']='REJECTED'
        with self.assertRaises(RuntimeError):fold(bad)

if __name__=='__main__':unittest.main()
