"""Authorized frozen campaign -> raw commit -> replay -> public branch only.

Any failure stops this process. No automatic scientific retries, training,
merges, model changes or subsequent study. Reinvoke only to resume the same
frozen run; the collector preserves every durably completed response.
"""
import argparse,fcntl,os,subprocess,sys,time
from common import *
from preservation_check import audit as preserve
from identity_check import verify as identity
from report import render
BRANCH='research/horus-delta-prediction-pilot-v0'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def command(args):subprocess.run(args,cwd=ROOT,check=True)
def commit(names,message):
 assert git('branch','--show-current')==BRANCH
 command(['git','add','--',*[str(P/name) for name in names]])
 staged=git('diff','--cached','--name-only').splitlines()
 assert set(staged)<= {'research/horus-delta-prediction-pilot-v0/'+n for n in names},staged
 if staged:command(['git','commit','-m',message])
 return git('rev-parse','HEAD')
def frozen(world_sha):
 method=json.loads((P/'method-freeze.json').read_text());world=json.loads((P/'world-data-freeze.json').read_text())
 assert subprocess.check_output(['git','show',world_sha+':research/horus-delta-prediction-pilot-v0/world-data-freeze.json'],cwd=ROOT)==(P/'world-data-freeze.json').read_bytes()
 assert subprocess.check_output(['git','show',world['method_freeze_sha']+':research/horus-delta-prediction-pilot-v0/method-freeze.json'],cwd=ROOT)==(P/'method-freeze.json').read_bytes()
 for name,digest in method['files_sha256'].items():assert filehash(P/name)==digest,name
 for name,digest in method['inherited_dependencies_sha256'].items():assert filehash(ROOT/name)==digest,name
 assert filehash(ASSETS/'private/worlds.jsonl')==world['private_worlds_sha256']
 command(['git','merge-base','--is-ancestor',world_sha,'HEAD']);return method,world

