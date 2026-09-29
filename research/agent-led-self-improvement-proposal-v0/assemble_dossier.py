from pathlib import Path
import ast,json,hashlib,re,subprocess,shutil
R=Path(__file__).resolve().parents[2];P=R/'research/agent-led-self-improvement-proposal-v0';S=P/'sources';S.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
entries=[]
def add(id,category,path,mode='full',nodes=None,origin=None):
 p=Path(path);p=p if p.is_absolute() else R/p;raw=(S/(id+p.suffix)).read_bytes() if origin and (S/(id+p.suffix)).exists() else p.read_bytes();text=raw.decode();(S/(id+p.suffix)).write_bytes(raw)
 if mode=='ast':
  tree=ast.parse(text);parts=[]
  for n in tree.body:
   if isinstance(n,(ast.Assign,ast.AnnAssign)):
    names={x.id for chosen in tree.body if isinstance(chosen,(ast.FunctionDef,ast.ClassDef)) and (nodes is None or chosen.name in nodes) for x in ast.walk(chosen) if isinstance(x,ast.Name)}
    targets=n.targets if isinstance(n,ast.Assign) else [n.target]
    if nodes is None or any(isinstance(t,ast.Name) and t.id in names for t in targets):parts.append(ast.unparse(n))
   if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and (nodes is None or n.name in nodes):parts.append(ast.unparse(n))
  text='\n\n'.join(parts)
 elif mode=='methods':
  tree=ast.parse(text);parts=[]
  for cls in tree.body:
   if isinstance(cls,ast.ClassDef):
    for n in cls.body:
     if isinstance(n,ast.FunctionDef) and cls.name+'.'+n.name in nodes:parts.append(ast.unparse(n))
  text='\n\n'.join(parts)
 elif mode=='methods_outline':
  tree=ast.parse(text);parts=[]
  for cls in tree.body:
   if isinstance(cls,ast.ClassDef):
    for n in cls.body:
     if isinstance(n,ast.FunctionDef) and cls.name+'.'+n.name in nodes:
      parts.append('function '+cls.name+'.'+n.name+'('+ast.unparse(n.args)+')')
      for x in ast.walk(n):
       if isinstance(x,ast.If):parts.append('condition: '+ast.unparse(x.test))
       if isinstance(x,ast.Raise):parts.append(ast.unparse(x))
      parts.append('calls: '+', '.join(sorted({ast.unparse(x.func) for x in ast.walk(n) if isinstance(x,ast.Call)})))
  text='\n'.join(parts)
 elif mode=='outline':
  tree=ast.parse(text);parts=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.FunctionDef):parts.append('function '+n.name+'('+ast.unparse(n.args)+')')
   elif isinstance(n,(ast.If,ast.Raise)):parts.append(ast.unparse(n.test) if isinstance(n,ast.If) else ast.unparse(n))
  text='\n'.join(parts)
 elif mode=='report':
  # Fixed neutral excerpt rule: first three prose paragraphs; all classification/recommendation lines;
  # first table, at most 14 lines. No outcome-based sentence selection or rewriting.
  blocks=text.split('\n\n');prose=[b for b in blocks if not b.startswith('#') and not b.startswith('|')]
  selected=prose[:2]
  lines=text.splitlines();selected += [l for l in lines if re.search(r'Classification:|Recommendation:|classification:|recommendation:',l)]
  table=[];started=False
  for l in lines:
   if l.startswith('|'):
    started=True;table.append(l)
    if len(table)==8:break
   elif started:break
  text='\n\n'.join(dict.fromkeys(selected))+('\n\n'+'\n'.join(table) if table else '')
  # Bound whole blocks, never mid-sentence truncation.
  blocks=text.split('\n\n');text='';
  for b in blocks:
   if len(text)+len(b)>2000:continue
   text+=('\n\n' if text else '')+b
 item=dict(id=id,category=category,source_path=str(p.relative_to(R)) if p.is_relative_to(R) else origin,source_sha256=sha(raw),source_copy='sources/'+id+p.suffix,projection_method=mode,projection_sha256=sha(text.encode()),content=text)
 entries.append(item)
