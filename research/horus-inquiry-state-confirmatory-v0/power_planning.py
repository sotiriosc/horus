"""Prospective effect planning from the completed pilot; no new model calls."""
import math,time
import numpy as np
from common import *

def sign_p(wins,losses):
 n=wins+losses
 return sum(math.comb(n,k) for k in range(wins,n+1))/2**n if n else 1.

def main():
 path=Path('/mnt/d/horus-research-assets/inquiry-state-pilot-v0/private/score-first/per-world-results.private.json');r=json.loads(path.read_text());rows=r['rows'];rng=np.random.default_rng(100305);N=20000;idx=rng.integers(0,16,(N,48));out={}
 info=np.array([b['information']-a['information'] for a,b in zip(rows['A'],rows['B'])]);bit=np.array([(b['short_correct_bits']-a['short_correct_bits'])/24 for a,b in zip(rows['A'],rows['B'])]);exact=np.array([(b['short_exact']-a['short_exact'])/2 for a,b in zip(rows['A'],rows['B'])])
 # Use every recorded decision, including step5; append flat steps7/8.
 area={}
 for arm in ['A','B']:
  area[arm]=np.array([np.trapezoid([row['curves']['0']['bits']]+[math.log2(d['post_H']) for d in row['decisions']]+[row['final_bits']]*2)/8 for row in rows[arm]])
 for retained in [1.,.5,.25]:
  di=info*retained;da=(area['A']-area['B'])*retained;z=di[idx];az=da[idx]
  wins=(z>1e-12).sum(1);loss=(z< -1e-12).sum(1);ap=np.array([sign_p(int(w),int(l)) for w,l in zip((az>1e-12).sum(1),(az< -1e-12).sum(1))]);ip=np.array([sign_p(int(w),int(l)) for w,l in zip(wins,loss)])
  arearatio=1-az.mean(1)/area['A'][idx].mean(1)
  repeatA=np.array([v['repeats'] for v in rows['A']])[idx].sum(1);repeatB=repeatA*(1-retained)
  # Added probes7/8 yield zero information in both arms: conservative dilution.
  zeroA=np.array([v['zero_information']+2 for v in rows['A']])[idx].sum(1);zeroB=zeroA-retained*np.array([a['zero_information']-b['zero_information'] for a,b in zip(rows['A'],rows['B'])])[idx].sum(1)
  conditions=dict(repeats=(repeatA>=24)&(repeatB<=.5*repeatA)&(repeatA-repeatB>=24),zero=(zeroB<=.6*zeroA)&(zeroA-zeroB>=24),information=(np.median(z,axis=1)>=1)&(ip<.025),area=(arearatio<=.85)&(ap<.025),prediction_exact_nonnegative=((exact*retained)[idx].mean(1)>=0),prediction_bit_noninferiority_normal_approx=((bit*retained)[idx].mean(1)-1.96*(bit*retained)[idx].std(1,ddof=1)/48**.5>-.02))
  out[str(retained)]=dict(component_pass_frequency={k:float(v.mean()) for k,v in conditions.items()},joint_pass_frequency=float(np.logical_and.reduce(list(conditions.values())).mean()))
 save(P/'power-planning.json',dict(status='PASS',scientific_model_calls=0,pilot_publication=BASE_SHA,pilot_numeric_source_sha256=filehash(path),seed=100305,resamples=N,planned_worlds=48,pilot_worlds=16,pilot_median_paired_information_bits=float(np.median(info)),scenarios=out,limitations=['Empirical pilot resampling is optimistic about population generalization; this is planning, not a new significance result.','Assume no additional information and two zero-information selections in either arm on probes7/8; no invented extrapolation benefit.','Prediction exact rate and bit effects are carried from two to three queries only as rates; additional queries are not treated as independent worlds.','Planning bit interval is a normal approximation; the frozen outcome gate uses a paired world bootstrap interval.','No O pilot exists. No claimed O power; O comparison can be underpowered.','Effects shrunk by50% and75% for sensitivity; no threshold chosen from scientific confirmatory outcomes.']))
 print(canon(out),flush=True)
if __name__=='__main__':main()
