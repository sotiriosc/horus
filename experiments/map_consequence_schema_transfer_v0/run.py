"""Exactly sixteen registered Map attempts or recorded replay; never retry."""
import argparse
import json,hashlib
from pathlib import Path
from unittest.mock import patch
from .protocol import parse
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,atomic_write,append_line,require_durable,fsync_dir,file_digest,inspect
from .protocol import ROOT,PACKAGE,CAMPAIGN,schedule,frozen,summarize
from .fixture import Context,GUARD

FILES=('metadata.json','contexts.jsonl','model-calls.jsonl','steps.jsonl','metrics.json','journal.jsonl','campaign-state.json')


class Recorder:
    def __init__(self,journal,client,stream,prior=None):self.j=journal;self.client=client;self.stream=stream;self.prior=prior;self.calls=[]
    def call(self,c):
        i=len(self.calls);d=c.d;assert i==d['index'] and i<16
        cid=f'{CAMPAIGN}:c{i:02d}:Map';assert cid not in self.j.calls
        self.j.calls[cid]='INTENT';request=c.request
        registered=json.loads((PACKAGE/'schedule.json').read_text())[i]
        assert registered['descriptor']==d and registered['request_sha256']==hashlib.sha256(json.dumps(request).encode()).hexdigest()
        intent=dict(descriptor=d,request=request,exact_request_json=json.dumps(request),snapshot=self.j.snapshot(c.before))
        self.j.append('REQUEST_INTENT_RECORDED',intent,cid)
        atomic_write(self.j.directory/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='REQUEST_INTENT_RECORDED',attempted_calls=i+1,completed_calls=i,
            journal_head_sha256=self.j.previous,journal_records=self.j.sequence,automatic_reissue_allowed=False))
        with patch(GUARD,side_effect=AssertionError('scored event cannot execute during inference')):
            c.audit_before()
            if self.prior is None:
                assert self.client.requests==i
                response=self.client.generate(dict(model=request['model'],system=request['system'],exact_prompt=request['prompt'],options=request['options']))
                assert self.client.requests==i+1
            else:
                old=self.prior[i];assert old['call_id']==cid and old['intent']==intent;response=old['response']
            self.j.append('RESPONSE_RECEIVED',response,cid)
            if response['transport_error']:raise RuntimeError('failed or ambiguous transport; STOP; no reissue')
            try:parsed=parse(response['raw_output'],d['condition']);error=None
            except (ValueError,TypeError) as exc:parsed=None;error=str(exc)
            self.j.append('PARSED',dict(parsed=parsed,error=error),cid);self.j.calls[cid]='PARSED';c.audit_before()
        row=dict(index=i,call_id=cid,intent=intent,request=request,response=response,parsed=parsed,parse_error=error)
        append_line(self.stream,row);self.calls.append(row)
        return row


def campaign(output,client,meta,prior=None):
    j=Journal(output,campaign=CAMPAIGN);rows=[]
    try:
        atomic_write(output/'metadata.json',meta)
        with (output/'contexts.jsonl').open('x') as cs,(output/'model-calls.jsonl').open('x') as ms,(output/'steps.jsonl').open('x') as ss:
            rec=Recorder(j,client,ms,prior)
            for d in schedule():
                frozen();j.episode=d['index'];j.decision=0;c=Context(d)
                context=c.record();append_line(cs,context);j.append('AUTHENTIC_HISTORY_READY',context)
                call=rec.call(c);row=c.finish(call,j);append_line(ss,row);rows.append(row)
                j.append('CONTEXT_FINALIZED',dict(index=d['index'],valid=row['valid'],score=row['score']))
                atomic_write(output/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='CONTEXT_FINALIZED',attempted_calls=len(rec.calls),completed_calls=len(rec.calls),completed_contexts=len(rows),
                    journal_head_sha256=j.previous,journal_records=j.sequence,automatic_reissue_allowed=False))
                print(f"call {len(rec.calls)}/16 {d['world']} {d['family']} seed={d['seed']} {d['condition']} parsed={call['parsed']} score={row['score']}",flush=True)
        assert len(rec.calls)==16 and (client.requests==16 if prior is None else len(prior)==16)
        result=summarize(rows,len(rec.calls),integrity=True,replay=False);atomic_write(output/'metrics.json',result)
        state=json.loads((output/'campaign-state.json').read_text());state['status']='SIXTEEN_CALLS_COMPLETE_STOP';atomic_write(output/'campaign-state.json',state)
        check=inspect(output);assert check['journal_valid'] and not check['ambiguous_calls'] and check['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(status='STOP_NO_REISSUE',reason=str(exc),completed_contexts=len(rows),inspection=inspect(output)));raise
    finally:j.close()
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    mode=ap.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    ap.add_argument('--model-bytes',type=Path);ap.add_argument('--preflight',type=Path);args=ap.parse_args()
    frozen();output=require_durable(args.output,ROOT)
    if output.exists():raise RuntimeError('existing evidence directory: no automatic rerun')
    if args.live:
        reservation=output.parent/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as f:append_line(f,dict(campaign_id=CAMPAIGN,output=output.name,maximum_calls=16))
        fsync_dir(reservation.parent)
        pre=json.loads(args.preflight.read_text());assert pre['passed'] and pre['actual_model_calls']==0 and pre['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        proof=json.loads(args.model_bytes.read_text());assert proof['complete_blobs_verified']
        client=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=metadata(client,old,proof);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,stateless=True,maximum_calls=16,model_roles=['Map'],probe_only=True,model_prediction_publication=False)
        result=campaign(output,client,meta)
    else:
        prior=[json.loads(l) for l in (args.replay/'model-calls.jsonl').read_text().splitlines()];assert len(prior)==16
        meta=json.loads((args.replay/'metadata.json').read_text());assert meta['campaign_id']==CAMPAIGN
        with patch('socket.socket',side_effect=AssertionError('ZERO INFERENCE in replay')):result=campaign(output,None,meta,prior)
        for n in FILES:assert (output/n).read_bytes()==(args.replay/n).read_bytes(),n
        snapshots=sorted((args.replay/'memory-snapshots').glob('*.json'));assert len(snapshots)==16
        for p in snapshots:assert p.read_bytes()==(output/'memory-snapshots'/p.name).read_bytes()
        print('PASS seven deterministic files and sixteen snapshots byte-identical; ZERO INFERENCE.')
    print(result['classification'])


if __name__=='__main__':main()
