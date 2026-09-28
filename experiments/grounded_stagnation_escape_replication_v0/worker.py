"""Driver-only new scenarios; imports frozen incumbent and candidate unchanged."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import SessionStore,ModelClient,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_stagnation_escape_evaluation_v0 import worker as base
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import qualifying_suffix

STUDY='GROUNDED_STAGNATION_ESCAPE_REPLICATION_V0'
ELIGIBLE=('R1','R2','R3','R4','R5','R6')
CONTROLS=('C1','C2','C3','C4','C5','C6')
GROUPS={
    'P3A':dict(state=3,setup=('ADVANCE',),cases=('R1','R4')),
    'P3H':dict(state=3,setup=('ADVANCE','HOLD'),cases=('R6',)),
    'P1A':dict(state=1,setup=('ADVANCE',),cases=('R2','R3')),
    'P2A':dict(state=2,setup=('ADVANCE',),cases=('R5',)),
}
CONTROL_SETUP={
    'C1':dict(state=3,actions=('ADVANCE',)),
    'C2':dict(state=3,actions=('ADVANCE','HOLD','RETREAT')),
    'C3':dict(state=3,actions=('ADVANCE','HOLD','HOLD','RETREAT')),
    'C4':dict(state=1,actions=('HOLD',)),
    'C5':dict(state=2,actions=('ADVANCE',)),
    'C6':dict(state=2,actions=('HOLD','ADVANCE','ADVANCE')),
}

def override(case,state,action,visit,index):
    """Frozen hidden driver schedule; no decision/model path reads this function."""
    if case in ('P3A','R1','R4','RA','RB') and state==3:
        if action=='ADVANCE':return (3,0)
        if action=='HOLD':return (3,1 if case in ('R4','RB') else 0)
    if case in ('P3H','R6') and state==3:
        if action=='ADVANCE':return (3,-1)
        if action=='HOLD':return ((0 if case=='R6' and visit>=5 else 3),0)
        if action=='RETREAT':return (3,0)
    if case in ('P1A','R2','R3') and state==1:
        if action=='ADVANCE':return (1,0)
        if action=='HOLD':return (1,-1 if case=='R3' else 0)
    if case in ('P2A','R5') and state==2:
        if action=='ADVANCE':return (2,0)
        if action=='HOLD':return (2,0)
    if case=='C1' and state==3 and action=='ADVANCE':return (3,1)
    if case=='C2' and state==3:
        return (3,0 if action=='HOLD' else -1)
    if case=='C3' and state==3:
        if action=='ADVANCE':return (3,0)
        if action=='RETREAT':return (3,-1)
        if action=='HOLD':return (3,1 if visit==1 else -1)
    if case=='C4' and state==1 and action=='HOLD':return (1,0)
    if case=='C5' and state==2 and action=='ADVANCE':return (2 if visit==1 else 3,0)
    if case=='C6':
        if state==2 and action=='HOLD':return (2,0)
        if state==2 and action=='ADVANCE':return (3,-1)
        if state==3 and action=='ADVANCE':return (2 if visit>=4 else 3,0)
    return None

# Configure only when this worker runs; importing this module cannot mutate
# the frozen Phase-4 module used by other studies/tests.
def configure():
    base.scenario_override=override
    base.STUDY=STUDY

def setup(path,case,initial_state,actions):
    configure()
    path.mkdir(parents=True,exist_ok=False)
    with SessionStore(path/'session',False) as store,ModernMemory(path/'memory.sqlite3',True) as memory:
        store.save(state=initial_state,next_transaction_id=1)
        for action in actions:
            base.execute(store,memory,case,'SETUP',0,action,'REGISTERED_SETUP',setup=True)

def advance(path,case,arm,index,context_start=1):
    configure()
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        client=ModelClient()
        action,source,route,info,assessments,suffix=base.decide(
            store,memory,client,case,arm,index,context_start)
        row=base.execute(store,memory,case,arm,index,action,source,route,info,
            assessments,counter_before=suffix['count'])
        print(json.dumps(dict(case=case,arm=arm,index=index,action=action,
            source=source,consequence=row['realized']['consequence'],
            next_state=row['realized']['next_state'],counter_before=suffix['count'])),flush=True)
        return dict(action=action,source=source,suffix_after=qualifying_suffix(store,memory))

def prepare(root):
    configure()
    root.mkdir(parents=True,exist_ok=False)
    for group,spec in GROUPS.items():
        path=root/'groups'/group
        setup(path,group,spec['state'],spec['setup'])
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            client=ModelClient()
            for index in (1,2):
                action,source,route,info,assessments,suffix=base.decide(
                    store,memory,client,group,'SHARED',index,1)
                row=base.execute(store,memory,group,'SHARED',index,action,source,route,info,
                    assessments,counter_before=suffix['count'])
                print(json.dumps(dict(group=group,index=index,action=action,
                    consequence=row['realized']['consequence'],state=row['realized']['next_state'])),flush=True)
        if group=='P3A':base.copy_arm(path,root/'restart_seed'/'RA')
        # Reopen after the copy; the signed D03 prefix is still common.
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            client=ModelClient()
            action,source,route,info,assessments,suffix=base.decide(
                store,memory,client,group,'SHARED',3,1)
            row=base.execute(store,memory,group,'SHARED',3,action,source,route,info,
                assessments,counter_before=suffix['count'])
            print(json.dumps(dict(group=group,index=3,action=action,
                consequence=row['realized']['consequence'],state=row['realized']['next_state'])),flush=True)
        for case in spec['cases']:
            for arm in ('I','S'):base.copy_arm(path,root/'cases'/case/arm)
    for case,spec in CONTROL_SETUP.items():
        path=root/'setup'/case
        setup(path,case,spec['state'],spec['actions'])
        for arm in ('I','S'):base.copy_arm(path,root/'cases'/case/arm)

def continue_ra(root):
    configure()
    """Must be a new OS process after prepare; no writable counter."""
    path=root/'restart_seed'/'RA'
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        suffix=qualifying_suffix(store,memory)
        _atomic_write(path/'restart-verdict.json',dict(status='PASS' if suffix['count']==2 else
            'PRECONDITION_NOT_MET',observed_suffix=suffix,expected_suffix=2,
            reconstructed_from_signed_history=True,no_persisted_counter=True,
            no_model_inference_during_reconstruction=True))
        client=ModelClient()
        action,source,route,info,assessments,before=base.decide(
            store,memory,client,'RA','SHARED',3,3)
        row=base.execute(store,memory,'RA','SHARED',3,action,source,route,info,
            assessments,counter_before=before['count'])
        print(json.dumps(dict(restart='RA',index=3,action=action,
            consequence=row['realized']['consequence'],suffix_before=before['count'])),flush=True)
    for arm in ('I','S'):base.copy_arm(path,root/'cases'/'RA'/arm)

def make_rb(root):
    configure()
    source=root/'cases'/'R4'/'S'
    with SessionStore(source/'session',True) as store,ModernMemory(source/'memory.sqlite3',False) as memory:
        decisions=base.rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        if len(decisions)!=4:raise RuntimeError('R4 S must stop immediately after D04')
    base.copy_arm(source,root/'cases'/'RB'/'S')

def continue_rb(root):
    configure()
    """Fresh process after the R4 candidate escape; inspect before D05."""
    path=root/'cases'/'RB'/'S'
    with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
        suffix=qualifying_suffix(store,memory)
        decisions=base.rows_of(store,'AUTONOMOUS_AGENT_DECISION')
        expected_escape=decisions[-1]['decision_source']=='STAGNATION_ESCAPE'
        status='PASS' if expected_escape and suffix['count']==0 else 'PRECONDITION_NOT_MET'
        _atomic_write(path/'restart-verdict.json',dict(status=status,observed_suffix=suffix,
            prior_escape=expected_escape,reconstructed_from_signed_history=True,
            no_persisted_counter=True,no_model_inference_during_reconstruction=True))
    base.run(root,'RB','S',5,5,5)

def run(root,case,arm,first,last,context_start=1):
    configure()
    base.run(root,case,arm,first,last,context_start)

def main():
    p=ArgumentParser();p.add_argument('command',choices=('prepare','continue-ra','make-rb','continue-rb','run'))
    p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--case');p.add_argument('--arm',choices=('I','S'))
    p.add_argument('--first',type=int);p.add_argument('--last',type=int)
    p.add_argument('--context-start',type=int,default=1)
    a=p.parse_args();root=a.private_root
    if a.command=='prepare':prepare(root)
    elif a.command=='continue-ra':continue_ra(root)
    elif a.command=='make-rb':make_rb(root)
    elif a.command=='continue-rb':continue_rb(root)
    else:
        if a.case is None or a.arm is None or a.first is None or a.last is None:
            p.error('run requires case, arm, first and last')
        run(root,a.case,a.arm,a.first,a.last,a.context_start)

if __name__=='__main__':main()
