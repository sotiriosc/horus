"""Zero-inference boundary, negative-scoring and durable interruption tests."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from .analysis import score,pair,metrics,criteria
from .contexts import reconstruct,public_contexts,PACKAGE
from .run import perform
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect,DurabilityFailure

SOURCE=None

class Tests(unittest.TestCase):
    def test_reconstruction_all_contexts(self):
        if SOURCE is None:self.skipTest('private preserved R1 source supplied by preflight')
        cs=reconstruct(SOURCE)
        self.assertEqual(public_contexts(cs),json.loads((PACKAGE/'contexts.json').read_text()))
        self.assertEqual(len(cs),42)
        for c in cs:
            h,w=c['requests']['H'],c['requests']['W']
            self.assertEqual({k for k in h if h[k]!=w[k]},{'prompt'})
            self.assertTrue(json.loads(h['prompt'])['VERIFIED_CHRONOLOGICAL_HISTORY'])
            self.assertEqual(json.loads(w['prompt'])['VERIFIED_CHRONOLOGICAL_HISTORY'],[])
    def test_strict_parser_no_format_accuracy(self):
        receipt=dict(next_state=1,realized_consequence=1)
        for raw in ['{}','{"next_state":true,"consequence":1}','{"next_state":1,"consequence":1,"x":0}','{"next_state":1,"next_state":1,"consequence":1}']:
            self.assertFalse(score(raw,receipt)['valid']);self.assertFalse(score(raw,receipt)['exact'])
        self.assertTrue(score('{"next_state":1,"consequence":1}',receipt)['exact'])
    def test_discordance_and_thresholds(self):
        yes=dict(valid=True,exact=True,next_state=True,consequence=True,prediction=dict(next_state=1,consequence=1))
        no={**yes,'exact':False,'consequence':False,'prediction':dict(next_state=1,consequence=0)}
        pairs=[dict(context_index=i,episode=i,decision=0,family='O1' if i<21 else 'O2',depth=1,state=1,action='HOLD',alias='K1',H=yes,W=no,output_change='consequence_changed_only',visibility_W_to_H='wrong_to_exact') for i in range(42)]
        m=metrics(pairs);self.assertEqual(m['effects']['exact']['net'],42)
        self.assertTrue(all(criteria(m,True,True,True,True).values()))
        self.assertFalse(all(criteria(m,True,True,True,False).values()))
        for p in pairs:p['H'],p['W']=p['W'],p['H']
        self.assertFalse(criteria(metrics(pairs),True,True,True,True)['favorable_minus_reverse_at_least_10'])
    def test_write_ahead_and_response_before_parse(self):
        if SOURCE is None:self.skipTest('private source required')
        c=reconstruct(SOURCE)[0]
        with tempfile.TemporaryDirectory() as folder:
            j=Journal(Path(folder)/'evidence',campaign='TEST')
            class Fake:
                requests=0
                def generate(self,call):
                    audit=inspect(j.directory);assert len(audit['ambiguous_calls'])==1
                    self.requests+=1
                    return dict(raw_output='{"next_state":1,"consequence":1}',transport_error=None,response_metadata={})
            original=score
            def checked(raw,receipt):
                states=inspect(j.directory)['call_states'];assert list(states.values())==['RESPONSE_RECEIVED']
                return original(raw,receipt)
            with (j.directory/'model-calls.jsonl').open('x') as stream,patch('experiments.composition_map_memory_ablation_v0.run.score',checked):
                perform(c,'H',0,j,Fake(),stream)
            j.close();self.assertFalse(inspect(j.directory)['ambiguous_calls'])
    def test_storage_failure_prevents_send_and_ambiguous_call_stops(self):
        if SOURCE is None:self.skipTest('private source required')
        c=reconstruct(SOURCE)[0]
        class Never:
            requests=0
            def generate(self,call):raise AssertionError('must never send')
        with tempfile.TemporaryDirectory() as folder:
            j=Journal(Path(folder)/'evidence',campaign='TEST')
            with (j.directory/'model-calls.jsonl').open('x') as stream,patch.object(j,'append',side_effect=DurabilityFailure('simulated disk failure')):
                with self.assertRaises(DurabilityFailure):perform(c,'H',0,j,Never(),stream)
            j.close()
        class Ambiguous:
            requests=0
            def generate(self,call):
                self.requests+=1;return dict(raw_output=None,transport_error='TimeoutError',response_metadata={})
        with tempfile.TemporaryDirectory() as folder:
            j=Journal(Path(folder)/'evidence',campaign='TEST');client=Ambiguous()
            with (j.directory/'model-calls.jsonl').open('x') as stream:
                with self.assertRaises(RuntimeError):perform(c,'H',0,j,client,stream)
            j.close();self.assertEqual(client.requests,1);self.assertEqual(len(inspect(j.directory)['ambiguous_calls']),1)

if __name__=='__main__':unittest.main()
