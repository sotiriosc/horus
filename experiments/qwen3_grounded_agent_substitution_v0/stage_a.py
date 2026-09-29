"""Frozen Stage A contexts and model-authority boundary audit."""
from argparse import ArgumentParser
from pathlib import Path
import json

from horus.live import SessionStore, ModelClient
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, canonical
from experiments.grounded_autonomous_agent_v0_2.worker import all_assessments
from experiments.grounded_authority_autonomous_agent_v0.protocol import GOAL, ACTIONS, select_route
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as base
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as frozen
from grounded_agent.policy import promoted_decide
from grounded_state import AuthenticatedMemory
from .shared import STUDY, sha, verify_sources, verify_q_model, q_action

FIXTURES = ('A', 'B1', 'B2', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H')
MECHANICAL = {'A', 'F', 'G'}


def projection(state, assessments, index=1, history=None):
    route = select_route(assessments)
    return dict(goal=GOAL, decision_id=f'C:D{index:02d}', decision_index=index,
        current_state=state, available_actions=route['candidates'],
        grounded_assessments=frozen.semantic_assessments(assessments),
        recent_agent_working_context=history or []), route


def signed_g(path):
    with SessionStore(path/'session', False) as store, ModernMemory(path/'memory.sqlite3', True) as memory:
        store.save(state=0, next_transaction_id=1)
        base.execute(store, memory, 'E1', 'S', 0, 'HOLD', 'REGISTERED_SETUP', setup=True)
        for index in (1, 2, 3):
            ctx = frozen.context(store, memory, index)
            if ctx['route']['route'] != 'MODEL':
                raise RuntimeError('G setup not mixed model route')
            info = dict(call_id=f'FIXTURE:{index}', raw_output_sha256=None,
                        context_tokens=0, output_tokens=0, latency_seconds=0, status='VALID')
            base.execute(store, memory, 'E1', 'S', index, 'HOLD', 'SAFE_GROUNDED_FALLBACK',
                ctx['route'], info, ctx['assessments'], counter_before=ctx['suffix']['count'])
        ctx = frozen.context(store, memory, 4)
        if ctx['suffix'] != {'count': 3, 'relation': [0, 'HOLD']}:
            raise RuntimeError('G signed suffix not exactly three')
        return ctx['projection'], ctx['route']


def signed_h(path):
    with SessionStore(path/'session', False) as store, ModernMemory(path/'memory.sqlite3', True) as memory:
        store.save(state=1, next_transaction_id=1)
        base.execute(store, memory, 'H', 'SETUP', 0, 'HOLD', 'REGISTERED_SETUP', setup=True)
        if store.checkpoint['current_state'] != 1:
            raise RuntimeError('H registered state-1 empirical setup did not self-loop')
        assessments = all_assessments(AuthenticatedMemory(store, memory), 1)
        hold = assessments['HOLD']
        if hold['relation_type'] != 'EMPIRICAL' or hold['kind'] == 'UNSEEN':
            raise RuntimeError('H empirical relation not observed')
        return projection(1, assessments)


def build(private):
    verify_sources()
    out = STUDY/'stage-a-fixtures.json'
    if out.exists() or private.exists():
        raise RuntimeError('Stage A fixture target already exists')
    private.mkdir(parents=True)
    frozen.configure()
    sensitivity = json.loads((Path('research/grounded-action-sensitivity-v0/contexts.json')).read_text())
    authority = json.loads((Path('research/grounded-authority-autonomous-agent-v0/public-result.json')).read_text())
    result = {}
    for name, source in [('A','A1'),('B1','B1'),('B2','B2'),('C1','C1'),('C2','C2'),('F','A2')]:
        row = sensitivity['contexts'][source]
        view, route = projection(row['current_state'], row['grounded_assessments'])
        result[name] = dict(source='sensitivity:'+source, projection=view, route=route,
                            semantic_projection_sha256=digest(view))
    for name, run, index in [('D','A',1),('E','C',5)]:
        rows = authority['runs'][run]['decisions']
        row = rows[index-1]
        history = [dict(decision_id=x['decision_id'], state=x['state'],
                        action=x['selected_action'], authenticated_consequence=x['realized']['consequence'],
                        source=x['decision_source']) for x in rows[max(0,index-4):index-1]]
        view, route = projection(row['state'], row['grounded_assessments_before'], index, history)
        if route['candidates'] != row['admissible_actions']:
            raise RuntimeError('public authority fixture candidate drift')
        result[name] = dict(source=f'authority:{run}:D{index:02d}', projection=view,
                            route=route, semantic_projection_sha256=digest(view))
    for name, builder in [('G',signed_g),('H',signed_h)]:
        views=[]
        for arm in ('D','Q'):
            path=private/'signed'/name/arm
            path.mkdir(parents=True)
            view,route=builder(path)
            views.append((view,route))
        if digest(views[0][0]) != digest(views[1][0]):
            raise RuntimeError(name+' independent signed projections differ semantically')
        view,route=views[0]
        result[name]=dict(source='fresh-independent-authenticated-setup', projection=view,
                          route=route, semantic_projection_sha256=digest(view))
    if set(result)!=set(FIXTURES):
        raise RuntimeError('fixture set changed')
    result={name:result[name] for name in FIXTURES}
    for name,item in result.items():
        expected='MECHANICAL' if name in ('A','F') else 'MODEL'
        if name=='G':expected='MODEL'  # escape has independent precedence over this route.
        if item['route']['route']!=expected:
            raise RuntimeError(name+' registered route drift')
    out.write_text(json.dumps(dict(preregistration_commit='33670789ab58422271a12c6569204319857516ef',
        source_manifest_sha256=sha((STUDY/'source-manifest.json').read_bytes()),
        fixtures=result, status='FROZEN_BEFORE_INFERENCE'),indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(status='FROZEN_BEFORE_INFERENCE',fixtures=list(result),
                          digests={k:v['semantic_projection_sha256'] for k,v in result.items()})))


def g_decision(private, arm):
    frozen.configure()
    path=private/'signed'/'G'/arm
    with SessionStore(path/'session', True) as store, ModernMemory(path/'memory.sqlite3', False) as memory:
        before=len(store.records['calls'])
        action,source,route,info,assessments,suffix=promoted_decide(store,memory,object(),4)
        if (action,source,route['route'],info['status'],suffix['count']) != (
                'ADVANCE','STAGNATION_ESCAPE','ESCAPE','NOT_CALLED',3):
            raise RuntimeError('G promoted escape boundary failed')
        new=store.records['calls'][before:]
        if len(new)!=1 or new[0]['kind']!='ACTION_FROZEN' or info['call_id'] is not None:
            raise RuntimeError('G made a model call')
        base.execute(store,memory,'E1','S',4,action,source,route,info,assessments,
                     counter_before=suffix['count'])
        if frozen.qualifying_suffix(store,memory)['count']!=0:
            raise RuntimeError('G one-shot suffix failed to reset')
        return dict(action=action,source=source,model_calls=0,action_parse_status='NOT_CALLED',
                    signed_execution=True,post_escape_suffix=0)


def model_decision(private, name, arm, fixture):
    path=private/'model-calls'/arm/name
    path.mkdir(parents=True)
    ctx=dict(state=fixture['projection']['current_state'],route=fixture['route'],
        assessments=fixture['projection']['grounded_assessments'],
        projection=fixture['projection'],suffix=dict(count=0,relation=None))
    with SessionStore(path/'session',False) as store:
        index=fixture['projection']['decision_index']
        if arm=='D':
            action,source,route,info,_,_=frozen.canonical_action_decision(store,ModelClient(),index,ctx)
        else:
            action,source,route,info,_,_=q_action(store,index,ctx)
        return dict(action=action,source=source,model_calls=1,
            action_parse_status=info['status'],allowed=route['candidates'],
            input_tokens=info['context_tokens'],output_tokens=info['output_tokens'],
            wall_seconds=info['latency_seconds'],raw_output_sha256=info['raw_output_sha256'],
            request_sha256=info['request_sha256'],
            prompt_eval_seconds=info.get('prompt_eval_duration_seconds'),
            generation_seconds=info.get('generation_duration_seconds'))


def run_arm(private, arm):
    if arm not in ('D','Q'):raise ValueError('invalid arm')
    verify_sources()
    if arm=='Q':verify_q_model()
    fixtures=json.loads((STUDY/'stage-a-fixtures.json').read_text())['fixtures']
    out=STUDY/f'stage-a-{arm.lower()}-results.json'
    if out.exists():raise RuntimeError('refusing to overwrite Stage A arm result')
    result=dict(arm=arm,status='RUNNING',decisions={})
    for name in FIXTURES:
        fixture=fixtures[name];route=fixture['route']
        if name=='G':
            item=g_decision(private,arm)
        elif route['route']=='MECHANICAL':
            item=dict(action=route['action'],source=route['source'],model_calls=0,
                      action_parse_status='NOT_CALLED',allowed=route['candidates'])
        else:
            item=model_decision(private,name,arm,fixture)
        item['semantic_projection_sha256']=fixture['semantic_projection_sha256']
        item['route']=('ESCAPE' if name=='G' else route['route'])
        if item['action'] not in route['candidates'] and name!='G':
            raise RuntimeError('Stage A action outside route')
        result['decisions'][name]=item
        out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(arm=arm,case=name,action=item['action'],source=item['source'],
                              calls=item['model_calls'])),flush=True)
    result['status']='COMPLETE'
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')


