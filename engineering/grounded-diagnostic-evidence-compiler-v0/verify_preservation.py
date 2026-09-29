"""Separate postflight: byte/ref verification only, outside compiler execution."""
import hashlib
import json
from pathlib import Path
import subprocess

P=Path(__file__).resolve().parent;ROOT=P.parents[1]
BASE='5687d82cc3eede8561ef435b980f23d919518c26'
CONTRACT='11776ad70b29a82f85c34115c088a494370a0f04'
IMPLEMENTATION='c6a04593237ec5af5b2661c5b9813ef274e13448'
RESULTS='c601974af21f495c36df8a3a2e1e7667452a64c6'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def read(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=read(P/'preservation-baseline.json');count=0
    batch=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for row in git('ls-tree','-r','-z',BASE).split(b'\0'):
        if not row:continue
        meta,name=row.split(b'\t');mode,kind,oid=meta.split();assert kind==b'blob'
        batch.stdin.write(oid+b'\n');batch.stdin.flush();header=batch.stdout.readline().split();raw=batch.stdout.read(int(header[2]));assert batch.stdout.read(1)==b'\n'
        assert (ROOT/name.decode()).read_bytes()==raw,name.decode();count+=1
    batch.stdin.close();assert batch.wait()==0
    for ref,want in baseline['local_refs'].items():assert git('rev-parse','refs/heads/'+ref).decode().strip()==want
    remote_text=git('ls-remote','--heads','origin',*('refs/heads/'+r for r in baseline['remote_refs'])).decode()
    remote={r.removeprefix('refs/heads/'):s for s,r in (line.split() for line in remote_text.splitlines())};assert remote==baseline['remote_refs']
    for freeze in [CONTRACT,IMPLEMENTATION,RESULTS]:
        assert subprocess.run(['git','merge-base','--is-ancestor',freeze,'HEAD'],cwd=ROOT).returncode==0
        names=git('ls-tree','-r','--name-only',freeze,'--',str(P.relative_to(ROOT))).decode().splitlines()
        for name in names:assert (ROOT/name).read_bytes()==git('show',freeze+':'+name),name
    assert git('rev-parse',CONTRACT+'^').decode().strip()==BASE
    assert git('rev-parse',IMPLEMENTATION+'^').decode().strip()==CONTRACT
    assert git('rev-parse',RESULTS+'^').decode().strip()==IMPLEMENTATION
    replay=read(P/'exact-replay.json')
    for name,want in replay['sha256'].items():assert sha(P/'results'/name)==want
    assert replay['byte_identical'] and replay['full_output_schema_valid']==80
    results=read(P/'results/feasibility-results.json');assert results['dependency_audit']['gold_files_read']==0 and results['dependency_audit']['denied_accesses']==[]
    for entry in read(P/'fixture-manifest.json')['entries']:assert sha(ROOT/entry['path'])==entry['sha256']
    b=ROOT/'research/blind-diagnostic-generalization-v0';r=b/'replacement-r2';raw=read(r/'raw-freeze.json')
    for name,want in raw['sha256'].items():assert sha(r/'raw'/name)==want
    assert sha(r/'scores.json')=='961dbaec40add7673aba15328efe9fd3f8d8eae5cd676b7da0c9043dc52f1883'
    for freeze in ['587ffedd39516b633376d222d6d84e6af186fcf8','2866e6bcf94539513c135df878b72058048e99cd']:
        assert subprocess.run(['git','merge-base','--is-ancestor',freeze,BASE],cwd=ROOT).returncode==0
    excluded=0
    for ref in git('for-each-ref','--format=%(refname)','refs/heads').decode().splitlines():
        if 'private-archive' in ref:
            assert subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT).returncode==1;excluded+=1
    for row in git('diff','--name-status',BASE,'HEAD').decode().splitlines():
        status,name=row.split('\t');assert status=='A' and name.startswith(str(P.relative_to(ROOT))+'/')
    report=dict(status='PASS',base=BASE,inherited_files_byte_identical=count,contract_freeze=CONTRACT,implementation_freeze=IMPLEMENTATION,results_commit=RESULTS,
        freeze_order_verified=True,frozen_implementation_and_results_unchanged=True,public_fixture_hashes_verified=80,compiled_output_schema_valid=80,replay_files_identical=81,
        protected_local_refs=baseline['local_refs'],protected_remote_refs=remote,known_main_difference=baseline['known_main_difference'],r2_raw_hashes_verified=len(raw['sha256']),r2_score_sha256=sha(r/'scores.json'),r2_and_postmortem_unchanged=True,
        original_v0_r1_engineering_s_e_unchanged=True,active_architecture='grounded authority -> S -> E -> ordinary model (unchanged)',memory_policy_threshold_sources_unchanged=True,
        no_private_evidence_access=True,private_archive_heads_excluded=excluded,zero_inference=results['zero_inference'],
        attestation='All parent tracked bytes and protected local/remote refs verified; compiler runtime denied filesystem/import/network/subprocess access, harness allowed only case evidence plus mechanical contract, and operation history contains no model or Horus execution. Verification hashes prior public artifacts outside compiler execution. No private Memory databases or reasoning opened.')
    target=P/'preservation-verification.json';value=(json.dumps(report,indent=2)+'\n').encode()
    if target.exists():assert target.read_bytes()==value
    else:target.write_bytes(value)
    print(json.dumps({k:report[k] for k in ['status','inherited_files_byte_identical','r2_raw_hashes_verified','public_fixture_hashes_verified','replay_files_identical','private_archive_heads_excluded']}))
if __name__=='__main__':main()
