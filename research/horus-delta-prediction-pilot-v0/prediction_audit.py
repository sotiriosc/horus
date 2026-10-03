"""Post-raw prediction receipt scoring from executed evidence only."""
from collections import Counter
from common import *
from interface import parse_analysis

def kinds(a,b):
 if b is None:return {'single_observation'}
 a,b=tuple(a),tuple(b);short,long=sorted([a,b],key=len);out=set()
 if len(long)==len(short)+1 and (long[:-1]==short or long[1:]==short):out.add('one_step_extension')
 if len(a)==len(b) and a!=b:
  for i in range(len(a)-1):
   x=list(a);x[i],x[i+1]=x[i+1],x[i]
   if tuple(x)==b:out.add('adjacent_swap')
 return out or {'other'}

def compare_trace(predicted,actual):
 assert len(predicted)==len(actual)
 matches=sum(a==b for x,y in zip(predicted,actual) for a,b in zip(x,y));total=4*len(actual)
 return ('supported' if matches==total else 'contradicted' if matches==0 else 'partially_matched'),matches,total

def measure(w,arm,records,decisions,baseline_decisions):
 legal=w['legal_probes'];mapping={r['id']:r['sequence'] for r in legal};sensors=w['sensors'];ledger=[];counts=Counter();details=[];tested_info=[];ignored_info=[];no_proposal_info=[];matched_adv=[];proposals=[]
 def bits(e):return [''.join(str(row[s]) for s in sensors) for row in e['complete_observed_trace']]
 all_exec=[records['EXECUTED_PROBE',f"{w['id']}:{arm}:discovery:{step}"] for step in range(1,7)]
 for step,(e,d) in enumerate(zip(all_exec,decisions),1):
  if step>1:
   base=f"{w['id']}:{arm}:discovery:{step}";analysis=parse_analysis(records['MODEL_RESPONSE',base+':analysis']['result']['text'],arm,ledger,legal,sensors);counts['analysis_calls']+=1;row=dict(step=step,schema_valid=analysis is not None)
   if analysis is None:counts['invalid_analyses']+=1;no_proposal_info.append(d['realized_bits'])
   else:
    counts['valid_analyses']+=1
    if analysis['status']=='INSUFFICIENT_DELTA':
     counts['insufficient_delta']+=1
     available=False
     for i,a in enumerate(ledger):
      for b in ledger[:i]:
       if kinds(a['probe'],b['probe'])!={'other'} and a['observations'][-1]!=b['observations'][-1]:available=True
     counts['insufficient_with_no_controlled_endpoint_delta']+=not available;counts['insufficient_despite_available_controlled_endpoint_delta']+=available;no_proposal_info.append(d['realized_bits'])
    else:
     counts['predictions_generated']+=1;source={x['probe_id']:x for x in ledger};a=source[analysis['evidence_A']];b=source.get(analysis['evidence_B']);expectedA=''.join(str(a['observations'][-1][s]) for s in sensors);expectedB=''.join(str(b['observations'][-1][s]) for s in sensors) if b else 'NONE'
     faithful=analysis['observed_endpoint_A']==expectedA and analysis['observed_endpoint_B']==expectedB;input_valid=analysis['comparison_kind'] in kinds(a['probe'],b['probe'] if b else None);counts['endpoint_claims_match_executed_evidence']+=faithful;counts['input_comparison_labels_valid']+=input_valid
     valid_pair=b is not None and input_valid and faithful;counts['valid_evidence_linked_comparisons']+=valid_pair
     changed=b is not None and expectedA!=expectedB;controlled=b is not None and bool(kinds(a['probe'],b['probe'])&{'one_step_extension','adjacent_swap'})
     counts['valid_controlled_observed_endpoint_deltas']+=valid_pair and changed and controlled
     target=analysis['prediction']['untested_probe_id'];pred=analysis['prediction']['predicted_trace'];later=[j for j,z in enumerate(all_exec) if j+1>=step and z['probe_id']==target];tested_current=e['probe_id']==target
     counts['current_prediction_selected']+=tested_current
     if tested_current:
      tested_info.append(d['realized_bits']);matched_adv.append(d['realized_bits']-baseline_decisions[step-1]['realized_bits'])
     else:ignored_info.append(d['realized_bits'])
     status='never_tested';correct=total=0;first=None;alternative=False
     if later:
      first=later[0]+1;actual=bits(all_exec[later[0]]);status,correct,total=compare_trace(pred,actual);counts['predictions_eventually_tested']+=1;counts['tested_correct_bits']+=correct;counts['tested_bits']+=total;counts['predictions_with_any_bit_contradiction']+=correct<total
      if arm=='T':alternative=actual==analysis['alternative_trace'];counts['alternative_supported']+=alternative;counts['outcome_separated_primary_and_alternative']+=(actual==pred) != alternative
     counts[status]+=1
     row.update(predicted_probe=target,predicted_trace=pred,evidence_faithful=faithful,input_label_valid=input_valid,valid_pair=valid_pair,controlled_endpoint_delta=valid_pair and changed and controlled,current_prediction_selected=tested_current,status=status,first_test_step=first,correct_bits=correct,total_bits=total,alternative_supported=alternative)
     proposals.append(row)
   details.append(row)
  ledger.append(dict(experiment=step,probe_id=e['probe_id'],probe=e['selected_probe'],observations=e['complete_observed_trace']))
 for row in proposals:
  if row['first_test_step'] is not None and row['correct_bits']<row['total_bits'] and row['first_test_step']<6:
   nxt=next((r for r in proposals if r['step']==row['first_test_step']+1),None);counts['contradictions_with_subsequent_decision']+=1
   counts['subsequent_selected_probe_changed']+=all_exec[row['first_test_step']]['probe_id']!=row['predicted_probe']
   if nxt:
    counts['subsequent_prediction_available']+=1;counts['subsequent_prediction_target_or_trace_changed']+=nxt['predicted_probe']!=row['predicted_probe'] or nxt['predicted_trace']!=row['predicted_trace']
 return dict(counts=dict(counts),details=details,prediction_testing_information=tested_info,nonprediction_information=ignored_info,no_prediction_information=no_proposal_info,matched_baseline_information_advantages=matched_adv)

def aggregate(measurements):
 counts=Counter();tested=[];ignored=[];absent=[];adv=[]
 for m in measurements:counts.update(m['counts']);tested+=m['prediction_testing_information'];ignored+=m['nonprediction_information'];absent+=m['no_prediction_information'];adv+=m['matched_baseline_information_advantages']
 mean=lambda x:sum(x)/len(x) if x else None
 return dict(counts=dict(counts),prediction_testing_experiments=len(tested),prediction_testing_worlds=sum(bool(m['prediction_testing_information']) for m in measurements),nonprediction_experiments=len(ignored),no_prediction_experiments=len(absent),mean_information_without_a_prediction=mean(absent),mean_information_testing_prediction=mean(tested),mean_information_not_testing_prediction=mean(ignored),mean_matched_baseline_information_advantage_when_testing=mean(adv),valid_analysis_fraction=counts['valid_analyses']/counts['analysis_calls'] if counts['analysis_calls'] else 0,selected_current_prediction_fraction=counts['current_prediction_selected']/counts['analysis_calls'] if counts['analysis_calls'] else 0,accuracy_among_tested=counts['supported']/counts['predictions_eventually_tested'] if counts['predictions_eventually_tested'] else None,bit_accuracy_among_tested=counts['tested_correct_bits']/counts['tested_bits'] if counts['tested_bits'] else None)
