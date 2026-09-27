from hashlib import sha256
import json
from pathlib import Path
from experiments.modern_memory_vs_horus_v0.preflight import main as original_preflight
from .transport import RULE_HASH

ROOT=Path(__file__).resolve().parents[2]

def main():
    original=original_preflight()
    manifest=json.loads((ROOT/'research/modern-memory-vs-horus-v0.1/source-manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen v0.1 source mismatch: '+name)
    if RULE_HASH!=manifest['transport_repair_rule_sha256']:
        raise RuntimeError('transport rule changed')
    return dict(status='PASS',inference_calls=0,original=original,
                v01_sources_verified=True,repair_rule_sha256=RULE_HASH)

if __name__=='__main__': print(json.dumps(main(),indent=2,sort_keys=True))
