"""Stateless local model transport, no framework reference."""
import json
import urllib.request
from .adapter import MODEL, SYSTEM, OPTIONS

class LocalModel:
    endpoint = "http://127.0.0.1:11434"

    def generate(self,prompt,seed):
        request=urllib.request.Request(self.endpoint+"/api/generate",data=json.dumps(dict(
            model=MODEL,system=SYSTEM,prompt=prompt,stream=False,options={**OPTIONS,"seed":seed})).encode(),
            headers={"Content-Type":"application/json"})
        with urllib.request.urlopen(request,timeout=600) as response:
            data=json.load(response)
        if not data.get("done") or not isinstance(data.get("response"),str):
            raise RuntimeError("incomplete response; no retry")
        return data["response"],{k:data[k] for k in ("model","created_at","done","total_duration",
            "load_duration","prompt_eval_count","prompt_eval_duration","eval_count","eval_duration") if k in data}

