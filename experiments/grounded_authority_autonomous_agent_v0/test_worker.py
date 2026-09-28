import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from horus.live import SessionStore
from .worker import run_stage,rows_of,parse_review
from .analyze import analyze

class FakeAgent:
    def generate(self,request):
        payload=json.loads(request['prompt'])
        value=({'assessment':'NO_CHANGE_PROPOSED'} if 'completed_decisions' in payload else
               {'selected_action':payload['available_actions'][0]})
        return dict(raw_output=json.dumps(value),transport_error=None,
            response_metadata=dict(prompt_eval_count=10,eval_count=5))

class WorkerTests(unittest.TestCase):
    def test_review_schema(self):
        self.assertEqual(parse_review('{"assessment":"NO_CHANGE_PROPOSED"}')[1],'VALID_SELF_REVIEW')
        self.assertEqual(parse_review('{"pattern":"x","proposal":"y"}')[1],'VALID_SELF_REVIEW')
        self.assertEqual(parse_review('{"pattern":"x"}')[1],'INVALID_SELF_REVIEW')

    @patch('experiments.grounded_authority_autonomous_agent_v0.worker.ModelClient',FakeAgent)
    def test_three_runs_restart_and_audit(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for run,stages in (('A',('single',)),('B',('first','second')),('C',('single',))):
                for stage in stages:run_stage(root,run,stage)
                with SessionStore(root/'runs'/run/'session',True) as store:
                    self.assertEqual(len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),30)
                    self.assertEqual(len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),7)
            x=analyze(root)
            self.assertEqual(x['behavioral_campaign_status'],'VALID')
            self.assertEqual(x['runs']['B']['restart'],'PASS')
            self.assertEqual(x['aggregate_metrics']['known_negative_with_better_established'],0)

if __name__=='__main__':unittest.main()
