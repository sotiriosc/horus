"""Only authenticated history and public sequence syntax enter model messages."""
import json,collections,importlib.util
from common import TRIAG
spec=importlib.util.spec_from_file_location('prior_triangulation_interface',TRIAG/'interface.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
parse_choice=prior.parse_choice
parse_prediction=prior.parse_prediction
RESET_FACT='Every probe begins from the identical deterministic reset state. Executing an identical probe again therefore reproduces the same trace and cannot provide new evidence about this machine. Repeats remain legal; choose independently.'
FRONTIER_FACT='The structural contrast frontier lists syntax relationships only, not causal facts, predicted outcomes, usefulness, information gain or recommended actions. Decide independently which legal probe to choose.'

def relations(tested,untried):
 a,b=tuple(tested),tuple(untried);out=[]
 if a!=b and len(a)==len(b) and b==a[::-1]:out.append('order_reversal')
 if len(b)==len(a)+1:
  if b[:-1]==a:out.append('one_step_extension')
  if b[1:]==a:out.append('added_context')
  if b[:-1]==a and b[-1]==a[-1]:out.append('repetition_extension')
 if len(a)==len(b)+1 and (a[:-1]==b or a[1:]==b):out.append('removed_context')
 return sorted(out)

def inquiry(ledger,legal):
 tested={e['probe_id'] for e in ledger};ids=[r['id'] for r in legal]
 assert tested<=set(ids)
 return dict(tested_probe_ids=[i for i in ids if i in tested],untried_probe_ids=[i for i in ids if i not in tested],experiments_completed=len(ledger),experiments_remaining=6-len(ledger))

def frontier(ledger,legal):
 state=inquiry(ledger,legal);mapping={r['id']:r['sequence'] for r in legal};groups=[]
 # All matching pairs are included; no utility ranking, truncation or outcome input.
 for tested in state['tested_probe_ids']:
  by_type=collections.defaultdict(list)
  for untried in state['untried_probe_ids']:
   for label in relations(mapping[tested],mapping[untried]):by_type[label].append(untried)
  for label in sorted(by_type):groups.append(dict(tested=tested,structural_relation=label,untried=by_type[label]))
 return groups

def messages(ports,reset,ledger,mode,arm,legal=None,query=None):
 assert arm in ['A','B','C'] and mode in ['choice','prediction']
 msg=prior.messages(ports,reset,ledger,mode,legal=legal,query=query)
 data=json.loads(msg[1]['content'])
 if mode=='choice':
  data['remaining_experiments']=6-len(ledger)
  if arm in ['B','C']:
   msg[0]['content']+=' '+RESET_FACT;data['inquiry_state']=inquiry(ledger,legal)
  if arm=='C':
   msg[0]['content']+=' '+FRONTIER_FACT;data['available_contrasts']=frontier(ledger,legal)
 # Prediction prompt is identical across arms: observations only, no bookkeeping.
 msg[1]['content']=json.dumps(data,separators=(',',':'))
 return msg
