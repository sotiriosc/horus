"""Single visibility point for two independently authenticated simulated arms.

Only `current` is committed experience. `work` is private transaction workspace;
readers resolve current once, never read workspace or resolve it once per arm.
No claim of atomic transactions over real-world irreversible actuators is made.
"""
import copy
import json
import os
import pickle
from pathlib import Path
import shutil
import time
from horus.core import digest
from horus.live import SessionStore, _atomic_write
from .storage import ModernMemory


def flush(store):
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])


def experience(context, controller):
    _, store, memory, routing, explorer, *_ = context
    core = controller._active.framework.inner
    return copy.deepcopy(dict(events=store.records['events'], memory=memory.rows(),
        routing=None if routing is None else (routing.records, routing.state),
        explorer=explorer, completed=store.checkpoint['completed_steps'],
        attempted=store.checkpoint['attempted_decisions'],
        state=core.map.current.state, next_transaction_id=core.next_transaction_id,
        core_memory=core.memory.records, world=pickle.dumps(controller._active.world),
        pending=core.pending, receipt=controller._source.reader().current()))


def identities(store):
    return [dict(event=e['record']['study_event'], action=e['record']['receipt']['action'],
                 regime=e['record']['external_regime_version'])
            for e in store.records['events'] if e['record']['stage'] == 'A']


def verify_pair(contexts, count):
    identities_by_arm = {}
    session_ids, sources = [], []
    for arm, context in contexts.items():
        _, store, memory, routing, *_ = context
        memory.reconcile(store)
        identities_by_arm[arm] = identities(store)
        if len(identities_by_arm[arm]) != count:
            raise RuntimeError('INVALID: Stage-A count mismatch')
        if routing is not None and len(routing.records) != len(store.records['events']):
            raise RuntimeError('INVALID: routing count mismatch')
        session_ids.append(store.checkpoint['session_id'])
        sources.append({e['record']['receipt']['source_identity'] for e in store.records['events']})
    if identities_by_arm['M'] != identities_by_arm['MH']:
        raise RuntimeError('INVALID: scheduled observation identity mismatch')
    if session_ids[0] == session_ids[1] or sources[0] & sources[1]:
        raise RuntimeError('INVALID: cross-arm state')
    return dict(status='PASS', count=count, scheduled_observations=identities_by_arm['M'],
                distinct_sessions=True, disjoint_receipt_sources=True)


def fsync_tree(root):
    for path in root.rglob('*'):
        if path.is_file() and not path.is_symlink():
            with path.open('rb') as stream: os.fsync(stream.fileno())
    for path in [*reversed([p for p in root.rglob('*') if p.is_dir()]), root]:
        fd = os.open(path, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)


def publish_snapshot(output, contexts, name, count):
    check = verify_pair(contexts, count)
    destination = output / 'pairs' / name
    if destination.exists(): raise RuntimeError('snapshot already exists')
    destination.mkdir(parents=True)
    for arm, context in contexts.items():
        root, store, memory, routing, explorer, *_ = context
        flush(store)
        memory.checkpoint()
        _atomic_write(root / 'explorer-state.json', explorer)
        shutil.copytree(root, destination / arm, symlinks=True,
                        ignore=shutil.ignore_patterns('.lock'))
        with SessionStore(destination / arm / 'session', True) as snap_store, \
             ModernMemory(destination / arm / 'memory.sqlite3', False) as snap_memory:
            snap_memory.reconcile(snap_store)
    _atomic_write(destination / 'pair.json', check)
    fsync_tree(destination)
    temporary = output / 'current.next'
    temporary.symlink_to(Path('pairs') / name, target_is_directory=True)
    os.replace(temporary, output / 'current')
    fd = os.open(output, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return check


def prepare(context, controller, opportunity, forecast, perturb=False):
    root, store, memory, routing, explorer, joint, specialists = context
    started = time.perf_counter()
    before = experience(context, controller)
    batch = forecast(condition=root.name, store=store, memory=memory,
        controller=controller, joint_client=joint, specialists=specialists,
        routing_store=routing, explorer_state=explorer,
        opportunity=opportunity, perturb=perturb)
    if experience(context, controller) != before:
        raise RuntimeError('INVALID: inference preparation changed experience')
    store.append('calls', 'PREPARATION_GUARD', dict(opportunity=opportunity,
        experience_unchanged=True, all_valid=batch['all_valid'],
        decision_abstained=batch['decision']['abstained'],
        seconds=time.perf_counter() - started,
        behavioral_outcome=('BEHAVIORAL_ABSTENTION' if batch['all_valid'] and batch['decision']['abstained'] else None),
        outcome=('READY' if batch['all_valid'] else 'MODEL_OUTPUT_INVALID')))
    flush(store)
    return batch


def commit_pair(contexts, controllers, batches, spec, publisher):
    # Complete validation precedes even the first external execution.
    if set(batches) != {'M', 'MH'} or not all(b['all_valid'] for b in batches.values()):
        raise RuntimeError('PAIR_PREPARATION_FAILED')
    verify_pair(contexts, spec['event'] - 1)
    result = {}
    for arm in ('M', 'MH'):
        root, store, memory, routing, explorer, *_ = contexts[arm]
        result[arm] = publisher(condition=arm, stage='A', event_number=spec['event'],
            controller=controllers[arm], store=store, memory=memory, batch=batches[arm],
            action=spec['forced_action'], routing_store=routing, explorer_state=explorer)
    verify_pair(contexts, spec['event'])
    return result
