"""Model-free paired protected world/receipt/Memory campaign for frozen E."""
from argparse import ArgumentParser
from contextlib import ExitStack
from hashlib import sha256
from pathlib import Path
import json, os

from horus.core import digest
from horus.live import SessionStore, _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical, file_hash
from experiments.grounded_autonomous_agent_v0_2.worker import all_assessments
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTIONS, known_value
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as protected
from experiments.empirical_evidence_acquisition_proposal_v0 import candidate as frozen
from grounded_state import AuthenticatedMemory

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / 'research/empirical-evidence-acquisition-evaluation-v0'
CASES_PATH = PUBLIC / 'case-definitions.json'
MANIFEST_PATH = PUBLIC / 'source-manifest.json'
STUDY = 'EMPIRICAL_EVIDENCE_ACQUISITION_EVALUATION_V0'
FROZEN_SHA256 = 'fcef478a02beb69a1d29988c5ce12929ad2ba077591131e0dcd114e7ccab99b4'
PRIVATE_SESSION_FILES = ('authority.key', 'checkpoint.json', 'events.jsonl',
                         'model-calls.private.jsonl', 'training-records.jsonl')


def load_cases():
    data = json.loads(CASES_PATH.read_text())
    if (data['frozen_candidate_sha256'] != FROZEN_SHA256 or
            data['parent_proposal_commit'] !=
            'e2d3dcce6a292d32037aca769578dfb53833cb57' or
            len(data['eligible_cases']) != 6 or len(data['control_cases']) != 12):
        raise RuntimeError('frozen case definitions changed')
    return data


def preflight():
    source = ROOT / 'experiments/empirical_evidence_acquisition_proposal_v0/candidate.py'
    if sha256(source.read_bytes()).hexdigest() != FROZEN_SHA256:
        raise RuntimeError('INVALID: frozen candidate source SHA-256 mismatch')
    if (frozen.WINDOW != 4 or frozen.ACTIONS != tuple(ACTIONS) or
            frozen.EMPIRICAL_KINDS != ('EMPIRICALLY_STABLE', 'VARIABLE_RELATION') or
            frozen.SOURCE != 'EMPIRICAL_EVIDENCE_ACQUISITION' or
            frozen.TRIGGER_REASON != 'DETERIORATED_EMPIRICAL_RELATION_WITH_MISSING_EVIDENCE'):
        raise RuntimeError('INVALID: frozen candidate constant drift')
    manifest = json.loads(MANIFEST_PATH.read_text())
    for relative, expected in manifest['sha256'].items():
        if sha256((ROOT / relative).read_bytes()).hexdigest() != expected:
            raise RuntimeError('INVALID: source manifest mismatch: ' + relative)
    data = load_cases()
    protected.STUDY = STUDY
    protected.scenario_override = fixture_override
    return data


def fixture_override(case, state, action, visit, index):
    """External registered world schedule; never an input to E."""
    spec = load_cases()['cases'][case]
    outcomes = spec['world_outcomes'].get(f'{state}:{action}', [])
    if visit < 1 or visit > len(outcomes):
        raise RuntimeError(f'INVALID: unregistered world action {case} {state}:{action} visit {visit}')
    outcome = outcomes[visit - 1]
    return outcome['next_state'], outcome['consequence']


def event_projection(store):
    result = []
    for envelope in store.records['events']:
        event = envelope['record']
        receipt = event['receipt']
        if (event['authorization_status'] != 'AUTHORIZED' or
                digest(receipt) != event['receipt_provenance_sha256']):
            raise RuntimeError('INVALID: unauthenticated event in candidate history')
        result.append(dict(event_stream_sequence=envelope['sequence'],
            authorization_status=event['authorization_status'],
            event_identity=canonical(event['receipt_identity']),
            receipt_identity=event['receipt_identity'],
            receipt_sha256=event['receipt_provenance_sha256'],
            state=receipt['pre_state'], action=receipt['action'],
            next_state=receipt['next_state'], consequence=receipt['realized_consequence']))
    return result


def semantic_assessments(assessments):
    result = json.loads(json.dumps(assessments))
    for assessment in result.values():
        assessment.pop('recent_receipt_provenance', None)
        pending = assessment.get('possible_change')
        if isinstance(pending, dict):
            pending.pop('recent_support', None)
    return result


