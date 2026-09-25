"""Frozen sixteen-call moving-positive transfer diagnostic; detached probes only."""
from copy import deepcopy
from pathlib import Path
import json
from experiments.map_output_schema_isolation_v0.protocol import MODEL,OPTIONS,SYSTEMS,MAPPINGS,parse
from experiments.cross_episode_initialization_boundary_v1.projection import serialize
from experiments.model_proposal_role_composition_v2_replacement_r1.durable import file_digest

ROOT=Path(__file__).resolve().parents[2];PACKAGE=Path(__file__).parent
PARENT='bf74d7eda79345efa7168ea1551de8b153b68791'
CAMPAIGN='HORUS_MAP_CONSEQUENCE_SCHEMA_TRANSFER_V0'
LIMIT=16
WORLDS={'WA':dict(state=0,action='ADVANCE',next_state=1,navigation='RETREAT',navigation_consequence=0,law_index=0),
        'WR':dict(state=3,action='RETREAT',next_state=2,navigation='ADVANCE',navigation_consequence=1,law_index=11)}
A='A — CONSEQUENCE-ONLY SCHEMA TRANSFERS TO MOVING POSITIVE RELATIONS'
B='B — NO MOVING-POSITIVE TRANSFER OBSERVED'
C='C — NOT ESTABLISHED'


def control(d):return dict(next_state=WORLDS[d['world']]['next_state'],consequence=1)


def schedule():
    blocks=[('WA','O1',99301,('J','S')),('WR','O1',99301,('S','J')),
        ('WA','O2',99301,('S','J')),('WR','O2',99301,('J','S')),
        ('WR','O2',99302,('S','J')),('WA','O2',99302,('J','S')),
        ('WR','O1',99302,('J','S')),('WA','O1',99302,('S','J'))]
    out=[]
    for world,family,seed,conditions in blocks:
        w=WORLDS[world]
        for condition in conditions:
            out.append(dict(index=len(out),world=world,state=w['state'],target_action=w['action'],family=family,mapping_index=0,
                mapping=MAPPINGS[family],seed=seed,condition=condition,history_depth=1,setup_count=2,setup_actions=[w['action'],w['navigation']]))
    return out


def body(d,payload):
    assert OPTIONS['Map']['num_predict']==32
    return dict(model=MODEL,system=SYSTEMS[d['condition']],prompt=serialize(payload),stream=False,options={**OPTIONS['Map'],'seed':d['seed']})


def matched(j,s,world):
    w=WORLDS[world]
    assert j['system']==SYSTEMS['J'] and s['system']==SYSTEMS['S']
    a=j['system'].split('. ');b=s['system'].split('. ')
    assert len(a)==len(b)==3 and a[0].encode()==b[0].encode() and a[2].encode()==b[2].encode() and a[1]!=b[1]
    assert j['prompt']==s['prompt']
    payload=json.loads(j['prompt']);history=payload['VERIFIED_CHRONOLOGICAL_HISTORY']
    assert payload['state']==w['state'] and len(history)==1
    assert (history[0]['epoch'],history[0]['transaction_id'],history[0]['next_state'],history[0]['consequence'])==(1001,1,w['next_state'],1)
    normalized=deepcopy(s);normalized['system']=j['system']
    assert normalized==j and json.dumps(normalized).encode()==json.dumps(j).encode()
    assert j['options']['num_predict']==s['options']['num_predict']==32
    return dict(passed=True,only_request_path='system.response_format_sentence',first_instruction_sentence_bytes_identical=True,
        last_instruction_sentence_bytes_identical=True,task_data_bytes_identical=True,normalized_envelope_bytes_identical=True,num_predict_both=32)


def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for n,h in r['sha256'].items():assert file_digest(ROOT/n)==h,n
    return r


