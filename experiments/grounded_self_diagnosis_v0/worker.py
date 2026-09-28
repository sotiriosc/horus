"""Three signed retrospective model calls; no world or action execution."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json,time,urllib.request
from horus.live import SessionStore,ModelClient,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import canonical,file_hash
from experiments.modern_memory_vs_horus_v0_1.transport import generate,RULE_HASH
from .protocol import (MODEL,MODEL_DIGEST,ORDER,SEEDS,OPTIONS,SYSTEM,
    build_inputs,parse_response)

INPUTS_PATH=Path('research/grounded-self-diagnosis-v0/inputs.json')

def verify_model():
    models=json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=10))['models']
    if sum(m['name']==MODEL and m['digest']==MODEL_DIGEST for m in models)!=1:
        raise RuntimeError('frozen model identity changed')

def run_one(root,run):
    if run not in ORDER:raise ValueError('unregistered control')
    verify_model()
    expected=build_inputs()
    if json.loads(INPUTS_PATH.read_text())!=expected:
        raise RuntimeError('committed blind inputs mismatch')
    root.mkdir(parents=True,exist_ok=True)
    with SessionStore(root/'session',run!='C') as store:
        prior=[x['record'] for x in store.records['training'] if x['kind']=='SELF_DIAGNOSIS']
        if [x['run'] for x in prior]!=list(ORDER[:ORDER.index(run)]):
            raise RuntimeError('retrospective call order violation')
        if run!='C':
            frozen=json.loads((root/'C-frozen.json').read_text())
            if (frozen['run']!='C' or frozen['raw_output_sha256']!=prior[0]['raw_output_sha256']
                or frozen['parsed']!=prior[0]['parsed']):
                raise RuntimeError('C proposal not frozen before controls')
        payload=expected[run]
        request=dict(model=MODEL,system=SYSTEM,prompt=canonical(payload),stream=False,
            options={**OPTIONS,'seed':SEEDS[run]})
        call_id=f'SELF_DIAGNOSIS:{run}:1'
        store.append('calls','REQUEST_INTENT',dict(call_id=call_id,role='SELF_DIAGNOSIS',
            request_sha256=digest(request),transport_rule_sha256=RULE_HASH))
        store.save(state=store.checkpoint['current_state'],
            next_transaction_id=store.checkpoint['next_transaction_id'])
        started=time.perf_counter()
        response=generate(ModelClient(),request,store,call_id)
        elapsed=time.perf_counter()-started
        raw=response.get('raw_output') or ''
        parsed,status=(None,'INVALID_RESPONSE_FORMAT') if response.get('transport_error') else parse_response(raw)
        record=dict(run=run,call_id=call_id,role='SELF_DIAGNOSIS',status=status,
            parsed=parsed,raw_output_sha256=digest(raw),request_sha256=digest(request),
            input_sha256=sha256(canonical(payload).encode()).hexdigest(),
            transport_error=response.get('transport_error'),
            context_tokens=response.get('response_metadata',{}).get('prompt_eval_count',0),
            output_tokens=response.get('response_metadata',{}).get('eval_count',0),
            latency_seconds=elapsed,non_authoritative=True)
        store.append('calls','PARSED',dict(call_id=call_id,role='SELF_DIAGNOSIS',
            status=status,parsed=parsed,raw_output_sha256=record['raw_output_sha256']))
        store.append('training','SELF_DIAGNOSIS',record)
        store.save(state=store.checkpoint['current_state'],
            next_transaction_id=store.checkpoint['next_transaction_id'])
        if store.records['events'] or store.checkpoint['completed_steps']:
            raise RuntimeError('forbidden world execution')
        if run=='C':_atomic_write(root/'C-frozen.json',record)
        if run=='B':_atomic_write(root/'complete.json',dict(status='COMPLETE',
            order=list(ORDER),calls=3,world_executions=0))
        return {k:record[k] for k in ('run','status','parsed','raw_output_sha256',
            'context_tokens','output_tokens','latency_seconds')}

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('run',choices=ORDER)
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();print(json.dumps(run_one(a.private_root,a.run),indent=2,sort_keys=True))
