"""Repeated unanswered questions never earn hypothetical resolution credit."""
from common import *
from interface import parse_frontier,messages
from qualify_interface import fixture
from question_audit import measure,covers
from machines import outcomes
w=json.loads((ASSETS/'engineering/design-worlds.json').read_text())[0];w['id']='SYNTHETIC-PERSISTENCE';ids=w['legal_probes'];chosen=ids[0];target=next(r for r in ids if not covers(chosen['sequence'],r['sequence']))
records={};ds=[]
for step in range(1,9):
 base=f"{w['id']}:O:discovery:{step}";probe=chosen['sequence'];frontier=dict(supported_so_far=[],unresolved_discrepancies=[],current_questions=[dict(question='What trace?',probe_id=target['id'],sensor=w['sensors'][0])],limits_of_current_discrimination=[],status='UNRESOLVED_BEYOND_CURRENT_DISCRIMINATION')
 records['MODEL_RESPONSE',base+':analysis']=dict(result=dict(text=canon(frontier)))
 records['EXECUTED_PROBE',base]=dict(complete_observed_trace=[dict(zip(w['sensors'],row)) for row in outcomes(w['root_ids'],probe)])
 ds.append(dict(probe=probe,realized_bits=1 if step==1 else 0))
r=measure(w,records,ds)['counts'];assert r['questions_repeated_without_new_target_evidence']==7 and r['unobserved_questions_later_answered_by_execution']==0 and r['questions_followed_by_informative_target_execution']==0
ports,reset,legal,history=fixture();assert parse_frontier('{bad',legal,ports['sensors']) is None
msg=messages(ports,reset,history[:7],'choice','O',legal=legal,interpretation='{bad');payload=json.loads(msg[1]['content']);assert payload['fresh_model_interpretation']['schema_valid'] is False
save(P/'question-boundary-tests.json',dict(status='PASS',model_calls=0,repeated_without_new_target_evidence_count=7,unexecuted_target_never_resolved=True,unrelated_informative_probe_does_not_resolve_question=True,invalid_frontier_preserved_and_marked=True));print('Question persistence and no-unexecuted-resolution checks PASS')
