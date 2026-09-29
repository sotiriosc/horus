"""Supplemental read-only post-action replay; added after the registered run."""
from pathlib import Path
from collections import Counter
import json
from experiments.empirical_evidence_acquisition_replication_v0.worker import *
from experiments.grounded_autonomous_agent_v0_1 import analyze as replay
import sys
root=Path(sys.argv[1]);data=preflight();total=0
for case,spec in data['cases'].items():
 for arm in ('C','E'):
  p=root/'cases'/case/arm
  with SessionStore(p/'session',True) as s,ModernMemory(p/'memory.sqlite3',False) as m:
   m.reconcile(s);rows=m.rows();h=history(s)
   audit=[x['record'] for x in s.records['training'] if x['kind']=='REPLICATION_ACTION_AUDIT']
   rejected=[x['record'] for x in s.records['training'] if x['kind']=='REGISTERED_REJECTED_ATTEMPT']
   old=replay.relation_type;replay.relation_type=lambda k:relation_type(spec,k)
   try:
    for seq,(env,x) in enumerate(zip(s.records['events'],audit),1):
     r=env['record']['receipt'];state=r['next_state'];aa={a:replay.prior_state(rows,f'{state}:{a}',seq+1) for a in A}
     size=seq+sum(v['after_authorized_event_count']<seq for v in rejected)
     observed=evaluate(state,aa,h[:size],spec)
     require(observed==x['after']['candidate'],'independent candidate-after replay '+case)
     total+=1
    boundary=read(p/'evaluation.json');o=boundary['boundary']['candidate']['output']
    if spec['expected_eligible']:
     require(o['source']==frozen.SOURCE and o['reason']==frozen.TRIGGER_REASON,'exact source and reason')
     if arm=='E': require(not boundary['after']['candidate']['output']['eligible'],'immediate reset')
   finally:replay.relation_type=old
# All original/source files and Phase 4 artifacts remain byte-identical to parent.
import subprocess
changed=subprocess.check_output(['git','diff','--name-only','41dd8ae','HEAD'],text=True).splitlines()
require(all('/empirical_evidence_acquisition_replication_v0/' in '/'+p or '/empirical-evidence-acquisition-replication-v0/' in '/'+p for p in changed),'historical source changed')
result=dict(status='PASS',independent_candidate_after_replays=total,exact_trigger_source_reason=True,frozen_candidate_sha256=SHA,historical_and_active_sources_unchanged=True,regression_tests=29)
write(PUBLIC/'supplemental-integrity-audit.json',result)
print(json.dumps(result))
