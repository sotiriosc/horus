"""Pure synthetic records. No external execution, receipts, agents or models."""
from copy import deepcopy
from hashlib import sha256
import json
STUDY='blind-diagnostic-generalization-v0'
CLASSES=('SUPPORTED_CURRENT_DEFECT','NO_SUPPORTED_DIAGNOSIS','INSUFFICIENT_EVIDENCE','HISTORICAL_DEFECT_NOT_CURRENT','INVALID_OR_CONTRADICTORY_EVIDENCE')
D,H,U,T,X=CLASSES
FAMILIES=('version_selection','authority_precedence','entity_binding','publication_update','operation_idempotence','boundary_comparison')
# Spec IDs/families/variants never cross the renderer boundary.
SPECS=[('d1',0,'defect',D),('d2',1,'defect',D),('d3',2,'defect',D),('d4',3,'defect',D),('d5',4,'defect',D),('d6',5,'defect',D),('h1',0,'healthy',H),('h2',2,'healthy',H),('h3',3,'healthy',H),('h4',5,'healthy',H),('u1',4,'unknown',U),('u2',0,'unknown',U),('u3',3,'unknown',U),('u4',5,'unknown',U),('t1',1,'historical',T),('t2',0,'historical',T),('t3',4,'historical',T),('x1',2,'identity_conflict',X),('x2',0,'deployment_conflict',X),('x3',3,'digest_conflict',X)]
PAIRS=(('d1','h1'),('d2','t1'),('d3','h2'),('d4','h3'),('d5','u1'),('d6','h4'))

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def derive(seed,domain):return sha256((seed+'\0'+domain).encode()).digest()
def number(seed,domain,mod):return int.from_bytes(derive(seed,domain)[:8],'big')%mod

def frame(family,version,bad,n):
 """Known bounded mutation changes operative inputs/configuration, then derives its output."""
 if family==0:
  cause=dict(active_config='@cfg2',used_config='@cfg1' if bad else '@cfg2',config_values={'@cfg1':n,'@cfg2':n+7},request_template='@action0',repeat_count=5)
  effect=dict(returned_value=cause['config_values'][cause['used_config']])
 elif family==1:
  cause=dict(source_primary='@src0',source_secondary='@src1',primary_decision='DENY',secondary_decision='ALLOW',first_consulted='@src1' if bad else '@src0')
  effect=dict(final_decision='ALLOW' if bad else 'DENY')
 elif family==2:
  cause=dict(requested_entity='@entity0',record_owner='@entity1' if bad else '@entity0',selected_source='@src1',primary_source_available=False,source_path='BACKUP',reading=n)
  effect=dict(attributed_entity='@entity0',published_reading=n)
 elif family==3:
  cause=dict(attempt_total_before=n,batch_size=5,publication_fields=[] if bad else ['attempt_total'],remote_delivery='DROPPED_BY_LINK',other_writes_in_interval=0)
  effect=dict(acknowledgment=True,attempt_total_after=n if bad else n+5)
 elif family==4:
  cause=dict(key_column='attempt_token' if bad else 'operation_token',amount=n,entries=[dict(sequence=1,attempt_token='@attempt0',operation_token='@op0'),dict(sequence=2,attempt_token='@attempt1',operation_token='@op0')],listing_complete=True)
  effect=dict(posted_units=n*(2 if bad else 1))
 else:
  cause=dict(sensed_level=n,target_level=n,implemented_comparator='>=' if bad else '>',comparison_result=bad,readings=[n,n,n])
  effect=dict(command_issued=bad)
 return dict(version=version,component_id=('@c1','@c0','@c2','@c1','@c0','@c2')[family],data=cause),dict(version=version,event_id='@event1' if version=='@v1' else '@event2',data=effect)

RULES=(
 'For every response, use the configuration named by active_config for that execution version. Configuration values are complete. Repeated identical requests may return identical values indefinitely.',
 'The primary source has decision priority: if its decision is DENY the final decision must be DENY regardless of the secondary source. If primary is ABSTAIN use secondary. A final ALLOW is permitted only in the latter situation with secondary ALLOW.',
 'A reading attributed to requested_entity must originate from a record with that same record_owner. A BACKUP source is permitted when the primary source is unavailable; source location does not change entity ownership.',
 'At acknowledgment, attempt_total_after equals attempt_total_before plus batch_size, irrespective of remote_delivery. The observation is after acknowledgment. No other writes occur in the stated interval. A remote link may drop every delivery without violating this contract.',
 'posted_units equals amount multiplied by the number of distinct operation_token values in the complete listing. Multiple attempt_token values for the same operation_token contribute only once. No other postings exist in this interval.',
 'Issue a command exactly when sensed_level is strictly greater than target_level. Equality meets the declared objective and requires no command. Repeated equal readings and an unchanged level are permitted.')