# Complete small current rules; deterministic projections of larger boundaries.
arch=[('SRC-ACTIVE-01','grounded_agent/__init__.py','full',None),('SRC-ACTIVE-02','grounded_agent/empirical_policy.py','ast',None),('SRC-ACTIVE-03','grounded_agent/empirical_adapter.py','ast',None),('SRC-ACTIVE-04','grounded_agent/policy.py','ast',None),('SRC-RULE-S','experiments/grounded_stagnation_escape_evaluation_v0/candidate.py','ast',None),('SRC-RULE-E','experiments/empirical_evidence_acquisition_proposal_v0/candidate.py','ast',None),('SRC-GROUND-D','grounded_state/deterministic.py','ast',None),('SRC-GROUND-E','grounded_state/empirical.py','ast',None),('SRC-GROUND-CORE','grounded_state/core.py','ast',['AuthenticatedMemory','derive_relation_state','assess_relation']),('SRC-MEMORY','experiments/modern_memory_vs_horus_v0/storage.py','methods_outline',['ModernMemory.record','ModernMemory.reconcile']),('SRC-AUTH','horus/live.py','methods_outline',['SessionStore._read_stream','SessionStore._validate_events','SessionStore.imported_history']),('SRC-EXECUTE','experiments/grounded_stagnation_escape_evaluation_v0/worker.py','outline',None),('SRC-AUTHORIZE','experiments/realized_event_grounding_v0/framework.py','methods_outline',['RealizedEventFramework._check','RealizedEventFramework.submit_package']),('SRC-ROUTE','experiments/grounded_authority_autonomous_agent_v0/protocol.py','ast',['known_value','select_route']),('SRC-TYPING','experiments/grounded_autonomous_agent_v0/protocol.py','ast',['relation_type'])]
for id,path,mode,nodes in arch:add(id,'architecture',path,mode,nodes)
add('SRC-CURRENT-STATUS','architecture','research/empirical-evidence-acquisition-promotion-v0/result.md','report')
add('SRC-CORE-STATUS','architecture','research/grounded-state-core-v0/architecture.md','report')
for id,path in [('CONST-01','research/empirical-information-stagnation-diagnosis-v0/constraint-provenance.md'),('CONST-02','research/empirical-evidence-acquisition-proposal-v0/constraint-provenance.md'),('CONST-03','engineering/grounded-agent-development-runtime-v0/runtime-manifest.md')]:add(id,'constraint',path)
behavior=[('EVID-UNCERTAINTY','research/grounded-uncertainty-state-v0/report.md'),('EVID-HYBRID','research/grounded-hybrid-controller-v0/report.md'),('EVID-FALLBACK','research/grounded-safe-fallback-v0/report.md'),('EVID-EMPIRICAL','research/grounded-stochastic-relation-v0/report.md'),('EVID-AUTO02','research/grounded-autonomous-agent-v0.2/result.md'),('EVID-AUTHORITY','research/grounded-authority-autonomous-agent-v0/result.md'),('EVID-SENSITIVITY','research/grounded-action-sensitivity-v0/report.md'),('EVID-S-DIAGNOSIS','research/grounded-framework-exploration-diagnosis-v0/campaign-diagnosis.md'),('EVID-S-PROPOSAL','research/grounded-stagnation-escape-proposal-v0/proposal.md'),('EVID-S-EVAL','research/grounded-stagnation-escape-evaluation-v0/result.md'),('EVID-S-REPLICATION','research/grounded-stagnation-escape-replication-v0/result.md'),('EVID-S-PROMOTION','research/grounded-stagnation-escape-promotion-v0/promotion-record.md'),('EVID-QWEN-QUAL','engineering/grounded-agent-development-runtime-v0/qualification.md'),('EVID-QWEN-SUB','research/qwen3-grounded-agent-substitution-v0/result.md'),('EVID-QWEN-THINK','research/qwen3-thinking-action-audit-v0/result.md'),('EVID-QWEN-BOUND0','research/qwen3-bounded-thinking-action-v0/result.md'),('EVID-QWEN-BOUND1','research/qwen3-bounded-thinking-action-v0.1/result.md'),('EVID-QWEN-R128','research/qwen3-r128-autonomous-grounded-agent-v0/result.md'),('EVID-H2','research/empirical-information-stagnation-diagnosis-v0/result.md'),('EVID-E-PROPOSAL','research/empirical-evidence-acquisition-proposal-v0/result.md'),('EVID-E-EVAL','research/empirical-evidence-acquisition-evaluation-v0/result.md'),('EVID-E-REPLICATION','research/empirical-evidence-acquisition-replication-v0/result.md'),('EVID-E-PROMOTION','research/empirical-evidence-acquisition-promotion-v0/result.md')]
for id,path in behavior:add(id,'behavior',path,'report')
add('EVID-REDUCER','behavior','/tmp/horus-v0-closed-loop/research/grounded-reducer-vs-model-v0/results.md','report',origin='research/grounded-reducer-vs-model-v0/results.md (source-only import from grounded-stochastic-relation worktree; no ancestry imported)')
registry=dict(id='REGISTRY-CURRENT',snapshot='69947aa243a69e7ae26db534727a7122922d978d',items=[dict(issue=issue,status=status,evidence_ids=ids) for issue,status,ids in [
 ('deterministic neutral stagnation','SOLVED_PROMOTED',['SRC-RULE-S','EVID-S-PROMOTION']),('deteriorated empirical stagnation with missing evidence','SOLVED_PROMOTED',['SRC-RULE-E','EVID-E-PROMOTION']),('explicit deterministic contradiction uncertainty','SOLVED_PROMOTED',['SRC-GROUND-D','EVID-UNCERTAINTY']),('protected grounded authority over exact experienced relations','SOLVED_PROMOTED',['SRC-ROUTE','EVID-AUTHORITY']),('durable authenticated Memory','SOLVED_PROMOTED',['SRC-MEMORY','SRC-AUTH']),('empirical versus deterministic distinction','SOLVED_PROMOTED',['SRC-GROUND-CORE','EVID-EMPIRICAL']),('Horus as active decision architecture','PARKED_UNSUPPORTED',['SRC-CORE-STATUS']),('Zakhor as necessary durable memory layer','PARKED_UNSUPPORTED',['SRC-CORE-STATUS']),('Qwen as active action model','NOT_PROMOTED',['EVID-QWEN-SUB','EVID-QWEN-R128']),('Dolphin model incumbent/reference','ACTIVE_HISTORICAL_MODEL',['EVID-QWEN-R128'])]],caveat='Promoted does not mean perfect; evidence may justify studying an existing rule. Historical pre-promotion problems must not be presented as unaddressed current defects.')
dump(P/'solved-problem-registry.json',registry)
dump(P/'dossier.json',dict(snapshot=registry['snapshot'],sources=entries))
dump(P/'dossier-manifest.json',dict(snapshot=registry['snapshot'],assembly='Fixed category inventory; source/AST projections; first-three-prose/classification/first-table report extraction. No model-selected sources or proposed solution.',sources=[{k:v for k,v in e.items() if k!='content'} for e in entries]))
print({c:sum(len(e['content']) for e in entries if e['category']==c) for c in ('architecture','constraint','behavior')})
