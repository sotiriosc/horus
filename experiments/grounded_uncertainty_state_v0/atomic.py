"""One committed visibility point for four receipt-local simulated arms."""
import copy
import json
import os
import pickle
from pathlib import Path
import shutil
import time
from horus.live import SessionStore, _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from .protocol import ARMS


def flush(store):
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])


def experience(context,controller):
    store=context['store'];memory=context['memory'];core=controller._active.framework.inner
    return copy.deepcopy(dict(events=store.records['events'],memory=memory.rows(),
        completed=store.checkpoint['completed_steps'],
        attempted=store.checkpoint['attempted_decisions'],
        state=core.map.current.state,next_transaction_id=core.next_transaction_id,
        core_memory=core.memory.records,world=pickle.dumps(controller._active.world),
        pending=core.pending,receipt=controller._source.reader().current()))


def scheduled_rows(store):
    return [dict(schedule=e['record']['schedule'],event=e['record']['study_event'],
        observation_id=e['record']['scheduled_observation_id'],
        phase=e['record']['phase'],regime=e['record']['external_regime_version'],
        action=e['record']['receipt']['action'],
        pre_state=e['record']['receipt']['pre_state'],
        next_state=e['record']['receipt']['next_state'],
        consequence=e['record']['receipt']['realized_consequence'])
        for e in store.records['events']]


def verify_triple(contexts,prefix):
    histories=[];sessions=[];sources=[]
    for arm in ARMS:
        ctx=contexts[arm];store=ctx['store'];memory=ctx['memory']
        memory.reconcile(store)
        history=scheduled_rows(store)
        if len(history)!=len(prefix):raise RuntimeError('INVALID: event-count mismatch')
        for row,spec in zip(history,prefix):
            for key,expected in [('schedule',spec['schedule']),('event',spec['event']),
                ('observation_id',spec['observation_id']),('phase',spec['phase']),
                ('regime',spec['regime']),('action',spec['action'])]:
                if row[key]!=expected:raise RuntimeError(f'INVALID: scheduled {key} mismatch')
        histories.append(history);sessions.append(store.checkpoint['session_id'])
        sources.append({e['record']['receipt']['source_identity'] for e in store.records['events']})
    if not all(history==histories[0] for history in histories):
        raise RuntimeError('INVALID: matched realized observations differ')
    if len(set(sessions))!=len(ARMS) or any(sources[i]&sources[j] for i in range(len(ARMS)) for j in range(i)):
        raise RuntimeError('INVALID: cross-arm receipt source')
    return dict(status='PASS',count=len(prefix),matched_observations=histories[0],
                distinct_sessions=True,disjoint_receipt_sources=True)


def publish_snapshot(schedule_root,contexts,name,prefix):
    check=verify_triple(contexts,prefix)
    destination=schedule_root/'triples'/name
    if destination.exists():raise RuntimeError('snapshot already exists')
    destination.mkdir(parents=True)
    for arm in ARMS:
        ctx=contexts[arm];root=ctx['root'];store=ctx['store'];memory=ctx['memory']
        flush(store);memory.checkpoint()
        shutil.copytree(root,destination/arm,symlinks=True,
                        ignore=shutil.ignore_patterns('.lock'))
        with SessionStore(destination/arm/'session',True) as observed, \
             ModernMemory(destination/arm/'memory.sqlite3',False) as observed_memory:
            observed_memory.reconcile(observed)
    _atomic_write(destination/'triple.json',check)
    for path in destination.rglob('*'):
        if path.is_file() and not path.is_symlink():
            with path.open('rb') as stream:os.fsync(stream.fileno())
    for directory in [p for p in destination.rglob('*') if p.is_dir()]+[destination]:
        fd=os.open(directory,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    temporary=schedule_root/'current.next'
    temporary.symlink_to(Path('triples')/name,target_is_directory=True)
    os.replace(temporary,schedule_root/'current')
    fd=os.open(schedule_root,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
    return check


def guarded_prepare(context,controller,forecast):
    start=time.perf_counter();before=experience(context,controller)
    batch=forecast()
    if experience(context,controller)!=before:
        raise RuntimeError('INVALID: preparation mutated authenticated experience')
    context['store'].append('calls','PREPARATION_GUARD',dict(
        arm=context['arm'],experience_unchanged=True,all_valid=batch['all_valid'],
        seconds=time.perf_counter()-start))
    flush(context['store'])
    return batch
