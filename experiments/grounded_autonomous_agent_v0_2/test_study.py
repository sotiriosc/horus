import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .worker import run_stage,rows_of,parse_action
from .analyze import analyze

class FakeAgent:
    def generate(self,request):
        payload=json.loads(request['prompt'].split('\n')[0])
        if 'completed_decisions' in payload:
            value=dict(assessment='NO_CHANGE_PROPOSED',pattern='No supported repeated error.',proposal='NO_CHANGE_PROPOSED')
        elif 'frozen_selected_action' in payload:
            value=dict(reason='Test choice before consequence.',evidence_source=[],
                reliance='UNSEEN_GENERALIZATION',claimed_status=None,claimed_consequence=None)
        else:value=dict(selected_action='ADVANCE')
        return dict(raw_output=json.dumps(value),transport_error=None,
            response_metadata=dict(prompt_eval_count=10,eval_count=5))

class BadDescriptions(FakeAgent):
    def generate(self,request):
        result=super().generate(request)
        payload=json.loads(request['prompt'].split('\n')[0])
        if 'completed_decisions' in payload:result['raw_output']='{"assessment":'
        elif 'frozen_selected_action' in payload:result['raw_output']='{"reason":'
        return result

class InvalidAction(FakeAgent):
    def generate(self,request):
        result=super().generate(request)
        payload=json.loads(request['prompt'].split('\n')[0])
        if 'available_actions' in payload:result['raw_output']='{"selected_action":"FLY"}'
        return result

class CampaignTests(unittest.TestCase):
    def test_strict_action_only(self):
        for raw in ('{}','{"selected_action":"FLY"}',
            '{"selected_action":"HOLD","reason":"extra"}',
            '{"selected_action":"HOLD","selected_action":"RETREAT"}',
            '{"selected_action":"HOLD"', 'HOLD'):
            with self.assertRaises(ValueError):parse_action(raw)
        self.assertEqual(parse_action('{"selected_action":"HOLD"}'),{'selected_action':'HOLD'})

    @patch('experiments.grounded_autonomous_agent_v0_2.worker.ModelClient',FakeAgent)
    def test_three_runs_restart_and_separate_validity(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for run,stages in (('A',('single',)),('B',('first','second')),('C',('single',))):
                for stage in stages:run_stage(root,run,stage)
                with SessionStore(root/'runs'/run/'session',True) as store,ModernMemory(root/'runs'/run/'memory.sqlite3',False) as memory:
                    self.assertEqual(memory.reconcile(store)['authenticated_events'],30)
                    self.assertEqual(len(rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')),7)
                    self.assertEqual(len([c for c in store.records['calls'] if c['kind']=='ACTION_FROZEN']),30)
            result=analyze(root)
            self.assertEqual(result['behavioral_campaign_status'],'VALID')
            self.assertEqual(result['runs']['B']['restart'],'PASS')
            self.assertEqual(result['runs']['A']['metrics']['decision_commentary_calls'],30)

    @patch('experiments.grounded_autonomous_agent_v0_2.worker.ModelClient',BadDescriptions)
    def test_malformed_description_cannot_invalidate_behavior(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);run_stage(root,'A','single')
            with SessionStore(root/'runs/A/session',True) as store,ModernMemory(root/'runs/A/memory.sqlite3',False) as memory:
                self.assertEqual(memory.reconcile(store)['authenticated_events'],30)
                self.assertTrue(all(d['commentary_status']=='INVALID_DECISION_COMMENTARY' for d in rows_of(store,'AUTONOMOUS_AGENT_DECISION')))
                self.assertTrue(all(r['review_status']=='INVALID_SELF_REVIEW' and r['proposal_status'] is None for r in rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')))

    @patch('experiments.grounded_autonomous_agent_v0_2.worker.ModelClient',InvalidAction)
    def test_invalid_action_stops_before_execution(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(RuntimeError):run_stage(root,'A','single')
            with SessionStore(root/'runs/A/session',True) as store:
                self.assertEqual(len(store.records['events']),0)
                self.assertEqual(len([c for c in store.records['calls'] if c['kind']=='REQUEST_INTENT']),2)

if __name__=='__main__':unittest.main()
