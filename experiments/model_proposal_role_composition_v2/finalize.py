"""Apply replay/regression evidence to provisional results without new inference."""
import argparse
import hashlib
import json
from pathlib import Path
from .analysis import A,B,C
from .run import encoded,FILES


def finalize(real,assurance):
    result=json.loads((real/'results.json').read_text())
    verification=json.loads(assurance.read_text())
    for name in FILES:
        assert hashlib.sha256((real/name).read_bytes()).hexdigest()==verification['live_evidence_sha256'][name],name
    executions=verification['executions'];assert executions
    passed=all(x['exit_code']==x['expected_exit_code'] for x in executions)
    assert verification['required_regression_groups_complete']
    replay=verification['v2_replay_byte_identical'] and all(verification['replay_files'][name]==verification['live_evidence_sha256'][name] for name in FILES)
    result['integrity_requirements'].update(exact_replay_passes=replay,historical_regressions_pass=passed)
    violation=not all(v for k,v in result['integrity_requirements'].items() if k not in ('exact_replay_passes','historical_regressions_pass'))
    result['classification']=B if violation else A if all(result['integrity_requirements'].values()) and all(result['live_path_coverage'].values()) else C
    result['classification_status']='FINAL: evaluated with recorded replay and historical regression evidence'
    result['classification_scope']='All 20 integrity requirements and all seven live paths evaluated separately; behavior is descriptive.'
    result['assurance_sha256']=hashlib.sha256(assurance.read_bytes()).hexdigest()
    result['actual_regression_commands']=len(executions)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('real','assurance','output'):p.add_argument('--'+name,required=True,type=Path)
    p.add_argument('--replay',type=Path);args=p.parse_args();result=finalize(args.real,args.assurance);text=encoded(result)
    if args.replay:assert text==args.replay.read_text()
    with args.output.open('x') as f:f.write(text)
    print(result['classification']);print('ZERO NEW INFERENCE; final results verified against retained campaign and assurance.')
