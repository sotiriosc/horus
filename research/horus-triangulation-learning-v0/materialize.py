"""Select and fix qualified scientific worlds from precommitted rules."""
import json,subprocess,time
from common import *
from machines import catalogue,dsl
from design import generate

def prior_graphs():
 old=Path('/mnt/d/horus-research-assets/causal-machine-v0/private/worlds.jsonl')
 active=Path('/mnt/d/horus-research-assets/active-causal-experimentation-v0/private/worlds.jsonl')
 previous=[json.loads(x) for x in old.read_text().splitlines()];assert len(previous)==3440
 a=[json.loads(x) for x in active.read_text().splitlines()];assert len(a)==160
 assert filehash(active)==json.loads((ACTIVE/'world-data-freeze.json').read_text())['private_worlds_sha256']
 forbidden={dsl.program_signature(w['program']['roots']) for w in previous}
 forbidden.update(w['graph_sha256'] for w in a)
 forbidden.update(json.loads((P/'design-engineering.json').read_text())['world_graph_hashes'])
 return forbidden,dict(prior_causal_worlds=len(previous),prior_active_causal_worlds=len(a),prior_causal_file_sha256=filehash(old),prior_active_file_sha256=filehash(active))

def main():
 start=time.monotonic();private=ASSETS/'private';private.mkdir(exist_ok=True);target=private/'worlds.jsonl';assert not target.exists()
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 for name in ['prospective-registration.json','design.py','machines.py','information.py']:
  committed=subprocess.check_output(['git','show',head+':research/horus-triangulation-learning-v0/'+name],cwd=ROOT)
  assert committed==(P/name).read_bytes(),'Commit rules before selection: '+name
 forbidden,prior=prior_graphs();worlds=[];stats=[]
 for cohort,count,seed in [('primary',120,914071),('control',40,914072)]:
  selected,stat=generate(seed,count,forbidden,control=cohort=='control');stat['cohort']=cohort;stats.append(stat)
  for i,w in enumerate(selected):
   w['id']=f'{cohort}-{i+1:03d}';w['cohort']=cohort;w['world_hash']=sha(w);worlds.append(w);forbidden.add(w['graph_sha256'])
 target.write_text(''.join(canon(w)+'\n' for w in worlds));target.chmod(0o600)
 save(P/'world-manifest.json',dict(private_worlds_sha256=filehash(target),worlds=[{k:w[k] for k in ['id','cohort','world_hash','graph_sha256']} for w in worlds]))
 save(P/'world-qualification.json',dict(status='PASS',selection_rules_commit=head,private_worlds_sha256=filehash(target),root_types=len(catalogue()),hypothesis_catalogue_sha256=sha(catalogue()),population_stats=stats,primary_worlds=120,control_worlds=40,short_queries_per_arm=600,long_queries_per_arm=360,legal_probes_per_world=79,reserved_short_per_world=5,reserved_long_per_world=3,all_short_and_long_queries_oracle_identifiable=True,minimum_oracle_bits_advantage=min(w['qualification']['oracle_bits_advantage'] for w in worlds),short_persistence_upper_bound=0.,short_common_trace_upper_bound=.2,long_repeat_period_le3_upper_bound=0.,long_marginal_hold_step3_upper_bound=0.,control_target_fixed_before_discovery=True,control_exactly_one_frozen_candidate_reaches_target=True,no_prior_or_interpopulation_graph_overlap=True,engineering_worlds_excluded=8,**prior,scientific_model_calls=0,seconds=round(time.monotonic()-start,2)))
 print((P/'world-qualification.json').read_text(),flush=True)
if __name__=='__main__':main()
