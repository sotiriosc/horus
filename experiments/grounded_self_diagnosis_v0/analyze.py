"""Read-only signed-call audit; never converts a transport failure into diagnosis evidence."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import canonical,file_hash
from .protocol import MODEL,ORDER,SEEDS,OPTIONS,SYSTEM,build_inputs


def analyze(root):
    inputs=build_inputs()
    with SessionStore(root/'session',True) as store:
        rows=[x['record'] for x in store.records['training'] if x['kind']=='SELF_DIAGNOSIS']
        requests=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        parsed=[x['record'] for x in store.records['calls'] if x['kind']=='PARSED']
        attempts=[x['record'] for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_INTENT']
        results=[x['record'] for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_RESULT']
        if [x['run'] for x in rows]!=list(ORDER) or len(requests)!=3 or len(parsed)!=3:
            raise RuntimeError('INVALID: call order or count')
        if store.records['events'] or store.checkpoint['completed_steps']:
            raise RuntimeError('INVALID: world execution')
        if len(attempts)!=len(results) or not 3<=len(attempts)<=6:
            raise RuntimeError('INVALID: transport accounting')
        output=[]
        for run,row,intent,parse in zip(ORDER,rows,requests,parsed):
            request=dict(model=MODEL,system=SYSTEM,prompt=canonical(inputs[run]),stream=False,
                options={**OPTIONS,'seed':SEEDS[run]})
            if row['input_sha256']!=sha256(canonical(inputs[run]).encode()).hexdigest():
                raise RuntimeError('INVALID: blind input mismatch')
            if row['request_sha256']!=digest(request) or intent['request_sha256']!=digest(request):
                raise RuntimeError('INVALID: request mismatch')
            if parse['status']!=row['status'] or parse['parsed']!=row['parsed']:
                raise RuntimeError('INVALID: signed parse mismatch')
            xs=[a for a in attempts if a['call_id']==row['call_id']]
            ys=[a for a in results if a['call_id']==row['call_id']]
            if len(xs)!=len(ys) or not 1<=len(xs)<=2:
                raise RuntimeError('INVALID: per-call transport count')
            if any(json.loads(a['request_bytes_utf8'])!=request for a in xs):
                raise RuntimeError('INVALID: transport request changed')
            output.append(dict(run=run,status=row['status'],parsed=row['parsed'],
                proposal_status=('NON_AUTHORITATIVE_SELF_PROPOSAL' if row['parsed'] and
                    row['parsed']['PROPOSED_CHANGE'].upper()!='NO_CHANGE' else
                    'NO_CHANGE_PROPOSED' if row['parsed'] else None),
                raw_output_sha256=row['raw_output_sha256'],request_sha256=row['request_sha256'],
                input_sha256=row['input_sha256'],transport_error=row['transport_error'],
                transport_attempts=len(xs),transport_outcomes=[y['outcome'] for y in ys],
                context_tokens=row['context_tokens'],output_tokens=row['output_tokens'],
                latency_seconds=row['latency_seconds']))
        frozen=json.loads((root/'C-frozen.json').read_text())
        if any(rows[0].get(k)!=v for k,v in frozen.items()):
            raise RuntimeError('INVALID: C not frozen before controls')
        result=dict(study_status='INVALID' if any(x['status']!='VALID_RESPONSE' for x in output)
            else 'PENDING_BLIND_EVALUATION',world_executions=0,primary_calls=3,
            physical_transport_attempts=len(attempts),C_frozen_before_controls=True,
            source_is_sanitized_public_result=True,model_responses=output,
            private_files_sha256={str(p.relative_to(root)):file_hash(p) for p in root.rglob('*')
                if p.is_file() and p.name!='.lock'})
        _atomic_write(root/'analysis.json',result)
        return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    x=analyze(p.parse_args().private_root)
    print(json.dumps({k:v for k,v in x.items() if k!='private_files_sha256'},indent=2,sort_keys=True))
