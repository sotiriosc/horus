"""Independent replay of protected paired decisions; emit aggregate public-safe verdicts."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical,file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    ACTIONS,GOAL,RECENT_DECISION_LIMIT,select_route,source_for_model_choice)
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import (
    expected_escape,qualifies,independent_suffix)
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import SOURCE,PURPOSE
from .worker import ELIGIBLE,CONTROLS,semantic_assessments,request_for

CASES=ELIGIBLE|CONTROLS

def insist(condition,description):
    if not condition:raise RuntimeError('INVALID: '+description)

def provenance_hash(events,rows):
    return digest(dict(events=[dict(receipt_identity=e['record']['receipt_identity'],
        receipt_sha256=e['record']['receipt_provenance_sha256'],
        source_scope=e['record']['source_scope']) for e in events],memory_rows=rows))

def history_projection(events):
    return [dict(kind=e['record']['execution_kind'],decision_index=e['record']['decision_index'],
        pre_state=e['record']['receipt']['pre_state'],action=e['record']['receipt']['action'],
        next_state=e['record']['receipt']['next_state'],consequence=e['record']['receipt']['realized_consequence'],
        authorization_status=e['record']['authorization_status']) for e in events]

def projection(decisions,d):
    previous=decisions[:d['index']-1]
    history=[dict(decision_id=x['decision_id'],state=x['state'],action=x['selected_action'],
        authenticated_consequence=x['realized']['consequence'],source=x['decision_source'])
        for x in previous][-RECENT_DECISION_LIMIT:]
    return dict(goal=GOAL,decision_id=d['decision_id'],decision_index=d['index'],
        current_state=d['state'],available_actions=d['admissible_actions'],
        grounded_assessments=semantic_assessments(d['grounded_assessments_before']),
        recent_agent_working_context=history)

def audit_arm(root,case,arm):
    path=root/'cases'/case/arm
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store)
        rows=memory.rows();events=store.records['events'];decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        insist(len(decisions)==CASES[case],f'{case}/{arm} horizon')
        insist(len(rows)==len(events),f'{case}/{arm} event/Memory count')
        insist(not rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE'),f'{case}/{arm} self-review')
        for e in events:
            r=e['record'];receipt=r['receipt']
            insist(r['authorization_status']=='AUTHORIZED' and digest(receipt)==r['receipt_provenance_sha256'],
                   f'{case}/{arm} original authorized receipt')
            insist(r['receipt_identity']==[receipt['source_identity'],receipt['event_id'],
                   receipt['epoch'],receipt['transaction_id']],f'{case}/{arm} receipt identity')
        freezes=[x['record'] for x in store.records['calls'] if x['kind']=='ACTION_FROZEN']
        intents=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        attempts=[x['record'] for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_INTENT']
        results=[x['record'] for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_RESULT']
        references=[x['record'] for x in store.records['calls'] if x['kind']=='SHARED_MATCHED_MODEL_DRAW']
        proofs=[x['record'] for x in store.records['calls'] if x['kind']=='PAIRING_PROOF']
        insist(len(freezes)==len(decisions)==len(proofs),f'{case}/{arm} freeze/proof cardinality')
        insist(len(intents)==sum(d['action_call_id'] is not None for d in decisions),f'{case}/{arm} model call cardinality')
        insist(len(attempts)==len(results),f'{case}/{arm} physical attempt cardinality')
        for j,d in enumerate(decisions):
            seq=d['event_stream_sequence'];e=events[seq-1]['record'];r=e['receipt']
            insist(d['index']==j+1 and d['decision_id']==f'C:D{j+1:02d}' and
                   e['decision_index']==j+1 and e['execution_kind']=='AUTONOMOUS_EXECUTION' and
                   d['state']==r['pre_state'] and d['selected_action']==r['action'] and
                   d['realized']==dict(next_state=r['next_state'],consequence=r['realized_consequence']) and
                   d['receipt_identity']==e['receipt_identity'] and
                   d['receipt_provenance_sha256']==e['receipt_provenance_sha256'],f'{case}/{arm} decision/receipt {j+1}')
            for action in ACTIONS:
                insist(d['grounded_assessments_before'][action]==prior_state(rows,f"{d['state']}:{action}",seq),
                       f'{case}/{arm} grounded pre-state {j+1}/{action}')
            insist(d['grounded_after']==prior_state(rows,f"{d['state']}:{d['selected_action']}",seq+1),
                   f'{case}/{arm} grounded post-state {j+1}')
            freeze=freezes[j]
            insist(freeze['selected_action']==d['selected_action'] and
                   freeze['decision_source']==d['decision_source'] and
                   freeze['action_call_id']==d['action_call_id'],f'{case}/{arm} action freeze {j+1}')
            route=select_route(d['grounded_assessments_before'])
            insist(d['admissible_actions']==route['candidates'] and d['selected_action'] in route['candidates'],
                   f'{case}/{arm} candidate scope {j+1}')
            escape,count=expected_escape(decisions[:j],d['state'],d['grounded_assessments_before'])
            insist(d['counter_before']==count,f'{case}/{arm} suffix reconstruction {j+1}')
            if d['decision_source']==SOURCE:
                insist(arm=='S' and escape==d['selected_action'] and d['policy_route']=='ESCAPE' and
                       d['policy_reason']==PURPOSE and d['acquisition_purpose']==PURPOSE and
                       d['action_call_id'] is None and d['action_parse_status']=='NOT_CALLED' and
                       d['selected_grounded_before']['kind']=='UNSEEN',f'{case}/{arm} escape scope {j+1}')
            else:
                insist(not (arm=='S' and escape is not None),f'{case}/{arm} omitted escape {j+1}')
                source=(route['source'] if route['route']=='MECHANICAL' else
                        source_for_model_choice(route,d['grounded_assessments_before'],d['selected_action']))
                insist(d['decision_source']==source and d['policy_route']==route['route'] and
                       d['policy_reason']==route['reason'],f'{case}/{arm} incumbent route {j+1}')
                if route['route']=='MECHANICAL':
                    insist(d['selected_action']==route['action'] and d['action_parse_status']=='NOT_CALLED',
                           f'{case}/{arm} mechanical choice {j+1}')
                else:insist(d['action_parse_status']=='VALID',f'{case}/{arm} parsed action {j+1}')
            pre_events=events[:seq-1];pre_rows=[x for x in rows if x['event_stream_sequence']<seq]
            p=proofs[j]
            insist(p[f'{arm}_raw_provenance_sha256']==provenance_hash(pre_events,pre_rows),
                   f'{case}/{arm} raw provenance proof {j+1}')
            projected=projection(decisions,d)
            insist(p[f'{arm}_semantic_projection_sha256']==digest(projected),
                   f'{case}/{arm} canonical projection proof {j+1}')
            planned=request_for(projected)
            insist(p[f'{arm}_request_sha256']==planned['canonical_sha256'] and
                   p[f'{arm}_wire_sha256']==planned['wire_sha256'],f'{case}/{arm} request proof {j+1}')
            if d['action_call_id'] is not None:
                call=d['action_call_id'];actual=[x for x in intents if x['call_id']==call]
                actual_attempts=[x for x in attempts if x['call_id']==call]
                insist(len(actual)==len(actual_attempts)==1 and
                       actual[0]['request_sha256']==planned['canonical_sha256'] and
                       actual_attempts[0]['request_bytes_sha256']==planned['wire_sha256'] and
                       actual_attempts[0]['request_bytes_utf8'].encode()==planned['wire'],
                       f'{case}/{arm} actual transport request {j+1}')
        return dict(decisions=decisions,events=events,rows=rows,intents=intents,
                    attempts=attempts,results=results,references=references,proofs=proofs,
                    private_sha256={str(p.relative_to(path)):file_hash(p) for p in path.rglob('*')
                                    if p.is_file() and p.name!='.lock'})

def analyze(root):
    runs={case:{arm:audit_arm(root,case,arm) for arm in ('I','S')} for case in CASES}
    per_case={};all_pairs=[];shared=0;independent=0;false_triggers=0;matched_inactive=0
    for case,arms in runs.items():
        I,S=arms['I'],arms['S'];pairs=[]
        for j,(ip,sp) in enumerate(zip(I['proofs'],S['proofs'])):
            p=json.loads((root/'pairs'/case/f'{j+1:02d}.json').read_text())
            signed_i={k:v for k,v in ip.items() if k!='recorded_at'}
            signed_s={k:v for k,v in sp.items() if k!='recorded_at'}
            insist(signed_i==signed_s and all(p[k]==v for k,v in signed_i.items()),
                   f'{case} signed paired proof {j+1}')
            i=I['decisions'][j];s=S['decisions'][j]
            imatched=(i['state']==s['state'] and
                      history_projection(I['events'][:i['event_stream_sequence']-1])==
                      history_projection(S['events'][:s['event_stream_sequence']-1]) and
                      ip['I_semantic_projection_sha256']==ip['S_semantic_projection_sha256'] and
                      i['admissible_actions']==s['admissible_actions'])
            trigger,_=expected_escape(S['decisions'][:j],s['state'],s['grounded_assessments_before'])
            insist(p['matched_context']==imatched and p['S_trigger']==(trigger is not None),
                   f'{case} pairing condition {j+1}')
            if case in CONTROLS and trigger is not None:false_triggers+=1
            if imatched and trigger is None:
                matched_inactive+=1
                insist(i['selected_action']==s['selected_action'],f'{case} matched inactive action {j+1}')
                if i['policy_route']=='MODEL':
                    shared+=1
                    insist(p['shared_draw'] and len([r for r in S['references'] if r['decision_id']==s['decision_id']])==1 and
                           s['action_call_id'] is None and i['action_call_id'] is not None and
                           p['I_semantic_projection_sha256']==p['S_semantic_projection_sha256'] and
                           p['I_raw_provenance_sha256']!=p['S_raw_provenance_sha256'] and
                           p['shared_request_sha256']==p['I_request_sha256']==p['S_request_sha256'] and
                           p['shared_response_sha256'] is not None,
                           f'{case} single shared draw {j+1}')
                else:insist(not p['shared_draw'] and i['action_call_id'] is None and s['action_call_id'] is None,
                           f'{case} mechanical parity {j+1}')
                if i['selected_action']==s['selected_action']:
                    insist(i['realized']==s['realized'],f'{case} matched-world receipt projection {j+1}')
            else:
                insist(not p['shared_draw'],f'{case} forbidden sharing {j+1}')
                if not imatched:independent+=sum(d['action_call_id'] is not None for d in (i,s))
            pairs.append(p);all_pairs.append(p)
        escapes=[d for d in S['decisions'] if d['decision_source']==SOURCE]
        first=next((d for d in escapes if d['index']==4),None)
        first_endpoint=bool(first and first['counter_before']==3 and
                            first['selected_grounded_before']['kind']=='UNSEEN' and
                            first['grounded_after']['kind']!='UNSEEN' and
                            I['decisions'][3]['grounded_assessments_before'][first['selected_action']]['kind']=='UNSEEN' and
                            I['decisions'][3]['selected_action']!=first['selected_action'])
        count,relation=independent_suffix(S['decisions'])
        streak=0;maximum=0;last=None
        for d in S['decisions']:
            key=(d['state'],d['selected_action'])
            streak=(streak+1 if key==last else 1) if qualifies(d) else 0
            last=key if streak else None;maximum=max(maximum,streak)
        per_case[case]=dict(horizon=CASES[case],matched_boundaries=sum(x['matched_context'] for x in pairs),
            shared_draws=sum(x['shared_draw'] for x in pairs),trigger_indices=[d['index'] for d in escapes],
            first_receipt_endpoint=first_endpoint if case in ELIGIBLE else None,
            first_escape_realized=first['realized'] if first else None,
            maximum_qualifying_streak=maximum,
            I_total_consequence=sum(d['realized']['consequence'] for d in I['decisions']),
            S_total_consequence=sum(d['realized']['consequence'] for d in S['decisions']),
            I_post_D4_consequence=sum(d['realized']['consequence'] for d in I['decisions'][4:]),
            S_post_D4_consequence=sum(d['realized']['consequence'] for d in S['decisions'][4:]),
            model_calls=dict(I=len(I['intents']),S=len(S['intents'])),
            physical_attempts=dict(I=len(I['attempts']),S=len(S['attempts'])),
            receipt_hashes=dict(I=[d['receipt_provenance_sha256'] for d in I['decisions']],
                                S=[d['receipt_provenance_sha256'] for d in S['decisions']]))
    restart=json.loads((root/'restart-E4.json').read_text())
    restart_pass=restart['status']=='PASS' and restart['reconstructed_suffix']['S']['count']==2
    mechanism=all(per_case[c]['first_receipt_endpoint'] and
                  per_case[c]['maximum_qualifying_streak']<=3 for c in ELIGIBLE)
    control_pass=all(not per_case[c]['trigger_indices'] for c in CONTROLS)
    cost_pass=per_case['E2']['S_post_D4_consequence']>=per_case['E2']['I_post_D4_consequence']
    # A negative acquisition cost is compared on the remaining horizon exactly as preregistered.
    if not mechanism or not control_pass or false_triggers:
        recommendation='RETAIN_INCUMBENT'
    elif not restart_pass or not cost_pass:
        recommendation='RETAIN_INCUMBENT' if not cost_pass else 'MORE_EVIDENCE_REQUIRED'
    elif matched_inactive==0 or shared==0:
        recommendation='MORE_EVIDENCE_REQUIRED'
    else:recommendation='PROMOTE_S'
    report=dict(campaign_status='VALID',recommendation=recommendation,
        canonical_model_view_changes_historical_raw_prompt=True,
        prior_replication_status='COST_OR_SCOPE_BLOCKS_PROMOTION',
        prior_replication_recommendation='RETAIN_INCUMBENT',
        prior_action_model_audit='ACTION_MODEL_STOCHASTIC_AS_CONFIGURED',
        counts=dict(matched_inactive=matched_inactive,shared_model_draws=shared,
                    independent_post_divergence_model_calls=independent,
                    false_triggers=false_triggers,total_physical_attempts=sum(
                        len(runs[c][a]['attempts']) for c in CASES for a in ('I','S'))),
        mechanism_pass=mechanism,control_pass=control_pass,restart_pass=restart_pass,
        negative_cost_gate_pass=cost_pass,per_case=per_case)
    private=dict(report=report,paired_records=all_pairs,
        artifact_sha256={c:{a:runs[c][a]['private_sha256'] for a in ('I','S')} for c in CASES})
    _atomic_write(root/'analysis.private.json',private)
    _atomic_write(root/'analysis.public.json',report)
    return report

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',type=Path,required=True)
    print(json.dumps(analyze(p.parse_args().private_root),sort_keys=True))
