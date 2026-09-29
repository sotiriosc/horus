"""Frozen model-route replacement; reasoning is private and never enters policy."""
from hashlib import sha256
from pathlib import Path
from urllib.request import Request,urlopen
import json,time

from horus.core import digest
from experiments.grounded_authority_autonomous_agent_v0.protocol import source_for_model_choice
from experiments.qwen3_bounded_thinking_action_v0_1.pure import (
    ROOT,MODEL_SHA256,URL,build_request,parse_final,metrics,sha,verify_model)

STUDY=ROOT/'research/qwen3-r128-autonomous-grounded-agent-v0'
PRIVATE_STUDY='QWEN3_R128_AUTONOMOUS_GROUNDED_AGENT_V0'
PREREG_COMMIT='53d021740617b5dae835b82b582904bb2c3fd9a1'


def verify_sources():
    manifest=json.loads((STUDY/'source-manifest.json').read_text())
    for relative,expected in manifest['frozen_source_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=expected:
            raise RuntimeError('frozen source drift: '+relative)
    return len(manifest['frozen_source_sha256'])


def save(store):
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])


def live_action(store,index,ctx):
    """One model attempt on a legitimate MODEL route; only strict final action is authoritative."""
    route=ctx['route']
    if route['route']!='MODEL':raise RuntimeError('model invoked outside MODEL route')
    projection=ctx['projection'];allowed=route['candidates']
    request=build_request(projection,allowed,3303+index)
    wire=json.dumps(request,separators=(',',':')).encode();call_id=f'T:{index}:ACTION:1'
    store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role='ACTION',
        semantic_projection_sha256=digest(projection),request_sha256=digest(request),
        request_bytes_sha256=sha(wire),model_artifact_sha256=MODEL_SHA256,
        preregistration_commit=PREREG_COMMIT))
    save(store)
    store.append('calls','TRANSPORT_ATTEMPT_INTENT',dict(call_id=call_id,attempt=1,
        request_bytes_utf8=wire.decode(),request_bytes_sha256=sha(wire)))
    save(store)
    response=None;error=None;started=time.perf_counter()
    try:
        with urlopen(Request(URL+'/v1/chat/completions',data=wire,
                             headers={'Content-Type':'application/json'}),timeout=600) as result:
            response=json.load(result)
    except Exception as exc:error=type(exc).__name__+': '+str(exc)
    wall=time.perf_counter()-started
    store.append('calls','TRANSPORT_ATTEMPT_RESULT',dict(call_id=call_id,attempt=1,
        response=response,transport_error=error,seconds=wall,request_bytes_sha256=sha(wire)))
    save(store)
    if error:
        store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status='INVALID',
            selected_action=None,error='transport: '+error))
        save(store)
        raise RuntimeError('invalid Q-TB action transport: '+error)
    try:action,content,reasoning=parse_final(response,allowed)
    except (ValueError,TypeError,KeyError,IndexError) as exc:
        store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status='INVALID',
            selected_action=None,error=repr(exc),raw_response_sha256=digest(response)))
        save(store)
        raise RuntimeError('invalid Q-TB final action: '+repr(exc))
    store.append('calls','PARSED',dict(call_id=call_id,role='ACTION',status='VALID',
        selected_action=action,reasoning_sha256=sha(reasoning),
        final_content_sha256=sha(content),raw_response_sha256=digest(response)))
    source=source_for_model_choice(route,ctx['assessments'],action)
    store.append('calls','ACTION_FROZEN',dict(decision_id=f'C:D{index:02d}',
        selected_action=action,decision_source=source,action_call_id=call_id,
        raw_output_sha256=sha(content)))
    save(store)
    m=metrics(response,wall)
    info=dict(call_id=call_id,raw_output_sha256=sha(content),request_sha256=digest(request),
        request_bytes_sha256=sha(wire),raw_response_sha256=digest(response),
        context_tokens=m['prompt_tokens'],output_tokens=m['completion_tokens'],
        latency_seconds=wall,prompt_eval_duration_seconds=m['prompt_seconds'],
        generation_duration_seconds=m['reasoning_generation_seconds'],
        runner_load_duration_seconds=0,status='VALID',reasoning_metrics=m)
    return action,source,route,info,ctx['assessments'],ctx['suffix']
