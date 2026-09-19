import unittest
from .checks import unknown_preflight,Synthetic
from .runtime import Broker,setup,step
from .protocol import schedule


class StudyTests(unittest.TestCase):
    def test_unknown_is_never_historical_memory(self):
        result=unknown_preflight()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['projection_contexts'],288)

    def test_runtime_uses_genuine_recovery_context_without_oracle(self):
        broker=Broker(Synthetic());row=step(setup('ROUTING_TEST'),broker,schedule()[0],0)
        self.assertTrue(row['genuine_recovery'])
        self.assertTrue(row['probe']['authorization']['committed'])
        self.assertEqual([x['role'] for x in broker.calls],['Explorer','Map','Recovery'])
        self.assertEqual(broker.calls[-1]['input']['VERIFIED_REALIZED_EVENT'],dict(next_state=1,consequence=1))
        self.assertEqual(row['unknown_to_known'][0]['after_explorer']['verified_outcomes'],[1])


if __name__=='__main__':unittest.main()
