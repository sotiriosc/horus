"""Zero-model-call interface diagnosis and exact replay; no inference implementation."""
import argparse
import hashlib
import json
from pathlib import Path
from .diagnostic import run


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--replay',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[2];pkg=Path(__file__).parent
    frozen=json.loads((pkg/'frozen-inputs.json').read_text())
    for group in ('source_sha256','additional_source_sha256'):
        for path,h in frozen[group].items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==h,path
    if a.output.resolve().is_relative_to(root):raise ValueError('retain detailed evidence outside public tree')
    a.output.mkdir(parents=True,exist_ok=False)
    data=run();uninstrumented=run(False)
    for arow,brow in zip(data['cases'],uninstrumented['cases']):
        assert {k:v for k,v in arow.items() if k!='native_observations'}=={k:v for k,v in brow.items() if k!='native_observations'}
    assert data['summary']==uninstrumented['summary']
    content=json.dumps(data,sort_keys=True,indent=2).encode()+b'\n'
    (a.output/'diagnostic.json').write_bytes(content)
    paths=list(pkg.glob('*.py'))+[pkg/'frozen-inputs.json',root/'research/model-recovery-proposal-v0-preregistration.md']
    result=dict(summary=data['summary'],interface=data['interface'],budget=data['budget'],
        observer_noninterference=True,diagnostic_sha256=hashlib.sha256(content).hexdigest(),
        source_sha256={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)})
    (a.output/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    if a.replay:
        for name in ('diagnostic.json','results.json'):assert (a.output/name).read_bytes()==(a.replay/name).read_bytes(),name
        print('Exact diagnostic replay: both files byte-identical; zero inference.')
    print(json.dumps(data['summary'],indent=2))
    # Exit 2 represents the intended blocked gate, not a native integrity failure.
    raise SystemExit(2)

if __name__=='__main__':main()
