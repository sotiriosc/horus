"""Prospective sensitivity calculations, without scientific model outcomes."""
import math,itertools
from statistics import NormalDist
from common import *
from study_stats import paired_signflip,paired_sign,mcnemar,holm

def main():
 assert paired_signflip([1]*7)['p']==1/128
 assert paired_signflip([1,-1])['p']==.75
 assert paired_signflip([0]*120)['p']==1
 assert holm({'P':.004,'A':.009})=={'P':.008,'A':.009}
 # Exact distribution cross-check by explicit enumeration, including ties.
 ds=[-2,1,0,3,-1];observed=sum(ds)
 brute=sum(sum(s*d for s,d in zip(signs,ds))>=observed for signs in itertools.product((-1,1),repeat=len(ds)))/2**len(ds)
 assert paired_signflip(ds)['p']==brute
 norm=NormalDist();rows=[]
 for effect in [.08,.10,.12,.15]:
  for rho in [0.,.2,.5]:
   variance=(.30-effect**2)/5*(1+4*rho)
   noncentral=math.sqrt(120)*effect/math.sqrt(variance)
   rows.append(dict(true_accuracy_gain=effect,endpoint_discordance=.30,within_machine_difference_correlation=rho,approximate_power_at_worst_holm_alpha_005=norm.cdf(noncentral-norm.inv_cdf(.995))))
 control=[]
 for win,loss in [(.25,.05),(.35,.05),(.40,.10)]:
  power=0.
  for w in range(41):
   for l in range(41-w):
    n=w+l
    p=min(1.,2*sum(math.comb(n,i) for i in range(max(w,l),n+1))/2**n) if n else 1.
    if w-l>=6 and p<.025:
     power+=math.comb(40,w)*math.comb(40-w,l)*win**w*loss**l*(1-win-loss)**(40-w-l)
  control.append(dict(T_only_probability=win,comparator_only_probability=loss,exact_pairwise_success_component_power_at_worst_holm_alpha_025=power))
 save(P/'power-planning.json',dict(status='PROSPECTIVE_NO_MODEL_DATA',primary_worlds=120,endpoints_per_world=5,method='Normal approximation for prediction significance sensitivity; exact multinomial integration for control success component. Not power guarantees for the conjunction of all gates.',prediction_scenarios=rows,control_scenarios=control,decision='Retain suggested 120/40 counts. Strong effects are detectable; small effects and highly correlated outcomes have materially lower power. Do not change counts or gates after scientific execution.',exact_test_implementation_checks='PASS'))
 print('Prospective power sensitivity and independent exact-test checks saved.')
if __name__=='__main__':main()
