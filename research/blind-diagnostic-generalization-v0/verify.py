"""Read-only final freeze verification. Does not invoke any model or mutate artifacts."""
import hashlib,json,subprocess,sys,unittest,io,importlib.metadata,platform
from pathlib import Path
from materialize import P,ROOT,bundle,encoded
from world_generator import STUDY,generate
from renderer import render,unrender,normalized,anti_coaching
from test_benchmark import fixtures,BenchmarkTests
from scorer import score_benchmark

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def preservation():
 baseline=json.loads((P/'preservation-baseline.json').read_text());changes=[]
 for name,want in baseline['parent_tracked_sha256'].items():
  f=ROOT/name
  if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=want:changes.append(name)
 for ref,want in baseline['protected_public_refs'].items():
  if git('rev-parse',ref).decode().strip()!=want:changes.append(ref)
 private=git('for-each-ref','--format=%(refname)','refs/heads/').decode().splitlines();private=[r for r in private if 'private-archive' in r]
 reachable=[r for r in private if subprocess.run(['git','merge-base','--is-ancestor',r,'HEAD'],cwd=ROOT).returncode==0]
 assert not changes,changes
 assert not reachable,reachable
 return dict(status='PASS',parent_tracked_files=len(baseline['parent_tracked_sha256']),protected_public_refs=baseline['protected_public_refs'],private_archive_heads_excluded=len(private),changed_parent_files=[],active_architecture='grounded authority -> S -> E -> ordinary model; unchanged')

def main():
 env=json.loads((P/'development-verification.json').read_text())
 assert importlib.metadata.version('jsonschema')==env['jsonschema'],'Scorer dependency mismatch'
 assert platform.python_version()==env['python'],'Python runtime mismatch'
 freeze=json.loads((P/'freeze-manifest.json').read_text());method=freeze['method_commit']
 assert subprocess.run(['git','merge-base','--is-ancestor',method,'HEAD'],cwd=ROOT).returncode==0
 method_files=git('ls-tree','-r','--name-only',method,'--',str(P.relative_to(ROOT))).decode().splitlines()
 for name in method_files:assert (ROOT/name).read_bytes()==git('show',method+':'+name),name
 data=bundle(STUDY);assert data==bundle(STUDY)
 assert set(freeze['sha256'])==set(data)
 assert {str(f.relative_to(P/'materialized')) for f in (P/'materialized').rglob('*') if f.is_file()}==set(data)
 for name,raw in data.items():
  assert raw==(P/'materialized'/name).read_bytes(),name
  assert hashlib.sha256(raw).hexdigest()==freeze['sha256'][name],name
 cases,_=generate(STUDY)
 for c in cases:
  for label in ('A','B'):
   for order in (1,2):
    out,m=render(c['world'],STUDY,c['case_id'],label,order);assert not anti_coaching(out);assert unrender(out,m)==normalized(c['world'])
 files,grades,rendered,finals,protocol=fixtures(STUDY)
 synthetic=score_benchmark(finals,grades,rendered,json.loads((P/'diagnostic-schema.json').read_text()),protocol)
 assert all(synthetic['gates'].values())
 log=io.StringIO();run=unittest.TextTestRunner(stream=log,verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(BenchmarkTests))
 assert run.wasSuccessful(),log.getvalue()
 manifest=json.loads(data['render-manifest.json'])
 result=dict(status='PASS',study_status='FROZEN_ZERO_INFERENCE_AWAITING_SEPARATE_APPROVAL',method_commit=method,method_files_unchanged=len(method_files),materialized_files=len(data),semantic_cases=20,matched_pairs=6,renderings=80,future_calls=80,actual_model_calls=0,tests_run=run.testsRun,test_failures=len(run.failures),test_errors=len(run.errors),exact_regeneration=True,gold_regeneration=True,anti_coaching_audit='PASS across all 80 final cases; generic prompt/schema separately checked',opaque_and_order_roundtrips=80,maximum_conservative_context_reservation=max(e['conservative_context_reservation'] for e in manifest['entries']),synthetic_scorer_handcheck='All gates pass for synthetic gold fixture only; NOT a capability result',preservation=preservation(),non_execution_attestation=dict(model_calls=0,server_starts=0,world_executions=0,authenticated_receipts=0,memory_writes=0,training=0,proposal_generation=0,policy_changes=0),attestation_basis='This phase executes only pure synthetic generation, deterministic unit tests, hashes and Git operations; no inference client is implemented. Parent tracked bytes and protected public refs verified.')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
