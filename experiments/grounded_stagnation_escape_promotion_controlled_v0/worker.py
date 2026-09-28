"""Pair stochastic draws on an arm-neutral, receipt-verified decision view."""
from argparse import ArgumentParser
from hashlib import sha256
from pathlib import Path
import json
from horus.live import SessionStore,ModelClient,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory,canonical
from experiments.grounded_autonomous_agent_v0_2.worker import all_assessments,rows_of,parse_action
from experiments.grounded_authority_autonomous_agent_v0.worker import call_model,decision_history
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    MODEL,GOAL,ACTION_SYSTEM,ACTION_OPTIONS,ACTION_FORMAT,RUNS,select_route,source_for_model_choice)
from grounded_state import AuthenticatedMemory
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as base
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import escape_choice,qualifying_suffix,SOURCE

STUDY='GROUNDED_STAGNATION_ESCAPE_PROMOTION_CONTROLLED_V0'
ELIGIBLE={'E1':7,'E2':8,'E3':9,'E4':10}
CONTROLS={'N1':2,'N2':2,'N3':2,'N4':4,'N5':3,'N6':6}
SETUPS={
 'E1':(0,('HOLD',)),'E2':(1,('ADVANCE',)),'E3':(2,('RETREAT',)),
 'E4':(3,('ADVANCE','HOLD')),
 'N1':(2,('RETREAT',)),'N2':(1,('ADVANCE','HOLD','RETREAT')),
 'N3':(0,('ADVANCE','HOLD','HOLD','RETREAT')),'N4':(2,('HOLD',)),
 'N5':(0,('ADVANCE',)),'N6':(3,('ADVANCE','RETREAT')),
}

def override(case,state,action,visit,index):
    if case=='E1' and state==0:
        if action=='HOLD':return 0,0
        if action=='ADVANCE':return 0,1
    if case=='E2' and state==1:
        if action=='ADVANCE':return 1,0
        if action=='HOLD':return 1,-1
    if case=='E3' and state==2:
        if action in ('RETREAT','ADVANCE'):return 2,0
    if case=='E4' and state==3:
        if action=='ADVANCE':return 3,-1
        if action=='HOLD':return 3,0
        if action=='RETREAT':return 3,1
    if case=='N1' and state==2 and action=='RETREAT':return 2,1
    if case=='N2' and state==1:
        return 1,0 if action=='HOLD' else -1
    if case=='N3' and state==0:
        if action=='ADVANCE':return 0,0
        if action=='HOLD':return 0,1 if visit==1 else -1
        if action=='RETREAT':return 0,-1
    if case=='N4' and state==2 and action=='HOLD':return 2,0
    if case=='N5' and state==0 and action=='ADVANCE':return (0 if index==0 else 1),0
    if case=='N6':
        if state==3 and action=='ADVANCE':return 2,0
        if state==2 and action=='RETREAT':return 3,0
    return None

def configure():
    base.scenario_override=override
    base.STUDY=STUDY

def signed_projection(store):
    projection=[]
    for e in store.records['events']:
        record=e['record'];receipt=record['receipt']
        if record['authorization_status']!='AUTHORIZED' or digest(receipt)!=record['receipt_provenance_sha256']:
            raise RuntimeError('unauthenticated event in matched history')
        projection.append(dict(kind=record['execution_kind'],decision_index=record['decision_index'],
            pre_state=receipt['pre_state'],action=receipt['action'],
            next_state=receipt['next_state'],consequence=receipt['realized_consequence'],
            authorization_status=record['authorization_status']))
    return projection

def semantic_assessments(assessments):
    """Remove only opaque receipt references; preserve every policy field."""
    return {action:{key:value for key,value in assessment.items()
            if key!='recent_receipt_provenance'}
            for action,assessment in assessments.items()}

def raw_provenance(store,memory):
    return digest(dict(events=[dict(receipt_identity=e['record']['receipt_identity'],
        receipt_sha256=e['record']['receipt_provenance_sha256'],
        source_scope=e['record']['source_scope']) for e in store.records['events']],
        memory_rows=memory.rows()))

def decision_projection(store,index,state,assessments,route):
    return dict(goal=GOAL,decision_id=f'C:D{index:02d}',decision_index=index,
        current_state=state,available_actions=route['candidates'],
        grounded_assessments=semantic_assessments(assessments),
        recent_agent_working_context=decision_history(store,1))

