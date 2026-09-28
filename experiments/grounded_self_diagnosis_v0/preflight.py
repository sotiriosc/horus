"""Check frozen inputs/source/model and reachable publication ancestry before inference."""
from hashlib import sha256
from pathlib import Path
import json
from publication.audit import audit
from .protocol import SOURCE,SOURCE_SHA256,build_inputs
from .worker import INPUTS_PATH,verify_model

def main():
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((root/'research/grounded-self-diagnosis-v0/source-manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if sha256((root/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen source mismatch: '+name)
    if sha256((root/SOURCE).read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise RuntimeError('source campaign changed')
    if json.loads((root/INPUTS_PATH).read_text())!=build_inputs(root/SOURCE):
        raise RuntimeError('blind input export changed')
    verify_model()
    checked=audit(False)
    if checked['status']!='PASS':raise RuntimeError('private artifact in reachable history')
    return dict(status='PASS',source_files=len(manifest['sha256']),
        reachable_history_audit=checked['status'],primary_call_ceiling=3)
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
