"""Descriptive resource summaries from recorded watchdog samples only."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];A=Path('/mnt/d/horus-research-assets/qwen3-14b-qlora-v0');stages={}
for p in sorted((A/'monitor').glob('cycle*.jsonl')):
 rows=[json.loads(x) for x in p.read_text().splitlines()];assert rows
 stages[p.stem]=dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),samples=len(rows),last_recorded_elapsed_seconds=rows[-1]['elapsed_seconds'],minimum_sampled_gpu_free_GiB=min(x['gpu_free_GiB'] for x in rows),maximum_sampled_temperature_C=max(x['gpu_temperature_C'] for x in rows),minimum_sampled_linux_available_GiB=min(x['linux_available_GiB'] for x in rows),minimum_sampled_windows_free_GiB=min(x['windows_free_GiB'] for x in rows),resource_threshold_stops=[x for x in rows if x['stop_reason']])
result=dict(scope='Descriptive sampled device/host resource accounting; may include other applications. Samples are not continuous process-allocation peaks and do not measure unlogged work or downtime. Frozen scientific recipe and gates are unchanged.',stages=stages)
(P/'resource-accounting.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(stages=len(stages))))
