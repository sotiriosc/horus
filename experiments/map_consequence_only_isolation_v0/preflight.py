"""Zero-model validation of request matching, detached probes, leakage and replay."""
from copy import deepcopy
import argparse,json
from pathlib import Path
from unittest.mock import patch
from experiments.model_map_proposal_v0.adapter import INVALID
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect,atomic_write,file_digest
from .protocol import PACKAGE,CAMPAIGN,CONTROL,SYSTEMS,schedule,frozen,summarize,body,matched,serialize,parse,A,B,C
from .fixture import Context
from .run import campaign,FILES


def fake_call(raw,d):
    try:value=parse(raw,d['condition']);error=None
    except (ValueError,TypeError) as exc:value=None;error=str(exc)
    return dict(call_id=f'preflight:{d["index"]}',parsed=value,parse_error=error,response=dict(raw_output=raw,transport_error=None,response_metadata={'synthetic_control':True}))


class Synthetic:
    def __init__(self):self.requests=0
    def generate(self,call):
        self.requests+=1;assert self.requests<=8
        value=dict(consequence=1)
        if call['system']==SYSTEMS['J']:value['next_state']=1
        else:assert call['system']==SYSTEMS['C']
        return dict(raw_output=json.dumps(value),transport_error=None,response_metadata={'synthetic_control':True})


