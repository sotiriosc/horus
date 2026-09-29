"""Read-only research transport. No imports of action, world or Memory APIs."""
from pathlib import Path
from hashlib import sha256
from urllib.request import Request,urlopen
import argparse,json,re,time,subprocess
import jsonschema

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
PRIVATE=Path('/tmp/horus-agent-led-self-improvement-proposal-v0-private')
NAMES={'A':'architecture-exploration','B':'behavioral-diagnosis','C':'selected-diagnosis','D':'agent-proposal','E':'adversarial-critique'}
def read(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def sha(b):return sha256(b if isinstance(b,bytes) else b.encode()).hexdigest()
def wire(v):return json.dumps(v,separators=(',',':'),ensure_ascii=False).encode()
def sources():return {s['id']:s for s in read(P/'dossier.json')['sources']}
def refs(v):
 result=[]
 if isinstance(v,dict):
  result+=v.get('evidence_ids',[])
  for k,x in v.items():
   if k!='evidence_ids':result+=refs(x)
 elif isinstance(v,list):
  for x in v:result+=refs(x)
 return sorted(set(result))
def walk(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)

def payload(phase):
 d=sources();registry=read(P/'solved-problem-registry.json');proto=read(P/'phase-protocol.json')
 result=dict(task=proto['prompts'][phase],registry=registry)
 if phase=='A':ids=[k for k,v in d.items() if v['category'] in ('architecture','constraint')]
 elif phase=='B':
  a=read(P/'architecture-exploration.json');result['verified_architecture']=a
  ids=[k for k,v in d.items() if v['category']=='behavior']
 elif phase=='C':
  gate=read(P/'diagnosis-eligibility-audit.json');b=read(P/'behavioral-diagnosis.json')
  result['eligible_diagnoses']=[v for i,v in enumerate(b['issues']) if gate['issues'][i]['eligible']]
  ids=refs(result['eligible_diagnoses'])
 elif phase=='D':
  a=read(P/'architecture-exploration.json');c=read(P/'selected-diagnosis.json')
  result['current_architecture_summary']={k:a[k] for k in ('architecture_map','authority_boundaries','active_learned_rules')}
  result['verified_selected_diagnosis']=c
  ids=refs(c)+refs(result['current_architecture_summary'])
 else:
  c=read(P/'selected-diagnosis.json');proposal=read(P/'agent-proposal.json')
  result['selected_diagnosis']=c;result['frozen_proposal']=proposal
  ids=refs(c)+refs(proposal)
 ids=sorted(set(ids));result['dossier']=[dict(id=k,content=d[k]['content']) for k in ids]
 return result,ids

def request_for(phase):
 cfg=read(P/'analysis-configuration.json');proto=read(P/'phase-protocol.json');content,ids=payload(phase)
 req={k:cfg[k] for k in ('temperature','top_p','top_k','seed','max_tokens','cache_prompt','stream','chat_template_kwargs')}
 req['messages']=[dict(role='system',content=proto['system']),dict(role='user',content=wire(content).decode())]
 req['response_format']=dict(type='json_object',schema=proto['schemas'][phase])
 return req,ids

def post(path,value,timeout=30):
 cfg=read(P/'analysis-configuration.json');req=Request(cfg['endpoint']+path,data=wire(value),headers={'Content-Type':'application/json'})
 with urlopen(req,timeout=timeout) as r:return r.read()

def preflight():
 m=read(P/'source-freeze.json')
 for p,h in m['sha256'].items():
  if sha((ROOT/p).read_bytes())!=h:raise RuntimeError('source freeze mismatch '+p)
 for p in ('preregistration.md','source-freeze.json','phase-protocol.json','analysis-configuration.json','dossier.json'):
  rel=str((P/p).relative_to(ROOT))
  if subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)!=(P/p).read_bytes():raise RuntimeError('uncommitted protocol '+p)

