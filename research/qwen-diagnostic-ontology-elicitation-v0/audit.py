"""No-model preflight: regeneration, representation isolation, construction and novelty."""
import ast,collections,hashlib,json,re
from pathlib import Path
import jsonschema
from generate import P,CLASSES,SHORT,generate,digest,raw,SEED
ROOT=P.parents[1]
def audit():
 generated=generate();actual={str(f.relative_to(P/'materialized')):f.read_bytes() for f in (P/'materialized').rglob('*') if f.is_file()};assert generated==actual
 manifest=json.loads(actual['render-manifest.json']);gold=json.loads(actual['gold.json']);spec=json.loads((P/'case-spec.json').read_bytes());entries=manifest['entries'];maps=json.loads(actual['label-maps.json'])
 assert len(gold)==20 and len(entries)==len(manifest['schedule'])==len(set(manifest['schedule']))==100
 assert collections.Counter(g['classification'] for g in gold)=={c:4 for c in CLASSES}
 for c in CLASSES:assert collections.Counter(g['difficulty'] for g in gold if g['classification']==c)=={'primitive':2,'composite':2}
 assert collections.Counter(maps['assignment'].values())=={'0':10,'1':10};assert maps['mappings']['0']!=maps['mappings']['1']
 assert SEED!=417351046
 forbidden=['healthy','historical defect','insufficient evidence','invalid evidence','current defect','expected answer','mutation','difficulty','primitive','composite','gold']+CLASSES+[s['mechanism'] for s in spec]
 old=ROOT/'research/blind-diagnostic-generalization-v0/materialized';oldbytes=b'\n'.join(p.read_bytes() for p in sorted(old.rglob('*.json')));oldids=set(re.findall(rb'z[0-9a-f]{16}',oldbytes));newids=set();novelty=[];computed=[]
 oldrecordsets=[]
 def recordsets(x):
  if isinstance(x,dict):
   if isinstance(x.get('records'),list):oldrecordsets.append(raw(x['records']))
   for v in x.values():recordsets(v)
  elif isinstance(x,list):
   for v in x:recordsets(v)
 for p in old.rglob('*.json'):recordsets(json.loads(p.read_bytes()))
 old_families=['version_selection','authority_precedence','entity_binding','publication_update','operation_idempotence','boundary_comparison']
 for g in gold:
  w=g['world_id'];i=g['slot'];ev=json.loads(actual['evidence/'+w+'.json']);text=raw(ev).decode()
  for bad in forbidden:assert bad.lower() not in text.lower(),(w,bad)
  newids.update(re.findall(rb'z[0-9a-f]{16}',raw(ev)));assert raw(ev['records']) not in oldrecordsets
  assert w.encode() not in oldbytes
  ids=[r['id'] for r in ev['records']];assert len(ids)==len(set(ids));assert set(g['required_evidence_ids'])<=set(ids)
  relevant={r['id']:r for r in ev['records']};r=[relevant[x] for x in g['required_evidence_ids']];contract,inp,receipt=r[:3];proof=g['proof'];q=proof['q']
  if i<4:
   required=[q/1000,(q+17+240)%256,q-7,3*q+7][i];output_keys=['delivered_litres','trailer_octet','remaining_spaces','load_units'];observed=receipt[output_keys[i]]
   assert observed!=required and observed==proof['actual'] and required==proof['required'];ww=g['witness'];assert inp[ww['decisive_field'][1:]]==ww['observed_value'];assert inp['build']==receipt['build']==ev['scope']['deployed_build']
  elif i<8:
   required=[2,3,258,q+5][i-4];key=['credit_display','trays_used','unsigned_word','closing_packs'][i-4];assert receipt[key]==required==proof['required']==proof['actual']
  elif i<12:
   assert inp[proof['unknown_field']]=='UNKNOWN';assert proof['benign_required']==proof['actual'];assert proof['defect_required']!=proof['actual'];assert proof['benign_value']!=proof['defect_value']
   f=[lambda v:3*q+v,lambda v:10*v,lambda v:v*2**2,lambda v:q-v][i-8]
   assert f(proof['benign_value'])==proof['actual'] and f(proof['defect_value'])!=proof['actual']
  elif i<16:
   required=[(q+9+250)%256,q*60,q+1,q+1][i-12];key=['sample_trailer','register_seconds','ticket_units','checked_out_fixtures'][i-12]
   assert receipt[key]==required and r[3][key]!=required;assert inp['build']==receipt['build']==ev['scope']['deployed_build'];assert r[3]['build']==ev['scope']['earlier_build']!=ev['scope']['deployed_build']
  else:
   key=proof['incompatible_field'];assert inp['sealed_object']==receipt['sealed_object'];assert inp['snapshot']==receipt['snapshot'];assert inp[key]!=receipt[key]
  if g['difficulty']=='primitive':assert len(ev['records'])<=4
  else:assert len(ev['records'])==len(g['required_evidence_ids'])+3
  er=[e for e in entries if e['world_id']==w];assert {e['arm'] for e in er}==set('ABCDE') and len(er)==5
  req={e['arm']:json.loads(actual[e['request_path']]) for e in er}
  for e in er:
   a=e['arm'];request=req[a];assert hashlib.sha256(actual[e['request_path']]).hexdigest()==e['request_sha256'];assert len(request['messages'])==2;assert request['messages'][1]['content'].split('Raw evidence:\n')[1]==text;assert request['seed']==SEED
   assert request['cache_prompt'] is False and request['max_tokens']==2048 and 'tools' not in request
   jsonschema.Draft7Validator.check_schema(request['response_format']['schema'])
   assert w not in request['messages'][1]['content'];assert g['mechanism'] not in request['messages'][1]['content']
  a=req['A'];b=req['B'];lines=a['messages'][1]['content'].splitlines();altered=lines[:1]+list(reversed(lines[1:6]))+lines[6:];reconstructed='\n'.join(altered)+'\n';assert b['messages'][1]['content']==reconstructed
  b['messages'][1]['content']=a['messages'][1]['content'];assert a==b
  c=req['C'];mapping=maps['mappings'][maps['assignment'][w]]
  for natural,opaque in mapping.items():
   assert natural not in c['messages'][1]['content'];c['messages'][1]['content']=c['messages'][1]['content'].replace(opaque+': ',natural+': ')
  c['response_format']['schema']['properties']['classification']['enum']=CLASSES;assert c==a
  assert req['E']['response_format']['schema']==json.loads((P/'schema-E.json').read_bytes())
  novelty.append({'world_id':w,'mechanism':g['mechanism'],'not_r2_mechanism':True,'comparison':'Arithmetic/conservation/immutable-capture operation; no selection, precedence, binding, publication, replay-deduplication or threshold-boundary decision. T uses deployment facts only to establish currentness.'})
  computed.append({'world_id':w,'class':g['classification'],'proof_check':'PASS'})
 assert not newids&oldids
 positions={a:dict(collections.Counter(e['arm_position'] for e in entries if e['arm']==a)) for a in 'ABCDE'}
 for counts in positions.values():assert counts=={p:4 for p in range(1,6)}
 for name in ('generate.py','transport.py','run_campaign.py','guard.py'):
  source=(P/name).read_text();tree=ast.parse(source)
  imports=[n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
  assert 'score' not in imports and 'scorer' not in imports
  if name=='generate.py':
   for bad in ('blind-diagnostic-generalization','compiler','raw/finals','scores.json'):assert bad not in source
 assert (P/'schema-E.json').read_bytes()==(ROOT/'research/blind-diagnostic-generalization-v0/diagnostic-schema.json').read_bytes()
 hashes={name:hashlib.sha256(data).hexdigest() for name,data in actual.items()}
 return {'status':'PASS','real_model_calls':0,'worlds':20,'calls':100,'class_counts':dict(collections.Counter(g['classification'] for g in gold)),'difficulty_counts':dict(collections.Counter(g['difficulty'] for g in gold)),'exact_regeneration_files':len(actual),'arm_positions':positions,'opaque_mapping_counts':dict(collections.Counter(maps['assignment'].values())),'new_ids':len(newids),'r2_id_overlap':0,'r2_record_set_overlap':0,'mechanism_novelty_review':novelty,'construction_checks':computed,'ontology_reuse':'Five class definitions retained unchanged; generic record/component/build/ID grammar and full E schema retained. Operational cases independently generated. Semantic novelty combines template review and arithmetic checks; byte non-overlap alone is not a semantic proof.','no_gold_compiler_prior_output_in_requests':True,'scorer_independent_schedule':True,'sha256':hashes}
if __name__=='__main__':
 result=audit();(P/'preflight.json').write_bytes(raw(result));print(json.dumps({k:v for k,v in result.items() if k not in ('sha256','mechanism_novelty_review','construction_checks')}))
