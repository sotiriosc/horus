"""Freeze guard for the preregistered autonomous campaign."""
from hashlib import sha256
from pathlib import Path
import json
from publication.audit import audit
from .protocol import RUNS,DECISIONS,REVIEW_EVERY,MODEL

def main():
    root=Path(__file__).resolve().parents[2]
    manifest=json.loads((root/'research/grounded-autonomous-agent-v0/source-manifest.json').read_text())
    for path,expected in manifest['sha256'].items():
        if sha256((root/path).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen source mismatch: '+path)
    checked=audit(False)
    if checked['status']!='PASS':raise RuntimeError('publication history contains private material')
    return dict(status='PASS',runs=list(RUNS),decisions_per_run=DECISIONS,
                review_every=REVIEW_EVERY,model=MODEL,source_files=len(manifest['sha256']),
                reachable_history_audit=checked['status'])
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
