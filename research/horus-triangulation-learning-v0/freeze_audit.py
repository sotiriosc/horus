"""Zero-inference deterministic world replay and model-boundary qualification."""
import ast,time,subprocess
from common import *
from design import generate
from materialize import prior_graphs
from machines import PASSIVE,PROBES,catalogue
from interface import messages
from legal_choice import LegalChoiceTrie
from prediction_format import PredictionFormat

def main():
 start=time.monotonic();worlds=[json.loads(x) for x in (ASSETS/'private/worlds.jsonl').read_text().splitlines()];forbidden,_=prior_graphs();replayed=[]
 for cohort,count,seed in [('primary',120,914071),('control',40,914072)]:
  selected,_=generate(seed,count,forbidden,control=cohort=='control')
  for i,w in enumerate(selected):
   w['id']=f'{cohort}-{i+1:03d}';w['cohort']=cohort;w['world_hash']=sha(w);replayed.append(w);forbidden.add(w['graph_sha256'])
 assert (ASSETS/'private/worlds.jsonl').read_bytes()==(''.join(canon(w)+'\n' for w in replayed)).encode()
 for w in worlds:
  allowed={tuple(r['sequence']) for r in w['legal_probes']};reserved={tuple(q) for q in w['reserved']}
  assert len(allowed)==79 and len(reserved)==5 and allowed|reserved==set(PROBES) and not allowed&reserved
  assert set(PASSIVE)<=allowed and all(not any(p[:len(q)]==q for p in allowed) for q in reserved)
  assert len({r['id'] for r in w['legal_probes']})==79
 # Model worker and message constructor cannot import the hidden world/evaluator.
 for name in ['model_worker.py','interface.py','runtime.py','legal_choice.py','prediction_format.py']:
  tree=ast.parse((P/name).read_text())
  for node in ast.walk(tree):
   if isinstance(node,ast.Import):names=[x.name for x in node.names]
   elif isinstance(node,ast.ImportFrom):names=[node.module or '']
   else:continue
   assert not any(n.split('.')[0] in {'machines','information','design','materialize','contribution','scoring','campaign'} for n in names),(name,names)
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0/231c69a380487f6c0e52d02dcf0d5456d1918201',local_files_only=True)
 snippets=[' uncertainty'*600,'界'*600,'"'*1600,'\\'*1600,'\n'*1600,'{}[]"\\'*600,'🙂'*600]
 hypotheses=[tok.decode(tok.encode(x,add_special_tokens=False)[:512],skip_special_tokens=True) for x in snippets]
 maxima={};fixtures=0
 for w in worlds:
  ports={k:w[k] for k in ['actuators','sensors']};reset=dict.fromkeys(w['sensors'],0);target=dict.fromkeys(w['sensors'],1)
  legal=[dict(id=r['id'],sequence=[w['actuators'][a] for a in r['sequence']]) for r in w['legal_probes']]
  ledger=[dict(experiment=i+1,probe_id=r['id'],probe=r['sequence'],observations=[dict.fromkeys(w['sensors'],j%2) for j in range(3)]) for i,r in enumerate([r for r in legal if len(r['sequence'])==3][:12])]
  cases=[]
  for h in hypotheses:
   cases.append(('analysis',messages(ports,reset,ledger[:11],'analysis',legal=legal,previous_analysis=h,target=target),512))
   cases.append(('T-choice',messages(ports,reset,ledger[:11],'choice',legal=legal,analysis=h,target=target),LegalChoiceTrie(tok,[r['id'] for r in legal]).max_tokens))
  cases.append(('A-choice',messages(ports,reset,ledger[:11],'choice',legal=legal,target=target),LegalChoiceTrie(tok,[r['id'] for r in legal]).max_tokens))
  for n in (3,4,5,6):cases.append(('prediction',messages(ports,reset,ledger,'prediction',query=[w['actuators'][0]]*n,target=target),PredictionFormat(tok,w['sensors'],n).max_tokens))
  for label,msgs,new in cases:
   length=len(tok.apply_chat_template(msgs,tokenize=True,add_generation_prompt=True,enable_thinking=False));fixtures+=1
   maxima[label]=max(maxima.get(label,0),length+new)
   assert length+new<=4096,(label,length,new)
 save(P/'freeze-audit.json',dict(status='PASS',scientific_model_calls=0,worlds=160,worlds_byte_identical_deterministic_regeneration=True,private_worlds_sha256=filehash(ASSETS/'private/worlds.jsonl'),hypothesis_catalogue_sha256=sha(catalogue()),all_reservations_prefix_sealed=True,all_passive_schedules_legal=True,all_model_catalogues_exactly_79=True,model_worker_import_boundary=True,full_ledger_context_fixtures=fixtures,maximum_prompt_plus_generation_by_mode=maxima,context=4096,stress_cases='Synthetic maximum-length ledgers for every public port catalogue, 512-token ASCII, CJK, emoji, quote, slash, newline and punctuation hypotheses; exact unescaped transport.',seconds=round(time.monotonic()-start,2)))
 print('World replay, model boundary and full-ledger context audit PASS',flush=True)
if __name__=='__main__':main()