DOMAINS=('document formatting service','access decision service','instrument reading catalogue','network attempt accounting','billing accumulator','pressure control comparator')


def make_world(family,variant,seed):
 n=11+number(seed,'quantity/'+str(family),20)
 # Both version snapshots are always supplied. No label states whether either violates its contract.
 old_bad=variant=='historical' or family==1
 current_bad=variant in ('defect','unknown')
 if family==1:old_bad=True;current_bad=False
 old,old_out=frame(family,'@v1',old_bad,n);new,new_out=frame(family,'@v2',current_bad,n)
 if variant=='unknown':
  if family==0:new['data']['active_config']='UNKNOWN'
  if family==3:new['data'].update(batch_size='UNKNOWN',publication_fields='UNKNOWN',other_writes_in_interval='UNKNOWN');new_out['data']['attempt_total_after']=n+5
  if family==4:new['data']['key_column']='UNKNOWN';new['data']['entries'][1]['operation_token']='UNKNOWN'
  if family==5:new['data'].update(sensed_level='UNKNOWN',implemented_comparator='UNKNOWN',comparison_result='UNKNOWN',readings=['UNKNOWN']*3)
 deployment='@v1' if family==1 and variant=='defect' else '@v2'
 # Neutral evidence capture facts are separate from operational contracts.
 capture=dict(deployment_version=deployment,immutable_event_id=new_out['event_id'],captured_event_data=deepcopy(new_out['data']),recorded_digest=digest([7,11,13]),recomputed_digest=digest([7,11,13]))
 if variant=='identity_conflict':capture['captured_event_data']['published_reading']+=1
 if variant=='deployment_conflict':capture['deployment_version']='@v1'
 if variant=='digest_conflict':capture['recorded_digest']=digest([7,11,14])
 records=[dict(id='@r0',kind='contract',data=dict(rule=RULES[family],scope='Each described component rule is complete for the presented inputs. No undocumented exceptions apply. UNKNOWN denotes omitted information, never a default value.')),
 dict(id='@r1',kind='deployment',data=dict(current_version=deployment,as_of=30)),
 dict(id='@r2',kind='execution_input',at=10,**old),dict(id='@r3',kind='execution_output',at=11,**old_out),
 dict(id='@r4',kind='execution_input',at=20,**new),dict(id='@r5',kind='execution_output',at=21,**new_out),
 dict(id='@r6',kind='capture',data=capture),
 dict(id='@r7',kind='capture_contract',data=dict(rule='The capture and deployment records describe the same as_of snapshot. An immutable event ID has one payload. recorded_digest and recomputed_digest refer to identical captured bytes and must agree. Operational input/configuration records are observations of implementation behavior, not assurances of compliance with the contract. Version ordinals are release order, not proof of deployment.'))]
 return dict(domain=DOMAINS[family],system_id='@sys',components=[dict(id='@c0',role='decision worker'),dict(id='@c1',role='publication worker'),dict(id='@c2',role='input/output worker')],versions=[dict(id='@v1',release_ordinal=1),dict(id='@v2',release_ordinal=2)],records=records)


def operational_violation(family,cause,effect):
 """Independent contract oracle over supplied facts, not the injection mode."""
 if family==0:
  if cause['active_config']=='UNKNOWN':return None
  return cause['used_config']!=cause['active_config'] or effect['returned_value']!=cause['config_values'][cause['active_config']]
 if family==1:
  expected=cause['primary_decision'] if cause['primary_decision']!='ABSTAIN' else cause['secondary_decision']
  return effect['final_decision']!=expected
 if family==2:return cause['requested_entity']!=cause['record_owner'] or effect['attributed_entity']!=cause['requested_entity'] or effect['published_reading']!=cause['reading']
 if family==3:
  if cause['batch_size']=='UNKNOWN' or cause['other_writes_in_interval']=='UNKNOWN':return None
  return effect['attempt_total_after']!=cause['attempt_total_before']+cause['batch_size']
 if family==4:
  tokens=[x['operation_token'] for x in cause['entries']]
  if 'UNKNOWN' in tokens or not cause['listing_complete']:return None
  return effect['posted_units']!=len(set(tokens))*cause['amount']
 if cause['sensed_level']=='UNKNOWN':return None
 return effect['command_issued']!=(cause['sensed_level']>cause['target_level'])


