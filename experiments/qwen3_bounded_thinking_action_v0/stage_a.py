"""Frozen public contexts, order controls, strict Q-TB calls and preregistered gates."""
from argparse import ArgumentParser
from copy import deepcopy
from pathlib import Path
from statistics import median
import json

from horus.core import digest
from horus.live import _atomic_write
from experiments.qwen3_grounded_agent_substitution_v0.stage_a import signed_g,g_decision
from .shared import STUDY,BUDGETS,MAX_TOKENS,sha,build_request,direct_action,verify_model,verify_sources

CASES=(('B1',('O0','O1')),('B2',('O0','O1')),
       ('C1',('O0','O1')),('C2',('O0','O1')),
       ('D',('O0','O1','O2')),('E',('O0','O1','O2')),('H',('O0',)) )


def matrix_budget():
    matrix=json.loads((STUDY/'interface-matrix.json').read_text())
    budget=matrix.get('selected_q_tb_budget')
    if matrix['status']!='PASS' or budget not in BUDGETS or budget!=min(
            x['budget'] for x in matrix['probes'] if x['status']=='PASS'):
        raise RuntimeError('Q-TB not frozen by passing interface matrix')
    return budget


def prepare(private):
    verify_sources();budget=matrix_budget()
    out=STUDY/'stage-a-projections.json'
    if out.exists():raise RuntimeError('Stage A projections already frozen')
    fixtures=json.loads((STUDY.parent/'qwen3-grounded-agent-substitution-v0/stage-a-fixtures.json').read_text())['fixtures']
    mechanical={}
    for name in ('A','F'):
        f=fixtures[name];route=f['route']
        if route['route']!='MECHANICAL':raise RuntimeError(name+' mechanical route drift')
        mechanical[name]=dict(action=route['action'],source=route['source'],model_calls=0,
            projection_sha256=digest(f['projection']))
    gpath=private/'signed'/'G'/'T';gpath.mkdir(parents=True)
    gp,gr=signed_g(gpath)
    if digest(gp)!=digest(fixtures['G']['projection']):raise RuntimeError('fresh signed G semantic projection drift')
    mechanical['G']=g_decision(private,'T')
    if mechanical['G']['model_calls']!=0:raise RuntimeError('escape made model call')
    plan=[]
    for name,orders in CASES:
        fixture=fixtures[name];original=fixture['projection'];allowed=fixture['route']['candidates']
        if fixture['route']['route']!='MODEL' or original['available_actions']!=allowed:
            raise RuntimeError('frozen model fixture route drift: '+name)
        for order in orders:
            projection=deepcopy(original)
            if order=='O1':projection['available_actions']=list(reversed(allowed))
            if order=='O2':projection['available_actions']=allowed[1:]+allowed[:1]
            seed=3303+projection['decision_index'];request=build_request(projection,allowed,seed)
            plan.append(dict(case=name,order=order,projection=projection,allowed=allowed,seed=seed,
                semantic_projection_sha256=digest(projection),request_sha256=digest(request),
                request_bytes_sha256=sha(json.dumps(request,separators=(',',':')).encode())))
    if len(plan)!=15:raise RuntimeError('Stage A call count drift')
    _atomic_write(out,dict(status='FROZEN_BEFORE_STAGE_A_INFERENCE',selected_q_tb_budget=budget,
        total_completion_cap=MAX_TOKENS,mechanical=mechanical,calls=plan))
    print(json.dumps(dict(status='FROZEN_BEFORE_STAGE_A_INFERENCE',calls=len(plan),
        selected_q_tb_budget=budget,mechanical=mechanical)),flush=True)


def run(private):
    verify_sources();verify_model();budget=matrix_budget()
    plan=json.loads((STUDY/'stage-a-projections.json').read_text())
    if plan['selected_q_tb_budget']!=budget or plan['status']!='FROZEN_BEFORE_STAGE_A_INFERENCE':
        raise RuntimeError('Stage A frozen plan drift')
    out=STUDY/'stage-a-results.json'
    if out.exists():raise RuntimeError('refusing to rerun Stage A')
    result=dict(status='RUNNING',selected_q_tb_budget=budget,calls=[])
    for row in plan['calls']:
        response=direct_action(row['projection'],row['allowed'],row['seed'],
            private/'stage-a'/row['case']/row['order'],budget)
        if response['semantic_projection_sha256']!=row['semantic_projection_sha256'] or response['request_sha256']!=row['request_sha256'] or response['request_bytes_sha256']!=row['request_bytes_sha256']:
            raise RuntimeError('Stage A frozen request/projection digest drift')
        public=dict(case=row['case'],order=row['order'],**response)
        result['calls'].append(public)
        if response['status']!='PASS':result['status']='BOUNDED_THINKING_INTERFACE_NOT_ESTABLISHED'
        _atomic_write(out,result)
        print(json.dumps(dict(case=row['case'],order=row['order'],status=response['status'],
            action=response.get('action'),wall_seconds=response['metrics']['wall_seconds'])),flush=True)
        if response['status']!='PASS':return result['status']
    result['status']='COMPLETE';_atomic_write(out,result)
    return result['status']


def gate():
    plan=json.loads((STUDY/'stage-a-projections.json').read_text())
    result=json.loads((STUDY/'stage-a-results.json').read_text())
    if result['status']!='COMPLETE' or len(result['calls'])!=15:
        raise RuntimeError('Stage A not complete')
    calls={(x['case'],x['order']):x for x in result['calls']}
    def action(case,order):return calls[(case,order)]['action']
    checks={
        'all_strict_final_and_separate_reasoning':all(x['status']=='PASS' for x in result['calls']),
        'all_frozen_request_digests_match':all(x['request_sha256']==p['request_sha256'] and
            x['semantic_projection_sha256']==p['semantic_projection_sha256'] for x,p in zip(result['calls'],plan['calls'])),
        'mechanical_and_escape_zero_model_calls':all(x['model_calls']==0 for x in plan['mechanical'].values()),
        'B1_neutral_both_orders':all(action('B1',o)=='HOLD' for o in ('O0','O1')),
        'B2_neutral_both_orders':all(action('B2',o)=='ADVANCE' for o in ('O0','O1')),
        'C_swap_order_stable_and_different':action('C1','O0')==action('C1','O1') and
            action('C2','O0')==action('C2','O1') and action('C1','O0')!=action('C2','O0'),
        'E_repeat_same_unseen_at_least_two':max(sum(action('E',o)==a for o in ('O0','O1','O2'))
            for a in ('ADVANCE','RETREAT'))>=2,
    }
    behavior=all(checks.values())
    latency=median(x['metrics']['wall_seconds'] for x in result['calls'])
    fast=latency<15
    classification='STAGE_B_ELIGIBLE' if behavior and fast else \
        'THINKING_DOES_NOT_FIX_POLICY' if not behavior else 'THINKING_TOO_SLOW'
    out=dict(stage='A',classification=classification,behavior_gate='PASS' if behavior else 'FAIL',
        latency_gate='PASS' if fast else 'FAIL',median_warm_action_wall_seconds=latency,
        frozen_latency_ceiling_seconds=15,checks=checks,stage_b_eligible=behavior and fast)
    _atomic_write(STUDY/'stage-a-gate.json',out)
    print(json.dumps(out,sort_keys=True),flush=True)
    return classification

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('command',choices=('prepare','run','gate'))
    p.add_argument('--private-root',type=Path)
    args=p.parse_args()
    if args.command in ('prepare','run') and args.private_root is None:p.error('--private-root required')
    {'prepare':lambda:prepare(args.private_root),'run':lambda:run(args.private_root),'gate':gate}[args.command]()