def request_for(projection):
    request=dict(model=MODEL,system=ACTION_SYSTEM,prompt=canonical(projection),stream=False,
        format=ACTION_FORMAT,options={**ACTION_OPTIONS,'seed':RUNS['C']+projection['decision_index']})
    wire=json.dumps(request).encode()
    return dict(wire=wire,canonical_sha256=digest(request),
        wire_sha256=sha256(wire).hexdigest(),request=request)

def context(store,memory,index):
    memory.reconcile(store)
    state=store.checkpoint['current_state']
    assessments=all_assessments(AuthenticatedMemory(store,memory),state)
    route=select_route(assessments)
    projection=decision_projection(store,index,state,assessments,route)
    request=request_for(projection)
    return dict(state=state,history=signed_projection(store),assessments=assessments,
        semantic_assessments=semantic_assessments(assessments),
        candidate_set=route['candidates'],route=route,request=request,
        projection=projection,projection_sha256=digest(projection),
        raw_provenance_sha256=raw_provenance(store,memory),
        suffix=qualifying_suffix(store,memory))

def same_context(a,b):
    checks=dict(state=a['state']==b['state'],
        authenticated_history_projection=a['history']==b['history'],
        semantic_projection_sha256=a['projection_sha256']==b['projection_sha256'],
        candidate_set=a['candidate_set']==b['candidate_set'])
    return all(checks.values()),checks

def verify_actual_request(store,call_id,planned):
    intents=[e['record'] for e in store.records['calls'] if e['kind']=='REQUEST_INTENT' and e['record']['call_id']==call_id]
    attempts=[e['record'] for e in store.records['calls'] if e['kind']=='TRANSPORT_ATTEMPT_INTENT' and e['record']['call_id']==call_id]
    if (len(intents)!=1 or len(attempts)!=1 or
        intents[0]['request_sha256']!=planned['canonical_sha256'] or
        attempts[0]['request_bytes_sha256']!=planned['wire_sha256'] or
        attempts[0]['request_bytes_utf8'].encode()!=planned['wire']):
        raise RuntimeError('actual model request differs from preregistered matched context')

def canonical_action_decision(store,client,index,ctx):
    route=ctx['route'];state=ctx['state']
    if route['route']=='MECHANICAL':
        action=route['action']
        info=dict(call_id=None,raw_output_sha256=None,request_sha256=None,
            context_tokens=0,output_tokens=0,latency_seconds=0,status='NOT_CALLED')
    else:
        info=call_model(store,client,'C',index,'ACTION',ACTION_SYSTEM,
            ctx['projection'],ACTION_OPTIONS,ACTION_FORMAT)
        if info['transport_error'] is not None:
            raise RuntimeError('action transport failure: '+str(info['transport_error']))
        try:
            action=parse_action(info['raw'])['selected_action']
            if action not in route['candidates']:
                raise ValueError('action outside admissible candidates')
            status='VALID'
        except (ValueError,TypeError) as exc:
            action=None;status='INVALID';info['parse_error']=repr(exc)
        info['status']=status
        store.append('calls','PARSED',dict(call_id=info['call_id'],role='ACTION',
            status=status,selected_action=action,error=info.get('parse_error'),
            raw_output_sha256=info['raw_output_sha256']))
        store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
        if status!='VALID':raise RuntimeError('invalid authoritative action: '+info['parse_error'])
    source=(route['source'] if route['route']=='MECHANICAL'
            else source_for_model_choice(route,ctx['assessments'],action))
    store.append('calls','ACTION_FROZEN',dict(decision_id=f'C:D{index:02d}',
        selected_action=action,decision_source=source,action_call_id=info['call_id'],
        raw_output_sha256=info['raw_output_sha256']))
    store.save(state=state,next_transaction_id=store.checkpoint['next_transaction_id'])
    return action,source,route,info,ctx['assessments'],ctx['suffix']

def frozen_decide(store,memory,client,case,arm,index,ctx):
    if arm=='S':
        action,_=escape_choice(store,memory,ctx['state'],ctx['assessments'])
        if action is not None:
            return base.decide(store,memory,client,case,arm,index,1)
    return canonical_action_decision(store,client,index,ctx)

def model_response_hash(store,call_id):
    matches=[e['record']['response'] for e in store.records['calls']
        if e['kind']=='TRANSPORT_ATTEMPT_RESULT' and e['record']['call_id']==call_id]
    if len(matches)!=1:raise RuntimeError('model response cardinality mismatch')
    return digest(matches[0])

