"""Prospective fixtures from authored facts; no diagnostic compiler or prior outputs."""
import argparse,copy,hashlib,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;SEED=862540719
CLASSES=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
DEFS=['Available current evidence supports a specific active structural or mechanical defect and distinguishes it from materially plausible benign alternatives.','The internally valid evidence is sufficient within the declared contract/input scope and supports no current defect. Unusual or undesirable behavior alone is insufficient.','The evidence is internally valid but a current defect and a materially plausible benign explanation remain observationally indistinguishable.','A defect is demonstrated for an older version, while supplied current mechanisms and observations show it is no longer active within the stated scope.','The supplied evidence package contains incompatible immutable, version, capture or provenance facts and cannot support a valid operational diagnosis.']
ARMS=['O','S','R','E']
def digest(*parts):return hashlib.sha256('|'.join(map(str,(SEED,)+parts)).encode()).hexdigest()
def ident(i,role):return 'f'+digest('identity',i,role)[:16]
def world_id(i):return 'w'+digest('world',i)[:12]
def raw(x):return (json.dumps(x,indent=2,ensure_ascii=True)+'\n').encode()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)

def compute(index,v):
 if index==0:return str(int(bool(v['a'] and v['b']) or bool(v['c'])))
 if index==1:
  transitions={'q0':{'a':'q1','b':'q0'},'q1':{'a':'q1','b':'q2'},'q2':{'a':'q3','b':'q0'},'q3':{'a':'q3','b':'q3'}};state='q0'
  for c in v['word']:state=transitions[state][c]
  return state
 if index==2:
  visited={v['start']}
  while True:
   expanded=visited|{b for a,b in v['edges'] if a in visited}
   if expanded==visited:break
   visited=expanded
  return ''.join('1' if n in visited else '0' for n in range(5))
 if index==3:
  left,right=v['left'],v['right'];prev=list(range(len(right)+1))
  for i,a in enumerate(left,1):
   row=[i]
   for j,b in enumerate(right,1):row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(a!=b)))
   prev=row
  return str(prev[-1])
 if index==4:return str(math.gcd(v['x'],v['y']))
 if index==5:return ','.join(str(max(v['values'][i:i+3])) for i in range(len(v['values'])-2))
 if index==6:
  result=[0]*(len(v['a'])+len(v['b'])-1)
  for i,a in enumerate(v['a']):
   for j,b in enumerate(v['b']):result[i+j]+=a*b
  return ','.join(map(str,result))
 if index==7:return str(sum(v['text'].startswith(v['pattern'],i) for i in range(len(v['text']))))
 if index==8:return str(math.comb(v['n'],v['k']))
 if index==9:return ''.join(c for c in v['text'] if c not in 'AEIOU')
 raise AssertionError(index)

CONVENTION='UNKNOWN denotes an uncaptured reference or value, never a literal operating input. Source declarations with the same capture_id describe one immutable event and must name the same operand record; no declaration has priority. Receipts are exact observed outputs, not promises that a contract was obeyed. No hidden transforms, lost data or unlisted target operations apply. Different components are separately scoped.'

