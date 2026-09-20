"""Frozen Map-only scope; all proposer and authority interfaces inherited."""
from pathlib import Path
import json
from experiments.model_proposal_role_composition_v2.protocol import MODEL, OPTIONS, SYSTEMS
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).parent
PARENT='bf26f6a65ac844676e6c35da2a4ed782b71de8f7'
CAMPAIGN='HORUS_MAP_POSITIVE_EVIDENCE_DEPTH_V0'
SYSTEM=SYSTEMS['Map']
assert SYSTEM=='Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.'
MAPPINGS={'O1':{'K1':'ADVANCE','K2':'HOLD','K3':'RETREAT'},'O2':{'Q7':'ADVANCE','M4':'HOLD','Z2':'RETREAT'}}
A='A — POSITIVE-EVIDENCE DEPTH SENSITIVITY OBSERVED'
B='B — NO DEPTH RESCUE OBSERVED'
C='C — NOT ESTABLISHED'


def schedule():
    out=[]
    for family,seed,depths in [('O1',98001,(1,2)),('O2',98001,(2,1)),('O2',98002,(1,2)),('O1',98002,(2,1))]:
        for depth in depths:
            out.append(dict(index=len(out),family=family,mapping_index=0,mapping=MAPPINGS[family],seed=seed,depth=depth,condition=f'D{depth}'))
    return out


def body(d,payload):
    return dict(model=MODEL,system=SYSTEM,prompt=serialize(payload),stream=False,options={**OPTIONS['Map'],'seed':d['seed']})


def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r


def summarize(rows,completed_calls,integrity=True,replay=False):
    by_depth={f'D{d}':dict(n=sum(r['descriptor']['depth']==d for r in rows),valid=sum(r['valid'] for r in rows if r['descriptor']['depth']==d),
        next_state_correct=sum(r['score']['next_state'] for r in rows if r['descriptor']['depth']==d),
        consequence_correct=sum(r['score']['consequence'] for r in rows if r['descriptor']['depth']==d),
        exact=sum(r['score']['exact'] for r in rows if r['descriptor']['depth']==d)) for d in (1,2)}
    pairs=[]
    for family in ('O1','O2'):
        for seed in (98001,98002):
            p=[r for r in rows if r['descriptor']['family']==family and r['descriptor']['seed']==seed]
            if len(p)!=2:continue
            x=next(r for r in p if r['descriptor']['depth']==1);y=next(r for r in p if r['descriptor']['depth']==2)
            cx=x['parsed']['consequence'] if x['valid'] else None;cy=y['parsed']['consequence'] if y['valid'] else None
            label=f'{cx} -> {cy}' if x['valid'] and y['valid'] and cx in (0,1) and cy in (0,1) else 'other / invalid'
            pairs.append(dict(family=family,seed=seed,D1=x['parsed'],D2=y['parsed'],category=label,
                improvement=x['valid'] and y['valid'] and not x['score']['exact'] and y['score']['exact'],
                regression=x['valid'] and y['valid'] and x['score']['exact'] and not y['score']['exact']))
    valid=sum(r['valid'] for r in rows);improve=sum(p['improvement'] for p in pairs);regress=sum(p['regression'] for p in pairs)
    complete=completed_calls==len(rows)==valid==8 and len(pairs)==4
    receipts=all(r['authentic_post_prediction_score'] for r in rows) and len(rows)==8
    ready=complete and receipts and integrity and replay
    verdict=A if ready and by_depth['D2']['exact']>=3 and improve>=2 and regress==0 else B if ready and by_depth['D2']['exact']<=1 else C
    return dict(study='map-positive-evidence-depth-v0',parent=PARENT,classification=verdict,real_model_calls=completed_calls,
        complete_trials=len(rows),valid=valid,by_depth=by_depth,pairs=pairs,improvements=improve,regressions=regress,
        authentic_post_prediction_receipts=receipts,integrity_passed=integrity,exact_replay_passed=replay,
        Explorer_model_calls=0,Recovery_model_calls=0,registered_call_limit=8,
        classification_status='FINAL' if replay else 'AWAITING_EXACT_REPLAY',
        scoring_scope='Actual external simulated HOLD execution after model prediction latch, scored against its original receipt.')
