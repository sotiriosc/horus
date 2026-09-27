"""Post hoc, read-only audit of stopped v0.1 sessions; emits sanitized JSON."""
from collections import Counter
from argparse import ArgumentParser
from pathlib import Path
import json

from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_1.worker import rows_of
from experiments.grounded_autonomous_agent_v0_1.protocol import ACTIONS, RUNS, REVIEW_EVERY

PARSER = ArgumentParser()
PARSER.add_argument('--private-root', required=True, type=Path)
PARSER.add_argument('--output', required=True, type=Path)
ARGS = PARSER.parse_args()
ROOT = ARGS.private_root
OUT = ARGS.output

def audit_run(run):
    path = ROOT / 'runs' / run
    with SessionStore(path / 'session', True) as store, ModernMemory(path / 'memory.sqlite3', False) as memory:
        memory.reconcile(store)
        rows = memory.rows()
        decisions = rows_of(store, 'AUTONOMOUS_AGENT_DECISION')
        reviews = rows_of(store, 'SELF_REVIEW_NON_AUTHORITATIVE')
        events = [e['record'] for e in store.records['events']]
        assert len(events) == len(decisions) == len(rows)
        for i, (d, e) in enumerate(zip(decisions, events), 1):
            receipt = e['receipt']
            assert d['decision_id'] == f'{run}:D{i:02d}' and d['index'] == i
            assert d['action_parse_status'] == 'VALID' and d['selected_action'] in ACTIONS
            assert e['decision_index'] == i and e['authorization_status'] == 'AUTHORIZED'
            assert receipt['pre_state'] == d['state'] and receipt['action'] == d['selected_action']
            assert d['realized'] == {'next_state': receipt['next_state'], 'consequence': receipt['realized_consequence']}
            assert d['event_stream_sequence'] == i and d['receipt_provenance_sha256'] == e['receipt_provenance_sha256']
            for action in ACTIONS:
                assert d['grounded_assessments_before'][action] == prior_state(rows, f'{d["state"]}:{action}', i)
            assert d['grounded_after'] == prior_state(rows, f'{d["state"]}:{d["selected_action"]}', i + 1)
        for n, r in enumerate(reviews, 1):
            assert r['after_decision'] == n * REVIEW_EVERY
            assert r['reviewed_decisions'] == [f'{run}:D{i:02d}' for i in range((n-1)*REVIEW_EVERY+1, n*REVIEW_EVERY+1)]
            assert r['non_authoritative'] and r['no_memory_or_state_change']
            assert r['review_status'] in ('VALID_SELF_REVIEW','INVALID_SELF_REVIEW')
            if r['review_status'] == 'INVALID_SELF_REVIEW': assert r['proposal_status'] is None
        parsed_calls = [x['record'] for x in store.records['calls'] if x['kind'] == 'PARSED']
        attempts = [c for c in parsed_calls if c['role'] == 'DECISION']
        invalid = [c for c in attempts if c['action_parse_status'] == 'INVALID']
        assert len(invalid) == 2 and all(c['call_id'].startswith(f'{run}:{len(decisions)+1}:DECISION:') for c in invalid)
        assert all(c['action_parse_status'] == 'VALID' for c in attempts[:-2])
        stop = json.loads((path/'stop.json').read_text())
        assert stop['status'] == 'INVALID' and 'no valid allowed action after 2 attempts' in stop['error']
        private_files = {str(p.relative_to(path)): file_hash(p) for p in sorted(path.rglob('*')) if p.is_file() and p.name != '.lock'}
        return {
            'run': run, 'status': 'INVALID', 'stop_before_decision': len(decisions)+1,
            'stop_reason': 'two invalid action parses; no world execution for stopped decision',
            'authenticated_receipts': len(events), 'decision_records': len(decisions),
            'grounded_memory_rows': len(rows), 'signed_stream_replay': 'PASS',
            'receipt_and_grounded_replay': 'PASS',
            'selected_actions': dict(Counter(d['selected_action'] for d in decisions)),
            'total_realized_consequence_partial': sum(d['realized']['consequence'] for d in decisions),
            'descriptive_status_counts': dict(Counter(d['descriptive_status'] for d in decisions)),
            'review_status_counts': dict(Counter(r['review_status'] for r in reviews)),
            'review_audit': [{'review_id': r['review_id'], 'status': r['review_status'],
                              'proposal_status': r['proposal_status'],
                              'no_memory_or_state_change': r['no_memory_or_state_change'],
                              'raw_output_sha256': r['raw_model_output_sha256']} for r in reviews],
            'invalid_action_attempts': [{'call_id': c['call_id'], 'parse_error': c['error'],
                                         'raw_output_sha256': c['raw_output_sha256']} for c in invalid],
            'decisions': [{'decision_id': d['decision_id'], 'state': d['state'],
                           'selected_action': d['selected_action'], 'action_parse_status': d['action_parse_status'],
                           'descriptive_status': d['descriptive_status'],
                           'realized': d['realized'], 'selected_grounded_before': d['selected_grounded_before'],
                           'grounded_state_change': d['grounded_state_change'],
                           'receipt_provenance_sha256': d['receipt_provenance_sha256'],
                           'raw_model_output_sha256': d['raw_model_output_sha256']} for d in decisions],
            'private_files_sha256': private_files,
        }

result = {'campaign': 'grounded-autonomous-agent-v0.1', 'status': 'INVALID',
          'valid_full_runs': 0, 'planned_full_runs': 3,
          'interpretation': 'No valid complete campaign inference; partial trajectories are protocol diagnostics only.',
          'runs': {run: audit_run(run) for run in RUNS}}
OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(json.dumps({'status': result['status'], 'runs': {
    k: {x: v[x] for x in ('stop_before_decision','authenticated_receipts','signed_stream_replay','receipt_and_grounded_replay','descriptive_status_counts','review_status_counts')}
    for k,v in result['runs'].items()}}, indent=2, sort_keys=True))
