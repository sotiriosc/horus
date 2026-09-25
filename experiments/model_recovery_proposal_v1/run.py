"""Exactly one frozen live campaign; private response evidence and exact replay."""
import argparse
import hashlib
import json
from pathlib import Path
from .adapter import MODEL,SYSTEM,OPTIONS
from .campaign import registration,probe,controls,encoded,FixedResponse,projection
from .analysis import summarize
from .transport import LocalModel,metadata

FILES=('registered-prompts.json','model-calls.jsonl','steps.jsonl','controls.json','metadata.json','results.json')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_check(root):
    frozen=json.loads((Path(__file__).parent/'frozen-inputs.json').read_text())
    for name,h in frozen['inherited_sha256'].items():assert digest(root/name)==h,name
    return frozen


def sources(root):
    p=Path(__file__).parent
    files=list(p.glob('*.py'))+[p/'frozen-inputs.json',p/'registration-digests.json',p/'preflight-results.json',root/'research/model-recovery-proposal-v1-preregistration.md']
    return {str(f.relative_to(root)):digest(f) for f in sorted(files)}


class Replay:
    def __init__(self,path):self.rows=[json.loads(line) for line in path.read_text().splitlines()];self.requests=0
    def generate(self,prompt,seed):
        row=self.rows[self.requests];self.requests+=1;call=row['model_call']
        assert row['index']==self.requests-1
        assert call['exact_prompt']==prompt and call['options']=={**OPTIONS,'seed':seed}
        assert call['model']==MODEL and call['system']==SYSTEM and not call['transport_error']
        return call['raw_output'],call['response_metadata']


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--replay',type=Path);p.add_argument('--model-bytes',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[2];pkg=Path(__file__).parent
    frozen=frozen_check(root);plan,annex=registration()
    gate=json.loads((pkg/'preflight-results.json').read_text());registered=json.loads((pkg/'registration-digests.json').read_text())
    assert gate['preflight']=='PASS' and gate['actual_model_calls']==0
    assert hashlib.sha256(annex).hexdigest()==gate['annex_sha256']==registered['annex_sha256']
    if a.output.resolve().is_relative_to(root):raise ValueError('private evidence must be external')
    a.output.mkdir(parents=True,exist_ok=False)
    source_hashes=sources(root)
    if a.replay:
        transport=Replay(a.replay);meta=json.loads((a.replay.parent/'metadata.json').read_text())
    else:
        if a.model_bytes is None:raise ValueError('verified model-byte proof required')
        transport=LocalModel();meta=metadata(transport,frozen,json.loads(a.model_bytes.read_text()))
    (a.output/'metadata.json').write_bytes(encoded(meta));(a.output/'registered-prompts.json').write_bytes(annex)
    rows=[]
    try:
        with (a.output/'model-calls.jsonl').open('w') as calls,(a.output/'steps.jsonl').open('w') as steps:
            def emit(row):calls.write(json.dumps(row,sort_keys=True)+'\n');calls.flush()
            for d in plan:
                assert sources(root)==source_hashes
                row=probe(transport,d,emit);rows.append(row)
                steps.write(json.dumps(row,sort_keys=True)+'\n');steps.flush()
                print(f"{len(rows)}/96 {d['family']} fixture={d['fixture']['fixture_id']} j={d['mapping_index']} valid={row['valid']} correct={row['correct']} commit={row['probe']['authorization']['committed']}",flush=True)
        assert transport.requests==len(rows)==96
        synthetic=controls(plan)
        for row in rows:
            call=row['model_call']
            duplicate=probe(FixedResponse(call['raw_output'],call['response_metadata']),row['descriptor'],instrument=False)
            assert encoded(projection(duplicate))==encoded(projection(row))
        assert frozen_check(root)==frozen and sources(root)==source_hashes
        (a.output/'controls.json').write_bytes(encoded(synthetic))
        result=dict(summary=summarize(rows,synthetic),model=meta,observer_noninterference=True,source_sha256=source_hashes,
                    evidence_sha256={name:digest(a.output/name) for name in FILES if name!='results.json'})
        (a.output/'results.json').write_bytes(encoded(result))
        if a.replay:
            assert transport.requests==len(transport.rows)==96
            for name in FILES:assert (a.output/name).read_bytes()==(a.replay.parent/name).read_bytes(),name
            print('Exact replay: all six files byte-identical; zero new inference.')
        print(result['summary']['overall']);print(result['summary']['authorization_integrity'])
    except Exception as exc:
        (a.output/'STOP.json').write_bytes(encoded(dict(error_type=type(exc).__name__,reason=str(exc),completed_rows=len(rows),requests=transport.requests)))
        raise


if __name__=='__main__':main()
