"""Posthoc inventory and incumbent replay. Never prints private stream content."""
import json,sys
from pathlib import Path
sys.path.insert(0,'/home/sotiriosc/horus-causal-machine-learning-v0/research/horus-causal-machine-learning-v0')
from common import *
import stack
from receipts import Stream,key
raw=json.loads((P/'incumbent-reproduction-raw-freeze.json').read_bytes());path=PRIVATE/raw['private_file'];assert filehash(path)==raw['sha256'];cs=rows(OLD/'materialized/T1.jsonl');outputs=rows(path);scored=stack.temporal_analysis.score(cs,outputs);assert sum(s['joint'] for s in scored)==540 and all(s['schema'] for s in scored)
for c,o in zip(cs,outputs):assert o['messages']==stack.temporal_data.messages(c)
inventory=[]
for path in sorted(PRIVATE.iterdir()):
 if not path.is_file() or path.name=='authority.key':continue
 item=dict(private_file=path.name,sha256=filehash(path),bytes=path.stat().st_size)
 if path.name.endswith('-signed.jsonl'):item['authenticated_records']=len(Stream(path,key()).verify())
 inventory.append(item)
dump(P/'private-evidence-audit.json',dict(status='PASS',incumbent_reproduction_replayed=540,incumbent_joint_and_schema=540,authority_key_remains_private=True,private_files=inventory,scope='Hashes/inventory only; private contents and authority material are excluded from Git. Scientific stream/token/target and candidate artifact checks are recorded in replay-and-oracle-audit.json.'))
print(json.dumps(dict(status='PASS',private_files=len(inventory),incumbent_reproduction_replayed=540)))
