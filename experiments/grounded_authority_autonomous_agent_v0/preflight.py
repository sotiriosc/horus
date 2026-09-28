"""Stop inference if frozen source, model identity, or publication lineage changes."""
from hashlib import sha256
from pathlib import Path
import json,urllib.request
from publication.audit import audit
from .protocol import MODEL,RUNS,DECISIONS

PINNED_DIGEST='4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a'

def main():
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((root/'research/grounded-authority-autonomous-agent-v0/source-manifest.json').read_text())
    for path,expected in manifest['sha256'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen source mismatch: '+path)
    models=json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=10))['models']
    matches=[m for m in models if m['name']==MODEL and m['digest']==PINNED_DIGEST]
    if len(matches)!=1:raise RuntimeError('pinned incumbent model unavailable or changed')
    checked=audit(False)
    if checked['status']!='PASS':raise RuntimeError('private artifact in reachable history')
    return dict(status='PASS',runs=list(RUNS),decisions_per_run=DECISIONS,
        model=MODEL,model_digest=PINNED_DIGEST,source_files=len(manifest['sha256']),
        reachable_history_audit=checked['status'])
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
