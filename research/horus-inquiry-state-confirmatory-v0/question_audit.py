"""Executed-evidence question accounting; prose never receives truth credit."""
from collections import Counter
from common import *
from interface import parse_frontier
from information import VersionSpace
from machines import reset_observation

def covers(executed,target):return tuple(executed[:len(target)])==tuple(target)

def measure(w,records,decisions):
 legal=w['legal_probes'];mapping={r['id']:tuple(r['sequence']) for r in legal};sensors=w['sensors'];vs=VersionSpace(reset_observation(w['root_ids']));seen_questions={};ledger=[];counts=Counter();detail=[]
 for step,d in enumerate(decisions,1):
  base=f"{w['id']}:O:discovery:{step}";raw=records['MODEL_RESPONSE',base+':analysis']['result']['text'];x=parse_frontier(raw,legal,sensors);counts['fresh_interpretation_calls']+=1
  row=dict(step=step,schema_valid=x is not None,questions=[])
  if x is None:counts['invalid_frontier_schema']+=1
  else:
   counts['valid_frontier_schema']+=1
   if x['status']=='UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION':
    counts['unresolved_status_uses']+=1
    counts['unresolved_status_with_finite_H_ambiguity']+=vs.count>1
    # H ambiguity is only finite-family corroboration, not proof of open-world limits.
    counts['unresolved_status_with_finite_H_singleton']+=vs.count==1
   for q in x['current_questions']:
    target=mapping[q['probe_id']];sensor=sensors.index(q['sensor']);key=(target,sensor);known=any(covers(p,target) for p in ledger);later=[j+1 for j,z in enumerate(decisions) if j+1>=step and covers(z['probe'],target)];counts['generated_questions']+=1;counts['questions_unobserved_at_generation']+=not known;counts['already_observed_question_targets']+=known
    parts=vs.values(target)['partition_counts_by_sensor'][sensor];ambiguous=sum(n>0 for n in parts)>1
    counts['questions_finitely_ambiguous_at_generation']+=ambiguous
    repeated=key in seen_questions and not any(covers(ledger[j],target) for j in range(seen_questions[key]-1,len(ledger)))
    counts['questions_repeated_without_new_target_evidence']+=repeated
    counts['unobserved_questions_later_answered_by_execution']+=not known and bool(later)
    aligned=covers(d['probe'],target);informative=d['realized_bits']>1e-12
    counts['questions_followed_immediately_by_target_execution']+=aligned
    counts['questions_followed_by_informative_target_execution']+=aligned and informative
    counts['questions_followed_by_any_informative_execution']+=informative
    row['questions'].append(dict(probe_id=q['probe_id'],sensor=q['sensor'],unobserved_at_generation=not known,finite_family_ambiguous=ambiguous,first_later_answer_step=later[0] if later and not known else None,repeated_without_new_target_evidence=repeated,immediate_target_execution=aligned,immediate_information_positive=informative))
    seen_questions[key]=step
  e=records['EXECUTED_PROBE',base];vs.observe(d['probe'],[[o[s] for s in sensors] for o in e['complete_observed_trace']]);ledger.append(d['probe']);detail.append(row)
 return dict(counts=counts,details=detail)
