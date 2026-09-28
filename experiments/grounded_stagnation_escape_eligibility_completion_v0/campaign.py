"""Fixed-order case generation; stop solely on signed naturally eligible prefixes."""
from argparse import ArgumentParser
from pathlib import Path
import json,os,subprocess,sys
from horus.live import _atomic_write
from .worker import ORDER,OPPORTUNITY,CONTROLS
from .analyze import audit_case

MODULE='experiments.grounded_stagnation_escape_eligibility_completion_v0.worker'

def invoke(root,command,case):
    env=dict(os.environ)
    env['PYTHONPATH']=str(Path.cwd())
    subprocess.run([sys.executable,'-m',MODULE,command,
                    '--private-root',str(root),'--case',case],
                   check=True,env=env)

def run(root):
    root.mkdir(parents=True,exist_ok=False)
    generated=[];eligible=[]
    for case in ORDER:
        invoke(root,'prepare-one',case)
        generated.append(case)
        if case in CONTROLS:
            invoke(root,'run-control',case)
        else:
            invoke(root,'run-until-pause',case)
            if (root/'cases'/case/'pause.json').exists():
                invoke(root,'restart-check',case)
                invoke(root,'continue-case',case)
        report,_=audit_case(root,case)
        _atomic_write(root/'cases'/case/'case-evaluation.json',report)
        if report['eligible_prefix']:eligible.append(case)
        print(json.dumps(dict(completed_case=case,prefix_status=report['prefix_status'],
            eligible_count=len(eligible),first_escape=report['first_escape_decision'],
            restart=report['restart_status'])),flush=True)
        if len(eligible)==4:break
    result=dict(status='COMPLETE',generated_cases=generated,eligible_cases=eligible,
                stop_reason='FOUR_NEW_ELIGIBLE_PREFIXES' if len(eligible)==4 else 'CASE_CEILING_12',
                maximum_generated_cases=12,fixed_order=list(ORDER))
    _atomic_write(root/'campaign-stop.json',result)
    print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    run(p.parse_args().private_root)