def main(world_sha):
 private=ASSETS/'private';lock=(private/'pipeline.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 state=private/'pipeline-state.json'
 def stage(name,**fields):save(state,dict(stage=name,world_freeze_sha=world_sha,utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),**fields));print(canon(dict(stage=name,**fields)),flush=True)
 method,world=frozen(world_sha);preserve(remote=True)
 if not (P/'raw-freeze.json').exists():
  stage('COLLECTING_RAW',planned_model_responses=544)
  command([sys.executable,'-u',str(P/'watchdog.py'),'scientific',sys.executable,'-u',str(P/'campaign.py'),'--world-freeze',world_sha])
 raw=json.loads((P/'raw-freeze.json').read_text());assert raw['status']=='RAW_COMPLETE_UNSCORED' and raw['model_responses']==544
 assert filehash(private/'campaign-signed.jsonl')==raw['private_raw_sha256']
 assert raw['world_freeze_sha']==world_sha and raw['method_freeze_sha']==world['method_freeze_sha']
 commit(['raw-freeze.json'],'Freeze complete authenticated delta-prediction pilot raw evidence before scoring')
 raw_sha=git('log','-1','--format=%H','--','research/horus-delta-prediction-pilot-v0/raw-freeze.json')
 stage('RAW_COMMITTED',raw_freeze_sha=raw_sha)
 frozen(world_sha)
 outputs=[private/'score-first',private/'score-replay']
 for output in outputs:command([sys.executable,'-u',str(P/'scoring.py'),'--raw-commit',raw_sha,'--output',str(output)])
 artifacts=['results.json','per-world-results.private.json','contribution-details.private.jsonl']
 replay={name:filehash(outputs[0]/name) for name in artifacts}
 assert replay=={name:filehash(outputs[1]/name) for name in artifacts}
 replay_report=dict(status='PASS',new_inference_calls=0,byte_identical_artifacts_sha256=replay,raw_freeze_sha=raw_sha)
 stage('SCORED_AND_REPLAY_VERIFIED',raw_freeze_sha=raw_sha)
 result=json.loads((outputs[0]/'results.json').read_text());save(P/'results.json',result);save(P/'replay.json',replay_report)
 save(P/'post-run-identity.json',identity());preservation=preserve(remote=True);save(P/'preservation-audit.json',preservation)
 frozen(world_sha)
 initial_audit=json.loads(subprocess.check_output([sys.executable,str(P/'publication_check.py')],cwd=ROOT));assert initial_audit['status']=='PASS';save(P/'publication-audit.json',initial_audit)
 registration=json.loads((P/'prospective-registration.json').read_text())
 handoff=dict(branch=BRANCH,base_sha=BASE_SHA,selection_rules_commit=json.loads((P/'world-qualification.json').read_text())['selection_rules_commit'],method_freeze_sha=world['method_freeze_sha'],world_data_freeze_sha=world_sha,raw_pre_score_freeze_sha=raw_sha,private_raw_sha256=raw['private_raw_sha256'],private_worlds_sha256=world['private_worlds_sha256'],model_repository='Qwen/Qwen3-14B',model_revision='231c69a380487f6c0e52d02dcf0d5456d1918201',adapter_sha256=ADAPTER_SHA,simulator_sha256=filehash(OLD/'dsl.py'),hypothesis_source_sha256=filehash(P/'machines.py'),hypothesis_catalogue_sha256=json.loads((P/'world-qualification.json').read_text())['hypothesis_catalogue_sha256'],seeds=registration['seeds'],populations=dict(worlds=16,arms=3,discovery_probes=6,sealed_queries=2,scientific_calls=544),collection_wall_seconds=raw['collection_wall_seconds'],total_recorded_inference_seconds=sum(v['seconds'] for v in result['costs'].values()))
 save(P/'handoff.json',handoff);(P/'REPORT.md').write_text(render(result,handoff,replay_report,preservation))
 save(P/'study-status.json',dict(status='COMPLETE_SCORED_REPLAYED_PUBLICATION_PENDING',classification=result['decision']['classification'],scientific_model_calls=544,training_steps=0,merged=False,promoted=False,subsequent_study=False))
 names=['results.json','replay.json','post-run-identity.json','preservation-audit.json','publication-audit.json','handoff.json','REPORT.md','study-status.json']
 head=commit(names,'Report frozen delta-prediction pilot evaluation with authenticated zero-inference replay')
 final_audit=json.loads(subprocess.check_output([sys.executable,str(P/'publication_check.py')],cwd=ROOT));assert final_audit['status']=='PASS' and final_audit['audited_head']==head
 save(private/'final-head-publication-audit.json',final_audit);preserve(remote=True);assert not git('status','--porcelain')
 stage('AUDITED_PUBLICATION_READY',head=head)
 assert git('remote','get-url','origin') in ['git@github.com:sotiriosc/horus.git','https://github.com/sotiriosc/horus.git','https://github.com/sotiriosc/horus']
 command(['git','-c','push.followTags=false','push','--recurse-submodules=no','origin',head+':refs/heads/'+BRANCH])
 remote=git('ls-remote','--heads','origin','refs/heads/'+BRANCH).split();assert remote==[head,'refs/heads/'+BRANCH]
 preservation=preserve(remote=True)
 receipt=dict(status='PUBLISHED_VERIFIED_STOP',remote='github.com/sotiriosc/horus',remote_branch='refs/heads/'+BRANCH,publication_sha=head,**handoff,classification=result['decision']['classification'],decision=result['decision'],preservation=preservation,final_history_audit_sha256=filehash(private/'final-head-publication-audit.json'))
 save(private/'publication-verification.json',receipt);stage('PUBLISHED_VERIFIED_STOP',publication_sha=head,classification=result['decision']['classification'])
 print(canon(receipt),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--world-freeze',required=True);args=ap.parse_args()
 try:main(args.world_freeze)
 except BaseException as error:
  print(canon(dict(status='STOPPED_REQUIRES_REVIEW',exception_type=type(error).__name__,message=str(error))),flush=True);raise
