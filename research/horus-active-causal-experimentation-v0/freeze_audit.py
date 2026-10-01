"""Pre-inference freeze audit. Does not run A0 or score scientific predictions."""
import json,subprocess,importlib.util,random
from common import *
from machines import *
from design import generate,PATTERNS
from interface import messages,strict_json

def main():
 worlds=[json.loads(x) for x in (ASSETS/'private/worlds.jsonl').read_text().splitlines()]
 assert len(worlds)==160 and len({w['id'] for w in worlds})==160
 oldpath=Path('/mnt/d/horus-research-assets/causal-machine-v0/private/worlds.jsonl')
 prior=[json.loads(x) for x in oldpath.read_text().splitlines()]
 forbidden={dsl.program_signature(w['program']['roots']) for w in prior}
 forbidden.update(json.loads((P/'design-engineering.json').read_text())['world_graph_hashes'])
 for cohort,count,seed in [('primary',120,851703),('control',40,851704)]:
  expected=[w for w in worlds if w['cohort']==cohort]
  replay,stats=generate(seed,count,forbidden)
  for original,again in zip(expected,replay):
   assert all(original[k]==json.loads(canon(v)) for k,v in again.items())
   forbidden.add(original['graph_sha256'])
 assert len({w['graph_sha256'] for w in worlds})==160
 reset_checks=0
 for w in worlds:
  assert sha({k:v for k,v in w.items() if k!='world_hash'})==w['world_hash']
  reserved=tuple(tuple(p) for p in w['reserved']);allowed=tuple(p for p in PROBES if p not in reserved)
  assert len(reserved)==5 and len(allowed)==79
  assert set(PASSIVE)<=set(allowed)
  assert tuple(pattern(p) for p in reserved)==PATTERNS
  assert all(not(len(p)>=len(q) and p[:len(q)]==q) for p in allowed for q in reserved)
  vm=dsl.Circuit([catalogue()[i] for i in w['root_ids']]);traces=[]
  for p in PROBES:
   state=vm.initial;trace=[]
   for a in p:state,obs=vm.step(state,a);trace.append(list(obs))
   assert trace==outcomes(w['root_ids'],p);reset_checks+=1
   if p in reserved:traces.append(trace)
  assert all(any(row!=trace[0] for row in trace) for trace in traces)
  assert len({canon(trace) for trace in traces})==5
  ports={k:w[k] for k in ['actuators','sensors']}
  visible=messages(ports,dict(zip(w['sensors'],reset_observation(w['root_ids']))),[],allowed=[[w['actuators'][a] for a in p] for p in allowed])
  data=json.loads(visible[1]['content'])
  assert set(data)=={'actuators','sensors','reset_observation','experiments','exact_probe_repeat_counts','allowed_probes','experiment_number','remaining_budget'}
  assert len(data['allowed_probes'])==79
  assert all([w['actuators'][a] for a in p] not in data['allowed_probes'] for p in reserved)
 # Model worker dependency boundary: source-level check for excluded evaluators.
 import ast
 tree=ast.parse((P/'model_worker.py').read_text())
 imported=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):imported.extend(x.name for x in node.names)
  if isinstance(node,ast.ImportFrom):imported.append(node.module)
 assert not set(imported)&{'machines','information','design','materialize'}
 baseline=json.loads((P/'preservation-baseline.json').read_text())
 heads=subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/heads/'],cwd=ROOT,text=True)
 assert set(baseline['local_heads'].splitlines())<=set(heads.splitlines())
 remote=subprocess.check_output(['git','ls-remote','--heads','origin'],cwd=ROOT,text=True)
 assert remote==baseline['remote_heads']
 changed=subprocess.check_output(['git','diff','--name-only',BASE_SHA,'--'],cwd=ROOT,text=True).splitlines()
 assert all(x.startswith('research/horus-active-causal-experimentation-v0/') for x in changed)
 assert filehash(ASSETS/'private/worlds.jsonl')==json.loads((P/'world-qualification.json').read_text())['private_worlds_sha256']
 assert not (ASSETS/'private/campaign-signed.jsonl').exists()
 for name in ['design-tests.json','receipt-tests.json','runtime-qualification.json','context-preflight.json','world-qualification.json','campaign-tests.json']:
  assert json.loads((P/name).read_text())['status']=='PASS',name
 save(P/'pre-freeze-audit.json',dict(status='PASS',deterministic_world_selection_replay=True,reset_trace_compiled_reference_checks=reset_checks,world_graph_uniqueness=True,prior_graphs_checked=len(prior),reserved_prefix_separation=True,visible_catalogue_exactly_79=True,worlds=160,primary_queries=600,reserved_queries_per_world=5,no_world_or_query_leakage=True,oracle_worker_dependency_boundary=True,receipt_authentication_test='PASS',prior_local_heads_preserved=len(baseline['local_heads'].splitlines()),prior_remote_heads_preserved=len(baseline['remote_heads'].splitlines()),inherited_tracked_files_unchanged=True,scientific_model_calls=0,training_steps=0,limitation='Prospective construction and source boundary audit. Actual scientific prompt, receipt reconstruction and raw replay audits remain mandatory after execution.'))
 print((P/'pre-freeze-audit.json').read_text())
if __name__=='__main__':main()
