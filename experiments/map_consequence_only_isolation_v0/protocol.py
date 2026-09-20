"""Frozen eight-call detached-probe diagnostic; no framework implementation."""
from copy import deepcopy
from pathlib import Path
import json
from experiments.model_proposal_role_composition_v2.protocol import MODEL,OPTIONS,SYSTEMS as EXISTING_SYSTEMS
from experiments.model_map_proposal_v0.adapter import parse as parse_joint
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest

ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='543b4c550bdff461c88dbc77ac976df15483a8a6'
CAMPAIGN='HORUS_MAP_CONSEQUENCE_ONLY_ISOLATION_V0'
SYSTEMS={'J':EXISTING_SYSTEMS['Map'],'C':'Predict the next externally realized consequence for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.'}
assert SYSTEMS['J']=='Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.'
MAPPINGS={'O1':{'K1':'ADVANCE','K2':'HOLD','K3':'RETREAT'},'O2':{'Q7':'ADVANCE','M4':'HOLD','Z2':'RETREAT'}}
CONTROL={'next_state':1,'consequence':1}
A='A — JOINT-OUTPUT COUPLING EFFECT OBSERVED'
B='B — CONSEQUENCE-ONLY DOES NOT RESCUE SELF-LOOP FORECAST'
C='C — NOT ESTABLISHED'


def parse(raw,condition):
    if condition=='J':return parse_joint(raw)
    assert condition=='C'
    def unique(pairs):
        out={}
        for key,value in pairs:
            if key in out:raise ValueError('duplicate key')
            out[key]=value
        return out
    if type(raw) is not str:raise ValueError('response is not text')
    value=json.loads(raw,object_pairs_hook=unique)
    if type(value) is not dict or set(value)!={'consequence'}:raise ValueError('exact consequence-only schema required')
    if type(value['consequence']) is not int:raise ValueError('exact integer required')
    if value['consequence'] not in (-1,0,1):raise ValueError('consequence outside finite domain')
    return value


def schedule():
    out=[]
    for family,seed,conditions in [('O1',99101,('J','C')),('O2',99101,('C','J')),('O2',99102,('J','C')),('O1',99102,('C','J'))]:
        for condition in conditions:
            out.append(dict(index=len(out),family=family,mapping_index=0,mapping=MAPPINGS[family],seed=seed,condition=condition,
                history_depth=1,setup_count=1,setup_actions=['HOLD']))
    return out


def body(d,payload):
    assert OPTIONS['Map']['num_predict']==32
    return dict(model=MODEL,system=SYSTEMS[d['condition']],prompt=serialize(payload),stream=False,options={**OPTIONS['Map'],'seed':d['seed']})


def matched(j,c):
    assert j['system']==SYSTEMS['J'] and c['system']==SYSTEMS['C']
    assert j['prompt']==c['prompt']
    payload=json.loads(j['prompt']);history=payload['VERIFIED_CHRONOLOGICAL_HISTORY']
    assert payload['state']==1 and len(history)==1
    assert (history[0]['epoch'],history[0]['transaction_id'],history[0]['next_state'],history[0]['consequence'])==(1001,1,1,1)
    normalized=deepcopy(c);normalized['system']=j['system']
    assert normalized==j and json.dumps(normalized).encode()==json.dumps(j).encode()
    assert j['options']['num_predict']==c['options']['num_predict']==32
    return dict(passed=True,only_request_path='system',task_data_bytes_identical=True,normalized_envelope_bytes_identical=True,num_predict_both=32)


def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r


def summarize(rows,completed_calls,integrity=True,replay=False,matched_requests=True,leak_controls=True):
    conditions={condition:dict(n=sum(r['descriptor']['condition']==condition for r in rows),valid=sum(r['valid'] for r in rows if r['descriptor']['condition']==condition),
        next_state_correct=sum(r['score']['next_state'] is True for r in rows if r['descriptor']['condition']==condition) if condition=='J' else None,
        consequence_positive=sum(r['valid'] and r['parsed']['consequence']==1 for r in rows if r['descriptor']['condition']==condition),
        consequence_correct=sum(r['score']['consequence'] is True for r in rows if r['descriptor']['condition']==condition),
        exact=sum(r['score']['exact'] is True for r in rows if r['descriptor']['condition']==condition) if condition=='J' else None) for condition in ('J','C')}
    pairs=[]
    for family in ('O1','O2'):
        for seed in (99101,99102):
            p=[r for r in rows if r['descriptor']['family']==family and r['descriptor']['seed']==seed]
            if len(p)!=2:continue
            x=next(r for r in p if r['descriptor']['condition']=='J');y=next(r for r in p if r['descriptor']['condition']=='C')
            cx=x['parsed']['consequence'] if x['valid'] else None;cy=y['parsed']['consequence'] if y['valid'] else None
            label=f'{cx} -> {cy}' if x['valid'] and y['valid'] and cx in (0,1) and cy in (0,1) else 'other / invalid'
            pairs.append(dict(family=family,seed=seed,J=x['parsed'],C=y['parsed'],category=label,
                improvement=x['valid'] and y['valid'] and cx!=1 and cy==1,regression=x['valid'] and y['valid'] and cx==1 and cy!=1))
    valid=sum(r['valid'] for r in rows);improve=sum(p['improvement'] for p in pairs);regress=sum(p['regression'] for p in pairs)
    complete=completed_calls==len(rows)==valid==8 and len(pairs)==4
    receipts=len(rows)==8 and all(r['authentic_post_response_score'] and r['authentic_history'] and r['probe_detached'] for r in rows)
    ready=complete and receipts and integrity and replay and matched_requests and leak_controls
    verdict=A if ready and conditions['J']['consequence_positive']<=1 and conditions['C']['consequence_positive']>=3 and improve>=2 and regress==0 else B if ready and conditions['C']['consequence_positive']<=1 else C
    return dict(study='map-consequence-only-isolation-v0',parent=PARENT,classification=verdict,real_model_calls=completed_calls,
        complete_trials=len(rows),valid=valid,by_condition=conditions,pairs=pairs,improvements=improve,regressions=regress,
        matched_request_check=matched_requests,authentic_post_response_receipts=receipts,future_answer_leak_controls=leak_controls,
        integrity_passed=integrity,exact_replay_passed=replay,Explorer_model_calls=0,Recovery_model_calls=0,registered_call_limit=8,
        classification_status='FINAL' if replay else 'AWAITING_EXACT_REPLAY',fixed_non_model_control=CONTROL,
        scoring_scope='Detached forecast probes scored only against new original simulated HOLD receipts after response and parse; framework uses existing non-model control.')
