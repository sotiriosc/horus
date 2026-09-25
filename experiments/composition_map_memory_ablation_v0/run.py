"""Single 84-call Map-only study, or zero-inference exact recorded-response replay."""
import argparse
import json
from pathlib import Path
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal, atomic_write, append_line, require_durable, file_digest, inspect
from .contexts import ROOT, PACKAGE, CAMPAIGN, frozen, reconstruct, public_contexts, source_hashes, lines
from .analysis import score, pair, metrics, criteria

FILES=('contexts.json','requests.json','model-calls.jsonl','pairs.json','metrics.json','journal.jsonl','campaign-state.json','metadata.json')


def call_spec(c,condition):
    body=c['requests'][condition]
    return dict(model=body['model'],system=body['system'],exact_prompt=body['prompt'],options=body['options'])


def perform(c,condition,index,journal,client,stream,prior=None):
    cid=f'{CAMPAIGN}:c{c["index"]:02d}:{condition}:Map'
    intent=dict(index=index,context_index=c['index'],condition=condition,role='Map',source_call_id=c['source_call_id'],
        episode=c['episode'],decision=c['decision'],mapping=c['mapping'],state=c['state'],action=c['action'],alias=c['alias'],
        memory_snapshot=c['memory_snapshot'],seed=c['seed'],request=c['requests'][condition],
        exact_request_json=c['exact_requests'][condition],request_sha256=c['request_sha256'][condition])
    journal.episode=c['episode'];journal.decision=c['decision']
    journal.append('REQUEST_INTENT_RECORDED',intent,cid)
    if prior is None:
        assert index<84 and client.requests==index
        response=client.generate(call_spec(c,condition))
    else:
        assert prior['intent']==intent and prior['call_id']==cid
        response=prior['response']
    # A failed/ambiguous transport stops this campaign. Never issue a replacement.
    if response['transport_error']:
        journal.append('TRANSPORT_FAILURE_STOP',response,cid)
        raise RuntimeError('transport failure/possibly issued; no retry')
    journal.append('RESPONSE_RECEIVED',response,cid)
    scoring=score(response['raw_output'],c['receipt'])
    journal.append('PARSED',scoring,cid)
    row=dict(index=index,call_id=cid,context_index=c['index'],condition=condition,intent=intent,response=response,scoring=scoring)
    append_line(stream,row)
    journal.append('REQUEST_FINALIZED',dict(index=index,context_index=c['index'],condition=condition),cid)
    atomic_write(journal.directory/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='REQUEST_FINALIZED',
        completed_calls=index+1,real_call_counts=dict(Map=index+1,Explorer=0,Recovery=0),last_completed_context=c['index'],
        last_completed_condition=condition,source_memory_unchanged=True,journal_head_sha256=journal.previous,
        journal_records=journal.sequence,automatic_reissue_allowed=False))
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--model-bytes',type=Path);p.add_argument('--preflight',type=Path)
    args=p.parse_args();reg=frozen();before=source_hashes(args.source)
    assert before==reg['r1_evidence_sha256']
    cs=reconstruct(args.source);assert public_contexts(cs)==json.loads((PACKAGE/'contexts.json').read_text())
    output=require_durable(args.output,ROOT)
    if output.exists():raise RuntimeError('existing evidence directory: inspect; automatic rerun forbidden')
    if args.live:
        # Global, immutable campaign reservation, independent of output directory.
        reservation=output.parent/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as stream:append_line(stream,dict(campaign_id=CAMPAIGN,output=output.name))
        from experiments.model_proposal_role_composition_v2_replacement_r1.durable import fsync_dir
        fsync_dir(output.parent)
        proof=json.loads(args.preflight.read_text())
        assert proof['passed'] and proof['actual_model_calls']==0 and proof['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        client=LocalModel()
        old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        model_proof=json.loads(args.model_bytes.read_text())
        assert model_proof['complete_blobs_verified']
        meta=metadata(client,old,model_proof);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,role='Map',stateless=True)
        prior=None
    else:
        client=None;prior=lines(args.replay/'model-calls.jsonl');assert len(prior)==84
        meta=json.loads((args.replay/'metadata.json').read_text())
        assert meta['campaign_id']==CAMPAIGN and meta['server']['version']=='0.1.16'
    journal=Journal(output,campaign=CAMPAIGN)
    rows=[];pairs=[]
    try:
        atomic_write(output/'contexts.json',cs);atomic_write(output/'metadata.json',meta)
        requests=[dict(context_index=c['index'],condition=k,request=c['requests'][k],exact_request_json=c['exact_requests'][k]) for c in cs for k in c['order']]
        atomic_write(output/'requests.json',requests)
        with (output/'model-calls.jsonl').open('x') as stream:
            for c in cs:
                assert frozen()==reg
                cr=[]
                for condition in c['order']:
                    index=len(rows)
                    row=perform(c,condition,index,journal,client,stream,None if prior is None else prior[index])
                    rows.append(row);cr.append(row)
                pairs.append(pair(c,cr))
                print(f'context={c["index"]:02d} episode={c["episode"]} decision={c["decision"]} complete_calls={len(rows)}',flush=True)
        assert len(rows)==84 and source_hashes(args.source)==before
        result=metrics(pairs);result.update(study='composition-map-memory-ablation-v0',campaign_id=CAMPAIGN,
            real_calls=84,world_executions=0,new_receipts=0,new_memory_events=0,Explorer_calls=0,Recovery_calls=0,
            primary_criteria=criteria(result,True,True,True,False),classification='AUTHENTIC-HISTORY MAP EFFECT NOT ESTABLISHED',status='AWAITING_EXACT_REPLAY')
        atomic_write(output/'pairs.json',pairs);atomic_write(output/'metrics.json',result)
        state=json.loads((output/'campaign-state.json').read_text());state['status']='ALL_84_CALLS_COMPLETED';atomic_write(output/'campaign-state.json',state)
        audit=inspect(output);assert audit['journal_valid'] and not audit['ambiguous_calls'] and audit['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(classification='AUTHENTIC-HISTORY MAP EFFECT NOT ESTABLISHED',
            status='INTERRUPTED_DO_NOT_REISSUE',error_type=type(exc).__name__,reason=str(exc),completed_calls=len(rows),inspection=inspect(output)))
        raise
    finally:journal.close()
    if args.replay:
        for name in FILES:assert (output/name).read_bytes()==(args.replay/name).read_bytes(),name
        print('PASS: eight registered files byte-identical; ZERO INFERENCE.')
    print(json.dumps(result['conditions'],sort_keys=True))


if __name__=='__main__':main()