def context(store, memory, spec):
    memory.reconcile(store)
    state = store.checkpoint['current_state']
    assessments = all_assessments(AuthenticatedMemory(store, memory), state)
    history = event_projection(store)
    candidate = frozen.evaluate(state, spec['candidate_input_order'], assessments, history)
    return dict(state=state, assessments=assessments,
        semantic_assessments=semantic_assessments(assessments),
        semantic_history=[dict(state=x['state'], action=x['action'],
            next_state=x['next_state'], consequence=x['consequence'],
            authorization_status=x['authorization_status']) for x in history],
        candidate_set=sorted(spec['candidate_input_order']),
        candidate=candidate,
        raw_provenance_sha256=digest([(x['event_identity'], x['receipt_sha256']) for x in history]))


def snapshot(store, memory, path, spec):
    observed = context(store, memory, spec)
    return dict(files={name:file_hash(path/'session'/name) for name in PRIVATE_SESSION_FILES},
        memory=memory.checkpoint(), current_state=observed['state'],
        semantic_assessments=observed['semantic_assessments'],
        candidate=observed['candidate'], event_count=len(store.records['events']),
        call_count=len(store.records['calls']), training_count=len(store.records['training']))


def check_pair(c, e):
    checks = dict(current_state=c['state'] == e['state'],
        semantic_grounded_assessments=c['semantic_assessments'] == e['semantic_assessments'],
        authorized_event_projection=c['semantic_history'] == e['semantic_history'],
        admissible_candidate_set=c['candidate_set'] == e['candidate_set'],
        empirical_recent_window=c['assessments'].get('HOLD', {}).get('recent_window') ==
            e['assessments'].get('HOLD', {}).get('recent_window'),
        cumulative_empirical_sum=c['candidate']['cumulative_sum'] == e['candidate']['cumulative_sum'],
        unseen_alternatives=c['candidate']['unseen_candidates'] == e['candidate']['unseen_candidates'],
        E_eligibility=c['candidate'] == e['candidate'],
        independent_raw_provenance=c['raw_provenance_sha256'] != e['raw_provenance_sha256'])
    if not all(checks.values()):
        raise RuntimeError('INVALID: paired protected pre-decision contexts differ: ' + repr(checks))
    return checks


def execute_registered(store, memory, case, arm, action, source, index=0,
                       setup=True, reason=None, assessments=None):
    if action not in ACTIONS:
        raise RuntimeError('INVALID: unregistered action')
    if setup:
        row = protected.execute(store, memory, case, arm, index, action, source, setup=True)
        event = store.records['events'][-1]['record']
        return dict(state=event['receipt']['pre_state'], action=action,
            consequence=event['receipt']['realized_consequence'],
            next_state=event['receipt']['next_state'],
            receipt_identity=event['receipt_identity'],
            receipt_sha256=event['receipt_provenance_sha256'])
    if assessments is None:
        raise RuntimeError('INVALID: evaluation assessments missing')
    store.append('calls', 'ACTION_FROZEN', dict(decision_id='C:D01', case=case, arm=arm,
        selected_action=action, decision_source=source, reason=reason,
        action_call_id=None, model_calls=0))
    store.save(state=store.checkpoint['current_state'],
        next_transaction_id=store.checkpoint['next_transaction_id'])
    route=dict(route='REGISTERED_SCIENTIFIC', reason='MODEL_FREE_REGISTERED_ACTION',
        candidates=list(ACTIONS), known_values={a:known_value(assessments[a]) for a in ACTIONS})
    info=dict(status='NOT_CALLED', call_id=None, raw_output_sha256=None,
              context_tokens=0, output_tokens=0, latency_seconds=0)
    return protected.execute(store, memory, case, arm, 1, action, source,
        route, info, assessments, setup=False)


def arm_path(root, case, arm):
    return root / 'cases' / case / arm


