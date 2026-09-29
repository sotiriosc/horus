"""Apply the preregistered behavioral and performance thresholds to replayed rows."""
from collections import Counter
from pathlib import Path
import json

from horus.live import _atomic_write
from .shared import STUDY


def evaluate():
    public=json.loads((STUDY/'stage-b-public.json').read_text())
    if public['campaign_integrity']!='PASS':raise RuntimeError('independent replay not passed')
    runs=public['runs']
    aggregated={}
    for arm in ('D','Q'):
        selected=[runs[f'{arm}{n}'] for n in (1,2,3)]
        metrics=[x['metrics'] for x in selected]
        rows=[r for run in selected for r in run['decisions']]
        model_rows=[r for r in rows if r['inference']['call_id'] is not None]
        counts=Counter(r['action'] for r in model_rows)
        patterns_by_action={a:set() for a in counts}
        for run in selected:
            for pattern,actions in run['metrics']['model_action_by_semantic_pattern'].items():
                for action,count in actions.items():
                    if count:patterns_by_action[action].add(pattern)
        fixation=[dict(action=a,count=count,total=len(model_rows),fraction=count/len(model_rows),
                       distinct_semantic_patterns=len(patterns_by_action[a]))
                  for a,count in counts.items() if len(model_rows)>=10 and
                  count/len(model_rows)>.8 and len(patterns_by_action[a])>=2]
        aggregated[arm]=dict(
            consequence_sum=sum(m['consequence_sum'] for m in metrics),
            known_negative_with_better_known=sum(m['known_negative_with_better_known'] for m in metrics),
            unseen_selections=sum(m['unseen_selections'] for m in metrics),
            unseen_available_decisions=sum(any(a['kind']=='UNSEEN' for a in r['assessments'].values()) for r in rows),
            unresolved_selections=sum(m['unresolved_selections'] for m in metrics),
            newly_grounded_relations=sum(m['newly_grounded_relations'] for m in metrics),
            neutral_fallback_model_decisions=sum(m['neutral_fallback_model_decisions'] for m in metrics),
            longest_same_relation_neutral_fallback_streak=max(m['longest_same_relation_neutral_fallback_streak'] for m in metrics),
            stagnation_escapes=sum(m['stagnation_escapes'] for m in metrics),
            mechanical_decisions=sum(m['mechanical_decisions'] for m in metrics),
            model_decisions=len(model_rows),abstentions=sum(m['abstentions'] for m in metrics),
            model_action_distribution=dict(counts),action_name_fixation=fixation,
            inference_wall_seconds=sum(m['inference_wall_seconds'] for m in metrics),
            prompt_eval_seconds=sum(m['prompt_eval_seconds'] for m in metrics),
            generation_seconds=sum(m['generation_seconds'] for m in metrics),
            input_tokens=sum(m['input_tokens'] for m in metrics),
            output_tokens=sum(m['output_tokens'] for m in metrics),
            runner_load_events=sum(m['runner_load_events'] for m in metrics),
            runner_load_seconds=sum(m['runner_load_seconds'] for m in metrics),
            all_receipt_memory_replay_pass=all(m['receipt_memory_replay']=='PASS' for m in metrics),
            restart_pass=metrics[1]['restart']['status']=='PASS',
            all_action_status_valid=all(r['parse_status'] in ('VALID','NOT_CALLED') for r in rows))
    d,q=aggregated['D'],aggregated['Q']
    regression=dict(
        authority_receipt_memory_or_restart_failure=not(q['all_receipt_memory_replay_pass'] and q['restart_pass'] and q['all_action_status_valid']),
        known_negative_with_better_known=q['known_negative_with_better_known']>0,
        consequence_more_than_six_below_d=q['consequence_sum']<d['consequence_sum']-6,
        at_least_three_fewer_newly_grounded=q['newly_grounded_relations']<=d['newly_grounded_relations']-3,
        more_than_nine_additional_neutral_fallbacks=q['neutral_fallback_model_decisions']>d['neutral_fallback_model_decisions']+9,
        zero_q_unseen_with_unseen_available=q['unseen_selections']==0 and q['unseen_available_decisions']>0,
        q_action_name_fixation=bool(q['action_name_fixation']))
    stage_a={arm:json.loads((STUDY/f'stage-a-{arm.lower()}-results.json').read_text()) for arm in ('D','Q')}
    case_actions={case:{arm:stage_a[arm]['decisions'][case]['action'] for arm in ('D','Q')}
                  for case in stage_a['D']['decisions']}
    report=dict(aggregate=aggregated,material_regression_flags=regression,
        any_material_regression=any(regression.values()),
        action_inference_speed_ratio_d_over_q=d['inference_wall_seconds']/q['inference_wall_seconds'],
        speed_gate_at_least_five_x=d['inference_wall_seconds']/q['inference_wall_seconds']>=5,
        fixed_fixture_actions=case_actions,
        pairwise_consequence={str(i):dict(D=runs[f'D{i}']['metrics']['consequence_sum'],
            Q=runs[f'Q{i}']['metrics']['consequence_sum']) for i in (1,2,3)})
    _atomic_write(STUDY/'threshold-audit.json',report)
    return report

if __name__=='__main__':
    result=evaluate()
    print(json.dumps({k:result[k] for k in ('material_regression_flags',
        'action_inference_speed_ratio_d_over_q','speed_gate_at_least_five_x')},sort_keys=True))
