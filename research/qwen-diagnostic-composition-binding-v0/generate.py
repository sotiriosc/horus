"""Fresh authored evidence generation; no compiler, prior cases or model outputs."""
import argparse,copy,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent;SEED=384206917
CLASSES=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE'];SHORT=dict(zip('DHUTX',CLASSES))
DEFS=['Available current evidence supports a specific active structural or mechanical defect and distinguishes it from materially plausible benign alternatives.','The internally valid evidence is sufficient within the declared contract/input scope and supports no current defect. Unusual or undesirable behavior alone is insufficient.','The evidence is internally valid but a current defect and a materially plausible benign explanation remain observationally indistinguishable.','A defect is demonstrated for an older version, while supplied current mechanisms and observations show it is no longer active within the stated scope.','The supplied evidence package contains incompatible immutable, version, capture or provenance facts and cannot support a valid operational diagnosis.']
SCHEMA={'type':'object','properties':{'classification':{'enum':CLASSES}},'required':['classification'],'additionalProperties':False}
OUT=['emitted_hex','expanded_glyphs','emitted_octet','shifted_letters','emitted_codewords','emitted_matrix','remaining_stack','unsigned_code','emitted_keys','emitted_divmod']
IN=[['source_octets'],['glyph_runs'],['source_octet','whitening_mask'],['source_letters','displacement'],['source_symbols','codewords'],['source_matrix'],['stack_items'],['signed_integer'],['source_keys'],['dividend','divisor']]
TAGS_A={1:'COMPONENT_BINDING',2:'VERSION_BINDING',3:'REDUNDANT_EVIDENCE',4:'TARGET_VS_DISTRACTOR'};FAMILIES=['H_D','H_U','D_T','H_X','U_D'];TAGS_B=dict(zip(FAMILIES,['VALUE_DEPENDENCY','UNKNOWN_DEPENDENCY','CURRENTNESS','PROVENANCE_IDENTITY','UNKNOWN_DEPENDENCY']))
def digest(*p):return hashlib.sha256('|'.join(map(str,(SEED,)+p)).encode()).hexdigest()
def raw(x):return (json.dumps(x,indent=2,ensure_ascii=True)+'\n').encode()
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def identifier(part,i,role):return 'k'+digest(part,i,role)[:16]
def unitid(part,i):return 'u'+digest('unit',part,i)[:12]
def replace_at(obj,path,value):
 target=obj
 for key in path[:-1]:target=target[key]
 target[path[-1]]=value

def calculate(i,v):
 if i==0:return ''.join('cbea' if b==202 else format(b,'02x') for b in v['source_octets'])
 if i==1:return ''.join(g*n for g,n in v['glyph_runs'])
 if i==2:return v['source_octet']^v['whitening_mask']
 if i==3:return ''.join(chr(65+(ord(c)-65+v['displacement'])%26) for c in v['source_letters'])
 if i==4:return ''.join(v['codewords'][c] for c in v['source_symbols'])
 if i==5:return [list(a) for a in zip(*v['source_matrix'])]
 if i==6:return v['stack_items'][:-1]
 if i==7:return 2*v['signed_integer'] if v['signed_integer']>=0 else -2*v['signed_integer']-1
 if i==8:return sorted(v['source_keys'])
 if i==9:
  q,r=divmod(v['dividend'],v['divisor']);return {'quotient':q,'residue':r}

def unknown_path(part,i):
 return {('A',4):['source_symbols',1],('A',5):['source_matrix',0,1],('B',2):['source_octet'],('B',3):['displacement'],('B',8):['source_keys',1],('B',9):['dividend']}.get((part,i))
def known_inputs(part,i,param):
 inp={k:copy.deepcopy(param[k]) for k in IN[i]};path=unknown_path(part,i)
 if path:replace_at(inp,path,param['benign'])
 return inp

