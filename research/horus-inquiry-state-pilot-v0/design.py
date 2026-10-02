"""Prospective small-world admission; no model behavior or outputs."""
import random,time
from common import *
from machines import *
from information import VersionSpace

def prior_graphs():
 from pathlib import Path
 old=Path('/mnt/d/horus-research-assets/causal-machine-v0/private/worlds.jsonl')
 result={dsl.program_signature(w['program']['roots']) for w in map(json.loads,old.read_text().splitlines())}
 for study in ['active-causal-experimentation-v0','triangulation-learning-v0']:
  path=Path('/mnt/d/horus-research-assets')/study/'private/worlds.jsonl'
  result.update(w['graph_sha256'] for w in map(json.loads,path.read_text().splitlines()))
  engineering=Path('/mnt/d/horus-research-assets')/study/'engineering/design-worlds.json'
  if engineering.exists():result.update(w['graph_sha256'] for w in json.loads(engineering.read_text()))
 return result

def qualifications(ids,reserved):
 reset=reset_observation(ids);single=[outcomes(ids,(a,))[-1] for a in range(4)]
 direct=any(single[a][s]!=reset[s] for a in range(4) for s in range(4))
 modifier=any(outcomes(ids,(a,b))[-1][s]-single[a][s] != single[b][s]-reset[s] for a in range(4) for b in range(4) if a!=b for s in range(4))
 order=any(outcomes(ids,(a,b))[-1]!=outcomes(ids,(b,a))[-1] for a in range(4) for b in range(a+1,4))
 repetition=any(outcomes(ids,(a,a,a))[0]!=outcomes(ids,(a,a,a))[-1] for a in range(4))
 if not(direct and modifier and (order or repetition)):return None
 traces=[outcomes(ids,p) for p in reserved]
 if any(all(row==t[0] for row in t) for t in traces) or traces[0]==traces[1]:return None
 allowed=tuple(p for p in PROBES if p not in reserved);vs=VersionSpace(reset);initial=vs.bits;positive=0;schedule=[]
 for _ in range(6):
  p=max(allowed,key=lambda p:vs.values(p)['information_gain']);before=vs.bits;vs.observe(p,outcomes(ids,p));positive+=before-vs.bits>1e-12;schedule.append(p)
 if positive<5 or initial-vs.bits<8 or not vs.identifies(reserved):return None
 return dict(direct_reset_effect=True,context_modifier_distinction=True,order_distinction=order,history_sensitive_repetition=repetition,oracle_positive_information_steps=positive,oracle_bits=initial-vs.bits,oracle_final_H=vs.count,oracle_identifies_reserved=True,oracle_schedule=schedule)

def generate(seed,count,forbidden=()):
 rng=random.Random(seed);roots=catalogue();groups={g:[i for i,r in enumerate(roots) if g in r['groups']] for g in ['direct','interaction','delay','latch','repetition']}
 temporal=sorted(set(groups['delay']+groups['latch']));seen=set(forbidden);accepted=[];start=time.monotonic()
 for candidate in range(50000):
  ids=[rng.choice(groups['direct']),rng.choice(groups['interaction']),rng.choice(temporal),rng.choice(groups['repetition'])];rng.shuffle(ids)
  patterns=[PATTERNS[candidate%5],PATTERNS[(candidate+2)%5]]
  reserved=tuple(rng.choice([p for p in PROBES if len(p)==3 and pattern(p)==pat]) for pat in patterns)
  q=qualifications(ids,reserved)
  if q is None:continue
  graph=graph_hash(ids)
  if graph in seen:continue
  seen.add(graph);names=rng.sample([f'{a}{b}' for a in 'KLMNPQRSTVWXYZ' for b in '23456789'],8)
  allowed=[p for p in PROBES if p not in reserved];rng.shuffle(allowed)
  legal=[dict(id=f'P{i:03d}',sequence=p) for i,p in enumerate(allowed)]
  accepted.append(dict(candidate_index=candidate,root_ids=ids,reserved=reserved,actuators=names[:4],sensors=names[4:],legal_probes=legal,graph_sha256=graph,qualification=q))
  if len(accepted)==count:return accepted,dict(seed=seed,candidates_considered=candidate+1,accepted=count,seconds=round(time.monotonic()-start,2))
 raise RuntimeError('Fixed candidate cap exhausted; stop before inference')
if __name__=='__main__':
 w,stats=generate(100201,4,prior_graphs());save(ASSETS/'engineering/design-worlds.json',w);save(P/'design-engineering.json',dict(status='PASS',root_types=len(catalogue()),scientific_model_calls=0,world_graph_hashes=[x['graph_sha256'] for x in w],**stats));print(canon(stats))
