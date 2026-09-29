"""Standard-library-only fixture, request and response path; no world capability."""
import ast
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import time
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[2]
STUDY=ROOT/'research/qwen3-bounded-thinking-action-v0.1'
MODEL_FILE=Path('/tmp/horus-development-runtime-assets/model/Qwen3-14B-Q4_K_M.gguf')
MODEL_SHA256='500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0'
URL='http://127.0.0.1:18081'
BUDGET=128
MAX_TOKENS=768
ACTIONS=('ADVANCE','HOLD','RETREAT')
FORBIDDEN_PRIVATE_NAMES={'authority.key','events.jsonl','memory.sqlite3','checkpoint.json','training-records.jsonl'}
COUNTERS={'world_execution_count':0,'new_receipt_count':0,'memory_write_count':0,'protected_controller_execution_count':0}


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def sha(data):return sha256(data if isinstance(data,bytes) else data.encode()).hexdigest()
def digest(value):return sha(canonical(value))


def atomic_write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    with tmp.open('w') as stream:
        json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,path)


def verify_sources():
    m=json.loads((STUDY/'source-manifest.json').read_text())
    for relative,expected in m['source_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=expected:raise RuntimeError('frozen source drift: '+relative)
    return len(m['source_sha256'])


def action_system():
    """Parse frozen prompt bytes as source data; never import the protected protocol."""
    path=ROOT/'experiments/grounded_authority_autonomous_agent_v0/protocol.py'
    tree=ast.parse(path.read_text())
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ACTION_SYSTEM' for t in node.targets):
            return ast.literal_eval(node.value)
    raise RuntimeError('frozen action prompt absent')


def assert_read_only(private):
    if any(v!=0 for v in COUNTERS.values()):raise RuntimeError('nonzero protected side-effect counter')
    forbidden=[str(x.relative_to(private)) for x in private.rglob('*') if x.is_file() and
               (x.name in FORBIDDEN_PRIVATE_NAMES or x.suffix=='.sqlite3')]
    if forbidden:raise RuntimeError('protected world/Memory artifact in v0.1 private root: '+repr(forbidden))
    return dict(COUNTERS,forbidden_artifacts=[],status='PASS')


def verify_model():
    h=sha256()
    with MODEL_FILE.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8<<20),b''):h.update(chunk)
    if h.hexdigest()!=MODEL_SHA256:raise RuntimeError('pinned GGUF drift')
    with urlopen(URL+'/health',timeout=10) as response:
        if json.load(response).get('status')!='ok':raise RuntimeError('pinned server not healthy')
    return MODEL_SHA256


def build_request(projection,allowed,seed):
    if not allowed or len(set(allowed))!=len(allowed) or set(allowed)!=set(projection['available_actions']):
        raise ValueError('candidate set drift')
    if not set(allowed)<=set(ACTIONS):raise ValueError('unknown action')
    schema={'type':'object','properties':{'selected_action':{'type':'string','enum':allowed}},
            'required':['selected_action'],'additionalProperties':False}
    return {'messages':[{'role':'system','content':action_system()},
                        {'role':'user','content':canonical(projection)}],
        'temperature':.2,'top_p':.9,'top_k':40,'seed':seed,'max_tokens':MAX_TOKENS,
        'stream':False,'cache_prompt':False,'chat_template_kwargs':{'enable_thinking':True},
        'response_format':{'type':'json_object','schema':schema}}


def tokenize(content):
    wire=json.dumps({'content':content,'add_special':False},separators=(',',':')).encode()
    try:
        with urlopen(Request(URL+'/tokenize',data=wire,headers={'Content-Type':'application/json'}),timeout=10) as response:
            tokens=json.load(response).get('tokens')
        return len(tokens) if isinstance(tokens,list) else None
    except Exception:return None