def author_raw(world,operation,results):
 # world contains lower-level facts only; classification is never passed here.
 i=world['index'];facts=world['facts'];inputs=operation['parameter_sets'][world['parameter_set']];records={};meta={'index':i,'target':ident(i,'target'),'service_build':ident(i,'service-build'),'other_build':ident(i,'other-build'),'input_ids':[ident(i,'operand-'+str(j)) for j in range(2)],'current_sources':[ident(i,'service-source-'+str(j)) for j in range(2)],'current_capture':ident(i,'service-capture'),'other_source':ident(i,'other-source'),'current_receipt':ident(i,'service-receipt'),'other_receipt':ident(i,'other-receipt')};unit='unit-'+digest('unit-code',i)[:9];manifest=ident(i,'manifest');contract=ident(i,'contract')
 records[meta['target']]={'kind':'component','unit_code':unit,'serving_manifest':manifest,'contract_ref':contract}
 records[manifest]={'kind':'deployment','component_id':meta['target'],'build_id':meta['service_build']}
 for build,order in ((meta['other_build'],1),(meta['service_build'],2)):records[build]={'kind':'build','component_id':meta['target'],'creation_order':order}
 records[contract]={'kind':'contract','component_id':meta['target'],'rule':operation['rule'],'admissible_input_ids':meta['input_ids']}
 for j,key in enumerate(meta['input_ids']):records[key]={'kind':'operand','component_id':meta['target'],'inputs':copy.deepcopy(inputs[j])}
 for j,key in enumerate(meta['current_sources']):
  claim=facts['claims'][j];records[key]={'kind':'source','component_id':meta['target'],'capture_id':meta['current_capture'],'input_ref':'UNKNOWN' if claim is None else meta['input_ids'][claim]}
 records[meta['other_source']]={'kind':'source','component_id':meta['target'],'capture_id':ident(i,'other-capture'),'input_ref':meta['input_ids'][facts['other_build_input']]}
 records[meta['current_receipt']]={'kind':'receipt','component_id':meta['target'],'build_id':meta['service_build'],'source_ref':meta['current_sources'][0],'emitted_value':results[facts['service_output']]}
 records[meta['other_receipt']]={'kind':'receipt','component_id':meta['target'],'build_id':meta['other_build'],'source_ref':meta['other_source'],'emitted_value':results[facts['other_build_output']]}
 for n in range(1 if world['parameter_set']==0 else 2):
  prefix='adjacent-'+str(n);component=ident(i,prefix);deploy=ident(i,prefix+'-manifest');build=ident(i,prefix+'-build');rule=ident(i,prefix+'-contract');operand=[ident(i,prefix+'-input-'+str(k)) for k in range(2)];source=ident(i,prefix+'-source');receipt=ident(i,prefix+'-receipt');capture=ident(i,prefix+'-capture')
  records[component]={'kind':'component','unit_code':'unit-'+digest(i,prefix)[:9],'serving_manifest':deploy,'contract_ref':rule}
  records[deploy]={'kind':'deployment','component_id':component,'build_id':build};records[build]={'kind':'build','component_id':component,'creation_order':2}
  records[rule]={'kind':'contract','component_id':component,'rule':operation['rule'],'admissible_input_ids':operand}
  for j,key in enumerate(operand):records[key]={'kind':'operand','component_id':component,'inputs':copy.deepcopy(inputs[j])}
  records[source]={'kind':'source','component_id':component,'capture_id':capture,'input_ref':operand[n%2]};records[receipt]={'kind':'receipt','component_id':component,'build_id':build,'source_ref':source,'emitted_value':results[n%2]}
  if world['parameter_set']==1 and n==0:
   earlier=ident(i,prefix+'-earlier-build');records[earlier]={'kind':'build','component_id':component,'creation_order':1};records[ident(i,prefix+'-earlier-receipt')]={'kind':'receipt','component_id':component,'build_id':earlier,'source_ref':source,'emitted_value':results[1]}
 # Stable record permutation conceals role insertion order but preserves identical S/E bytes.
 records=dict(sorted(records.items(),key=lambda kv:digest('record-order',i,kv[0])))
 return {'scope':{'requested_unit':unit,'operation':operation['domains'][world['parameter_set']],'scope_rule':'Judge only the requested unit and its two supplied target executions.','evidence_convention':CONVENTION},'records':records},meta

def author_reduction(world,operation,results):
 # Direct fixture from prospectively authored facts; never consumes raw evidence or S gold/output.
 facts=world['facts'];inputs=operation['parameter_sets'][world['parameter_set']]
 allowed=[{'input_value':copy.deepcopy(v),'required_result':results[j]} for j,v in enumerate(inputs)]
 def trial(service,order,claims,observed):
  declarations=[{'claimed_input':'UNKNOWN' if c is None else copy.deepcopy(inputs[c]),'required_result_for_claim':'UNKNOWN' if c is None else results[c]} for c in claims]
  return {'in_service':service,'creation_order':order,'observed_result':results[observed],'source_capture':{'scope':'All declarations below concern the very same immutable event. None has priority and no further declaration is available.','input_declarations':declarations},'admissible_completions':copy.deepcopy(allowed)}
 return {'scope':'Both trials concern the requested unit only. UNKNOWN denotes an uncaptured value, not a literal operating input. Observed results are exact, with no hidden transformations.','trials':[trial(True,2,facts['claims'],facts['service_output']),trial(False,1,[facts['other_build_input']],facts['other_build_output'])]}

