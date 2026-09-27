"""Finite parser, model-visible context and inherited authorization boundaries."""
import json
import unittest
from .adapter import parse,INVALID,SYSTEM
from .campaign import registration,probe,FixedResponse,controls
from .analysis import summarize
from .preflight import check


class RecoveryModelTests(unittest.TestCase):
    def test_strict_parser(self):
        for i in range(4):self.assertEqual(parse(json.dumps({'replacement_state':i})),i)
        for raw in INVALID:
            with self.assertRaises(ValueError):parse(raw)

    def test_schedule_balance_and_context_isolation(self):
        plan,_=registration();self.assertEqual(len(plan),96)
        for family in ('O1','O2'):
            subset=[d for d in plan if d['family']==family]
            self.assertEqual(len(subset),48)
            for fixture in range(8):
                group=[d for d in subset if d['fixture']['fixture_id']==fixture]
                self.assertEqual(sorted(d['seed'] for d in group),list(range(70001,70007)))
                self.assertEqual(len({tuple(d['mapping'].items()) for d in group}),6)
                for token in group[0]['mapping']:
                    self.assertEqual(sum(d['surface_action']==token for d in group),2)
        for d in plan:
            payload=json.loads(d['exact_prompt'])
            self.assertEqual(set(payload),{'pre_state','action','VERIFIED_REALIZED_EVENT','measurement_matches','allowed_replacement_states'})
            self.assertNotIn(d['fixture']['action'],d['exact_prompt'])
            self.assertIs(payload['measurement_matches'],False)
            self.assertNotIn('RECOVERING',d['exact_prompt'])

    def test_full_zero_call_preflight(self):
        summary,_,_,_=check();self.assertEqual(summary['correct_authorizations'],96)
        self.assertEqual(summary['wrong_rejections'],96);self.assertEqual(summary['actual_model_calls'],0)

    def test_malformed_output_has_one_opportunity_and_no_authority(self):
        d=registration()[0][0]
        for raw in ('{}','{"replacement_state":true}'):
            transport=FixedResponse(raw);row=probe(transport,d)
            self.assertEqual(transport.requests,1);self.assertEqual(row['callback_count'],1)
            self.assertFalse(row['probe']['authorization']['committed'])
            self.assertEqual(row['probe']['before'],row['probe']['after'])
            self.assertFalse(any(e['kind'].endswith('authorizer') for e in row['events']))

    def test_wrong_value_not_repaired_and_envelope_framework_owned(self):
        d=registration()[0][0];wrong=(d['fixture']['actual_next_state']+1)%4
        row=probe(FixedResponse(json.dumps({'replacement_state':wrong})),d)
        auth=next(e for e in row['events'] if e['kind']=='status_authorizer')
        self.assertEqual(auth['candidate']['value'],wrong)
        self.assertEqual(auth['candidate']['status'],'RECOVERING')
        self.assertTrue(auth['state_recovery']);self.assertFalse(auth['accepted'])
        self.assertEqual(row['probe']['commit_delta'],0)

    def test_usefulness_does_not_pool_families(self):
        plan,_=registration();rows=[]
        for d in plan:
            target=d['fixture']['actual_next_state']
            value=target if d['family']=='O1' else (target+1)%4
            rows.append(probe(FixedResponse(json.dumps({'replacement_state':value})),d))
        s=summarize(rows,controls(plan))
        self.assertEqual(s['families']['O1']['support'],'SUPPORTED')
        self.assertEqual(s['families']['O2']['support'],'NOT ESTABLISHED')
        self.assertEqual(s['authorization_integrity'],'PASS')
        self.assertEqual(s['overall'],'MODEL RECOVERY PROPOSAL USEFULNESS NOT ESTABLISHED')


if __name__=='__main__':unittest.main()
