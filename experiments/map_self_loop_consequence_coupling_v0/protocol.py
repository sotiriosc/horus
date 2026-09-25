"""Frozen eight-call matched-request protocol; no runtime architecture changes."""
from copy import deepcopy
from pathlib import Path
import json
from experiments.model_proposal_role_composition_v2.protocol import MODEL,OPTIONS,SYSTEMS
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest

ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='1b1f75650215a333498e0d7de5ba23dc9db407ec'
CAMPAIGN='HORUS_MAP_SELF_LOOP_CONSEQUENCE_COUPLING_V0'
SYSTEM=SYSTEMS['Map']
assert SYSTEM=='Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.'
MAPPINGS={'O1':{'K1':'ADVANCE','K2':'HOLD','K3':'RETREAT'},'O2':{'Q7':'ADVANCE','M4':'HOLD','Z2':'RETREAT'}}
A='A — SELF-LOOP / CONSEQUENCE COUPLING EFFECT OBSERVED'
B='B — NO MOVEMENT RESCUE OBSERVED'
C='C — NOT ESTABLISHED'


def schedule():
    out=[]
    for family,seed,conditions in [('O1',99001,('S','M')),('O2',99001,('M','S')),('O2',99002,('S','M')),('O1',99002,('M','S'))]:
        for condition in conditions:
            out.append(dict(index=len(out),family=family,mapping_index=0,mapping=MAPPINGS[family],seed=seed,condition=condition,
                history_depth=1,setup_count=1 if condition=='S' else 2,setup_actions=['HOLD'] if condition=='S' else ['HOLD','RETREAT']))
    return out


def body(d,payload):
    return dict(model=MODEL,system=SYSTEM,prompt=serialize(payload),stream=False,options={**OPTIONS['Map'],'seed':d['seed']})


def matched(left,right):
    """Require one exact wire-byte change, history[0].next_state: 1 -> 2."""
    s=json.loads(left['prompt']);m=json.loads(right['prompt'])
    assert len(s['VERIFIED_CHRONOLOGICAL_HISTORY'])==len(m['VERIFIED_CHRONOLOGICAL_HISTORY'])==1
    assert s['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['next_state']==1 and m['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['next_state']==2
    m['VERIFIED_CHRONOLOGICAL_HISTORY'][0]['next_state']=1
    normalized=deepcopy(right);normalized['prompt']=serialize(m)
    assert normalized==left and json.dumps(normalized).encode()==json.dumps(left).encode()
    a=json.dumps(left).encode();b=json.dumps(right).encode()
    diffs=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert len(a)==len(b) and len(diffs)==1 and (a[diffs[0]],b[diffs[0]])==(ord('1'),ord('2'))
    return dict(passed=True,only_path='VERIFIED_CHRONOLOGICAL_HISTORY[0].next_state',wire_bytes_different=1,S=1,M=2)


def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r


def summarize(rows,completed_calls,integrity=True,replay=False,matched_requests=True):
    conditions={condition:dict(n=sum(r['descriptor']['condition']==condition for r in rows),valid=sum(r['valid'] for r in rows if r['descriptor']['condition']==condition),
        next_state_correct=sum(r['score']['next_state'] for r in rows if r['descriptor']['condition']==condition),
        consequence_positive=sum(r['valid'] and r['parsed']['consequence']==1 for r in rows if r['descriptor']['condition']==condition),
        consequence_correct=sum(r['score']['consequence'] for r in rows if r['descriptor']['condition']==condition),
        exact=sum(r['score']['exact'] for r in rows if r['descriptor']['condition']==condition)) for condition in ('S','M')}
    pairs=[]
    for family in ('O1','O2'):
        for seed in (99001,99002):
            p=[r for r in rows if r['descriptor']['family']==family and r['descriptor']['seed']==seed]
            if len(p)!=2:continue
            x=next(r for r in p if r['descriptor']['condition']=='S');y=next(r for r in p if r['descriptor']['condition']=='M')
            cx=x['parsed']['consequence'] if x['valid'] else None;cy=y['parsed']['consequence'] if y['valid'] else None
            label=f'{cx} -> {cy}' if x['valid'] and y['valid'] and cx in (0,1) and cy in (0,1) else 'other / invalid'
            pairs.append(dict(family=family,seed=seed,S=x['parsed'],M=y['parsed'],category=label,
                improvement=x['valid'] and y['valid'] and cx!=1 and cy==1,regression=x['valid'] and y['valid'] and cx==1 and cy!=1))
    valid=sum(r['valid'] for r in rows);improve=sum(p['improvement'] for p in pairs);regress=sum(p['regression'] for p in pairs)
    complete=completed_calls==len(rows)==valid==8 and len(pairs)==4
    receipts=len(rows)==8 and all(r['authentic_post_prediction_score'] for r in rows)
    ready=complete and receipts and integrity and replay and matched_requests
    verdict=A if ready and conditions['S']['consequence_positive']<=1 and conditions['M']['consequence_positive']>=3 and improve>=2 and regress==0 else B if ready and conditions['M']['consequence_positive']<=1 else C
    return dict(study='map-self-loop-consequence-coupling-v0',parent=PARENT,classification=verdict,real_model_calls=completed_calls,
        complete_trials=len(rows),valid=valid,by_condition=conditions,pairs=pairs,improvements=improve,regressions=regress,
        matched_request_check=matched_requests,authentic_post_prediction_receipts=receipts,integrity_passed=integrity,exact_replay_passed=replay,
        Explorer_model_calls=0,Recovery_model_calls=0,registered_call_limit=8,classification_status='FINAL' if replay else 'AWAITING_EXACT_REPLAY',
        scoring_scope='Actual external simulated HOLD execution after model prediction latch, scored against its original receipt.')
