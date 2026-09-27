from hashlib import sha256
import json
from pathlib import Path
from experiments.grounded_hybrid_controller_v0.preflight import main as parent_preflight
from experiments.modern_memory_vs_horus_v0_1.transport import RULE_HASH
from .protocol import ARMS,SCENARIOS,MODEL_LOGICAL_CEILING,TOTAL_LOGICAL_CEILING,TOTAL_PHYSICAL_CEILING
ROOT=Path(__file__).resolve().parents[2]
def main():
    parent=parent_preflight()
    manifest=json.loads((ROOT/'research/grounded-safe-fallback-v0/source-manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen source mismatch: '+name)
    actual=sha256(json.dumps(SCENARIOS,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if manifest['schedule_sha256']!=actual or manifest['transport_rule_sha256']!=RULE_HASH:
        raise RuntimeError('frozen protocol or transport mismatch')
    return dict(status='PASS',parent_preflight=parent['status'],inference_calls=0,
        scenarios=list(SCENARIOS),arms=list(ARMS),model_logical_ceiling=MODEL_LOGICAL_CEILING,
        total_logical_ceiling=TOTAL_LOGICAL_CEILING,total_physical_ceiling=TOTAL_PHYSICAL_CEILING)
if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
