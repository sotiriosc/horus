import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCHEDULES,EVENTS_PER_ARM
from .uncertainty import fold
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

def row(i,v):return dict(realized_next_state=1,realized_consequence=v,authorization_status='AUTHORIZED',
    event_identity=str(i),receipt_provenance_sha256='hash'+str(i),event_stream_sequence=i)

class StudyTests(unittest.TestCase):
    def test_rule_and_third_value(self):
        self.assertEqual(fold([])['kind'],'UNSEEN')
        self.assertEqual(fold([row(1,1)])['kind'],'ESTABLISHED')
        s=fold([row(1,1),row(2,-1)])
        self.assertEqual((s['kind'],s['candidate_count'],s['candidate_support']),('UNRESOLVED_CHANGE',1,['2']))
        self.assertEqual(fold([row(1,1),row(2,-1),row(3,-1)])['established_value']['consequence'],-1)
        self.assertEqual(fold([row(1,1),row(2,-1),row(3,1)])['established_value']['consequence'],1)
        s=fold([row(1,1),row(2,-1),row(3,0)])
        self.assertEqual(s['kind'],'UNRESOLVED_CHANGE')
        self.assertEqual(len(s['receipt_provenance']),3)
        self.assertEqual(s['alternatives'][0]['support'],['2'])

    @patch('experiments.grounded_uncertainty_state_v0.worker.load_clients',clients)
    def test_protected_four_arm_campaign(self):
        with TemporaryDirectory() as d:
            root=Path(d)/'study';root.mkdir()
            for name in SCHEDULES:
                schedule=root/'schedules'/name
                for arm in ARMS:
                    path=schedule/'work'/arm;path.mkdir(parents=True)
                    with SessionStore(path/'session',False):pass
                    with ModernMemory(path/'memory.sqlite3',True):pass
                    (schedule/arm).symlink_to(Path('current')/arm,target_is_directory=True)
            for stage in ('SUSTAINED1','SUSTAINED2','ANOMALY','EXCURSION','NOISE_THEN_CHANGE'):
                run_stage(root,stage)
            (root/'campaign-complete.json').write_text('{}')
            result=analyze(root);proof=replay(root)
            self.assertEqual(result['classification'],'EXPLICIT_UNCERTAINTY_SUPPORTED')
            self.assertEqual(proof['status'],'PASS')
            self.assertEqual(result['totals']['U']['events'],EVENTS_PER_ARM)
            self.assertEqual(result['uncertainty']['missed_ambiguity_count'],0)
            self.assertEqual(result['costs']['U']['logical_model_calls'],0)
            self.assertTrue(any(x['status']=='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH'
                for x in result['information_boundary_audit']))
if __name__=='__main__':unittest.main()
