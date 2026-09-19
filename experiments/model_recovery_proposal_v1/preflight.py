"""Complete fixed schedule with synthetic correct/wrong values; zero inference."""
import argparse
import hashlib
import json
from pathlib import Path
from .campaign import registration,probe,FixedResponse,no_recovery,encoded,projection


def check():
    plan,annex=registration();rows=[]
    for d in plan:
        for correct in (True,False):
            value=d['fixture']['actual_next_state']
            if not correct:value=(value+1)%4
            transport=FixedResponse(json.dumps({'replacement_state':value}))
            row=probe(transport,d)
            assert transport.requests==1 and row['correct']==correct
            duplicate=probe(FixedResponse(transport.raw),d,instrument=False)
            assert encoded(projection(row))==encoded(projection(duplicate))
            rows.append(row)
    holds=no_recovery()
    return dict(preflight='PASS',actual_model_calls=0,registered_calls=96,synthetic_transactions=len(rows),
                correct_authorizations=sum(r['correct'] for r in rows),wrong_rejections=sum(not r['correct'] for r in rows),
                no_recovery_controls=len(holds),observer_noninterference=True,
                annex_sha256=hashlib.sha256(annex).hexdigest()),dict(rows=rows,no_recovery=holds),plan,annex


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--replay',type=Path)
    a=parser.parse_args();result,data,plan,annex=check()
    if a.output.resolve().is_relative_to(Path(__file__).resolve().parents[2]):raise ValueError('evidence must be external')
    a.output.mkdir(parents=True,exist_ok=False)
    for name,content in (('preflight.json',encoded(data)),('results.json',encoded(result)),('registered-prompts.json',annex)):
        (a.output/name).write_bytes(content)
        if a.replay:assert content==(a.replay/name).read_bytes()
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
