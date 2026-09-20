"""Stateless, no-retry local transport and exact recorded-response transport."""
import json
import urllib.request


class LocalModel:
    endpoint='http://127.0.0.1:11434'
    def __init__(self):self.requests=0

    def generate(self,call):
        if self.requests>=288:raise RuntimeError('absolute inference budget')
        self.requests+=1
        payload=dict(model=call['model'],system=call['system'],prompt=call['exact_prompt'],stream=False,options=call['options'])
        request=urllib.request.Request(self.endpoint+'/api/generate',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(request,timeout=600) as response:data=json.load(response)
            if not data.get('done') or type(data.get('response')) is not str:raise ValueError('incomplete response')
            return dict(raw_output=data['response'],transport_error=None,response_metadata={k:data[k] for k in
                ('model','created_at','done','total_duration','load_duration','prompt_eval_count','prompt_eval_duration','eval_count','eval_duration') if k in data})
        except Exception as exc:
            return dict(raw_output=None,transport_error=type(exc).__name__,response_metadata={})


class Replay:
    def __init__(self,path):self.rows=[json.loads(x) for x in path.read_text().splitlines()];self.requests=0
    def generate(self,call):
        prior=self.rows[self.requests];self.requests+=1
        for key in call:
            if key not in ('raw_output','parsed','parse_error','transport_error','response_metadata'):assert call[key]==prior[key],key
        return {k:prior[k] for k in ('raw_output','transport_error','response_metadata')}
