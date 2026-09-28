"""Source and publication-history guard for the separate action sensitivity v0 campaign."""
from hashlib import sha256
from pathlib import Path
import json
from publication.audit import audit
from .protocol import PRIMARY_CALLS,MODEL

def main():
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((root/'research/grounded-action-sensitivity-v0/source-manifest.json').read_text())
    for path,expected in manifest['sha256'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen action sensitivity v0 source mismatch: '+path)
    checked=audit(False)
    if checked['status']!='PASS':raise RuntimeError('private artifact in reachable history')
    return dict(status='PASS',primary_calls=PRIMARY_CALLS,model=MODEL,source_files=len(manifest['sha256']),
        reachable_history_audit=checked['status'])
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
