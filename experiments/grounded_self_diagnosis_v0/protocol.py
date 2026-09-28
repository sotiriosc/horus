"""Frozen retrospective one-call-per-run interface, with no action authority."""
from hashlib import sha256
from pathlib import Path
import json,re
from experiments.grounded_autonomous_agent_v0_2.protocol import MODEL
from experiments.grounded_authority_autonomous_agent_v0.protocol import GOAL

SOURCE=Path('research/grounded-authority-autonomous-agent-v0/public-result.json')
SOURCE_SHA256='7a6be657a46b9f23d728ebde8605fe2adfe9c5fcd5a2828b7094515a87d925b4'
ORDER=('C','A','B')
SEEDS={'C':54003,'A':54001,'B':54002}
OPTIONS=dict(temperature=0.2,top_p=0.9,top_k=40,repeat_penalty=1.1,
    num_ctx=8192,num_predict=1024)
MODEL_DIGEST='4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a'
SYSTEM=(
    'You are examining one completed trajectory of your own decisions. Use only the shown '
    'predecision grounded evidence, action choices, and authenticated outcomes. Identify '
    'a repeated decision-process pattern only if the completed record supports it. Do not '
    'assume hidden world rules, unseen action outcomes, or future events. If no defensible '
    'pattern or change is supported, say so. Keep the response short and use exactly these '
    'three headings in order: DIAGNOSIS:, PROPOSED_CHANGE:, EVIDENCE:. Under EVIDENCE, '
    'list only decision indices such as D01,D02, or NONE. Do not include receipt hashes.')


def compact_assessment(a):
    value=dict(kind=a['kind'],status=a['assessment_status'],
        relation_type=a['relation_type'],observations=a['observation_count'])
    if a['relation_type']=='DETERMINISTIC':
        if a['established_value'] is not None:value['established_value']=a['established_value']
        if a['candidate_value'] is not None:
            value['candidate_value']=a['candidate_value'];value['candidate_count']=a['candidate_count']
    else:
        if a.get('segment_counts'):value['segment_counts']=a['segment_counts']
        if a.get('empirical_frequencies'):value['empirical_frequencies']=a['empirical_frequencies']
        if a.get('recent_window'):value['recent_window']=a['recent_window']
        if a.get('possible_change'):
            p=a['possible_change']
            value['possible_change']={k:p[k] for k in ('challenger','candidate_start','prior_counts','recent_counts') if k in p}
    return value


def build_inputs(source_path=SOURCE):
    if sha256(source_path.read_bytes()).hexdigest()!=SOURCE_SHA256:
        raise RuntimeError('frozen sanitized source mismatch')
    source=json.loads(source_path.read_text())
    if source['behavioral_campaign_status']!='VALID':raise RuntimeError('source campaign invalid')
    result={}
    for run in ORDER:
        decisions=source['runs'][run]['decisions']
        if len(decisions)!=30:raise RuntimeError('source run incomplete')
        rows=[]
        for index,d in enumerate(decisions,1):
            if d['index']!=index or d['run']!=run:raise RuntimeError('source decision mismatch')
            rows.append(dict(decision_index=f'D{index:02d}',world_state=d['state'],
                action_assessments={a:compact_assessment(v) for a,v in d['grounded_assessments_before'].items()},
                admissible_actions=d['admissible_actions'],decision_source=d['decision_source'],
                selected_action=d['selected_action'],model_called=d['action_call_id'] is not None,
                authenticated_consequence=d['realized']['consequence'],
                resulting_state=d['realized']['next_state']))
        result[run]=dict(goal=GOAL,completed_decisions=rows)
    return result


def parse_response(raw):
    # Plain-text headings tolerate whitespace/Markdown, but no inferred missing fields.
    headings=list(re.finditer(r'(?im)^\s*(?:\*\*)?(DIAGNOSIS|PROPOSED_CHANGE|EVIDENCE):(?:\*\*)?\s*',raw))
    if [m.group(1).upper() for m in headings]!=['DIAGNOSIS','PROPOSED_CHANGE','EVIDENCE']:
        return None,'INVALID_RESPONSE_FORMAT'
    values={}
    for i,m in enumerate(headings):
        content=raw[m.end():(headings[i+1].start() if i+1<len(headings) else len(raw))].strip()
        content=content.strip('* \t\r\n')
        if not content:return None,'INVALID_RESPONSE_FORMAT'
        values[m.group(1).upper()]=content
    evidence=values['EVIDENCE'].strip()
    if evidence.upper()=='NONE':indices=[]
    else:
        tokens=[x for x in re.split(r'[\s,;]+',evidence) if x]
        if not tokens or not all(re.fullmatch(r'D(?:0[1-9]|[12][0-9]|30)',x.upper()) for x in tokens):
            return None,'INVALID_RESPONSE_FORMAT'
        indices=[x.upper() for x in tokens]
        if len(indices)!=len(set(indices)):return None,'INVALID_RESPONSE_FORMAT'
    values['EVIDENCE']=indices
    if values['DIAGNOSIS'].upper()=='NO_PATTERN_FOUND' and (indices or values['PROPOSED_CHANGE'].upper()!='NO_CHANGE'):
        return None,'INVALID_RESPONSE_FORMAT'
    return values,'VALID_RESPONSE'
