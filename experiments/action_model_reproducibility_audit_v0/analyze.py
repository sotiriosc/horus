"""Audit exact-byte inference calls without interpreting action value or executing a world."""
from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from pathlib import Path
from statistics import median
import json
from horus.core import digest
from experiments.grounded_autonomous_agent_v0_2.worker import parse_action
from .worker import FIXTURES,WARM_COUNT,FRESH_COUNT,SERVER_COUNT,write_json

EXPECTED={'warm':WARM_COUNT,'fresh_runner':FRESH_COUNT,'fresh_server':SERVER_COUNT}
def sha(x):return sha256(x).hexdigest()
def distribution(values):
    values=[v for v in values if isinstance(v,(int,float))]
    return None if not values else dict(count=len(values),minimum=min(values),median=median(values),maximum=max(values))
def audit_call(root,fixture,condition,index):
    path=root/'calls'/condition/fixture/f'{index:03d}'
    row=json.loads((path/'result.private.json').read_text())
    intent=json.loads((path/'intent.private.json').read_text())
    body=(root/'fixtures'/(fixture+'.request.private.json')).read_bytes()
    spec=FIXTURES[fixture]
    if (row['fixture']!=fixture or row['condition']!=condition or row['index']!=index or
        row['wire_request_sha256']!=sha(body) or row['canonical_request_sha256']!=digest(json.loads(body)) or
        intent['wire_request_sha256']!=sha(body) or sha(body)!=spec['wire']):
        raise RuntimeError('request provenance mismatch')
    response_file=path/'response.private.json'
    if response_file.exists():
        response=response_file.read_bytes();value=json.loads(response)
        raw=value.get('response')
        if row['response_sha256']!=sha(response):raise RuntimeError('response hash mismatch')
        if isinstance(raw,str):
            if row['raw_output_sha256']!=sha(raw.encode()) or row['raw_output_canonical_sha256']!=digest(raw):
                raise RuntimeError('raw output hash mismatch')
            try:action=parse_action(raw)['selected_action']
            except (ValueError,TypeError,KeyError):action='INVALID'
            if action!=row['selected_action']:raise RuntimeError('action parser replay mismatch')
    elif row['response_sha256'] is not None or row['transport_error'] is None:
        raise RuntimeError('missing response provenance')
    return row

def audit(root):
    fixtures=json.loads((root/'fixtures.private.json').read_text())
    if set(fixtures)!=set(FIXTURES):raise RuntimeError('fixture set mismatch')
    for fixture,spec in FIXTURES.items():
        body=(root/'fixtures'/(fixture+'.request.private.json')).read_bytes()
        if sha(body)!=spec['wire'] or digest(json.loads(body))!=spec['canonical'] or len(body)!=spec['bytes']:
            raise RuntimeError('fixture hash mismatch')
    statuses={}
    for name in ('fresh-runner','fresh-server'):
        p=root/(name+'-status.private.json')
        statuses[name]=json.loads(p.read_text()) if p.exists() else dict(status='NOT_RUN',completed=0,reason='condition not attempted')
    runs={};all_rows=[]
    for condition,maximum in EXPECTED.items():
        runs[condition]={}
        for fixture in FIXTURES:
            directory=root/'calls'/condition/fixture
            observed=sorted(int(p.name) for p in directory.iterdir() if p.is_dir()) if directory.exists() else []
            if observed!=list(range(1,len(observed)+1)) or len(observed)>maximum:
                raise RuntimeError('call count/index outside frozen schedule')
            rows=[audit_call(root,fixture,condition,i) for i in observed]
            all_rows.extend(rows)
            actions=Counter(r['selected_action'] for r in rows)
            raws=Counter(r['raw_output_sha256'] or 'NO_RAW_OUTPUT' for r in rows)
            runners=[]
            for r in rows:
                observed_pids={int(pid) for pid,name in r['processes_sampled'].items() if name!='ollama'}
                runners.append(observed_pids)
            common=set.intersection(*runners) if runners else set()
            loaded=[r['response_metadata'].get('load_duration') for r in rows]
            stable_runner=bool(common) and all(r['server_pid']==rows[0]['server_pid'] for r in rows)
            runs[condition][fixture]=dict(call_count=len(rows),registered_count=maximum,
                request_wire_sha256=FIXTURES[fixture]['wire'],
                unique_raw_outputs=len([k for k in raws if k!='NO_RAW_OUTPUT']),
                unique_selected_actions=len([k for k in actions if k!='INVALID']),
                action_frequencies=dict(sorted(actions.items())),raw_output_hash_frequencies=dict(sorted(raws.items())),
                response_hash_frequencies=dict(sorted(Counter(r['response_sha256'] or 'NO_RESPONSE' for r in rows).items())),
                transport_failures=sum(r['transport_error'] is not None for r in rows),
                invalid_action_outputs=actions.get('INVALID',0),
                latency_seconds=distribution([r['elapsed_seconds'] for r in rows]),
                load_duration_ns=distribution(loaded),
                prompt_eval_duration_ns=distribution([r['response_metadata'].get('prompt_eval_duration') for r in rows]),
                eval_duration_ns=distribution([r['response_metadata'].get('eval_duration') for r in rows]),
                common_observed_runner_pids=sorted(common),stable_runner_observed=stable_runner,
                after_first_load_durations_ns=loaded[1:])
    warm_complete=all(runs['warm'][f]['call_count']==WARM_COUNT for f in FIXTURES)
    if not warm_complete:classification='INVALID';reason='warm registered schedule incomplete'
    elif any(r['transport_error'] is not None for r in all_rows):
        classification='INVALID';reason='transport failure in registered series'
    else:
        warm_varies=any(runs['warm'][f]['unique_raw_outputs']>1 or runs['warm'][f]['unique_selected_actions']>1 for f in FIXTURES)
        warm_stable=all(runs['warm'][f]['stable_runner_observed'] for f in FIXTURES)
        fresh_varies=any(runs[c][f]['unique_raw_outputs']>1 or runs[c][f]['unique_selected_actions']>1 for c in ('fresh_runner','fresh_server') for f in FIXTURES)
        if warm_varies and warm_stable:
            classification='ACTION_MODEL_STOCHASTIC_AS_CONFIGURED';reason='same-byte output variation within observed common warm runner under nonzero-temperature sampling'
        elif warm_varies and not warm_stable:
            classification='REQUEST_STATE_NOT_FULLY_FROZEN';reason='warm variation observed without common runner identity across all calls'
        elif fresh_varies:
            classification='REQUEST_STATE_NOT_FULLY_FROZEN';reason='output variation appears only across runner/server conditions'
        else:
            classification='ACTION_MODEL_REPRODUCIBLE';reason='no output/action variation observed in completed comparable conditions; historical C5 remains unexplained'
    result=dict(study='ACTION_MODEL_REPRODUCIBILITY_AUDIT_V0',classification=classification,
        classification_reason=reason,pre_inference_configuration='EXPLICITLY_STOCHASTIC',
        conditions=statuses,runs=runs,total_test_calls=len(all_rows),
        warm_schedule_complete=warm_complete,world_executions=0,memory_writes=0,
        action_value_judged=False,promotion_changed=False)
    write_json(root/'analysis.private.json',result)
    return result

def main():
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    x=audit(p.parse_args().private_root)
    print(json.dumps({k:x[k] for k in ('classification','classification_reason','total_test_calls','conditions')},sort_keys=True,indent=2))
if __name__=='__main__':main()
