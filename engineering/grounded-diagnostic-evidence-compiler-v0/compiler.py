"""Pure extraction under a supplied generic evidence-format contract. No file access."""
import json


def pack(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)


def ordered(values):
    return sorted(values, key=pack)


def token(value):
    return str(value).replace('~', '~0').replace('/', '~1')


def exact_type(value):
    if value is None: return 'null'
    if type(value) is bool: return 'boolean'
    if type(value) is int: return 'integer'
    if type(value) is float: return 'number'
    if type(value) is str: return 'string'
    if type(value) is list: return 'array'
    if type(value) is dict: return 'object'
    raise ValueError('Non-JSON value')


def walk(value, path=''):
    yield path, value
    if type(value) is dict:
        for key in sorted(value):
            yield from walk(value[key], path + '/' + token(key))
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from walk(child, path + '/' + str(index))


def concrete(value):
    return type(value) is str and value not in ('', 'UNKNOWN')


def numeric(value):
    return type(value) in (int, float) and value == value and value not in (float('inf'), float('-inf'))


def compare(left, right, left_path, right_path):
    """Typed tri-state equality with exact conflicting or unresolved source facts."""
    facts = []
    def item(path, value, present=True):
        return dict(path=path, present=present, exact_type=exact_type(value) if present else 'absent', value=value if present else None)
    def visit(a, b, pa, pb):
        if a == 'UNKNOWN' or b == 'UNKNOWN':
            facts.append(dict(consistent='unknown', values=ordered([item(pa,a),item(pb,b)])));return
        if type(a) is not type(b):
            facts.append(dict(consistent=False, values=ordered([item(pa,a),item(pb,b)])));return
        if type(a) is dict:
            for key in sorted(set(a) | set(b)):
                p=pa+'/'+token(key);q=pb+'/'+token(key)
                if key not in a or key not in b:
                    facts.append(dict(consistent=False,values=ordered([item(p,a.get(key),key in a),item(q,b.get(key),key in b)])))
                else:visit(a[key],b[key],p,q)
        elif type(a) is list:
            if len(a)!=len(b):facts.append(dict(consistent=False,values=ordered([item(pa,a),item(pb,b)])))
            else:
                for index in range(len(a)):visit(a[index],b[index],pa+'/'+str(index),pb+'/'+str(index))
        elif a!=b:facts.append(dict(consistent=False,values=ordered([item(pa,a),item(pb,b)])))
    visit(left,right,left_path,right_path)
    state=False if any(f['consistent'] is False for f in facts) else 'unknown' if facts else True
    return state, ordered(facts)


