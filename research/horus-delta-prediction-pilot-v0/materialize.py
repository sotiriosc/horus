"""Fixed scientific selection from precommitted admission rules."""
import subprocess
from common import *
from machines import catalogue
from design import generate,prior_graphs

def main():
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for name in ['prospective-registration.json','design.py','machines.py','information.py','interface.py']:
  assert subprocess.check_output(['git','show',head+':research/horus-delta-prediction-pilot-v0/'+name],cwd=ROOT)==(P/name).read_bytes(),name
 path=ASSETS/'private/worlds.jsonl';assert not path.exists();forbidden=prior_graphs();forbidden.update(json.loads((P/'design-engineering.json').read_text())['world_graph_hashes'])
 worlds,stats=generate(100403,16,forbidden)
 for i,w in enumerate(worlds):w['id']=f'delta-{i+1:03d}';w['world_hash']=sha(w)
 path.write_text(''.join(canon(w)+'\n' for w in worlds));path.chmod(0o600)
 save(P/'world-manifest.json',dict(private_worlds_sha256=filehash(path),worlds=[{k:w[k] for k in ['id','world_hash','graph_sha256']} for w in worlds]))
 save(P/'world-qualification.json',dict(status='PASS',selection_rules_commit=head,private_worlds_sha256=filehash(path),hypothesis_catalogue_sha256=sha(catalogue()),root_types=len(catalogue()),all_worlds_direct_modifier_temporal=True,all_reserved_oracle_identifiable=True,minimum_oracle_positive_information_steps=min(w['qualification']['oracle_positive_information_steps'] for w in worlds),minimum_oracle_information_bits=min(w['qualification']['oracle_bits'] for w in worlds),legal_probes=82,reserved_queries=2,no_prior_or_engineering_graph_overlap=True,scientific_model_calls=0,**stats));print(canon(stats),flush=True)
if __name__=='__main__':main()
