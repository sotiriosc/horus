"""Zero-model interface and schedule checks."""
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;SOURCE=P.parent/'qwen-epistemic-primitive-factorization-v0'
def verify():
 old=json.loads((SOURCE/'materialized/render-manifest.json').read_bytes());new=json.loads((P/'materialized/render-manifest.json').read_bytes());assert old['schedule']==new['schedule'];assert len(set(new['schedule']))==112
 hashes=json.loads((P/'neutral-task-hashes.json').read_bytes())['files'];settings=json.loads((P/'decoding.json').read_bytes());seen=[]
 for oe,e in zip(old['entries'],new['entries']):
  assert {k:v for k,v in oe.items() if k!='request_sha256'}=={k:v for k,v in e.items() if k!='request_sha256'}
  rid=e['render_id'];raw=(SOURCE/'materialized/neutral'/(rid+'.json')).read_bytes();assert hashlib.sha256(raw).hexdigest()==hashes[rid];n=json.loads(raw);payload=(P/'materialized'/e['request_path']).read_bytes();r=json.loads(payload);assert hashlib.sha256(payload).hexdigest()==e['request_sha256'];assert r['messages']==n['messages'];assert r['response_format']=={'type':'json_object','schema':n['response_schema']};assert {k:v for k,v in r.items() if k not in ('messages','response_format')}==settings;seen.append(rid)
 assert set(seen)==set(hashes)==set(new['schedule']);return dict(status='PASS',scientific_model_calls=0,neutral_tasks_byte_hashed=112,messages_and_schemas_exact=112,source_schedule_exact=True,states=56,pairs=28)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
