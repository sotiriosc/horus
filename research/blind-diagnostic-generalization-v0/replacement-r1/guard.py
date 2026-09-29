"""Read-only inheritance and runtime checks; never regenerate benchmark artifacts."""
import hashlib,json,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[1]
BASE='bb58926e0f2581bee38393e179b758b18d0879e4'
PRIVATE=Path('/tmp/horus-blind-diagnostic-generalization-v0-replacement-r1-private')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def file_sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(8388608),b''):h.update(chunk)
 return h.hexdigest()
def inheritance():
 names=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
 for name in names:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 baseline=json.loads((B/'preservation-baseline.json').read_bytes());refs=dict(baseline['protected_public_refs']);refs['research/blind-diagnostic-generalization-v0']=BASE
 for ref,want in refs.items():assert git('rev-parse','refs/heads/'+ref).decode().strip()==want,ref
 freeze=json.loads((B/'freeze-manifest.json').read_bytes())
 for name,want in freeze['sha256'].items():assert file_sha(B/'materialized'/name)==want,name
 manifest=json.loads((B/'materialized/render-manifest.json').read_bytes());assert len(manifest['schedule'])==len(set(manifest['schedule']))==80
 for row in manifest['entries']:assert file_sha(B/'materialized'/row['request_path'])==row['request_sha256']
 return dict(status='PASS',parent_files_byte_identical=len(names),materialized_files_hashed=len(freeze['sha256']),request_hashes_verified=80,protected_refs=refs,world_regeneration=False,original_campaign_classification=json.loads((B/'campaign/scores.json').read_bytes())['classification'])
def runtime_identity():
 frozen=json.loads((B/'model-runtime.json').read_bytes())['artifact_provenance']['parent_verification'];assets=Path('/tmp/horus-development-runtime-assets');checks={}
 for name,want in frozen['artifact_sha256'].items():
  got=file_sha(assets/name);assert got==want,name;checks[name]=got
 server=assets/'engine/llama-b11242/llama-server';got=file_sha(server);assert got==frozen['installed_server_sha256'];checks['installed_server']=got
 launch=json.loads((B/'campaign/launch.json').read_bytes());version=subprocess.check_output(launch['command'][:4]+['--version'],stderr=subprocess.STDOUT).decode();assert '11242' in version and '526c43b8f' in version
 return dict(status='PASS',sha256=checks,version=version,llama_cpp_commit=frozen['llama_cpp_commit'],launch_flags='Exact original campaign/launch.json command and cwd, unchanged')
def frozen_transport(commit):
 assert git('merge-base','--is-ancestor',commit,'HEAD')==b''
 names=git('ls-tree','-r','--name-only',commit,'--',str(P.relative_to(ROOT))).decode().splitlines();assert names
 for name in names:assert (ROOT/name).read_bytes()==git('show',commit+':'+name),name
 return dict(commit=commit,method_files_unchanged=len(names))
