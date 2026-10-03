"""Every screening condition is mandatory; no preference for Triangulation."""
import copy
from common import *
from gates import decision
base=dict(mean_information_per_probe_advantage=.25,median_paired_information_advantage_bits=1,information_wins=10,useful_contrast_mean_advantage=.5,zero_information_reduction=0,short_exact_difference=-1,short_bit_accuracy_difference=-.02)
comp={n:dict(base) for n in ['D-B','T-B','T-D']};m=dict(mean_matched_baseline_information_advantage_when_testing=.25,prediction_testing_experiments=16,prediction_testing_worlds=8,valid_analysis_fraction=.9,counts=dict(valid_evidence_linked_comparisons=12));mechanism={a:copy.deepcopy(m) for a in ['D','T']}
assert decision(comp,mechanism)['recommended_arm']=='T'
for k,v in [('mean_information_per_probe_advantage',.249),('median_paired_information_advantage_bits',.99),('information_wins',9),('useful_contrast_mean_advantage',.49),('zero_information_reduction',-1),('short_exact_difference',-2),('short_bit_accuracy_difference',-.021)]:
 c=copy.deepcopy(comp);c['D-B'][k]=v;assert not decision(c,mechanism)['screening']['D-B']['passed'],k
for k,v in [('mean_matched_baseline_information_advantage_when_testing',.249),('prediction_testing_experiments',15),('prediction_testing_worlds',7),('valid_analysis_fraction',.899)]:
 q=copy.deepcopy(mechanism);q['D'][k]=v;assert not decision(comp,q)['screening']['D-B']['passed'],k
q=copy.deepcopy(mechanism);q['D']['counts']['valid_evidence_linked_comparisons']=11;assert not decision(comp,q)['screening']['D-B']['passed']
c=copy.deepcopy(comp);c['T-D']['information_wins']=9;assert decision(c,mechanism)['recommended_arm']=='D'
c['D-B']['information_wins']=9;assert decision(c,mechanism)['recommended_arm'] is None
assert decision(comp,mechanism,False)['recommended_arm'] is None
save(P/'gate-tests.json',dict(status='PASS',model_calls=0,each_screening_threshold_checked=True,mechanism_coverage_required=True,D_preferred_when_T_increment_fails=True,T_requires_actual_increment=True,integrity_required=True));print('Literal screening gate tests PASS')
