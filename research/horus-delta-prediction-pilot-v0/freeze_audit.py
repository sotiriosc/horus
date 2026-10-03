"""Zero-inference exact world regeneration and public-only message qualification."""
import ast,time,random
from common import *
from design import generate,prior_graphs
from machines import PROBES,catalogue
from interface import messages
from legal_choice import LegalChoiceTrie
from qualify_interface import synthetic_analysis
from runtime import CONTEXT,TEXT_MAX_NEW

def main():
 start=time.monotonic();forbidden=prior_graphs();forbidden.update(json.loads((P/'design-engineering.json').read_text())['world_graph_hashes'])
 worlds,_=generate(100403,16,forbidden)
 for i,w in enumerate(worlds):w['id']=f'delta-{i+1:03d}';w['world_hash']=sha(w)
 assert (ASSETS/'private/worlds.jsonl').read_bytes()==(''.join(canon(w)+'\n' for w in worlds)).encode()
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True);rng=random.Random(100402);maximum=0;cases=0
 for w in worlds:
  allowed={tuple(r['sequence']) for r in w['legal_probes']};reserved={tuple(p) for p in w['reserved']};assert len(allowed)==82 and len(reserved)==2 and allowed|reserved==set(PROBES)
  assert all(not any(p[:len(q)]==q for p in allowed) for q in reserved)
  ports={k:w[k] for k in ['actuators','sensors']};reset=dict.fromkeys(w['sensors'],0)
  legal=[dict(id=r['id'],sequence=[w['actuators'][a] for a in r['sequence']]) for r in w['legal_probes']];grammar=LegalChoiceTrie(tok,[r['id'] for r in legal])
  for _ in range(40):
   selected=rng.sample(legal,5);ledger=[dict(experiment=i+1,probe_id=r['id'],probe=r['sequence'],observations=[dict.fromkeys(w['sensors'],(i+j)%2) for j in range(len(r['sequence']))]) for i,r in enumerate(selected)]
   for arm,mode in [('B','choice'),('D','analysis'),('T','analysis'),('D','choice'),('T','choice')]:
    msg=messages(ports,reset,ledger,mode,arm,legal=legal,analysis=synthetic_analysis(arm,ledger,legal,w['sensors']) if arm!='B' and mode=='choice' else None);tokens=len(tok.apply_chat_template(msg,tokenize=True,add_generation_prompt=True,enable_thinking=False))+(TEXT_MAX_NEW if mode=='analysis' else grammar.max_tokens);maximum=max(maximum,tokens);cases+=1;assert tokens<=CONTEXT
 for name in ['model_worker.py','interface.py','runtime.py','legal_choice.py','prediction_format.py','analysis_format.py']:
  for node in ast.walk(ast.parse((P/name).read_text())):
   names=[x.name for x in node.names] if isinstance(node,ast.Import) else [node.module or ''] if isinstance(node,ast.ImportFrom) else []
   assert not any(n.split('.')[0] in ['machines','design','information','scoring','contribution','campaign','gates','prediction_audit'] for n in names)
 save(P/'freeze-audit.json',dict(status='PASS',worlds_byte_identical_regeneration=True,all_queries_prefix_sealed=True,model_worker_import_boundary=True,complete_frontier_and_history_context_cases=cases,maximum_prompt_plus_generation=maximum,context=CONTEXT,hypothesis_catalogue_sha256=sha(catalogue()),private_worlds_sha256=filehash(ASSETS/'private/worlds.jsonl'),model_calls=0,seconds=round(time.monotonic()-start,2)));print('Deterministic world replay and context/boundary audit PASS',flush=True)
if __name__=='__main__':main()