def oracle(family,world):
 r={x['id']:x for x in world['records']};capture=r['@r6']['data'];deployment=r['@r1']['data']['current_version']
 if capture['deployment_version']!=deployment or capture['captured_event_data']!=r['@r5']['data'] or capture['immutable_event_id']!=r['@r5']['event_id'] or capture['recorded_digest']!=capture['recomputed_digest']:return X
 current=('@r2','@r3') if deployment=='@v1' else ('@r4','@r5')
 violation=operational_violation(family,r[current[0]]['data'],r[current[1]]['data'])
 if violation is None:return U
 if violation:return D
 if deployment=='@v2' and operational_violation(family,r['@r2']['data'],r['@r3']['data']):return T
 return H


def differences(a,b,path=''):
 if type(a)!=type(b):return [path]
 if isinstance(a,dict):
  return [p for k in sorted(set(a)|set(b)) for p in (differences(a[k],b[k],path+'/'+k) if k in a and k in b else [path+'/'+k])]
 if isinstance(a,list):
  if len(a)!=len(b):return [path]
  return [p for i,(x,y) in enumerate(zip(a,b)) for p in differences(x,y,path+'/'+str(i))]
 return [] if a==b else [path]


def generate(seed):
 cases=[]
 for spec,family,variant,expected in SPECS:
  world=make_world(family,variant,seed);classification=oracle(family,world)
  assert classification==expected,(spec,classification,expected)
  current=('@r2','@r3') if world['records'][1]['data']['current_version']=='@v1' else ('@r4','@r5')
  evidence=['@r0','@r1',*current]
  if classification==T:evidence=['@r0','@r1','@r2','@r3','@r4','@r5']
  if classification==X:evidence=['@r6','@r7',{'identity_conflict':'@r5','deployment_conflict':'@r1','digest_conflict':'@r6'}[variant]];evidence=sorted(set(evidence))
  gold=dict(classification=classification,affected_components=[('@c1','@c0','@c2','@c1','@c0','@c2')[family]] if classification==D else [],mechanism_family=FAMILIES[family] if classification==D else None,mechanism_witness=dict(contract_evidence_id='@r0',cause_evidence_id=current[0],effect_evidence_id=current[1]) if classification==D else None,required_evidence=evidence)
  if classification==D:
   cause=world['records'][2 if current[0]=='@r2' else 4]['data'];effect=world['records'][3 if current[1]=='@r3' else 5]['data']
   decisive=[(current[0],'/used_config',cause.get('used_config'),cause.get('active_config')),
             (current[1],'/final_decision',effect.get('final_decision'),'DENY'),
             (current[0],'/record_owner',cause.get('record_owner'),cause.get('requested_entity')),
             (current[1],'/attempt_total_after',effect.get('attempt_total_after'),cause.get('attempt_total_before',0)+cause.get('batch_size',0)),
             (current[1],'/posted_units',effect.get('posted_units'),cause.get('amount')),
             (current[1],'/command_issued',effect.get('command_issued'),False)][family]
   gold['mechanism_witness'].update(zip(('decisive_evidence_id','decisive_field','observed_value','required_value'),decisive))
   gold['mechanism_alternatives']=[]
   if family==0:
    alternate=deepcopy(gold['mechanism_witness']);alternate.update(decisive_evidence_id=current[1],decisive_field='/returned_value',observed_value=effect['returned_value'],required_value=cause['config_values'][cause['active_config']]);gold['mechanism_alternatives'].append(alternate)
  cases.append(dict(case_id=derive(seed,'semantic/'+spec).hex()[:16],spec_id=spec,family=FAMILIES[family],variant=variant,world=world,gold=gold))
 by={c['spec_id']:c for c in cases};pairs=[]
 for i,(a,b) in enumerate(PAIRS):
  pairs.append(dict(pair_id='P'+str(i+1),left=by[a]['case_id'],right=by[b]['case_id'],left_spec=a,right_spec=b,classes=[by[a]['gold']['classification'],by[b]['gold']['classification']],changed_paths=differences(by[a]['world'],by[b]['world'])))
 return cases,pairs
