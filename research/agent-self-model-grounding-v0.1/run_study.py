"""Isolated read-only factual study. No world, receipt or Memory APIs imported."""
from pathlib import Path
from hashlib import sha256
from urllib.request import Request,urlopen
import argparse,json,re,time,subprocess,sys
import jsonschema
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
sys.path.insert(0,str(ROOT))
from publication.audit import SENSITIVE_PATTERNS
PRIVATE=Path('/tmp/horus-agent-self-model-grounding-v0-1-private')
def read(n):return json.loads((P/n).read_text())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def wire(v):return json.dumps(v,separators=(',',':'),ensure_ascii=False).encode()
def sha(v):return sha256(v if isinstance(v,bytes) else v.encode()).hexdigest()
def post(path,value,timeout=30):
 cfg=read('analysis-configuration.json')
 with urlopen(Request(cfg['endpoint']+path,data=wire(value),headers={'Content-Type':'application/json'}),timeout=timeout) as r:return r.read()
def payload(phase):
 common=dict(architecture_manifest=read('architecture-manifest.json'))
 if phase=='A':common.update(authority_graph=read('authority-graph.json'),source_ID_index=read('source-index.json'),current_status_registry=read('current-status-registry.json'))
 else:
  common['verified_phase_a']=read('phase-a-output.json')
  common['synthetic_routing_contexts']=[dict(case_id=c['case_id'],context=c['synthetic_context']) for c in read('routing-cases.json')['cases']]
 return common

def make_request(phase):
 cfg=read('analysis-configuration.json');proto=read('analysis-protocol.json')
 req={k:cfg[k] for k in ('temperature','top_p','top_k','min_p','seed','max_tokens','cache_prompt','stream','chat_template_kwargs')}
 req['messages']=[dict(role='system',content=proto['system']),dict(role='user',content=wire(dict(task=proto['prompts'][phase],inputs=payload(phase))).decode())]
 req['response_format']=dict(type='json_object',schema=proto['schemas'][phase])
 return req

def preflight():
 freeze=read('source-freeze.json')
 for p,h in freeze['sha256'].items():
  if sha((ROOT/p).read_bytes())!=h:raise RuntimeError('source freeze mismatch: '+p)
 for name in ('preregistration.md','source-freeze.json','architecture-manifest.json','authority-graph.json','analysis-protocol.json','analysis-configuration.json','routing-cases.json'):
  rel=str((P/name).relative_to(ROOT))
  if subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)!=(P/name).read_bytes():raise RuntimeError('uncommitted registration: '+name)