def state_gold(evidence):
 # Offline author gold only. Never passed to author_reduction or another fixture renderer.
 records=evidence['records'];target=next(k for k,r in records.items() if r['kind']=='component' and r['unit_code']==evidence['scope']['requested_unit']);component=records[target];build=records[component['serving_manifest']]['build_id'];receipts={k:r for k,r in records.items() if r['kind']=='receipt'};sources={k:r for k,r in records.items() if r['kind']=='source'};captures={}
 for key,r in sources.items():captures.setdefault(r['capture_id'],[]).append(key)
 groups=[];knowledge=[];conflicts=[]
 for capture,members in sorted(captures.items()):
  refs=sorted({sources[key]['input_ref'] for key in members if sources[key]['input_ref']!='UNKNOWN'});status='UNKNOWN' if not refs else 'KNOWN' if len(refs)==1 else 'DISAGREEING';groups.append({'capture_id':capture,'source_record_ids':sorted(members)});knowledge.append({'capture_id':capture,'status':status,'input_ids':refs})
  if status=='DISAGREEING':conflicts.append(capture)
 return {'target_component_id':target,'in_service_build_id':build,'in_service_receipt_ids':sorted(k for k,r in receipts.items() if r['component_id']==target and r['build_id']==build),'other_build_receipt_ids':sorted(k for k,r in receipts.items() if r['component_id']==target and r['build_id']!=build),'other_component_receipt_ids':sorted(k for k,r in receipts.items() if r['component_id']!=target),'receipt_source_links':[{'receipt_id':k,'source_record_id':r['source_ref']} for k,r in sorted(receipts.items())],'capture_groups':groups,'source_knowledge':knowledge,'conflicting_capture_ids':conflicts}

CLASS_TEXT='Class definitions:\n'+'\n'.join(c+': '+d for c,d in zip(CLASSES,DEFS))+'\n\nReturn only the classification object. No rationale, citations or other prose.'
SYSTEM_DIAG='Use only the supplied bounded evidence and class definitions. Do not invent missing facts or silently reconcile incompatible declarations of one immutable event. Return exactly one JSON object satisfying the response schema. No tools, interventions or solution proposals.'
SYSTEM_OP='Perform only the specified bounded operation for each supplied input. Return exactly one JSON object satisfying the response schema. Results must use the exact output convention specified by the operational rule. No tools or explanatory prose.'
SYSTEM_STATE='Organize the supplied records into the requested structured state. Required operational results are already supplied; do not recompute arithmetic and do not produce a diagnostic classification. Return exactly one JSON object satisfying the response schema. No tools or explanatory prose.'
STATE_TASK='Identify the component matching requested_unit and follow its serving_manifest to the in-service build. Partition target receipts into that build versus other builds; separately list receipts of all other components. Link every receipt to its source record. Group every source declaration by immutable capture_id. For each capture use status KNOWN if all declarations agree on one concrete input reference, UNKNOWN if every declaration is UNKNOWN, or DISAGREEING if different concrete input references are asserted. input_ids lists distinct concrete references, excluding UNKNOWN. List DISAGREEING capture IDs in conflicting_capture_ids. Include all receipts and source captures in links/groups/knowledge. Array order is irrelevant; no duplicates. Return only the nine fields in the schema.'

