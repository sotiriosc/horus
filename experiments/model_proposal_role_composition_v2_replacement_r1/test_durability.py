"""Zero-network durability simulation and instrumentation equivalence."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from experiments.model_proposal_role_composition_v2 import runtime
from experiments.model_proposal_role_composition_v2.checks import Synthetic
from experiments.model_proposal_role_composition_v2.protocol import schedule
from .durable import Journal,inspect,call_id,atomic_write,append_line,DurabilityFailure,require_durable
from .instrumentation import DurableTransport,observe_boundaries

BASE=None

def fixture_call():
    return dict(episode=0,decision=0,role='Explorer',mapping=schedule()[0]['mapping'],current_state=0,memory=[],
        model='synthetic-no-model',system='test',exact_prompt='{}',options={'seed':80002},input={})


def crash_child(path,phase):
    j=Journal(path,'DURABILITY_TEST');j.episode=0;j.decision=0;c=fixture_call();cid=call_id(j.campaign,0,0,'Explorer')
    if phase>=1:j.intent(c)
    if phase>=2:j.response(cid,dict(raw_output='K1',response_metadata={'synthetic':True},transport_error=None))
    if phase>=3:j.parsed({**c,'raw_output':'K1','parsed':dict(surface='K1',action='ADVANCE'),'parse_error':None})
    if phase>=4:
        j.append('TRANSACTION_FINALIZED',{'synthetic_durability_phase':True})
        atomic_write(j.directory/'campaign-state.json',dict(journal_head_sha256=j.previous,status='TRANSACTION_FINALIZED'))
    os._exit(73)  # abrupt process exit: no close/destructor cleanup


class DurabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='r1-durability-',dir=BASE);self.root=Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()

    def test_real_crash_restart_all_five_states(self):
        expected=['NOT_ISSUED','REQUEST_INTENT_RECORDED','RESPONSE_RECEIVED','PARSED','TRANSACTION_FINALIZED']
        for phase,status in enumerate(expected):
            path=self.root/str(phase)
            code='from experiments.model_proposal_role_composition_v2_replacement_r1.test_durability import crash_child; crash_child('+repr(str(path))+','+str(phase)+')'
            run=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True)
            self.assertEqual(run.returncode,73,run.stderr)
            result=inspect(path,call_id('DURABILITY_TEST',0,0,'Explorer'))
            self.assertEqual(result['expected_call_status'],status);self.assertTrue(result['journal_valid'])
            self.assertFalse(result['automatic_reissue_allowed']);self.assertFalse(result['automatic_resume_allowed'])
            if phase==1:self.assertEqual(len(result['ambiguous_calls']),1)
            with self.assertRaises(FileExistsError):Journal(path,'DURABILITY_TEST')

    def test_intent_fsync_precedes_send_response_fsync_precedes_parse(self):
        j=Journal(self.root/'ordering','ORDERING_TEST');j.episode=0;j.decision=0
        original=os.fsync;seen=[]
        def sync(fd):seen.append(fd);return original(fd)
        class Base:
            def generate(inner,call):
                self.assertTrue(seen);self.assertEqual(next(iter(inspect(j.directory)['call_states'].values())),'REQUEST_INTENT_RECORDED')
                return dict(raw_output='K1',response_metadata={'synthetic':True},transport_error=None)
        with patch('os.fsync',side_effect=sync):
            result=DurableTransport(Base(),j).generate(fixture_call());self.assertEqual(next(iter(inspect(j.directory)['call_states'].values())),'RESPONSE_RECEIVED')
            j.parsed({**fixture_call(),**result,'parsed':dict(surface='K1',action='ADVANCE'),'parse_error':None})
        self.assertGreaterEqual(len(seen),3);j.close()

    def test_torn_record_and_duplicate_intent_stop_without_reissue(self):
        j=Journal(self.root/'torn','TORN');j.episode=0;j.decision=0;j.intent(fixture_call())
        with self.assertRaises(DurabilityFailure):j.intent(fixture_call())
        j.close()
        with (self.root/'torn/journal.jsonl').open('ab') as stream:stream.write(b'{"partial":');stream.flush();os.fsync(stream.fileno())
        audit=inspect(self.root/'torn');self.assertFalse(audit['journal_valid']);self.assertFalse(audit['automatic_reissue_allowed'])

    def test_fsync_failure_is_not_a_scientific_rejection(self):
        j=Journal(self.root/'failure','FAILURE');j.episode=0;j.decision=0
        with patch('os.fsync',side_effect=OSError('simulated storage failure')):
            with self.assertRaises(DurabilityFailure):j.intent(fixture_call())
        j.close()

    def test_all_boundary_records_and_exact_frozen_transaction_equivalence(self):
        d=schedule()[0];label='EQUIVALENCE_TEST'
        old=runtime.Broker(Synthetic());expected=runtime.step(runtime.setup(label),old,d,0)
        j=Journal(self.root/'equivalence','EQUIVALENCE_TEST');j.episode=0;j.decision=0
        broker=runtime.Broker(DurableTransport(Synthetic(),j),j.parsed)
        with observe_boundaries(j):actual=runtime.step(runtime.setup(label),broker,d,0)
        self.assertEqual(actual,expected);self.assertEqual(broker.calls,old.calls)
        with (j.directory/'model-calls.jsonl').open('x') as cf:
            for c in broker.calls:append_line(cf,c)
        with (j.directory/'steps.jsonl').open('x') as sf:append_line(sf,actual)
        j.finalize(actual,broker.calls,{'0':'ONGOING'});j.close()
        rows=[json.loads(s) for s in (self.root/'equivalence/journal.jsonl').read_text().splitlines()]
        kinds=[r['status'] for r in rows]
        for status in ('PREDICTION_LATCHED','EXTERNAL_EVENT','AUTHENTIC_RECEIPT','MEASURE_RESULT','RECOVERY_OPPORTUNITY',
                       'RECOVERY_CANDIDATE_ENVELOPE','CANDIDATE_ENVELOPE','AUTHORIZER_DECISION','COMMIT_OR_REJECTION','TRANSACTION_FINALIZED'):
            self.assertIn(status,kinds)
        self.assertLess(kinds.index('PREDICTION_LATCHED'),kinds.index('EXTERNAL_EVENT'))
        self.assertLess(kinds.index('EXTERNAL_EVENT'),kinds.index('AUTHENTIC_RECEIPT'))
        self.assertTrue(inspect(self.root/'equivalence')['campaign_state_matches_journal'])

    def test_ephemeral_output_is_rejected(self):
        for p in ('/tmp/r1','/var/tmp/r1','/dev/shm/r1','/run/r1'):
            with self.assertRaises(ValueError):require_durable(p)


if __name__=='__main__':unittest.main()
