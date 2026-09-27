"""Bounded request-local transport repair, with durable physical-attempt records."""
import copy
from hashlib import sha256
import json
import time
import urllib.request
import urllib.error
from horus.live import ModelClient
from .atomic import flush

RULE = dict(maximum_attempts=2, identical_request_bytes=True,
    eligible_errors=['TimeoutError', 'ConnectionError', 'ConnectionResetError',
                    'ConnectionAbortedError', 'ConnectionRefusedError',
                    'BrokenPipeError', 'RemoteDisconnected', 'URLError', 'HTTP_SERVICE_INTERRUPTION'],
    eligible_http_status=[408, 429, 500, 502, 503, 504],
    semantic_retry=False, batch_retry=False, before_execution_only=True)
RULE_HASH = sha256(json.dumps(RULE, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def invoke(client, request):
    if type(client) is not ModelClient:
        return client.generate(request)
    # Frozen HTTP serialization, timeout and response validation, with status
    # retained so client/schema errors cannot be retried as service outages.
    client.requests += 1
    req = urllib.request.Request(client.endpoint + '/api/generate',
        data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=600) as response:
            value=json.load(response)
        if value.get('done') is not True or type(value.get('response')) is not str:
            raise ValueError('incomplete model response')
        return dict(raw_output=value['response'], transport_error=None,
            response_metadata={k:value[k] for k in ('model','created_at','done',
                'total_duration','load_duration','prompt_eval_count','prompt_eval_duration',
                'eval_count','eval_duration') if k in value})
    except urllib.error.HTTPError as exc:
        return dict(raw_output=None, transport_error=('HTTP_SERVICE_INTERRUPTION'
            if exc.code in RULE['eligible_http_status'] else 'HTTP_REQUEST_REJECTED'),
            response_metadata=dict(http_status=exc.code))
    except Exception as exc:
        return dict(raw_output=None, transport_error=type(exc).__name__,response_metadata={})


def generate(client, request, store, call_id):
    # Same serializer used by the frozen ModelClient; preserve insertion order.
    wire = json.dumps(request).encode()
    wire_hash = sha256(wire).hexdigest()
    for attempt in (1, 2):
        attempt_id = f'{call_id}:transport:{attempt}'
        store.append('calls', 'TRANSPORT_ATTEMPT_INTENT', dict(call_id=call_id,
            attempt=attempt, attempt_id=attempt_id, request_bytes_utf8=wire.decode(),
            request_bytes_sha256=wire_hash, repair_rule_sha256=RULE_HASH))
        flush(store)
        started = time.perf_counter()
        try:
            result = invoke(client, copy.deepcopy(request))
        except Exception as exc:
            result = dict(raw_output=None, transport_error=type(exc).__name__,
                          response_metadata={})
        seconds = time.perf_counter() - started
        error = result.get('transport_error')
        eligible = error in RULE['eligible_errors']
        kind = 'TRANSPORT_FAILURE' if eligible else 'MODEL_OUTPUT_INVALID' if error else 'RESPONSE_RECEIVED'
        store.append('calls', 'TRANSPORT_ATTEMPT_RESULT', dict(call_id=call_id,
            attempt=attempt, attempt_id=attempt_id, request_bytes_sha256=wire_hash,
            outcome=kind, repair_eligible=eligible, response=result,
            seconds=seconds, repaired=(attempt == 2 and not error),
            unrepaired=(eligible and attempt == 2)))
        flush(store)
        if not eligible or attempt == 2:
            return result
    raise AssertionError('unreachable')
