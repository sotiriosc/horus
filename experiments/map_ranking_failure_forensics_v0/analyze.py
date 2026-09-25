"""Pure retrospective tabulation. No mechanical chooser or experiment runtime."""
from collections import Counter, defaultdict
from copy import deepcopy
import argparse
import hashlib
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ACTIONS = ('ADVANCE', 'HOLD', 'RETREAT')


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def ranking(values):
    return [[a for a in ACTIONS if values[a] == v] for v in sorted(set(values.values()), reverse=True)]


def ratio(n, d):
    return dict(matches=n, total=d, rate=n / d if d else None)


def modes(values):
    counts = Counter(values); n = max(counts.values())
    return sorted(v for v, k in counts.items() if k == n)


def summary(rows):
    n = len(rows)
    return dict(n=n, consequence_distribution={str(v): sum(r['parsed_prediction']['consequence'] == v for r in rows) for v in (-1, 0, 1)},
        latest_copy=ratio(sum(r['LATEST_COPY'] for r in rows), n),
        exact_accuracy=ratio(sum(r['exact_correct'] for r in rows), n),
        consequence_accuracy=ratio(sum(r['consequence_correct'] for r in rows), n),
        tie_context_forecasts=sum(r['in_tie_context'] for r in rows),
        tied_maximum_members=sum(r['tied_maximum_member'] for r in rows),
        erroneous_tie_creators=sum(r['erroneous_tie_creator'] for r in rows),
        wrong_unique_max_members=sum(r['wrong_unique_max_member'] for r in rows),
        wrong_ranking_error_forecasts=sum(r['in_wrong_ranking'] and not r['consequence_correct'] for r in rows))


