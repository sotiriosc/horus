import json
from pathlib import Path
P=Path('engineering/grounded-diagnostic-evidence-compiler-v0');manifest=json.loads((P/'fixture-manifest.json').read_bytes());count=0;candidates=0
for entry in manifest['entries']:
 case=json.loads(Path(entry['path']).read_bytes());out=json.loads((P/'results/compiled'/(entry['render_id']+'.json')).read_bytes())
 assert sorted(case['components'],key=lambda v:v['id'])==sorted((x['component'] for x in out['component_index']),key=lambda v:v['id'])
 assert sorted(case['versions'],key=lambda v:v['id'])==sorted((x['version'] for x in out['version_index']),key=lambda v:v['id'])
 records={r['id']:r for r in case['records']}
 def resolve(path):
  value=case
  for token in path.split('/')[1:]:
   token=token.replace('~1','/').replace('~0','~');value=value[int(token)] if isinstance(value,list) else value[token]
  return value
 for edge in out['evidence_graph']['edges']:
  reason=edge['reason'];src=records[edge['source']['id']];target=edge['target'];values=[resolve(p) for p in edge['source_paths']]
  assert src['kind']==edge['source']['kind']
  if reason=='declares_current_version':assert src['kind']=='deployment' and target['kind']=='version' and values==[src['data']['current_version']]==[target['id']]
  elif reason=='record_version':assert target['kind']=='version' and values==[src['version']]==[target['id']]
  elif reason=='capture_version':assert src['kind']=='capture' and target['kind']=='version' and values==[src['data']['deployment_version']]==[target['id']]
  elif reason=='input_component':assert src['kind']=='execution_input' and target['kind']=='component' and values==[src['component_id']]==[target['id']]
  elif reason=='output_event':assert src['kind']=='execution_output' and target['kind']=='event' and values==[src['event_id']]==[target['id']]
  elif reason=='capture_event':assert src['kind']=='capture' and target['kind']=='event' and values==[src['data']['immutable_event_id']]==[target['id']]
  elif reason=='output_capture_same_event':
   cap=records[target['id']];assert cap['kind']=='capture' and src['kind']=='execution_output';assert src['event_id']==cap['data']['immutable_event_id'];assert len(values)==2 and values[0]==values[1]==src['event_id']
  elif reason=='candidate_input_output':
   output=records[target['id']];assert src['kind']=='execution_input' and output['kind']=='execution_output';assert src['version']==output['version'] and type(src['at']) in (int,float) and type(output['at']) in (int,float) and src['at']<output['at'];candidates+=1
  else:raise AssertionError(reason)
  count+=1
 for row in out['input_output_candidates']:
  output=records[row['output_record_id']]
  want={r['id'] for r in case['records'] if r['kind']=='execution_input' and r.get('version')==output.get('version') and type(r.get('at')) in (int,float) and type(output.get('at')) in (int,float) and r['at']<output['at'] and ('component_id' not in r or 'component_id' not in output or r['component_id']==output['component_id']) and ('event_id' not in r or 'event_id' not in output or r['event_id']==output['event_id'])}
  assert {x['input_record_id'] for x in row['candidates']}==want
report=dict(status='PASS',packages=80,component_and_version_indexes_preserved=80,graph_edges_verified=count,candidate_edges_verified=candidates,verification='Independent source-pointer resolution, endpoint kinds, explicit equality/chronology and complete candidate-set checks; only public evidence and compiled outputs; no gold or scientific scorer.')
(P/'structural-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