def base_world(part,i,spec):
 mechanism=spec['mechanisms'][i];param=spec['part_'+part.lower()+'_parameters'][i];comp=identifier(part,i,'target-component');build=identifier(part,i,'current-build');older=identifier(part,i,'earlier-build');source_id=identifier(part,i,'source');receipt_id=identifier(part,i,'receipt');contract_id=identifier(part,i,'contract');capture=identifier(part,i,'source-capture')
 source={'kind':'source','component_id':comp,'build':build,'capture_id':capture,'capture_rule':'One immutable source capture; every attestation with this capture_id asserts exactly the same source fields.'};source.update({k:copy.deepcopy(param[k]) for k in IN[i]})
 contract={'kind':'contract','component_id':comp,'rule':mechanism['contract'],'attestation_rule':'Attestations for one immutable capture have equal standing. No attestation is preferred, superseded or provisional; no other source is available.'}
 receipt={'kind':'receipt','component_id':comp,'build':build,'source_ref':source_id,'capture_id':identifier(part,i,'output-capture')}
 v=known_inputs(part,i,param);correct=calculate(i,v)
 if part=='A' and i in (0,1,4,5):observed=copy.deepcopy(param[OUT[i]])
 elif part=='B' and i in (8,9):observed=copy.deepcopy(param[OUT[i]])
 else:observed=correct
 receipt[OUT[i]]=observed
 records={contract_id:contract,source_id:source,receipt_id:receipt}
 scope={'component_id':comp,'deployed_build':build,'operation':mechanism['part_'+part.lower()+'_domain'],'bounded_scope':'Exactly the supplied target operation. Source captures and output receipts are exact observations, without hidden transforms, lost data, unlisted operations or adjustments. Different components are separately scoped. The operational contract specifies required behavior; it does not assert that an implementation obeyed it.'}
 old_id=None;attestation_id=None
 historical=(part=='A' and i in (6,7)) or (part=='B' and i in (4,5))
 if historical:
  old_id=identifier(part,i,'earlier-receipt');old=copy.deepcopy(receipt);old.update(build=older,capture_id=identifier(part,i,'earlier-output-capture'),build_relation='This build was created before the other supplied build. Both traces use the listed source values.');old[OUT[i]]=copy.deepcopy(param['old_output']);records[old_id]=old
  source.pop('build') # The two builds use exactly this captured source, independent of deployment.
  if part=='B':scope['deployed_build']=older
 contradiction=(part=='A' and i in (8,9)) or (part=='B' and i in (6,7))
 if contradiction:
  attestation_id=identifier(part,i,'source-attestation');other=copy.deepcopy(source);other['kind']='source_attestation';records[attestation_id]=other
  if part=='A':
   if i==8:other['source_keys'][0]=param['conflicting_key']
   else:other['dividend']=param['conflicting_dividend']
 ev={'scope':scope,'records':records}
 meta={'part':part,'unit_id':unitid(part,i),'mechanism_index':i,'mechanism':mechanism['name'],'component_id':comp,'contract_id':contract_id,'source_id':source_id,'receipt_id':receipt_id,'earlier_receipt_id':old_id,'attestation_id':attestation_id,'newer_build':build,'earlier_build':older,'output_field':OUT[i]}
 return ev,meta

def distractors(part,i,spec):
 param=spec['part_'+part.lower()+'_parameters'][i];v=known_inputs(part,i,param);comp=identifier(part,i,'neighbor-component');build=identifier(part,i,'neighbor-current-build');source_id=identifier(part,i,'neighbor-source');out=calculate(i,v)
 level1={identifier(part,i,'neighbor-contract'):{'kind':'contract','component_id':comp,'rule':spec['mechanisms'][i]['contract'],'in_service_build':build,'scope_note':'Independent component. These inputs and outputs do not govern any other component.'},source_id:dict(kind='source',component_id=comp,build=build,capture_id=identifier(part,i,'neighbor-capture'),**v),identifier(part,i,'neighbor-receipt'):{'kind':'receipt','component_id':comp,'build':build,'source_ref':source_id,OUT[i]:out}}
 old=copy.deepcopy(level1[identifier(part,i,'neighbor-receipt')]);old.update(build=identifier(part,i,'neighbor-old-build'),capture_id=identifier(part,i,'neighbor-old-output'),build_relation='Earlier non-current branch of this independent component; in_service_build remains the one in its contract record.')
 bad=copy.deepcopy(out)
 if isinstance(bad,str):bad=bad+'00'
 elif isinstance(bad,int):bad+=23
 elif isinstance(bad,list):bad=list(reversed(bad))
 else:bad['residue']+=23
 old[OUT[i]]=bad
 level2={identifier(part,i,'neighbor-earlier-receipt'):old}
 comp2=identifier(part,i,'observer-component')
 level4={identifier(part,i,'observer-record'):{'kind':'observer_status','component_id':comp2,'display_caption':'copper-lantern','completed_panels':811+i},identifier(part,i,'reporting-relation'):{'kind':'reporting_relation','component_id':comp,'reports_counters_to':comp2,'relation_scope':'Display counters only. This is not a computation or data dependency of the target component.'},identifier(part,i,'counter-record'):{'kind':'work_counter','component_id':comp2,'inspection_window':'window-'+digest(part,i,'window')[:7],'panel_capacity':947+i}}
 return level1,level2,level4

