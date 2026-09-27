import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING
from .reducer import predict
from .worker import run_stage
from .analyze import analyze
from .replay import replay

class FixedClient:
    model_id='synthetic-infrastructure-test'
    horus_model_identity=dict(artifact_sha256='test-only')
    tokenizer=lambda self,*a,**k:SimpleNamespace(input_ids=[1])
    def generate(self,request):
        if 'next_state' in request['system']:
            return dict(raw_output='{"next_state":1,"consequence":0}',transport_error=None)
        return dict(raw_output='{"consequence":0}',transport_error=None)

def clients(_condition):
    return FixedClient(),{'G2':FixedClient()},None

def fresh(root):
    root.mkdir()
    for name in SCHEDULES:
        schedule_root=root/'schedules'/name
        for arm in ARMS:
            path=schedule_root/'work'/arm;path.mkdir(parents=True)
            with SessionStore(path/'session',False):pass
            with ModernMemory(path/'memory.sqlite3',True):pass
            (schedule_root/arm).symlink_to(Path('current')/arm,target_is_directory=True)

class StudyTests(unittest.TestCase):
    def test_frozen_schedules_and_ceiling(self):
        self.assertEqual({k:len(v) for k,v in SCHEDULES.items()},
                         {'A':12,'B':9,'C':12,'D':14})
        self.assertEqual((MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING),(96,192))
        for rows in SCHEDULES.values():
            self.assertEqual([r['event'] for r in rows],list(range(1,len(rows)+1)))
            self.assertEqual(len({r['observation_id'] for r in rows}),len(rows))

    def test_mechanical_rules_and_cold_start(self):
        class Memory:
            def __init__(self,values):self.values=values
            def rows(self,relation):return [dict(event_identity=str(i),
                realized_next_state=1,realized_consequence=v,relation=relation)
                for i,v in enumerate(self.values)]
        for values,l,r in (([],0,0),([1],1,1),([1,-1],-1,-1),
                           ([1,1,-1],-1,1),([1,-1,-1],-1,-1)):
            self.assertEqual(predict(Memory(values),1,'L')['consequence'],l)
            self.assertEqual(predict(Memory(values),1,'R3')['consequence'],r)

    @patch('experiments.grounded_reducer_vs_model_v0.worker.load_clients',clients)
    def test_all_schedules_restart_perturbation_and_exact_replay(self):
        with TemporaryDirectory() as d:
            root=Path(d)/'study';fresh(root)
            for stage in ('A1','A2','B','C','D'):run_stage(root,stage)
            (root/'campaign-complete.json').write_text('{}')
            result=analyze(root);proof=replay(root)
            self.assertEqual(proof['status'],'PASS')
            self.assertEqual(proof['logical_calls'],96)
            self.assertEqual(len(proof['matched_snapshots']),4+47+5)
            self.assertTrue(all(result['totals'][arm]['n']==47 for arm in ARMS))
            self.assertEqual(result['operational']['L']['logical_model_calls'],0)
            self.assertEqual(result['operational']['R3']['logical_model_calls'],0)
            for name,rows in SCHEDULES.items():
                self.assertEqual(json.loads((root/'schedules'/name/'current/triple.json').read_text())['count'],len(rows))

if __name__=='__main__':unittest.main()
