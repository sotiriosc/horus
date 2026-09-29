"""Independent read-only replay of protected E/C sessions into safe public reports."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json

from horus.core import digest
from horus.live import SessionStore, _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical, file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTIONS
from experiments.empirical_evidence_acquisition_proposal_v0.candidate import evaluate as evaluate_E
from .worker import PUBLIC, load_cases, preflight, arm_path, event_projection


def insist(value, message):
    if not value:
        raise RuntimeError('INVALID: ' + message)


def safe_private_hashes(path):
    names = ('authority.key','checkpoint.json','events.jsonl',
             'model-calls.private.jsonl','training-records.jsonl')
    files = {f'session/{name}':file_hash(path/'session'/name) for name in names}
    files['memory.sqlite3'] = file_hash(path/'memory.sqlite3')
    for extension in ('-wal','-shm'):
        extra = path / ('memory.sqlite3' + extension)
        if extra.exists():
            files[extra.name] = file_hash(extra)
    return files


def audit_arm(root, case, arm, spec):
    path = arm_path(root, case, arm)
    pair = json.loads((root/'cases'/case/'pair.json').read_text())
    with SessionStore(path/'session', True) as store, ModernMemory(path/'memory.sqlite3', False) as memory:
        admission = memory.reconcile(store)
        events = [envelope['record'] for envelope in store.records['events']]
        mem_rows = memory.rows()
        insist(admission['authenticated_events'] == len(events) == len(mem_rows),
               f'{case}/{arm} Memory admission count')
        visits = Counter()
        for sequence, (envelope, row) in enumerate(zip(store.records['events'], mem_rows), 1):
            event = envelope['record']; receipt = event['receipt']
            relation = f"{receipt['pre_state']}:{receipt['action']}"
            visits[relation] += 1
            schedule = spec['world_outcomes'].get(relation, [])
            insist(visits[relation] <= len(schedule), f'{case}/{arm} unregistered world visit')
            expected = schedule[visits[relation]-1]
            insist(envelope['sequence'] == sequence and
                   event['authorization_status'] == 'AUTHORIZED' and
                   event['receipt_provenance_sha256'] == digest(receipt) and
                   event['receipt_identity'] == list(row_identity(receipt)) and
                   row['event_identity'] == canonical(event['receipt_identity']) and
                   row['receipt_provenance_sha256'] == event['receipt_provenance_sha256'] and
                   row['event_stream_sequence'] == sequence and
                   (receipt['next_state'],receipt['realized_consequence']) ==
                   (expected['next_state'],expected['consequence']) and
                   row['realized_consequence'] == receipt['realized_consequence'] and
                   row['realized_next_state'] == receipt['next_state'],
                   f'{case}/{arm} original authorized receipt {sequence}')
        decisions = rows_of(store, 'AUTONOMOUS_AGENT_DECISION')
        insists = [x for x in store.records['calls'] if x['kind'] == 'ACTION_FROZEN']
        model = [x for x in store.records['calls'] if x['kind'] in (
            'REQUEST_INTENT','TRANSPORT_ATTEMPT_INTENT','TRANSPORT_ATTEMPT_RESULT')]
        insist(len(decisions) == len(insists) == 1 and not model and
               all(x['kind'] == 'ACTION_FROZEN' for x in store.records['calls']),
               f'{case}/{arm} model-free frozen action')
        d = decisions[0]
        execution_seq = d['event_stream_sequence']
        insist(1 <= execution_seq <= len(events), f'{case}/{arm} evaluation sequence')
        event = events[execution_seq-1]; receipt = event['receipt']
        expected_source = ('EMPIRICAL_EVIDENCE_ACQUISITION' if arm == 'E' and
                           spec['expected_E_target'] is not None else
                           'REGISTERED_EMPIRICAL_CONTINUATION')
        insist(d['selected_action'] == pair[arm]['action'] == receipt['action'] and
               d['decision_source'] == event['action_source'] == expected_source and
               d['state'] == receipt['pre_state'] and
               d['realized'] == dict(next_state=receipt['next_state'],
                                      consequence=receipt['realized_consequence']) and
               d['receipt_provenance_sha256'] == event['receipt_provenance_sha256'] and
               d['action_call_id'] is None and d['action_parse_status'] == 'NOT_CALLED' and
               insists[0]['record']['decision_id'] == d['decision_id'] and
               insists[0]['record']['case'] == case and
               insists[0]['record']['arm'] == arm and
               insists[0]['record']['selected_action'] == d['selected_action'] and
               insists[0]['record']['decision_source'] == d['decision_source'],
               f'{case}/{arm} frozen choice/receipt binding')
        for action in ACTIONS:
            relation = f"{d['state']}:{action}"
            insist(d['grounded_assessments_before'][action] ==
                   prior_state(mem_rows, relation, execution_seq),
                   f'{case}/{arm} pre-grounded replay {action}')
        relation = f"{d['state']}:{d['selected_action']}"
        insist(d['grounded_after'] == prior_state(mem_rows, relation, execution_seq+1),
               f'{case}/{arm} post-grounded replay')
        pre_history = [dict(x) for x in event_projection(store)[:execution_seq-1]]
        candidate = evaluate_E(d['state'], spec['candidate_input_order'],
                               d['grounded_assessments_before'], pre_history)
        insist(candidate == pair['candidate_before'] and
               pair[arm]['receipt_sha256'] == event['receipt_provenance_sha256'],
               f'{case}/{arm} candidate replay')
        if arm == 'E' and spec['expected_E_target'] is not None:
            target = d['grounded_assessments_before'][d['selected_action']]
            insist(target['kind'] == 'UNSEEN' and target['observation_count'] == 0 and
                   d['grounded_after']['kind'] != 'UNSEEN' and
                   d['grounded_after']['observation_count'] >= 1,
                   f'{case} missing relation acquisition')
            post_history = event_projection(store)[:execution_seq]
            post_state = receipt['next_state']
            post_assessments = {a:prior_state(mem_rows,f'{post_state}:{a}',execution_seq+1)
                                for a in ACTIONS}
            post = evaluate_E(post_state, spec['candidate_input_order'],
                              post_assessments, post_history)
            insist(not post['eligible'], f'{case} immediate retrigger')
        summary = dict(case=case, arm=arm, protected_receipts=len(events),
            memory_rows=len(mem_rows), original_receipt_replay='PASS',
            authorized_memory_replay='PASS', grounded_pre_post_replay='PASS',
            receipt_identity=event['receipt_identity'],
            receipt_sha256=event['receipt_provenance_sha256'],
            selected_action=d['selected_action'], decision_source=d['decision_source'],
            realized=d['realized'], pre_selected_kind=d['selected_grounded_before']['kind'],
            post_selected_kind=d['grounded_after']['kind'],
            post_selected_observation_count=d['grounded_after']['observation_count'],
            model_calls=0)
    summary['private_artifact_sha256'] = safe_private_hashes(path)
    return summary


def row_identity(receipt):
    return (receipt['source_identity'], receipt['event_id'],
            receipt['epoch'], receipt['transaction_id'])


def main(root):
    data = preflight()
    insist(json.loads((root/'evaluation-complete.json').read_text())['status'] == 'PASS',
           'campaign completion marker')
    public = {}; protected = {}; controls = {}; safety_triggers = 0
    for case in data['eligible_cases'] + data['control_cases']:
        spec = data['cases'][case]
        pair = json.loads((root/'cases'/case/'pair.json').read_text())
        insist(all(pair['matched_checks'].values()), f'{case} paired semantic prefix')
        arms = {arm:audit_arm(root,case,arm,spec) for arm in data['arms']}
        insist(arms['C']['receipt_sha256'] != arms['E']['receipt_sha256'] and
               pair['C_raw_provenance_sha256'] != pair['E_raw_provenance_sha256'],
               f'{case} independent protected provenance')
        expected = case in data['eligible_cases']
        candidate = pair['candidate_before']
        insist(candidate['eligible'] == expected and
               candidate['target_action'] == spec['expected_E_target'],
               f'{case} preregistered predicate/target')
        insist(pair['C']['action'] == 'HOLD' and
               pair['E']['action'] == (spec['expected_E_target'] if expected else 'HOLD'),
               f'{case} paired action endpoint')
        if expected:
            insist(pair['E']['source'] == 'EMPIRICAL_EVIDENCE_ACQUISITION' and
                   pair['E']['reason'] == 'DETERIORATED_EMPIRICAL_RELATION_WITH_MISSING_EVIDENCE' and
                   not pair['E']['candidate_after']['eligible'],
                   f'{case} trigger/reset endpoint')
        else:
            insist(pair['E']['source'] == 'REGISTERED_EMPIRICAL_CONTINUATION' and
                   pair['C']['action'] == pair['E']['action'] and
                   pair['C']['consequence'] == pair['E']['consequence'] and
                   pair['C']['next_state'] == pair['E']['next_state'],
                   f'{case} silent matched control')
            controls[case] = dict(status='PASS',exclusion=spec['primary_exclusion'],
                candidate=candidate,C_action=pair['C']['action'],
                E_action=pair['E']['action'],same_realized_outcome=True)
        safety_triggers += int(not expected and candidate['eligible'])
        public[case] = dict(case=case,expected_eligible=expected,
            matched_predecision_checks=pair['matched_checks'],
            semantic_predecision_sha256=pair['semantic_predecision_sha256'],
            candidate_before=candidate,
            C={k:arms['C'][k] for k in ('selected_action','decision_source','realized',
                'receipt_identity','receipt_sha256','pre_selected_kind',
                'post_selected_kind','post_selected_observation_count','model_calls')},
            E={k:arms['E'][k] for k in ('selected_action','decision_source','realized',
                'receipt_identity','receipt_sha256','pre_selected_kind',
                'post_selected_kind','post_selected_observation_count','model_calls')},
            immediate_E_eligible=pair['E']['candidate_after']['eligible'],
            fresh_prefix_recurrence=pair.get('fresh_prefix_recurrence'))
        protected[case] = arms
    insist(safety_triggers == 0, 'unsafe E trigger count')
    restarts = {}
    for case in ('E1','E6'):
        records = json.loads((root/'restart-three.json').read_text())[case]
        insist(all(v['status']=='PASS' and v['before_snapshot_equal'] and
                   v['suffix_before']==3 and v['suffix_after']==4 and
                   v['previous_pid'] != v['restart_pid'] and
                   v['target_after']==data['cases'][case]['expected_E_target']
                   for v in records.values()), f'{case} three-to-four restart')
        restarts[case] = {a:{k:v[k] for k in ('status','before_snapshot_equal',
            'suffix_before','suffix_after','target_after','fourth_receipt_sha256')}
            for a,v in records.items()}
    eligible_restart = json.loads((root/'restart-eligible.json').read_text())
    insist(all(v['status']=='PASS' and v['exact_snapshot_equal'] and
               v['previous_pid'] != v['restart_pid'] and
               v['target_action']==data['cases']['E4']['expected_E_target'] and
               v['suffix_count']==len(data['cases']['E4']['prefix'])
               for v in eligible_restart.values()), 'E4 eligible restart')
    restarts['E4'] = {a:{k:v[k] for k in ('status','exact_snapshot_equal',
        'empirical_kind','recent_window','recent_sum','cumulative_sum',
        'unseen_candidates','suffix_count','target_action')}
        for a,v in eligible_restart.items()}
    recurrence = public['E3']['fresh_prefix_recurrence']
    insist([x['eligible'] for x in recurrence] == [False,False,False,True] and
           recurrence[-1]['target_action']=='RETREAT', 'E3 fresh-prefix recurrence')
    predictions = {key:dict(status='PASS',evidence=detail) for key,detail in {
        'P1':'E1–E6 C continued HOLD and E selected frozen target at eligible boundary',
        'P2':'E1–E6 target relation was UNSEEN/count 0 before and observed/count >=1 after signed admission',
        'P3':'E1 positive, E2 neutral, E3 negative and E4 state-changing original receipts retained',
        'P4':'N4 benign stationary and N5 isolated anomaly full-context controls remained silent',
        'P5':'All 36 protected arms had zero action-model requests',
        'P6':'Every E acquisition immediately broke eligibility; E3 required a fresh four-receipt suffix',
        'P7':'E1/E6 three-to-four and E4 eligible-boundary fresh-process reconstructions passed',
    }.items()}
    _atomic_write(PUBLIC/'public-results.json', dict(status='PASS',
        mode='PROSPECTIVE_MODEL_FREE_PROTECTED_PAIRED_EVALUATION',
        eligible_case_count=6,control_case_count=12,model_calls=0,
        no_reward_improvement_claim=True, cases=public))
    _atomic_write(PUBLIC/'restart-audit.json', dict(status='PASS',
        fresh_process_reconstruction=True,no_mutable_exploration_counter=True,
        E3_fresh_prefix_recurrence=recurrence,cases=restarts))
    _atomic_write(PUBLIC/'prediction-audit.json', dict(status='PASS',predictions=predictions))
    _atomic_write(PUBLIC/'protected-path-audit.json', dict(status='PASS',
        source_candidate_sha256=data['frozen_candidate_sha256'],
        independent_protected_arms=36,model_calls=0,
        all_original_receipts_replayed=True,all_authorized_memory_replayed=True,
        all_grounded_pre_post_replayed=True,cases=protected))
    _atomic_write(PUBLIC/'control-audit.json', dict(status='PASS',
        control_count=12,unsafe_trigger_count=safety_triggers,controls=controls))
    print(json.dumps(dict(status='PASS',cases=len(public),
        eligible=6,controls=len(controls),model_calls=0,
        safety_triggers=safety_triggers),sort_keys=True))


if __name__ == '__main__':
    parser = ArgumentParser();parser.add_argument('--private-root',required=True,type=Path)
    args=parser.parse_args();main(args.private_root)
