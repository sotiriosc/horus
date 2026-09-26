"""Regression for the v0.13 post-result serializer defect."""
import unittest
from .problem_ownership_run import _plain_rows

class ProblemOwnershipResultTests(unittest.TestCase):
    def test_authorized_and_abstained_rows_share_public_pre_state_schema(self):
        common=dict(prediction_batch_sequence=1,status="AUTHORIZED",
            explorer={"action":"ADVANCE","reason":"DEADLOCK_INFORMATION_PROBE",
                      "problem_id":"PR-0003","capability_assessment":None},
            receipt={"realized_consequence":-1,"next_state":2},
            forecasts={"ADVANCE":{"valid":True}})
        authorized={**common,"state":1}
        abstained={**common,"prediction_batch_sequence":2,"status":"ABSTAINED",
            "pre_state":2,"receipt":None,"explorer":{**common["explorer"],"action":None}}
        rows=_plain_rows([authorized,abstained])
        self.assertEqual([row["pre_state"] for row in rows],[1,2])

if __name__=="__main__": unittest.main()
