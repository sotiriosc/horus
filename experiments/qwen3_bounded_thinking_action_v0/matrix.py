"""One precommitted all-unseen fixture probe per native reasoning budget."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from .shared import BUDGETS,STUDY,direct_action,verify_model,verify_sources


def fixture():
    old=json.loads((STUDY.parent/'qwen3-grounded-agent-substitution-v0/stage-a-fixtures.json').read_text())['fixtures']['D']
    return old['projection'],old['route']['candidates']


def probe(private,budget):
    if budget not in BUDGETS:raise ValueError('unregistered budget')
    verify_sources();verify_model()
    out=STUDY/'interface-matrix.json'
    data=json.loads(out.read_text()) if out.exists() else dict(status='RUNNING',probes=[])
    expected=BUDGETS[len(data['probes'])] if len(data['probes'])<3 else None
    if budget!=expected:raise RuntimeError('matrix budget order/retry violation')
    projection,allowed=fixture()
    result=direct_action(projection,allowed,88101,private/f'R{budget}',budget)
    data['probes'].append(result)
    if len(data['probes'])==3:
        passes=[row['budget'] for row in data['probes'] if row['status']=='PASS']
        data['selected_q_tb_budget']=min(passes) if passes else None
        data['status']='PASS' if passes else 'BOUNDED_THINKING_INTERFACE_NOT_ESTABLISHED'
    _atomic_write(out,data)
    print(json.dumps(dict(budget=budget,status=result['status'],action=result.get('action'),
        wall_seconds=result['metrics']['wall_seconds'],selected_q_tb_budget=data.get('selected_q_tb_budget'))),flush=True)
    return result['status']

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('budget',type=int,choices=BUDGETS)
    p.add_argument('--private-root',required=True,type=Path)
    args=p.parse_args();probe(args.private_root,args.budget)
