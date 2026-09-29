"""Use frozen scorer once for primary result; separate exact replay, no inference."""
import argparse,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent;sys.path.insert(0,str(B))
from scorer import score_benchmark

def raw(path):return path.read_bytes()
def load(path):return json.loads(raw(path))
def encode(value):return (json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()
def score():
 freeze=load(P/'raw-freeze.json');root=P/'raw'
 files={str(f.relative_to(root)):f for f in root.rglob('*') if f.is_file()}
 assert set(files)==set(freeze['sha256'])
 for name,path in files.items():assert hashlib.sha256(raw(path)).hexdigest()==freeze['sha256'][name],name
 execution=load(root/'execution.json')
 finals={f.stem:raw(f).decode('utf-8') for f in (root/'finals').glob('*.txt')}
 assert len(finals)==execution['completed_calls']
 grading=load(B/'materialized/grading.json');rendered={rid:load(B/'materialized/rendered'/(rid+'.json')) for rid in grading}
 protocol=load(B/'protocol.json');protocol['matched_pairs']=load(B/'materialized/matched-pairs.json')
 violations=[] if execution['stop'] is None else [execution['stop']['reason']]
 return score_benchmark(finals,grading,rendered,load(B/'diagnostic-schema.json'),protocol,violations=violations)

def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['primary','replay']);mode=a.parse_args().mode
 result=encode(score())
 if mode=='primary':
  with (P/'scores.json').open('xb') as f:f.write(result)
  print(result.decode(),end='')
 else:
  assert result==raw(P/'scores.json'),'Exact score replay mismatch'
  replay=dict(status='PASS',score_bytes_identical=True,score_sha256=hashlib.sha256(result).hexdigest(),new_inference_calls=0,raw_freeze_sha256=hashlib.sha256(raw(P/'raw-freeze.json')).hexdigest(),limitation='Reproduces INVALID_STUDY for preserved pre-request transport failure; no diagnostic performance was measured')
  with (P/'replay.json').open('xb') as f:f.write(encode(replay))
  print(json.dumps(replay))
if __name__=='__main__':main()