def proof(ev,meta,gold,param):
 i=meta['mechanism_index'];source=ev['records'][meta['source_id']];current_receipts=[(key,record) for key,record in ev['records'].items() if record.get('kind')=='receipt' and record.get('component_id')==meta['component_id'] and record.get('build')==ev['scope']['deployed_build']];assert len(current_receipts)==1;current_receipt_id,receipt=current_receipts[0];path=unknown_path(meta['part'],i);out={'contract_sentence':ev['records'][meta['contract_id']]['rule'],'decisive_records':[meta[k] for k in ('contract_id','source_id','receipt_id','earlier_receipt_id','attestation_id') if meta[k]],'deployed_build':ev['scope']['deployed_build'],'gold':gold,'current_receipt_id':current_receipt_id,'observed_output':receipt[OUT[i]],'scope_excludes':'Hidden transforms, lost data and unlisted target operations; other components are independent.'}
 explanations={'D':'The active build has an exact source and an output unequal to the operational requirement; no supplied benign transformation is allowed.','H':'The active build output equals the complete operational requirement; no unresolved required source fact or immutable-capture conflict is present.','U':'The missing source leaf has a permitted benign completion and a permitted violating completion with the same observed output; no capture assertion supplies the missing value.','T':'The older supplied build violates the same contract; the explicitly deployed newer build has a compliant receipt for the same inputs.','X':'Two equal-standing attestations of one immutable source capture disagree; selecting either as the operational truth would require evidence not supplied.'}
 short=next(k for k,v in SHORT.items() if v==gold);out['author_argument']=explanations[short]
 if path:
  completions={}
  for label in ('benign','defect'):
   candidate={k:copy.deepcopy(source[k]) for k in IN[i]};replace_at(candidate,path,param[label]);completions[label]={'source_leaf':param[label],'required_output':calculate(i,candidate)}
  out['alternative_completions']=completions;out['critical_source_leaf']=path
 if 'UNKNOWN' not in canon({k:source[k] for k in IN[i]}):out['contract_required_output']=calculate(i,source)
 return out

