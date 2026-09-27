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
            ids=[d['decision_id'] for d in payload['completed_decisions']]
            value=dict(SELF_REVIEW=dict(recent_decisions=ids,what_worked='Observed receipt outcomes were recorded.',
                what_failed='No supported failure claim.',mistakes_or_missed_evidence='None established.',
                uncertainty_handling='Unseen states remain unseen.',repeated_pattern='No defensible pattern.',
                proposed_behavioral_hypothesis='NO_CHANGE_PROPOSED',supporting_decisions=ids,
                confidence='LOW'))
        else:
            value=dict(selected_action='ADVANCE',reason='Test only: choose an allowed action.',
                evidence_source=[],reliance=('GROUNDED' if payload['grounded_assessments']['ADVANCE']['assessment_status']=='GROUNDED'
                    else 'UNSEEN_GENERALIZATION'),claimed_status=None,claimed_consequence=None)
        return dict(raw_output=json.dumps(value),transport_error=None,
                    response_metadata=dict(prompt_eval_count=10,eval_count=5))


class MalformedDescriptionAgent(FakeAgent):
    def generate(self,request):
        result=super().generate(request)
        value=json.loads(result['raw_output'])
        if 'SELF_REVIEW' in value:
            value={'SELF_REVIEW':{'recent_decisions':['HOLD']}}
        else:
            value['reliance']=0
        result['raw_output']=json.dumps(value)
        return result

class InvalidActionAgent(FakeAgent):
    def generate(self,request):
        return dict(raw_output='{"selected_action":"FLY"}',transport_error=None,
                    response_metadata=dict(prompt_eval_count=10,eval_count=5))

class CampaignTests(unittest.TestCase):
    @patch('experiments.grounded_autonomous_agent_v0_1.worker.ModelClient',FakeAgent)
    def test_three_protected_runs_and_fresh_process_restart(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            for run,stages in (('A',('single',)),('B',('first','second')),('C',('single',))):
                for stage in stages:run_stage(root,run,stage)
                path=root/'runs'/run
                with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
                    self.assertEqual(memory.reconcile(store)['authenticated_events'],30)
                    self.assertEqual(len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),30)
                    reviews=rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')
                    self.assertEqual(len(reviews),6)
                    self.assertTrue(all(x['non_authoritative'] and x['no_memory_or_state_change'] for x in reviews))
                if run=='B':
                    self.assertEqual(json.loads((path/'restart-verdict.json').read_text())['status'],'PASS')
            result=analyze(root)
            self.assertEqual(result['status'],'COMPLETE')
            self.assertEqual(set(result['runs']),{'A','B','C'})

    def test_action_parse_is_strict(self):
        for raw in ('{}','{"selected_action":"FLY"}',
                    '{"selected_action":"HOLD","selected_action":"RETREAT"}',
                    '{"selected_action":"HOLD","action":"RETREAT"}'):
            with self.assertRaises(ValueError):parse_action(raw)
        self.assertEqual(parse_action('{"selected_action":"HOLD","reliance":0}')['selected_action'],'HOLD')

    @patch('experiments.grounded_autonomous_agent_v0_1.worker.ModelClient',MalformedDescriptionAgent)
    def test_malformed_descriptions_and_reviews_never_gain_authority(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp);run_stage(root,'A','single')
            with SessionStore(root/'runs/A/session',True) as store,ModernMemory(root/'runs/A/memory.sqlite3',False) as memory:
                self.assertEqual(memory.reconcile(store)['authenticated_events'],30)
                decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
                reviews=rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE')
                self.assertTrue(all(d['action_parse_status']=='VALID' and
                    d['descriptive_status']=='INVALID_DESCRIPTIVE_OUTPUT' for d in decisions))
                self.assertTrue(all(r['review_status']=='INVALID_SELF_REVIEW' and
                    r['proposal_status'] is None and r['no_memory_or_state_change'] for r in reviews))
                calls=[x for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
                self.assertEqual(len(calls),36)

    @patch('experiments.grounded_autonomous_agent_v0_1.worker.ModelClient',InvalidActionAgent)
    def test_invalid_action_stops_before_world_execution(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaises(RuntimeError):run_stage(root,'A','single')
            with SessionStore(root/'runs/A/session',True) as store,ModernMemory(root/'runs/A/memory.sqlite3',False) as memory:
                self.assertEqual(len(store.records['events']),0)
                self.assertEqual(memory.reconcile(store)['authenticated_events'],0)
                self.assertEqual(len([x for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']),2)

if __name__=='__main__':unittest.main()
