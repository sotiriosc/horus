"""Zero-model-call receipt, leak, strict-parser and durability preflight."""
from copy import deepcopy
from pathlib import Path
import argparse,json
from unittest.mock import patch
from experiments.model_map_proposal_v0.adapter import parse,INVALID
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect,atomic_write,file_digest
from .protocol import PACKAGE,schedule,frozen,summarize,body,A,B,C
from .fixture import Context
from .run import campaign,FILES


def fake_call(raw,d):
    try:value=parse(raw);error=None
    except (ValueError,TypeError) as exc:value=None;error=str(exc)
    return dict(call_id=f'preflight:{d["index"]}',parsed=value,parse_error=error,response=dict(raw_output=raw,transport_error=None,response_metadata={}))


class Synthetic:
    def __init__(self):self.requests=0
    def generate(self,call):
        self.requests+=1;assert self.requests<=8
        return dict(raw_output='{"next_state":1,"consequence":1}',transport_error=None,response_metadata={'synthetic_control':True})


def run(out):
    frozen();out.mkdir(exist_ok=False);canaries=[]
    with patch('socket.socket',side_effect=AssertionError('no inference in preflight')):
        # Each canary changes only the private next-execution consequence after acquiring genuine history.
        for d in schedule():
            c=Context(d);before=deepcopy(c.before);request=json.dumps(c.request)
            world=c.c._active.world.fixture.oracle
            law=list(world._CONSEQUENCE);law[4]=-1;world._CONSEQUENCE=tuple(law)
            assert c.before==before and json.dumps(c.request)==request
            assert json.dumps(body(d,c.reader.capture(d['mapping'])['map_inputs']['HOLD']))==request
            c.audit_before();row=c.finish(fake_call('{"next_state":1,"consequence":1}',d))
            assert row['receipt']['realized_consequence']==-1 and row['actual']['consequence']==-1
            assert row['after']['protected']['memory'][-1]['consequence']==-1 and not row['score']['exact']
            assert row['after']['protected']['memory'][:-1]==before['protected']['memory']
            canaries.append(dict(descriptor=d,request_bytes_unchanged=True,scored_future_not_executed_at_request=True,
                prior_observations=before['protected']['memory'],receipt=row['receipt'],actual=row['actual'],published_last=row['after']['protected']['memory'][-1]))
        client=Synthetic();campaign(out/'synthetic',client,dict(campaign_id='HORUS_MAP_POSITIVE_EVIDENCE_DEPTH_V0',synthetic_control=True))
        prior=[json.loads(l) for l in (out/'synthetic/model-calls.jsonl').read_text().splitlines()]
        campaign(out/'synthetic-replay',None,dict(campaign_id='HORUS_MAP_POSITIVE_EVIDENCE_DEPTH_V0',synthetic_control=True),prior)
        for n in FILES:assert (out/'synthetic'/n).read_bytes()==(out/'synthetic-replay'/n).read_bytes()
        for p in (out/'synthetic/memory-snapshots').glob('*.json'):assert p.read_bytes()==(out/'synthetic-replay/memory-snapshots'/p.name).read_bytes()
        bad=list(INVALID)+['{"next_state":1,"next_state":1,"consequence":1}','{"next_state":NaN,"consequence":1}']
        for raw in bad:
            try:parse(raw)
            except (ValueError,TypeError):pass
            else:raise AssertionError('invalid repaired')
        c=Context(schedule()[0]);row=c.finish(fake_call('{',c.d));assert row['before']==row['after'] and not row['valid']
        def synthetic_rows(d1,d2):
            out=[]
            for d in schedule():
                i=(0 if d['family']=='O1' else 2)+(d['seed']-98001);correct=(d1 if d['depth']==1 else d2)[i]
                out.append(dict(descriptor=d,valid=True,parsed=dict(next_state=1,consequence=1 if correct else 0),
                    score=dict(next_state=True,consequence=correct,exact=correct),authentic_post_prediction_score=True))
            return out
        cases=[([False,False,True,False],[True,True,True,False],A),([False]*4,[True,False,False,False],B),
            ([False]*4,[True,True,False,False],C),([True]*4,[True]*4,C),([True,False,False,False],[False,True,True,True],C)]
        for x,y,expected in cases:assert summarize(synthetic_rows(x,y),8,True,True)['classification']==expected
        assert summarize(synthetic_rows([False]*4,[True]*4),8,True,False)['classification']==C
        rows=synthetic_rows([False]*4,[True]*4);rows[0]['valid']=False;rows[0]['parsed']=None;rows[0]['authentic_post_prediction_score']=False
        assert summarize(rows,8,True,True)['classification']==C
        # Durable ambiguous intent must never be treated as permission to repeat.
        j=Journal(out/'ambiguous',campaign='PREFLIGHT_ONLY');j.append('REQUEST_INTENT_RECORDED',{},'one');j.close()
        check=inspect(out/'ambiguous');assert check['ambiguous_calls']==['one'] and not check['automatic_reissue_allowed']
        partial=out/'ambiguous/journal.jsonl';partial.write_bytes(partial.read_bytes()+b'{')
        assert not inspect(out/'ambiguous')['journal_valid']
    atomic_write(out/'canaries.json',canaries)
    result=dict(passed=True,actual_model_calls=0,canaries=len(canaries),synthetic_campaign_responses=8,synthetic_replay_responses=8,
        strict_parser_rejections=len(bad),invalid_no_execution=True,classification_controls=7,durability_controls=2,
        byte_identical_replay=True,frozen_inputs_sha256=file_digest(PACKAGE/'frozen-inputs.json'),
        world_executions=dict(canaries=20,synthetic_campaign=20,synthetic_replay=20,invalid_fixture_setup=1,total=61))
    atomic_write(out/'preflight.json',result);print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);run(ap.parse_args().out)