def parse_final(response,allowed):
    if not isinstance(response,dict):raise ValueError('missing response')
    choices=response.get('choices')
    if not isinstance(choices,list) or len(choices)!=1:raise ValueError('ambiguous choice count')
    choice=choices[0];message=choice.get('message') or {}
    content=message.get('content');reasoning=message.get('reasoning_content')
    if not isinstance(reasoning,str) or not reasoning.strip():raise ValueError('missing separate reasoning')
    if not isinstance(content,str) or '<think>' in content or '</think>' in content:
        raise ValueError('missing final content or mixed reasoning')
    if choice.get('finish_reason')!='stop':raise ValueError('final action incomplete')
    def pairs(items):
        if len(items)!=len({k for k,_ in items}):raise ValueError('duplicate JSON field')
        return dict(items)
    parsed=json.loads(content,object_pairs_hook=pairs)
    if not isinstance(parsed,dict) or set(parsed)!={'selected_action'}:raise ValueError('final object has extra/missing field')
    action=parsed['selected_action']
    if type(action) is not str or action not in allowed:raise ValueError('invalid selected action')
    return action,content,reasoning


def metrics(response,wall):
    response=response if isinstance(response,dict) else {}
    choice=(response.get('choices') or [{}])[0];message=choice.get('message') or {}
    reasoning=message.get('reasoning_content');content=message.get('content')
    usage=response.get('usage') or {};timings=response.get('timings') or {}
    exact=(usage.get('completion_tokens_details') or {}).get('reasoning_tokens')
    reasoning_proxy=tokenize(reasoning) if isinstance(reasoning,str) else None
    final_proxy=tokenize(content) if isinstance(content,str) else None
    return dict(prompt_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),
        reasoning_tokens=exact if type(exact) is int else reasoning_proxy,
        reasoning_token_method='runtime_usage' if type(exact) is int else
            'pinned_local_tokenize_proxy' if reasoning_proxy is not None else 'UNAVAILABLE',
        final_output_tokens_proxy=final_proxy,
        final_token_method='pinned_local_tokenize_proxy' if final_proxy is not None else 'UNAVAILABLE',
        prompt_seconds=timings.get('prompt_ms',0)/1000,
        reasoning_generation_seconds=timings.get('predicted_ms',0)/1000,
        wall_seconds=wall,finish_reason=choice.get('finish_reason'),
        reasoning_sha256=sha(reasoning) if isinstance(reasoning,str) else None,
        final_sha256=sha(content) if isinstance(content,str) else None,
        reasoning_characters=len(reasoning) if isinstance(reasoning,str) else None,
        final_characters=len(content) if isinstance(content,str) else None)


def direct_call(row,private_root,phase):
    assert_read_only(private_root)
    path=private_root/phase/row['name']
    if path.exists():raise RuntimeError('refusing duplicate physical call')
    path.mkdir(parents=True)
    request=build_request(row['projection'],row['allowed'],row['seed'])
    wire=json.dumps(request,separators=(',',':')).encode()
    if digest(request)!=row['request_sha256'] or sha(wire)!=row['request_bytes_sha256'] or digest(row['projection'])!=row['projection_sha256']:
        raise RuntimeError('frozen request/projection digest drift')
    atomic_write(path/'intent.private.json',dict(request=request,request_sha256=digest(request),
        request_bytes_sha256=sha(wire),projection_sha256=digest(row['projection'])))
    response=None;error=None;started=time.perf_counter()
    try:
        with urlopen(Request(URL+'/v1/chat/completions',data=wire,
                             headers={'Content-Type':'application/json'}),timeout=600) as stream:
            response=json.load(stream)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    wall=time.perf_counter()-started
    atomic_write(path/'response.private.json',dict(response=response,transport_error=error,wall_seconds=wall))
    out=dict(name=row['name'],status='FAIL',transport_error=error,
        projection_sha256=digest(row['projection']),request_sha256=digest(request),
        request_bytes_sha256=sha(wire),response_sha256=digest(response) if response is not None else None,
        metrics=metrics(response,wall))
    if error:out['parse_error']='transport: '+error
    else:
        try:action,_,_=parse_final(response,row['allowed'])
        except (ValueError,TypeError,KeyError,IndexError) as exc:out['parse_error']=repr(exc)
        else:out.update(status='PASS',action=action)
    atomic_write(path/'verdict.private.json',out)
    assert_read_only(private_root)
    return out


