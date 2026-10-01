"""Select fresh qualified worlds using precommitted rules, without A0 calls."""
import json,random,subprocess,time
from common import *
from machines import *
from design import generate

def main():
 start=time.monotonic();out=ASSETS/'private';out.mkdir(parents=True,exist_ok=True)
 target=out/'worlds.jsonl';assert not target.exists(),'Scientific worlds already fixed; never replace'
 registration=json.loads((P/'prospective-design.json').read_text())
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 committed=subprocess.check_output(['git','show',head+':research/horus-active-causal-experimentation-v0/prospective-design.json'],cwd=ROOT)
 assert committed==(P/'prospective-design.json').read_bytes(),'Selection rules must be committed first'
 forbidden=set(json.loads((P/'design-engineering.json').read_text())['world_graph_hashes'])
 old=Path('/mnt/d/horus-research-assets/causal-machine-v0/private/worlds.jsonl')
 prior=[json.loads(x) for x in old.read_text().splitlines()]
 assert len(prior)==3440
 for w in prior:forbidden.add(dsl.program_signature(w['program']['roots']))
 worlds=[];stats=[]
 for cohort,count in [('primary',120),('control',40)]:
  selected,st=generate(registration['seeds'][cohort],count,forbidden)
  st['cohort']=cohort;stats.append(st)
  for i,w in enumerate(selected):
   w['id']=f'{cohort}-{i+1:03d}';w['cohort']=cohort
   if cohort=='control':
    rng=random.Random(registration['seeds']['control_planner']+i)
    allowed=[p for p in PROBES if len(p)==3 and p not in tuple(tuple(x) for x in w['reserved'])]
    candidates=rng.sample(allowed,8)
    target_obs=next((outcomes(w['root_ids'],p)[-1] for p in candidates if outcomes(w['root_ids'],p)[-1]!=reset_observation(w['root_ids'])),None)
    assert target_obs is not None,'Fixed control target qualification failed; STOP before inference'
    w['control_candidates']=candidates;w['target']=target_obs
   w['world_hash']=sha(w);worlds.append(w);forbidden.add(w['graph_sha256'])
 target.write_text(''.join(canon(w)+'\n' for w in worlds));target.chmod(0o600)
 save(P/'world-qualification.json',dict(status='PASS',selection_rules_commit=head,private_worlds_sha256=filehash(target),population_stats=stats,primary_worlds=120,control_worlds=40,primary_queries=600,discovery_catalogue_size=79,reserved_per_world=5,reserved_pattern_counts={k:120 for k in ['000','001','010','011','012']},reserved_length_counts={'1':0,'2':0,'3':600},prefix_separation=True,passive_reservation_separation=True,all_reserved_predictions_identifiable_by_oracle=True,minimum_oracle_gap_bits=min(w['qualification']['oracle_bits_advantage'] for w in worlds),reset_persistence_upper_bound=0.,last_observation_persistence_upper_bound=0.,actuator_independent_marginal_upper_bound=.2,prior_worlds_checked=len(prior),prior_worlds_file_sha256=filehash(old),no_graph_isomorphism_overlap=True,engineering_worlds_excluded=12,scientific_model_calls=0,seconds=round(time.monotonic()-start,2)))
 save(P/'world-manifest.json',dict(worlds=[{k:w[k] for k in ['id','cohort','world_hash','graph_sha256']} for w in worlds],private_worlds_sha256=filehash(target)))
 print((P/'world-qualification.json').read_text(),flush=True)
if __name__=='__main__':main()
