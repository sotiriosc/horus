"""Bounded post-campaign diagnostic; never enters action, receipt or Memory paths."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json
import re
import time

from horus.live import _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import canonical, file_hash
from experiments.grounded_autonomous_agent_v0.protocol import OPTIONS
from experiments.grounded_autonomous_agent_v0_2.protocol import MODEL
from .shared import STUDY, Q_URL, MODEL_SHA256, verify_q_model, verify_sources

SYSTEM = ('You are a non-authoritative retrospective analyst. Review only the 30 '
          'completed decisions and authenticated consequences supplied. Do not infer hidden '
          'world regimes, outcomes of unchosen actions, or future events. Do not change '
          'policy, prompts, Memory, or later decisions. Return a concise JSON object with '
          'PATTERN, DIAGNOSIS, POSSIBLE_CHANGE, and EVIDENCE_DECISIONS. Cite exact '
          'decision IDs. If no defensible change is supported, set POSSIBLE_CHANGE to '
          'NO_CHANGE_PROPOSED. Distinguish observed bad choices from insufficient evidence.')
FIELDS = ('PATTERN','DIAGNOSIS','POSSIBLE_CHANGE','EVIDENCE_DECISIONS')


def projected_assessment(x):
    return dict(kind=x['kind'], relation_type=x['relation_type'],
        assessment_status=x['assessment_status'],
        established_value=x.get('established_value'),
        candidate_value=x.get('candidate_value'),
        empirical_frequencies=x.get('empirical_frequencies'))


def prepare():
    verify_sources()
    results=json.loads((STUDY/'stage-b-public.json').read_text())
    if results['campaign_integrity']!='PASS':raise RuntimeError('campaign integrity gate')
    inputs={}
    for name,run in results['runs'].items():
        rows=run['decisions']
        if len(rows)!=30:raise RuntimeError('incomplete trajectory')
        items=[dict(decision_id=d['decision_id'],state=d['state'],
            assessments={a:projected_assessment(x) for a,x in d['assessments'].items()},
            admissible_actions=d['admissible_actions'],selected_action=d['action'],
            decision_source=d['decision_source'],
            authenticated_consequence=d['consequence'],next_state=d['next_state'],
            grounded_change=d['grounded_change']) for d in rows]
        inputs[name]=dict(trajectory=name,completed_decisions=items)
    _atomic_write(STUDY/'retrospective-inputs.json',inputs)
    return inputs


def call(private,model_arm,trajectory):
    if model_arm not in ('D','Q') or trajectory not in [f'{a}{i}' for a in 'DQ' for i in (1,2,3)]:
        raise ValueError('invalid review arm/trajectory')
    verify_sources()
    inputs=json.loads((STUDY/'retrospective-inputs.json').read_text())
    prompt=canonical(inputs[trajectory])
    path=private/'reviews'/f'{model_arm}-on-{trajectory}'
    if path.exists():raise RuntimeError('review already attempted; no retries')
    path.mkdir(parents=True)
    if model_arm=='Q':
        verify_q_model()
        request=dict(messages=[dict(role='system',content=SYSTEM),dict(role='user',content=prompt)],
            temperature=.2,top_p=.9,top_k=40,seed=3303+int(trajectory[1:]),
            max_tokens=1024,stream=False,cache_prompt=False,
            chat_template_kwargs={'enable_thinking':False},
            response_format={'type':'json_object'})
        url=Q_URL+'/v1/chat/completions'
    else:
        request=dict(model=MODEL,system=SYSTEM,prompt=prompt,stream=False,format='json',
            options={**OPTIONS,'num_ctx':8192,'num_predict':1024,
                     'seed':3303+int(trajectory[1:])})
        url='http://127.0.0.1:11434/api/generate'
    wire=json.dumps(request,separators=(',',':')).encode()
    _atomic_write(path/'intent.private.json',dict(url=url,request=request,
        request_sha256=sha256(wire).hexdigest(),prompt_sha256=sha256(prompt.encode()).hexdigest(),
        trajectory=trajectory,model_arm=model_arm,timeout_seconds=900))
    started=time.perf_counter();response=None;error=None
    try:
        with urlopen(Request(url,data=wire,headers={'Content-Type':'application/json'}),
                     timeout=900) as stream:
            response=json.load(stream)
    except Exception as exc:
        error=type(exc).__name__+': '+str(exc)
    wall=time.perf_counter()-started
    raw=None
    if response is not None:
        try:raw=(response['response'] if model_arm=='D' else response['choices'][0]['message']['content'])
        except (KeyError,IndexError,TypeError):pass
    try:parsed=json.loads(raw) if isinstance(raw,str) else None
    except json.JSONDecodeError:parsed=None
    complete=(isinstance(parsed,dict) and set(parsed)==set(FIELDS)
        and all(isinstance(parsed[k],str) and parsed[k].strip() for k in FIELDS[:3])
        and isinstance(parsed['EVIDENCE_DECISIONS'],list)
        and all(isinstance(x,str) for x in parsed['EVIDENCE_DECISIONS']))
    known={d['decision_id'] for d in inputs[trajectory]['completed_decisions']}
    citations=parsed['EVIDENCE_DECISIONS'] if complete else []
    public=dict(model_arm=model_arm,trajectory=trajectory,complete=complete,
        transport_error=error,wall_seconds=wall,
        request_sha256=sha256(wire).hexdigest(),prompt_sha256=sha256(prompt.encode()).hexdigest(),
        raw_response_sha256=sha256((raw or '').encode()).hexdigest() if raw is not None else None,
        citations=citations,citations_all_in_trajectory=all(c in known for c in citations),
        citation_count=len(citations),parsed_output=parsed if complete else None,
        input_tokens=(response.get('prompt_eval_count') if model_arm=='D' else
                      (response.get('usage') or {}).get('prompt_tokens')) if response else None,
        output_tokens=(response.get('eval_count') if model_arm=='D' else
                       (response.get('usage') or {}).get('completion_tokens')) if response else None,
        timeout_censored=bool(error and ('timed out' in error.lower() or 'timeout' in error.lower())))
    _atomic_write(path/'response.private.json',dict(response=response,error=error,raw_output=raw,
        wall_seconds=wall,public=public))
    _atomic_write(STUDY/f'retrospective-{model_arm}-on-{trajectory}.json',public)
    return public


def main():
    p=ArgumentParser();p.add_argument('mode',choices=('prepare','call'))
    p.add_argument('--model-arm',choices=('D','Q'));p.add_argument('--trajectory')
    p.add_argument('--private-root',type=Path)
    a=p.parse_args()
    if a.mode=='prepare':print(json.dumps({k:len(v['completed_decisions']) for k,v in prepare().items()}))
    else:
        if not (a.model_arm and a.trajectory and a.private_root):raise ValueError('call arguments missing')
        print(json.dumps(call(a.private_root,a.model_arm,a.trajectory),sort_keys=True),flush=True)

if __name__=='__main__':main()
