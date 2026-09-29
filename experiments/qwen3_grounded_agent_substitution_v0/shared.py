"""Frozen-source checks and private, exact Qwen transport at the promoted model boundary."""
from hashlib import sha256
from pathlib import Path
import json
import time
from urllib.request import Request, urlopen

from experiments.modern_memory_vs_horus_v0.storage import canonical
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    ACTION_SYSTEM, source_for_model_choice)
from horus.core import digest

ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / 'research/qwen3-grounded-agent-substitution-v0'
MODEL_FILE = Path('/tmp/horus-development-runtime-assets/model/Qwen3-14B-Q4_K_M.gguf')
MODEL_SHA256 = '500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0'
Q_URL = 'http://127.0.0.1:18081'
PREREG_COMMIT = '33670789ab58422271a12c6569204319857516ef'


def sha(data):
    return sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def verify_sources():
    manifest = json.loads((STUDY / 'source-manifest.json').read_text())
    for relative, expected in manifest['sha256'].items():
        if sha((ROOT / relative).read_bytes()) != expected:
            raise RuntimeError('frozen source drift: ' + relative)
    return len(manifest['sha256'])


def verify_q_model():
    if not MODEL_FILE.is_file():
        raise RuntimeError('pinned Qwen GGUF unavailable')
    h = sha256()
    with MODEL_FILE.open('rb') as stream:
        for part in iter(lambda: stream.read(8 << 20), b''):
            h.update(part)
    if h.hexdigest() != MODEL_SHA256:
        raise RuntimeError('pinned Qwen GGUF digest mismatch')
    with urlopen(Q_URL + '/health', timeout=5) as response:
        if json.load(response).get('status') != 'ok':
            raise RuntimeError('Qwen development server not ready')
    return h.hexdigest()


def q_action(store, index, ctx):
    """Only substitute the model transport; route, escape and protected execution stay frozen."""
    route = ctx['route']
    if route['route'] != 'MODEL':
        raise RuntimeError('Q model called outside model-authority route')
    allowed = route['candidates']
    schema = {'type': 'object', 'properties': {'selected_action': {'type': 'string', 'enum': allowed}},
              'required': ['selected_action'], 'additionalProperties': False}
    request = {
        'messages': [{'role': 'system', 'content': ACTION_SYSTEM},
                     {'role': 'user', 'content': canonical(ctx['projection'])}],
        'temperature': 0.2, 'top_p': 0.9, 'top_k': 40, 'seed': 3303 + index,
        'max_tokens': 48, 'stream': False, 'cache_prompt': False,
        'chat_template_kwargs': {'enable_thinking': False},
        'response_format': {'type': 'json_object', 'schema': schema}}
    wire = json.dumps(request, separators=(',', ':')).encode()
    call_id = f'Q:{index}:ACTION:1'
    store.append('calls', 'REQUEST_INTENT', dict(call_id=call_id, role='ACTION',
        semantic_projection_sha256=digest(ctx['projection']), request_bytes_sha256=sha(wire),
        model_artifact_sha256=MODEL_SHA256, preregistration_commit=PREREG_COMMIT))
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    store.append('calls', 'TRANSPORT_ATTEMPT_INTENT', dict(call_id=call_id,
        attempt=1, request_bytes_utf8=wire.decode(), request_bytes_sha256=sha(wire)))
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    started = time.perf_counter()
    response = None
    error = None
    try:
        req = Request(Q_URL + '/v1/chat/completions', data=wire,
                      headers={'Content-Type': 'application/json'})
        with urlopen(req, timeout=600) as result:
            response = json.load(result)
    except Exception as exc:
        error = type(exc).__name__ + ': ' + str(exc)
    latency = time.perf_counter() - started
    store.append('calls', 'TRANSPORT_ATTEMPT_RESULT', dict(call_id=call_id,
        attempt=1, response=response, transport_error=error, seconds=latency,
        request_bytes_sha256=sha(wire)))
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    if error:
        raise RuntimeError('Q action transport failure: ' + error)
    try:
        raw = response['choices'][0]['message']['content']
        parsed = parse_action(raw)
        action = parsed['selected_action']
        if action not in allowed:
            raise ValueError('Q action outside admissible set')
        status = 'VALID'
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        action = None
        status = 'INVALID'
        error = repr(exc)
    store.append('calls', 'PARSED', dict(call_id=call_id, role='ACTION',
        status=status, selected_action=action, error=error,
        raw_output_sha256=sha(raw if 'raw' in locals() else '')))
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    if status != 'VALID':
        raise RuntimeError('invalid Q authoritative action: ' + error)
    source = source_for_model_choice(route, ctx['assessments'], action)
    store.append('calls', 'ACTION_FROZEN', dict(decision_id=f'C:D{index:02d}',
        selected_action=action, decision_source=source, action_call_id=call_id,
        raw_output_sha256=sha(raw)))
    store.save(state=store.checkpoint['current_state'],
               next_transaction_id=store.checkpoint['next_transaction_id'])
    timing = response.get('timings') or {}
    usage = response.get('usage') or {}
    info = dict(call_id=call_id, raw_output_sha256=sha(raw), request_sha256=sha(wire),
        context_tokens=usage.get('prompt_tokens', 0), output_tokens=usage.get('completion_tokens', 0),
        latency_seconds=latency, prompt_eval_duration_seconds=timing.get('prompt_ms', 0)/1000,
        generation_duration_seconds=timing.get('predicted_ms', 0)/1000,
        runner_load_duration_seconds=0, status=status)
    return action, source, route, info, ctx['assessments'], ctx['suffix']
