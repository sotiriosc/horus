"""Read-only preservation and artifact checks, without benchmark regeneration."""
import hashlib,json,subprocess,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
B=ROOT/'research/blind-diagnostic-generalization-v0'
BASE='b156dd01ce6f1deed049fa2589581888d36f34fb'
def sha_file(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for data in iter(lambda:f.read(8388608),b''):h.update(data)
 return h.hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def preservation():
 names=git('ls-tree','-r','--name-only',BASE).decode().splitlines()
 for name in names:assert (ROOT/name).read_bytes()==git('show',BASE+':'+name),name
 refs=json.loads((B/'preservation-baseline.json').read_bytes())['protected_public_refs']
 refs.update({'research/blind-diagnostic-generalization-v0':'bb58926e0f2581bee38393e179b758b18d0879e4','research/blind-diagnostic-generalization-v0-replacement-r1':BASE})
 for ref,want in refs.items():assert git('rev-parse','refs/heads/'+ref).decode().strip()==want,ref
 frozen=json.loads((B/'freeze-manifest.json').read_bytes())
 for name,want in frozen['sha256'].items():assert sha_file(B/'materialized'/name)==want,name
 renders=json.loads((B/'materialized/render-manifest.json').read_bytes())
 for row in renders['entries']:assert sha_file(B/'materialized'/row['request_path'])==row['request_sha256']
 original=json.loads((B/'campaign/scores.json').read_bytes());r1=json.loads((B/'replacement-r1/scores.json').read_bytes());assert original['classification']==r1['classification']=='INVALID_STUDY'
 private=[r for r in git('for-each-ref','--format=%(refname)','refs/heads/').decode().splitlines() if 'private-archive' in r]
 for ref in private:assert subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=ROOT).returncode==1
 return dict(status='PASS',base_files_byte_identical=len(names),materialized_hashes=len(frozen['sha256']),request_hashes=80,protected_refs=refs,original_campaign='INVALID_STUDY',r1_campaign='INVALID_STUDY',private_archive_heads_excluded=len(private),world_regeneration=False)
def runtime_hashes():
 cfg=json.loads((B/'model-runtime.json').read_bytes())['artifact_provenance']['parent_verification'];assets=Path('/tmp/horus-development-runtime-assets');results={}
 for name,want in cfg['artifact_sha256'].items():
  actual=sha_file(assets/name);assert actual==want,name;results[name]=actual
 actual=sha_file(assets/'engine/llama-b11242/llama-server');assert actual==cfg['installed_server_sha256'];results['installed_server']=actual
 launch=json.loads((B/'campaign/launch.json').read_bytes());version=subprocess.check_output(launch['command'][:4]+['--version'],stderr=subprocess.STDOUT).decode();assert '11242' in version and '526c43b8f' in version
 return dict(status='PASS',sha256=results,version=version,commit=cfg['llama_cpp_commit'])
def source_integrity():
 audit=json.loads((P/'source-audit.json').read_bytes());root=Path('/tmp/horus-runtime-control-pinned-source');source=root/('llama.cpp-'+audit['source_commit'])
 assert sha_file(root/'source.tar.gz')==audit['archive_sha256']
 with tarfile.open(root/'source.tar.gz') as archive:assert archive.pax_headers['comment']==audit['source_commit']
 for name,entry in audit['files'].items():assert sha_file(source/name)==entry['sha256'],name
 return dict(status='PASS',source_commit=audit['source_commit'],source_files=len(audit['files']))
if __name__=='__main__':print(json.dumps(dict(preservation=preservation(),runtime=runtime_hashes(),source=source_integrity()),indent=2))