def gate():
    fixtures=json.loads((STUDY/'stage-a-fixtures.json').read_text())['fixtures']
    arms={arm:json.loads((STUDY/f'stage-a-{arm.lower()}-results.json').read_text()) for arm in ('D','Q')}
    checks={}
    for arm,record in arms.items():
        checks[arm]={}
        if record['status']!='COMPLETE':raise RuntimeError(arm+' incomplete')
        for name,item in record['decisions'].items():
            f=fixtures[name]
            expected_calls=0 if name in MECHANICAL else 1
            checks[arm][name]=bool(item['model_calls']==expected_calls and
                item['semantic_projection_sha256']==f['semantic_projection_sha256'] and
                (name=='G' or item['action'] in f['route']['candidates']) and
                (expected_calls==0 or item['action_parse_status']=='VALID') and
                (name!='G' or item['post_escape_suffix']==0))
    passed=all(all(x.values()) for x in checks.values())
    out=dict(stage='A',status='PASS' if passed else 'FAIL',checks=checks,
             model_calls_per_arm=sum(name not in MECHANICAL for name in FIXTURES),
             stage_b_authorized_by_preregistration=passed)
    (STUDY/'stage-a-gate.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out))
    if not passed:raise RuntimeError('Stage A gate failed')


def main():
    p=ArgumentParser();p.add_argument('command',choices=('prepare','run-d','run-q','gate'))
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args()
    {'prepare':lambda:build(a.private_root),'run-d':lambda:run_arm(a.private_root,'D'),
     'run-q':lambda:run_arm(a.private_root,'Q'),'gate':gate}[a.command]()

if __name__=='__main__':main()
