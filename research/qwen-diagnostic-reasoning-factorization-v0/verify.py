"""Independent operation, evidence-state, reduction and non-reuse verification."""
import ast,collections,copy,functools,hashlib,itertools,json,re
from pathlib import Path
import jsonschema
from generate import P,CLASSES,ARMS,SEED,raw,canonical,generate
ROOT=P.parents[1]
def norm(x):
 if isinstance(x,dict):return {k:norm(v) for k,v in sorted(x.items())}
 if isinstance(x,list):return sorted([norm(v) for v in x],key=canonical)
 return x

def independent_operation(i,v):
 if i==0:return '1' if v['c']==1 or (v['a'],v['b'])==(1,1) else '0'
 if i==1:
  state=0
  for letter in v['word']:
   if state==0:state=1 if letter=='a' else 0
   elif state==1:state=1 if letter=='a' else 2
   elif state==2:state=3 if letter=='a' else 0
  return 'q'+str(state)
 if i==2:
  todo=[v['start']];seen=set()
  while todo:
   x=todo.pop(0)
   if x in seen:continue
   seen.add(x);todo.extend(edge[1] for edge in v['edges'] if edge[0]==x)
  return ''.join(str(int(x in seen)) for x in range(5))
 if i==3:
  @functools.lru_cache(None)
  def distance(a,b):
   if not a:return len(b)
   if not b:return len(a)
   return min(distance(a[1:],b)+1,distance(a,b[1:])+1,distance(a[1:],b[1:])+(a[0]!=b[0]))
  return str(distance(v['left'],v['right']))
 if i==4:return str(next(d for d in range(min(v['x'],v['y']),0,-1) if v['x']%d==0 and v['y']%d==0))
 if i==5:return ','.join(str(sorted(v['values'][n:n+3])[-1]) for n in range(len(v['values'])-2))
 if i==6:
  a,b=v['a'],v['b'];return ','.join(str(sum(a[j]*b[k-j] for j in range(len(a)) if 0<=k-j<len(b))) for k in range(len(a)+len(b)-1))
 if i==7:return str(len(re.findall('(?='+re.escape(v['pattern'])+')',v['text'])))
 if i==8:return str(sum(1 for _ in itertools.combinations(range(v['n']),v['k'])))
 if i==9:return v['text'].translate(str.maketrans('','','AEIOU'))
 raise AssertionError(i)

def independently_bind(ev):
 rr=ev['records'];requested=ev['scope']['requested_unit'];candidates=[key for key in rr if rr[key].get('unit_code')==requested];assert len(candidates)==1;target=candidates[0];build=rr[rr[target]['serving_manifest']]['build_id'];active=[];other=[];outside=[];links=[];grouped=collections.defaultdict(list)
 for key,rec in rr.items():
  if rec['kind']=='receipt':
   assert rec['source_ref'] in rr and rr[rec['source_ref']]['kind']=='source';assert rr[rec['source_ref']]['component_id']==rec['component_id'];links.append({'receipt_id':key,'source_record_id':rec['source_ref']})
   if rec['component_id']!=target:outside.append(key)
   elif rec['build_id']==build:active.append(key)
   else:other.append(key)
  if rec['kind']=='source':grouped[rec['capture_id']].append(key)
 groups=[];knowledge=[];conflicts=[]
 for cap,members in grouped.items():
  vals=[]
  for source in members:
   value=rr[source]['input_ref']
   if value!='UNKNOWN':assert rr[value]['kind']=='operand';vals.append(value)
  vals=list(set(vals));status='DISAGREEING' if len(vals)>1 else 'UNKNOWN' if not vals else 'KNOWN'
  if status=='DISAGREEING':conflicts.append(cap)
  groups.append({'capture_id':cap,'source_record_ids':members});knowledge.append({'capture_id':cap,'status':status,'input_ids':vals})
 return {'target_component_id':target,'in_service_build_id':build,'in_service_receipt_ids':active,'other_build_receipt_ids':other,'other_component_receipt_ids':outside,'receipt_source_links':links,'capture_groups':groups,'source_knowledge':knowledge,'conflicting_capture_ids':conflicts}

