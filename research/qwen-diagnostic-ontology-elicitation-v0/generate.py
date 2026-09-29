"""Prospectively specified fresh templates. Reads only this study's method assets."""
import argparse,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
SEED=731926581
CLASSES=['SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE']
DEFS=[
'Available current evidence supports a specific active structural or mechanical defect and distinguishes it from materially plausible benign alternatives.',
'The internally valid evidence is sufficient within the declared contract/input scope and supports no current defect. Unusual or undesirable behavior alone is insufficient.',
'The evidence is internally valid but a current defect and a materially plausible benign explanation remain observationally indistinguishable.',
'A defect is demonstrated for an older version, while supplied current mechanisms and observations show it is no longer active within the stated scope.',
'The supplied evidence package contains incompatible immutable, version, capture or provenance facts and cannot support a valid operational diagnosis.']
SHORT=dict(zip('DHUTX',CLASSES))
def digest(*parts):return hashlib.sha256('|'.join(map(str,(SEED,)+parts)).encode()).hexdigest()
def raw(x):return (json.dumps(x,indent=2,ensure_ascii=True)+'\n').encode()
def ident(slot,role):return 'z'+digest('record',slot,role)[:16]
def worldid(slot):return 'w'+digest('world',slot)[:12]
def make_world(s):
 i=s['slot'];q=11+int(digest('quantity',i)[:8],16)%19;comp=ident(i,'component');build='build-'+digest('build',i)[:8]
 contract={'id':ident(i,'contract'),'component_id':comp}
 inp={'id':ident(i,'calculation'),'component_id':comp,'build':build}
 receipt={'id':ident(i,'receipt'),'component_id':comp,'build':build,'calculation_ref':inp['id']}
 proof={'q':q,'mechanism':s['mechanism'],'concept':s['class'],'difficulty':s['difficulty']}
 decisive=None;old=None
 if i==0:
  contract.update(rule='Convert measured millilitres to litres by division by exactly 1000. No rounding, clamping or other transformation is permitted.')
  inp.update(dose_millilitres=q,applied_divisor=1,executed_expression='dose_millilitres / applied_divisor')
  receipt.update(delivered_litres=q);decisive=('applied_divisor',1,1000);proof.update(required=q/1000,actual=q)
 elif i==1:
  contract.update(rule='The trailer is the sum of the three octets modulo 256. The additive bias is exactly zero.')
  inp.update(frame_octets=[q,17,240],applied_bias=1,executed_expression='(sum(frame_octets) + applied_bias) modulo 256')
  actual=(q+17+240+1)%256;receipt.update(trailer_octet=actual);decisive=('applied_bias',1,0);proof.update(required=(q+17+240)%256,actual=actual)
 elif i==2:
  contract.update(rule='For this reservation, remaining pallet spaces must equal opening spaces minus all seven newly committed spaces. No release, expiry or other transaction occurred in this operation.')
  inp.update(opening_spaces=q,committed_spaces=7,applied_decrement=0,executed_expression='opening_spaces - applied_decrement')
  receipt.update(remaining_spaces=q);decisive=('applied_decrement',0,7);proof.update(required=q-7,actual=q)
 elif i==3:
  contract.update(rule='This calibration converts the raw count to load units by 3 times raw count plus 7. Exact integer arithmetic; intercept must be 7.')
  inp.update(raw_count=q,applied_gain=3,applied_intercept=0,executed_expression='applied_gain * raw_count + applied_intercept')
  receipt.update(load_units=3*q);decisive=('applied_intercept',0,7);proof.update(required=3*q+7,actual=3*q)
 elif i==4:
  contract.update(rule='Display the nearest integer credit; exact halves go to the even integer. Decreasing a positive half to an even integer is permitted.')
  inp.update(credit_exact=2.5,executed_expression='round to nearest integer, ties to even')
  receipt.update(credit_display=2);proof.update(required=2,actual=2)
 elif i==5:
  contract.update(rule='Use the fewest trays holding at most three parcels each. A partially occupied final tray is allowed and must count as one tray.')
  inp.update(parcel_quantity=7,tray_capacity=3,executed_expression='ceiling(parcel_quantity / tray_capacity)')
  receipt.update(trays_used=3,last_tray_occupancy=1);proof.update(required=3,actual=3)
 elif i==6:
  contract.update(rule='For this component the first octet is the high octet and the second is low. The unsigned word equals 256 times first plus second. Neighboring components have their own independent encoding.')
  inp.update(first_octet=1,second_octet=2,executed_expression='256 * first_octet + second_octet')
  receipt.update(unsigned_word=258);proof.update(required=258,actual=258)
 elif i==7:
  contract.update(rule='Closing seed packs equal opening packs plus all received packs minus all dispatched packs. All flows for this operation are listed; no losses or adjustments occurred.')
  inp.update(opening_packs=q,received_packs=9,dispatched_packs=4,executed_expression='opening_packs + received_packs - dispatched_packs')
  receipt.update(closing_packs=q+5);proof.update(required=q+5,actual=q+5)
 elif i==8:
  contract.update(rule='The specified displacement equals 3 times sample count plus deployment_offset. The contract permits any integer deployment_offset from 0 through 10; its configured value for this deployment was not captured.')
  inp.update(sample_count=q,deployment_offset='UNKNOWN',applied_offset=0,executed_expression='3 * sample_count + applied_offset')
  receipt.update(displacement_units=3*q);proof.update(actual=3*q,unknown_field='deployment_offset',benign_value=0,benign_required=3*q,defect_value=7,defect_required=3*q+7)
 elif i==9:
  contract.update(rule='Elapsed milliseconds must equal tick count times the configured milliseconds_per_tick. Any positive integer period is permitted, but this package does not record which period was configured.')
  inp.update(tick_count=10,milliseconds_per_tick='UNKNOWN',applied_tick_period=2,executed_expression='tick_count * applied_tick_period')
  receipt.update(elapsed_milliseconds=20);proof.update(actual=20,unknown_field='milliseconds_per_tick',benign_value=2,benign_required=20,defect_value=3,defect_required=30)
 elif i==10:
  contract.update(rule='Delay for attempt number n equals configured base_delay times 2 to power n. Any positive integer base is allowed. The configured base for this transmission stream was not retained; no jitter or cap applies.')
  inp.update(attempt_number=2,base_delay='UNKNOWN',applied_base=10,executed_expression='applied_base * 2 ** attempt_number')
  receipt.update(delay_milliseconds=40);proof.update(actual=40,unknown_field='base_delay',benign_value=10,benign_required=40,defect_value=12,defect_required=48)
 elif i==11:
  contract.update(rule='Remaining rack positions equal opening positions minus the positions reserved by this transaction. Reservations are nonnegative integers no greater than opening positions. The reservation count is missing from this capture; no release or other change occurred.')
  inp.update(opening_positions=q,reserved_positions='UNKNOWN',applied_reservation=5,executed_expression='opening_positions - applied_reservation')
  receipt.update(remaining_positions=q-5);proof.update(actual=q-5,unknown_field='reserved_positions',benign_value=5,benign_required=q-5,defect_value=8,defect_required=q-8)
 elif i in (12,13,14,15):
  old={'id':ident(i,'earlier-receipt'),'component_id':comp,'build':'build-'+digest('old-build',i)[:8],'capture_relation':'Earlier execution of this same bounded operation; this build is not deployed now.'}
  if i==12:
   contract.update(rule='Compute the trailer as sum of the three sample octets modulo 256, with zero additive bias, on either build.')
   inp.update(sample_octets=[q,9,250],applied_increment=0,executed_expression='(sum(sample_octets) + applied_increment) modulo 256')
   v=(q+9+250)%256;receipt.update(sample_trailer=v);old.update(sample_octets=[q,9,250],applied_increment=1,executed_expression='(sum(sample_octets) + applied_increment) modulo 256',sample_trailer=(v+1)%256)
   proof.update(required=v,actual=v,old_actual=(v+1)%256)
  elif i==13:
   contract.update(rule='The register stores seconds, exactly sixty times the requested minutes. This requirement is the same on both builds.')
   inp.update(requested_minutes=q,applied_multiplier=60,executed_expression='requested_minutes * applied_multiplier')
   receipt.update(register_seconds=q*60);old.update(requested_minutes=q,applied_multiplier=1,executed_expression='requested_minutes * applied_multiplier',register_seconds=q)
   proof.update(required=q*60,actual=q*60,old_actual=q)
  elif i==14:
   contract.update(rule='Round positive fractional tariff units to nearest integer, with exact halves rounded upward. Both builds have this contract.')
   inp.update(tariff_units=q+.5,rounding_mode='nearest, halves upward',executed_expression='floor(tariff_units + 0.5)')
   receipt.update(ticket_units=q+1);old.update(tariff_units=q+.5,rounding_mode='floor',executed_expression='floor(tariff_units)',ticket_units=q)
   proof.update(required=q+1,actual=q+1,old_actual=q)
  else:
   contract.update(rule='At completion the checked-out fixture count equals opening count plus four acquisitions minus three releases. All acquisitions and releases completed exactly once, no other transactions or failures occurred. Same rule on both builds.')
   inp.update(opening_fixtures=q,acquired_fixtures=4,released_fixtures=3,executed_expression='opening_fixtures + acquired_fixtures - released_fixtures')
   receipt.update(checked_out_fixtures=q+1);old.update(opening_fixtures=q,acquired_fixtures=4,released_fixtures=3,executed_expression='opening_fixtures + acquired_fixtures',checked_out_fixtures=q+4)
   proof.update(required=q+1,actual=q+1,old_actual=q+4)
 else:
  field=['charge_cents','mint_epoch','lease_holder','utc_milliseconds'][i-16]
  val=[q,1700000000+q,'spooler-amber',1700000000000+q][i-16];other=val+1 if isinstance(val,int) else 'spooler-indigo'
  details=[
   'The sealed ledger entry has one immutable integer charge_cents. Projections of the same sealed entry and snapshot preserve that integer exactly.',
   'The token bytes are immutable with one canonical, unambiguous integer mint_epoch field. Decodings of the identical token bytes and snapshot preserve that field exactly.',
   'The queue snapshot has exactly one lease_holder. Complete attestations of that same immutable snapshot give that same holder; these are not observations before and after a transfer.',
   'The event has exactly one canonical UTC utc_milliseconds field. Attestations of the same immutable event and snapshot preserve that integer exactly; no local timezone conversion is involved.'][i-16]
  contract.update(rule=details,attestation_scope='Both supplied attestations claim complete exact capture of this same immutable object at this same snapshot. Neither is designated as preferred, superseded or provisional. No further source is available.')
  obj='object-'+digest('sealed-object',i)[:8];snap='snapshot-'+digest('snapshot',i)[:8]
  inp={'id':ident(i,'attestation-one'),'component_id':comp,'build':build,'sealed_object':obj,'snapshot':snap,'attests_exact_capture':True,field:val}
  receipt={'id':ident(i,'attestation-two'),'component_id':comp,'build':build,'sealed_object':obj,'snapshot':snap,'attests_exact_capture':True,field:other}
  proof.update(incompatible_field=field,first_value=val,second_value=other,same_immutable_identity=True)
 records=[contract,inp,receipt]+([old] if old else [])
 required=[r['id'] for r in records]
 if s['difficulty']=='composite':
  othercomp=ident(i,'neighbor-component')
  records.extend([
   {'id':ident(i,'neighbor-contract'),'component_id':othercomp,'rule':'This independent component reports local processing counters; its settings do not govern the scoped component.','neighbor_setting':513 if i!=6 else 'low octet first'},
   {'id':ident(i,'neighbor-earlier'),'component_id':othercomp,'counter_window':'earlier','completed_units':q+2,'dropped_units':0},
   {'id':ident(i,'neighbor-later'),'component_id':othercomp,'counter_window':'later','previous_receipt_ref':ident(i,'neighbor-earlier'),'completed_units':q+5,'dropped_units':0}])
 scope={'component_id':comp,'deployed_build':build,'operation':s['domain'],'boundary':'Exactly the supplied target operation and its stated inputs. The executed expressions and recorded outputs are exact; no hidden postprocessing, rounding, transport loss or unlisted adjustment applies except rounding explicitly required by the contract. Other components are separately scoped.'}
 if old:scope['earlier_build']=old['build']
 records.sort(key=lambda r:digest('record-order',worldid(i),r['id']))
 evidence={'scope':scope,'records':records}
 gold={'world_id':worldid(i),'slot':i,'classification':SHORT[s['class']],'difficulty':s['difficulty'],'mechanism':s['mechanism'],'required_evidence_ids':required,'proof':proof}
 if decisive:
  field,observed,required_value=decisive
  gold['witness']={'affected_component_ids':[comp],'contract_evidence_id':contract['id'],'cause_evidence_id':inp['id'],'effect_evidence_id':receipt['id'],'decisive_evidence_id':inp['id'],'decisive_field':'/'+field,'observed_value':observed,'required_value':required_value}
 return evidence,gold