def analyze(evidence):
    assert len(evidence) == 48
    before = deepcopy(evidence)
    forecasts = []; contexts = []
    for c in evidence:
        assert [r['action'] for r in c['actions']] == list(ACTIONS)
        pred = {r['action']: r['parsed_prediction']['consequence'] for r in c['actions']}
        truth = {r['action']: r['retained_detached_outcome']['consequence'] for r in c['actions']}
        latest = {r['action']: r['history'][-1]['consequence'] for r in c['actions']}
        rp, rt, rl = ranking(pred), ranking(truth), ranking(latest)
        assert len(rt[0]) == 1
        best = rt[0][0]
        classification = 'MAP_TIE' if len(rp[0]) > 1 else 'MAP_TRUE_BEST_UNIQUE' if rp[0][0] == best else 'MAP_WRONG_UNIQUE'
        same = rp == rl
        counter = ('SAME_TIE' if len(rp[0]) > 1 else 'SAME_WRONG_MAXIMUM' if rp[0][0] != best else 'SAME_RANKING') if same else 'DIFFERENT'
        errors = [a for a in ACTIONS if pred[a] != truth[a]]
        under = pred[best] < truth[best]
        over = [a for a in ACTIONS if a != best and pred[a] > truth[a]]
        failure = None
        if classification != 'MAP_TRUE_BEST_UNIQUE':
            if classification == 'MAP_TIE' and len(errors) > 1: failure = 'D_MULTIPLE_FORECAST_ERRORS_CREATE_TIE'
            elif under and over: failure = 'C_BOTH'
            elif under: failure = 'A_TRUE_BEST_ACTION_UNDERPREDICTED'
            elif over: failure = 'B_NON_BEST_ACTION_OVERPREDICTED'
            elif classification == 'MAP_TIE' and not errors: failure = 'E_CORRECT_FORECASTS_DOMAIN_TIE'
            else: failure = 'F_OTHER_AMBIGUOUS'
        context = {k: c[k] for k in ('context_index', 'family', 'world', 'mapping_index', 'mapping', 'state', 'epoch')}
        context.update(predicted_triple=[pred[a] for a in ACTIONS], actual_triple=[truth[a] for a in ACTIONS], latest_triple=[latest[a] for a in ACTIONS],
            predicted_ranking=rp, actual_ranking=rt, latest_ranking=rl, classification=classification,
            counterfactual_relation=counter, same_maximum_set=rp[0] == rl[0], same_consequence_triple=pred == latest,
            latest_ranking_true_best_unique=len(rl[0]) == 1 and rl[0][0] == best,
            failure_class=failure, consequence_error_actions=errors, true_best_underpredicted=under, non_best_overpredicted=over,
            all_components_exact=all(r['parsed_prediction'] == r['retained_detached_outcome'] for r in c['actions']))
        contexts.append(context)
        for r in c['actions']:
            row = deepcopy(r); row.update({k: c[k] for k in ('context_index', 'family', 'world', 'mapping_index', 'state', 'epoch')})
            a = r['action']; actual = r['retained_detached_outcome']; p = r['parsed_prediction']; h = r['history']
            assert len(h) == r['history_depth'] and h[-1] == r['latest_observation']
            corrected = {**pred, a: truth[a]}
            row.update(LATEST_COPY=p['consequence'] == h[-1]['consequence'],
                latest_relation='LATEST_COPY' if p['consequence'] == h[-1]['consequence'] else 'NON_LATEST',
                consequence_correct=p['consequence'] == actual['consequence'], next_state_correct=p['next_state'] == actual['next_state'], exact_correct=p == actual,
                depth_bin=str(len(h)) if len(h) < 3 else '3+',
                in_tie_context=classification == 'MAP_TIE', in_wrong_ranking=classification == 'MAP_WRONG_UNIQUE',
                tied_maximum_member=classification == 'MAP_TIE' and a in rp[0],
                erroneous_tie_creator=classification == 'MAP_TIE' and pred[a] != truth[a] and len(ranking(corrected)[0]) == 1,
                wrong_unique_max_member=classification == 'MAP_WRONG_UNIQUE' and a == rp[0][0],
                consequence_error=p['consequence']-actual['consequence'])
            forecasts.append(row)
    assert len(forecasts) == 144 and evidence == before
    groups = {}
    for key in ('world', 'family', 'action', 'alias', 'mapping_index', 'depth_bin', 'alias_registry_position', 'map_call_position', 'seed'):
        groups[key] = {str(v): summary([r for r in forecasts if r[key] == v]) for v in sorted({r[key] for r in forecasts})}
    by_family = {f: {key: {str(v): summary([r for r in forecasts if r['family'] == f and r[key] == v]) for v in sorted({r[key] for r in forecasts if r['family'] == f})}
                    for key in ('world','action','alias','mapping_index','depth_bin','alias_registry_position')} for f in ('O1', 'O2')}
    fitted = {key: {str(v): modes([r['parsed_prediction']['consequence'] for r in forecasts if r[key] == v]) for v in sorted({r[key] for r in forecasts})} for key in ('alias','action')}
    # No held-out claim: these constants are modal outputs fitted on this same table.
    # Retain all tied modal constants as alternatives; choose lowest only to tabulate one explicit fixed rule.
    selected = {key: {k: vals[0] for k, vals in group.items()} for key, group in fitted.items()}
    for r in forecasts:
        h = [x['consequence'] for x in r['history']]; p = r['parsed_prediction']['consequence']
        r['simple_rule_matches'] = dict(latest=p == h[-1], most_frequent=p in modes(h), first=p == h[0],
            constant_zero=p == 0, fixed_alias=p == selected['alias'][r['alias']], fixed_action=p == selected['action'][r['action']])
    rule_names = tuple(forecasts[0]['simple_rule_matches'])
    def rule_summary(rows):return {k: ratio(sum(r['simple_rule_matches'][k] for r in rows), len(rows)) for k in rule_names}
    rules = dict(all=rule_summary(forecasts), by_family={f: rule_summary([r for r in forecasts if r['family']==f]) for f in ('O1','O2')},
        by_world={w: rule_summary([r for r in forecasts if r['world']==w]) for w in ('W0','W1','W3','D1')},
        fitted_modal_alternatives=fitted, fitted_selected_constants=selected,
        interpretation='Compatibility only. Fixed outputs are optimistic in-sample modal baselines; numeric-min tie convention is explicit, not a claim about the model. Constant zero cannot identify uncertainty. History modes are unambiguous here.')
    patterns = {}
    for w in ('W0', 'W1', 'W3', 'D1'):
        subset=[c for c in contexts if c['world']==w]
        triples=sorted({tuple(c['predicted_triple']) for c in subset})
        patterns[w]=[dict(triple=list(t),count=sum(tuple(c['predicted_triple'])==t for c in subset),
            by_family={f:sum(tuple(c['predicted_triple'])==t and c['family']==f for c in subset) for f in ('O1','O2')},
            context_indices=[c['context_index'] for c in subset if tuple(c['predicted_triple'])==t]) for t in triples]
    pairs=[]
    for w in ('W0','W1','W3','D1'):
        for m in range(6):
            for a in ACTIONS:
                p=[r for r in forecasts if r['world']==w and r['mapping_index']==m and r['action']==a]
                assert len(p)==2 and p[0]['seed']==p[1]['seed']
                assert p[0]['state']==p[1]['state']
                assert [{k:v for k,v in x.items() if k!='surface_action'} for x in p[0]['history']]==[{k:v for k,v in x.items() if k!='surface_action'} for x in p[1]['history']]
                pairs.append(dict(world=w,mapping_index=m,action=a,seed=p[0]['seed'],
                    aliases={r['family']:r['alias'] for r in p},consequences={r['family']:r['parsed_prediction']['consequence'] for r in p},
                    same_consequence=p[0]['parsed_prediction']['consequence']==p[1]['parsed_prediction']['consequence']))
    counter={k:sum(c['counterfactual_relation']==k for c in contexts) for k in ('SAME_RANKING','SAME_TIE','SAME_WRONG_MAXIMUM','DIFFERENT')}
    counter.update(same_maximum_set=sum(c['same_maximum_set'] for c in contexts),same_consequence_triple=sum(c['same_consequence_triple'] for c in contexts),
                   latest_true_best_unique=sum(c['latest_ranking_true_best_unique'] for c in contexts),contexts=48)
    return dict(study='map-ranking-failure-forensics-v0',diagnosis='NOT DETERMINABLE FROM RETAINED EVIDENCE',
        diagnosis_scope='Dominant internal mechanism is not identifiable. All 23 residual failures observably underpredict the true-best positive consequence and depart from latest history.',
        new_model_calls=0,new_world_executions=0,contexts=contexts,forecasts=forecasts,total=summary(forecasts),groups=groups,by_family=by_family,
        consequence_triple_patterns=patterns,simple_rules=rules,latest_ranking_counterfactual=counter,
        residual_failure_counts=dict(Counter(c['failure_class'] for c in contexts if c['failure_class'])),
        seed_pairs=pairs,seed_pair_same_consequence=sum(p['same_consequence'] for p in pairs),
        finite_domain_ties=dict(observed_ties=sum(c['classification']=='MAP_TIE' for c in contexts),
            genuine_correct_forecast_maximum_ties=sum(c['classification']=='MAP_TIE' and not c['consequence_error_actions'] for c in contexts),
            erroneous_maximum_ties=sum(c['classification']=='MAP_TIE' and bool(c['consequence_error_actions']) for c in contexts),
            underlying_continuous_quality='Not recorded; no inference beyond the declared finite consequence objective.'))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    manifest=json.loads((PACKAGE/'source-manifest.json').read_text());raw=(PACKAGE/'retained-evidence.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==manifest['finite_evidence_sha256']
    result=analyze(json.loads(raw));args.out.mkdir(parents=True,exist_ok=True);write(args.out/'results.json',result)
    print(json.dumps({k:result[k] for k in ('total','simple_rules','latest_ranking_counterfactual','residual_failure_counts','finite_domain_ties','seed_pair_same_consequence')},sort_keys=True))


if __name__=='__main__':main()
