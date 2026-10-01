"""Synthetic CPU fault-injection only; no scientific cases or model requests."""
import json,tempfile,unittest,sys
from pathlib import Path
from unittest.mock import patch
from contextlib import ExitStack
import torch
from safetensors.torch import save_file,load_file
P=Path('/home/sotiriosc/horus-causal-machine-learning-v0/research/horus-causal-machine-learning-v0');sys.path.insert(0,str(P))
import training,admission
from common import dump,write_rows,filehash
class Tiny(torch.nn.Module):
 def __init__(self):super().__init__();self.weight=torch.nn.Parameter(torch.tensor([0.25,0.75]))
 def save_pretrained(self,folder):
  folder.mkdir(parents=True,exist_ok=True);save_file({'weight':self.weight.detach().contiguous()},str(folder/'adapter_model.safetensors'))
def fp(model,adapter):return {'weight':model.weight.detach().tolist()} if adapter else {'immutable_base':'synthetic'}
def setstate(model,state):
 with torch.no_grad():model.weight.copy_(state['weight'])
class RecoveryTests(unittest.TestCase):
 def execute(self,root,interrupt=False):
  root.mkdir(exist_ok=True);private=root/'private';private.mkdir(exist_ok=True);adapters=root/'adapters';adapters.mkdir(exist_ok=True)
  dataset=[dict(messages=[{'synthetic_value':i/20}],target=str(i/20)) for i in range(10)];write_rows(root/'D1.jsonl',dataset);dump(root/'M0-base-fingerprints.json',fp(None,False));calls=0
  def loss(model,tok,messages,target):
   nonlocal calls
   calls+=1
   # 10 training examples and both epoch-0/epoch-1 validation complete first.
   if interrupt and calls==13:raise RuntimeError('synthetic infrastructure interruption')
   return ((model.weight-float(target))**2).mean()
  with ExitStack() as ctx:
   for name,val in [('P',root),('OLD',root),('PRIVATE',private),('ADAPTERS',adapters)]:ctx.enter_context(patch.object(training,name,val))
   ctx.enter_context(patch.object(training.stack,'load',side_effect=lambda arm:(Tiny(),None)))
   ctx.enter_context(patch.object(training,'validation_examples',return_value=dataset[:1]));ctx.enter_context(patch.object(training.runtime,'fingerprints',side_effect=fp));ctx.enter_context(patch.object(training.runtime,'loss',side_effect=loss));ctx.enter_context(patch.object(training,'set_peft_model_state_dict',side_effect=setstate));ctx.enter_context(patch.object(training,'commit',return_value='synthetic'));ctx.enter_context(patch.object(training,'emit'))
   for name,val in [('reset_peak_memory_stats',None),('get_rng_state_all',[]),('set_rng_state_all',None),('max_memory_allocated',0),('max_memory_reserved',0)]:ctx.enter_context(patch.object(torch.cuda,name,return_value=val))
   training.train(1)
  return load_file(str(adapters/'C1/adapter_model.safetensors'))['weight'],json.loads((root/'C1-artifact-freeze.json').read_bytes())
 def test_resume_matches_uninterrupted_parameters_optimizer_and_exposures(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);baseline,full=self.execute(p/'baseline')
   with self.assertRaisesRegex(RuntimeError,'synthetic infrastructure'):self.execute(p/'resume',interrupt=True)
   recovered,part=self.execute(p/'resume');self.assertTrue(torch.equal(baseline,recovered));self.assertEqual(part['examples_seen'],20);self.assertEqual(part['optimizer_steps'],4);self.assertEqual(part['recovery_used'],'C1-recovery-step-000002');self.assertEqual([x['loss'] for x in full['loss_curve']],[x['loss'] for x in part['loss_curve']])
 def test_temporal_scores_recover_ids_from_request_records(self):
  with tempfile.TemporaryDirectory() as tmp:
   cases=[dict(id=f'synthetic-{i}',gold={'current_violation':'NO','prior_violation':'UNKNOWN'}) for i in range(540)]
   outputs=[dict(text=json.dumps(c['gold'])) for c in cases];req=dict(record=dict(case_ids=[c['id'] for c in cases]));response=dict(kind='PREDICTION_BATCH',record=dict(id='batch',outputs=outputs));tape=type('Tape',(),dict(arm='synthetic',stream=type('Stream',(),dict(records=[response]))(),index={('REQUEST_BATCH','batch'):req}))()
   with patch.object(admission,'P',Path(tmp)),patch.object(admission,'rows',return_value=cases):result=admission.score_temporal(tape)
   self.assertEqual(result['joint_correct'],540);self.assertEqual(result['schema_valid'],540)
if __name__=='__main__':unittest.main()
