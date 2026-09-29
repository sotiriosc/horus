"""Independent signed replay, semantic fixation gate and frozen classification."""
from argparse import ArgumentParser
from collections import Counter,defaultdict
from hashlib import sha256
from math import ceil
from pathlib import Path
from statistics import median
import json

from horus.core import digest
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,file_hash,canonical
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    ACTIONS,GOAL,RECENT_DECISION_LIMIT,select_route,source_for_model_choice)
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import expected_escape,qualifies
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import PURPOSE
from experiments.grounded_stagnation_escape_promotion_controlled_v0.worker import semantic_assessments
from experiments.qwen3_bounded_thinking_action_v0_1.pure import build_request,sha
from .shared import STUDY,PRIVATE_STUDY,verify_sources


def insist(ok,message):
    if not ok:raise RuntimeError('INVALID: '+message)


def visible_assessment(value):
    return {k:v for k,v in value.items() if k!='recent_receipt_provenance'}


def semantic_signature(assessments,allowed):
    """Material grounded content, independent of state, provenance and display order."""
    return canonical(dict(allowed=sorted(allowed),assessments={action:dict(
        kind=a['kind'],relation_type=a['relation_type'],assessment_status=a['assessment_status'],
        established_value=a.get('established_value') if a['kind']=='ESTABLISHED' else None,
        unresolved_values=[a.get('established_value'),a.get('candidate_value')]
            if a['kind']=='UNRESOLVED_CHANGE' else None,
        empirical_frequencies=a.get('empirical_frequencies') if a['relation_type']=='EMPIRICAL' else None)
        for action,a in sorted(assessments.items())}))


def contextual_diversity(model_records):
    patterns=defaultdict(Counter)
    for record in model_records:
        patterns[semantic_signature(record['grounded_assessments_before'],
                                    record['admissible_actions'])][record['selected_action']]+=1
    qualifying=[]
    for signature,actions in patterns.items():
        total=sum(actions.values());maximum=max(actions.values());winners=[a for a,n in actions.items() if n==maximum]
        if total>=2 and maximum>=2 and len(winners)==1:
            qualifying.append(dict(signature_sha256=sha(signature),winner=winners[0],
                                   winner_count=maximum,total=total))
    passed=any(a['winner']!=b['winner'] for i,a in enumerate(qualifying) for b in qualifying[i+1:])
    return dict(pass_status=passed,distinct_material_patterns=len(patterns),
                recurrent_winning_patterns=qualifying)


