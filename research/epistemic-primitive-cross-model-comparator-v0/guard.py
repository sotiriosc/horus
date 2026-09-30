"""Read-only preservation and pinned runtime guards. No gold/scorer import."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
BASE='2cfcf8097c99d13df2156dde47409af0f65cb42a'
PRIVATE=Path('/tmp/horus-ministral-cross-model-comparator-v0-private')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def file_sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(8388608),b''):h.update(chunk)
 return h.hexdigest()
def inheritance():
 names=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
 for name in names:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 baseline=json.loads((P/'preservation-baseline.json').read_bytes())
 for ref,want in baseline['local_refs'].items():assert git('rev-parse','refs/heads/'+ref).decode().strip()==want,ref
 return dict(status='PASS',parent_files_byte_identical=len(names),protected_local_refs=baseline['local_refs'])
def runtime_identity():
 frozen=json.loads((P/'model-runtime.json').read_bytes());checks={}
 for path,want in frozen['artifact_sha256'].items():
  got=file_sha(Path(path));assert got==want,path;checks[path]=got
 launch=json.loads((P/'original-launch.json').read_bytes());version=subprocess.check_output(launch['command'][:4]+['--version'],stderr=subprocess.STDOUT).decode();assert '11242' in version and '526c43b8f' in version
 return dict(status='PASS',sha256=checks,version=version,llama_cpp_commit=frozen['llama_cpp_commit'])
def frozen_transport(commit):
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b''
 names=git('ls-tree','-r','--name-only',commit,'--',str(P.relative_to(ROOT))).decode().splitlines();assert names
 for name in names:assert (ROOT/name).read_bytes()==git('show',commit+':'+name),name
 return dict(commit=commit,files_unchanged=len(names))