def prepare(root):
    data = preflight()
    root.mkdir(parents=True, exist_ok=False)
    records = {}
    for case in data['eligible_cases'] + data['control_cases']:
        spec = data['cases'][case]
        records[case] = {}
        for arm in data['arms']:
            path = arm_path(root, case, arm)
            path.mkdir(parents=True, exist_ok=False)
            with SessionStore(path/'session', False) as store, ModernMemory(path/'memory.sqlite3', True) as memory:
                store.save(state=spec['initial_state'], next_transaction_id=1)
                rows = []
                for row in spec['setup']:
                    got = execute_registered(store, memory, case, arm, row['action'], 'REGISTERED_SETUP')
                    if {k:got[k] for k in ('state','action','consequence','next_state')} != {
                            'state':row['pre_state'], 'action':row['action'],
                            'consequence':row['consequence'], 'next_state':row['next_state']}:
                        raise RuntimeError('INVALID: setup schedule mismatch')
                    rows.append(got)
                prefix = spec['prefix'][:3] if spec['restart'] == 'AFTER_THREE' else spec['prefix']
                for row in prefix:
                    got = execute_registered(store, memory, case, arm, row['action'],
                                             'REGISTERED_EMPIRICAL_PREFIX')
                    if (got['state'],got['action'],got['consequence'],got['next_state']) != (
                            row['pre_state'],row['action'],row['consequence'],row['next_state']):
                        raise RuntimeError('INVALID: empirical prefix schedule mismatch')
                    rows.append(got)
                if spec['restart'] != 'AFTER_THREE':
                    for row in spec['interrupt']:
                        got = execute_registered(store, memory, case, arm, row['action'],
                                                 'REGISTERED_SUFFIX_INTERRUPT')
                        if (got['state'],got['action'],got['consequence'],got['next_state']) != (
                                row['pre_state'],row['action'],row['consequence'],row['next_state']):
                            raise RuntimeError('INVALID: suffix-interrupt schedule mismatch')
                        rows.append(got)
                snap = snapshot(store, memory, path, spec)
                if spec['restart'] == 'AFTER_THREE' and snap['candidate']['suffix_count'] != 3:
                    raise RuntimeError('INVALID: restart-three suffix not 3')
                if spec['restart'] == 'AFTER_ELIGIBLE' and not snap['candidate']['eligible']:
                    raise RuntimeError('INVALID: restart-eligible context not eligible')
                records[case][arm] = dict(pid=os.getpid(), snapshot=snap,
                                          protected_receipts=rows)
                _atomic_write(path/'prepared.json', records[case][arm])
        if spec['restart'] != 'AFTER_THREE':
            with ExitStack() as stack:
                contexts = {}
                for arm in data['arms']:
                    path = arm_path(root, case, arm)
                    store = stack.enter_context(SessionStore(path/'session', True))
                    memory = stack.enter_context(ModernMemory(path/'memory.sqlite3', False))
                    contexts[arm] = context(store, memory, spec)
                check_pair(contexts['C'], contexts['E'])
        print(json.dumps(dict(case=case, prepared_events=len(records[case]['C']['protected_receipts']),
            restart=spec['restart'])), flush=True)
    _atomic_write(root/'preparation.json', dict(status='PASS', pid=os.getpid(),
        case_count=len(records), cases={k:{a:v['snapshot']['event_count'] for a,v in arms.items()}
            for k,arms in records.items()}))


def restart_three(root):
    data = preflight()
    output = {}
    for case in ('E1', 'E6'):
        spec = data['cases'][case]
        output[case] = {}
        for arm in data['arms']:
            path = arm_path(root, case, arm)
            expected = json.loads((path/'prepared.json').read_text())
            if expected['pid'] == os.getpid():
                raise RuntimeError('INVALID: restart did not change process')
            with SessionStore(path/'session', True) as store, ModernMemory(path/'memory.sqlite3', False) as memory:
                before = snapshot(store, memory, path, spec)
                if before != expected['snapshot'] or before['candidate']['suffix_count'] != 3:
                    raise RuntimeError('INVALID: restart-three durable state/suffix mismatch')
                row = spec['prefix'][3]
                got = execute_registered(store, memory, case, arm, row['action'],
                                         'REGISTERED_EMPIRICAL_PREFIX_AFTER_RESTART')
                if (got['state'],got['action'],got['consequence'],got['next_state']) != (
                        row['pre_state'],row['action'],row['consequence'],row['next_state']):
                    raise RuntimeError('INVALID: fourth registered receipt mismatch')
                after = context(store, memory, spec)
                if not after['candidate']['eligible'] or after['candidate']['suffix_count'] != 4:
                    raise RuntimeError('INVALID: fourth receipt did not reconstruct eligibility')
                output[case][arm] = dict(status='PASS', previous_pid=expected['pid'],
                    restart_pid=os.getpid(), before_snapshot_equal=True,
                    suffix_before=3, suffix_after=4,
                    target_after=after['candidate']['target_action'],
                    fourth_receipt_identity=got['receipt_identity'],
                    fourth_receipt_sha256=got['receipt_sha256'])
                _atomic_write(path/'restart-three.json', output[case][arm])
        print(json.dumps(dict(case=case, restart_after_three='PASS')), flush=True)
    _atomic_write(root/'restart-three.json', output)


