"""Exactly one 48-call campaign, or exact zero-inference recorded-response replay."""
import argparse,json
from pathlib import Path
from unittest.mock import patch
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import (
    Journal,atomic_write,append_line,require_durable,fsync_dir,file_digest,inspect)
from .contexts import ROOT,PACKAGE,CAMPAIGN,Context,schedule,frozen
from .analysis import score,pair,summarize
FILES=('contexts.json','requests.json','metadata.json','model-calls.jsonl','pairs.json','metrics.json','journal.jsonl','campaign-state.json')

def perform(c,role,condition,index,journal,client,stream,prior=None):
    assert 0<=index<48
    audit=c.audit();body=c.request(role,condition)
    cid=f'{CAMPAIGN}:c{c.d["index"]:02d}:{role}:{condition}'
    if cid in journal.calls:raise RuntimeError('duplicate call ID; no reissue')
    journal.calls[cid]='INTENT'
    snapshot=journal.snapshot(dict(CARRY=c.after,FRESH=c.fresh_initial))
    intent=dict(index=index,context_index=c.d['index'],role=role,condition=condition,mapping=c.mapping,
        audit=audit,system_snapshot=snapshot,request=body,exact_request_json=json.dumps(body))
    journal.append('REQUEST_INTENT_RECORDED',intent,cid)
    if prior is None:
        assert client.requests==index
        response=client.generate(dict(model=body['model'],system=body['system'],exact_prompt=body['prompt'],options=body['options']))
    else:
        assert prior['call_id']==cid and prior['intent']==intent
        response=prior['response']
    # Preserve even an unsuccessful transport observation before stopping.
    journal.append('RESPONSE_RECEIVED',response,cid)
    if response['transport_error']:raise RuntimeError('transport failure or ambiguous request; no retry')
    scoring=score(role,response['raw_output'],c.mapping,c.receipt)
    c.audit()
    journal.append('PARSED',scoring,cid)
    row=dict(index=index,call_id=cid,context_index=c.d['index'],role=role,condition=condition,
        intent=intent,response=response,scoring=scoring)
    append_line(stream,row)
    journal.append('REQUEST_FINALIZED',dict(index=index,read_only_systems_unchanged=True),cid)
    atomic_write(journal.directory/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='REQUEST_FINALIZED',completed_calls=index+1,
        journal_head_sha256=journal.previous,journal_records=journal.sequence,automatic_reissue_allowed=False))
    return row

def campaign(output,client,meta,prior=None):
    journal=Journal(output,campaign=CAMPAIGN);rows=[];pairs=[];contexts=[];requests=[]
    try:
        atomic_write(output/'metadata.json',meta)
        with (output/'model-calls.jsonl').open('x') as stream:
            for d in schedule():
                frozen();c=Context(d);contexts.append(c.evidence())
                atomic_write(output/'contexts.json',contexts)
                for role in ('Explorer','Map'):
                    role_rows=[]
                    for condition in d['order']:
                        index=len(rows)
                        request=c.request(role,condition)
                        requests.append(dict(index=index,context_index=d['index'],role=role,condition=condition,request=request))
                        atomic_write(output/'requests.json',requests)
                        row=perform(c,role,condition,index,journal,client,stream,None if prior is None else prior[index])
                        rows.append(row);role_rows.append(row)
                        print(f'completed_calls={len(rows)} context={d["index"]:02d} role={role} condition={condition}',flush=True)
                    pairs.append(pair(d,role,role_rows))
                c.audit()
        assert len(rows)==48 and (prior is not None or client.requests==48)
        result=summarize(pairs,rows)
        atomic_write(output/'pairs.json',pairs);atomic_write(output/'metrics.json',result)
        state=json.loads((output/'campaign-state.json').read_text());state['status']='ALL_48_CALLS_COMPLETED';atomic_write(output/'campaign-state.json',state)
        audit=inspect(output);assert audit['journal_valid'] and not audit['ambiguous_calls'] and audit['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(status='STOP_NO_REISSUE',reason=str(exc),completed_calls=len(rows),inspection=inspect(output)))
        raise
    finally:journal.close()
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--model-bytes',type=Path);p.add_argument('--preflight',type=Path)
    a=p.parse_args();reg=frozen();output=require_durable(a.output,ROOT)
    if output.exists():raise RuntimeError('existing evidence directory; no automatic rerun')
    if a.live:
        # Campaign-wide reservation is fixed to the private study archive supplied at preregistration.
        reservation=Path.home()/'horus_cross_episode_model_transfer_v0_review'/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as stream:append_line(stream,dict(campaign_id=CAMPAIGN,output=output.name))
        fsync_dir(reservation.parent)
        proof=json.loads(a.preflight.read_text());assert proof['passed'] and proof['actual_model_calls']==0
        assert proof['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        model=json.loads(a.model_bytes.read_text());assert model['complete_blobs_verified']
        client=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=metadata(client,old,model);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,stateless=True,model_call_budget=48)
        result=campaign(output,client,meta)
    else:
        prior=[json.loads(line) for line in (a.replay/'model-calls.jsonl').read_text().splitlines()];assert len(prior)==48
        meta=json.loads((a.replay/'metadata.json').read_text());assert meta['campaign_id']==CAMPAIGN
        with patch('socket.socket',side_effect=AssertionError('replay must never access network')):
            result=campaign(output,None,meta,prior)
        for name in FILES:assert (output/name).read_bytes()==(a.replay/name).read_bytes(),name
        snapshots=list((a.replay/'memory-snapshots').glob('*.json'));assert len(snapshots)==12
        for path in snapshots:assert path.read_bytes()==(output/'memory-snapshots'/path.name).read_bytes(),path.name
        print('PASS: eight files and 12 snapshots byte-identical; ZERO INFERENCE.')
    print(result['threshold_decision'])
if __name__=='__main__':main()
