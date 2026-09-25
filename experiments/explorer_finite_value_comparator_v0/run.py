"""One 144-call Explorer-only detached comparator study or exact replay."""
import argparse,json
from pathlib import Path
from unittest.mock import patch
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,atomic_write,append_line,require_durable,fsync_dir,file_digest,inspect
from .protocol import ROOT,PACKAGE,CAMPAIGN,schedule,request,request_hash,build,score,frozen,detached_only
from .analysis import summarize
FILES=('contexts.jsonl','requests.jsonl','metadata.json','model-calls.jsonl','pairs.json','metrics.json','journal.jsonl','campaign-state.json','isolation.json')
def campaign(output,client,meta,prior=None):
    j=Journal(output,campaign=CAMPAIGN);rows=[]
    try:
        atomic_write(output/'metadata.json',meta)
        with detached_only() as guards,(output/'contexts.jsonl').open('x') as contexts,(output/'requests.jsonl').open('x') as requests,(output/'model-calls.jsonl').open('x') as calls:
            registered=json.loads((PACKAGE/'schedule.json').read_text())
            for d in schedule():
                frozen();i=d['index'];assert 0<=i<144;view,target=build(d);body=request(d)
                assert {k:registered[i][k] for k in d}==d and request_hash(body)==registered[i]['request_sha256']
                append_line(contexts,dict(descriptor=d,view=view,target=target,detached=True,history=None))
                append_line(requests,dict(descriptor=d,request=body))
                cid=f'{CAMPAIGN}:{d["family"]}:{d["relation"]}:j{d["schedule"]:02d}:{d["condition"]}:Explorer'
                assert cid not in j.calls;j.calls[cid]='INTENT'
                intent=dict(descriptor=d,request=body,exact_request_json=json.dumps(body),request_sha256=request_hash(body),view=view,detached=True)
                j.append('REQUEST_INTENT_RECORDED',intent,cid)
                if prior is None:
                    assert client.requests==i
                    response=client.generate(dict(model=body['model'],system=body['system'],exact_prompt=body['prompt'],options=body['options']))
                else:
                    old=prior[i];assert old['call_id']==cid and old['intent']==intent;response=old['response']
                j.append('RESPONSE_RECEIVED',response,cid)
                if response['transport_error']:raise RuntimeError('failed/ambiguous transport; no automatic reissue')
                scoring=score(response['raw_output'],d);j.append('PARSED',scoring,cid)
                row=dict(index=i,call_id=cid,descriptor=d,intent=intent,response=response,scoring=scoring)
                append_line(calls,row);rows.append(row);j.append('REQUEST_FINALIZED',dict(index=i),cid)
                atomic_write(output/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='REQUEST_FINALIZED',completed_calls=len(rows),journal_records=j.sequence,journal_head_sha256=j.previous,automatic_reissue_allowed=False))
                print(f'calls={len(rows)} {d["relation"]}/{d["family"]}/j{d["schedule"]}/{d["condition"]}',flush=True)
            assert len(rows)==144 and (prior is not None or client.requests==144)
            isolation=dict(passed=True,world_executions=0,Memory_changes=0,Map_model_calls=0,prohibited_attempts={n:m.call_count for n,m in guards.items()})
        result=summarize(rows);atomic_write(output/'metrics.json',result);atomic_write(output/'pairs.json',result['pairs']);atomic_write(output/'isolation.json',isolation)
        state=json.loads((output/'campaign-state.json').read_text());state['status']='ALL_144_CALLS_COMPLETED';atomic_write(output/'campaign-state.json',state)
        check=inspect(output);assert check['journal_valid'] and not check['ambiguous_calls'] and check['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(status='STOP_NO_REISSUE',completed_calls=len(rows),reason=str(exc),inspection=inspect(output)));raise
    finally:j.close()
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--model-bytes',type=Path);p.add_argument('--preflight',type=Path);a=p.parse_args();frozen();output=require_durable(a.output,ROOT)
    if output.exists():raise RuntimeError('existing archive; no automatic rerun')
    if a.live:
        reservation=Path.home()/'horus_explorer_finite_value_comparator_v0_review'/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as stream:append_line(stream,dict(campaign_id=CAMPAIGN,output=output.name))
        fsync_dir(reservation.parent)
        pre=json.loads(a.preflight.read_text());assert pre['passed'] and pre['actual_model_calls']==0 and pre['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        proof=json.loads(a.model_bytes.read_text());assert proof['complete_blobs_verified']
        client=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=metadata(client,old,proof);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,stateless=True,model_call_budget=144,role='Explorer');r=campaign(output,client,meta)
    else:
        prior=[json.loads(x) for x in (a.replay/'model-calls.jsonl').read_text().splitlines()];assert len(prior)==144
        meta=json.loads((a.replay/'metadata.json').read_text());assert meta['campaign_id']==CAMPAIGN
        with patch('socket.socket',side_effect=AssertionError('replay forbids network')):r=campaign(output,None,meta,prior)
        for name in FILES:assert (output/name).read_bytes()==(a.replay/name).read_bytes(),name
        assert not (output/'memory-snapshots').exists()
        print('PASS nine deterministic files byte-identical; ZERO INFERENCE, WORLD EXECUTION OR MEMORY CHANGES.')
    print(r['classification']);print(r['next_state_classification'])
if __name__=='__main__':main()