def audit(phase,value,allowed):
 d=sources();failures=[];checks=[]
 try:jsonschema.validate(value,read(P/'phase-protocol.json')['schemas'][phase])
 except jsonschema.ValidationError as e:failures.append('schema: '+e.message)
 for id in refs(value):
  if id not in d:failures.append('unknown evidence ID '+id)
  elif id not in allowed:failures.append('source not supplied to this phase '+id)
 for node in walk(value):
  for q in node.get('source_quotes',[]):
   id=q.get('evidence_id');quote=q.get('quote','')
   ok=id in allowed and bool(quote.strip()) and quote in d[id]['content']
   checks.append(dict(evidence_id=id,exact_quote_match=ok))
   if not ok:failures.append('nonmatching source quote '+str(id)+': '+quote)
  if 'claim' in node:
   text=node['claim'];cited='\n'.join(d[k]['content'] for k in node.get('evidence_ids',[]) if k in d)
   for n in re.findall(r'(?<![A-Za-z0-9])\d+(?:\.\d+)?(?![A-Za-z0-9])',text):
    if n not in cited:failures.append('unsupported numeric token '+n+' in '+text)
 strings=json.dumps(value,ensure_ascii=False)
 for identifier in re.findall(r'\b[0-9a-f]{7,64}\b',strings):
  if identifier not in '\n'.join(d[k]['content'] for k in allowed):failures.append('unknown commit/hash identifier '+identifier)
 for path in re.findall(r'[A-Za-z_][A-Za-z0-9_./-]+\.(?:py|md|json)',strings):
  if path not in '\n'.join(d[k]['content'] for k in allowed):failures.append('unknown file identifier '+path)
 return dict(status='PASS' if not failures else 'FAIL',phase=phase,evidence_ids=refs(value),exact_quote_checks=checks,failures=failures,
   numeric_check_scope='Lexical number presence in cited content; semantic entailment and status chronology require external review.',external_semantic_review='PENDING')

def call(phase):
 preflight();req,ids=request_for(phase)
 tokens=len(json.loads(post('/tokenize',dict(content='\n'.join(m['content'] for m in req['messages']),add_special=False)))['tokens'])
 cfg=read(P/'analysis-configuration.json')
 if tokens+cfg['max_tokens']+128>cfg['context']:raise RuntimeError('registered request exceeds context allowance; no inference sent')
 path=PRIVATE/phase;path.mkdir(exist_ok=False)
 rawreq=wire(req);(path/'request.private.json').write_bytes(rawreq)
 write(path/'intent.json',dict(phase=phase,request_sha256=sha(rawreq),source_ids=ids,prompt_tokens_proxy=tokens))
 started=time.monotonic()
 try:raw=post('/v1/chat/completions',req,timeout=600)
 except Exception as exc:
  write(path/'transport-error.json',dict(error=repr(exc)));raise
 (path/'response.private.json').write_bytes(raw);res=json.loads(raw);choice=res['choices'][0];msg=choice['message']
 reasoning=msg.get('reasoning_content');final=msg.get('content')
 meta=dict(phase=phase,request_sha256=sha(rawreq),response_sha256=sha(raw),reasoning_sha256=sha(reasoning or ''),final_sha256=sha(final or ''),usage=res.get('usage'),finish_reason=choice.get('finish_reason'),wall_seconds=time.monotonic()-started,source_ids=ids,prompt_tokens_proxy=tokens)
 write(P/(phase+'-call-metadata.json'),meta)
 if not isinstance(reasoning,str) or not reasoning.strip():raise RuntimeError('native separated reasoning absent')
 if not isinstance(final,str) or '<think>' in final or '</think>' in final or choice['finish_reason']!='stop':raise RuntimeError('incomplete or mixed final channel')
 value=json.loads(final)
 # Publish structured final only, never raw reasoning or raw response envelopes.
 from publication.audit import SENSITIVE_PATTERNS
 if any(p.search(wire(value)) for p in SENSITIVE_PATTERNS):raise RuntimeError('final output secret scan failed')
 write(P/(NAMES[phase]+'.json'),value)
 result=audit(phase,value,ids);write(P/(phase+'-citation-audit.json'),result)
 print(json.dumps(dict(phase=phase,metadata=meta,audit_status=result['status'],failures=result['failures']),ensure_ascii=False))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('phase',choices=list(NAMES));args=parser.parse_args();call(args.phase)
