"""Zero-inference matched-request, genuine-history, leak and software checks."""
from copy import deepcopy
from dataclasses import asdict
import argparse,json
from pathlib import Path
from unittest.mock import patch
from experiments.model_map_proposal_v0.adapter import parse,INVALID
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import Journal,inspect,atomic_write,file_digest
from .protocol import PACKAGE,schedule,frozen,summarize,body,matched,serialize,A,B,C
from .fixture import Context,ConditionController
from .run import campaign,FILES


def fake_call(raw,d):
    try:value=parse(raw);error=None
    except (ValueError,TypeError) as exc:value=None;error=str(exc)
    return dict(call_id=f'preflight:{d["index"]}',parsed=value,parse_error=error,response=dict(raw_output=raw,transport_error=None,response_metadata={}))


class Synthetic:
    def __init__(self):self.requests=0
    def generate(self,call):
        self.requests+=1;assert self.requests<=8
        ns=json.loads(call['exact_prompt'])['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['next_state']
        return dict(raw_output=json.dumps(dict(next_state=ns,consequence=1)),transport_error=None,response_metadata={'synthetic_control':True})


def run(out):
    frozen();out.mkdir(exist_ok=False);canaries=[];requests={};scope=[]
    with patch('socket.socket',side_effect=AssertionError('no inference in preflight')):
        for state in range(4):
            for action in ('ADVANCE','HOLD','RETREAT'):
                actual={}
                for condition in ('S','M'):
                    world=ConditionController('SOFTWARE_SCOPE',condition)._make_world(state)
                    actual[condition]=asdict(world.execute(1001,1,action));assert world.execution_count==1
                expected={**actual['S']}
                if (state,action)==(1,'HOLD'):expected['next_state']=2
                assert actual['M']==expected
                scope.append(dict(state=state,action=action,**actual,only_registered_relation_changed=True))
        for d in schedule():
            c=Context(d);before=deepcopy(c.before);request=json.dumps(c.request);requests[d['family'],d['seed'],d['condition']]=deepcopy(c.request)
            oracle=c.c._active.world.fixture.oracle;law=list(oracle._CONSEQUENCE);law[4]=-1;oracle._CONSEQUENCE=tuple(law)
            assert c.before==before and json.dumps(body(d,c.reader.capture(d['mapping'])['map_inputs']['HOLD']))==request
            c.audit_before();raw=json.dumps(dict(next_state=1 if d['condition']=='S' else 2,consequence=1))
            row=c.finish(fake_call(raw,d));assert row['receipt']['realized_consequence']==row['actual']['consequence']==-1
            assert row['after']['protected']['memory'][-1]['consequence']==-1 and not row['score']['exact']
            assert row['after']['protected']['memory'][:-1]==before['protected']['memory']
            canaries.append(dict(descriptor=d,request_bytes_unchanged=True,scored_future_not_executed_at_request=True,
                original_history=c.payload,prior_Memory=before['protected']['memory'],receipt=row['receipt'],actual=row['actual'],published_last=row['after']['protected']['memory'][-1]))
        matching=[dict(family=f,seed=s,**matched(requests[f,s,'S'],requests[f,s,'M'])) for f in ('O1','O2') for s in (99001,99002)]
        broken=deepcopy(requests['O1',99001,'M']);payload=json.loads(broken['prompt']);payload['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['transaction_id']=2
        broken['prompt']=serialize(payload)
        try:matched(requests['O1',99001,'S'],broken)
        except AssertionError:pass
        else:raise AssertionError('additional visible mismatch admitted')
        client=Synthetic();meta=dict(campaign_id='HORUS_MAP_SELF_LOOP_CONSEQUENCE_COUPLING_V0',synthetic_control=True)
        campaign(out/'synthetic',client,meta)
        prior=[json.loads(l) for l in (out/'synthetic/model-calls.jsonl').read_text().splitlines()]
        campaign(out/'synthetic-replay',None,meta,prior)
        for n in FILES:assert (out/'synthetic'/n).read_bytes()==(out/'synthetic-replay'/n).read_bytes()
        for p in (out/'synthetic/memory-snapshots').glob('*.json'):assert p.read_bytes()==(out/'synthetic-replay/memory-snapshots'/p.name).read_bytes()
        bad=list(INVALID)+['{"next_state":1,"next_state":1,"consequence":1}','{"next_state":NaN,"consequence":1}']
        for raw in bad:
            try:parse(raw)
            except (ValueError,TypeError):pass
            else:raise AssertionError('invalid repaired')
        c=Context(schedule()[0]);row=c.finish(fake_call('{',c.d));assert row['before']==row['after'] and not row['valid']
        def synthetic_rows(s,m):
            out=[]
            for d in schedule():
                i=(0 if d['family']=='O1' else 2)+(d['seed']-99001);positive=(s if d['condition']=='S' else m)[i]
                out.append(dict(descriptor=d,valid=True,parsed=dict(next_state=1 if d['condition']=='S' else 2,consequence=1 if positive else 0),
                    score=dict(next_state=True,consequence=positive,exact=positive),authentic_post_prediction_score=True))
            return out
        cases=[([False]*4,[True,True,True,False],A),([False]*4,[True,False,False,False],B),
            ([False]*4,[True,True,False,False],C),([True]*4,[True]*4,C),([True,False,False,False],[False,True,True,True],C),
            ([True,True,False,False],[True,True,True,True],C)]
        for s,m,expected in cases:assert summarize(synthetic_rows(s,m),8,True,True)['classification']==expected
        base=synthetic_rows([False]*4,[True]*4)
        assert summarize(base,8,True,False)['classification']==C
        assert summarize(base,8,True,True,matched_requests=False)['classification']==C
        # Consequence, not joint exactness, drives A: deliberately wrong predicted states still count.
        for r in base:r['parsed']['next_state']=3;r['score']['next_state']=False;r['score']['exact']=False
        assert summarize(base,8,True,True)['classification']==A
        base[0]['valid']=False;base[0]['parsed']=None;base[0]['authentic_post_prediction_score']=False
        assert summarize(base,8,True,True)['classification']==C
        j=Journal(out/'ambiguous',campaign='PREFLIGHT_ONLY');j.append('REQUEST_INTENT_RECORDED',{},'one');j.close()
        check=inspect(out/'ambiguous');assert check['ambiguous_calls']==['one'] and not check['automatic_reissue_allowed']
        partial=out/'ambiguous/journal.jsonl';partial.write_bytes(partial.read_bytes()+b'{');assert not inspect(out/'ambiguous')['journal_valid']
    atomic_write(out/'canaries.json',canaries);atomic_write(out/'matched-requests.json',matching);atomic_write(out/'world-law-scope.json',scope)
    result=dict(passed=True,actual_model_calls=0,canaries=8,matched_request_pairs=4,extra_field_mismatch_rejected=True,
        world_relation_pairs=12,synthetic_campaign_responses=8,synthetic_replay_responses=8,strict_parser_rejections=len(bad),invalid_no_execution=True,
        classification_controls=10,durability_controls=2,byte_identical_replay=True,frozen_inputs_sha256=file_digest(PACKAGE/'frozen-inputs.json'),
        world_executions=dict(law_scope=24,canaries=20,synthetic_campaign=20,synthetic_replay=20,invalid_fixture_setup=1,total=85))
    atomic_write(out/'preflight.json',result);print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);run(ap.parse_args().out)