SYSTEM='Analyze only the supplied bounded system evidence. Do not invent missing facts or silently reconcile contradictory capture facts. Apply the supplied class definitions. Return exactly one JSON object satisfying the supplied response schema. No tools, external knowledge lookup, system changes, interventions or solution proposals.'
MINIMAL='Return only the classification object. No rationale, citations or other prose.'
FULL='Return classification, affected_component_ids (one responsible component for a current defect), evidence_ids, observed, inferred, unknown, diagnostic_statement, causal_mechanism, strongest_alternative_explanation and falsifier, satisfying the schema. Separate observed facts from inference and unknowns. For a current defect link the governing contract, operative input/calculation and resulting receipt with exact record IDs; identify one decisive field as a top-level JSON pointer within its record, its observed value and contract-required value. Cite all witness records in evidence_ids. For other classes cite the records establishing the conclusion; for a historical conclusion include earlier and deployed traces. Give no solution or modification. Prose cannot override structured fields.'
def generate():
 spec=json.loads((P/'case-spec.json').read_bytes());e_schema=json.loads((P/'schema-E.json').read_bytes())
 maps={str(n):dict(zip(CLASSES,sorted(['K7','M2','R9','T4','V6'],key=lambda l:digest('mapping-'+str(n),l)))) for n in range(2)}
 assert maps['0']!=maps['1']
 ids=[worldid(s['slot']) for s in spec]
 assignments={w:str(k%2) for k,w in enumerate(sorted(ids,key=lambda w:digest('map-assignment',w)))}
 files={};golds=[];entries=[];byworld={}
 for s in spec:
  evidence,gold=make_world(s);w=gold['world_id'];golds.append(gold);files['evidence/'+w+'.json']=raw(evidence);byworld[w]={}
  for arm in 'ABCDE':
   labels=maps[assignments[w]] if arm=='C' else dict(zip(CLASSES,CLASSES))
   lines=[labels[c]+': '+d for c,d in zip(CLASSES,DEFS)]
   if arm=='B':lines.reverse()
   schema={'type':'object','properties':{'classification':{'enum':[labels[c] for c in CLASSES]}},'required':['classification'],'additionalProperties':False}
   instruction=MINIMAL
   if arm=='D':
    schema['properties']['rationale']={'type':'string','minLength':1,'maxLength':500};schema['required'].append('rationale')
    instruction='Return only classification and a rationale of at most 500 characters. No witness IDs, JSON pointers, intervention or solution.'
   if arm=='E':schema=e_schema;instruction=FULL
   user='Class definitions:\n'+'\n'.join(lines)+'\n\n'+instruction+'\n\nRaw evidence:\n'+raw(evidence).decode()
   req={'messages':[{'role':'system','content':SYSTEM},{'role':'user','content':user}], 'response_format':{'type':'json_object','schema':schema},'temperature':.2,'top_p':.9,'top_k':40,'min_p':.05,'seed':SEED,'max_tokens':2048,'cache_prompt':False,'stream':False,'chat_template_kwargs':{'enable_thinking':True}}
   rid=digest('render',w,arm)[:20];payload=raw(req);files['requests/'+rid+'.json']=payload;byworld[w][arm]=rid
   entries.append({'render_id':rid,'world_id':w,'arm':arm,'mapping':assignments[w] if arm=='C' else None,'definition_order':'reverse' if arm=='B' else 'forward','request_path':'requests/'+rid+'.json','request_sha256':hashlib.sha256(payload).hexdigest()})
 order=sorted(ids,key=lambda w:digest('world-order',w));base=sorted('ABCDE',key=lambda a:digest('arm-order',a));schedule=[]
 for i,w in enumerate(order):
  arms=base[i%5:]+base[:i%5]
  for position,arm in enumerate(arms,1):
   rid=byworld[w][arm];schedule.append(rid)
   entry=next(e for e in entries if e['render_id']==rid);entry.update(world_position=i+1,arm_position=position,call_order=len(schedule))
 files['gold.json']=raw(golds);files['label-maps.json']=raw({'seed':SEED,'mappings':maps,'assignment':assignments})
 files['render-manifest.json']=raw({'seed':SEED,'base_arm_order':base,'schedule':schedule,'entries':entries})
 return files
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);args=a.parse_args();args.out.mkdir(parents=True,exist_ok=False)
 for name,data in generate().items():
  dest=args.out/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 print('Materialized 20 worlds and 100 requests; no model access.')
