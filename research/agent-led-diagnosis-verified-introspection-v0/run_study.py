"""Isolated diagnosis transport and mechanical provenance gates; no active execution."""
from pathlib import Path
from hashlib import sha256
from urllib.request import Request,urlopen
import argparse,json,re,subprocess,sys,time
import jsonschema
P=Path(__file__).resolve().parent;ROOT=P.parents[1];sys.path.insert(0,str(ROOT))
from publication.audit import SENSITIVE_PATTERNS
PRIVATE=Path('/tmp/horus-agent-led-diagnosis-verified-introspection-v0-private')
FILES={'A':'phase-a-diagnoses.json','B':'selected-diagnosis.json','C':'adversarial-diagnosis-audit.json'}
def read(n):return json.loads((P/n).read_text())
def write(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def wire(v):return json.dumps(v,separators=(',',':'),ensure_ascii=False).encode()
def sha(b):return sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
def post(path,v,timeout=30):
 with urlopen(Request(read('analysis-configuration.json')['endpoint']+path,data=wire(v),headers={'Content-Type':'application/json'}),timeout=timeout) as r:return r.read()
def catalog():
 d=read('versioned-behavioral-dossier.json');c={e['evidence_id']:e for e in d['evidence']+d['decision_records']}
 for e in read('self-introspection-manifest.json')['source_index']:c.setdefault(e['evidence_id'],e)
 c['ARCHITECTURE']=read('architecture-state.json');c['REGISTRY']=read('solved-problem-registry.json');c['CONSTRAINTS']=read('constraint-provenance.json')
 for x in read('evidence-gap-register.json')['items']:c[x['evidence_id']]=x
 return c

def evidence_for(ids):
 c=catalog();return [c[x] for x in sorted(set(ids))]

def payload(phase):
 if phase=='A':return dict(architecture=read('architecture-state.json'),introspection_verification={k:v for k,v in read('self-introspection-manifest.json').items() if k!='source_index'},behavioral_dossier=read('versioned-behavioral-dossier.json'),evidence_gap_register=read('evidence-gap-register.json')['items'],solved_problem_registry=read('solved-problem-registry.json'),constraint_provenance=read('constraint-provenance.json'))
 if phase=='B':
  survivors=read('verified-diagnoses.json')['diagnoses'];assert survivors
  return dict(architecture=read('architecture-state.json'),surviving_diagnoses=survivors,cited_evidence=evidence_for([i for d in survivors for i in d['evidence_ids']]),selection_criteria=['evidence strength','current relevance','falsifiability','boundedness','minimal scope'])
 selected=read('selected-diagnosis.json');d=next(x for x in read('verified-diagnoses.json')['diagnoses'] if x['diagnosis_id']==selected['selected_diagnosis_id'])
 return dict(selected_diagnosis=d,selection=selected,cited_evidence=evidence_for(d['evidence_ids']+selected['evidence_ids']),solved_problem_registry=read('solved-problem-registry.json'))

def request(phase):
 cfg=read('analysis-configuration.json');proto=read('analysis-protocol.json')
 req={k:cfg[k] for k in ['temperature','top_p','top_k','min_p','seed','max_tokens','cache_prompt','stream','chat_template_kwargs']}
 req['messages']=[dict(role='system',content=proto['system']),dict(role='user',content=wire(dict(task=proto['prompts'][phase],inputs=payload(phase))).decode())]
 req['response_format']=dict(type='json_object',schema=proto['schemas'][phase]);return req

def preflight():
 for n,h in read('source-freeze.json')['sha256'].items():assert sha((ROOT/n).read_bytes())==h,n
 for n in read('source-freeze.json')['registration_files']:
  path=str((P/n).relative_to(ROOT));assert subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)==(P/n).read_bytes()