def condition_counts(rows):
    return {condition:dict(n=sum(r['descriptor']['condition']==condition for r in rows),valid=sum(r['valid'] for r in rows if r['descriptor']['condition']==condition),
        next_state_correct=sum(r['score']['next_state'] is True for r in rows if r['descriptor']['condition']==condition) if condition=='J' else None,
        consequence_positive=sum(r['valid'] and r['parsed']['consequence']==1 for r in rows if r['descriptor']['condition']==condition),
        consequence_correct=sum(r['score']['consequence'] is True for r in rows if r['descriptor']['condition']==condition),
        exact=sum(r['score']['exact'] is True for r in rows if r['descriptor']['condition']==condition) if condition=='J' else None) for condition in ('J','S')}


def summarize(rows,completed_calls,integrity=True,replay=False,matched_requests=True,leak_controls=True):
    conditions=condition_counts(rows);pairs=[]
    for world in ('WA','WR'):
        for family in ('O1','O2'):
            for seed in (99301,99302):
                p=[r for r in rows if (r['descriptor']['world'],r['descriptor']['family'],r['descriptor']['seed'])==(world,family,seed)]
                if len(p)!=2:continue
                x=next(r for r in p if r['descriptor']['condition']=='J');y=next(r for r in p if r['descriptor']['condition']=='S')
                cx=x['parsed']['consequence'] if x['valid'] else None;cy=y['parsed']['consequence'] if y['valid'] else None
                category='other / invalid'
                if x['valid'] and y['valid']:
                    if (cx,cy) in ((0,1),(-1,1),(1,1),(0,0),(-1,-1)):category=f'{cx} -> {cy}'
                    elif cx==1 and cy!=1:category='+1 -> wrong'
                pairs.append(dict(world=world,family=family,seed=seed,J=x['parsed'],S=y['parsed'],category=category,
                    improvement=x['valid'] and y['valid'] and cx!=1 and cy==1,regression=x['valid'] and y['valid'] and cx==1 and cy!=1))
    valid=sum(r['valid'] for r in rows);improve=sum(p['improvement'] for p in pairs);regress=sum(p['regression'] for p in pairs)
    breakdown={key:{str(value):dict(by_condition=condition_counts([r for r in rows if r['descriptor'][key]==value]),
        improvements=sum(p['improvement'] for p in pairs if p[key]==value),regressions=sum(p['regression'] for p in pairs if p[key]==value))
        for value in values} for key,values in (('world',('WA','WR')),('family',('O1','O2')),('seed',(99301,99302)))}
    complete=completed_calls==len(rows)==valid==LIMIT and len(pairs)==8
    receipts=len(rows)==LIMIT and all(r['authentic_post_response_score'] and r['authentic_history'] and r['probe_detached'] for r in rows)
    ready=complete and receipts and integrity and replay and matched_requests and leak_controls
    per_world=all(breakdown['world'][world]['by_condition']['S']['consequence_positive']>=3 for world in WORLDS)
    verdict=A if ready and conditions['S']['consequence_positive']>=7 and conditions['J']['consequence_positive']<=4 and improve>=3 and regress==0 and per_world else B if ready and conditions['S']['consequence_positive']<=2 else C
    return dict(study='map-consequence-schema-transfer-v0',parent=PARENT,classification=verdict,real_model_calls=completed_calls,
        complete_trials=len(rows),valid=valid,by_condition=conditions,pairs=pairs,improvements=improve,regressions=regress,breakdown=breakdown,
        each_world_S_positive_at_least_three=per_world,matched_request_check=matched_requests,first_instruction_sentence_identical=matched_requests,
        authentic_post_response_receipts=receipts,future_answer_leak_controls=leak_controls,integrity_passed=integrity,exact_replay_passed=replay,
        Explorer_model_calls=0,Recovery_model_calls=0,registered_call_limit=LIMIT,classification_status='FINAL' if replay else 'AWAITING_EXACT_REPLAY',
        fixed_non_model_controls={w:control(dict(world=w)) for w in WORLDS},
        scoring_scope='Detached probes with authentic one-row target histories, scored against new original moving-positive simulated execution receipts after response and parse; ordinary non-model controls drive framework.')
