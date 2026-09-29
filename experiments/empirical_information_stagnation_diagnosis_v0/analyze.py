"""Read-only projection of already published decision and empirical records.

No runner, model client, simulator, SessionStore, or Memory interface is imported.
All predicates below use only pre-decision fields. Stochastic schedules provide
relation-only signal proxies; they do not certify missing alternatives.
"""
from collections import Counter
from hashlib import sha256
from fractions import Fraction
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/empirical-information-stagnation-diagnosis-v0'
R128 = ROOT / 'research/qwen3-r128-autonomous-grounded-agent-v0/public-result.json'
HISTORY = ROOT / 'research/qwen3-grounded-agent-substitution-v0/stage-b-public.json'
SCHEDULES = ROOT / 'research/grounded-stochastic-relation-v0/evidence/schedules'
WINDOW = 4  # frozen grounded_state.empirical.WINDOW; no fitted threshold


def read(path):
    return json.loads(path.read_text())


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def counts(values):
    return {'+1': values.count(1), '0': values.count(0), '-1': values.count(-1)}


def distribution(values):
    if not values:
        return {}
    tally = Counter(values)
    return {v: Fraction(n, len(values)) for v, n in tally.items()}


def frequencies(values):
    tally = Counter(values)
    return {f'1:{v}': {'count': n, 'denominator': len(values)}
            for v, n in sorted(tally.items())}


def consecutive_negative(values):
    n = 0
    for v in reversed(values):
        if v != -1:
            break
        n += 1
    return n


def predicates(context):
    """Conditional signals. No future receipt, schedule phase, or unseen outcome."""
    kind = context['kind']
    if kind not in ('EMPIRICALLY_STABLE', 'VARIABLE_RELATION'):
        return {h: False for h in ('H1', 'H2', 'H3', 'H4')}
    obs = context['observation_count']
    recent = context['recent']
    common = context['missing_alternative'] and not context['established_positive']
    # H1: a full frozen window of receipt updates without a new kind,
    # outcome, or possible-change transition.
    h1 = common and obs >= WINDOW and len(context['last_marginal_flags']) >= WINDOW and all(
        not any(x.values()) for x in context['last_marginal_flags'][-WINDOW:])
    # H2: two natural zero-crossing signs, not a fitted negative cutoff.
    h2 = common and len(recent) == WINDOW and sum(recent) <= 0 and context['cumulative_sum'] <= 0
    # H3: a full window of successive pre-decision VARIABLE assessments.
    h3 = common and len(context['last_kinds']) >= WINDOW and all(
        k == 'VARIABLE_RELATION' for k in context['last_kinds'][-WINDOW:])
    # H4: minimal coverage opportunity once the existing empirical window is full.
    h4 = common and obs >= WINDOW
    return dict(H1=h1, H2=h2, H3=h3, H4=h4)


def r128():
    source = read(R128)
    result = {}
    marginal = {}
    signatures = []
    for run, record in source['runs'].items():
        decisions = record['decisions']
        rows = []
        changes = []
        past = []
        flags = []
        kinds = []
        observed_outcomes = set()
        for i, d in enumerate(decisions):
            assert d['index'] == i + 1 and d['state'] == 1 and d['action'] == 'HOLD'
            assessment = d['assessments']['HOLD']
            assert assessment['observation_count'] == i
            assert assessment['empirical_frequencies'] == frequencies(past)
            assert [v['consequence'] for v in assessment['recent_window']] == past[-WINDOW:]
            alternatives = {a: d['assessments'][a]['kind'] for a in d['admissible_actions'] if a != d['action']}
            missing = [a for a, kind in alternatives.items() if kind == 'UNSEEN']
            established_positive = any(a['relation_type'] == 'DETERMINISTIC' and
                a['kind'] == 'ESTABLISHED' and a['established_value']['consequence'] == 1
                for a in d['assessments'].values())
            assert all(d['assessments'][a]['observation_count'] == 0 for a in missing)
            c = dict(kind=assessment['kind'], observation_count=i, recent=past[-WINDOW:],
                     cumulative_sum=sum(past), missing_alternative=bool(missing),
                     established_positive=established_positive,
                     last_marginal_flags=flags, last_kinds=kinds)
            signal = predicates(c)
            consequence = d['consequence']
            assert d['next_state'] == 1
            next_assessment = decisions[i + 1]['assessments']['HOLD'] if i + 1 < len(decisions) else None
            after_kind = d['grounded_change']['after_kind']
            assert d['grounded_change']['before_kind'] == assessment['kind']
            assert d['grounded_change']['after_count'] == i + 1
            if next_assessment:
                assert next_assessment['kind'] == after_kind
            next_possible = next_assessment['possible_change'] is not None if next_assessment else False
            before_possible = assessment['possible_change'] is not None
            novel = consequence not in observed_outcomes
            flag = {'kind_changed': after_kind != assessment['kind'],
                    'new_outcome': novel, 'possible_change_changed': next_possible != before_possible}
            changes.append(dict(decision_id=d['decision_id'], receipt_sha256=d['receipt_sha256'],
                before_kind=assessment['kind'], after_kind=after_kind,
                before_observation_count=i, after_observation_count=i + 1,
                flags=flag, before_empirical_frequencies=frequencies(past),
                after_empirical_frequencies=frequencies(past + [consequence]),
                frequency_counts_changed=True,
                normalized_frequency_changed=(distribution(past) != distribution(past + [consequence])),
                recent_window_before=past[-WINDOW:],
                recent_window_after=(past + [consequence])[-WINDOW:],
                recent_window_changed=(past + [consequence])[-WINDOW:] != past[-WINDOW:],
                new_relation_created=assessment['kind'] == 'UNSEEN',
                no_classification_novelty_or_change_flag=not any(flag.values())))
            window = past[-WINDOW:]
            rows.append(dict(decision_id=d['decision_id'], decision_index=i + 1, state=d['state'],
                selected_action=d['action'], selected_relation_kind=assessment['kind'],
                selected_relation_type=assessment['relation_type'], observation_count=i,
                empirical_frequencies=assessment['empirical_frequencies'],
                recent_empirical_window=assessment['recent_window'],
                recent_window_counts=counts(window), recent_window_sum=sum(window),
                recent_window_mean=(sum(window) / len(window) if window else None),
                cumulative_counts=counts(past), cumulative_consequence=sum(past),
                consecutive_negative_observations=consecutive_negative(past),
                possible_change=before_possible, other_available_action_kinds=alternatives,
                unseen_alternatives=missing, unseen_alternative_count=len(missing),
                any_deterministic_established_positive=established_positive,
                existing_S_eligible=False,
                existing_S_ineligibility='selected relation is EMPIRICAL, not deterministic ESTABLISHED 0',
                candidate_signals_predecision=signal,
                realized_consequence=consequence,
                realized_next_state=d['next_state'],
                cumulative_consequence_after=sum(past) + consequence,
                receipt_sha256=d['receipt_sha256']))
            past.append(consequence)
            observed_outcomes.add(consequence)
            flags.append(flag)
            kinds.append(assessment['kind'])
        result[run] = rows
        marginal[run] = changes
        signatures.append([(r['state'], r['selected_action'], r['selected_relation_kind'],
                            r['realized_consequence'], r['unseen_alternative_count']) for r in rows])
    assert all(x == signatures[0] for x in signatures[1:])
    assert len({tuple(r['receipt_sha256'] for r in result[k]) for k in result}) == 3
    write('r128-empirical-trace.json', dict(source=str(R128.relative_to(ROOT)),
        source_sha256=digest(R128), run_count=3, unique_semantic_trace_count=1,
        independent_receipt_streams=3, window=WINDOW, runs=result))
    write('marginal-information-analysis.json', dict(source_sha256=digest(R128),
        definition='Classification novelty is kind/new outcome/possible-change transition. Every receipt still changes count and may refine frequency; no threshold makes that quantitatively negligible.',
        runs=marginal))
    return result


