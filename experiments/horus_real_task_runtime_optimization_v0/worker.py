"""One-shot references and bounded fresh-process campaign halves. No scoring."""
import argparse,json,statistics,subprocess,time
from .adapter import *

def guard(freeze):
 assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='research/horus-real-task-runtime-optimization-v0'
 subprocess.run(['git','diff','--exit-code',freeze,'--','experiments/horus_real_task_runtime_optimization_v0'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 lineage=json.loads((PUBLIC/'lineage.json').read_text())
 for name,pin in lineage['source_hashes'].items():assert file_sha(ROOT/name)==pin['sha256'],name
 subprocess.run(['git','diff','--exit-code',lineage['latest_base'],'--','.',':(exclude)experiments/horus_real_task_runtime_optimization_v0',':(exclude)research/horus-real-task-runtime-optimization-v0'],cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
 manifest=json.loads((PUBLIC/'runtime-manifest.json').read_text())
 for name,h in manifest['files_sha256'].items():assert file_sha(name)==h,name
 for name,h in json.loads((PUBLIC/'frozen-inputs.json').read_text()).items():assert file_sha(ROOT/name)==h,name
 assert gpu()['uuid']==manifest['hardware']['uuid']
 return dict(status='PASS',freeze=freeze,promoted_source_files_unchanged=len(lineage['source_hashes']),runtime_files_verified=len(manifest['files_sha256']))

def workload(wid):
 specs=json.loads((PUBLIC/'workload-manifest.json').read_text())['workloads'];w=next(x for x in specs if x['id']==wid)
 assert file_sha(ROOT/w['request_path'])==w['sha256'];return w,json.loads((ROOT/w['request_path']).read_text())

def references(freeze):
 guard(freeze);root=PRIVATE/'references';root.mkdir(parents=True,exist_ok=False);rows={};start=time.perf_counter()
 write(root/'intent.json',dict(freeze=freeze,workloads=12,repetitions=3,started_at=now()))
 try:
  for w in json.loads((PUBLIC/'workload-manifest.json').read_text())['workloads']:
   _,request_body=workload(w['id']);rep=[]
   for i in range(3):
    with Server('HOLD',root/f"{w['id']}-{i}") as server:
     row=server.measure(request_body,'reference',w['validator']);rep.append(row)
    assert row['valid'],'HOLD reference invalid; no campaign'
    assert row['prompt_tokens']+request_body['max_tokens']<=8192,'required context does not fit'
    assert len({x['output_sha256'] for x in rep})==1,'HOLD output not reproducible; no campaign'
   rows[w['id']]=dict(output_sha256=rep[0]['output_sha256'],reference_seconds=statistics.median(x['wall_seconds'] for x in rep),runs=rep)
   write(PUBLIC/'reference-progress.json',dict(status='IN_PROGRESS',workloads=rows))
   elapsed=time.perf_counter()-start;done=len(rows)*3
   print(json.dumps(dict(stage='HOLD_references',completed=done,total=36,elapsed_seconds=round(elapsed),estimated_remaining_seconds=round(elapsed/done*(36-done)))),flush=True)
  result=dict(status='PASS',method_freeze=freeze,reference_executions=36,workloads=rows,rule='median of three independent fresh-process runs; exact output hash equality',elapsed_seconds=time.perf_counter()-start)
  write(PUBLIC/'references.json',result)
 except BaseException as exc:
  write(PUBLIC/'reference-stop.json',dict(status='REFERENCE_QUALIFICATION_FAILED',error=str(exc),completed_workloads=list(rows),no_autonomous_campaign=True));raise

def measure_action(action,w,request_body,ref,path):
 started=time.perf_counter()
 try:
  with Server(action,path) as server:measurement=server.measure(request_body,'execution',w['validator'],ref['output_sha256'])
 except InfrastructureError:raise
 except Exception as exc:
  # A launched candidate failure is real negative feedback, not an omitted episode.
  if not (path/'launch.json').exists():raise
  measurement=dict(action=action,valid=False,wall_seconds=None,error=type(exc).__name__+': '+str(exc),resource_violation=True,output_sha256=sha(b''),output_bytes=0,finish_reason=None,prompt_tokens=None,completion_tokens=None,timings={},launch_seconds=None,full_gpu_residency=False,peak_vram_mib=None)
  write(path/'execution-measurement.json',measurement)
 if measurement.get('monitor_errors',0):raise InfrastructureError('GPU monitoring unavailable during action; stop without Memory admission')
 measurement['executor_total_seconds']=time.perf_counter()-started
 return measurement

def stage(freeze,half):
 guard(freeze);bind_task_metadata();schedule=json.loads((PUBLIC/'schedule.json').read_text());refs=json.loads((PUBLIC/'references.json').read_text());assert refs['status']=='PASS'
 frozen_reference=subprocess.check_output(['git','show',freeze+':'+str((PUBLIC/'references.json').relative_to(ROOT))],cwd=ROOT);assert frozen_reference==(PUBLIC/'references.json').read_bytes()
 root=PRIVATE/'campaign';run=root/f'half-{half}';run.mkdir(parents=True,exist_ok=False);write(run/'intent.json',dict(half=half,freeze=freeze,started_at=now()))
 contexts={};started=time.perf_counter();completed=0
 try:
  for arm in ('A','B'):
   for profile in range(4):
    key=f'{arm}-P{profile}';folder=root/key;s=SessionStore(folder/'session',half==1);m=ModernMemory(folder/'memory.sqlite3',half==0)
    if half==0:s.save(state=profile,next_transaction_id=1)
    contexts[key]=(s,m)
  before={key:snapshot(*sm) for key,sm in contexts.items()}
  if half==1:
   expected=json.loads((root/'before-restart.json').read_text());assert expected==before,'restart state mismatch'
   write(PUBLIC/'restart.json',dict(status='PASS',fresh_process=True,all_eight_contexts_exact=True,before_sha256=digest(expected),after_sha256=digest(before),memory_reset=False,model_calls_during_verification=0))
  for encounter in schedule['schedule'][half*12:(half+1)*12]:
   w,request_body=workload(encounter['workload']);ref=refs['workloads'][w['id']]
   for arm in encounter['arm_order']:
    index=encounter['index'];key=f"{arm}-P{w['profile']}";path=root/'executions'/f'{index:02d}-{arm}'
    intent=dict(global_index=index,arm=arm,profile=w['profile'],workload=w['id'],started_at=now())
    write(root/'intents'/f'{index:02d}-{arm}.json',intent)
    if arm=='C':
     measurement=measure_action('HOLD',w,request_body,ref,path)
     result=dict(measurement=measurement,decision=None,event=None,realized_consequence=consequence(measurement,ref['reference_seconds'],.1))
    else:
     s,m=contexts[key];local_index=len(rows_of(s,'AUTONOMOUS_AGENT_DECISION'))+1
     decision=(integrated_decide if arm=='A' else promoted_decide)(s,m,ModelClient(),local_index)
     if decision[3]['call_id'] is not None:park_ordinary()
     world=RuntimeWorld(w['profile'],decision[0],lambda action:measure_action(action,w,request_body,ref,path),ref['reference_seconds'],.1)
     result=execute_protected(s,m,local_index,decision,world,index,w['id'])
     result['realized_consequence']=result['event']['receipt']['realized_consequence']
    safe=dict(**intent,**result,reference_seconds=ref['reference_seconds'],reference_output_sha256=ref['output_sha256'],half=half)
    write(PUBLIC/'raw'/f'{index:02d}-{arm}.json',safe);completed+=1
    if completed%3==0:
     elapsed=time.perf_counter()-started
     print(json.dumps(dict(stage=f'campaign_half_{half}',completed_in_half=completed,total_in_half=36,elapsed_seconds=round(elapsed),estimated_remaining_seconds=round(elapsed/completed*(36-completed)))),flush=True)
  after={key:snapshot(*sm) for key,sm in contexts.items()}
  write(root/('before-restart.json' if half==0 else 'completed-state.json'),after)
  write(run/'complete.json',dict(status='COMPLETE',completed=completed,elapsed_seconds=time.perf_counter()-started))
 except BaseException as exc:
  write(PUBLIC/'campaign-stop.json',dict(status='INCOMPLETE_OR_INFRASTRUCTURE_INVALID',half=half,completed_in_half=completed,error=type(exc).__name__+': '+str(exc)));raise
 finally:
  for s,m in contexts.values():m.close();s.close()

def main():
 p=argparse.ArgumentParser();p.add_argument('phase',choices=['references','half0','half1']);p.add_argument('--freeze',required=True);args=p.parse_args()
 if args.phase=='references':references(args.freeze)
 else:stage(args.freeze,int(args.phase[-1]))
if __name__=='__main__':main()