def run(out):
    frozen();out.mkdir(exist_ok=False);canaries=[];requests={};detached=[]
    with patch('socket.socket',side_effect=AssertionError('no inference in preflight')):
        for d in schedule():
            c=Context(d);before=deepcopy(c.before);request=json.dumps(c.request);requests[d['family'],d['seed'],d['condition']]=deepcopy(c.request)
            oracle=c.c._active.world.fixture.oracle;law=list(oracle._CONSEQUENCE);law[4]=-1;oracle._CONSEQUENCE=tuple(law)
            assert c.before==before and json.dumps(body(d,c.reader.capture(d['mapping'])['map_inputs']['HOLD']))==request
            c.audit_before();value=dict(consequence=1)
            if d['condition']=='J':value['next_state']=1
            row=c.finish(fake_call(json.dumps(value),d));assert row['receipt']['realized_consequence']==row['actual']['consequence']==-1
            assert row['after']['protected']['memory'][-1]['consequence']==-1 and row['score']['consequence'] is False
            assert not row['control_measurement_matches']
            assert row['after']['protected']['memory'][:-1]==before['protected']['memory']
            canaries.append(dict(descriptor=d,request_bytes_unchanged=True,scored_future_not_executed_at_request=True,
                original_history=c.payload,prior_Memory=before['protected']['memory'],receipt=row['receipt'],actual=row['actual'],
                published_last=row['after']['protected']['memory'][-1],control_prediction=row['control_prediction'],probe_score=row['score']))
        matching=[dict(family=f,seed=s,**matched(requests[f,s,'J'],requests[f,s,'C'])) for f in ('O1','O2') for s in (99101,99102)]
        broken=deepcopy(requests['O1',99101,'C']);payload=json.loads(broken['prompt']);payload['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['transaction_id']=2;broken['prompt']=serialize(payload)
        try:matched(requests['O1',99101,'J'],broken)
        except AssertionError:pass
        else:raise AssertionError('additional visible mismatch admitted')
        # Hold source identity and fixture fixed; vary every finite consequence, wrong J state, and invalid probes.
        baseline=None
        for condition in ('J','C'):
            for value in (-1,0,1,None):
                d=deepcopy(schedule()[0]);d['condition']=condition;c=Context(d)
                raw='{' if value is None else json.dumps(dict(consequence=value,**({'next_state':3} if condition=='J' else {})))
                row=c.finish(fake_call(raw,d));grounded={k:row[k] for k in ('control_prediction','latch','actual','receipt','authorization','effects','provenance','control_measurement_matches','before','after')}
                if baseline is None:baseline=grounded
                assert grounded==baseline and row['probe_detached'] and not row['probe_publication']
                assert row['control_measurement_matches'] and row['score']['consequence']==(value==1 if value is not None else None)
                assert row['score']['next_state'] is None if condition=='C' or value is None else row['score']['next_state'] is False
                detached.append(dict(condition=condition,raw=raw,parsed=row['parsed'],probe_score=row['score'],identical_grounded_record=True))
        client=Synthetic();meta=dict(campaign_id=CAMPAIGN,synthetic_control=True,probe_only=True)
        campaign(out/'synthetic',client,meta)
        prior=[json.loads(l) for l in (out/'synthetic/model-calls.jsonl').read_text().splitlines()]
        campaign(out/'synthetic-replay',None,meta,prior)
        for n in FILES:assert (out/'synthetic'/n).read_bytes()==(out/'synthetic-replay'/n).read_bytes()
        for p in (out/'synthetic/memory-snapshots').glob('*.json'):assert p.read_bytes()==(out/'synthetic-replay/memory-snapshots'/p.name).read_bytes()
        bad_j=list(INVALID)+['{"next_state":1,"next_state":1,"consequence":1}','{"next_state":NaN,"consequence":1}']
        bad_c=['{','{"consequence":1} because','because {"consequence":1}','{"consequence":1,"next_state":1}',
            '{"consequence":true}','{"consequence":1.0}','{"consequence":"1"}','{"consequence":null}',
            '{"consequence":2}','{"consequence":-2}','{"consequence":NaN}','{"consequence":Infinity}',
            '{"consequence":1,"consequence":1}','{"consequence":1}{"consequence":1}','{}','[]','1','null',None,'```json\n{"consequence":1}\n```']
        for condition,bad in (('J',bad_j),('C',bad_c)):
            for raw in bad:
                try:parse(raw,condition)
                except (ValueError,TypeError):pass
                else:raise AssertionError('invalid repaired')
        for value in (-1,0,1):assert parse(json.dumps(dict(consequence=value)),'C')==dict(consequence=value)
        def synthetic_rows(j,c):
            rows=[]
            for d in schedule():
                i=(0 if d['family']=='O1' else 2)+(d['seed']-99101);positive=(j if d['condition']=='J' else c)[i]
                parsed=dict(consequence=int(positive))
                if d['condition']=='J':parsed['next_state']=1
                rows.append(dict(descriptor=d,valid=True,parsed=parsed,score=dict(next_state=True if d['condition']=='J' else None,
                    consequence=positive,exact=positive if d['condition']=='J' else None),authentic_post_response_score=True,authentic_history=True,probe_detached=True))
            return rows
        cases=[([False]*4,[True,True,True,False],A),([False]*4,[True,False,False,False],B),
            ([False]*4,[True,True,False,False],C),([True]*4,[True]*4,C),([True,False,False,False],[False,True,True,True],C),
            ([True,True,False,False],[True,True,True,True],C)]
        for j,c,expected in cases:assert summarize(synthetic_rows(j,c),8,True,True)['classification']==expected
        base=synthetic_rows([False]*4,[True]*4)
        for kwargs in (dict(replay=False),dict(replay=True,matched_requests=False),dict(replay=True,leak_controls=False),dict(replay=True,integrity=False)):
            assert summarize(base,8,**kwargs)['classification']==C
        for r in base:
            if r['descriptor']['condition']=='J':r['parsed']['next_state']=3;r['score']['next_state']=False;r['score']['exact']=False
        assert summarize(base,8,True,True)['classification']==A
        base[0]['valid']=False;base[0]['parsed']=None
        assert summarize(base,8,True,True)['classification']==C
        j=Journal(out/'ambiguous',campaign='PREFLIGHT_ONLY');j.append('REQUEST_INTENT_RECORDED',{},'one');j.close()
        check=inspect(out/'ambiguous');assert check['ambiguous_calls']==['one'] and not check['automatic_reissue_allowed']
        partial=out/'ambiguous/journal.jsonl';partial.write_bytes(partial.read_bytes()+b'{');assert not inspect(out/'ambiguous')['journal_valid']
    atomic_write(out/'canaries.json',canaries);atomic_write(out/'matched-requests.json',matching)
    atomic_write(out/'detachment-controls.json',dict(variants=detached,identical_grounded_record=baseline))
    result=dict(passed=True,actual_model_calls=0,canaries=8,matched_request_pairs=4,extra_field_mismatch_rejected=True,
        detached_output_variants=8,synthetic_campaign_responses=8,synthetic_replay_responses=8,strict_J_parser_rejections=len(bad_j),
        strict_C_parser_rejections=len(bad_c),invalid_probes_no_authority=True,classification_controls=12,durability_controls=2,
        byte_identical_replay=True,frozen_inputs_sha256=file_digest(PACKAGE/'frozen-inputs.json'),
        world_executions=dict(canaries=16,detachment_controls=16,synthetic_campaign=16,synthetic_replay=16,total=64))
    atomic_write(out/'preflight.json',result);print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);run(ap.parse_args().out)
