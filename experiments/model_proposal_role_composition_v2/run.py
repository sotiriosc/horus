"""One bounded v2 live run or mechanically identical recorded-response replay."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.model_recovery_proposal_v1.transport import metadata as verify_server
from .protocol import schedule,SYSTEMS,OPTIONS
from .runtime import Broker,setup,step
from .transport import LocalModel,Replay
from .checks import controls
from .preflight import check,frozen
from .analysis import summarize

FILES=('metadata.json','schedule.json','model-calls.jsonl','steps.jsonl','chains.json','controls.json','results.json')
def encoded(x):return json.dumps(x,sort_keys=True,indent=2)+'\n'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--replay',type=Path);parser.add_argument('--model-bytes',type=Path)
    parser.add_argument('--baseline',required=True,type=Path,help='Original v1 model-calls.jsonl; comparison only')
    args=parser.parse_args();root=Path(__file__).resolve().parents[2]
    registration=frozen();gate=check();assert gate['status']=='PASS'
    assert digest(args.baseline)==registration['baseline_calls_sha256']
    baseline=[json.loads(s) for s in args.baseline.read_text().splitlines() if s]
    baseline=[c for c in baseline if c['role']=='Map'];assert len(baseline)==9
    if args.output.resolve().is_relative_to(root):raise ValueError('private evidence must be external')
    args.output.mkdir(parents=True,exist_ok=False)
    if args.replay:
        client=Replay(args.replay/'model-calls.jsonl');meta=json.loads((args.replay/'metadata.json').read_text())
        assert meta['role_systems']==SYSTEMS and meta['role_options']==OPTIONS
    else:
        if args.model_bytes is None:raise ValueError('full verified model-byte proof required')
        client=LocalModel();old=json.loads((root/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=verify_server(client,old,json.loads(args.model_bytes.read_text()))
        meta.pop('system',None);meta.pop('options',None)
        meta.update(role_systems=SYSTEMS,role_options=OPTIONS,stateless=True)
    (args.output/'metadata.json').write_text(encoded(meta));(args.output/'schedule.json').write_text(encoded(schedule()))
    rows=[]
    with (args.output/'model-calls.jsonl').open('w') as cf,(args.output/'steps.jsonl').open('w') as sf:
        def emit(call):cf.write(json.dumps(call,sort_keys=True)+'\n');cf.flush()
        broker=Broker(client,emit)
        try:
            for descriptor in schedule():
                bundle=setup(descriptor['episode'])
                for decision in range(8):
                    assert frozen()==registration
                    row=step(bundle,broker,descriptor,decision);rows.append(row)
                    sf.write(json.dumps(row,sort_keys=True)+'\n');sf.flush()
                    print(f"episode={descriptor['episode']} {descriptor['family']} decision={decision} calls={len(broker.calls)} executed={row['probe']['authorization']['executed']} commit={row['probe']['authorization']['committed']} stop={row['termination']}",flush=True)
                    if row['termination']:break
            if args.replay:assert client.requests==len(client.rows)
            synthetic=controls();assert synthetic['counts']==dict(Explorer=5,Map=14,Recovery=22)
            result,chains=summarize(rows,broker.calls,baseline)
            assert frozen()==registration
            result.update(source_sha256=registration['sha256'],post_live_controls=synthetic['counts'],
                unknown_preflight=dict(status=gate['status'],projection_contexts=gate['projection_contexts']),
                baseline_calls_sha256=registration['baseline_calls_sha256'])
            for name,value in (('controls.json',synthetic),('chains.json',chains),('results.json',result)):
                (args.output/name).write_text(encoded(value))
        except Exception as exc:
            (args.output/'STOP.json').write_text(encoded(dict(error_type=type(exc).__name__,reason=str(exc),completed_steps=len(rows),requests=len(broker.calls))))
            raise
    if args.replay:
        for name in FILES:assert (args.output/name).read_bytes()==(args.replay/name).read_bytes(),name
        print('All seven evidence files byte-identical; zero new inference.')
    print(result['live_eligible_classification']);print(result['real_calls']);print('Final decision awaits replay/regressions.')


if __name__=='__main__':main()
