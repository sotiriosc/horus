"""Post-campaign verification only; no model loads or scientific selection."""
import sys,json,subprocess,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];sys.path.insert(0,str(P))
from data import *
from analysis import *
from run import filehash,PRIVATE,ARTIFACTS,load_outputs

def git(*args):return subprocess.check_output(['git',*args],cwd=R,text=True)
freeze=json.loads((P/'data-freeze.json').read_bytes())
for name,digest in freeze['files'].items():assert filehash(P/name)==digest,name
checks=[]
for cycle in [1,2]:
 resultfile=P/f'cycle{cycle}-results.json'
 if not resultfile.exists():continue
 result=json.loads(resultfile.read_bytes());arm=f'M{cycle-1}';name=f'H{cycle}';cs=rows(P/'materialized'/f'{name}.jsonl');outputs=load_outputs(arm,name);scored=score(cs,outputs);published=rows(P/f'{name}-scored.jsonl')
 assert len(outputs)==len(cs)==len(published)
 for c,o,s,pub in zip(cs,outputs,scored,published):
  assert o['messages']==messages(c);assert all(pub[k]==v for k,v in s.items());assert pub['raw_answer_sha256']==sha(o['text']);assert pub['prompt_sha256']==sha(o['rendered_prompt']);assert pub['final_answer']==(o['text'] if s['schema'] else None)
 if 'admission_stop' in result:checks.append(dict(cycle=cycle,admission_stop=result['admission_stop'],harvest_replayed=len(cs)));continue
 previous=rows(P/'D1.jsonl') if cycle==2 else None
 training,composition=construct_training(cs,rows(P/'materialized'/f'N{cycle}.jsonl'),scored,cycle,previous)
 assert training==rows(P/f'D{cycle}.jsonl');assert composition==json.loads((P/f'D{cycle}-composition.json').read_bytes());assert audit_datasets(P/'materialized',training)==result['leakage']
 artifact=json.loads((P/f'M{cycle}-artifact-freeze.json').read_bytes());assert artifact['base_unchanged'] and artifact['adapter_changed'];assert artifact['initial_adapter_parameter_fingerprints']!=artifact['adapter_parameter_fingerprints']
 for key,folder in [('initial_adapter_files',ARTIFACTS/f'M{cycle}-initial'),('adapter_files',ARTIFACTS/f'M{cycle}')]:
  for name,meta in artifact[key].items():assert filehash(folder/name)==meta['sha256'] and (folder/name).stat().st_size==meta['bytes']
 assert artifact['examples_seen']==2*len(training);assert artifact['optimizer_steps']==2*((len(training)+7)//8);assert len(artifact['loss_curve'])==artifact['optimizer_steps']
 plan=[('M0','T1'),('M1','T1'),('M0','R1'),('M1','R1')] if cycle==1 else [('M1','T2'),('M2','T2'),('M2','T1'),('M2','R1'),('M1','R2'),('M2','R2')]
 predictions={}
 for arm,name in plan:
  cases=rows(P/'materialized'/f'{name}.jsonl');outs=load_outputs(arm,name);scores=score(cases,outs);published=rows(P/f'{arm}-{name}-scored.jsonl');assert len(scores)==len(published)
  for c,o,s,pub in zip(cases,outs,scores,published):
   assert o['messages']==messages(c);assert all(pub[k]==v for k,v in s.items());assert pub['raw_answer_sha256']==sha(o['text']);assert pub['prompt_sha256']==sha(o['rendered_prompt']);assert pub['final_answer']==(o['text'] if s['schema'] else None)
  predictions[arm,name]=scores
 comparison=compare(rows(P/'materialized'/f'T{cycle}.jsonl'),predictions[f'M{cycle-1}',f'T{cycle}'],predictions[f'M{cycle}',f'T{cycle}']);assert comparison==result['comparison']
 if cycle==1:
  regression=regress(rows(P/'materialized/R1.jsonl'),predictions['M0','R1'],predictions['M1','R1']);assert regression==result['regression'];assert cycle1_gate(comparison,regression,artifact,result['leakage'])==result['gate']
 else:
  retention=compare(rows(P/'materialized/T1.jsonl'),rows(P/'M1-T1-scored.jsonl'),predictions['M2','T1']);regs=dict(R1=regress(rows(P/'materialized/R1.jsonl'),rows(P/'M1-R1-scored.jsonl'),predictions['M2','R1']),R2=regress(rows(P/'materialized/R2.jsonl'),predictions['M1','R2'],predictions['M2','R2']));assert retention==result['retention'] and regs==result['regressions'];assert cycle2_gate(comparison,retention,regs,artifact,result['leakage'])==result['gate']
 checks.append(dict(cycle=cycle,harvest_replayed=len(cs),training_exposures=len(training),evaluation_endpoints_replayed=sum(len(v) for v in predictions.values()),classification=result['gate']['classification']))
dump(P/'replay-audit.json',dict(status='PASS',frozen_files_verified=len(freeze['files']),checks=checks))
b=json.loads((P/'preservation-baseline.json').read_bytes());base=b['base']
def tree(rev):
 out={}
 for line in git('ls-tree','-r',rev).splitlines():metadata,name=line.split('\t',1);out[name]=metadata
 return out
before=tree(base);after=tree('HEAD');assert all(after.get(n)==v for n,v in before.items());changed=set(after)-set(before);assert all(n.startswith('research/qwen-error-driven-qlora-learning-v0/') for n in changed)
heads='\n'.join(l for l in git('for-each-ref','--format=%(refname) %(objectname)','refs/heads').splitlines() if not l.startswith('refs/heads/research/qwen-error-driven-qlora-learning-v0 '));assert heads==b['local_heads']
remote_before={r:sha for sha,r in (x.split() for x in b['remote_heads'].splitlines())};remote_after={r:sha for sha,r in (x.split() for x in git('ls-remote','--heads','origin').splitlines())};assert all(remote_after.get(r)==sha for r,sha in remote_before.items())
promoted=tree('69947aa243a69e7ae26db534727a7122922d978d');protected={n:v for n,v in promoted.items() if n.startswith(('grounded_agent/','grounded_state/','horus/','experiments/')) and n.endswith(('.py','.json'))};assert all(after.get(n)==v for n,v in protected.items())
archives=[]
for ref in git('for-each-ref','--format=%(refname)','refs/heads').splitlines():
 if 'private-archive' in ref:
  reachable=subprocess.run(['git','merge-base','--is-ancestor',ref,'HEAD'],cwd=R).returncode==0;assert not reachable;archives.append(dict(ref=ref,reachable=False))
dump(P/'preservation-audit.json',dict(status='PASS',inherited_files_verified=len(before),promoted_E_source_files_verified=len(protected),prior_local_refs=len(heads.splitlines()),prior_remote_refs=len(remote_before),private_archive_ref_checks=archives,main_unchanged=True,scope='Committed prior results and branch refs unchanged; no prior source files modified. The external restart cleared temporary worktrees/private files; their recovery is not claimed. Persistent downloaded base and research artifacts are retained.'))
print(json.dumps(dict(status='PASS',cycles=checks,inherited_files=len(before),promoted_source_files=len(protected))))
