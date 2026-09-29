"""Engineering harness support; raw evidence and generic contract only."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

P=Path(__file__).resolve().parent
ID=re.compile(r'z[0-9a-f]{16}')
ID_WORD=re.compile(r'\bz[0-9a-f]{16}\b')

def pack(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)
def read(p):return json.loads(p.read_bytes())
def run(case,worker=None):
    request={'case':case,'contract':read(P/'mechanical-contract.json')}
    proc=subprocess.run([sys.executable,'-I','-S',str(worker or P/'worker.py')],input=pack(request).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
    if proc.returncode:raise RuntimeError(proc.stderr.decode())
    return json.loads(proc.stdout),proc.stdout

def walk(v,path=''):
    yield path,v
    if isinstance(v,dict):
        for k,x in v.items():yield from walk(x,path+'/'+k.replace('~','~0').replace('/','~1'))
    elif isinstance(v,list):
        for i,x in enumerate(v):yield from walk(x,path+'/'+str(i))

def strings(v):
    if isinstance(v,str):yield v
    elif isinstance(v,list):
        for x in v:yield from strings(x)
    elif isinstance(v,dict):
        for k,x in v.items():yield k;yield from strings(x)

def ids(v):return {m.group() for text in strings(v) for m in ID_WORD.finditer(text)}
def replace(v,mapping):
    if isinstance(v,str):return ID_WORD.sub(lambda m:mapping.get(m.group(),m.group()),v)
    if isinstance(v,list):return [replace(x,mapping) for x in v]
    if isinstance(v,dict):return {replace(k,mapping):replace(x,mapping) for k,x in v.items()}
    return v

def mask(v):
    if isinstance(v,str):return ID_WORD.sub('@ID',v)
    if isinstance(v,list):return [mask(x) for x in v]
    if isinstance(v,dict):return ['OBJECT',*sorted([[mask(k),mask(x)] for k,x in v.items()],key=pack)]
    return v

def canonical_map(case):
    prepared=copy.deepcopy(case)
    for name in ('records','components','versions'):
        keys=[pack(mask(v)) for v in prepared[name]]
        if len(keys)!=len(set(keys)):raise ValueError('Ambiguous ID-masked entity alignment')
        prepared[name]=[v for _,v in sorted(zip(keys,prepared[name]),key=lambda pair:pair[0])]
    mapping={}
    def visit(v):
        if isinstance(v,str):
            for m in ID_WORD.finditer(v):
                if m.group() not in mapping:mapping[m.group()]='@label'+str(len(mapping)+1)
        elif isinstance(v,list):
            for x in v:visit(x)
        elif isinstance(v,dict):
            entries=sorted(v.items(),key=lambda pair:pack([mask(pair[0]),mask(pair[1])]))
            keys=[pack([mask(k),mask(x)]) for k,x in entries]
            if len(keys)!=len(set(keys)):raise ValueError('Ambiguous ID-masked field alignment')
            for k,x in entries:visit(k);visit(x)
    visit(prepared);return mapping

POINTER_KEYS={'source_path','full_json_pointer','source_paths','binding_paths','path'}
SET_LISTS={'record_index','component_index','version_index','current_record_ids','historical_record_ids','unversioned_record_ids','unresolved_record_ids','unknown_locations','event_links','capture_links','integrity_findings','input_output_candidates','field_inventory','ambiguities','candidate_witness_material','nodes','edges','source_paths','binding_paths','record_ids','differences','values','candidates','linked_record_ids','contract_record_ids','capture_contract_record_ids'}
def normalize(output,case,mapping=None):
    mapping=mapping or {}
    def visit(v,key='',inside_value=False):
        if isinstance(v,str):
            if key in POINTER_KEYS and not inside_value:
                match=re.match(r'^/(records|components|versions)/(\d+)(/.*)?$',v)
                if match:v='/'+match[1]+'_by_id/'+case[match[1]][int(match[2])]['id']+(match[3] or '')
            return replace(v,mapping)
        if isinstance(v,dict):return {replace(k,mapping):visit(x,k,inside_value or k in ('value','component','version')) for k,x in v.items()}
        if isinstance(v,list):
            result=[visit(x,key,inside_value) for x in v]
            return sorted(result,key=pack) if key in SET_LISTS and not inside_value else result
        return v
    return pack(visit(output))

def synthetic():
    z=lambda n:'z'+format(n,'016x')
    return dict(system_id=z(1),domain='synthetic mechanics',components=[dict(id=z(2),role='worker'),dict(id=z(3),role='other')],versions=[dict(id=z(4),release_ordinal=1),dict(id=z(5),release_ordinal=2)],records=[
      dict(id=z(6),kind='deployment',data=dict(current_version=z(5),as_of=30)),
      dict(id=z(7),kind='execution_input',version=z(5),at=20,component_id=z(2),data={'measurement':1,'a/b~c':[True,2.0]}),
      dict(id=z(8),kind='execution_output',version=z(5),at=21,event_id=z(9),data={'measurement':1}),
      dict(id=z(10),kind='capture',data=dict(deployment_version=z(5),immutable_event_id=z(9),captured_event_data={'measurement':1},recorded_digest='digest-a',recomputed_digest='digest-a')),
      dict(id=z(11),kind='execution_input',version=z(4),at=10,component_id=z(2),data={'measurement':0}),
      dict(id=z(12),kind='execution_output',version=z(4),at=11,event_id=z(13),data={'measurement':0}),
      dict(id=z(14),kind='contract',data={'rule':'Uninterpreted operational text'}),
      dict(id=z(15),kind='capture_contract',data={'rule':read(P/'mechanical-contract.json')['source']['common_format_statement']})])

def independent_checks(case,out):
    assert sorted(r['record_id'] for r in out['record_index'])==sorted(r['id'] for r in case['records'])
    assert ids(out)<=ids(case)
    expected=[]
    for i,r in enumerate(case['records']):
        if isinstance(r.get('data'),dict):
            for path,value in walk(r['data']):expected.append((r['id'],path,'/records/'+str(i)+'/data'+path,pack(value),type(value).__name__))
    types={'NoneType':'null','bool':'boolean','int':'integer','float':'number','str':'string','list':'array','dict':'object'}
    got={(e['record_id'],e['json_pointer_relative_to_data'],e['full_json_pointer'],pack(e['value']),e['exact_type']) for e in out['field_inventory']}
    assert got=={(rid,rel,full,value,types[typ]) for rid,rel,full,value,typ in expected}
    want_unknown={(r['id'],'/records/'+str(i)+path) for i,r in enumerate(case['records']) for path,value in walk(r) if type(value) is str and value=='UNKNOWN'}
    assert {(x['record_id'],x['full_json_pointer']) for x in out['unknown_locations']}==want_unknown
    expected_links={(o['id'],c['id'],o['event_id']) for o in case['records'] if o['kind']=='execution_output' and isinstance(o.get('event_id'),str) and o['event_id']!='UNKNOWN' for c in case['records'] if c['kind']=='capture' and c.get('data',{}).get('immutable_event_id')==o['event_id']}
    assert {(x['output_record_id'],x['capture_record_id'],x['event_id']) for x in out['capture_links']}==expected_links
    def resolve(pointer):
        cur=case
        for part in pointer.split('/')[1:]:
            part=part.replace('~1','/').replace('~0','~');cur=cur[int(part)] if isinstance(cur,list) else cur[part]
        return cur
    for edge in out['evidence_graph']['edges']:
        assert edge['source_paths'] and edge['reason']!='causes'
        for pointer in edge['source_paths']:resolve(pointer)
    declared=[r['data']['current_version'] for r in case['records'] if r['kind']=='deployment']
    if declared and len(set(declared))==1:assert out['current_version']==declared[0]
    known={v['id'] for v in case['versions']}
    expected_partition={k:[] for k in ('current','historical','unversioned','unresolved')}
    for record in case['records']:
        bindings=[]
        if 'version' in record:bindings.append(record['version'])
        if record['kind']=='capture' and 'deployment_version' in record.get('data',{}):bindings.append(record['data']['deployment_version'])
        if not bindings:status='unversioned'
        elif out['current_version'] is None or len(set(bindings))!=1 or bindings[0] not in known:status='unresolved'
        else:status='current' if bindings[0]==out['current_version'] else 'historical'
        expected_partition[status].append(record['id'])
    for status,want in expected_partition.items():assert out[status+'_record_ids']==sorted(want)
    for unknown in out['unknown_locations']:
        assert unknown['record_id'] in expected_partition[unknown['status']]
    for finding in out['integrity_findings']:
        if finding['check'] in ('digest_equality','capture_snapshot_binding','linked_version') and len(finding['source_paths'])==2:
            values=[resolve(pointer) for pointer in finding['source_paths']]
            if all(type(v) is str and v not in ('','UNKNOWN') for v in values):assert finding['consistent']==(values[0]==values[1])
    contract=read(P/'mechanical-contract.json')
    assert set(out)==set(contract['output']['required'])
    return dict(record_ids=True,opaque_ids=True,field_inventory=True,unknown_inventory=True,event_links=True,graph_provenance=True,deployment_binding=True,output_shape=True)
