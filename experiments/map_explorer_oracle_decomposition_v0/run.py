"""One bounded live decomposition, or exact zero-inference replay."""
import argparse,json
from pathlib import Path
from unittest.mock import patch
from experiments.model_proposal_role_composition_v2.transport import LocalModel
from experiments.model_recovery_proposal_v1.transport import metadata
from experiments.model_map_proposal_v0.adapter import parse
from experiments.model_explorer_semantic_prior_study_v0.adapter import parse_surface
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,atomic_write,append_line,require_durable,fsync_dir,file_digest,inspect
from .contexts import ROOT,PACKAGE,CAMPAIGN,ACTIONS,Context,ProposalFailure,schedule,slots,body,permute,request_hash,frozen
from .analysis import classify,summarize
FILES=('metadata.json','contexts.jsonl','model-calls.jsonl','decisions.jsonl','metrics.json','journal.jsonl','campaign-state.json')
GUARD='experiments.base_framework_v1.hidden_oracle.TrueWorldOracle.execute'
class Recorder:
    def __init__(self,journal,client,stream,prior=None):self.j=journal;self.client=client;self.stream=stream;self.prior=prior;self.calls=[]
    def call(self,c,slot,request):
        i=len(self.calls);d=c.d;cid=f'{CAMPAIGN}:c{d["index"]:02d}:{slot}'
        assert i<288 and cid not in self.j.calls;self.j.calls[cid]='INTENT';c.audit()
        registered=json.loads((PACKAGE/'schedule.json').read_text())[d['index']]
        entry=next(x for x in registered['potential_calls'] if x['slot']==slot)
        h=request_hash(request)
        if slot!='ModelMap':assert h==entry['request_sha256']
        else:assert entry['request_sha256'] is None and entry['conditional']=='UNIQUE_VALID_MODEL_MAXIMUM'
        intent=dict(descriptor=d,slot=slot,request=request,exact_request_json=json.dumps(request),request_sha256=h,
            snapshot=self.j.snapshot(c.original_snapshot))
        self.j.append('REQUEST_INTENT_RECORDED',intent,cid)
        if self.prior is None:
            assert self.client.requests==i
            response=self.client.generate(dict(model=request['model'],system=request['system'],exact_prompt=request['prompt'],options=request['options']))
        else:
            old=self.prior[i];assert old['call_id']==cid and old['intent']==intent;response=old['response']
        self.j.append('RESPONSE_RECEIVED',response,cid)
        if response['transport_error']:raise RuntimeError('failed or ambiguous transport; STOP, no reissue')
        if slot.startswith('Map:'):
            try:value=parse(response['raw_output']);error=None
            except (ValueError,TypeError) as exc:value=None;error=str(exc)
        else:
            _,value,error=parse_surface(response['raw_output'],dict(surface_option_order=list(d['mapping']),surface_to_underlying=d['mapping']))
        self.j.append('PARSED',dict(parsed=value,error=error),cid)
        c.audit();row=dict(index=i,call_id=cid,context_index=d['index'],slot=slot,request=request,intent=intent,response=response,parsed=value,parse_error=error,parsed_recorded=True)
        append_line(self.stream,row);self.calls.append(row)
        atomic_write(self.j.directory/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='PARSED',completed_calls=len(self.calls),journal_head_sha256=self.j.previous,journal_records=self.j.sequence,automatic_reissue_allowed=False))
        print(f'calls={len(self.calls)} context={d["index"]} {d["world"]}/{d["family"]}/m{d["mapping_index"]} slot={slot}',flush=True)
        return row

def decision(c,rec):
    d=c.d;choices={};map_calls=[]
    with patch(GUARD,side_effect=AssertionError('world evaluation forbidden during Map stage')):
        for action in ACTIONS:map_calls.append(rec.call(c,'Map:'+action,c.map_requests[action]))
        collected=c.collect(map_calls)
    rec.j.append('MAP_COLLECTION_BOUND',dict(context_index=d['index'],collection=collected))
    oracle=c.oracle(map_calls)
    rec.j.append('ORACLE_EVALUATED_AFTER_MAP',dict(context_index=d['index'],oracle=oracle))
    views={'Oracle':c.forecast_view(oracle['values'])};views['Permutation']=permute(views['Oracle'])
    with patch(GUARD,side_effect=AssertionError('world evaluation forbidden during Explorer stage')):
        for slot in slots(d)[3:5]:choices[slot]=rec.call(c,slot,body(d,slot,views[slot]))['parsed']
        preliminary=classify(d,map_calls,oracle,choices)
        if preliminary['eligible']:
            assert collected['view'] is not None;views['ModelMap']=collected['view']
            def source(system,prompt):
                req=body(d,'ModelMap',views['ModelMap']);assert req['system']==system and req['prompt']==prompt
                row=rec.call(c,'ModelMap',req);choices['ModelMap']=row['parsed'];return row['response']['raw_output']
            try:
                proposal=c.session.choose(source);assert c.session.validate(proposal)
                assert proposal.underlying_action==choices['ModelMap']
            except ProposalFailure as exc:
                assert str(exc)=='INVALID_EXPLORER' and choices['ModelMap'] is None
        else:
            if preliminary['ranking']=='TIED_MAXIMUM':
                def forbidden(*args):raise AssertionError('tie slot must remain unissued')
                try:c.session.choose(forbidden)
                except ProposalFailure as exc:assert str(exc)=='TIED_MAXIMUM'
                else:raise AssertionError('tie admitted')
            else:assert collected['failure']=='INVALID_MAP'
            rec.j.append('SLOT_INTENTIONALLY_UNISSUED',dict(context_index=d['index'],slot='ModelMap',reason=preliminary['ranking']))
    result=classify(d,map_calls,oracle,choices);assert result['eligible']==('ModelMap' in choices)
    return dict(result=result,oracle=oracle,views=views,interface_binding=c.session.evidence(),
        interface_counter_scope='Legacy synthetic_* field names count recorded-response binding invocations, not additional inference.',
        map_collection=collected,oracle_after_all_Map_parses=True,audit_after=c.audit(),protected_unchanged=True)