def old_fixtures():
    return json.loads((ROOT/'research/qwen3-grounded-agent-substitution-v0/stage-a-fixtures.json').read_text())['fixtures']


def base_projections():
    f=old_fixtures();a=deepcopy(f['A']['projection']);a['available_actions']=list(ACTIONS)
    a2=deepcopy(f['F']['projection']);a2['available_actions']=list(ACTIONS)
    e=deepcopy(f['E']['projection'])
    b2=deepcopy(e)
    b2['grounded_assessments']['ADVANCE']=deepcopy(f['B2']['projection']['grounded_assessments']['ADVANCE'])
    authority=json.loads((ROOT/'research/grounded-authority-autonomous-agent-v0/public-result.json').read_text())
    unseen_hold=deepcopy(authority['runs']['A']['decisions'][3]['grounded_assessments_before']['HOLD'])
    unseen_hold.pop('recent_receipt_provenance',None)
    b2['grounded_assessments']['HOLD']=unseen_hold
    bases={'A1':a,'A2':a2,'B1_E':e,'B2':b2,'C1':deepcopy(f['C1']['projection']),
           'C2':deepcopy(f['C2']['projection']),'D':deepcopy(f['D']['projection'])}
    aa=a['grounded_assessments'];bb=a2['grounded_assessments']
    assert [aa[x]['established_value']['consequence'] for x in ACTIONS]==[1,-1,0]
    assert [bb[x]['established_value']['consequence'] for x in ACTIONS]==[-1,1,0]
    assert e['grounded_assessments']['HOLD']['kind']=='ESTABLISHED'
    assert b2['grounded_assessments']['ADVANCE']['kind']=='ESTABLISHED' and b2['grounded_assessments']['HOLD']['kind']=='UNSEEN'
    return bases


def make_plan():
    bases=base_projections();matrix=[]
    for case,orders in [('A1',('O0','O1','O2')),('A2',('O0','O1','O2')),
                        ('B1_E',('O0','O1','O2')),('B2',('O0','O1','O2')),
                        ('C1',('O0','O1')),('C2',('O0','O1')),
                        ('D',('O0','O1','O2'))]:
        original=bases[case];allowed=list(original['available_actions'])
        for order in orders:
            projection=deepcopy(original)
            if order=='O1':projection['available_actions']=list(reversed(allowed))
            if order=='O2':projection['available_actions']=allowed[1:]+allowed[:1]
            seed=3303+projection['decision_index']
            request=build_request(projection,allowed,seed)
            matrix.append(dict(name=case+'_'+order,case=case,order=order,
                projection=projection,allowed=allowed,seed=seed,
                projection_sha256=digest(projection),request_sha256=digest(request),
                request_bytes_sha256=sha(json.dumps(request,separators=(',',':')).encode())))
    assert len(matrix)==19
    probes=[]
    for i,case in enumerate(('D','A1','B1_E')):
        projection=deepcopy(bases[case]);allowed=list(projection['available_actions']);seed=88101+i
        request=build_request(projection,allowed,seed)
        probes.append(dict(name='P'+str(i+1)+'_'+case,case=case,order='O0',
            projection=projection,allowed=allowed,seed=seed,
            projection_sha256=digest(projection),request_sha256=digest(request),
            request_bytes_sha256=sha(json.dumps(request,separators=(',',':')).encode())))
    return dict(status='FROZEN_BEFORE_INFERENCE',budget=BUDGET,total_completion_cap=MAX_TOKENS,
        read_only_before_inference=dict(COUNTERS),preflight=probes,stage_a=matrix,
        synthetic_b2_source='E plus B2 ADVANCE established-0 plus grounded-authority A decision 4 HOLD unseen; no world execution')
