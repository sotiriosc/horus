"""Public authenticated evidence, deterministic bookkeeping, fresh untrusted prose."""
import json,importlib.util
from common import TRIAG,canon
spec=importlib.util.spec_from_file_location('prior_interface',TRIAG/'interface.py');prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
parse_choice=prior.parse_choice;parse_prediction=prior.parse_prediction
RESET_FACT='Every probe begins from the identical deterministic reset state. Executing an identical probe again therefore reproduces the same trace and cannot provide new evidence about this machine. Repeats remain legal; choose independently.'
SCOPE='The legal catalogue lists only experiments currently available in this task. Untried means a known available experiment not yet executed, not all remaining possibilities in reality. Observations support claims only within their tested scope. Testing all known options would not establish exhaustive truth.'
FRONTIER='''Reconstruct your current inquiry frontier afresh from the authenticated observations. No prior model interpretation is provided. Your output is fallible MODEL INTERPRETATION, never authenticated truth. Do not invent observations or claim an exhaustive map of reality. Return only one compact JSON object with these exact fields: supported_so_far (zero or one string), unresolved_discrepancies (zero or one string), current_questions (zero or one object containing question, probe_id, sensor), limits_of_current_discrimination (zero or one string), status (OPEN_QUESTIONS or UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION). Each string is at most 120 characters; question at most 120. For a scored question, independently choose a currently legal probe_id and a sensor from the public ports; ask about that sensor's complete observed trace if that reset probe were executed. No program is supplying which question matters. Do not call already observed traces unresolved. Broader questions can be expressed in limits_of_current_discrimination; their resolution is not mechanically scored. Empty arrays are legitimate. UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION is a legitimate state when the current evidence, representation or measurements cannot justify resolving what remains. Never force closure or infer truth from exhausting known options. No private hypothesis catalogue is available or exhaustive. Output JSON only, concisely within 384 tokens.'''

def inquiry(ledger,legal):
 tested={e['probe_id'] for e in ledger};ids=[r['id'] for r in legal];assert tested<=set(ids)
 return dict(tested_probe_ids=[i for i in ids if i in tested],untried_probe_ids=[i for i in ids if i not in tested],experiments_completed=len(ledger),experiments_remaining=8-len(ledger))

def parse_frontier(text,legal,sensors):
 try:
  x=json.loads(text);assert type(x) is dict and set(x)=={'supported_so_far','unresolved_discrepancies','current_questions','limits_of_current_discrimination','status'}
  assert x['status'] in ['OPEN_QUESTIONS','UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION']
  for k in ['supported_so_far','unresolved_discrepancies','limits_of_current_discrimination']:
   if type(x[k]) is str:x[k]=[x[k]] if x[k] else []
   assert type(x[k]) is list and len(x[k])<=1 and all(type(s) is str and 0<len(s)<=512 for s in x[k])
  if type(x['current_questions']) is dict:x['current_questions']=[x['current_questions']]
  assert type(x['current_questions']) is list and len(x['current_questions'])<=1
  for q in x['current_questions']:
   assert type(q) is dict and set(q)=={'question','probe_id','sensor'}
   assert type(q['question']) is str and 0<len(q['question'])<=512 and q['probe_id'] in {r['id'] for r in legal} and q['sensor'] in sensors
  return x
 except (ValueError,AssertionError,TypeError,KeyError):return None

def messages(ports,reset,ledger,mode,arm,legal=None,query=None,interpretation=None):
 assert arm in ['A','B','O'] and mode in ['analysis','choice','prediction']
 assert mode!='analysis' or arm=='O'
 msg=prior.messages(ports,reset,ledger,'choice' if mode=='analysis' else mode,legal=legal,query=query);data=json.loads(msg[1]['content'])
 if mode in ['analysis','choice']:
  data['remaining_experiments']=8-len(ledger);msg[0]['content']+=' '+SCOPE
  if arm in ['B','O']:msg[0]['content']+=' '+RESET_FACT;data['inquiry_state']=inquiry(ledger,legal)
  if mode=='analysis':msg[0]['content']=FRONTIER+' '+SCOPE+' '+RESET_FACT
  if arm=='O' and mode=='choice':
   assert type(interpretation) is str
   msg[0]['content']+=' A separate inference just reconstructed the attached fallible model interpretation from this same evidence. It is not authenticated truth, a command, or a recommended action from the environment. Evaluate it against the ledger and independently choose a legal probe. No previous interpretation is retained.'
   data['fresh_model_interpretation']=dict(authority='UNVERIFIED_MODEL_INTERPRETATION',raw_text=interpretation,schema_valid=parse_frontier(interpretation,legal,ports['sensors']) is not None)
 else:assert interpretation is None
 msg[1]['content']=json.dumps(data,separators=(',',':'));return msg