def freeze_reference(store,index,action,source,info,request,response_sha):
    record=dict(decision_id=f'C:D{index:02d}',draw_kind='SHARED_MATCHED_MODEL_DRAW',
        selected_action=action,source_request_sha256=request['canonical_sha256'],
        source_wire_sha256=request['wire_sha256'],source_shared_response_sha256=response_sha,
            response_sha256=response_sha,
        source_raw_output_sha256=info['raw_output_sha256'])
    store.append('calls','SHARED_MATCHED_MODEL_DRAW',record)
    store.append('calls','ACTION_FROZEN',dict(decision_id=f'C:D{index:02d}',
        selected_action=action,decision_source=source,action_call_id=None,
        raw_output_sha256=info['raw_output_sha256']))
    store.save(state=store.checkpoint['current_state'],
        next_transaction_id=store.checkpoint['next_transaction_id'])
    return dict(call_id=None,raw_output_sha256=info['raw_output_sha256'],
        request_sha256=request['canonical_sha256'],context_tokens=0,output_tokens=0,
        latency_seconds=0,status='VALID')

def prepare(root):
    configure();root.mkdir(parents=True,exist_ok=False)
    for case,(state,actions) in SETUPS.items():
        seed=root/'seeds'/case
        seed.mkdir(parents=True,exist_ok=False)
        with SessionStore(seed/'session',False) as store,ModernMemory(seed/'memory.sqlite3',True):
            store.save(state=state,next_transaction_id=1)
        for arm in ('I','S'):
            path=root/'cases'/case/arm
            base.copy_arm(seed,path)
            with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
                for action in actions:
                    base.execute(store,memory,case,arm,0,action,'REGISTERED_SETUP',setup=True)
        print(json.dumps(dict(case=case,setup_actions=list(actions),independent_setup_receipts=True)),flush=True)