def generate():
 spec=json.loads((P/'case-spec.json').read_bytes());schemas=json.loads((P/'schemas.json').read_bytes());files={};gold=[];entries=[];worlds=[]
 for full in spec['worlds']:
  w={k:copy.deepcopy(v) for k,v in full.items() if k not in ('class','composition')};operation=spec['operations'][w['operation']];i=w['index'];wid=world_id(i);inputs=operation['parameter_sets'][w['parameter_set']];results=[compute(w['operation'],v) for v in inputs];assert results[0]!=results[1]
  evidence,meta=author_raw(w,operation,results);reduction=author_reduction(w,operation,results);mechanical_table=[{'input_record_id':key,'required_output':compute(w['operation'],rec['inputs'])} for key,rec in evidence['records'].items() if rec['kind']=='operand']
  op_fixture={'operational_rule':operation['rule'],'inputs':inputs};state_fixture={'raw_evidence':evidence,'supplied_computations':mechanical_table}
  fixtures={'O':op_fixture,'S':state_fixture,'R':reduction,'E':evidence};files['worlds/'+wid+'.json']=raw(evidence)
  authored_gold=state_gold(evidence)
  proof={'contract':operation['rule'],'admissible_inputs':inputs,'mechanically_required_results':results,'service_claims':w['facts']['claims'],'service_observed':results[w['facts']['service_output']],'other_build_input':w['facts']['other_build_input'],'other_build_observed':results[w['facts']['other_build_output']],'current_build_creation_order':2,'other_build_creation_order':1,'same_immutable_capture_for_service_claims':True,'no_claim_priority':True,'declared_gold':full['class'],'argument':{'SUPPORTED_CURRENT_DEFECT':'Known agreeing service input requires one result but the exact service observation is the other; hidden transformations are excluded.','NO_SUPPORTED_DIAGNOSIS':'Current and earlier observations match their known requirements; the bounded input and capture evidence is complete and agreeing.','INSUFFICIENT_EVIDENCE':'The service input is uncaptured. Both supplied admissible inputs remain possible, but only one yields the observed result; no declaration distinguishes them.','HISTORICAL_DEFECT_NOT_CURRENT':'The earlier build observation violates its known requirement; the explicitly in-service newer build matches its requirement.','INVALID_OR_CONTRADICTORY_EVIDENCE':'Two equal-standing declarations of one immutable service-input event identify different operands, with no additional source to resolve the incompatibility.'}[full['class']]}
  gold.append({'world_id':wid,'index':i,'operation':w['operation'],'family':operation['family'],'class':full['class'],'composition':full['composition'],'phase':w['phase'],'O':{'results':results},'S':authored_gold,'R':{'classification':full['class']},'E':{'classification':full['class']},'proof':proof,'metadata':meta})
  for arm in ARMS:
   fixture=fixtures[arm];rid=digest('render',wid,arm)[:20];system=SYSTEM_OP if arm=='O' else SYSTEM_STATE if arm=='S' else SYSTEM_DIAG
   instruction='Compute both results in the supplied input order. Return only {"results":["first result","second result"]}.' if arm=='O' else STATE_TASK if arm=='S' else CLASS_TEXT
   user=instruction+'\n\nTask data:\n'+raw(fixture).decode();neutral={'messages':[{'role':'system','content':system},{'role':'user','content':user}],'response_schema':schemas[arm]};request={'messages':neutral['messages'],'response_format':{'type':'json_object','schema':schemas[arm]},'temperature':.2,'top_p':.9,'top_k':40,'min_p':.05,'seed':SEED,'max_tokens':2048,'cache_prompt':False,'stream':False,'chat_template_kwargs':{'enable_thinking':True}}
   files['fixtures/'+rid+'.json']=raw(fixture);files['neutral/'+rid+'.json']=raw(neutral);files['requests/'+rid+'.json']=raw(request);entries.append({'world_id':wid,'arm':arm,'render_id':rid,'request_path':'requests/'+rid+'.json','request_sha256':hashlib.sha256(raw(request)).hexdigest()})
  worlds.append({'world_id':wid,'phase':w['phase']})
 base=sorted(ARMS,key=lambda a:digest('arm-order',a));schedule=[];last=None
 for epoch in range(4):
  order=sorted(worlds,key=lambda w:digest('epoch-order',epoch,w['world_id']))
  if last==order[0]['world_id']:order=order[1:]+order[:1]
  for world in order:
   arm=base[(world['phase']+epoch)%4];entry=next(e for e in entries if e['world_id']==world['world_id'] and e['arm']==arm);entry.update(epoch=epoch+1,within_world_position=epoch+1,call_order=len(schedule)+1);schedule.append(entry['render_id']);last=world['world_id']
 files['gold.json']=raw(gold);files['render-manifest.json']=raw({'seed':SEED,'base_arm_order':base,'schedule':schedule,'entries':entries});return files
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
 for name,data in generate().items():path=args.out/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print('Materialized 20 worlds and 80 matched tasks/requests; no model calls.')
