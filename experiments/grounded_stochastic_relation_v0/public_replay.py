"""Semantic replay of sanitized receipt summaries; HMAC validation needs local archive."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
from experiments.modern_memory_vs_horus_v0.storage import canonical
from experiments.grounded_uncertainty_state_v0.uncertainty import fold as d_fold
from .empirical import fold as e_fold
from .protocol import ARMS,SCHEDULES

def read(p):return json.loads(p.read_text())
def digest(p):return sha256(p.read_bytes()).hexdigest()

def replay(root):
    evidence=root/'research/grounded-stochastic-relation-v0/evidence'
    hashes=read(evidence/'artifact-hashes.json');analysis=read(evidence/'analysis.json')
    source=read(root/'research/grounded-stochastic-relation-v0/source-manifest.json')
    for path,expected in source['sha256'].items():
        if digest(root/path)!=expected:raise RuntimeError('frozen source mismatch: '+path)
    if sha256(canonical(SCHEDULES).encode()).hexdigest()!=source['schedule_sha256']:
        raise RuntimeError('frozen schedule mismatch')
    for path,expected in hashes['public_summaries'].items():
        if digest(root/path)!=expected:raise RuntimeError('public summary hash mismatch: '+path)
    verdicts={};total=0;first10=[]
    for name,specs in SCHEDULES.items():
        public=read(evidence/'schedules'/name/'public.json')
        if public['status']!='COMPLETE':raise RuntimeError('incomplete summary')
        arm_rows={a:[] for a in ARMS}
        for row in public['rows']:arm_rows[row['arm']].append(row)
        if any(len(arm_rows[a])!=len(specs) for a in ARMS):raise RuntimeError('missing public rows')
        for arm in ARMS:
            histories={};rows=arm_rows[arm]
            for index,row in enumerate(rows):
                spec=specs[index];relation=row['relation']
                if row['index']!=index or row['phase']!=spec['phase'] or relation!=f"{spec['state']}:{spec['action']}":
                    raise RuntimeError('registered schedule mismatch')
                if spec['consequence'] is not None and row['realized']['consequence']!=spec['consequence']:
                    raise RuntimeError('registered outcome mismatch')
                history=histories.setdefault(relation,[])
                if row['D_before']!=d_fold(history) or row['E_before']!=e_fold(history):
                    raise RuntimeError('pre-event public fold mismatch')
                admission=row['durable_admission']
                if admission['relation']!=relation or admission['event_stream_head_sha256']!=row['event_stream_head_sha256'] or admission['event_identity']!=row['E_after']['receipt_provenance'][-1]['identity']:
                    raise RuntimeError('public event provenance mismatch')
                history.append(dict(realized_next_state=row['realized']['next_state'],
                    realized_consequence=row['realized']['consequence'],authorization_status='AUTHORIZED',
                    event_identity=admission['event_identity'],
                    receipt_provenance_sha256=row['receipt_provenance_sha256'],
                    event_stream_sequence=row['event_stream_sequence']))
                if row['D_after']!=d_fold(history) or row['E_after']!=e_fold(history):
                    raise RuntimeError('post-event public fold mismatch')
            for relation in ('1:HOLD','2:HOLD'):
                condition=public['conditions'][arm]['states'][relation]
                if condition['D']!=d_fold(histories.get(relation,[])) or condition['E']!=e_fold(histories.get(relation,[])):
                    raise RuntimeError('final public state mismatch')
        for index in range(len(specs)):
            values=[(arm_rows[a][index]['relation'],arm_rows[a][index]['realized']) for a in ARMS]
            if values[1:]!=values[:-1]:raise RuntimeError('unmatched public arm outcomes')
        if name.startswith('F_'):
            first10.append([(r['relation'],r['realized']) for r in arm_rows['E'][:10]])
        expected=analysis['reports'][name]
        alarms=[r['index'] for r in arm_rows['E'] if r['relation']=='1:HOLD' and r['E_after']['kind']=='POSSIBLE_REGIME_CHANGE']
        if alarms!=expected['alarms']:raise RuntimeError('public warning mismatch')
        verdicts[name]=dict(status='PASS',events=len(specs),matched_arms=True,
            deterministic_and_empirical_folds=True,possible_change_events=alarms)
        total+=len(specs)*len(ARMS)
    if first10[0]!=first10[1]:raise RuntimeError('ambiguous prefix mismatch')
    if analysis['information_boundary']['status']!='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH':
        raise RuntimeError('information boundary missing')
    return dict(status='PASS',public_semantic_replay=True,authenticated_raw_replay='LOCAL_ARCHIVE_ONLY',
        classification=analysis['classification'],authorized_event_summaries=total,
        information_boundary='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH',schedules=verdicts,
        model_calls_executed=0)

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd())
    a=p.parse_args();print(json.dumps(replay(a.root.resolve()),indent=2,sort_keys=True))
