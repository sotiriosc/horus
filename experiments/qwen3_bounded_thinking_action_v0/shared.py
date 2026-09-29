"""Only final content crosses the authoritative action boundary; reasoning stays private."""
from pathlib import Path
from hashlib import sha256
import json

from horus.core import digest
from horus.live import _atomic_write
from experiments.qwen3_thinking_action_audit_v0 import shared as parent

ROOT=Path(__file__).resolve().parents[2]
STUDY=ROOT/'research/qwen3-bounded-thinking-action-v0'
PREREG_COMMIT='33076ce'
BUDGETS=(128,256,384)
MAX_TOKENS=768
PRIVATE_STUDY='QWEN3_BOUNDED_THINKING_ACTION_V0'
MODEL_SHA256=parent.MODEL_SHA256
Q_URL=parent.Q_URL
sha=parent.sha
parse_final=parent.parse_final
transport=parent.transport
tokenize=parent.tokenize
verify_model=parent.verify_model


def verify_sources():
    manifest=json.loads((STUDY/'source-manifest.json').read_text())
    for relative,expected in manifest['frozen_source_sha256'].items():
        if sha((ROOT/relative).read_bytes())!=expected:
            raise RuntimeError('frozen source drift: '+relative)
    return len(manifest['frozen_source_sha256'])


def build_request(projection,allowed,seed):
    request=parent.build_request(projection,allowed,seed)
    assert request['max_tokens']==512 and request['chat_template_kwargs']=={'enable_thinking':True}
    request['max_tokens']=MAX_TOKENS
    return request


def safe_metrics(response,wall):
    if not isinstance(response,dict):
        return dict(wall_seconds=wall,input_tokens=None,completion_tokens=None,
            reasoning_tokens_proxy=None,final_output_tokens_proxy=None)
    choices=response.get('choices') or [{}]
    choice=choices[0] if len(choices)==1 and isinstance(choices[0],dict) else {}
    message=choice.get('message') or {}
    reasoning=message.get('reasoning_content');content=message.get('content')
    usage=response.get('usage') or {};timings=response.get('timings') or {}
    details=usage.get('completion_tokens_details') or {}
    exact=details.get('reasoning_tokens')
    reasoning_proxy=tokenize(reasoning) if isinstance(reasoning,str) else None
    final_proxy=tokenize(content) if isinstance(content,str) else None
    return dict(input_tokens=usage.get('prompt_tokens'),completion_tokens=usage.get('completion_tokens'),
        reasoning_tokens=exact if type(exact) is int else reasoning_proxy,
        reasoning_token_method='runtime_usage' if type(exact) is int else
            'pinned_local_tokenize_proxy' if reasoning_proxy is not None else 'UNAVAILABLE',
        final_output_tokens_proxy=final_proxy,final_token_method='pinned_local_tokenize_proxy' if final_proxy is not None else 'UNAVAILABLE',
        prompt_time_seconds=timings.get('prompt_ms',0)/1000,
        reasoning_generation_time_seconds=timings.get('predicted_ms',0)/1000,
        wall_seconds=wall,finish_reason=choice.get('finish_reason'),
        reasoning_sha256=sha(reasoning) if isinstance(reasoning,str) else None,
        final_content_sha256=sha(content) if isinstance(content,str) else None,
        reasoning_characters=len(reasoning) if isinstance(reasoning,str) else None,
        final_characters=len(content) if isinstance(content,str) else None)


def direct_action(projection,allowed,seed,private_path,budget):
    """One physical attempt; no retry, no world execution, raw content only private."""
    if budget not in BUDGETS:raise ValueError('unregistered budget')
    if private_path.exists():raise RuntimeError('refusing to retry existing model call')
    private_path.mkdir(parents=True)
    request=build_request(projection,allowed,seed)
    _atomic_write(private_path/'intent.private.json',dict(request=request,budget=budget,
        request_sha256=digest(request),semantic_projection_sha256=digest(projection)))
    wire,response,error,wall=transport(request)
    _atomic_write(private_path/'response.private.json',dict(response=response,error=error,
        wall_seconds=wall,wire_sha256=sha(wire)))
    result=dict(budget=budget,request_sha256=digest(request),request_bytes_sha256=sha(wire),
        semantic_projection_sha256=digest(projection),
        raw_response_sha256=digest(response) if response is not None else None,
        transport_error=error,metrics=safe_metrics(response,wall))
    if error:
        result.update(status='FAIL',parse_error='transport: '+error)
    else:
        try:action,_,_=parse_final(response,allowed)
        except (ValueError,KeyError,TypeError,IndexError) as exc:
            result.update(status='FAIL',parse_error=repr(exc))
        else:result.update(status='PASS',action=action)
    _atomic_write(private_path/'verdict.private.json',result)
    return result
