"""Verify public history and frozen postmortem evidence; never read private evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

P=Path(__file__).resolve().parent
ROOT=P.parents[1]
BASE='f4becaf11220f853a87e741fa84009bd0de715b2'
CODEBOOK='36a2f7f4b498707cbb71b26e68cc25226918982a'
IMPLEMENTATION='b8ddfb4d05ad1745b1c78bcdd08c464c0c5dfe84'
DETERMINISTIC='7b8ba59444df26ef4e4fdb40dab678f6d031e337'
B=ROOT/'research/blind-diagnostic-generalization-v0'
R=B/'replacement-r2'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=read(P/'preservation-baseline.json')
    entries=git('ls-tree','-r','-z',BASE).split(b'\0');count=0
    batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for entry in entries:
        if not entry:continue
        meta,name=entry.split(b'\t');mode,kind,oid=meta.split();assert kind==b'blob'
        batch.stdin.write(oid+b'\n');batch.stdin.flush();header=batch.stdout.readline().split()
        raw=batch.stdout.read(int(header[2]));assert batch.stdout.read(1)==b'\n'
        assert (ROOT/name.decode()).read_bytes()==raw,name.decode();count+=1
    batch.stdin.close();assert batch.wait()==0 and count==baseline['base_tracked_file_count']
    for ref,want in baseline['protected_public_refs'].items():assert git('rev-parse','refs/heads/'+ref).decode().strip()==want,ref
    for milestone in [baseline['method_freeze'],baseline['case_freeze'],BASE,CODEBOOK,IMPLEMENTATION,DETERMINISTIC]:
        assert subprocess.run(['git','merge-base','--is-ancestor',milestone,'HEAD'],cwd=ROOT).returncode==0
    assert git('rev-parse',CODEBOOK+'^').decode().strip()==BASE
    assert git('rev-parse',IMPLEMENTATION+'^').decode().strip()==CODEBOOK
    assert git('rev-parse',DETERMINISTIC+'^').decode().strip()==IMPLEMENTATION
    assert not git('ls-tree','-r','--name-only',CODEBOOK,'--',str((P/'deterministic').relative_to(ROOT))).strip()
    assert not git('ls-tree','-r','--name-only',DETERMINISTIC,'--',str((P/'qualitative-illustrations.md').relative_to(ROOT))).strip()
    frozen_names=git('ls-tree','-r','--name-only',DETERMINISTIC,'--',str(P.relative_to(ROOT))).decode().splitlines()
    for name in frozen_names:assert (ROOT/name).read_bytes()==git('show',DETERMINISTIC+':'+name),name
    manifest=read(P/'deterministic/deterministic-manifest.json')
    for name,want in manifest['files'].items():assert sha(P/'deterministic'/name)==want
    replay=read(P/'deterministic-replay.json')
    for name,want in replay['sha256'].items():assert sha(P/'deterministic'/name)==want
    raw=read(R/'raw-freeze.json')
    files={str(f.relative_to(R/'raw')):f for f in (R/'raw').rglob('*') if f.is_file()}
    assert set(files)==set(raw['sha256'])
    for name,want in raw['sha256'].items():assert sha(files[name])==want
    scores=read(R/'scores.json');rows=[json.loads(line) for line in (P/'deterministic/rendering-postmortem.jsonl').read_text().splitlines()]
    assert len(rows)==80 and {r['render_id'] for r in rows}==set(scores['renderings'])
    for r in rows:assert r['original_scorer_credit']==scores['renderings'][r['render_id']]
    sem=read(P/'deterministic/semantic-postmortem.json');assert len(sem)==20
    for r in sem:assert r['original_scorer_credit']==scores['semantic_cases'][r['semantic_case_id']]
    pair=read(P/'deterministic/matched-pair-postmortem.json');assert [p['original_scorer_credit'] for p in pair]==scores['matched_pairs']
    assert sha(R/'scores.json')=='961dbaec40add7673aba15328efe9fd3f8d8eae5cd676b7da0c9043dc52f1883'
    aggregate=read(P/'deterministic/aggregate-postmortem.json')
    assert aggregate['original_primary_classification']==scores['classification']=='BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0'
    assert aggregate['original_measured']==scores['measured'] and aggregate['original_mandatory_gates']==scores['gates']
    for name,want in read(P/'input-manifest.json')['files'].items():assert sha(ROOT/name)==want
    for line in git('diff','--name-status',BASE,'HEAD').decode().splitlines():
        kind,name=line.split('\t');assert kind=='A' and name.startswith(str(P.relative_to(ROOT))+'/')
    excluded=0
    for ref in git('for-each-ref','--format=%(refname)','refs/heads').decode().splitlines():
        if 'private-archive' in ref:
            assert subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT).returncode==1;excluded+=1
    report=dict(status='PASS',base_commit=BASE,base_files_byte_identical=count,public_input_hashes_verified=257,protected_public_refs=baseline['protected_public_refs'],
        method_freeze=baseline['method_freeze'],case_freeze=baseline['case_freeze'],codebook_freeze=CODEBOOK,implementation_freeze=IMPLEMENTATION,deterministic_freeze=DETERMINISTIC,
        codebook_before_aggregate_commit=True,deterministic_commit_before_qualitative_review=True,frozen_analysis_files_unchanged=len(frozen_names),r2_raw_files_hash_verified=len(files),
        r2_score_sha256=sha(R/'scores.json'),r2_primary_classification=scores['classification'],r2_replacement_id='R2',
        original_credit_copies_verified=dict(renderings=80,semantic_cases=20,matched_pairs=6),exact_deterministic_replay=replay['byte_identical'],
        private_archive_heads_excluded=excluded,private_data_accessed=False,private_data_basis='Analysis reads only the 257 public input files and analysis artifacts; no private directory, envelope, reasoning, log or Memory database opened. Private-archive checks inspect ref ancestry only.',
        no_new_execution=aggregate['no_new_execution'],scientific_score_invocations=0,active_architecture='grounded authority -> S -> E -> ordinary model (unchanged)',
        preservation_basis='All inherited tracked bytes, frozen commits, ten protected refs and raw/score hashes verified; isolated analysis operation history has no Horus or model execution, Memory writes, receipts, policy/threshold changes, training, architecture work or improvement proposals.')
    target=P/'preservation-verification.json';value=(json.dumps(report,indent=2)+'\n').encode()
    if target.exists():assert target.read_bytes()==value
    else:target.write_bytes(value)
    print(json.dumps({k:report[k] for k in ['status','base_files_byte_identical','r2_raw_files_hash_verified','original_credit_copies_verified','private_archive_heads_excluded','scientific_score_invocations']}))
if __name__=='__main__':main()
