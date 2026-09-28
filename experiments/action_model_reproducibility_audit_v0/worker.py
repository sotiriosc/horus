"""Replay archived HTTP request bytes without world execution or Memory writes."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json,os,subprocess,threading,time,urllib.request,urllib.error
from horus.live import SessionStore
from horus.core import digest
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action

MODEL='dolphin-mixtral:latest'
DIGEST='4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a'
FIXTURES={
 'C5_IDENTICAL_REQUEST':dict(case='C5',call_id='C:2:ACTION:1',canonical='0e5f079446e11a16bf6ec025101ac3131253552ca7cf791b3e0164e627fc3112',wire='63931708f48b23ca51682acbee95a6099230d215861b5450918c566fdbe4d133',bytes=2022),
 'G_STABLE_REQUEST':dict(case='G',call_id='C:1:ACTION:1',canonical='c03268648a2f639c1db95a3f998012429fc651e4133c1514dce3317a168ffd35',wire='3114960d6e873ec5a8dd195d057bd386cb80d6d79e9c8f90270a57df770414b3',bytes=2120),
}
WARM_COUNT=20
FRESH_COUNT=10
SERVER_COUNT=3

def sha(data):return sha256(data).hexdigest()
def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    tmp.replace(path)

def tagged_model(endpoint):
    with urllib.request.urlopen(endpoint+'/api/tags',timeout=15) as r: value=json.load(r)
    model=next((m for m in value['models'] if m.get('name')==MODEL),None)
    if model is None or model.get('digest')!=DIGEST:raise RuntimeError('model digest mismatch')
    return model

def archive_body(root,case,call_id):
    out=[]
    for arm in ('I','S'):
        with SessionStore(root/'cases'/case/arm/'session',True) as store:
            intents=[e['record'] for e in store.records['calls'] if e['kind']=='REQUEST_INTENT' and e['record'].get('call_id')==call_id]
            attempts=[e['record'] for e in store.records['calls'] if e['kind']=='TRANSPORT_ATTEMPT_INTENT' and e['record'].get('call_id')==call_id]
            if len(intents)!=1 or len(attempts)!=1:raise RuntimeError('archival call multiplicity mismatch')
            out.append((intents[0],attempts[0]))
    if out[0][0]['request_sha256']!=out[1][0]['request_sha256'] or out[0][1]['request_bytes_utf8']!=out[1][1]['request_bytes_utf8']:
        raise RuntimeError('archival I/S requests differ')
    return out[0]

def extract(root,replication_archive,phase4_archive):
    root.mkdir(parents=True,exist_ok=False)
    tagged_model('http://127.0.0.1:11434')
    summaries={}
    for name,spec in FIXTURES.items():
        source=replication_archive if name.startswith('C5') else phase4_archive
        intent,attempt=archive_body(source,spec['case'],spec['call_id'])
        body=attempt['request_bytes_utf8'].encode('utf-8')
        if (intent['request_sha256']!=spec['canonical'] or sha(body)!=spec['wire'] or
            attempt['request_bytes_sha256']!=spec['wire'] or len(body)!=spec['bytes']):
            raise RuntimeError('archival request hash mismatch')
        obj=json.loads(body);prompt=json.loads(obj['prompt'])
        if obj['model']!=MODEL or obj['options']['temperature']!=0.2 or obj['format']!='json':
            raise RuntimeError('frozen request contents changed')
        (root/'fixtures').mkdir(exist_ok=True)
        (root/'fixtures'/(name+'.request.private.json')).write_bytes(body)
        summaries[name]=dict(canonical_request_sha256=spec['canonical'],wire_request_sha256=spec['wire'],
            byte_length=len(body),model=obj['model'],system_sha256=sha(obj['system'].encode()),
            prompt_sha256=sha(obj['prompt'].encode()),allowed_actions=prompt['available_actions'],
            state=prompt['current_state'],assessment_kinds={a:x['kind'] for a,x in prompt['grounded_assessments'].items()},
            history_length=len(prompt['recent_agent_working_context']),options=obj['options'],
            format=obj['format'],stream=obj['stream'],stop_in_request=obj.get('stop'),
            template_parameters_scope='model-level; recorded separately')
    write_json(root/'fixtures.private.json',summaries)
    print(json.dumps({k:dict(canonical_sha=v['canonical_request_sha256'],wire_sha=v['wire_request_sha256']) for k,v in summaries.items()}),flush=True)

def model_processes():
    found={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit() or int(p.name)==os.getpid():continue
        try:
            parts=(p/'cmdline').read_bytes().split(b'\0')
            exe=Path(parts[0].decode('utf-8','replace')).name if parts and parts[0] else ''
            if 'ollama' in exe.lower() or 'llama' in exe.lower():
                found[int(p.name)]=exe
        except (OSError,PermissionError,ProcessLookupError):pass
    return found

def post_bytes(endpoint,body):
    request=urllib.request.Request(endpoint+'/api/generate',data=body,
        headers={'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(request,timeout=600) as response:
        return response.read()

def one(root,fixture,condition,index,endpoint,server_pid=None):
    spec=FIXTURES[fixture];body=(root/'fixtures'/(fixture+'.request.private.json')).read_bytes()
    if sha(body)!=spec['wire'] or len(body)!=spec['bytes']:raise RuntimeError('fixture bytes changed')
    tagged_model(endpoint)
    path=root/'calls'/condition/fixture/f'{index:03d}'
    if path.exists():raise RuntimeError('call slot already used')
    path.mkdir(parents=True)
    before=model_processes();sampled=dict(before);stop=threading.Event()
    def observe():
        while not stop.wait(.5):sampled.update(model_processes())
    thread=threading.Thread(target=observe,daemon=True);thread.start()
    write_json(path/'intent.private.json',dict(fixture=fixture,condition=condition,index=index,
        canonical_request_sha256=spec['canonical'],wire_request_sha256=spec['wire'],
        endpoint=endpoint,started_unix_ns=time.time_ns(),server_pid=server_pid,
        processes_before=before))
    started=time.perf_counter();response=None;error=None
    try:response=post_bytes(endpoint,body)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    elapsed=time.perf_counter()-started;stop.set();thread.join(timeout=2)
    after=model_processes();sampled.update(after)
    value=None;raw=None;selected='INVALID';parse_error=None
    if response is not None:
        (path/'response.private.json').write_bytes(response)
        try:
            value=json.loads(response)
            raw=value.get('response')
            if value.get('done') is not True or not isinstance(raw,str):raise ValueError('incomplete response')
            selected=parse_action(raw)['selected_action']
        except Exception as exc:parse_error=type(exc).__name__+': '+str(exc)
    metadata={key:value.get(key) for key in ('model','created_at','total_duration','load_duration',
        'prompt_eval_count','prompt_eval_duration','eval_count','eval_duration') if value is not None}
    record=dict(fixture=fixture,condition=condition,index=index,
        canonical_request_sha256=spec['canonical'],wire_request_sha256=sha(body),
        response_sha256=sha(response) if response is not None else None,
        raw_output_sha256=sha(raw.encode()) if isinstance(raw,str) else None,
        raw_output_canonical_sha256=digest(raw) if isinstance(raw,str) else None,
        selected_action=selected,transport_error=error,parse_error=parse_error,
        elapsed_seconds=round(elapsed,6),response_metadata=metadata,
        model_digest=DIGEST,server_pid=server_pid,
        processes_before=before,processes_sampled=sampled,processes_after=after)
    write_json(path/'result.private.json',record)
    print(json.dumps({k:record[k] for k in ('fixture','condition','index','selected_action','raw_output_sha256','elapsed_seconds','transport_error')},sort_keys=True),flush=True)
    return record

def warm(root,endpoint):
    for fixture in FIXTURES:
        for index in range(1,WARM_COUNT+1):one(root,fixture,'warm',index,endpoint)

def unload(endpoint,root,index):
    body=json.dumps(dict(model=MODEL,keep_alive=0)).encode()
    path=root/'controls'/'unload'/f'{index:03d}'
    path.mkdir(parents=True,exist_ok=False)
    started=time.perf_counter();response=None;error=None
    try:response=post_bytes(endpoint,body)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    if response is not None:(path/'response.private.json').write_bytes(response)
    write_json(path/'result.private.json',dict(request_sha256=sha(body),response_sha256=sha(response) if response else None,
        error=error,elapsed_seconds=round(time.perf_counter()-started,6)))
    return error

def fresh_runner(root,endpoint):
    status={'status':'RUNNING','completed':0,'reason':None}
    write_json(root/'fresh-runner-status.private.json',status)
    n=0
    for fixture in FIXTURES:
        for index in range(1,FRESH_COUNT+1):
            n+=1
            if unload(endpoint,root,n):
                status.update(status='NOT_RUN' if n==1 else 'PARTIAL',reason='unload control rejected')
                write_json(root/'fresh-runner-status.private.json',status);return
            # Old Ollama versions may not expose runner state. A nonzero load_duration
            # is required post hoc when PID observation is unavailable.
            for _ in range(20):
                processes=model_processes()
                if not any(name!='ollama' for name in processes.values()):break
                time.sleep(1)
            row=one(root,fixture,'fresh_runner',index,endpoint)
            load=row['response_metadata'].get('load_duration')
            old=set(row['processes_before'])
            new=set(row['processes_sampled'])-old
            row['fresh_load_verified']=bool((isinstance(load,(int,float)) and load>0) or new)
            write_json(root/'calls'/'fresh_runner'/fixture/f'{index:03d}'/'result.private.json',row)
            status['completed']+=1
            if not row['fresh_load_verified']:
                status.update(status='PARTIAL',reason='fresh runner not verifiable')
                write_json(root/'fresh-runner-status.private.json',status);return
            write_json(root/'fresh-runner-status.private.json',status)
    status['status']='PASS';write_json(root/'fresh-runner-status.private.json',status)

def serve_once(root,fixture,index,port):
    endpoint=f'http://127.0.0.1:{port}'
    env=os.environ.copy();env['OLLAMA_HOST']=f'127.0.0.1:{port}'
    path=root/'controls'/'servers'/fixture/f'{index:03d}'
    path.mkdir(parents=True,exist_ok=False)
    log=(path/'server.private.log').open('wb')
    proc=subprocess.Popen(['ollama','serve'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
    try:
        deadline=time.monotonic()+45
        while True:
            if proc.poll() is not None:raise RuntimeError('owned server exited during startup')
            try:
                tagged_model(endpoint);break
            except Exception:
                if time.monotonic()>deadline:raise RuntimeError('owned server startup timeout')
                time.sleep(.5)
        row=one(root,fixture,'fresh_server',index,endpoint,proc.pid)
        row['owned_server_pid']=proc.pid
        write_json(root/'calls'/'fresh_server'/fixture/f'{index:03d}'/'result.private.json',row)
        return row
    finally:
        try:os.killpg(proc.pid,15)
        except ProcessLookupError:pass
        try:proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            try:os.killpg(proc.pid,9)
            except ProcessLookupError:pass
            proc.wait(timeout=10)
        log.close()

def fresh_server(root,port):
    status={'status':'RUNNING','completed':0,'reason':None};write_json(root/'fresh-server-status.private.json',status)
    for fixture in FIXTURES:
        for index in range(1,SERVER_COUNT+1):
            try:serve_once(root,fixture,index,port)
            except Exception as exc:
                status.update(status='NOT_RUN' if not status['completed'] else 'PARTIAL',reason=type(exc).__name__+': '+str(exc))
                write_json(root/'fresh-server-status.private.json',status);return
            status['completed']+=1;write_json(root/'fresh-server-status.private.json',status)
    status['status']='PASS';write_json(root/'fresh-server-status.private.json',status)

def main():
    p=ArgumentParser();p.add_argument('command',choices=('extract','warm','fresh-runner','fresh-server'))
    p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--replication-archive',type=Path);p.add_argument('--phase4-archive',type=Path)
    p.add_argument('--endpoint',default='http://127.0.0.1:11434');p.add_argument('--port',type=int,default=11435)
    a=p.parse_args()
    if a.command=='extract':
        if not a.replication_archive or not a.phase4_archive:p.error('extract requires both archives')
        extract(a.private_root,a.replication_archive,a.phase4_archive)
    elif a.command=='warm':warm(a.private_root,a.endpoint)
    elif a.command=='fresh-runner':fresh_runner(a.private_root,a.endpoint)
    else:fresh_server(a.private_root,a.port)
if __name__=='__main__':main()
