"""Exactly one 96-call Map campaign, or zero-inference exact replay."""
import argparse,json,hashlib
from pathlib import Path
from unittest.mock import patch
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_map_proposal_v0.adapter import parse
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,atomic_write,append_line,require_durable,fsync_dir,file_digest,inspect
from .contexts import ROOT,PACKAGE,CAMPAIGN,Context,schedule,frozen
from .analysis import summarize
FILES=('contexts.jsonl','requests.jsonl','metadata.json','model-calls.jsonl','metrics.json','journal.jsonl','campaign-state.json')
def perform(c,journal,client,stream,prior=None):
    d=c.d;i=d['index'];assert 0<=i<96
    cid=f'{CAMPAIGN}:{d["family"]}:j{d["schedule"]:02d}:{d["arm"]}:Map'
    assert cid not in journal.calls;journal.calls[cid]='INTENT'
    body=c.request();audit=c.audit();registered=json.loads((PACKAGE/'schedule.json').read_text())[i]
    assert {k:registered[k] for k in d}==d
    assert hashlib.sha256(json.dumps(body).encode()).hexdigest()==registered['request_sha256']
    intent=dict(descriptor=d,audit=audit,system_snapshot=journal.snapshot(c.original_snapshot),request_payload=c.view,request=body,exact_request_json=json.dumps(body))
    journal.append('REQUEST_INTENT_RECORDED',intent,cid)
    if prior is None:
        assert client.requests==i
        response=client.generate(dict(model=body['model'],system=body['system'],exact_prompt=body['prompt'],options=body['options']))
    else:
        assert prior['call_id']==cid and prior['intent']==intent;response=prior['response']
    journal.append('RESPONSE_RECEIVED',response,cid)
    if response['transport_error']:raise RuntimeError('transport failed/ambiguous; no reissue')
    try:parsed=parse(response['raw_output']);error=None
    except (ValueError,TypeError) as exc:parsed=None;error=str(exc)
    journal.append('PARSED',dict(prediction=parsed,error=error),cid)
    outcome=c.finish(response['raw_output'],parsed,lambda p:journal.append('PREDICTION_LATCHED',p,cid))
    journal.append('EVENT_SCORED',outcome,cid)
    setup_counts=dict(mismatches=sum(not e['after']['protected']['memory'][-1]['measurement_matches'] for e in c.rows),
        state_recovery=sum(o['kind']=='recovery_state_proposal' for e in c.rows for o in e['observed_recovery']),
        measurement_recovery=sum(o['kind']=='recovery_measurement' for e in c.rows for o in e['observed_recovery']))
    row=dict(index=i,call_id=cid,descriptor=d,intent=intent,response=response,parse_error=error,outcome=outcome,setup_counts=setup_counts)
    append_line(stream,row);journal.append('REQUEST_FINALIZED',dict(index=i),cid)
    atomic_write(journal.directory/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='REQUEST_FINALIZED',completed_calls=i+1,
        journal_records=journal.sequence,journal_head_sha256=journal.previous,automatic_reissue_allowed=False))
    return row

def campaign(output,client,meta,prior=None):
    journal=Journal(output,campaign=CAMPAIGN);rows=[]
    try:
        atomic_write(output/'metadata.json',meta)
        with (output/'contexts.jsonl').open('x') as contexts,(output/'requests.jsonl').open('x') as requests,(output/'model-calls.jsonl').open('x') as calls:
            for d in schedule():
                frozen();c=Context(d);append_line(contexts,c.evidence());append_line(requests,dict(descriptor=d,request=c.request()))
                rows.append(perform(c,journal,client,calls,None if prior is None else prior[d['index']]))
                print(f'completed_calls={len(rows)} family={d["family"]} j={d["schedule"]} arm={d["arm"]}',flush=True)
        assert len(rows)==96 and (prior is not None or client.requests==96)
        result=summarize(rows);atomic_write(output/'metrics.json',result)
        state=json.loads((output/'campaign-state.json').read_text());state['status']='ALL_96_CALLS_COMPLETED';atomic_write(output/'campaign-state.json',state)
        check=inspect(output);assert check['journal_valid'] and not check['ambiguous_calls'] and check['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(status='STOP_NO_REISSUE',completed_calls=len(rows),reason=str(exc),inspection=inspect(output)));raise
    finally:journal.close()
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--model-bytes',type=Path);p.add_argument('--preflight',type=Path);a=p.parse_args();frozen()
    output=require_durable(a.output,ROOT)
    if output.exists():raise RuntimeError('existing evidence directory; no automatic rerun')
    if a.live:
        reservation=Path.home()/'horus_map_temporal_relation_forecast_v0_review'/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as stream:append_line(stream,dict(campaign_id=CAMPAIGN,output=output.name))
        fsync_dir(reservation.parent)
        pre=json.loads(a.preflight.read_text());assert pre['passed'] and pre['actual_model_calls']==0
        assert pre['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        model=json.loads(a.model_bytes.read_text());assert model['complete_blobs_verified']
        client=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=metadata(client,old,model);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,stateless=True,model_call_budget=96,role='Map');result=campaign(output,client,meta)
    else:
        prior=[json.loads(x) for x in (a.replay/'model-calls.jsonl').read_text().splitlines()];assert len(prior)==96
        meta=json.loads((a.replay/'metadata.json').read_text());assert meta['campaign_id']==CAMPAIGN
        with patch('socket.socket',side_effect=AssertionError('no network during replay')):result=campaign(output,None,meta,prior)
        for name in FILES:assert (output/name).read_bytes()==(a.replay/name).read_bytes(),name
        snapshots=list((a.replay/'memory-snapshots').glob('*.json'));assert len(snapshots)==96
        for path in snapshots:assert path.read_bytes()==(output/'memory-snapshots'/path.name).read_bytes()
        print('PASS: seven files and 96 snapshots byte-identical; ZERO INFERENCE.')
    print(result['classification'])
if __name__=='__main__':main()
