"""Authenticate original evidence and freeze safe raw projections before scoring."""
import collections,json,os,subprocess
from .adapter import *
from .worker import guard,workload
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_authority_autonomous_agent_v0.protocol import select_route,source_for_model_choice
from experiments.empirical_evidence_acquisition_proposal_v0.candidate import evaluate
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
from experiments.grounded_stagnation_escape_promotion_controlled_v0.worker import decision_projection,request_for
from types import SimpleNamespace

def main(freeze):
 preservation=guard(freeze);bind_task_metadata();rows=[json.loads(f.read_text()) for f in sorted((PUBLIC/'raw').glob('*.json'))];root=PRIVATE/'campaign';reference=json.loads((PUBLIC/'references.json').read_text());checks=[];histories={};memory_rows={}
 schedule=json.loads((PUBLIC/'schedule.json').read_text())['schedule']
 assert len(rows)==72 and len({(r['global_index'],r['arm']) for r in rows})==72
 for arm in ('A','B'):
  for profile in range(4):
   key=f'{arm}-P{profile}';path=root/key
   with SessionStore(path/'session',True) as s,ModernMemory(path/'memory.sqlite3',False) as m:
    history=authenticated_projection(s,m);decisions=rows_of(s,'AUTONOMOUS_AGENT_DECISION');assert len(history)==len(decisions)==len(m.rows())==6
    for i,d in enumerate(decisions,1):
     rr=next(r for r in rows if r['arm']==arm and r['profile']==profile and r['decision']['index']==i);envelope=s.records['events'][i-1];event=envelope['record']
     assert rr['decision']=={k:v for k,v in d.items() if k!='recorded_at'} and digest(envelope)==rr['authenticated_event_envelope_sha256']
     assert {k:v for k,v in event.items() if k!='recorded_at'}==rr['event']
     assert rr['measurement']==event['runtime_measurement'] and digest(rr['measurement'])==event['measurement_sha256']==d['measurement_sha256']
     assert event['receipt']['realized_consequence']==rr['realized_consequence']==consequence(rr['measurement'],rr['reference_seconds'],.1)
     for action in CANDIDATES:assert d['grounded_assessments_before'][action]==prior_state(m.rows(),f'{profile}:{action}',i)
     assert d['grounded_after']==prior_state(m.rows(),f"{profile}:{d['selected_action']}",i+1)
     route=select_route(d['grounded_assessments_before']);e=evaluate(profile,route['candidates'],d['grounded_assessments_before'],history[:i-1])
     assert d['suffix_before']=={'count':0,'relation':None}
     if arm=='A' and e['eligible']:
      assert d['decision_source']=='EMPIRICAL_EVIDENCE_ACQUISITION' and d['selected_action']==e['target_action'] and d['action_call_id'] is None
     else:
      assert d['decision_source']==source_for_model_choice(route,d['grounded_assessments_before'],d['selected_action']) and d['action_call_id'] is not None
      proxy=SimpleNamespace(records={'training':[x for x in s.records['training'] if x['kind']=='AUTONOMOUS_AGENT_DECISION' and x['record']['index']<i]})
      planned=request_for(decision_projection(proxy,i,profile,d['grounded_assessments_before'],route))
      intents=[x['record'] for x in s.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_INTENT' and x['record']['call_id']==d['action_call_id']]
      assert 1<=len(intents)<=2 and all(x['request_bytes_utf8'].encode()==planned['wire'] for x in intents)
      responses=[x['record']['response'] for x in s.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_RESULT' and x['record']['call_id']==d['action_call_id'] and x['record']['response']['transport_error'] is None]
      assert len(responses)==1
      assert parse_action(responses[0]['raw_output'])['selected_action']==d['selected_action']
    memory_rows[key]=dict(events=len(m.rows()),database_sha256=file_sha(path/'memory.sqlite3'),rows_sha256=digest(m.rows()),grounded_sha256=digest(all_assessments(AuthenticatedMemory(s,m),profile)))
    histories[key]=dict(events=len(history),history_sha256=digest(history))
 for r in rows:
  encounter=schedule[r['global_index']-1];assert r['profile']==encounter['profile'] and r['workload']==encounter['workload'] and r['half']==encounter['half']
  w,req=workload(r['workload']);ref=reference['workloads'][w['id']];assert r['reference_seconds']==ref['reference_seconds'] and r['reference_output_sha256']==ref['output_sha256']
  m=r['measurement'];path=root/'executions'/f"{r['global_index']:02d}-{r['arm']}"
  private_measure=json.loads((path/'execution-measurement.json').read_text());assert all(m[k]==v for k,v in private_measure.items())
  if (path/'execution-final.txt').exists():assert file_sha(path/'execution-final.txt')==m['output_sha256']
  if m['valid']:assert m['finish_reason']=='stop' and m['reference_match'] and m['structural_valid'] and m['peak_vram_mib']<=22000
  assert r['realized_consequence']==consequence(m,ref['reference_seconds'],.1)
  if r['arm']=='C':assert r['decision'] is None and r['event'] is None and m['action']=='HOLD'
  checks.append(dict(index=r['global_index'],arm=r['arm'],actual_termination=json.loads((path/'termination.json').read_text()) if (path/'termination.json').exists() else None))
 assert json.loads((PUBLIC/'restart.json').read_text())['status']=='PASS'
 lineage=json.loads((PUBLIC/'lineage.json').read_text());current={l.split()[1]:l.split()[0] for l in subprocess.check_output(['git','ls-remote','--heads','origin'],cwd=ROOT).decode().splitlines()}
 assert all(current[k]==v for k,v in lineage['remote_refs'].items())
 local={l.split()[0]:l.split()[1] for l in subprocess.check_output(['git','for-each-ref','--format=%(refname) %(objectname)','refs/heads'],cwd=ROOT).decode().splitlines()}
 assert all(local[k]==v for k,v in lineage['local_refs'].items())
 basefiles=subprocess.check_output(['git','ls-tree','-r','--name-only',lineage['latest_base']],cwd=ROOT).decode().splitlines()
 result=dict(status='PASS',scheduled=72,attempted=72,completed=72,scientific_decisions={'A':24,'B':24,'C':24},authorization_events=48,all_original_receipts_authenticated=True,continuous_measurements_bound_to_signed_events=True,policy_replay=True,raw_measurements_match_private=True,restart='PASS',memory=memory_rows,histories=histories,server_terminations=checks,preservation=preservation,inherited_files_unchanged=len(basefiles),protected_local_refs=len(lineage['local_refs']),protected_remote_refs=len(lineage['remote_refs']))
 write(PUBLIC/'postflight.json',result)
 manifest={str(f.relative_to(PRIVATE)):{'sha256':file_sha(f),'bytes':f.stat().st_size} for f in sorted(PRIVATE.rglob('*')) if f.is_file()}
 write(PUBLIC/'private-evidence-manifest.json',dict(policy='Original private signed streams, authorizations, keys, Memory databases and server/model envelopes remain outside Git. Hashes only.',files=manifest))
 for f in PRIVATE.rglob('*'):
  if f.is_file():f.chmod(0o400)
 hashes={str(f.relative_to(PUBLIC/'raw')):file_sha(f) for f in (PUBLIC/'raw').glob('*.json')}
 write(PUBLIC/'raw-freeze.json',dict(status='FROZEN_BEFORE_ANALYSIS',scoring_occurred=False,environment_freeze=freeze,raw_sha256=hashes,private_manifest_sha256=file_sha(PUBLIC/'private-evidence-manifest.json')))
 for f in (PUBLIC/'raw').glob('*.json'):f.chmod(0o444)
 print(json.dumps(dict(status='PASS',completed=72,authorized_memory_events=48,original_private_files=len(manifest),raw_files=len(hashes))),flush=True)
if __name__=='__main__':
 import sys
 from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
 main(sys.argv[1])
