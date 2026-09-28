import unittest
from .protocol import build_inputs,parse_response,ORDER

class ProtocolTests(unittest.TestCase):
    def test_blind_inputs(self):
        inputs=build_inputs()
        self.assertEqual(tuple(inputs),ORDER)
        for payload in inputs.values():
            self.assertEqual(len(payload['completed_decisions']),30)
            text=str(payload)
            for forbidden in ('world_phase','external_regime','stagnation','bad exploration','SELF_REVIEW'):
                self.assertNotIn(forbidden,text)
            self.assertTrue(all(len(d['action_assessments'])==3 for d in payload['completed_decisions']))
    def test_compact_response_parser(self):
        raw='DIAGNOSIS:\nRepeated choice.\nPROPOSED_CHANGE:\nTry a bounded probe.\nEVIDENCE:\nD04,D05,D06'
        parsed,status=parse_response(raw)
        self.assertEqual(status,'VALID_RESPONSE')
        self.assertEqual(parsed['EVIDENCE'],['D04','D05','D06'])
        self.assertEqual(parse_response('DIAGNOSIS:\nNo\nEVIDENCE:\nNONE')[1],'INVALID_RESPONSE_FORMAT')
if __name__=='__main__':unittest.main()