def step(root,case,index):
    configure()
    paths={arm:root/'cases'/case/arm for arm in ('I','S')}
    with SessionStore(paths['I']/'session',True) as i,SessionStore(paths['S']/'session',True) as s,\
        ModernMemory(paths['I']/'memory.sqlite3',False) as im,ModernMemory(paths['S']/'memory.sqlite3',False) as sm:
        for store in (i,s):
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=index-1:
                raise RuntimeError('paired decision index mismatch')
        ic=context(i,im,index);sc=context(s,sm,index)
        matched,checks=same_context(ic,sc)
        escape,observed_suffix=escape_choice(s,sm,sc['state'],sc['assessments'])
        if observed_suffix!=sc['suffix']:raise RuntimeError('candidate suffix changed during check')
        client=ModelClient();I=S=None;shared=False;response_sha=None;draw_source={}
        if matched and escape is None and ic['route']['route']=='MODEL':
            action,source,route,info,_,_=canonical_action_decision(i,client,index,ic)
            verify_actual_request(i,info['call_id'],ic['request'])
            response_sha=model_response_hash(i,info['call_id'])
            ssource=source_for_model_choice(sc['route'],sc['assessments'],action)
            sinfo=freeze_reference(s,index,action,ssource,info,sc['request'],response_sha)
            I=(action,source,route,info,ic['assessments'],ic['suffix'])
            S=(action,ssource,sc['route'],sinfo,sc['assessments'],sc['suffix'])
            shared=True;draw_source=dict(I='SHARED_MATCHED_MODEL_DRAW',S='SHARED_MATCHED_MODEL_DRAW')
        elif matched and escape is not None:
            action,source,route,info,_,_=canonical_action_decision(i,client,index,ic)
            verify_actual_request(i,info['call_id'],ic['request'])
            response_sha=model_response_hash(i,info['call_id'])
            I=(action,source,route,info,ic['assessments'],ic['suffix'])
            S=base.decide(s,sm,client,case,'S',index,1)
            if S[1]!=SOURCE or S[3]['call_id'] is not None or S[0]!=escape:
                raise RuntimeError('frozen candidate trigger mismatch')
            draw_source=dict(I='SHARED_OR_INCUMBENT_MODEL_DRAW',S='STAGNATION_ESCAPE')
        else:
            I=frozen_decide(i,im,client,case,'I',index,ic)
            S=frozen_decide(s,sm,client,case,'S',index,sc)
            draw_source=dict(I='INDEPENDENT_OR_MECHANICAL',S='INDEPENDENT_OR_MECHANICAL')
            if matched and ic['route']['route']=='MECHANICAL' and I[0]!=S[0]:
                raise RuntimeError('matched mechanical action mismatch')
        if matched and escape is None and I[0]!=S[0]:
            raise RuntimeError('matched inactive action mismatch')
        pair=dict(case=case,index=index,matched_context=matched,matched_checks=checks,
            shared_draw=shared,S_trigger=escape is not None,
            prior_suffix=sc['suffix'],I_action=I[0],S_action=S[0],draw_decision_source=draw_source,
            I_policy_source=I[1],S_policy_source=S[1],
            I_raw_provenance_sha256=ic['raw_provenance_sha256'],
            S_raw_provenance_sha256=sc['raw_provenance_sha256'],
            I_semantic_projection_sha256=ic['projection_sha256'],
            S_semantic_projection_sha256=sc['projection_sha256'],
            shared_request_sha256=ic['request']['canonical_sha256'] if matched else None,
            I_request_sha256=ic['request']['canonical_sha256'],S_request_sha256=sc['request']['canonical_sha256'],
            I_wire_sha256=ic['request']['wire_sha256'],S_wire_sha256=sc['request']['wire_sha256'],
            shared_response_sha256=response_sha,
            response_sha256=response_sha,
            I_action_call_id=I[3]['call_id'],S_action_call_id=S[3]['call_id'],
            I_raw_output_sha256=I[3]['raw_output_sha256'],S_raw_output_sha256=S[3]['raw_output_sha256'],
            sampling_options=ic['request']['request']['options'])
        # Freeze the pairing proof in both signed call streams before either world executes.
        for store in (i,s):
            store.append('calls','PAIRING_PROOF',pair)
            store.save(state=store.checkpoint['current_state'],
                next_transaction_id=store.checkpoint['next_transaction_id'])
        ir=base.execute(i,im,case,'I',index,*I[:4],I[4],counter_before=I[5]['count'])
        sr=base.execute(s,sm,case,'S',index,*S[:4],S[4],counter_before=S[5]['count'])
        pair.update(I_realized=ir['realized'],S_realized=sr['realized'],
            I_receipt_sha256=ir['receipt_provenance_sha256'],
            S_receipt_sha256=sr['receipt_provenance_sha256'])
        (root/'pairs'/case).mkdir(parents=True,exist_ok=True)
        _atomic_write(root/'pairs'/case/f'{index:02d}.json',pair)
        print(json.dumps(dict(case=case,index=index,matched=matched,shared=shared,
            trigger=escape is not None,I=I[0],S=S[0],I_reward=ir['realized']['consequence'],
            S_reward=sr['realized']['consequence'])),flush=True)

def run(root,case,first,last):
    if case not in ELIGIBLE|CONTROLS:raise ValueError('unknown case')
    if last>(ELIGIBLE|CONTROLS)[case]:raise ValueError('outside registered horizon')
    for index in range(first,last+1):step(root,case,index)
    _atomic_write(root/'cases'/case/'completion.json',dict(case=case,completed_through=last))

def restart_check(root):
    configure();result={}
    for arm in ('I','S'):
        path=root/'cases'/'E4'/arm
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=2:
                raise RuntimeError('E4 restart not after D02')
            result[arm]=qualifying_suffix(store,memory)
    verdict=dict(status='PASS' if result['S']['count']==2 else 'PRECONDITION_NOT_MET',
        reconstructed_suffix=result,no_persisted_counter=True,
        no_model_inference_during_reconstruction=True,fresh_os_process=True)
    _atomic_write(root/'restart-E4.json',verdict)
    print(json.dumps(verdict),flush=True)

def main():
    p=ArgumentParser();p.add_argument('command',choices=('prepare','run','restart-check'))
    p.add_argument('--private-root',required=True,type=Path);p.add_argument('--case')
    p.add_argument('--first',type=int);p.add_argument('--last',type=int)
    a=p.parse_args()
    if a.command=='prepare':prepare(a.private_root)
    elif a.command=='restart-check':restart_check(a.private_root)
    else:
        if not a.case or a.first is None or a.last is None:p.error('run requires case, first, last')
        run(a.private_root,a.case,a.first,a.last)
if __name__=='__main__':main()
