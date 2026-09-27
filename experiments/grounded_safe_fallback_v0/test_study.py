import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCENARIOS,DECISIONS_PER_ARM
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
    def test_only_grounded_nonnegative_is_fallback(self):
        x=[dict(action='HOLD',relation='1:HOLD',status='UNRESOLVED',value=None),
           dict(action='RETREAT',relation='1:RETREAT',status='GROUNDED',value=dict(consequence=0))]
        self.assertIsNone(choose(x,'H_ABSTAIN')['action'])
        safe=choose(x,'H_SAFE')
        self.assertEqual((safe['action'],safe['reason'],safe['action_justified'],safe['optimality_established']),
                         ('RETREAT','SAFE_GROUNDED_FALLBACK',True,False))
        x[1]['value']['consequence']=-1
        self.assertIsNone(choose(x,'H_SAFE')['action'])
        x[1]['value']['consequence']=1
        self.assertEqual(choose(x,'H_SAFE')['reason'],choose(x,'H_ABSTAIN')['reason'])
    @patch('experiments.grounded_safe_fallback_v0.worker.load_clients',clients)
    def test_protected_scenarios_restart_and_probe(self):
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
            count=0
            for scenario,spec in SCENARIOS.items():
                root=output/'scenarios'/scenario
                self.assertEqual(json.loads((root/'matched-seed.json').read_text())['status'],'PASS')
                rows=json.loads((root/'stage-complete.json').read_text())['decisions']
                count+=len(rows['H_SAFE'])
                for arm in ARMS:self.assertEqual(len(rows[arm]),1+bool(spec.get('probe')))
            self.assertEqual(count,DECISIONS_PER_ARM)
            (output/'campaign-complete.json').write_text('{}')
            self.assertEqual(analyze(output)['status'],'COMPLETE')
            self.assertEqual(replay(output)['status'],'PASS')
            h=output/'scenarios/P8_RESTART_SAFE'
            self.assertEqual(json.loads((h/'restart.json').read_text())['status'],'PASS')
            self.assertEqual(json.loads((h/'perturbation.json').read_text())['status'],'PASS')
            p2=json.loads((output/'scenarios/P2_SAFE_ZERO_CONFIRM_WORSE/stage-complete.json').read_text())
            self.assertIsNone(p2['decisions']['H_ABSTAIN'][0]['selected_action'])
            self.assertEqual(p2['decisions']['H_SAFE'][0]['reason'],'SAFE_GROUNDED_FALLBACK')
            self.assertEqual(p2['decisions']['H_SAFE'][0]['realized']['consequence'],0)
if __name__=='__main__':unittest.main()
