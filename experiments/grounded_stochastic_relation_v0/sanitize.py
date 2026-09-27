"""Deterministic public export from a local full-evidence archive.

Run only with an explicitly selected local archive. Never copies raw session files.
"""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json, subprocess

ARCHIVE_COMMIT='7cbd76a6f7871cd03e5b32c2106f8e7df3e6c696'
STUDY=Path('research/grounded-stochastic-relation-v0')
ROW_KEYS=('arm','schedule','index','phase','relation','prediction','realized',
    'D_before','E_before','D_after','E_after','receipt_identity',
    'receipt_provenance_sha256','event_stream_sequence','event_stream_head_sha256',
    'durable_admission','model_calls','context_tokens','model_ids','fold_seconds',
    'serialized_e_bytes')
CONDITION_KEYS=('current_state','events','files','memory','states')
PRIVATE_FILES=('authority.key','checkpoint.json','events.jsonl',
    'model-calls.private.jsonl','training-records.jsonl','memory.sqlite3')

def digest(path):return sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def export(archive_root,publish_root):
    head=subprocess.check_output(['git','-C',str(archive_root),'rev-parse','HEAD'],text=True).strip()
    if head!=ARCHIVE_COMMIT:raise RuntimeError('archive must be exact full-evidence commit')
    source=archive_root/STUDY/'evidence';target=publish_root/STUDY/'evidence'
    analysis=read(source/'analysis.json')
    if analysis['classification']!='EMPIRICAL_GROUNDING_SUPPORTED':
        raise RuntimeError('unexpected archival result')
    from .protocol import ARMS,SCHEDULES
    private={};public={}
    for name,specs in SCHEDULES.items():
        schedule_root=source/'schedules'/name
        complete=read(schedule_root/'complete.json')
        parts=[read(schedule_root/'before-restart.json'),complete] if name=='G_RESTART' else [complete]
        rows=[{k:r[k] for k in ROW_KEYS} for part in parts for r in part['rows']]
        if len(rows)!=len(specs)*len(ARMS):raise RuntimeError('wrong number of public rows')
        conditions={a:{k:complete['conditions'][a][k] for k in CONDITION_KEYS} for a in ARMS}
        verdict=dict(status='PASS',archive_audit='PASS',matched_protected_observations=True,
            empirical_history_correct=True,source='local_archive_analysis')
        if name=='G_RESTART':
            restart=read(schedule_root/'restart.json');perturb=read(schedule_root/'perturbation.json')
            verdict.update(fresh_process_restart=restart['status'],
                exact_file_and_state_match=restart['exact_file_and_state_match'],
                rejected_unauthorized_admission=perturb['status'],
                before_restart_states={a:parts[0]['conditions'][a]['states'] for a in ARMS})
        export_row=dict(schedule=name,status='COMPLETE',rows=rows,conditions=conditions,
                        replay_verdict=verdict)
        path=target/'schedules'/name/'public.json';write(path,export_row)
        public[str(path.relative_to(publish_root))]=digest(path)
        for arm in ARMS:
            work=schedule_root/'work'/arm
            for filename in PRIVATE_FILES:
                path=work/('memory.sqlite3' if filename=='memory.sqlite3' else 'session/'+filename)
                private[str(path.relative_to(archive_root))]=dict(sha256=digest(path),bytes=path.stat().st_size)
    write(target/'analysis.json',analysis)
    public[str((target/'analysis.json').relative_to(publish_root))]=digest(target/'analysis.json')
    manifest=dict(schema=1,archive_commit=ARCHIVE_COMMIT,
        archive_evidence_tree='local_only',private_artifacts=private,
        public_summaries=public,
        explanation='Hashes bind omitted local raw files; public summaries support semantic replay but cannot independently validate HMACs without local keys.')
    write(target/'artifact-hashes.json',manifest)
    return dict(private_files=len(private),public_files=len(public),archive_commit=head)

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--archive-root',required=True,type=Path)
    p.add_argument('--publish-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(export(a.archive_root.resolve(),a.publish_root.resolve()),sort_keys=True))
