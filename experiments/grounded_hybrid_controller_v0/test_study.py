import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCENARIOS
from .policy import choose
from .worker import run_stage
from .analyze import analyze
from .replay import replay

class FixedClient:
    model_id='synthetic-infrastructure-test'
    horus_model_identity=dict(artifact_sha256='test-only')
    tokenizer=lambda self,*a,**k:SimpleNamespace(input_ids=[1])
    def generate(self,request):
        return dict(raw_output='{"next_state":1,"consequence":0}' if 'next_state' in request['system']
            else '{"consequence":0}',transport_error=None)
def clients(_):return FixedClient(),{'G2':FixedClient()},None

class StudyTests(unittest.TestCase):
    def test_selector_never_flattens_unresolved(self):
        a=[dict(action='ADVANCE',status='UNRESOLVED',value=None),
           dict(action='HOLD',status='GROUNDED',value=dict(consequence=0))]
        self.assertIsNone(choose(a,'HYBRID')['action'])
        a[1]['value']['consequence']=1
        self.assertEqual(choose(a,'HYBRID')['action'],'HOLD')
    @patch('experiments.grounded_hybrid_controller_v0.worker.load_clients',clients)
    def test_matched_protected_scenarios_and_handoff(self):
        with TemporaryDirectory() as d:
            output=Path(d)/'campaign';output.mkdir()
            for scenario in SCENARIOS:
                for arm in ARMS:
                    root=output/'scenarios'/scenario/'work'/arm;root.mkdir(parents=True)
                    with SessionStore(root/'session',False):pass
                    with ModernMemory(root/'memory.sqlite3',True):pass
            for scenario,spec in SCENARIOS.items():
                for stage in (('H1','H2') if spec.get('restart') else ('single',)):
                    run_stage(output,scenario,stage)
            for scenario in SCENARIOS:
                root=output/'scenarios'/scenario
                self.assertEqual(json.loads((root/'matched-seed.json').read_text())['status'],'PASS')
                decisions=json.loads((root/'stage-complete.json').read_text())['decisions']
                for arm in ARMS:self.assertEqual(len(decisions[arm]),2 if scenario=='E_MULTIPLE_UNSEEN' else 1)
            d=json.loads((output/'scenarios/D_UNRESOLVED_BEST/stage-complete.json').read_text())
            self.assertIsNone(d['decisions']['HYBRID'][0]['selected_action'])
            e=json.loads((output/'scenarios/E_MULTIPLE_UNSEEN/stage-complete.json').read_text())
            first=e['decisions']['HYBRID'][0]['selected_action']
            self.assertEqual(next(a for a in e['decisions']['HYBRID'][0]['assessments']
                                  if a['action']==first)['status'],'MODEL_GENERALIZATION')
            self.assertEqual(next(a for a in e['decisions']['HYBRID'][1]['assessments']
                                  if a['action']==first)['status'],'GROUNDED')
            (output/'campaign-complete.json').write_text('{}')
            self.assertEqual(analyze(output)['status'],'COMPLETE')
            self.assertEqual(replay(output)['status'],'PASS')
            h=output/'scenarios/H_RESTART_UNRESOLVED'
            self.assertEqual(json.loads((h/'restart.json').read_text())['status'],'PASS')
            self.assertEqual(json.loads((h/'perturbation.json').read_text())['status'],'PASS')
if __name__=='__main__':unittest.main()
