"""Independent operational evaluator and structural audit. Never called by inference."""
import collections,copy,hashlib,json,re
from pathlib import Path
from generate import P,CLASSES,SHORT,IN,OUT,SEED,FRAME,SCHEMA,canon,generate,raw
ROOT=P.parents[1]

def operation(index,v):
 # Separate implementation from generator calculations, operating solely on supplied facts.
 if index==0:
  output=bytearray()
  for byte in v['source_octets']:output.extend([203,234] if byte==202 else [byte])
  return output.hex()
 if index==1:
  output=[]
  for glyph,count in v['glyph_runs']:
   for _ in range(count):output.append(glyph)
  return ''.join(output)
 if index==2:
  lhs=format(v['source_octet'],'08b');rhs=format(v['whitening_mask'],'08b');return int(''.join('0' if a==b else '1' for a,b in zip(lhs,rhs)),2)
 if index==3:
  alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ';shifted=alphabet[v['displacement']:]+alphabet[:v['displacement']];return v['source_letters'].translate(str.maketrans(alphabet,shifted))
 if index==4:
  words=[]
  for symbol in v['source_symbols']:words.append(v['codewords'][symbol])
  return ''.join(words)
 if index==5:return [[v['source_matrix'][c][r] for c in range(2)] for r in range(2)]
 if index==6:
  items=list(v['stack_items']);items.pop();return items
 if index==7:
  n=v['signed_integer'];return abs(n)*2-int(n<0)
 if index==8:
  items=[]
  for key in v['source_keys']:
   at=next((i for i,x in enumerate(items) if key<x),len(items));items.insert(at,key)
  return items
 if index==9:
  n=v['dividend'];d=v['divisor'];q=n//d;return {'quotient':q,'residue':n-d*q}
 raise AssertionError(index)