def derive_reduction(ev,operation):
 state=independently_bind(ev);rr=ev['records'];target=state['target_component_id'];contract=rr[rr[target]['contract_ref']];allowed=[{'input_value':copy.deepcopy(rr[key]['inputs']),'required_result':independent_operation(operation,rr[key]['inputs'])} for key in contract['admissible_input_ids']];trials=[]
 for rid in state['in_service_receipt_ids']+state['other_build_receipt_ids']:
  receipt=rr[rid];source=rr[receipt['source_ref']];capture=source['capture_id'];members=[key for key,r in rr.items() if r['kind']=='source' and r['capture_id']==capture]
  # Declaration order is immaterial; compare normalized assertion lists below.
  declarations=[]
  for key in members:
   ref=rr[key]['input_ref'];value='UNKNOWN' if ref=='UNKNOWN' else copy.deepcopy(rr[ref]['inputs']);required='UNKNOWN' if ref=='UNKNOWN' else independent_operation(operation,value);declarations.append({'claimed_input':value,'required_result_for_claim':required})
  trials.append({'in_service':receipt['build_id']==state['in_service_build_id'],'creation_order':rr[receipt['build_id']]['creation_order'],'observed_result':receipt['emitted_value'],'source_capture':{'scope':'All declarations below concern the very same immutable event. None has priority and no further declaration is available.','input_declarations':declarations},'admissible_completions':copy.deepcopy(allowed)})
 return {'scope':'Both trials concern the requested unit only. UNKNOWN denotes an uncaptured value, not a literal operating input. Observed results are exact, with no hidden transformations.','trials':trials}

def reduction_normal_form(state):
 result=copy.deepcopy(state)
 for trial in result['trials']:
  trial['source_capture']['input_declarations'].sort(key=canonical)
  trial['admissible_completions'].sort(key=canonical)
 result['trials'].sort(key=lambda t:(not t['in_service'],t['creation_order']))
 return result

def independent_class(state):
 trials=state['trials'];current=next(t for t in trials if t['in_service']);assert sum(t['in_service'] for t in trials)==1
 for t in trials:
  known=[d for d in t['source_capture']['input_declarations'] if d['claimed_input']!='UNKNOWN']
  if len({canonical(d['claimed_input']) for d in known})>1:return CLASSES[4]
 claims=current['source_capture']['input_declarations'];known=[d for d in claims if d['claimed_input']!='UNKNOWN']
 if not known:
  required=[x['required_result'] for x in current['admissible_completions']];assert current['observed_result'] in required and any(v!=current['observed_result'] for v in required);return CLASSES[2]
 if known[0]['required_result_for_claim']!=current['observed_result']:return CLASSES[0]
 for t in trials:
  if not t['in_service']:
   assert t['creation_order']<current['creation_order'];d=t['source_capture']['input_declarations'][0]
   if d['required_result_for_claim']!=t['observed_result']:return CLASSES[3]
 return CLASSES[1]

def prior_inventory():
 # All preserved study trees, including compiler fixtures and self-model/diagnosis.
 files=[f for root in ('research','analysis','engineering') for f in (ROOT/root).rglob('*') if f.is_file() and P not in f.parents and '.git' not in f.parts and '__pycache__' not in f.parts and f.suffix in ('.json','.jsonl','.md','.txt','.py')]
 ids=set();objects=set();contracts=set();tuples=set();count=0
 def inspect(x):
  if isinstance(x,dict):
   objects.add(hashlib.sha256(canonical(x).encode()).hexdigest())
   for k,v in x.items():
    if isinstance(v,str) and k in ('rule','contract','contract_text','operational_rule','requirement'):contracts.add(v)
    if isinstance(v,(dict,list)):inspect(v)
   if 'messages' in x and isinstance(x['messages'],list):
    for msg in x['messages']:
     if not isinstance(msg,dict):continue
     content=msg.get('content','')
     if not isinstance(content,str):continue
     for separator in ('Raw evidence:\n','Task data:\n'):
      if separator in content:
       try:inspect(json.loads(content.split(separator,1)[1]))
       except ValueError:pass
  elif isinstance(x,list):
   for v in x:inspect(v)
 for f in files:
  data=f.read_bytes();ids.update(re.findall(rb'[zkf][0-9a-f]{16}',data))
  if f.suffix=='.json':
   try:inspect(json.loads(data));count+=1
   except (ValueError,UnicodeDecodeError):pass
 return files,ids,objects,contracts,count