def restart_eligible(root):
    data = preflight()
    case = 'E4'; spec = data['cases'][case]
    output = {}
    for arm in data['arms']:
        path = arm_path(root, case, arm)
        expected = json.loads((path/'prepared.json').read_text())
        if expected['pid'] == os.getpid():
            raise RuntimeError('INVALID: eligible restart did not change process')
        with SessionStore(path/'session', True) as store, ModernMemory(path/'memory.sqlite3', False) as memory:
            actual = snapshot(store, memory, path, spec)
            if actual != expected['snapshot'] or not actual['candidate']['eligible']:
                raise RuntimeError('INVALID: eligible restart changed durable context')
            output[arm] = dict(status='PASS', previous_pid=expected['pid'],
                restart_pid=os.getpid(), exact_snapshot_equal=True,
                empirical_kind=actual['semantic_assessments']['HOLD']['kind'],
                recent_window=actual['semantic_assessments']['HOLD']['recent_window'],
                recent_sum=actual['candidate']['recent_sum'],
                cumulative_sum=actual['candidate']['cumulative_sum'],
                unseen_candidates=actual['candidate']['unseen_candidates'],
                suffix_count=actual['candidate']['suffix_count'],
                target_action=actual['candidate']['target_action'])
            _atomic_write(path/'restart-eligible.json', output[arm])
    _atomic_write(root/'restart-eligible.json', output)
    print(json.dumps(dict(case=case, restart_after_eligibility='PASS')), flush=True)


