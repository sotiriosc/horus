"""Read-only authenticated replay and preregistered eligible-prefix accounting."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import expected_escape,qualifies
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import SOURCE
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import analyze as prior
from .worker import OPPORTUNITY,CONTROLS,ORDER,SETUPS

CASES=OPPORTUNITY|CONTROLS

def insist(ok,what):
    if not ok:raise RuntimeError('INVALID: '+what)

def audit_case(root,case):
    if case not in CASES:raise ValueError('unregistered case')
    prior.CASES[case]=CASES[case]
    arms={a:prior.audit_arm(root,case,a) for a in ('I','S')}
    I=arms['I'];S=arms['S'];pairs=[];shared=0;inactive=0;independent=0
    expected_setup=len(SETUPS[case][1])
    for arm,record in arms.items():
        setups=[e for e in record['events'] if e['record']['execution_kind']=='REGISTERED_SETUP']
        insist(len(setups)==expected_setup,f'{case}/{arm} setup cardinality')
    for j,(ip,sp) in enumerate(zip(I['proofs'],S['proofs'])):
        p=json.loads((root/'pairs'/case/f'{j+1:02d}.json').read_text())
        signed_i={k:v for k,v in ip.items() if k!='recorded_at'}
        signed_s={k:v for k,v in sp.items() if k!='recorded_at'}
        insist(signed_i==signed_s and all(p[k]==v for k,v in signed_i.items()),
               f'{case} signed pairing proof {j+1}')
        i=I['decisions'][j];s=S['decisions'][j]
        matched=(i['state']==s['state'] and
            prior.history_projection(I['events'][:i['event_stream_sequence']-1])==
            prior.history_projection(S['events'][:s['event_stream_sequence']-1]) and
            ip['I_semantic_projection_sha256']==ip['S_semantic_projection_sha256'] and
            i['admissible_actions']==s['admissible_actions'])
        expected,_=expected_escape(S['decisions'][:j],s['state'],s['grounded_assessments_before'])
        insist(p['matched_context']==matched and p['S_trigger']==(expected is not None),
               f'{case} matched/trigger proof {j+1}')
        if matched and expected is None:
            inactive+=1
            insist(i['selected_action']==s['selected_action'],f'{case} inactive action mismatch {j+1}')
            insist(i['realized']==s['realized'],f'{case} matched-world consequence mismatch {j+1}')
            if i['policy_route']=='MODEL':
                shared+=1
                refs=[r for r in S['references'] if r['decision_id']==s['decision_id']]
                insist(p['shared_draw'] and len(refs)==1 and i['action_call_id'] is not None and
                       s['action_call_id'] is None and
                       p['I_raw_provenance_sha256']!=p['S_raw_provenance_sha256'] and
                       p['I_semantic_projection_sha256']==p['S_semantic_projection_sha256'] and
                       p['shared_request_sha256']==p['I_request_sha256']==p['S_request_sha256'] and
                       p['shared_response_sha256'] is not None,
                       f'{case} shared draw cardinality {j+1}')
            else:
                insist(not p['shared_draw'] and i['action_call_id'] is None and s['action_call_id'] is None,
                       f'{case} matched mechanical choice {j+1}')
        else:
            insist(not p['shared_draw'],f'{case} shared across trigger/divergence {j+1}')
            if not matched:independent+=sum(d['action_call_id'] is not None for d in (i,s))
        if expected is not None and matched:
            insist(i['policy_route']=='MODEL' and i['action_call_id'] is not None and
                   s['decision_source']==SOURCE and s['action_call_id'] is None,
                   f'{case} incumbent/escape trigger boundary {j+1}')
        pairs.append(p)
    streak=0;maximum=0;last=None
    for d in S['decisions']:
        key=(d['state'],d['selected_action'])
        streak=(streak+1 if key==last else 1) if qualifies(d) else 0
        last=key if streak else None;maximum=max(maximum,streak)
    escapes=[]
    for d in S['decisions']:
        if d['decision_source']!=SOURCE:continue
        j=d['index']-1;later=S['decisions'][j+1:];other=I['decisions'][j]
        relation=(d['state'],d['selected_action'])
        later_use=[x['index'] for x in later if
                   (x['state'],x['selected_action'])==relation and
                   x['selected_grounded_before']['kind']!='UNSEEN']
        observed_behavior_difference=[x['index'] for x in later if
            (x['state'],x['selected_action'])==relation and
            I['decisions'][x['index']-1]['state']==x['state'] and
            I['decisions'][x['index']-1]['selected_action']!=x['selected_action']]
        first_before=d['selected_grounded_before']['kind']=='UNSEEN'
        acquired=d['grounded_after']['kind']!='UNSEEN'
        escapes.append(dict(decision_index=d['index'],matched_prefix=pairs[j]['matched_context'],
            prior_qualifying_suffix=d['counter_before'],relation=f'{relation[0]}:{relation[1]}',
            first_unseen_before=first_before,grounded_after_kind=d['grounded_after']['kind'],
            first_authenticated_receipt_sha256=d['receipt_provenance_sha256'],
            I_ordinary_action=other['selected_action'],I_action_call_id=other['action_call_id'],
            S_action_model_calls=0 if d['action_call_id'] is None else 1,
            immediate_consequence=d['realized']['consequence'],
            remaining_S_consequences=[x['realized']['consequence'] for x in later],
            later_grounded_relation_selections=later_use,
            observed_later_I_S_action_difference_on_relation=observed_behavior_difference,
            endpoint_pass=bool(pairs[j]['matched_context'] and d['counter_before']==3 and
                first_before and acquired and other['policy_route']=='MODEL' and
                d['action_call_id'] is None and maximum<=3)))
    first=escapes[0] if escapes else None
    eligible=bool(case in OPPORTUNITY and first and first['matched_prefix'] and
                  first['prior_qualifying_suffix']==3)
    reasons=[]
    if case in OPPORTUNITY and not eligible:
        ds=S['decisions']
        if any(d['decision_source']=='MODEL_FOR_UNSEEN' for d in ds):
            reasons.append('MODEL_NATURALLY_EXPLORED_UNSEEN')
        if any(d['realized']['next_state']!=d['state'] for d in ds):
            reasons.append('STATE_CHANGED')
        if any(d['grounded_after']['kind']=='ESTABLISHED' and
               d['realized']['consequence']==1 for d in ds):
            reasons.append('ESTABLISHED_PLUS_ONE')
        if any(d['counter_before']>0 and d['selected_action']!=ds[j-1]['selected_action']
               for j,d in enumerate(ds) if j):reasons.append('FALLBACK_IDENTITY_CHANGED')
        if not reasons:reasons.append('NO_THREE_CONSECUTIVE_QUALIFYING_COMPLETIONS_WITH_UNSEEN_ALTERNATIVE')
    pause=root/'cases'/case/'pause.json';restart=root/'cases'/case/'restart-verdict.json'
    restart_data=json.loads(restart.read_text()) if restart.exists() else None
    restart_pass=bool(restart_data and restart_data['status']=='PASS' and
                      restart_data['post_restart_reconstructed_suffix']['I']['count']==2 and
                      restart_data['post_restart_reconstructed_suffix']['S']['count']==2)
    if case in OPPORTUNITY:
        insist(pause.exists()==restart.exists(),f'{case} incomplete restart lifecycle')
    result=dict(case=case,kind='OPPORTUNITY' if case in OPPORTUNITY else 'CONTROL',
        horizon=CASES[case],prefix_status=('ELIGIBLE' if eligible else 'PREFIX_INELIGIBLE')
            if case in OPPORTUNITY else 'NO_TRIGGER_CONTROL',
        eligibility_reasons=reasons,eligible_prefix=eligible,
        candidate_first_endpoint_pass=first['endpoint_pass'] if first else None,
        first_escape_decision=first['decision_index'] if first else None,
        escape_records=escapes,maximum_qualifying_streak=maximum,
        matched_inactive_decisions=inactive,shared_model_draws=shared,
        independent_post_divergence_calls=independent,
        false_triggers=len(escapes) if case in CONTROLS else 0,
        restart_status=('PASS' if restart_pass else 'NO_RESTART_OPPORTUNITY' if not pause.exists() else 'FAIL')
            if case in OPPORTUNITY else 'NOT_APPLICABLE',
        total_consequence=dict(I=sum(d['realized']['consequence'] for d in I['decisions']),
                               S=sum(d['realized']['consequence'] for d in S['decisions'])),
        model_calls=dict(I=len(I['intents']),S=len(S['intents'])),
        physical_attempts=dict(I=len(I['attempts']),S=len(S['attempts'])),
        receipt_hashes=dict(I=[d['receipt_provenance_sha256'] for d in I['decisions']],
                            S=[d['receipt_provenance_sha256'] for d in S['decisions']]))
    return result,dict(arms=arms,pairs=pairs,restart=restart_data)

def analyze(root):
    stop=json.loads((root/'campaign-stop.json').read_text())
    generated=stop['generated_cases']
    insist(len(generated)<=12 and generated[:4]==list(CONTROLS) and
           generated==list(ORDER[:len(generated)]),'generated case order/ceiling')
    cases={};private={}
    for case in generated:cases[case],private[case]=audit_case(root,case)
    eligible=[c for c in generated if cases[c]['eligible_prefix']]
    insist(len(eligible)<=4 and stop['eligible_cases']==eligible,'registered early-stop count')
    if len(eligible)==4:insist(generated[-1]==eligible[-1],'did not stop after fourth eligible case')
    else:insist(len(generated)==12,'stopped before case ceiling without target')
    false=sum(cases[c]['false_triggers'] for c in CONTROLS)
    endpoint_failure=[c for c in eligible if not cases[c]['candidate_first_endpoint_pass']]
    max_streak=max(x['maximum_qualifying_streak'] for x in cases.values())
    restart_eligible=[c for c in eligible if cases[c]['restart_status']=='PASS']
    inactive=sum(x['matched_inactive_decisions'] for x in cases.values())
    shared=sum(x['shared_model_draws'] for x in cases.values())
    # Negative acquisition is secondary; a new material policy failure is a
    # grounded negative action chosen despite a superior established candidate.
    material_cost=[]
    for c in generated:
        if c not in OPPORTUNITY:continue
        for d in private[c]['arms']['S']['decisions']:
            if d['known_negative_with_better_established']:
                material_cost.append(dict(case=c,decision=d['index']))
    if false or endpoint_failure or max_streak>3 or material_cost:
        recommendation='RETAIN_INCUMBENT'
    elif len(eligible)<4 or not restart_eligible or inactive==0 or shared==0:
        recommendation='MORE_EVIDENCE_REQUIRED'
    else:recommendation='PROMOTE_S'
    report=dict(campaign_status='VALID',classification=('ELIGIBLE_EVIDENCE_INCOMPLETE'
        if len(eligible)<4 else 'FOUR_NEW_ELIGIBLE_PREFIXES_OBTAINED'),
        recommendation=recommendation,
        prior_controlled_pairing_recommendation='MORE_EVIDENCE_REQUIRED',
        prior_phase4_classification='STAGNATION_ESCAPE_SUPPORTED',
        prior_action_model_audit='ACTION_MODEL_STOCHASTIC_AS_CONFIGURED',
        generated_cases=generated,eligible_cases=eligible,eligible_prefix_count=len(eligible),
        prefix_ineligible_cases=[c for c in generated if c in OPPORTUNITY and not cases[c]['eligible_prefix']],
        controls_completed=list(CONTROLS),false_triggers=false,
        eligible_first_endpoint_failures=endpoint_failure,eligible_restart_passes=restart_eligible,
        maximum_qualifying_streak=max_streak,material_new_cost_flags=material_cost,
        matched_inactive_decisions=inactive,shared_model_draws=shared,
        independent_post_divergence_model_calls=sum(x['independent_post_divergence_calls'] for x in cases.values()),
        physical_model_attempts=sum(sum(x['physical_attempts'].values()) for x in cases.values()),
        per_case=cases)
    _atomic_write(root/'analysis.private.json',dict(report=report,private_replay=private))
    _atomic_write(root/'analysis.public.json',report)
    return report

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    print(json.dumps(analyze(p.parse_args().private_root),sort_keys=True))
