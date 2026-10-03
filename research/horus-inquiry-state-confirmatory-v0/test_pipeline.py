"""Fault-injected orchestration: no real Git mutations, inference or network."""
import tempfile,json
from pathlib import Path
from unittest.mock import patch
from common import canon,save,filehash
import pipeline as q

def case(fault=None):
 with tempfile.TemporaryDirectory() as d:
  root=Path(d);study=root/'study';assets=root/'assets';private=assets/'private';old=root/'old'
  for p in [study,private,old]:p.mkdir(parents=True)
  (old/'dsl.py').write_text('synthetic');(study/'machines.py').write_text('synthetic');(private/'campaign-signed.jsonl').write_text('synthetic raw')
  save(study/'raw-freeze.json',dict(status='RAW_COMPLETE_UNSCORED',model_responses=1968,collection_wall_seconds=123,private_raw_sha256=filehash(private/'campaign-signed.jsonl'),world_freeze_sha='WORLD',method_freeze_sha='METHOD'))
  save(study/'prospective-registration.json',dict(original_design_commit='DESIGN',seeds={},population={}))
  save(study/'world-qualification.json',dict(selection_rules_commit='RULES',hypothesis_catalogue_sha256='CATALOGUE'))
  events=[];head=['WORLD'];scores=[0]
  def git(*args):
   if args[:2]==('log','-1'):return 'RAW'
   if args[:2]==('status','--porcelain'):return ''
   if args[:2]==('remote','get-url'):return 'https://github.com/sotiriosc/horus.git'
   if args[:2]==('ls-remote','--heads'):return 'FINAL\trefs/heads/'+q.BRANCH
   raise AssertionError(args)
  def commit(names,message):
   events.append('commit:'+names[0]);head[0]='RAW' if names==['raw-freeze.json'] else 'FINAL';return head[0]
  def command(args):
   if str(study/'scoring.py') in args:
    assert 'commit:raw-freeze.json' in events;events.append('score');scores[0]+=1;out=Path(args[-1]);out.mkdir(parents=True)
    result=dict(decision=dict(classification='SYNTHETIC'),costs={'A':{'seconds':1},'B':{'seconds':1},'O':{'seconds':1}})
    save(out/'results.json',result)
    for n in ['per-world-results.private.json','contribution-details.private.jsonl']:(out/n).write_text('changed' if fault=='replay' and scores[0]==2 else 'identical')
   elif args[0]=='git' and 'push' in args:
    assert events.count('score')==2 and 'audit:FINAL' in events
    assert args==['git','-c','push.followTags=false','push','--recurse-submodules=no','origin','FINAL:refs/heads/'+q.BRANCH]
    events.append('push')
   else:raise AssertionError(args)
  def check_output(args,**kwargs):
   assert str(study/'publication_check.py') in args;events.append('audit:'+head[0]);return canon(dict(status='FAIL' if fault=='audit' and head[0]=='FINAL' else 'PASS',audited_head=head[0])).encode()
  replacements=dict(P=study,ROOT=root,ASSETS=assets,OLD=old,git=git,commit=commit,command=command,frozen=lambda _: ({},dict(method_freeze_sha='METHOD',private_worlds_sha256='WORLDS')),preserve=lambda **_:dict(status='PASS'),identity=lambda:dict(status='PASS'),render=lambda *args:'synthetic report')
  with patch.multiple(q,**replacements),patch.object(q.subprocess,'check_output',check_output):
   try:q.main('WORLD')
   except AssertionError:
    assert fault and 'push' not in events
   else:
    assert fault is None and events.count('push')==1
    receipt=json.loads((private/'publication-verification.json').read_text());assert receipt['publication_sha']=='FINAL' and receipt['status']=='PUBLISHED_VERIFIED_STOP'
 return events
for fault in [None,'replay','audit']:case(fault)
from common import P
save(P/'pipeline-tests.json',dict(status='PASS',model_calls=0,real_git_mutations=0,network_calls=0,raw_commit_precedes_scoring=True,two_replays_required=True,replay_difference_blocks_publication=True,failed_final_history_audit_blocks_publication=True,only_exact_authorized_branch_push=True,remote_head_verification=True))
print('Pipeline raw-first, replay failure, audit failure and exact-branch publication tests PASS')