def compile_evidence(case, contract):
    if contract.get('version')!='grounded-evidence-format-v0':raise ValueError('Unsupported format contract')
    if type(case) is not dict:raise ValueError('Evidence must be an object')
    for key in ('records','components','versions'):
        if type(case.get(key)) is not list:raise ValueError('Missing declared collection')
        for item in case[key]:
            if type(item) is not dict or not concrete(item.get('id')):raise ValueError('Invalid declared identity')
    ambiguity=[];nodes={};edges=[]
    def node(kind, ident, path, declared=True):
        key=(kind,ident)
        if key not in nodes:nodes[key]=dict(kind=kind,id=ident,declared=declared,source_paths=[])
        nodes[key]['declared']=nodes[key]['declared'] or declared
        if path not in nodes[key]['source_paths']:nodes[key]['source_paths'].append(path)
        return dict(kind=kind,id=ident)
    def edge(source,target,reason,paths):
        edges.append(dict(source=source,target=target,reason=reason,source_paths=sorted(set(paths))))
    def issue(code,record_ids,paths):
        ambiguity.append(dict(code=code,record_ids=sorted(record_ids),source_paths=sorted(paths)))
    versions={};components={}
    for collection,lookup,kind in [('versions',versions,'version'),('components',components,'component')]:
        for index,item in enumerate(case[collection]):
            path='/'+collection+'/'+str(index);lookup.setdefault(item['id'],[]).append(path)
            node(kind,item['id'],path+'/id')
        for ident,paths in lookup.items():
            if len(paths)>1:issue('duplicate_'+kind+'_id',[ident],paths)
    records=[]
    for index,record in enumerate(case['records']):
        if type(record.get('kind')) is not str:raise ValueError('Missing record kind')
        path='/records/'+str(index);data=record.get('data');data=data if type(data) is dict else {}
        records.append(dict(raw=record,path=path,data=data,id=record['id'],kind=record['kind']))
        node(record['kind'],record['id'],path+'/id')
    record_groups={}
    for r in records:record_groups.setdefault(r['id'],[]).append(r['path'])
    for ident,paths in record_groups.items():
        if len(paths)>1:issue('duplicate_record_id',[ident],paths)
    declarations=[r for r in records if r['kind']=='deployment']
    values=[r['data'].get('current_version') for r in declarations]
    current=values[0] if values and all(concrete(v) and v==values[0] for v in values) and len(versions.get(values[0],[]))==1 else None
    if current is None:issue('unresolved_current_deployment',[r['id'] for r in declarations],[r['path']+'/data/current_version' for r in declarations])
    for r in declarations:
        value=r['data'].get('current_version')
        if concrete(value):
            target=node('version',value,r['path']+'/data/current_version',value in versions)
            edge(dict(kind=r['kind'],id=r['id']),target,'declares_current_version',[r['path']+'/data/current_version'])
    partitions={k:[] for k in ('current','historical','unversioned','unresolved')}
    index=[];unknown=[];inventory=[];events={};event_links=[];capture_links=[];findings=[];candidates=[]
    for r in records:
        raw=r['raw'];path=r['path'];bindings=[]
        if 'version' in raw:bindings.append((raw['version'],path+'/version'))
        if r['kind']=='capture' and 'deployment_version' in r['data']:bindings.append((r['data']['deployment_version'],path+'/data/deployment_version'))
        bound=bindings[0][0] if bindings and all(concrete(v) and v==bindings[0][0] for v,p in bindings) else None
        status='unversioned' if not bindings else 'unresolved' if bound is None or current is None or len(versions.get(bound,[]))!=1 else 'current' if bound==current else 'historical'
        if status=='unresolved':issue('unresolved_record_version',[r['id']],[p for v,p in bindings])
        r['status']=status;r['bound']=bound;partitions[status].append(r['id'])
        index.append(dict(record_id=r['id'],kind=r['kind'],source_path=path,timestamp=raw.get('at'),timestamp_present='at' in raw,version=raw.get('version'),version_present='version' in raw,component_id=raw.get('component_id'),bound_version=bound,binding_paths=[p for v,p in bindings],status=status))
        for value,pointer in bindings:
            if concrete(value):
                target=node('version',value,pointer,value in versions)
                edge(dict(kind=r['kind'],id=r['id']),target,'capture_version' if pointer.endswith('/data/deployment_version') else 'record_version',[pointer])
        if r['kind']=='execution_input' and concrete(raw.get('component_id')):
            pointer=path+'/component_id';target=node('component',raw['component_id'],pointer,raw['component_id'] in components)
            edge(dict(kind=r['kind'],id=r['id']),target,'input_component',[pointer])
        for pointer,value in walk(raw,path):
            if type(value) is str and value=='UNKNOWN':unknown.append(dict(record_id=r['id'],full_json_pointer=pointer,value=value,exact_type='string',status=status))
        if type(raw.get('data')) is dict:
            for relative,value in walk(raw['data']):
                inventory.append(dict(record_id=r['id'],json_pointer_relative_to_data=relative,full_json_pointer=path+'/data'+relative,value=value,exact_type=exact_type(value),is_container=type(value) in (dict,list)))
        if r['kind']=='execution_output':event=raw.get('event_id');event_path=path+'/event_id';payload=raw.get('data');payload_path=path+'/data'
        elif r['kind']=='capture':event=r['data'].get('immutable_event_id');event_path=path+'/data/immutable_event_id';payload=r['data'].get('captured_event_data');payload_path=path+'/data/captured_event_data'
        else:continue
        if concrete(event):
            r['event']=event;r['event_path']=event_path;r['payload']=payload;r['payload_path']=payload_path
            events.setdefault(event,[]).append(r)
            event_links.append(dict(record_id=r['id'],record_kind=r['kind'],event_id=event,source_path=event_path))
            edge(dict(kind=r['kind'],id=r['id']),node('event',event,event_path),'output_event' if r['kind']=='execution_output' else 'capture_event',[event_path])
        else:
            issue('missing_event_link',[r['id']],[event_path])
            findings.append(dict(check='event_payload_linkage',consistent='unknown',record_ids=[r['id']],source_paths=[event_path],differences=[]))
    def finding(check,rs,paths,left=None,right=None,available=True):
        state,diffs=compare(left,right,paths[0],paths[1]) if available else ('unknown',[])
        findings.append(dict(check=check,consistent=state,record_ids=sorted(r['id'] for r in rs),source_paths=sorted(paths),differences=diffs))
    for event,claimants in events.items():
        claimants=sorted(claimants,key=lambda r:(r['id'],r['path']))
        for i,left in enumerate(claimants):
            for right in claimants[i+1:]:
                finding('immutable_event_payload',[left,right],[left['payload_path'],right['payload_path']],left['payload'],right['payload'],type(left['payload']) is dict and type(right['payload']) is dict)
        outputs=[r for r in claimants if r['kind']=='execution_output']
        captures=[r for r in claimants if r['kind']=='capture']
        for capture in captures:
            if len(outputs)!=1:issue('missing_capture_output' if not outputs else 'multiple_capture_outputs',[capture['id'],*[r['id'] for r in outputs]],[capture['event_path'],*[r['event_path'] for r in outputs]])
            if not outputs:findings.append(dict(check='event_payload_linkage',consistent='unknown',record_ids=[capture['id']],source_paths=[capture['event_path']],differences=[]))
            for output in outputs:
                paths=[output['event_path'],capture['event_path']]
                capture_links.append(dict(output_record_id=output['id'],capture_record_id=capture['id'],event_id=event,source_paths=sorted(paths)))
                edge(dict(kind=output['kind'],id=output['id']),dict(kind=capture['kind'],id=capture['id']),'output_capture_same_event',paths)
                paths=[output['path']+'/version',capture['path']+'/data/deployment_version']
                finding('linked_version',[output,capture],paths,output['raw'].get('version'),capture['data'].get('deployment_version'),concrete(output['raw'].get('version')) and concrete(capture['data'].get('deployment_version')))
    for r in records:
        if r['kind']=='capture':
            data=r['data'];paths=[r['path']+'/data/recorded_digest',r['path']+'/data/recomputed_digest']
            finding('digest_equality',[r],paths,data.get('recorded_digest'),data.get('recomputed_digest'),concrete(data.get('recorded_digest')) and concrete(data.get('recomputed_digest')))
            if current is None:
                findings.append(dict(check='capture_snapshot_binding',consistent='unknown',record_ids=[r['id']],source_paths=[r['path']+'/data/deployment_version'],differences=[]))
            else:
                for deployment in declarations:
                    paths=[r['path']+'/data/deployment_version',deployment['path']+'/data/current_version']
                    finding('capture_snapshot_binding',[r,deployment],paths,data.get('deployment_version'),current,concrete(data.get('deployment_version')))
    inputs=[r for r in records if r['kind']=='execution_input']
    for output in records:
        if output['kind']!='execution_output':continue
        matches=[];out=output['raw']
        for inp in inputs:
            raw=inp['raw']
            if not(concrete(raw.get('version')) and raw.get('version')==out.get('version') and numeric(raw.get('at')) and numeric(out.get('at')) and raw['at']<out['at']):continue
            if 'component_id' in raw and 'component_id' in out and raw['component_id']!=out['component_id']:continue
            if 'event_id' in raw and 'event_id' in out and (not concrete(raw['event_id']) or raw['event_id']!=out['event_id']):continue
            paths=[inp['path']+'/version',output['path']+'/version',inp['path']+'/at',output['path']+'/at']
            for field in ('component_id','event_id'):
                if field in raw and field in out:paths.extend([inp['path']+'/'+field,output['path']+'/'+field])
            matches.append(dict(input_record_id=inp['id'],component_id=raw.get('component_id'),source_paths=sorted(paths)))
            edge(dict(kind=inp['kind'],id=inp['id']),dict(kind=output['kind'],id=output['id']),'candidate_input_output',paths)
        if len(matches)!=1:issue('missing_input_candidate' if not matches else 'multiple_input_candidates',[output['id'],*[m['input_record_id'] for m in matches]],[output['path']])
        candidates.append(dict(output_record_id=output['id'],candidates=ordered(matches),ambiguous=len(matches)!=1,causality_asserted=False))
    state=False if any(f['consistent'] is False for f in findings) else 'unknown' if not findings or any(f['consistent']=='unknown' for f in findings) else True
    for n in nodes.values():n['source_paths']=sorted(n['source_paths'])
    contracts=sorted(r['id'] for r in records if r['kind']=='contract');capture_contracts=sorted(r['id'] for r in records if r['kind']=='capture_contract')
    material=[]
    for entry in inventory:
        linked=sorted({link['output_record_id'] if link['capture_record_id']==entry['record_id'] else link['capture_record_id'] for link in capture_links if entry['record_id'] in (link['output_record_id'],link['capture_record_id'])})
        material.append(dict(record_id=entry['record_id'],json_pointer_relative_to_data=entry['json_pointer_relative_to_data'],full_json_pointer=entry['full_json_pointer'],exact_type=entry['exact_type'],value=entry['value'],is_container=entry['is_container'],linked_record_ids=linked,contract_record_ids=contracts,capture_contract_record_ids=capture_contracts))
    return dict(format_version=contract['version'],case_identity=case.get('system_id'),record_index=ordered(index),
        component_index=ordered([dict(component=item,source_path='/components/'+str(i)) for i,item in enumerate(case['components'])]),
        version_index=ordered([dict(version=item,source_path='/versions/'+str(i)) for i,item in enumerate(case['versions'])]),
        current_version=current,current_record_ids=sorted(partitions['current']),historical_record_ids=sorted(partitions['historical']),unversioned_record_ids=sorted(partitions['unversioned']),unresolved_record_ids=sorted(partitions['unresolved']),
        unknown_locations=ordered(unknown),event_links=ordered(event_links),capture_links=ordered(capture_links),integrity_consistent=state,integrity_findings=ordered(findings),input_output_candidates=ordered(candidates),
        field_inventory=ordered(inventory),evidence_graph=dict(nodes=ordered(list(nodes.values())),edges=ordered(edges)),ambiguities=ordered(ambiguity),candidate_witness_material=ordered(material))
