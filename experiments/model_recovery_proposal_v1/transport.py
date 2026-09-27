"""Stateless local generation. No retry and no authority reference."""
import json
import urllib.request
from .adapter import MODEL, SYSTEM, OPTIONS


class LocalModel:
    endpoint = 'http://127.0.0.1:11434'
    def __init__(self): self.requests = 0
    def generate(self, prompt, seed):
        if self.requests >= 96: raise RuntimeError('frozen call limit')
        self.requests += 1
        request = urllib.request.Request(self.endpoint + '/api/generate', data=json.dumps(dict(
            model=MODEL, system=SYSTEM, prompt=prompt, stream=False, options={**OPTIONS, 'seed':seed})).encode(),
            headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request, timeout=600) as response: data = json.load(response)
        if not data.get('done') or type(data.get('response')) is not str:
            raise RuntimeError('incomplete response; no retry')
        return data['response'], {k:data[k] for k in ('model','created_at','done','total_duration',
            'load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration') if k in data}


def metadata(transport, frozen, proof):
    assert proof['manifest_sha256'] == frozen['model']['manifest_digest']
    assert proof['weights_sha256'] == frozen['model']['weights_digest']
    def get(name, payload=None):
        req=urllib.request.Request(transport.endpoint+'/api/'+name,
            data=None if payload is None else json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=30) as response: return json.load(response)
    version=get('version'); assert version['version']=='0.1.16'
    model=next(m for m in get('tags')['models'] if m['name']==MODEL)
    assert model['digest']==frozen['model']['manifest_digest']
    shown=get('show',dict(name=MODEL))
    assert shown['template']=='<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n'
    assert model['details']['parameter_size']=='47B' and model['details']['quantization_level']=='Q4_0'
    return dict(model=MODEL,system=SYSTEM,options=OPTIONS,server=version,installed_model=model,
                template={k:shown[k] for k in ('template','system','parameters','details') if k in shown},
                verified_model_bytes=proof)