def schedule_crosscheck():
    all_reports = {}
    for path in sorted(SCHEDULES.glob('*/public.json')):
        data = read(path)
        # E is the empirical arm; D/M duplicate the registered consequences.
        rows = [r for r in data['rows'] if r['arm'] == 'E']
        relation_history = {}
        hits = {h: [] for h in ('H1', 'H2', 'H3', 'H4')}
        for row in rows:
            rel = row['relation']
            hist = relation_history.setdefault(rel, dict(flags=[], kinds=[]))
            before, after = row['E_before'], row['E_after']
            prior = [x['consequence'] for x in before['chronological_outcomes']]
            assert len(prior) == before['observation_count']
            c = dict(kind=before['kind'], observation_count=len(prior),
                recent=[x['consequence'] for x in before['recent_window']],
                cumulative_sum=sum(prior), missing_alternative=True,
                established_positive=False, last_marginal_flags=hist['flags'],
                last_kinds=hist['kinds'])
            signal = predicates(c)
            for h, yes in signal.items():
                if yes:
                    hits[h].append(dict(index=row['index'], relation=rel,
                        phase_analysis_only=row['phase'], kind=before['kind'],
                        observed_cumulative=sum(prior), recent_sum=sum(c['recent'])))
            observed = (row['realized']['next_state'], row['realized']['consequence'])
            flag = dict(kind_changed=before['kind'] != after['kind'],
                new_outcome=observed not in {(x['next_state'], x['consequence']) for x in before['chronological_outcomes']},
                possible_change_changed=bool(before['possible_change']) != bool(after['possible_change']))
            hist['flags'].append(flag)
            hist['kinds'].append(before['kind'])
        all_reports[path.parent.name] = dict(source=str(path.relative_to(ROOT)),
            source_sha256=digest(path), empirical_arm_rows=len(rows),
            missing_alternative_available='NOT_RECORDED_IN_RELATION_ONLY_SCHEDULE',
            signal_hits_conditional_on_unseen_alternative=hits,
            signal_counts={h: len(x) for h, x in hits.items()})
    write('empirical-crosscheck.json', dict(method='Frozen E-arm pre-observation states; phase used only after predicates as an analysis label. True alternative availability is absent, so these are signal-proxy hits, not proven policy triggers or false positives.',
        predicates='H1/H2/H3/H4 as in read-only analyzer; assumed missing alternative and no +1 only for conditional signal test.',
        schedules=all_reports))
    return all_reports


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    traces = r128()
    cross = schedule_crosscheck()
    for h in ('H1', 'H2', 'H3', 'H4'):
        x = [r['decision_index'] for r in traces['T1'] if r['candidate_signals_predecision'][h]]
        print(h, 'R128 first/count', min(x) if x else None, len(x),
              'B/C/F stationary proxy',*[cross[k]['signal_counts'][h] for k in
                ('B_STATIONARY_VARIABLE', 'C_RARE_ANOMALY', 'F_STATIONARY_FUTURE')])


if __name__ == '__main__':
    main()
