"""Independent supported/partial/contradicted/untested and adaptation fixtures."""
from common import *
from machines import outcomes
from qualify_interface import synthetic_analysis
from prediction_audit import measure,compare_trace
assert compare_trace(['0000'],['0000'])==('supported',4,4)
assert compare_trace(['0000'],['1111'])==('contradicted',0,4)
assert compare_trace(['0000'],['0001'])==('partially_matched',3,4)
w=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[0];w['id']='SYNTHETIC';legal=w['legal_probes'];sensors=w['sensors'];schedule=legal[:6]
for arm in ['D','T']:
 records={};ledger=[];ds=[];base=[]
 for step,target in enumerate(schedule,1):
  ident=f"{w['id']}:{arm}:discovery:{step}";trace=[dict(zip(sensors,row)) for row in outcomes(w['root_ids'],target['sequence'])]
  records['EXECUTED_PROBE',ident]=dict(probe_id=target['id'],selected_probe=target['sequence'],complete_observed_trace=trace)
  if step>1:
   x=json.loads(synthetic_analysis(arm,ledger,legal,sensors));proposed=legal[5] if step==5 else legal[6] if step==6 else target
   actual=[''.join(map(str,row)) for row in outcomes(w['root_ids'],proposed['sequence'])];pred=list(actual)
   if step==3:pred=[''.join(str(1-int(c)) for c in row) for row in actual]
   if step==4:pred[0]=str(1-int(pred[0][0]))+pred[0][1:]
   x['prediction'].update(untested_probe_id=proposed['id'],predicted_trace=pred)
   if arm=='T':x['alternative_trace']=[''.join(str(1-int(c)) for c in row) for row in pred]
   records['MODEL_RESPONSE',ident+':analysis']=dict(result=dict(text=canon(x)))
  ledger.append(dict(experiment=step,probe_id=target['id'],probe=target['sequence'],observations=trace));ds.append(dict(probe=target['sequence'],realized_bits=step));base.append(dict(realized_bits=0))
 r=measure(w,arm,records,ds,base);c=r['counts']
 assert [c[k] for k in ['predictions_generated','predictions_eventually_tested','supported','contradicted','partially_matched','never_tested','predictions_with_any_bit_contradiction']]==[5,4,2,1,1,1,2]
 assert c['current_prediction_selected']==3 and len(r['prediction_testing_information'])==3 and len(r['nonprediction_information'])==2
 assert c['contradictions_with_subsequent_decision']==2 and c['subsequent_selected_probe_changed']==2
 if arm=='T':assert c['alternative_supported']==1 and c['outcome_separated_primary_and_alternative']==3
save(P/'prediction-audit-tests.json',dict(status='PASS',model_calls=0,supported_partial_contradicted_never_tested=True,first_actual_execution_only=True,partial_contains_contradiction=True,alternative_discrimination=True,next_decision_changes_counted=True,testing_vs_ignoring_separated=True));print('Prediction receipt classification and adaptation tests PASS')