def audit_A(v):
 jsonschema.validate(v,read('analysis-protocol.json')['schemas']['A']);cat=catalog();source={s['evidence_id']:s for s in read('self-introspection-manifest.json')['source_index']}
 ids=[d['diagnosis_id'] for d in v['diagnoses']];assert len(ids)==len(set(ids))
 results=[]
 for d in v['diagnoses']:
  checks=[]
  def check(n,ok,detail=None):checks.append(dict(check=n,passed=bool(ok),detail=detail))
  cited=d['evidence_ids'];check('all_evidence_ids_exist',set(cited)<=set(cat))
  ev=[cat[i] for i in cited if i in cat];versions={e['system_version'] for e in ev if 'system_version' in e}
  check('cited_versions_declared',versions<=set(d['system_versions_used']),sorted(versions))
  current=[e for e in ev if e.get('system_version')=='S_PLUS_E_ACTIVE']
  check('current_evidence_anchor_present',bool(current),'Historical evidence alone cannot establish current persistence.')
  check('not_marked_already_addressed',not d['already_addressed_by_S'] and not d['already_addressed_by_E'])
  check('falsifier_and_information_request_present',bool(d['falsifier'].strip()) and bool(d['minimum_new_evidence_needed'].strip()))
  factual=json.dumps([d[k] for k in ['statement','current_relevance','observed','inferred','unknown']])
  raw='\n'.join((ROOT/source[i]['path']).read_text() if i in source else json.dumps(cat[i]) for i in cited if i in cat)
  numbers=re.findall(r'(?<![A-Za-z0-9_])[-+]?\d+(?:\.\d+)?(?![A-Za-z0-9_])',factual)
  missing=[n for n in numbers if n not in raw]
  check('numeric_literals_occur_in_cited_public_evidence',not missing,dict(claimed_numbers=numbers,missing=missing,limit='Literal check only; contextual correspondence must also pass the external source-linked gate.'))
  paths=re.findall(r'[A-Za-z_][A-Za-z0-9_./-]+\.(?:py|md|json)',factual)
  check('no_invented_code_paths',all(p in raw or (ROOT/p).is_file() for p in paths),paths)
  commits=re.findall(r'\b[a-f0-9]{7,40}\b',factual)
  check('no_invented_commit_identifier',all(x in raw for x in commits),commits)
  check('no_hidden_outcome_identifiers',not re.search(r'(?i)hidden (?:world|regime|outcome) (?:is|was|equals)',factual))
  results.append(dict(diagnosis_id=d['diagnosis_id'],mechanical_status='PASS' if all(c['passed'] for c in checks) else 'FAIL',checks=checks,semantic_gate='PENDING_SOURCE_LINKED_REVIEW'))
 consistent=v['no_supported_diagnosis']==(not v['diagnoses'])
 return dict(phase='A',schema_valid=True,empty_answer_consistent=consistent,diagnoses=results,full_gate='PENDING_SOURCE_LINKED_REVIEW' if consistent else 'FAIL',no_output_repair=True,limitations='Free-text entailment, scope, novelty and causal relevance are not proved by token matching. A mandatory source-linked external review must verify every assertion before selection; ambiguous or unsupported factual claims cannot pass. No additional model grades or repairs Phase A.')

def run(phase):
 preflight()
 if phase=='B':assert read('phase-a-audit.json')['full_gate']=='PASS' and read('verified-diagnoses.json')['diagnoses']
 if phase=='C':assert read('selection-audit.json')['status']=='PASS'
 req=request(phase);cfg=read('analysis-configuration.json')
 tokens=len(json.loads(post('/tokenize',dict(content='\n'.join(m['content'] for m in req['messages']),add_special=False)))['tokens'])
 assert tokens+cfg['max_tokens']+128<=cfg['context'],'Context overflow; stop without inference or retuning'
 target=PRIVATE/phase;target.mkdir(exist_ok=False)
 rawreq=wire(req);(target/'request.private.json').write_bytes(rawreq)
 (target/'intent.json').write_text(json.dumps(dict(phase=phase,request_sha256=sha(rawreq),prompt_tokens_proxy=tokens))+'\n')
 started=time.monotonic();raw=post('/v1/chat/completions',req,600);(target/'response.private.json').write_bytes(raw)
 response=json.loads(raw);ch=response['choices'][0];msg=ch['message'];reason=msg.get('reasoning_content');final=msg.get('content')
 meta=dict(phase=phase,request_sha256=sha(rawreq),response_sha256=sha(raw),reasoning_sha256=sha(reason or ''),final_sha256=sha(final or ''),usage=response.get('usage'),finish_reason=ch.get('finish_reason'),wall_seconds=time.monotonic()-started,prompt_tokens_proxy=tokens)
 write(phase.lower()+'-call-metadata.json',meta)
 assert isinstance(reason,str) and reason.strip() and isinstance(final,str) and ch['finish_reason']=='stop'
 assert '<think>' not in final and '</think>' not in final
 v=json.loads(final);jsonschema.validate(v,read('analysis-protocol.json')['schemas'][phase])
 assert not any(p.search(wire(v)) for p in SENSITIVE_PATTERNS)
 write(FILES[phase],v)
 if phase=='A':write('phase-a-audit.json',audit_A(v))
 print(json.dumps(meta))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['A','B','C']);args=p.parse_args()
 try:run(args.phase)
 except Exception as exc:
  write('protocol-stop.json',dict(classification='INVALID',phase=args.phase,error=repr(exc)));raise
