"""Thin host for the inherited scorer; no R2 grading changes or taxonomy rewrites."""
import argparse,hashlib,json,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent

def encode(v):return (json.dumps(v,indent=2,ensure_ascii=True)+'\n').encode()
def load_raw(output):
 freeze=json.loads((output/'raw-freeze.json').read_bytes());root=output/'raw'
 assert freeze['purpose']=='SCIENTIFIC_R2','Mock evidence must never reach scientific scoring'
 files={str(f.relative_to(root)):f for f in root.rglob('*') if f.is_file()};assert set(files)==set(freeze['sha256'])
 for name,f in files.items():assert hashlib.sha256(f.read_bytes()).hexdigest()==freeze['sha256'][name]
 execution=json.loads((root/'execution.json').read_bytes());assert execution['purpose']=='SCIENTIFIC_R2'
 finals={f.stem:f.read_bytes().decode('utf-8') for f in (root/'finals').glob('*.txt')}
 assert len(finals)==execution['completed_calls']
 return finals,execution

def compute():
 from guard import inheritance,frozen_transport,ROOT,schema_compatibility
 inheritance();schema_compatibility();freeze=json.loads((P/'launch-preflight.json').read_bytes())['checks']['transport']['commit'];frozen_transport(freeze)
 # Raw set must be committed before the frozen scorer is imported/called.
 for name in ('raw-freeze.json','raw/execution.json'):
  path=P/name;assert subprocess.check_output(['git','show','HEAD:'+str(path.relative_to(ROOT))],cwd=ROOT)==path.read_bytes()
 raw,execution=load_raw(P)
 sys.path.insert(0,str(B))
 from scorer import score_benchmark
 def read(name):return json.loads((B/name).read_bytes())
 grading=read('materialized/grading.json');rendered={rid:read('materialized/rendered/'+rid+'.json') for rid in grading}
 protocol=read('protocol.json');protocol['matched_pairs']=read('materialized/matched-pairs.json')
 violations=[] if execution['stop'] is None else [execution['stop']['reason']]
 return score_benchmark(raw,grading,rendered,read('diagnostic-schema.json'),protocol,violations=violations)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['primary','replay']);mode=parser.parse_args().mode
 if mode=='primary':
  assert not (P/'scores.json').exists(),'Primary scoring already exists'
  value=encode(compute());(P/'scores.json').write_bytes(value)
  (P/'outcome.json').write_bytes(encode(dict(replacement_id='R2',classification=json.loads(value)['classification'],original_campaign=dict(classification='INVALID_STUDY',calls=0,published_head='bb58926e0f2581bee38393e179b758b18d0879e4'))))
  print(json.dumps({'replacement_id':'R2','classification':json.loads(value)['classification']}))
 else:
  value=encode(compute());assert value==(P/'scores.json').read_bytes()
  report=dict(status='PASS',replacement_id='R2',byte_identical=True,score_sha256=hashlib.sha256(value).hexdigest(),new_model_calls=0)
  if not (P/'replay.json').exists():(P/'replay.json').write_bytes(encode(report))
  print(json.dumps(report))
if __name__=='__main__':main()
