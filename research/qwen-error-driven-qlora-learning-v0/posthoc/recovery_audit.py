"""Post-training accounting for the externally reported restart; no model inference."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];A=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
events=[json.loads((A/'provenance'/n).read_bytes()) for n in ['scientific-training-restart-1.json','scientific-training-interruption-2.json']];event=events[-1];artifact=json.loads((P/'M1-artifact-freeze.json').read_bytes());assert artifact['recovery_used']==event['resume_checkpoint']
old=Path(event['initial_adapter_archive']);same={}
for name,info in artifact['initial_adapter_files'].items():
 same[name]=digest(old/name)==info['sha256']
 if name!='adapter_config.json':assert same[name]
old_config=json.loads((old/'adapter_config.json').read_bytes());new_config=json.loads((A/'study-adapters/M1-initial/adapter_config.json').read_bytes())
old_config['target_modules']=sorted(old_config['target_modules']);new_config['target_modules']=sorted(new_config['target_modules']);assert old_config==new_config
config_note='Initial adapter tensor file and README are byte-identical. adapter_config.json differs only in ordering of target_modules serialized from an unordered set across processes; normalized configs are identical. The frozen runtime asserted the same exact 280 targeted projections at every load.'
old_seconds=sum(e['pre_restart_last_record']['wall_seconds'] for e in events);discarded=sum(e['completed_updates_to_recompute'] for e in events);record=dict(status='PASS',events=events,initial_artifact_files_identical_after_recovery=same,initial_adapter_config_semantically_identical=True,initial_artifact_comparison_note=config_note,retained_optimizer_updates=artifact['optimizer_steps'],retained_training_exposures=artifact['examples_seen'],logged_discarded_completed_updates=discarded,logged_discarded_completed_exposures=8*discarded,minimum_physical_completed_updates=artifact['optimizer_steps']+discarded,minimum_physical_completed_exposures=artifact['examples_seen']+8*discarded,recorded_pre_restart_training_process_seconds=old_seconds,resumed_training_process_seconds=artifact['wall_seconds'],combined_recorded_active_seconds=old_seconds+artifact['wall_seconds'],duration_scope='Sum of the last logged update elapsed time from each interrupted process and the complete final resumed process elapsed time. Excludes downtime and any unlogged work at interruption; therefore a recorded lower bound, not exact elapsed calendar time.',recipe_or_data_changed=False,completed_harvest_repeated=False,sealed_results_used_for_recovery=False)
(P/'training-recovery-audit.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:record[k] for k in ['status','retained_optimizer_updates','logged_discarded_completed_updates','combined_recorded_active_seconds']}))
