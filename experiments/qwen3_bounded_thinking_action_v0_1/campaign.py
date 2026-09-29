"""Read-only preflight and semantic diagnostic; no simulator or Memory imports."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
from statistics import median
import json
from .pure import STUDY,atomic_write,assert_read_only,verify_sources,verify_model,make_plan,direct_call


def prepare(private):
    verify_sources();assert_read_only(private)
    path=STUDY/'frozen-plan.json'
    if path.exists():raise RuntimeError('plan already frozen')
    plan=make_plan();atomic_write(path,plan)
    atomic_write(STUDY/'read-only-attestation-before.json',assert_read_only(private))
    print(json.dumps(dict(status=plan['status'],preflight=len(plan['preflight']),stage_a=len(plan['stage_a']),
        read_only=plan['read_only_before_inference'])),flush=True)


def run_preflight(private):
    verify_sources();assert_read_only(private);verify_model()
    plan=json.loads((STUDY/'frozen-plan.json').read_text())
    if plan['status']!='FROZEN_BEFORE_INFERENCE':raise RuntimeError('plan not frozen')
    path=STUDY/'preflight-result.json'
    if path.exists():raise RuntimeError('preflight already attempted')
    result=dict(status='RUNNING',calls=[])
    for row in plan['preflight']:
        item=direct_call(row,private,'preflight')
        result['calls'].append(item)
        if item['status']!='PASS':result['status']='BOUNDED_THINKING_INTERFACE_NOT_ESTABLISHED'
        atomic_write(path,result)
        print(json.dumps(dict(name=row['name'],status=item['status'],action=item.get('action'),
            wall_seconds=item['metrics']['wall_seconds'])),flush=True)
        if item['status']!='PASS':return result['status']
    result['status']='PASS';atomic_write(path,result)
    return 'PASS'


def run_stage_a(private):
    verify_sources();assert_read_only(private);verify_model()
    pre=json.loads((STUDY/'preflight-result.json').read_text())
    if pre['status']!='PASS' or len(pre['calls'])!=3:raise RuntimeError('three-call interface preflight not passed')
    plan=json.loads((STUDY/'frozen-plan.json').read_text())
    path=STUDY/'stage-a-result.json'
    if path.exists():raise RuntimeError('Stage A already attempted')
    result=dict(status='RUNNING',calls=[])
    for row in plan['stage_a']:
        item=direct_call(row,private,'stage-a')
        result['calls'].append(item)
        if item['status']!='PASS':result['status']='BOUNDED_THINKING_INTERFACE_NOT_ESTABLISHED'
        atomic_write(path,result)
        print(json.dumps(dict(name=row['name'],status=item['status'],action=item.get('action'),
            wall_seconds=item['metrics']['wall_seconds'])),flush=True)
        if item['status']!='PASS':return result['status']
    result['status']='COMPLETE';atomic_write(path,result)
    return 'COMPLETE'


def gate(private):
    assert_read_only(private)
    plan=json.loads((STUDY/'frozen-plan.json').read_text())
    result=json.loads((STUDY/'stage-a-result.json').read_text())
    if result['status']!='COMPLETE' or len(result['calls'])!=19:raise RuntimeError('Stage A incomplete')
    calls={x['name']:x for x in result['calls']}
    def action(case,order):return calls[case+'_'+order]['action']
    order3=('O0','O1','O2')
    a1=[action('A1',o) for o in order3];a2=[action('A2',o) for o in order3]
    bchanged=sum(action('B1_E',o)!=action('B2',o) for o in order3)
    counts=Counter(x['action'] for x in result['calls'])
    checks={
        'all_strict_final_actions':all(x['status']=='PASS' for x in result['calls']),
        'frozen_request_digests':all(x['request_sha256']==row['request_sha256'] and
            x['projection_sha256']==row['projection_sha256'] for x,row in zip(result['calls'],plan['stage_a'])),
        'at_least_two_action_names':len(counts)>=2,
        'A_grounded_plus_one_swap_directional_all_orders':a1==['ADVANCE']*3 and a2==['HOLD']*3,
        'B_established_unseen_status_swap_changes_at_least_two_orders':bchanged>=2,
        'no_universal_HOLD':counts.get('HOLD',0)<19,
        'A_order_stability':len(set(a1))==1 and len(set(a2))==1,
    }
    behavior=all(checks.values())
    latency=median(x['metrics']['wall_seconds'] for x in result['calls']);fast=latency<15
    classification='QWEN_BOUNDED_THINKING_SEMANTIC_GATE_PASSED' if behavior and fast else \
        'THINKING_DOES_NOT_FIX_POLICY' if not behavior else 'THINKING_TOO_SLOW'
    established_negative=[];unresolved=[];unseen=[]
    for row,item in zip(plan['stage_a'],result['calls']):
        a=row['projection']['grounded_assessments'][item['action']]
        value=a.get('established_value') or {}
        if a['kind']=='ESTABLISHED' and value.get('consequence',0)<0:established_negative.append(row['name'])
        if a['kind']=='UNRESOLVED_CHANGE':unresolved.append(row['name'])
        if a['kind']=='UNSEEN':unseen.append(row['name'])
    output=dict(classification=classification,behavior_gate='PASS' if behavior else 'FAIL',
        latency_gate='PASS' if fast else 'FAIL',median_warm_action_wall_seconds=latency,
        frozen_latency_ceiling_seconds=15,checks=checks,action_counts=dict(sorted(counts.items())),
        B_changed_matched_orders=bchanged,established_negative_selections=established_negative,
        unresolved_selections=unresolved,unseen_selections=unseen,
        stage_b_authorized=False,read_only_verdict=assert_read_only(private))
    atomic_write(STUDY/'stage-a-gate.json',output)
    print(json.dumps(output,sort_keys=True),flush=True)
    return classification

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('command',choices=('prepare','preflight','stage-a','gate'))
    p.add_argument('--private-root',required=True,type=Path)
    args=p.parse_args()
    {'prepare':lambda:prepare(args.private_root),'preflight':lambda:run_preflight(args.private_root),
     'stage-a':lambda:run_stage_a(args.private_root),'gate':lambda:gate(args.private_root)}[args.command]()
