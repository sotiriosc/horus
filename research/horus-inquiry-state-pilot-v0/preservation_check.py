"""Preserve all prior local/remote heads and inherited tracked content."""
import subprocess
from common import *
BRANCH='research/horus-inquiry-state-pilot-v0'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def audit(remote=False):
 baseline=json.loads((P/'preservation-baseline.json').read_text());old=dict(x.split(' ',1) for x in baseline['local_heads'].splitlines())
 now=dict(x.split(' ',1) for x in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').splitlines())
 for name,value in old.items():
  if name!='refs/heads/'+BRANCH:assert now[name]==value,name
 changes=git('diff','--name-only',BASE_SHA).splitlines();assert all(n.startswith('research/'+BRANCH.split('/')[-1]+'/') for n in changes)
 for name,value in old.items():
  if name.endswith('-private-archive'):assert subprocess.run(['git','merge-base','--is-ancestor',value,'HEAD'],cwd=ROOT).returncode==1
 assert git('rev-parse','research/horus-triangulation-learning-v0')==BASE_SHA
 result=dict(status='PASS',prior_local_heads_unchanged=sum(n!='refs/heads/'+BRANCH for n in old),private_archive_heads_unreachable=sum(n.endswith('-private-archive') for n in old),inherited_tracked_content_unchanged=True,preceding_study_head=BASE_SHA)
 if remote:
  prior={line.split()[1]:line.split()[0] for line in baseline['remote_heads'].splitlines()};current={line.split()[1]:line.split()[0] for line in git('ls-remote','--heads','origin').splitlines()}
  assert all(current.get(n)==v for n,v in prior.items());result['prior_remote_heads_unchanged']=len(prior)
 return result
if __name__=='__main__':print(canon(audit(remote=True)))
