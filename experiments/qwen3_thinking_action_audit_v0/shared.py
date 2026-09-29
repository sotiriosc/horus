"""Frozen native-thinking transport; only final content can become an action."""
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json
import time

from horus.core import digest
from horus.live import _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import canonical
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
from experiments.grounded_authority_autonomous_agent_v0.protocol import ACTION_SYSTEM, source_for_model_choice
from experiments.qwen3_grounded_agent_substitution_v0.shared import MODEL_FILE, MODEL_SHA256, Q_URL

ROOT=Path(__file__).resolve().parents[2]
STUDY=ROOT/'research/qwen3-thinking-action-audit-v0'
PRIVATE_STUDY='QWEN3_THINKING_ACTION_AUDIT_V0'
PREREG_COMMIT='04b2fd8'
MAX_TOKENS=512


def sha(data):return sha256(data if isinstance(data,bytes) else data.encode()).hexdigest()


def verify_sources():
    manifest=json.loads((STUDY/'source-manifest.json').read_text())
    for relative,expected in manifest['source_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=expected:
            raise RuntimeError('frozen source drift: '+relative)
    return len(manifest['source_sha256'])


def verify_model():
    h=sha256()
    with MODEL_FILE.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8<<20),b''):h.update(chunk)
    if h.hexdigest()!=MODEL_SHA256:raise RuntimeError('Qwen artifact digest mismatch')
    with urlopen(Q_URL+'/health',timeout=10) as response:
        if json.load(response).get('status')!='ok':raise RuntimeError('thinking server not ready')
    return h.hexdigest()


def build_request(projection,allowed,seed):
    if not allowed or len(set(allowed))!=len(allowed):raise ValueError('invalid candidate list')
    if set(projection['available_actions'])!=set(allowed):raise ValueError('projection candidate drift')
    schema=dict(type='object',properties={'selected_action':dict(type='string',enum=allowed)},
                required=['selected_action'],additionalProperties=False)
    return dict(messages=[dict(role='system',content=ACTION_SYSTEM),
                          dict(role='user',content=canonical(projection))],
        temperature=.2,top_p=.9,top_k=40,seed=seed,max_tokens=MAX_TOKENS,
        stream=False,cache_prompt=False,
        chat_template_kwargs={'enable_thinking':True},
        response_format={'type':'json_object','schema':schema})


def transport(request):
    wire=json.dumps(request,separators=(',',':')).encode()
    started=time.perf_counter();response=None;error=None
    try:
        with urlopen(Request(Q_URL+'/v1/chat/completions',data=wire,
                             headers={'Content-Type':'application/json'}),timeout=600) as stream:
            response=json.load(stream)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    return wire,response,error,time.perf_counter()-started


def tokenize(text):
    wire=json.dumps({'content':text,'add_special':False},separators=(',',':')).encode()
    try:
        with urlopen(Request(Q_URL+'/tokenize',data=wire,
                             headers={'Content-Type':'application/json'}),timeout=10) as stream:
            value=json.load(stream)
        tokens=value.get('tokens')
        return len(tokens) if isinstance(tokens,list) else None
    except Exception:return None


def parse_final(response,allowed):
    if not isinstance(response,dict):raise ValueError('missing response')
    choices=response.get('choices')
    if not isinstance(choices,list) or len(choices)!=1:raise ValueError('ambiguous choice count')
    choice=choices[0];message=choice.get('message') or {}
    content=message.get('content');reasoning=message.get('reasoning_content')
    if not isinstance(reasoning,str) or not reasoning.strip():
        raise ValueError('native reasoning was not separately observed')
    if not isinstance(content,str) or '<think>' in content or '</think>' in content:
        raise ValueError('reasoning mixed into final content or final content missing')
    if choice.get('finish_reason')!='stop':raise ValueError('final action did not complete')
    action=parse_action(content)['selected_action']
    if action not in allowed:raise ValueError('action outside current candidate set')
    return action,content,reasoning


def safe_metrics(response,wall,content,reasoning):
    usage=response.get('usage') or {};timings=response.get('timings') or {}
    details=usage.get('completion_tokens_details') or {}
    exact_reasoning=details.get('reasoning_tokens')
    proxy_reasoning=tokenize(reasoning)
    proxy_final=tokenize(content)
    return dict(input_tokens=usage.get('prompt_tokens'),
        completion_tokens=usage.get('completion_tokens'),
        reasoning_tokens=exact_reasoning if type(exact_reasoning) is int else proxy_reasoning,
        reasoning_token_count_method='runtime_usage' if type(exact_reasoning) is int else
                                     'local_tokenize_proxy' if proxy_reasoning is not None else 'UNAVAILABLE',
        final_output_tokens_proxy=proxy_final,
        final_token_count_method='local_tokenize_proxy' if proxy_final is not None else 'UNAVAILABLE',
        prompt_eval_seconds=timings.get('prompt_ms',0)/1000,
        reasoning_and_generation_seconds=timings.get('predicted_ms',0)/1000,
        wall_seconds=wall,finish_reason=response['choices'][0].get('finish_reason'),
        reasoning_sha256=sha(reasoning),final_content_sha256=sha(content),
        reasoning_characters=len(reasoning),final_characters=len(content))


