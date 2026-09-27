import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from horus.live import SessionStore
from horus.grounded_exploration import initialize_grounded_exploration_registry
from .storage import ModernMemory
from .transport import generate, RULE_HASH
from .atomic import prepare, commit_pair, publish_snapshot
from .harness import forecast_batch, new_controller
from .worker import _open, _close, run_stage


class FakeClient:
    model_id = 'synthetic-test-only'
    def __init__(self, specialist=None, failures=()):
        self.failures = list(failures); self.requests = []
        self.horus_model_identity = dict(artifact_sha256='test', specialist_id=specialist)
        self.tokenizer = lambda *_a, **_k: SimpleNamespace(input_ids=[1])
    def generate(self, request):
        self.requests.append(json.dumps(request).encode())
        if self.failures:
            failure = self.failures.pop(0)
            if failure:
                return dict(raw_output=None, transport_error=failure)
        value = {'consequence': 0}
        if 'next_state' in request['system']: value['next_state'] = 1
        return dict(raw_output=json.dumps(value), transport_error=None)


def clients(condition, registry=None):
    from .protocol import G2_ADAPTER, G3_ADAPTER
    from .storage import file_hash
    pool = {}
    for key in ('G2',) if condition == 'M' else ('G2', 'G3'):
        c = FakeClient(key)
        c.horus_model_identity['artifact_sha256'] = file_hash(G2_ADAPTER if key == 'G2' else G3_ADAPTER)
        pool[key] = c
    return FakeClient(), pool, None


def initialize(root):
    for arm in ('M', 'MH'):
        path = root / 'work' / arm; path.mkdir(parents=True)
        with SessionStore(path / 'session', False): pass
        with ModernMemory(path / 'memory.sqlite3', True): pass
        if arm == 'MH': initialize_grounded_exploration_registry(path / 'registry')
        (root / arm).symlink_to(Path('current') / arm, target_is_directory=True)


class ProtocolTests(unittest.TestCase):
    def test_repair_bytes_and_bound(self):
        for failures, expected in ((['TimeoutError'], 2),
                (['TimeoutError', 'TimeoutError'], 2), (['ValueError'], 1),
                (['ROLE_VIOLATION'], 1), ([], 1)):
            with TemporaryDirectory() as d, SessionStore(Path(d) / 'session', False) as store:
                c = FakeClient(failures=failures)
                generate(c, {'system': 'test', 'prompt': 'frozen'}, store, 'test')
                self.assertEqual(len(c.requests), expected)
                self.assertEqual(len(set(c.requests)), 1)
                attempts = [r['record'] for r in store.records['calls'] if r['kind'] == 'TRANSPORT_ATTEMPT_INTENT']
                self.assertEqual(len({r['attempt_id'] for r in attempts}), expected)
                self.assertTrue(all(r['repair_rule_sha256'] == RULE_HASH for r in attempts))

    def test_no_execution_if_either_preparation_invalid(self):
        for bad in ('M', 'MH'):
            calls = []
            with self.assertRaisesRegex(RuntimeError, 'PAIR_PREPARATION_FAILED'):
                commit_pair({}, {}, {a: dict(all_valid=a != bad) for a in ('M','MH')},
                            {'event':1}, lambda **kw: calls.append(kw))
            self.assertEqual(calls, [])

    @patch('experiments.modern_memory_vs_horus_v0_1.worker.load_clients', clients)
    def test_full_synthetic_schedule_restart_and_atomic_visibility(self):
        with TemporaryDirectory() as d:
            root = Path(d); initialize(root)
            for stage in ('A1', 'A2', 'B'): run_stage(root, stage)
            pair = json.loads((root / 'current/pair.json').read_text())
            self.assertEqual(pair['count'], 12)
            for arm in ('M', 'MH'):
                with SessionStore(root / arm / 'session', True) as store:
                    self.assertEqual(sum(r['record']['stage']=='A' for r in store.records['events']), 12)
            snapshots = list((root / 'pairs').iterdir())
            self.assertEqual(len(snapshots), 16)
            for snap in snapshots:
                counts = []
                for arm in ('M', 'MH'):
                    with SessionStore(snap / arm / 'session', True) as store:
                        counts.append(sum(r['record']['stage']=='A' for r in store.records['events']))
                self.assertEqual(*counts)

    @patch('experiments.modern_memory_vs_horus_v0_1.worker.load_clients', clients)
    def test_failed_sibling_retains_calls_and_no_event(self):
        with TemporaryDirectory() as d:
            root=Path(d); initialize(root)
            contexts={a:_open(root,a) for a in ('M','MH')}
            try:
                batches={}; controllers={}
                contexts['MH'][5].failures=['TimeoutError','TimeoutError']
                for arm, context in contexts.items():
                    controllers[arm]=new_controller(context[1],'A')
                    batches[arm]=prepare(context,controllers[arm],'A:01',forecast_batch)
                self.assertTrue(batches['M']['all_valid'])
                self.assertFalse(batches['MH']['all_valid'])
                self.assertEqual(len(contexts['M'][5].requests),3)
                self.assertEqual(len(contexts['MH'][5].requests),4)
                for context in contexts.values():
                    self.assertEqual(context[1].records['events'],[])
                    self.assertEqual(context[2].rows(),[])
            finally:
                for c in contexts.values(): _close(*c[:5])

    @patch('experiments.modern_memory_vs_horus_v0_1.worker.load_clients', clients)
    def test_commit_interruption_keeps_previous_pair_visible(self):
        from .harness import publish
        with TemporaryDirectory() as d:
            root=Path(d); initialize(root)
            contexts={a:_open(root,a) for a in ('M','MH')}
            try:
                publish_snapshot(root,contexts,'initial',0)
                batches={}; controllers={}
                for arm,c in contexts.items():
                    controllers[arm]=new_controller(c[1],'A')
                    batches[arm]=prepare(c,controllers[arm],'A:01',forecast_batch)
                def fail_second(**kwargs):
                    if kwargs['condition']=='MH': raise OSError('injected commit interruption')
                    return publish(**kwargs)
                with self.assertRaises(OSError):
                    commit_pair(contexts,controllers,batches,dict(event=1,forced_action='HOLD'),fail_second)
                self.assertEqual((root/'current').readlink(),Path('pairs/initial'))
                for arm in ('M','MH'):
                    with SessionStore(root/arm/'session',True) as store:
                        self.assertEqual(len(store.records['events']),0)
            finally:
                for c in contexts.values(): _close(*c[:5])

if __name__ == '__main__': unittest.main()
