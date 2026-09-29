"""Read-only Phase 3 replay on preserved public records; no world or model imports."""
from hashlib import sha256
from pathlib import Path
import json

from .candidate import evaluate, empirical_component

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/empirical-evidence-acquisition-proposal-v0'
R128 = ROOT / 'research/qwen3-r128-autonomous-grounded-agent-v0/public-result.json'
DIAGNOSIS = ROOT / 'research/empirical-information-stagnation-diagnosis-v0/r128-empirical-trace.json'
DIAGNOSIS_CROSSCHECK = ROOT / 'research/empirical-information-stagnation-diagnosis-v0/empirical-crosscheck.json'
SCHEDULES = ROOT / 'research/grounded-stochastic-relation-v0/evidence/schedules'
CANDIDATE = Path(__file__).with_name('candidate.py')


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write(name, data):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')


def public_verified_projection(decision):
    """Projection of a receipt already replay-verified by the R128 campaign.

    This does not independently authenticate the private signed event stream.
    """
    assert decision['parse_status'] == 'VALID'
    assert decision['receipt_sha256'] and decision['receipt_identity'] and decision['event_identity']
    return dict(event_stream_sequence=decision['index'],
                authorization_status='AUTHORIZED',
                event_identity=decision['event_identity'],
                receipt_identity=decision['receipt_identity'],
                receipt_sha256=decision['receipt_sha256'],
                state=decision['state'], action=decision['action'],
                next_state=decision['next_state'], consequence=decision['consequence'])


def replay_r128():
    data = read(R128)
    assert data['campaign_integrity'] == 'PASS'
    assert data['verdict']['authority_replay'] == 'PASS'
    assert data['verdict']['restart'] == 'PASS'
    diagnosis = read(DIAGNOSIS)
    result = {}
    for run, record in sorted(data['runs'].items()):
        assert record['metrics']['receipt_memory_replay'] == 'PASS'
        prior = []
        rows = []
        for decision, diagnosed in zip(record['decisions'], diagnosis['runs'][run]):
            assert decision['decision_id'] == diagnosed['decision_id']
            assert decision['index'] == len(prior) + 1
            verdict = evaluate(decision['state'], decision['admissible_actions'],
                               decision['assessments'], prior)
            assert verdict['eligible'] == diagnosed['candidate_signals_predecision']['H2']
            rows.append(dict(decision_id=decision['decision_id'],
                             predecision_authenticated_receipts=len(prior),
                             historical_action=decision['action'],
                             selected_empirical_kind=decision['assessments'][decision['action']]['kind'],
                             candidate=verdict))
            prior.append(public_verified_projection(decision))
        hits = [row['decision_id'] for row in rows if row['candidate']['eligible']]
        assert hits == [f'{run}:D{i:02d}' for i in (19, 20, 21, 22, 23)]
        result[run] = dict(first_would_trigger=hits[0],
                           all_would_trigger_boundaries=hits,
                           would_trigger_count=len(hits),
                           historical_decisions=rows)
    write('r128-readonly-replay.json', dict(status='PASS',
        mode='READ_ONLY_UNCHANGED_HISTORICAL_TRAJECTORY',
        candidate_source_sha256=digest(CANDIDATE),
        source=str(R128.relative_to(ROOT)), source_sha256=digest(R128),
        diagnosis_source_sha256=digest(DIAGNOSIS),
        source_campaign_authority_replay='PASS',
        source_campaign_receipt_memory_replay='PASS',
        source_campaign_restart='PASS',
        no_hypothetical_continuation=True,
        note='Later would-trigger boundaries follow unchanged historical HOLD choices; an actual acquisition would break that suffix.',
        runs=result))
    return result


def crosscheck():
    prior = read(DIAGNOSIS_CROSSCHECK)['schedules']
    schedules = {}
    for path in sorted(SCHEDULES.glob('*/public.json')):
        source = read(path)
        rows = [row for row in source['rows'] if row['arm'] == 'E']
        hits = []
        for row in rows:
            # Only already-observed pre-boundary outcomes enter E's predicate.
            before = row['E_before']
            result = empirical_component(before, before['chronological_outcomes'])
            if result['signal']:
                hits.append(dict(index=row['index'], relation=row['relation'],
                    label='CONDITIONAL_EMPIRICAL_SIGNAL',
                    kind=before['kind'], recent_sum=result['recent_sum'],
                    cumulative_sum=result['cumulative_sum'],
                    phase_analysis_only=row['phase']))
        old_hits = prior[path.parent.name]['signal_hits_conditional_on_unseen_alternative']['H2']
        assert [(x['index'], x['relation']) for x in hits] == [
            (x['index'], x['relation']) for x in old_hits]
        schedules[path.parent.name] = dict(source=str(path.relative_to(ROOT)),
            source_sha256=digest(path), empirical_arm_pre_observation_rows=len(rows),
            signal_count=len(hits), signals=hits,
            alternative_availability='NOT_RECORDED',
            full_policy_trigger_status='NOT_TESTABLE_FROM_RELATION_ONLY_TRACE')
    write('empirical-readonly-crosscheck.json', dict(status='PASS',
        label='CONDITIONAL_EMPIRICAL_SIGNAL',
        candidate_source_sha256=digest(CANDIDATE),
        diagnosis_crosscheck_sha256=digest(DIAGNOSIS_CROSSCHECK),
        method='E-arm pre-observation empirical component only; registered phase is an analysis label and is never passed to the candidate.',
        no_hidden_unexecuted_outcomes_used=True,
        schedules=schedules))
    return schedules


def main():
    r = replay_r128()
    s = crosscheck()
    print('R128', {run: (x['first_would_trigger'], x['would_trigger_count']) for run, x in r.items()})
    print('empirical-only signals', {name: x['signal_count'] for name, x in s.items()})


if __name__ == '__main__':
    main()