def direct_action(projection,allowed,seed,private_path):
    """One read-only physical model attempt, with private raw response preservation."""
    if private_path.exists():raise RuntimeError('refusing to retry existing direct call')
    private_path.mkdir(parents=True)
    request=build_request(projection,allowed,seed)
    _atomic_write(private_path/'intent.private.json',dict(request=request,
        request_sha256=digest(request),semantic_projection_sha256=digest(projection)))
    wire,response,error,wall=transport(request)
    _atomic_write(private_path/'response.private.json',dict(response=response,error=error,
        wall_seconds=wall,wire_sha256=sha(wire)))
    result=dict(request_sha256=digest(request),request_bytes_sha256=sha(wire),
        semantic_projection_sha256=digest(projection),wall_seconds=wall,
        raw_response_sha256=digest(response) if response is not None else None,
        transport_error=error)
    if error:
        result.update(status='INTERFACE_INCOMPATIBLE',parse_error='transport: '+error)
        _atomic_write(private_path/'verdict.private.json',result)
        return result
    try:action,content,reasoning=parse_final(response,allowed)
    except (ValueError,KeyError,TypeError) as exc:
        result.update(status='INTERFACE_INCOMPATIBLE',parse_error=repr(exc))
        _atomic_write(private_path/'verdict.private.json',result)
        return result
    result.update(status='VALID',action=action,metrics=safe_metrics(response,wall,content,reasoning))
    _atomic_write(private_path/'verdict.private.json',result)
    return result


def live_action(store,index,ctx):
    """Replace only the frozen MODEL-route transport; never expose thought to policy."""
    route=ctx['route']
    if route['route']!='MODEL':raise RuntimeError('thinking model called outside MODEL route')
    projection=ctx['projection'];allowed=route['candidates']
    request=build_request(projection,allowed,3303+index)
    wire=json.dumps(request,separators=(',',':')).encode();call_id=f'T:{index}:ACTION:1'
    store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role='ACTION',
        semantic_projection_sha256=digest(projection),request_bytes_sha256=sha(wire),
        model_artifact_sha256=MODEL_SHA256,preregistration_commit=PREREG_COMMIT))
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    store.append('calls','TRANSPORT_ATTEMPT_INTENT',dict(call_id=call_id,attempt=1,
        request_bytes_utf8=wire.decode(),request_bytes_sha256=sha(wire)))
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    actual_wire,response,error,wall=transport(request)
    if actual_wire!=wire:raise RuntimeError('transport wire changed after intent')
    store.append('calls','TRANSPORT_ATTEMPT_RESULT',dict(call_id=call_id,attempt=1,
        response=response,transport_error=error,seconds=wall,request_bytes_sha256=sha(wire)))
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    if error:raise RuntimeError('thinking transport failure: '+error)
    try:action,content,reasoning=parse_final(response,allowed)
    except (ValueError,KeyError,TypeError) as exc:
        store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status='INVALID',
            selected_action=None,error=repr(exc),raw_response_sha256=digest(response)))
        store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
        raise RuntimeError('invalid thinking final action: '+repr(exc))
    store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status='VALID',
        selected_action=action,reasoning_sha256=sha(reasoning),final_content_sha256=sha(content)))
    source=source_for_model_choice(route,ctx['assessments'],action)
    store.append('calls','ACTION_FROZEN',dict(decision_id=f'C:D{index:02d}',
        selected_action=action,decision_source=source,action_call_id=call_id,
        raw_output_sha256=sha(content)))
    store.save(state=store.checkpoint['current_state'],next_transaction_id=store.checkpoint['next_transaction_id'])
    m=safe_metrics(response,wall,content,reasoning)
    info=dict(call_id=call_id,raw_output_sha256=sha(content),request_sha256=sha(wire),
        context_tokens=m['input_tokens'],output_tokens=m['completion_tokens'],
        latency_seconds=wall,prompt_eval_duration_seconds=m['prompt_eval_seconds'],
        generation_duration_seconds=m['reasoning_and_generation_seconds'],
        runner_load_duration_seconds=0,status='VALID',thinking_metrics=m)
    return action,source,route,info,ctx['assessments'],ctx['suffix']