def campaign(output,client,meta,prior=None):
    j=Journal(output,campaign=CAMPAIGN);contexts=[]
    try:
        atomic_write(output/'metadata.json',meta)
        with (output/'contexts.jsonl').open('x') as cs,(output/'model-calls.jsonl').open('x') as ms,(output/'decisions.jsonl').open('x') as ds:
            rec=Recorder(j,client,ms,prior)
            for d in schedule():
                frozen();c=Context(d);append_line(cs,c.evidence());row=decision(c,rec);append_line(ds,row);contexts.append(row)
                j.append('CONTEXT_FINALIZED',dict(context_index=d['index'],result=row['result'],protected_unchanged=True))
                atomic_write(output/'campaign-state.json',dict(campaign_id=CAMPAIGN,status='CONTEXT_FINALIZED',completed_contexts=len(contexts),completed_calls=len(rec.calls),journal_head_sha256=j.previous,journal_records=j.sequence,automatic_reissue_allowed=False))
        r=summarize(contexts,rec.calls);assert r['Map_calls']==144 and r['mandatory_calls']==240 and r['Oracle_Explorer_calls']==r['Permutation_Explorer_calls']==48
        assert len(rec.calls)==240+r['conditional_eligible_contexts']<=288
        if prior is None:assert client.requests==len(rec.calls)
        else:assert len(prior)==len(rec.calls)
        atomic_write(output/'metrics.json',r)
        s=json.loads((output/'campaign-state.json').read_text());s['status']='ALL_REGISTERED_SLOTS_RESOLVED';atomic_write(output/'campaign-state.json',s)
        check=inspect(output);assert check['journal_valid'] and not check['ambiguous_calls'] and check['campaign_state_matches_journal']
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(status='STOP_NO_REISSUE',completed_contexts=len(contexts),reason=str(exc),inspection=inspect(output)));raise
    finally:j.close()
    return r

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--model-bytes',type=Path);p.add_argument('--preflight',type=Path);a=p.parse_args();frozen();output=require_durable(a.output,ROOT)
    if output.exists():raise RuntimeError('existing archive; no automatic rerun')
    if a.live:
        reservation=Path.home()/'horus_map_explorer_oracle_decomposition_v0_review'/'LIVE_CAMPAIGN_RESERVED.json'
        with reservation.open('x') as f:append_line(f,dict(campaign_id=CAMPAIGN,output=output.name))
        fsync_dir(reservation.parent)
        pre=json.loads(a.preflight.read_text());assert pre['passed'] and pre['actual_model_calls']==0 and pre['frozen_inputs_sha256']==file_digest(PACKAGE/'frozen-inputs.json')
        model=json.loads(a.model_bytes.read_text());assert model['complete_blobs_verified']
        client=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=metadata(client,old,model);meta.pop('system',None);meta.pop('options',None)
        meta.update(campaign_id=CAMPAIGN,stateless=True,mandatory_calls=240,maximum_calls=288);r=campaign(output,client,meta)
    else:
        prior=[json.loads(x) for x in (a.replay/'model-calls.jsonl').read_text().splitlines()];assert 240<=len(prior)<=288
        meta=json.loads((a.replay/'metadata.json').read_text());assert meta['campaign_id']==CAMPAIGN
        with patch('socket.socket',side_effect=AssertionError('no inference/network in replay')):r=campaign(output,None,meta,prior)
        for n in FILES:assert (output/n).read_bytes()==(a.replay/n).read_bytes(),n
        snaps=list((a.replay/'memory-snapshots').glob('*.json'));assert len(snaps)==48
        for q in snaps:assert q.read_bytes()==(output/'memory-snapshots'/q.name).read_bytes()
        print('PASS seven deterministic files and 48 snapshots byte-identical; ZERO INFERENCE; identical unissued slots.')
    print(r['classification'])
if __name__=='__main__':main()
