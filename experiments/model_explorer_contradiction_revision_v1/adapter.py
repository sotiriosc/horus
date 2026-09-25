"""String-only Explorer proposal; no evidence or authorization capability."""
import json
import urllib.request
from experiments.model_explorer_integration_v0.adapter import MODEL, OPTIONS

SYSTEM = "Choose one available action using only the verified chronological outcomes shown. Higher verified consequences are preferable. Reply with exactly one available action and no explanation."


def render(records, descriptor):
    inverse = {v:k for k,v in descriptor["mapping"].items()}
    return dict(state=1, available_actions=descriptor["options"],
        VERIFIED_CHRONOLOGICAL_HISTORY=[dict(transaction_id=r.transaction_id,
            surface_action=inverse[r.action], consequence=r.consequence)
            for r in sorted(records, key=lambda r:(r.epoch,r.transaction_id))
            if r.authorization == "AUTHORIZED" and r.pre_state == 1 and r.action in ("HOLD","ADVANCE")])


def serialize(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def parse(raw, descriptor):
    token = raw.strip() if isinstance(raw,str) else None
    return (token, descriptor["mapping"][token]) if token in descriptor["options"] else (None,None)


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


def propose(transport, records, descriptor):
    payload=render(records,descriptor);prompt=serialize(payload)
    assert prompt==descriptor["exact_prompt"]
    raw,metadata=transport.generate(prompt,descriptor["seed"])
    alias,action=parse(raw,descriptor)
    return dict(model=MODEL,system=SYSTEM,options={**OPTIONS,"seed":descriptor["seed"]},
        exact_prompt=prompt,payload=payload,raw_output=raw,response_metadata=metadata,
        parsed_alias=alias,parsed_action=action)
