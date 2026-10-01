"""Offline world qualification. Never calls A0. Never selects Active actions."""
import argparse,random,time,math
from collections import Counter
from common import *
from machines import *
from information import VersionSpace
PATTERNS=('000','001','010','011','012')
def reserve(rng):
 return tuple(rng.choice([p for p in PROBES if len(p)==3 and pattern(p)==kind and p not in PASSIVE]) for kind in PATTERNS)
def qualify(ids,reserved):
 traces=[outcomes(ids,p) for p in reserved];reset=reset_observation(ids)
 # Every full trace changes internally; all constant persistence predictors fail.
 if any(all(row==t[0] for row in t) for t in traces):return None
 if any(all(row==reset for row in t) for t in traces):return None
 # Bounds ANY actuator-independent three-position predictor, even fitted to labels.
 max_marginal=max(Counter(canon(t) for t in traces).values())/5
 if max_marginal>.30:return None
 allowed=tuple(p for p in PROBES if p not in reserved)
 passive=VersionSpace(reset)
 for p in PASSIVE:passive.observe(p,outcomes(ids,p))
 oracle=VersionSpace(reset);chosen=[]
 for t in range(12):
  p=max(allowed,key=lambda p:oracle.values(PROBES.index(p))['information_gain'])
  chosen.append(p);oracle.observe(p,outcomes(ids,p))
 if passive.bits-oracle.bits<2-1e-12:return None
 if not oracle.identifies(reserved):return None
 return dict(passive_final_count=passive.count,oracle_final_count=oracle.count,oracle_bits_advantage=passive.bits-oracle.bits,oracle_identifies_all_reserved=True,reserved_reset_persistence_exact=0,reserved_any_constant_persistence_exact=0,reserved_actuator_independent_marginal_upper_bound=max_marginal,oracle_schedule=chosen)
def generate(seed,count,forbidden=(),max_candidates=50000):
 rng=random.Random(seed);accepted=[];seen=set(forbidden);start=time.monotonic()
 for candidate in range(max_candidates):
  ids=tuple(rng.randrange(len(catalogue())) for _ in range(4));reserved=reserve(rng)
  q=qualify(ids,reserved)
  if q is None:continue
  sig=graph_hash(ids)
  if sig in seen:continue
  seen.add(sig)
  # Names independent of graph, observable ports all uniformly shuffled opaque IDs.
  names=rng.sample([f'{a}{b}' for a in 'KLMNPQRSTVWXYZ' for b in '23456789'],8)
  accepted.append(dict(candidate_index=candidate,root_ids=ids,reserved=reserved,actuators=names[:4],sensors=names[4:],graph_sha256=sig,qualification=q))
  if len(accepted)==count:return accepted,dict(seed=seed,candidates_considered=candidate+1,accepted=count,seconds=round(time.monotonic()-start,2))
 raise RuntimeError(f'Qualification exhausted fixed {max_candidates} candidates; accepted {len(accepted)}; STOP before inference')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--engineering',action='store_true');a=ap.parse_args();assert a.engineering
 worlds,stats=generate(715019,12,max_candidates=3000)
 out=ASSETS/'engineering';out.mkdir(exist_ok=True,parents=True)
 save(out/'design-worlds.json',worlds)
 save(P/'design-engineering.json',dict(status='PASS',root_types=len(catalogue()),**stats,world_graph_hashes=[w['graph_sha256'] for w in worlds],oracle_gap_bits=[w['qualification']['oracle_bits_advantage'] for w in worlds],scientific_worlds=0,model_calls=0))
 print(canon(dict(root_types=len(catalogue()),**stats)),flush=True)
