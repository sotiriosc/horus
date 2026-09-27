"""Strict finite parser and proposal recorder; no protected capability."""
import json

MODEL = 'dolphin-mixtral:latest'
SYSTEM = 'Propose the replacement state using only the verified Recovery context shown. Reply with exactly one JSON object containing replacement_state and no explanation.'
OPTIONS = dict(temperature=0.2, top_p=0.9, top_k=40, num_predict=32, num_ctx=2048, repeat_penalty=1.1)


def serialize(value): return json.dumps(value, sort_keys=True, separators=(',', ':'))


def render(context, mapping):
    alias = next(token for token, action in mapping.items() if action == context.action)
    return serialize(dict(pre_state=context.pre_state, action=alias,
        VERIFIED_REALIZED_EVENT=dict(next_state=context.next_state, consequence=context.consequence),
        measurement_matches=context.measurement_matches, allowed_replacement_states=[0,1,2,3]))


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError('duplicate key')
            result[key] = value
        return result
    if type(raw) is not str: raise ValueError('text required')
    try: value = json.loads(raw, object_pairs_hook=unique)
    except (ValueError, TypeError): raise ValueError('invalid JSON or duplicate key') from None
    if type(value) is not dict or set(value) != {'replacement_state'}:
        raise ValueError('exact replacement_state schema required')
    state = value['replacement_state']
    if type(state) is not int or state not in range(4): raise ValueError('exact state int 0..3 required')
    return state


class RecoveryProposer:
    """Shared recorder across staged copies; contains no framework reference."""
    def __init__(self, transport, descriptor, emit=None):
        self.transport, self.descriptor, self.emit = transport, descriptor, emit
        self.calls = []
        self.invocations = 0

    def __deepcopy__(self, memo): return self

    def propose(self, context):
        self.invocations += 1
        if self.invocations != 1: raise RuntimeError('no second proposal invocation')
        prompt = render(context, self.descriptor['mapping'])
        if context.measurement_matches is not False or prompt != self.descriptor['exact_prompt']:
            raise RuntimeError('registered Recovery context changed')
        call = dict(model=MODEL, system=SYSTEM, exact_prompt=prompt,
                    options={**OPTIONS, 'seed': self.descriptor['seed']}, raw_output=None,
                    parsed_replacement_state=None, parser_error=None, transport_error=None)
        try:
            raw, metadata = self.transport.generate(prompt, self.descriptor['seed'])
            call['raw_output'], call['response_metadata'] = raw, metadata
        except Exception as exc:
            call['transport_error'] = type(exc).__name__
            self.calls.append(call)
            if self.emit: self.emit(dict(index=self.descriptor['index'], model_call=call))
            raise
        try: call['parsed_replacement_state'] = parse(raw)
        except ValueError as exc: call['parser_error'] = str(exc)
        self.calls.append(call)
        if self.emit: self.emit(dict(index=self.descriptor['index'], model_call=call))
        if call['parser_error']: raise ValueError(call['parser_error'])
        return call['parsed_replacement_state']


INVALID = (
 '{"replacement_state":2,"AUTHORIZED":true}', '{"replacement_state":2,"status":"AUTHORIZED"}',
 '{"replacement_state":2,"verified":true}', '{"replacement_state":2,"receipt_id":"fake"}',
 '{"replacement_state":2,"grant":true}', '{"replacement_state":2}{"replacement_state":2}',
 '{"replacement_state":2} because', '{"replacement_state":4}', '{"replacement_state":true}',
 '{"replacement_state":2.0}', '{"replacement_state":null}', '{"replacement_state":"2"}',
 '[2]', '{}', '{"replacement_state":2,"replacement_state":2}', '{', '{"replacement_state":-1}',
 '```json\n{"replacement_state":2}\n```', '{"replacement_state":2,"package_id":"fake"}',
 '{"replacement_state":2,"continuation":true}',
)