def exact_snapshot_run(private,pair):
    path=private/'runs'/f'T{pair}'
    insist((path/'complete.json').is_file(),f'T{pair} complete marker')
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        memory.reconcile(store)
        events=store.records['events'];memory_rows=memory.rows();calls=store.records['calls']
        decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        freezes=[x['record'] for x in calls if x['kind']=='ACTION_FROZEN']
        intents=[x['record'] for x in calls if x['kind']=='REQUEST_INTENT']
        attempts=[x['record'] for x in calls if x['kind']=='TRANSPORT_ATTEMPT_RESULT']
        parses=[x['record'] for x in calls if x['kind']=='PARSED']
        insist(len(decisions)==len(events)==len(memory_rows)==len(freezes)==30,
               f'T{pair} decision/receipt/Memory/freeze cardinality')
        insist(not rows_of(store,'SELF_REVIEW_NON_AUTHORITATIVE'),f'T{pair} no self-review')
        steps=[json.loads(line) for line in (path/'step-summaries.private.jsonl').read_text().splitlines()]
        insist(len(steps)==30,f'T{pair} step summaries')
        model_count=sum(d['action_call_id'] is not None for d in decisions)
        insist(len(intents)==len(attempts)==len(parses)==model_count,f'T{pair} model attempt cardinality')
        new_exact=set();new_observed=set();public_rows=[];unresolved=[]
        states=set();actions=set()
        for n,(d,e,freeze,step) in enumerate(zip(decisions,events,freezes,steps),1):
            ev=e['record'];receipt=ev['receipt'];action=d['selected_action'];states.update((d['state'],d['realized']['next_state']));actions.add(action)
            insist(d['index']==n and ev['decision_index']==n and d['event_stream_sequence']==n,
                   f'T{pair}:{n} sequence')
            insist(ev['study']==PRIVATE_STUDY and ev['run']==f'T{pair}' and
                   ev['authorization_status']=='AUTHORIZED' and ev['execution_kind']=='AUTONOMOUS_EXECUTION',
                   f'T{pair}:{n} authorization')
            insist(d['state']==receipt['pre_state'] and action==receipt['action'] and
                   d['realized']==dict(next_state=receipt['next_state'],
                                       consequence=receipt['realized_consequence']),
                   f'T{pair}:{n} receipt outcome')
            insist(digest(receipt)==ev['receipt_provenance_sha256']==d['receipt_provenance_sha256']
                   ==step['receipt_sha256'] and d['receipt_identity']==ev['receipt_identity'],
                   f'T{pair}:{n} provenance')
            insist(freeze['selected_action']==action and freeze['decision_source']==d['decision_source']
                   and freeze['action_call_id']==d['action_call_id'],f'T{pair}:{n} frozen action')
            for candidate in ACTIONS:
                insist(d['grounded_assessments_before'][candidate]==
                       prior_state(memory_rows,f"{d['state']}:{candidate}",n),
                       f'T{pair}:{n} grounded pre-state {candidate}')
            relation=f"{d['state']}:{action}"
            insist(d['grounded_after']==prior_state(memory_rows,relation,n+1),
                   f'T{pair}:{n} grounded post-state')
            selected=d['selected_grounded_before']
            if selected['kind']!='ESTABLISHED' and d['grounded_after']['kind']=='ESTABLISHED':
                new_exact.add(relation)
            if selected['kind']=='UNSEEN' and d['grounded_after']['kind']!='UNSEEN':
                new_observed.add(relation)
            route=select_route(d['grounded_assessments_before'])
            insist(d['admissible_actions']==route['candidates'] and action in route['candidates'],
                   f'T{pair}:{n} candidate route')
            escape,_=expected_escape(decisions[:n-1],d['state'],d['grounded_assessments_before'])
            if d['decision_source']=='STAGNATION_ESCAPE':
                insist(escape==action and d['policy_route']=='ESCAPE' and
                       d['policy_reason']==PURPOSE and d['action_call_id'] is None and
                       d['action_parse_status']=='NOT_CALLED' and selected['kind']=='UNSEEN',
                       f'T{pair}:{n} frozen model-free escape')
            else:
                insist(escape is None,f'T{pair}:{n} missed escape')
                source=route['source'] if route['route']=='MECHANICAL' else \
                    source_for_model_choice(route,d['grounded_assessments_before'],action)
                insist(d['decision_source']==source and d['policy_route']==route['route'] and
                       d['policy_reason']==route['reason'],f'T{pair}:{n} policy authority')
                if route['route']=='MECHANICAL':
                    insist(action==route['action'] and d['action_call_id'] is None and
                           d['action_parse_status']=='NOT_CALLED',f'T{pair}:{n} mechanical ceiling')
                else:
                    insist(d['action_call_id'] is not None and d['action_parse_status']=='VALID',
                           f'T{pair}:{n} strict model action')
            insist(step['selected_action']==action and step['realized_consequence']==
                   d['realized']['consequence'] and step['inference']['call_id']==d['action_call_id'],
                   f'T{pair}:{n} step journal')
            if d['action_call_id'] is not None:
                matches=[x for x in intents if x['call_id']==d['action_call_id']]
                attempt=[x for x in attempts if x['call_id']==d['action_call_id']]
                parsed=[x for x in parses if x['call_id']==d['action_call_id']]
                insist(len(matches)==len(attempt)==len(parsed)==1 and parsed[0]['status']=='VALID',
                       f'T{pair}:{n} unique strict physical attempt')
                history=[dict(decision_id=x['decision_id'],state=x['state'],
                    action=x['selected_action'],authenticated_consequence=x['realized']['consequence'],
                    source=x['decision_source']) for x in decisions[:n-1]][-RECENT_DECISION_LIMIT:]
                projection=dict(goal=GOAL,decision_id=f'C:D{n:02d}',decision_index=n,
                    current_state=d['state'],available_actions=route['candidates'],
                    grounded_assessments=semantic_assessments(d['grounded_assessments_before']),
                    recent_agent_working_context=history)
                request=build_request(projection,route['candidates'],3303+n)
                wire=json.dumps(request,separators=(',',':')).encode()
                insist(matches[0]['semantic_projection_sha256']==digest(projection) and
                       matches[0]['request_sha256']==digest(request) and
                       matches[0]['request_bytes_sha256']==sha(wire) and
                       attempt[0]['request_bytes_sha256']==sha(wire) and
                       attempt[0]['transport_error'] is None and
                       step['inference']['raw_response_sha256']==digest(attempt[0]['response']),
                       f'T{pair}:{n} exact model request/response projection')
                insist(step['inference']['action_parse_status']=='VALID' and
                       step['inference']['finish_reason']=='stop',f'T{pair}:{n} final interface')
            if d['action_call_id'] is not None and any(
                    d['grounded_assessments_before'][candidate]['kind']=='UNRESOLVED_CHANGE'
                    for candidate in route['candidates']):
                alternatives={candidate:visible_assessment(d['grounded_assessments_before'][candidate])
                              for candidate in route['candidates']}
                later=[]
                for candidate in route['candidates']:
                    if alternatives[candidate]['kind']=='UNRESOLVED_CHANGE':
                        rel=f"{d['state']}:{candidate}"
                        final=prior_state(memory_rows,rel,31)
                        later.append(dict(relation=rel,final_kind=final['kind'],
                            resolved_to_established=final['kind']=='ESTABLISHED'))
                unresolved.append(dict(decision_id=d['decision_id'],state=d['state'],
                    available_grounded_alternatives=alternatives,display_order=route['candidates'],
                    selected_action=action,reasoning_tokens=step['inference']['reasoning_tokens'],
                    realized_consequence=d['realized']['consequence'],later_resolution=later))
            public_rows.append(dict(decision_id=d['decision_id'],index=n,state=d['state'],
                assessments={candidate:visible_assessment(value) for candidate,value in
                    d['grounded_assessments_before'].items()},
                admissible_actions=d['admissible_actions'],action=action,
                decision_source=d['decision_source'],audit_source=step['audit_source'],
                parse_status=d['action_parse_status'],selected_kind=selected['kind'],
                selected_relation_type=selected['relation_type'],
                consequence=d['realized']['consequence'],next_state=d['realized']['next_state'],
                grounded_change=d['grounded_state_change'],receipt_identity=d['receipt_identity'],
                receipt_sha256=d['receipt_provenance_sha256'],event_identity=d['event_identity'],
                known_negative_with_better_established=d['known_negative_with_better_established'],
                suffix_before=step['suffix_before'],suffix_after=step['suffix_after'],
                inference=step['inference']))
        restart=None
        if pair==2:
            restart=json.loads((path/'restart-verdict.json').read_text())
            insist(restart['status']=='PASS' and restart['fresh_process'] and
                   restart['durable_memory_exact'] and restart['grounded_state_exact'] and
                   restart['current_state_exact'] and restart['signed_stagnation_suffix_exact'] and
                   restart['first_post_restart_decision_valid'] and
                   not restart['first_post_restart_decision_pending'], 'T2 restart')
        model_steps=[step['inference'] for step in steps if step['inference']['call_id'] is not None]
        metrics=dict(realized_consequence_total=sum(d['realized']['consequence'] for d in decisions),
            action_distribution=dict(Counter(d['selected_action'] for d in decisions)),
            model_action_distribution=dict(Counter(d['selected_action'] for d in decisions
                if d['action_call_id'] is not None)),
            new_exact_relations=len(new_exact),new_exact_relation_ids=sorted(new_exact),
            newly_grounded_relations_historical_definition=len(new_observed),
            unseen_selections=sum(d['selected_grounded_before']['kind']=='UNSEEN' for d in decisions),
            unresolved_selections=sum(d['selected_grounded_before']['kind']=='UNRESOLVED_CHANGE' for d in decisions),
            distinct_states_explored=sorted(states),distinct_actions_explored=sorted(actions),
            known_negative_with_better_established=sum(d['known_negative_with_better_established'] for d in decisions),
            mechanical_decisions=sum(d['decision_source']=='GROUNDED_MECHANICAL' for d in decisions),
            established_plus_one_mechanical_choices=sum(d['decision_source']=='GROUNDED_MECHANICAL' and
                d['selected_grounded_before']['kind']=='ESTABLISHED' and
                (d['selected_grounded_before']['established_value'] or {}).get('consequence')==1 for d in decisions),
            safe_grounded_fallbacks=sum(d['decision_source']=='SAFE_GROUNDED_FALLBACK' for d in decisions),
            stagnation_escapes=sum(d['decision_source']=='STAGNATION_ESCAPE' for d in decisions),
            model_decisions=len(model_steps),model_choices_unseen=sum(d['action_call_id'] is not None and
                d['selected_grounded_before']['kind']=='UNSEEN' for d in decisions),
            model_choices_involving_unresolved=len(unresolved),
            input_tokens=sum(s['input_tokens'] for s in model_steps),
            reasoning_tokens=sum(s['reasoning_tokens'] or 0 for s in model_steps),
            final_output_tokens_proxy=sum(s['final_output_tokens_proxy'] or 0 for s in model_steps),
            prompt_seconds=sum(s['prompt_eval_seconds'] for s in model_steps),
            reasoning_generation_seconds=sum(s['generation_seconds'] for s in model_steps),
            model_inference_wall_seconds=sum(s['wall_seconds'] for s in model_steps),
            physical_attempts=sum(s['physical_attempts'] for s in model_steps),
            receipt_memory_replay='PASS',restart=restart)
        hashes={str(p.relative_to(path)):file_hash(p) for p in path.rglob('*')
                if p.is_file() and p.name!='.lock'}
        return dict(metrics=metrics,decisions=public_rows,unresolved_contexts=unresolved,
                    private_artifact_sha256=hashes,model_records=[d for d in decisions
                        if d['action_call_id'] is not None],model_timings=[s['wall_seconds'] for s in model_steps])