def evaluate_all(root):
    data = preflight()
    if not (root/'preparation.json').is_file() or not (root/'restart-three.json').is_file() or not (
            root/'restart-eligible.json').is_file():
        raise RuntimeError('INVALID: required preparation/restart stage missing')
    results = {}
    for case in data['eligible_cases'] + data['control_cases']:
        spec = data['cases'][case]
        if spec['restart'] == 'AFTER_THREE' and not (arm_path(root,case,'E')/'restart-three.json').is_file():
            raise RuntimeError('INVALID: fourth receipt/restart missing')
        if spec['restart'] == 'AFTER_ELIGIBLE' and not (arm_path(root,case,'E')/'restart-eligible.json').is_file():
            raise RuntimeError('INVALID: eligible restart missing')
        with ExitStack() as stack:
            live = {}
            for arm in data['arms']:
                path = arm_path(root, case, arm)
                store = stack.enter_context(SessionStore(path/'session', True))
                memory = stack.enter_context(ModernMemory(path/'memory.sqlite3', False))
                live[arm] = dict(store=store, memory=memory,
                                 before=context(store, memory, spec))
            paired = check_pair(live['C']['before'], live['E']['before'])
            expected = case in data['eligible_cases']
            candidate = live['E']['before']['candidate']
            if candidate['eligible'] != expected or candidate['target_action'] != spec['expected_E_target']:
                raise RuntimeError('INVALID: preregistered eligibility or target mismatch')
            actions = {'C':'HOLD', 'E':candidate['target_action'] if expected else 'HOLD'}
            pair = dict(case=case, matched_checks=paired,
                C_raw_provenance_sha256=live['C']['before']['raw_provenance_sha256'],
                E_raw_provenance_sha256=live['E']['before']['raw_provenance_sha256'],
                semantic_predecision_sha256=digest(dict(
                    state=live['C']['before']['state'],
                    history=live['C']['before']['semantic_history'],
                    assessments=live['C']['before']['semantic_assessments'],
                    candidate_set=live['C']['before']['candidate_set'])),
                candidate_before=candidate, actions=actions)
            for arm in data['arms']:
                store = live[arm]['store']; memory = live[arm]['memory']
                source = ('REGISTERED_EMPIRICAL_CONTINUATION' if arm == 'C' or not expected
                          else frozen.SOURCE)
                reason = ('REGISTERED_CONTINUATION_CONTROL' if source != frozen.SOURCE
                          else frozen.TRIGGER_REASON)
                row = execute_registered(store, memory, case, arm, actions[arm], source,
                    index=1, setup=False, reason=reason,
                    assessments=live[arm]['before']['assessments'])
                after = context(store, memory, spec)
                if source == frozen.SOURCE:
                    target_before = live[arm]['before']['assessments'][actions[arm]]
                    if target_before['kind'] != 'UNSEEN' or target_before['observation_count'] != 0:
                        raise RuntimeError('INVALID: E target was not truly unseen')
                    if row['grounded_after']['kind'] == 'UNSEEN' or row['grounded_after']['observation_count'] < 1:
                        raise RuntimeError('INVALID: E target did not acquire authenticated evidence')
                    if after['candidate']['eligible']:
                        raise RuntimeError('INVALID: immediate E retrigger after acquisition')
                pair[arm] = dict(action=actions[arm], source=source, reason=reason,
                    pre_selected_assessment=live[arm]['before']['assessments'][actions[arm]],
                    post_selected_assessment=row['grounded_after'],
                    consequence=row['realized']['consequence'],
                    next_state=row['realized']['next_state'],
                    receipt_identity=row['receipt_identity'],
                    receipt_sha256=row['receipt_provenance_sha256'],
                    event_identity=row['event_identity'],
                    event_stream_sequence=row['event_stream_sequence'],
                    candidate_after=after['candidate'],
                    model_calls=sum(x['kind']=='REQUEST_INTENT' for x in store.records['calls']))
            if expected and pair['E']['consequence'] != spec['E_target_outcome']['consequence']:
                raise RuntimeError('INVALID: frozen E target outcome mismatch')
            if pair['C']['consequence'] != spec['C_boundary_outcome']['consequence']:
                raise RuntimeError('INVALID: frozen control outcome mismatch')
            if expected and pair['E']['next_state'] != spec['E_target_outcome']['next_state']:
                raise RuntimeError('INVALID: frozen E next state mismatch')
            if case == 'E3':
                recurrence = []
                store = live['E']['store']; memory = live['E']['memory']
                for count, consequence in enumerate(spec['fresh_recurrence_consequences'], 1):
                    got = execute_registered(store, memory, case, 'E', 'HOLD',
                        'REGISTERED_FRESH_EMPIRICAL_SUFFIX')
                    if got['consequence'] != consequence:
                        raise RuntimeError('INVALID: recurrence schedule mismatch')
                    observed = context(store, memory, spec)['candidate']
                    if observed['suffix_count'] != count or observed['eligible'] != (count == 4):
                        raise RuntimeError('INVALID: fresh-prefix recurrence boundary')
                    recurrence.append(dict(fresh_suffix_count=count, eligible=observed['eligible'],
                        target_action=observed['target_action'], consequence=consequence,
                        receipt_sha256=got['receipt_sha256']))
                if recurrence[-1]['target_action'] != 'RETREAT':
                    raise RuntimeError('INVALID: second unseen relation unavailable after fresh suffix')
                pair['fresh_prefix_recurrence'] = recurrence
            _atomic_write(root/'cases'/case/'pair.json', pair)
            results[case] = dict(status='PASS', E_trigger=expected,
                C_action=pair['C']['action'], E_action=pair['E']['action'],
                C_consequence=pair['C']['consequence'],
                E_consequence=pair['E']['consequence'])
            print(json.dumps(dict(case=case, E_trigger=expected,
                C=pair['C']['action'], E=pair['E']['action'],
                C_consequence=pair['C']['consequence'],
                E_consequence=pair['E']['consequence'])), flush=True)
    _atomic_write(root/'evaluation-complete.json', dict(status='PASS',
        case_count=len(results), model_calls=0, results=results))


def main():
    parser = ArgumentParser()
    parser.add_argument('command', choices=('preflight','prepare','restart-three',
                                            'restart-eligible','evaluate'))
    parser.add_argument('--private-root', type=Path)
    args = parser.parse_args()
    if args.command == 'preflight':
        preflight(); print(json.dumps(dict(status='PASS', candidate_sha256=FROZEN_SHA256)))
        return
    if args.private_root is None:
        parser.error('--private-root required')
    try:
        if args.command == 'prepare': prepare(args.private_root)
        elif args.command == 'restart-three': restart_three(args.private_root)
        elif args.command == 'restart-eligible': restart_eligible(args.private_root)
        else: evaluate_all(args.private_root)
    except Exception as exc:
        if args.private_root.exists():
            _atomic_write(args.private_root/'stop.json',
                dict(status='INVALID', stage=args.command, error=repr(exc)))
        raise


if __name__ == '__main__': main()