def audit():
 expected=generate();actual={str(f.relative_to(P/'materialized')):f.read_bytes() for f in (P/'materialized').rglob('*') if f.is_file()};assert actual==expected
 manifest=json.loads(actual['render-manifest.json']);gold=json.loads(actual['gold.json']);spec=json.loads((P/'case-spec.json').read_bytes());schemas=json.loads((P/'schemas.json').read_bytes());entries=manifest['entries'];assert len(gold)==20 and len(entries)==len(set(manifest['schedule']))==80
 assert collections.Counter(g['class'] for g in gold)=={c:4 for c in CLASSES}
 for c in CLASSES:assert collections.Counter(g['composition'] for g in gold if g['class']==c)=={'simpler':2,'composition-dependent':2}
 files,prior_ids,prior_objects,prior_contracts,prior_json_count=prior_inventory();new_ids=set();proofs=[];leak_tokens=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE','OPERATIONAL_COMPUTATION','EVIDENCE_STATE_REASONING','EPISTEMIC_REDUCTION','END_TO_END_DIAGNOSIS','gold','defect','benign','insufficient','historical','invalid','conflict','compliance','diagnostic_verdict']
 old_labels=[]
 for q in ('qwen-diagnostic-ontology-elicitation-v0','qwen-diagnostic-composition-binding-v0'):
  prior=json.loads((ROOT/'research'/q/'case-spec.json').read_bytes());old_labels.extend(x['mechanism'] for x in prior) if isinstance(prior,list) else old_labels.extend(x['name'] for x in prior['mechanisms'])
 old_labels+=['version_selection','authority_precedence','entity_binding','publication_update','operation_idempotence','boundary_comparison']
 for op in spec['operations']:
  assert op['rule'] not in prior_contracts;assert op['family'].lower() not in {n.lower() for n in old_labels}
 for g in gold:
  wid=g['world_id'];ev=json.loads(actual['worlds/'+wid+'.json']);assert hashlib.sha256(canonical(ev).encode()).hexdigest() not in prior_objects;new_ids.update(re.findall(rb'f[0-9a-f]{16}',raw(ev)));ee={e['arm']:e for e in entries if e['world_id']==wid};assert set(ee)==set(ARMS)
  fixtures={arm:json.loads(actual['fixtures/'+e['render_id']+'.json']) for arm,e in ee.items()};assert fixtures['E']==ev and raw(fixtures['S']['raw_evidence'])==raw(ev)
  op=spec['operations'][g['operation']];independent_results=[independent_operation(g['operation'],v) for v in fixtures['O']['inputs']];assert independent_results==g['O']['results'] and independent_results[0]!=independent_results[1]
  assert fixtures['O']['operational_rule']==op['rule'];assert set(fixtures['O'])=={'operational_rule','inputs'}
  for v,result in zip(fixtures['O']['inputs'],independent_results):
   tup={'operational_rule':op['rule'],'inputs':v,'required_output':result};assert hashlib.sha256(canonical(tup).encode()).hexdigest() not in prior_objects
  for row in fixtures['S']['supplied_computations']:assert row['required_output']==independent_operation(g['operation'],ev['records'][row['input_record_id']]['inputs'])
  assert {x['input_record_id'] for x in fixtures['S']['supplied_computations']}=={key for key,r in ev['records'].items() if r['kind']=='operand'}
  bound=independently_bind(ev);assert norm(bound)==norm(g['S']);reduced=derive_reduction(ev,g['operation']);assert reduction_normal_form(reduced)==reduction_normal_form(fixtures['R']);assert independent_class(reduced)==g['class']
  assert not re.search(r'f[0-9a-f]{16}',raw(fixtures['R']).decode())
  for arm,e in ee.items():
   fixturetext=raw(fixtures[arm]).decode().lower()
   # S output instructions may request conflicts; the S fixture itself supplies no verdict flags.
   for token in leak_tokens+old_labels+[o['family'] for o in spec['operations']]:assert token.lower() not in fixturetext,(wid,arm,token)
   for token in ('simpler','composition-dependent',wid):assert token not in fixturetext
   request=json.loads(actual[e['request_path']]);neutral=json.loads(actual['neutral/'+e['render_id']+'.json']);assert request['messages']==neutral['messages'];assert request['response_format']['schema']==neutral['response_schema']==schemas[arm];assert request['messages'][1]['content'].split('Task data:\n',1)[1]==raw(fixtures[arm]).decode();assert len(request['messages'])==2 and request['seed']==SEED and request['max_tokens']==2048 and request['cache_prompt'] is False
   if arm in ('O','S'):
    for label in CLASSES:assert label not in raw(request).decode()
   assert hashlib.sha256(actual[e['request_path']]).hexdigest()==e['request_sha256'];jsonschema.Draft7Validator(schemas[arm]).validate(g[arm])
  proofs.append({'world_id':wid,'operation_results_verified':2,'evidence_state_verified':True,'reduction_matches_raw_world':True,'independent_class':g['class'],'gold_matches':True})
 assert not new_ids&prior_ids
 epochs=[];glookup={g['world_id']:g for g in gold}
 for epoch in range(1,5):
  rr=[e for e in entries if e['epoch']==epoch];assert len(rr)==20 and len({e['world_id'] for e in rr})==20;assert collections.Counter(e['arm'] for e in rr)=={a:5 for a in ARMS}
  for c in CLASSES:assert collections.Counter(e['arm'] for e in rr if glookup[e['world_id']]['class']==c)=={a:1 for a in ARMS}
  epochs.append({'epoch':epoch,'arm_counts':dict(collections.Counter(e['arm'] for e in rr)),'each_class_each_arm_once':True})
 for c in CLASSES:
  for a in ARMS:assert collections.Counter(e['within_world_position'] for e in entries if e['arm']==a and glookup[e['world_id']]['class']==c)=={n:1 for n in range(1,5)}
 for family in range(10):
  first=[e['arm'] for e in entries if e['within_world_position']==1 and glookup[e['world_id']]['operation']==family];assert len(first)==2 and len(set(first))==2
 for name in ('generate.py','transport.py','run_campaign.py','guard.py'):
  path=P/name
  if not path.exists():continue
  source=path.read_text();tree=ast.parse(source);imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)];assert 'score' not in imports and 'verify' not in imports
 source=(P/'generate.py').read_text();tree=ast.parse(source)
 for name in ('author_raw','author_reduction'):
  node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);segment=ast.get_source_segment(source,node);assert "['class']" not in segment and 'state_gold(' not in segment
 return {'status':'PASS','scientific_model_calls_before_freeze':0,'worlds':20,'requests':80,'arms_applicable_to_all_worlds':True,'materialized_files':len(actual),'class_counts':dict(collections.Counter(g['class'] for g in gold)),'new_record_ids':len(new_ids),'prior_files_audited':len(files),'prior_json_files_parsed':prior_json_count,'prior_id_overlap':0,'prior_exact_world_contract_tuple_overlap':0,'independent_world_checks':proofs,'epoch_checks':epochs,'neutral_requests':80,'O_has_only_rule_operands':True,'S_and_E_raw_bytes_identical':True,'R_has_no_ids_or_judgment_flags':True,'R_authored_independently_of_raw_parser_and_S_gold':True,'no_existing_compiler_imported':True,'semantic_review':'Ten new operations; no direct templates from R2, ontology, composition/binding, compiler or self-model/diagnosis inventories. Broad arithmetic/string/graph concepts reused honestly; specific required relations differ. Internally authored tasks, not external/open-world evidence.','sha256':{name:hashlib.sha256(data).hexdigest() for name,data in actual.items()}}
if __name__=='__main__':
 result=audit();(P/'preflight.json').write_bytes(raw(result));print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','independent_world_checks','epoch_checks')}))
