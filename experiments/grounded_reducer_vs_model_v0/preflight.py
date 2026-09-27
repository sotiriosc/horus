from hashlib import sha256
import json
from pathlib import Path
from experiments.modern_memory_vs_horus_v0.preflight import main as protected_preflight
from experiments.modern_memory_vs_horus_v0_1.preflight import main as repaired_preflight
from experiments.modern_memory_vs_horus_v0_1.transport import RULE_HASH
from .protocol import ARMS,SCHEDULES,MODEL_LOGICAL_CEILING,MODEL_PHYSICAL_CEILING

ROOT=Path(__file__).resolve().parents[2]

def main():
    original=protected_preflight()
    inherited=repaired_preflight()
    manifest=json.loads((ROOT/'research/grounded-reducer-vs-model-v0/source-manifest.json').read_text())
    for name,expected in manifest['sha256'].items():
        if sha256((ROOT/name).read_bytes()).hexdigest()!=expected:
            raise RuntimeError('frozen source mismatch: '+name)
    if manifest['transport_rule_sha256']!=RULE_HASH:
        raise RuntimeError('bounded transport rule changed')
    if manifest['schedule_sha256']!=sha256(json.dumps(SCHEDULES,sort_keys=True,
                    separators=(',',':')).encode()).hexdigest():
        raise RuntimeError('schedule changed')
    return dict(status='PASS',inference_calls=0,protected_preflight=original['status'],
        parent_repair_preflight=inherited['status'],frozen_sources_verified=True,
        schedules={name:len(rows) for name,rows in SCHEDULES.items()},
        conditions=list(ARMS),model_logical_ceiling=MODEL_LOGICAL_CEILING,
        model_physical_ceiling=MODEL_PHYSICAL_CEILING,
        repair_rule_sha256=RULE_HASH)

if __name__=='__main__':print(json.dumps(main(),indent=2,sort_keys=True))