def classify(runs):
    records=[d for run in runs.values() for d in run['model_records']]
    model_actions=Counter(d['selected_action'] for d in records)
    n=len(records);share=max(model_actions.values())/n if n else 1
    contextual=contextual_diversity(records)
    violations=sum(run['metrics']['known_negative_with_better_established'] for run in runs.values())
    fixation_checks=dict(two_model_action_names=len(model_actions)>=2,
        largest_action_share_at_most_85_percent=share<=.85,
        recurring_actions_across_materially_different_patterns=contextual['pass_status'],
        zero_known_negative_with_better_established=violations==0,
        zero_grounded_authority_violations=True)
    fixation=all(fixation_checks.values())
    exact=sum(run['metrics']['new_exact_relations'] for run in runs.values())
    observed=sum(run['metrics']['newly_grounded_relations_historical_definition'] for run in runs.values())
    consequence=sum(run['metrics']['realized_consequence_total'] for run in runs.values())
    timings=[time for run in runs.values() for time in run['model_timings']]
    ordered=sorted(timings);warm_median=median(ordered) if ordered else None
    p95=ordered[ceil(.95*len(ordered))-1] if ordered else None
    latency=bool(ordered and warm_median<15 and p95<20)
    material_failure=consequence<0 or violations>0
    if fixation and exact>=6 and latency and not material_failure:
        classification='QWEN_R128_AUTONOMOUS_SUPPORTED';recommendation='PROMOTE_QWEN_R128'
    elif fixation and exact>=6 and not latency and not material_failure:
        classification='QWEN_R128_TOO_SLOW';recommendation='RETAIN_DOLPHIN'
    elif not fixation and exact<6:
        classification='QWEN_R128_STILL_POLICY_LIMITED';recommendation='RETAIN_DOLPHIN'
    else:
        classification='MIXED_QWEN_R128_RESULT';recommendation='MORE_EVIDENCE_REQUIRED'
    return dict(classification=classification,recommendation=recommendation,
        fixation_gate='PASS' if fixation else 'FAIL',fixation_checks=fixation_checks,
        model_action_counts=dict(model_actions),largest_model_action_share=share,
        contextual_diversity=contextual,new_exact_relations=exact,
        historical_newly_grounded_relations=observed,
        exploration_minimum_six=exact>=6,dolphin_reference_nine_met_descriptively=exact>=9,
        total_realized_consequence=consequence,material_new_behavioral_failure=material_failure,
        latency_gate='PASS' if latency else 'FAIL',median_warm_action_wall_seconds=warm_median,
        p95_nearest_rank_action_wall_seconds=p95,
        total_model_inference_wall_seconds=sum(ordered),model_decisions=n,
        timeout_events=0,strict_interface='PASS',authority_replay='PASS',restart='PASS',
        historical_reference=dict(Q_N=dict(model_HOLD='90/90',new_grounded_relations=3,
            action_inference_wall_seconds=36.80),D=dict(new_grounded_relations=9,
            action_inference_wall_seconds=1776.09)),
        trajectories_diverge_no_counterfactual_claim=True)


def analyze(private):
    verify_sources()
    runs={f'T{pair}':exact_snapshot_run(private,pair) for pair in (1,2,3)}
    verdict=classify(runs)
    public=dict(campaign_integrity='PASS',verdict=verdict,
        runs={name:dict(metrics=run['metrics'],decisions=run['decisions'],
                        unresolved_contexts=run['unresolved_contexts']) for name,run in runs.items()})
    _atomic_write(STUDY/'public-result.json',public)
    _atomic_write(STUDY/'private-artifact-hashes.json',
                  {name:run['private_artifact_sha256'] for name,run in runs.items()})
    print(json.dumps(verdict,sort_keys=True),flush=True)
    return public

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    args=p.parse_args();analyze(args.private_root)
