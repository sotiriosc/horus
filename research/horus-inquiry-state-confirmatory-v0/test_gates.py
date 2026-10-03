"""Boundary and evidence-link tests without model inference."""
import copy
from common import *
from gates import decision,sign_p
from question_audit import covers
base=dict(short_exact_difference=0,paired_world_bootstrap_bit_difference_lower_97_5=-.019,repeat_ratio=.5,repeat_reduction=24,zero_information_ratio=.6,zero_information_reduction=24,median_paired_information_advantage_bits=1.,information_sign_p=.024,uncertainty_area_ratio=.85,area_sign_p=.024,mean_information_per_probe_advantage=.125)
comp={'B-A':dict(base),'O-B':dict(base)};arms={'A':{'exact_repeats':48},'B':{'zero_information':100,'experiments':384}};q=dict(generated_questions=384,questions_followed_by_informative_target_execution=320,invalid_frontier_schema=0)
assert decision(comp,arms,q)['bookkeeping']['supported'] and decision(comp,arms,q)['open_frontier']['supported']
for k,v in [('repeat_ratio',.501),('repeat_reduction',23),('zero_information_ratio',.601),('zero_information_reduction',23),('median_paired_information_advantage_bits',.99),('information_sign_p',.025),('uncertainty_area_ratio',.851),('area_sign_p',.025),('short_exact_difference',-1),('paired_world_bootstrap_bit_difference_lower_97_5',-.02)]:
 c=copy.deepcopy(comp);c['B-A'][k]=v;assert not decision(c,arms,q)['bookkeeping']['supported'],k
for k,v in [('mean_information_per_probe_advantage',.124),('median_paired_information_advantage_bits',.49),('zero_information_ratio',.801),('zero_information_reduction',11),('information_sign_p',.025),('uncertainty_area_ratio',.951),('area_sign_p',.025),('short_exact_difference',-1),('paired_world_bootstrap_bit_difference_lower_97_5',-.02)]:
 c=copy.deepcopy(comp);c['O-B'][k]=v;assert not decision(c,arms,q)['open_frontier']['supported'],k
for k,v in [('generated_questions',191),('questions_followed_by_informative_target_execution',200),('invalid_frontier_schema',1)]:
 qq=dict(q);qq[k]=v;assert not decision(comp,arms,qq)['open_frontier']['supported'],k
assert not decision(comp,arms,q,False)['bookkeeping']['supported'] and not decision(comp,arms,q,False)['open_frontier']['supported']
assert sign_p([1]*10)==1/1024 and sign_p([0]*10)==1 and sign_p([-1]*10)==1
assert covers([0,1,2],[0,1]) and not covers([1,0,2],[0,1]) and not covers([0],[0,1])
save(P/'gate-tests.json',dict(status='PASS',model_calls=0,strict_alpha_boundary=True,conjunctions_checked=True,prediction_noninferiority_boundary=True,question_coverage_boundaries=True,invalid_frontier_cannot_pass=True));print('Gate and measurement boundary tests PASS')