SYSTEM='Analyze only the supplied bounded system evidence. Do not invent missing facts or silently reconcile contradictory capture facts. Apply the supplied class definitions. Return exactly one JSON object satisfying the supplied response schema. No tools, external knowledge lookup, system changes, interventions or solution proposals.'
FRAME='Class definitions:\n'+'\n'.join(c+': '+d for c,d in zip(CLASSES,DEFS))+'\n\nReturn only the classification object. No rationale, citations or other prose.\n\nRaw evidence:\n'
def generate():
 spec=json.loads((P/'case-spec.json').read_bytes());files={};entries=[];gold=[];core_ids=[];pair_ids=[];structural=[]
 def emit(ev,meta,label,suffix,**extra):
  rid=digest('render',meta['part'],meta['unit_id'],suffix)[:20];text=raw(ev);task={'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':FRAME+text.decode()}],'response_schema':SCHEMA}
  request={'messages':task['messages'],'response_format':{'type':'json_object','schema':SCHEMA},'temperature':.2,'top_p':.9,'top_k':40,'min_p':.05,'seed':SEED,'max_tokens':2048,'cache_prompt':False,'stream':False,'chat_template_kwargs':{'enable_thinking':True}}
  files['evidence/'+rid+'.json']=text;files['neutral/'+rid+'.json']=raw(task);files['requests/'+rid+'.json']=raw(request)
  entry=dict(render_id=rid,part=meta['part'],unit_id=meta['unit_id'],request_path='requests/'+rid+'.json',request_sha256=hashlib.sha256(raw(request)).hexdigest(),**extra);entries.append(entry)
  param=spec['part_'+meta['part'].lower()+'_parameters'][meta['mechanism_index']]
  gold.append(dict(meta,render_id=rid,classification=label,proof=proof(ev,meta,label,param),**extra));return rid
 for i in range(10):
  ev,meta=base_world('A',i,spec);label=SHORT[spec['mechanisms'][i]['part_a_class']];core_ids.append(meta['unit_id']);l1,l2,l4=distractors('A',i,spec)
  att=copy.deepcopy(ev['records'][meta['receipt_id']]);att['kind']='output_attestation';att['attests_record']=meta['receipt_id'];l3={identifier('A',i,'redundant-output'):att}
  for level,addition in enumerate(({},l1,l2,l3,l4)):
   ev['records'].update(addition);emit(copy.deepcopy(ev),meta,label,str(level),level=level,tag=TAGS_A.get(level))
  structural.append({'part':'A','unit_id':meta['unit_id'],'decisive_record_ids':[meta[k] for k in ('contract_id','source_id','receipt_id','earlier_receipt_id','attestation_id') if meta[k]],'expected_additions':[0,3,1,1,3]})
 for i in range(10):
  a,meta=base_world('B',i,spec);pair_ids.append(meta['unit_id']);param=spec['part_b_parameters'][i];l1,l2,_=distractors('B',i,spec);a['records'].update(l1);a['records'].update(l2);b=copy.deepcopy(a)
  if i in (0,1):path=['records',meta['receipt_id'],OUT[i]];value=param['changed_output']
  elif i in (2,3):path=['records',meta['source_id']]+unknown_path('B',i);value='UNKNOWN'
  elif i in (4,5):path=['scope','deployed_build'];value=meta['newer_build']
  elif i==6:path=['records',meta['attestation_id'],'stack_items',2];value=param['conflicting_item']
  elif i==7:path=['records',meta['attestation_id'],'signed_integer'];value=param['conflicting_integer']
  else:path=['records',meta['source_id']]+unknown_path('B',i);value=param['defect']
  replace_at(b,path,value);family=spec['mechanisms'][i]['part_b_contrast'];left,right=family.split('_')
  for endpoint,ev,label in (('A',a,SHORT[left]),('B',b,SHORT[right])):emit(ev,meta,label,endpoint,endpoint=endpoint,family=family,tag=TAGS_B[family])
  structural.append({'part':'B','unit_id':meta['unit_id'],'family':family,'declared_delta':'/'+'/'.join(map(str,path))})
 levels=sorted(range(5),key=lambda x:digest('level-order',x));families=sorted(range(5),key=lambda x:digest('family-order',FAMILIES[x]));positions=[(0,3),(1,4),(2,5),(3,6),(4,0),(5,1),(6,2),(0,4),(1,5),(2,6)];schedule=[]
 for block in range(10):
  rep=block//5;arows=[]
  for c in range(5):
   unit=core_ids[2*c+rep];level=levels[(block%5+c)%5];arows.append(next(e for e in entries if e['part']=='A' and e['unit_id']==unit and e['level']==level))
  arows.sort(key=lambda e:digest('within-block',block,e['unit_id']));family_index=families[block%5];pair=pair_ids[2*family_index+rep];endpoint_order=['A','B'] if (family_index+rep)%2==0 else ['B','A'];brows=[next(e for e in entries if e['part']=='B' and e['unit_id']==pair and e['endpoint']==x) for x in endpoint_order];placements=dict(zip(sorted(positions[block]),brows));ai=0
  for pos in range(7):
   if pos in placements:e=placements[pos]
   else:e=arows[ai];ai+=1
   e.update(block=block+1,block_position=pos+1,call_order=len(schedule)+1);schedule.append(e['render_id'])
 files['gold.json']=raw(gold);files['structure-spec.json']=raw(structural);files['render-manifest.json']=raw({'seed':SEED,'level_permutation':levels,'family_permutation':[FAMILIES[i] for i in families],'schedule':schedule,'entries':entries});return files
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
 for name,data in generate().items():p=args.out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 print('Materialized 10 ladders / 50 requests and 10 pairs / 20 requests; zero model calls.')
