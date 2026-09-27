import json,unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .worker import run_stage,rows_of
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

class CampaignTests(unittest.TestCase):
    @patch('experiments.grounded_autonomous_agent_v0.worker.ModelClient',FakeAgent)
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

if __name__=='__main__':unittest.main()