def diff(a,b,path=''):
 if type(a)!=type(b):return [path]
 if isinstance(a,dict):
  out=[]
  for k in sorted(a.keys()|b.keys()):
   if k not in a or k not in b:out.append(path+'/'+k)
   else:out.extend(diff(a[k],b[k],path+'/'+k))
  return out
 if isinstance(a,list):
  if len(a)!=len(b):return [path]
  return sum((diff(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
 return [] if a==b else [path]

def observed_class(ev,index):
 target=ev['scope']['component_id'];records=[r for r in ev['records'].values() if r.get('component_id')==target];source=next(r for r in records if r['kind']=='source');values={k:source[k] for k in IN[index]}
 for att in (r for r in records if r['kind']=='source_attestation'):
  assert att['capture_id']==source['capture_id']
  if any(att[k]!=source[k] for k in IN[index]):return SHORT['X']
 if 'UNKNOWN' in canon(values):return SHORT['U']
 expected=operation(index,values);receipts=[r for r in records if r['kind']=='receipt'];current=[r for r in receipts if r['build']==ev['scope']['deployed_build']];assert len(current)==1
 if current[0][OUT[index]]!=expected:return SHORT['D']
 if any(r['build']!=ev['scope']['deployed_build'] and r[OUT[index]]!=expected for r in receipts):return SHORT['T']
 return SHORT['H']

def audit():
 files=generate();stored={str(f.relative_to(P/'materialized')):f.read_bytes() for f in (P/'materialized').rglob('*') if f.is_file()};assert files==stored
 manifest=json.loads(files['render-manifest.json']);gold=json.loads(files['gold.json']);structure=json.loads(files['structure-spec.json']);spec=json.loads((P/'case-spec.json').read_bytes());entries=manifest['entries'];byrid={g['render_id']:g for g in gold}
 assert len(entries)==len(set(manifest['schedule']))==70 and len(gold)==70;assert collections.Counter(e['part'] for e in entries)=={'A':50,'B':20};assert SEED not in (417351046,731926581)
 oldroots=[ROOT/'research/blind-diagnostic-generalization-v0/materialized',ROOT/'research/qwen-diagnostic-ontology-elicitation-v0/materialized'];oldbytes=b'\n'.join(f.read_bytes() for root in oldroots for f in sorted(root.rglob('*.json')));oldids=set(re.findall(rb'[zk][0-9a-f]{16}',oldbytes));newids=set();oldobjects=set();oldcontracts=set();oldtuples=set()
 def harvest(obj):
  if isinstance(obj,dict):
   oldobjects.add(canon(obj))
   for k,v in obj.items():
    if isinstance(v,str) and k in ('rule','contract','contract_text','requirement','statement'):oldcontracts.add(v)
    if isinstance(v,(dict,list)):harvest(v)
  elif isinstance(obj,list):
   for v in obj:harvest(v)
 for root in oldroots:
  for f in root.rglob('*.json'):
   obj=json.loads(f.read_bytes());harvest(obj)
   if isinstance(obj,dict) and 'messages' in obj:
    for message in obj['messages']:
     content=message.get('content','')
     if 'Raw evidence:\n' in content:
      try:harvest(json.loads(content.split('Raw evidence:\n',1)[1]))
      except ValueError:pass
 oldlabels=['version_selection','authority_precedence','entity_binding','publication_update','operation_idempotence','boundary_comparison','big-endian serialization','exponential delay','half-up rounding','immutable timestamp']
 prior_spec=json.loads((ROOT/'research/qwen-diagnostic-ontology-elicitation-v0/case-spec.json').read_bytes());oldlabels.extend(x['mechanism'] for x in prior_spec)
 banned=CLASSES+['DECISIVE_ONLY','IRRELEVANT_COMPONENT','IRRELEVANT_HISTORICAL','REDUNDANT_CONSISTENT_EVIDENCE','MIXED_DISTRACTOR','COMPONENT_BINDING','VERSION_BINDING','REDUNDANT_EVIDENCE','TARGET_VS_DISTRACTOR','VALUE_DEPENDENCY','UNKNOWN_DEPENDENCY','CURRENTNESS','PROVENANCE_IDENTITY','healthy','historical defect','insufficient evidence','invalid evidence','current defect','gold class','expected answer']
 for m in spec['mechanisms']:assert m['name'].lower() not in {x.lower() for x in oldlabels}
 semantic=[];fingerprints=[]
 for e in entries:
  g=byrid[e['render_id']];ev=json.loads(files['evidence/'+e['render_id']+'.json']);request=json.loads(files[e['request_path']]);neutral=json.loads(files['neutral/'+e['render_id']+'.json']);index=g['mechanism_index'];text=raw(ev).decode();newids.update(re.findall(rb'k[0-9a-f]{16}',raw(ev)))
  for token in banned+oldlabels+[m['name'] for m in spec['mechanisms']]:assert token.lower() not in text.lower(),(e['render_id'],token)
  assert g['unit_id'].encode() not in oldbytes and g['unit_id'] not in text;assert canon(ev) not in oldobjects
  for record in ev['records'].values():
   if 'rule' in record:assert record['rule'] not in oldcontracts
  assert request['messages']==neutral['messages'] and request['response_format']['schema']==neutral['response_schema']==SCHEMA
  assert request['messages'][1]['content']==FRAME+text;assert len(request['messages'])==2;assert request['seed']==SEED and request['cache_prompt'] is False and request['max_tokens']==2048
  assert hashlib.sha256(files[e['request_path']]).hexdigest()==e['request_sha256']
  contract=ev['records'][g['contract_id']];assert contract['rule']==spec['mechanisms'][index]['contract'];calculated=observed_class(ev,index);assert calculated==g['classification'],(g['part'],index,g.get('endpoint'),g.get('level'),calculated,g['classification'])
  source=ev['records'][g['source_id']];receipt=ev['records'][g['receipt_id']]
  current=ev['records'][g['proof']['current_receipt_id']];assert current['build']==ev['scope']['deployed_build'];assert g['proof']['observed_output']==current[OUT[index]]
  if calculated==SHORT['U']:
   alternatives=g['proof']['alternative_completions'];path=g['proof']['critical_source_leaf'];expectations={}
   for name in ('benign','defect'):
    candidate=copy.deepcopy(source);ptr=candidate
    for k in path[:-1]:ptr=ptr[k]
    ptr[path[-1]]=alternatives[name]['source_leaf'];expectations[name]=operation(index,candidate);assert expectations[name]==alternatives[name]['required_output']
   assert expectations['benign']==receipt[OUT[index]] and expectations['defect']!=receipt[OUT[index]]
  # Each decisive tuple contains the new exact operational contract and actual input/output.
  tup={'contract':contract['rule'],'source':{k:source[k] for k in IN[index]},'output':receipt[OUT[index]]};assert canon(tup) not in oldobjects;fingerprints.append(hashlib.sha256(canon(tup).encode()).hexdigest())
  semantic.append({'render_id':e['render_id'],'independent_evaluator_class':calculated,'author_gold_matches':True})
 assert not newids&oldids
 ladder_proofs=[];pair_proofs=[]
 for row in structure:
  ee=[e for e in entries if e['unit_id']==row['unit_id']]
  if row['part']=='A':
   ee.sort(key=lambda e:e['level']);assert len(ee)==5 and [e['level'] for e in ee]==list(range(5));evs=[json.loads(files['evidence/'+e['render_id']+'.json']) for e in ee];base=evs[0]
   assert len({byrid[e['render_id']]['classification'] for e in ee})==1
   adds=[]
   for l,ev in enumerate(evs):
    assert canon(ev['scope'])==canon(base['scope'])
    for key in row['decisive_record_ids']:assert canon(ev['records'][key])==canon(base['records'][key])
    if l:
     prev=evs[l-1];assert set(prev['records'])<set(ev['records'])
     for key,value in prev['records'].items():assert canon(ev['records'][key])==canon(value)
     added=sorted(set(ev['records'])-set(prev['records']));assert len(added)==row['expected_additions'][l];adds.append({'level':l,'new_record_ids':added,'all_previous_facts_identical':True})
   ladder_proofs.append({'unit_id':row['unit_id'],'scope_unchanged':True,'decisive_facts_unchanged':True,'steps':adds})
  else:
   ee.sort(key=lambda e:e['endpoint']);assert len(ee)==2;aa,bb=[json.loads(files['evidence/'+e['render_id']+'.json']) for e in ee];delta=diff(aa,bb);assert delta==[row['declared_delta']],(row,delta)
   assert byrid[ee[0]['render_id']]['classification']!=byrid[ee[1]['render_id']]['classification'];pair_proofs.append({'unit_id':row['unit_id'],'family':row['family'],'recursive_diff':delta,'one_scalar_fact':True,'both_endpoints_mechanically_verified':True})
 a0=[g for g in gold if g['part']=='A' and g['level']==0];assert collections.Counter(g['classification'] for g in a0)=={c:2 for c in CLASSES}
 first=collections.Counter();bpositions=collections.Counter();blocks=[]
 for block in range(1,11):
  ee=sorted([e for e in entries if e['block']==block],key=lambda e:e['block_position']);assert len(ee)==7;aa=[e for e in ee if e['part']=='A'];bb=[e for e in ee if e['part']=='B'];assert len(aa)==5 and len(bb)==2
  assert {e['level'] for e in aa}==set(range(5));assert {byrid[e['render_id']]['classification'] for e in aa}==set(CLASSES);assert bb[0]['unit_id']==bb[1]['unit_id'];first[bb[0]['endpoint']]+=1;bpositions.update(e['block_position'] for e in bb);blocks.append({'block':block,'A_levels_once_each':True,'A_classes_once_each':True,'B_pair':bb[0]['unit_id'],'first_endpoint':bb[0]['endpoint']})
 assert first=={'A':5,'B':5};assert sorted(bpositions.values())==[2,3,3,3,3,3,3]
 assert manifest['schedule']==[e['render_id'] for e in sorted(entries,key=lambda e:e['call_order'])]
 return {'status':'PASS','scientific_calls_before_freeze':0,'materialized_files':len(files),'requests':70,'A_requests':50,'B_requests':20,'independent_semantic_checks':semantic,'ladder_proofs':ladder_proofs,'pair_proofs':pair_proofs,'schedule_blocks':blocks,'B_first_endpoint_counts':dict(first),'B_position_counts':dict(bpositions),'new_record_component_capture_ids':len(newids),'prior_id_overlap':0,'prior_exact_evidence_overlap':0,'prior_contract_overlap':0,'prior_decisive_tuple_overlap':0,'decisive_tuple_hashes':fingerprints,'mechanism_novelty':'Ten new operations versus both preserved mechanism inventories; no previous world/template imported. Generic ontology and capture/currentness relations reused intentionally. Mechanical non-overlap supplements author semantic review, not a proof of open-world novelty.','authorship_limitation':'Internally authored research-program cases; not independently authored external tasks; no open-world generalization claim.','no_tags_gold_proofs_compiler_in_inputs':True,'sha256':{n:hashlib.sha256(d).hexdigest() for n,d in files.items()}}
if __name__=='__main__':
 result=audit();(P/'preflight.json').write_bytes(raw(result));print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','independent_semantic_checks','ladder_proofs','pair_proofs','schedule_blocks','decisive_tuple_hashes')}))
