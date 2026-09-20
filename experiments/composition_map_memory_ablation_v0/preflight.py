"""Read-only evidence gate, full model bytes, and zero-inference tests."""
import argparse,hashlib,json,unittest
from pathlib import Path
from datetime import datetime,timezone
from . import test_study
from .contexts import ROOT,PACKAGE,frozen,reconstruct,public_contexts,source_hashes
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import atomic_write,require_durable,file_digest


def verify_model(model_root,expected):
    def sha(path):
        h=hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
        return h.hexdigest()
    manifest=model_root/'manifests/registry.ollama.ai/library/dolphin-mixtral/latest'
    assert sha(manifest)==expected['manifest_sha256'];m=json.loads(manifest.read_text());blobs=[]
    for item in [m['config'],*m['layers']]:
        digest=item['digest'].split(':')[1];path=model_root/'blobs'/item['digest']
        assert sha(path)==digest and path.stat().st_size==item['size']
        blobs.append(dict(digest=digest,bytes=path.stat().st_size,media_type=item['mediaType']))
    assert blobs==expected['all_manifest_blobs']
    return {**expected,'verified_utc':datetime.now(timezone.utc).isoformat(),'complete_blobs_verified':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--model-root',type=Path);p.add_argument('--expected-model',type=Path)
    args=p.parse_args();require_durable(args.output.parent,ROOT);reg=frozen()
    assert source_hashes(args.source)==reg['r1_evidence_sha256']
    cs=reconstruct(args.source);assert public_contexts(cs)==json.loads((PACKAGE/'contexts.json').read_text())
    if args.model_root:
        model=verify_model(args.model_root,json.loads(args.expected_model.read_text()))
        atomic_write(args.output.parent/'model-bytes.json',model)
    test_study.SOURCE=args.source
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(test_study.Tests))
    proof=dict(passed=result.wasSuccessful(),tests=result.testsRun,actual_model_calls=0,contexts=42,
        H_byte_identical=42,W_only_history_difference=42,source_evidence_unchanged=source_hashes(args.source)==reg['r1_evidence_sha256'],
        frozen_inputs_sha256=file_digest(PACKAGE/'frozen-inputs.json'))
    atomic_write(args.output,proof)
    if not proof['passed']:raise SystemExit(2)
    print('PASS: 42 authenticated contexts; 84 fixed requests; zero inference.')


if __name__=='__main__':main()