def all_objects(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from all_objects(x)
 elif isinstance(v,list):
  for x in v:yield from all_objects(x)

def audit(phase,value):
 failures=[];checks=[]
 def check(label,valid,central=True):
  checks.append(dict(check=label,pass_check=bool(valid),central=central))
  if not valid:failures.append(dict(check=label,central=central))
 try:jsonschema.validate(value,read('analysis-protocol.json')['schemas'][phase])
 except jsonschema.ValidationError as exc:
  return dict(status='FAIL',classification='AGENT_SELF_MODEL_PARTIAL',phase=phase,failures=[dict(check='schema',detail=exc.message,central=False)],checks=checks,quote_comparisons=0)
 allowed={s['source_id'] for s in read('source-index.json')['sources']}
 for i,node in enumerate(all_objects(value)):
  if 'evidence_ids' in node:check('valid_evidence_ids_'+str(i),bool(node['evidence_ids']) and set(node['evidence_ids'])<=allowed,False)
 # Free prose cannot invent code paths/commits; source IDs themselves are allowed.
 rendered=json.dumps(value)
 for path in re.findall(r'[A-Za-z_][A-Za-z0-9_./-]+\.(?:py|md|json)',rendered):
  check('known_code_path_'+path,path in json.dumps(read('source-index.json')),False)
 if phase=='A':
  expected=read('architecture-manifest.json');graph=read('authority-graph.json');v=value['self_model'];aa=v['active_architecture']
  for key in ('ordered_decision_layers','rollback_component','model_route_position'):check(key,aa[key]==graph[key])
  ids=[c['component_id'] for c in v['components']];check('exact_unique_component_set',len(ids)==len(set(ids)) and set(ids)=={c['component_id'] for c in expected['components']})
  lookup={c['component_id']:c for c in v['components']}
  for c in expected['components']:
   got=lookup.get(c['component_id'],{})
   for field in ('status','role','can_select_action','can_execute_world','can_write_memory'):
    check(c['component_id']+'.'+field,got.get(field)==c[field])
   check(c['component_id']+'.uses_model_when_triggered',got.get('uses_model_when_triggered')==c['uses_model_call_when_triggered'])
   check(c['component_id']+'.supporting_citations',set(got.get('evidence_ids',[]))<=set(c['source_ids']),False)
  distinct={(x['a'],x['b']):x for x in v['authority_distinctions']}
  check('exact_distinction_pairs',set(distinct)=={(x['a'],x['b']) for x in graph['distinctions']})
  for x in graph['distinctions']:
   got=distinct.get((x['a'],x['b']),{})
   check(x['a']+' distinct from '+x['b'],got.get('relationship')=='DISTINCT_COMPONENTS')
   check(x['a']+'.distinction_citations',set(got.get('evidence_ids',[]))<=set(x['evidence_ids']),False)
  gotfail={x['condition']:x for x in v['failure_behavior']}
  check('exact_failure_conditions',set(gotfail)=={x['condition'] for x in graph['failure_behavior']})
  for x in graph['failure_behavior']:
   got=gotfail.get(x['condition'],{})
   for k in ('behavior','action_emitted','model_called'):check(x['condition']+'.'+k,got.get(k)==x[k])
  dedicated=value['mandatory_distinction']
  check('grounded_authority_is_not_S',dedicated['is_grounded_mechanical_authority_the_same_component_as_S'] is False)
  check('dedicated_explanation_present',bool(dedicated['explanation'].strip()),False)
  check('dedicated_support',set(dedicated['evidence_ids'])<=set(['SRC-SELECTOR','SRC-ROUTING','SRC-S','SRC-ENTRY']),False)
 else:
  registered=read('routing-cases.json')['cases'];ids=[x['case_id'] for x in value['cases']]
  check('exact_unique_case_set',len(ids)==len(set(ids)) and set(ids)=={x['case_id'] for x in registered})
  lookup={x['case_id']:x for x in value['cases']}
  for c in registered:
   got=lookup.get(c['case_id'],{})
   for k,want in c['expected'].items():check(c['case_id']+'.'+k,got.get(k)==want)
   if not c['expected_action_emitted']:check(c['case_id']+'.no_action_authority',got.get('action_authority_type')=='NO_ACTION' and got.get('model_called') is False)
 classification='PASS' if not failures else 'AGENT_SELF_MODEL_GROUNDING_FAILED' if any(f['central'] for f in failures) else 'AGENT_SELF_MODEL_PARTIAL'
 return dict(status='PASS' if not failures else 'FAIL',classification=classification,phase=phase,checks=checks,failures=failures,quote_comparisons=0,grading='Exact deterministic comparison to preregistered interface/answers; no model grader.')

def call(phase):
 preflight()
 if phase=='B' and read('phase-a-audit.json')['status']!='PASS':raise RuntimeError('Phase A gate blocks Phase B')
 req=make_request(phase);cfg=read('analysis-configuration.json')
 tokens=len(json.loads(post('/tokenize',dict(content='\n'.join(m['content'] for m in req['messages']),add_special=False)))['tokens'])
 if tokens+cfg['max_tokens']+128>cfg['context']:raise RuntimeError('Context overflow before inference; stop, do not tune')
 private=PRIVATE/phase;private.mkdir(parents=True,exist_ok=False);rawreq=wire(req)
 (private/'request.private.json').write_bytes(rawreq)
 (private/'intent.json').write_text(json.dumps(dict(phase=phase,request_sha256=sha(rawreq),prompt_tokens_proxy=tokens))+'\n')
 started=time.monotonic()
 try:raw=post('/v1/chat/completions',req,timeout=600)
 except Exception as e:
  (private/'transport-error.json').write_text(json.dumps(dict(error=repr(e))));raise
 (private/'response.private.json').write_bytes(raw)
 response=json.loads(raw);choice=response['choices'][0];msg=choice['message'];reason=msg.get('reasoning_content');final=msg.get('content')
 meta=dict(phase=phase,request_sha256=sha(rawreq),response_sha256=sha(raw),reasoning_sha256=sha(reason or ''),final_sha256=sha(final or ''),usage=response.get('usage'),finish_reason=choice.get('finish_reason'),wall_seconds=time.monotonic()-started,prompt_tokens_proxy=tokens)
 write('phase-'+phase.lower()+'-call-metadata.json',meta)
 if not isinstance(reason,str) or not reason.strip():raise RuntimeError('Native separated reasoning missing')
 if not isinstance(final,str) or '<think>' in final or '</think>' in final or choice.get('finish_reason')!='stop':raise RuntimeError('Incomplete or mixed final channel')
 value=json.loads(final)
 if any(p.search(wire(value)) for p in SENSITIVE_PATTERNS):raise RuntimeError('Final secret scan failed')
 write('phase-'+phase.lower()+'-output.json',value)
 result=audit(phase,value);write('phase-'+phase.lower()+'-audit.json',result)
 print(json.dumps(dict(phase=phase,status=result['status'],classification=result['classification'],failures=result['failures'],metadata=meta)))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['A','B']);a=p.parse_args()
 try:call(a.phase)
 except Exception as exc:
  write('protocol-stop.json',dict(classification='INVALID',phase=a.phase,error=repr(exc)));raise
