"""Register once, run exactly 18 stateless calls, or replay without inference."""
import argparse
import json
import os
from pathlib import Path
import urllib.request
from .protocol import ROOT, MODEL, OPTIONS, SYSTEMS, MANIFEST, WEIGHTS, encoded, line, read, lines, register, validate_registration, classify, summarize
from experiments.model_recovery_proposal_v1.transport import metadata


class Transport:
    endpoint='http://127.0.0.1:11434'
    def __init__(self):self.count=0
    def generate(self, entry):
        if self.count>=18:raise RuntimeError('18-call limit')
        self.count+=1
        req=urllib.request.Request(self.endpoint+'/api/generate',data=entry['request_json'].encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=600) as response:data=json.load(response)
        if data.get('done') is not True or type(data.get('response')) is not str:raise RuntimeError('incomplete response; no retry')
        return data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument('--register',type=Path,metavar='COMPOSITION_ARCHIVE')
    group.add_argument('--live',action='store_true');group.add_argument('--replay',type=Path)
    p.add_argument('--registration',type=Path);p.add_argument('--proof',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.resolve().is_relative_to(ROOT):raise ValueError('raw evidence must remain outside public tree')
    if args.register:
        reg=register(args.register);validate_registration(reg)
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'registration.json').write_text(encoded(reg));print('18 requests frozen; ZERO MODEL CALLS');return
    reg=read(args.registration) if args.registration else read(args.replay/'registration.json')
    validate_registration(reg)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'registration.json').write_text(encoded(reg))
    if args.replay:
        meta=read(args.replay/'metadata.json');archived=lines(args.replay/'model-calls.jsonl');attempts=lines(args.replay/'attempted-requests.jsonl')
        assert len(archived)==len(attempts)==18
    else:
        transport=Transport();proof=read(args.proof)
        meta=metadata(transport,dict(model=dict(manifest_digest=MANIFEST,weights_digest=WEIGHTS)),proof)
        del meta['system'];meta['systems']=SYSTEMS;meta['options']=OPTIONS
    (args.output/'metadata.json').write_text(encoded(meta));rows=[]
    with (args.output/'model-calls.jsonl').open('x') as log, (args.output/'attempted-requests.jsonl').open('x') as audit:
        for entry in reg['plan']:
            attempt=dict(index=entry['index'],context=entry['context'],condition=entry['condition'],request_json=entry['request_json'])
            audit.write(line(attempt));audit.flush();os.fsync(audit.fileno())
            if args.replay:
                assert attempt==attempts[entry['index']]
                response=archived[entry['index']]['response']
            else:
                try:response=transport.generate(entry)
                except Exception as exc:
                    (args.output/'failure.json').write_text(encoded(dict(index=entry['index'],error=str(exc),retry=False)))
                    (args.output/'results.json').write_text(encoded(summarize(reg,rows,meta)))
                    raise
            row=classify(entry,response)
            if args.replay:assert row==archived[entry['index']]
            rows.append(row);log.write(line(row));log.flush();os.fsync(log.fileno())
            print(f"{entry['index']+1}/18 context={entry['context']} {entry['condition']} valid={row['shape']['strict_valid']}",flush=True)
    result=summarize(reg,rows,meta);(args.output/'results.json').write_text(encoded(result))
    if args.replay:
        for name in ('registration.json','metadata.json','model-calls.jsonl','attempted-requests.jsonl','results.json'):
            assert (args.output/name).read_bytes()==(args.replay/name).read_bytes(),name
        print('FIVE FILES BYTE-IDENTICAL; ZERO NEW INFERENCE')
    print(result['primary_decision'])


if __name__=='__main__':main()
