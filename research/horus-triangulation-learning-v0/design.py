"""Prospective offline qualification: no model responses or model outputs."""
import argparse,random,time
from collections import Counter
from common import *
from machines import *
from information import VersionSpace

def reserve(rng):return tuple(rng.choice([p for p in PROBES if len(p)==3 and pattern(p)==kind and p not in PASSIVE]) for kind in PATTERNS)
def is_aperiodic(trace):return all(any(trace[i]!=trace[i%period] for i in range(len(trace))) for period in (1,2,3))
def qualify(ids,reserved,longs):
 reset=reset_observation(ids);traces=[outcomes(ids,p) for p in reserved]
 if any(all(row==t[0] for row in t) for t in traces):return None
 if len(set(canon(t) for t in traces))!=5:return None
 for p in longs:
  t=outcomes(ids,p)
  # Defeat all repeats of a length<=3 history block and the frozen per-position
  # marginal baseline that holds its step-3 estimate on all later steps.
  if not is_aperiodic(t) or all(row==t[2] for row in t[3:]):return None
 allowed=tuple(p for p in PROBES if p not in reserved)
 passive=VersionSpace(reset)
 for p in PASSIVE:passive.observe(p,outcomes(ids,p))
 oracle=VersionSpace(reset);schedule=[]
 for _ in range(12):
  p=max(allowed,key=lambda p:oracle.values(p)['information_gain']);schedule.append(p);oracle.observe(p,outcomes(ids,p))
 if passive.bits-oracle.bits<2-1e-12:return None
 if not oracle.identifies(reserved+longs):return None
 return dict(passive_final_H=passive.count,oracle_final_H=oracle.count,oracle_bits_advantage=passive.bits-oracle.bits,oracle_identifies_all_short_and_long_queries=True,short_persistence_upper_bound=0.,short_common_trace_upper_bound=.2,long_constant_or_period_le3_persistence_upper_bound=0.,long_marginal_hold_last_position_upper_bound=0.,oracle_schedule=schedule)

def generate(seed,count,forbidden=(),max_candidates=50000,control=False):
 rng=random.Random(seed);accepted=[];seen=set(forbidden);start=time.monotonic();roots=catalogue()
 groups={g:[i for i,r in enumerate(roots) if g in r['groups']] for g in ('interaction','delay','latch','repetition')}
 for candidate in range(max_candidates):
  ids=[rng.choice(groups[g]) for g in groups];rng.shuffle(ids)
  reserved=reserve(rng);longs=tuple(tuple(rng.randrange(4) for _ in range(n)) for n in (4,5,6))
  q=qualify(ids,reserved,longs)
  if q is None:continue
  control_fields={}
  if control:
   target_rng=random.Random(914073+candidate)
   target=[target_rng.randrange(2) for _ in range(4)]
   candidates=target_rng.sample([p for p in PROBES if len(p)==3 and p not in reserved],8)
   if target==reset_observation(ids):continue
   if sum(outcomes(ids,p)[-1]==target for p in candidates)!=1:continue
   control_fields=dict(target=target,control_candidates=candidates,target_candidate_seed=914073+candidate)
  graph=graph_hash(ids)
  if graph in seen:continue
  seen.add(graph);names=rng.sample([f'{a}{b}' for a in 'KLMNPQRSTVWXYZ' for b in '23456789'],8)
  # Stable opaque ID assignment is independently shuffled per world, so neither
  # low IDs nor token ordering encode short-first or an information policy.
  allowed=[p for p in PROBES if p not in reserved];rng.shuffle(allowed)
  legal=[dict(id=f'P{i:03d}',sequence=p) for i,p in enumerate(allowed)]
  accepted.append(dict(candidate_index=candidate,root_ids=ids,reserved=reserved,long_queries=longs,actuators=names[:4],sensors=names[4:],legal_probes=legal,graph_sha256=graph,qualification=q,**control_fields))
  if len(accepted)==count:return accepted,dict(seed=seed,candidates_considered=candidate+1,accepted=count,seconds=round(time.monotonic()-start,2))
 raise RuntimeError(f'Qualification exhausted fixed candidate cap; {len(accepted)} accepted. STOP before inference.')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--engineering',action='store_true');a=ap.parse_args();assert a.engineering
 worlds,stats=generate(817031,8,max_candidates=10000);out=ASSETS/'engineering';out.mkdir(exist_ok=True,parents=True)
 save(out/'design-worlds.json',worlds)
 save(P/'design-engineering.json',dict(status='PASS',root_types=len(catalogue()),**stats,world_graph_hashes=[w['graph_sha256'] for w in worlds],oracle_gap_bits=[w['qualification']['oracle_bits_advantage'] for w in worlds],scientific_worlds=0,model_calls=0))
 print(canon(dict(root_types=len(catalogue()),**stats)),flush=True)
