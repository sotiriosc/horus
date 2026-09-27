"""Audit the frozen receipts and report bounded epistemic outcomes."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical
from horus.live import SessionStore, _atomic_write
from experiments.grounded_uncertainty_state_v0.uncertainty import fold as d_fold
from .empirical import fold as e_fold
from .protocol import ARMS,SCHEDULES,RESTART_AFTER

def analyze(output):
    manifest=json.loads((Path(__file__).resolve().parents[2]/'research/grounded-stochastic-relation-v0/source-manifest.json').read_text())
    if sha256(canonical(SCHEDULES).encode()).hexdigest()!=manifest['schedule_sha256']:
        raise RuntimeError('INVALID: schedule changed')
    for name,expected in manifest['sha256'].items():
        if sha256((Path(__file__).resolve().parents[2]/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('INVALID: frozen source changed: '+name)
    reports={};all_rows=[];storage=0;memory_storage=0;fold_seconds=0;model_calls=0;context_tokens=0;false_certainty=0
    for name,specs in SCHEDULES.items():
        root=output/'schedules'/name
        complete=json.loads((root/'complete.json').read_text())
        if complete['status']!='COMPLETE':raise RuntimeError('INVALID: incomplete schedule')
        by_arm={a:[] for a in ARMS};memory_by_arm={}
        for a in ARMS:
            path=root/'work'/a
            with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
                memory.reconcile(store)
                if len(store.records['events'])!=len(specs):raise RuntimeError('INVALID: missing events')
                memory_by_arm[a]={r:memory.rows(r) for r in ('1:HOLD','2:HOLD','1:ADVANCE','2:RETREAT')}
                for relation in ('1:HOLD','2:HOLD'):
                    rows=memory_by_arm[a][relation]
                    if d_fold(rows)!=complete['conditions'][a]['states'][relation]['D'] or e_fold(rows)!=complete['conditions'][a]['states'][relation]['E']:
                        raise RuntimeError('INVALID: stored state differs from authenticated history')
                for envelope in store.records['training']:
                    row=envelope['record']
                    if envelope['kind']=='STOCHASTIC_RELATION_SCORED_EVENT':by_arm[a].append(row)
                if len(by_arm[a])!=len(specs):raise RuntimeError('INVALID: scored rows missing')
            storage+=sum(p.stat().st_size for p in path.rglob('*') if p.is_file())
            memory_storage+=(path/'memory.sqlite3').stat().st_size
        for i,spec in enumerate(specs):
            values=[by_arm[a][i]['realized'] for a in ARMS]
            if not all(v==values[0] for v in values):raise RuntimeError('INVALID: unmatched arm receipt')
            if spec['consequence'] is not None and values[0]['consequence']!=spec['consequence']:
                raise RuntimeError('INVALID: outcome differs from registration')
        for a in ARMS:
            seen={}
            for row in by_arm[a]:
                relation=row['relation'];seen.setdefault(relation,[])
                if row['D_before']!=d_fold(seen[relation]) or row['E_before']!=e_fold(seen[relation]):
                    raise RuntimeError('INVALID: pre-event fold mismatch')
                # Durable rows supply exact receipt provenance; observed values are independently checked.
                seen[relation]=memory_by_arm[a][relation][:row['E_after']['observation_count']]
                if row['D_after']!=d_fold(seen[relation]) or row['E_after']!=e_fold(seen[relation]):
                    raise RuntimeError('INVALID: post-event fold mismatch')
                observed=[dict(next_state=x['realized_next_state'],consequence=x['realized_consequence']) for x in seen[relation]]
                if row['E_after']['chronological_outcomes']!=observed or row['E_after']['observation_count']!=len(observed):
                    raise RuntimeError('INVALID: empirical history differs from observable receipts')
                if [p['identity'] for p in row['E_after']['receipt_provenance']]!=[x['event_identity'] for x in seen[relation]]:
                    raise RuntimeError('INVALID: empirical provenance differs from observable receipts')
                if row['E_after']['recent_window']!=observed[-4:]:
                    raise RuntimeError('INVALID: empirical recent window differs from observable receipts')
                if row['E_after']['kind']=='EMPIRICALLY_STABLE' and len(row['E_after']['segment_counts'])!=1:
                    false_certainty+=1
                fold_seconds+=row['fold_seconds'];model_calls+=row['model_calls'];context_tokens+=row['context_tokens']
        e_rows=[r for r in by_arm['E'] if r['relation']=='1:HOLD']
        d_rows=[r for r in by_arm['D'] if r['relation']=='1:HOLD']
        alarms=[r['index'] for r in e_rows if r['E_after']['kind']=='POSSIBLE_REGIME_CHANGE']
        d_unresolved=[r['index'] for r in d_rows if r['D_after']['kind']=='UNRESOLVED_CHANGE']
        false_alarms=[i for i in alarms if specs[i]['phase'] in ('stationary','ambiguous')]
        shifts=[i for i,s in enumerate(specs) if s['phase']=='shift' and (i==0 or specs[i-1]['phase']!='shift')]
        restores=[i for i,s in enumerate(specs) if s['phase']=='restoration' and (i==0 or specs[i-1]['phase']!='restoration')]
        latencies={str(start):next((i-start+1 for i in alarms if i>=start),None) for start in shifts+restores}
        e_counts=Counter(r['E_after']['kind'] for r in e_rows)
        d_counts=Counter(r['D_after']['kind'] for r in d_rows)
        points={a:dict(correct=sum(r['prediction']==r['realized'] for r in by_arm[a] if r['relation']=='1:HOLD' and (a!='M' or r['model_calls'])),
            n=sum(1 for r in by_arm[a] if r['relation']=='1:HOLD' and (a!='M' or r['model_calls']))) for a in ARMS}
        reports[name]=dict(events=len(specs),alarms=alarms,false_alarms=false_alarms,
            D_unresolved=d_unresolved,shift_and_restoration_latency=latencies,
            E_state_counts=dict(e_counts),D_state_counts=dict(d_counts),points=points,
            final_E=e_rows[-1]['E_after'],model_calls=sum(r['model_calls'] for r in by_arm['M']),
            context_tokens=sum(r['context_tokens'] for r in by_arm['M']),
            serialized_e_bytes_max=max(r['serialized_e_bytes'] for r in e_rows))
        all_rows.extend(e_rows)
    f1=reports['F_STATIONARY_FUTURE'];f2=reports['F_SHIFT_FUTURE']
    with SessionStore(output/'schedules'/'F_STATIONARY_FUTURE'/'work'/'E'/'session',True) as s1,SessionStore(output/'schedules'/'F_SHIFT_FUTURE'/'work'/'E'/'session',True) as s2:
        prefix1=[(x['record']['receipt']['pre_state'],x['record']['receipt']['action'],x['record']['receipt']['realized_consequence']) for x in s1.records['events'][:10]]
        prefix2=[(x['record']['receipt']['pre_state'],x['record']['receipt']['action'],x['record']['receipt']['realized_consequence']) for x in s2.records['events'][:10]]
    if prefix1!=prefix2:raise RuntimeError('INVALID: F observed prefixes differ')
    restart=json.loads((output/'schedules'/'G_RESTART'/'restart.json').read_text())
    perturb=json.loads((output/'schedules'/'G_RESTART'/'perturbation.json').read_text())
    if restart['status']!='PASS' or perturb['status']!='PASS':raise RuntimeError('INVALID: restart or perturbation')
    false_alarms=sum(len(r['false_alarms']) for r in reports.values())
    latencies=[v for r in reports.values() for v in r['shift_and_restoration_latency'].values()]
    supported=(false_alarms==0 and all(v is not None and v<=4 for v in latencies)
        and not reports['C_RARE_ANOMALY']['alarms'] and prefix1==prefix2
        and f1['alarms']==[] and f2['alarms'] and restart['exact_file_and_state_match'])
    d_sufficient=all(not reports[n]['D_unresolved'] for n in ('B_STATIONARY_VARIABLE','C_RARE_ANOMALY'))
    classification=('EMPIRICAL_GROUNDING_SUPPORTED' if supported and not d_sufficient else
        'DETERMINISTIC_STATE_SUFFICIENT' if supported and d_sufficient else
        'CHANGE_VARIABILITY_NOT_IDENTIFIABLE' if any(v is None for v in latencies) else 'MIXED')
    result=dict(status='COMPLETE',classification=classification,reports=reports,
        aggregate=dict(false_change_alarms=false_alarms,missed_shift_or_restoration=sum(v is None for v in latencies),
            latencies_receipts=latencies,explicit_uncertainty_frequency=sum(r['E_after']['kind'] in ('VARIABLE_RELATION','POSSIBLE_REGIME_CHANGE') for r in all_rows)/len(all_rows),
            false_certainty=false_certainty,empirical_state_correctness='PASS',storage_bytes=storage,
            storage_bytes_per_authorized_event=storage/(sum(len(s) for s in SCHEDULES.values())*len(ARMS)),
            memory_sqlite_bytes=memory_storage,
            mechanical_fold_seconds=fold_seconds,model_calls=model_calls,context_tokens=context_tokens,
            serialized_e_bytes_max=max(r['serialized_e_bytes_max'] for r in reports.values())),
        information_boundary=dict(status='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH',
            observed_prefix=prefix1,shared_prefix_length=10),restart_integrity=restart['status'],
        perturbation=perturb)
    _atomic_write(output/'analysis.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();print(json.dumps(analyze(a.output),indent=2,sort_keys=True))
