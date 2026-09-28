"""New fixtures; exact frozen canonical paired decision/execution functions are imported."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import qualifying_suffix
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as paired

STUDY='GROUNDED_STAGNATION_ESCAPE_ELIGIBILITY_COMPLETION_V0'
OPPORTUNITY={'P01':6,'P02':7,'P03':8,'P04':6,'P05':7,'P06':8,'P07':9,'P08':10}
CONTROLS={'T1':2,'T2':2,'T3':3,'T4':4}
ORDER=tuple(CONTROLS)+tuple(OPPORTUNITY)
SETUPS={
 'P01':(0,('HOLD','RETREAT')),'P02':(1,('ADVANCE','RETREAT')),
 'P03':(2,('RETREAT','ADVANCE')),'P04':(3,('ADVANCE','RETREAT')),
 'P05':(0,('ADVANCE','HOLD')),'P06':(1,('RETREAT','ADVANCE')),
 'P07':(2,('ADVANCE','RETREAT')),'P08':(3,('RETREAT','ADVANCE')),
 'T1':(0,('HOLD',)),'T2':(3,('ADVANCE','HOLD','RETREAT')),
 'T3':(3,('RETREAT','HOLD','HOLD','ADVANCE')),'T4':(2,('HOLD',)),
}
OUTCOMES={
 'P01':{0:{'HOLD':0,'RETREAT':-1,'ADVANCE':1}},
 'P02':{1:{'ADVANCE':0,'RETREAT':-1,'HOLD':-1}},
 'P03':{2:{'RETREAT':0,'ADVANCE':-1,'HOLD':0}},
 'P04':{3:{'ADVANCE':0,'RETREAT':-1,'HOLD':-1}},
 'P05':{0:{'ADVANCE':0,'HOLD':-1,'RETREAT':1}},
 'P06':{1:{'RETREAT':0,'ADVANCE':-1,'HOLD':1}},
 'P07':{2:{'ADVANCE':0,'RETREAT':-1,'HOLD':-1}},
 'P08':{3:{'RETREAT':0,'ADVANCE':-1,'HOLD':1}},
 'T1':{0:{'HOLD':1}},
 'T2':{3:{'ADVANCE':0,'HOLD':-1,'RETREAT':-1}},
 'T3':{3:{'RETREAT':0,'ADVANCE':-1}},
 'T4':{2:{'HOLD':0,'ADVANCE':1,'RETREAT':1}},
}

def override(case,state,action,visit,index):
    if case=='T3' and state==3 and action=='HOLD':
        return 3,1 if visit==1 else -1
    value=OUTCOMES.get(case,{}).get(state,{}).get(action)
    return None if value is None else (state,value)

def configure():
    paired.base.scenario_override=override
    paired.base.STUDY=STUDY

def install():
    paired.ELIGIBLE=OPPORTUNITY
    paired.CONTROLS=CONTROLS
    paired.SETUPS=SETUPS
    paired.configure=configure
    configure()

def prepare_one(root,case):
    install()
    if case not in SETUPS:raise ValueError('unregistered case')
    state,actions=SETUPS[case]
    seed=root/'seeds'/case
    seed.mkdir(parents=True,exist_ok=False)
    with SessionStore(seed/'session',False) as store,ModernMemory(seed/'memory.sqlite3',True):
        store.save(state=state,next_transaction_id=1)
    for arm in ('I','S'):
        path=root/'cases'/case/arm
        paired.base.copy_arm(seed,path)
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            for action in actions:
                paired.base.execute(store,memory,case,arm,0,action,'REGISTERED_SETUP',setup=True)
    print(json.dumps(dict(case=case,setup_actions=list(actions),independent_setup_receipts=True)),flush=True)

def run_control(root,case):
    install()
    if case not in CONTROLS:raise ValueError('not a control')
    paired.run(root,case,1,CONTROLS[case])

def run_until_pause(root,case):
    install()
    if case not in OPPORTUNITY:raise ValueError('not an opportunity case')
    for index in range(1,OPPORTUNITY[case]+1):
        paired.step(root,case,index)
        path=root/'cases'/case/'S'
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            suffix=qualifying_suffix(store,memory)
        if suffix['count']==2:
            marker=dict(case=case,after_decision=index,
                reason='FIRST_NATURAL_SIGNED_SUFFIX_TWO',no_persisted_candidate_counter=True)
            _atomic_write(root/'cases'/case/'pause.json',marker)
            print(json.dumps(marker),flush=True)
            return
    _atomic_write(root/'cases'/case/'completion.json',
                  dict(case=case,completed_through=OPPORTUNITY[case],restart_opportunity='NONE'))

def restart_check(root,case):
    install()
    marker=json.loads((root/'cases'/case/'pause.json').read_text())
    after=marker['after_decision'];observed={};calls={}
    for arm in ('I','S'):
        path=root/'cases'/case/arm
        with SessionStore(path/'session',True) as store,ModernMemory(path/'memory.sqlite3',False) as memory:
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=after:
                raise RuntimeError('restart position differs from signed history')
            before=len(store.records['calls'])
            observed[arm]=qualifying_suffix(store,memory)
            calls[arm]=len(store.records['calls'])-before
    status='PASS' if observed['I']['count']==observed['S']['count']==2 and not any(calls.values()) else 'FAIL'
    verdict=dict(case=case,status=status,after_decision=after,
                 pre_restart_S_suffix=2,post_restart_reconstructed_suffix=observed,
                 no_model_calls_during_reconstruction=calls,
                 no_persisted_mutable_counter=True,fresh_os_process=True)
    _atomic_write(root/'cases'/case/'restart-verdict.json',verdict)
    print(json.dumps(verdict),flush=True)
    if status!='PASS':raise RuntimeError('registered restart failed')

def continue_case(root,case):
    install()
    marker=json.loads((root/'cases'/case/'pause.json').read_text())
    verdict=json.loads((root/'cases'/case/'restart-verdict.json').read_text())
    if verdict['status']!='PASS' or verdict['after_decision']!=marker['after_decision']:
        raise RuntimeError('restart check absent or failed')
    first=marker['after_decision']+1
    if first<=OPPORTUNITY[case]:paired.run(root,case,first,OPPORTUNITY[case])
    else:_atomic_write(root/'cases'/case/'completion.json',
                       dict(case=case,completed_through=OPPORTUNITY[case]))

def main():
    p=ArgumentParser();p.add_argument('command',choices=('prepare-one','run-control','run-until-pause','restart-check','continue-case'))
    p.add_argument('--private-root',required=True,type=Path);p.add_argument('--case',required=True)
    a=p.parse_args();functions={'prepare-one':prepare_one,'run-control':run_control,
        'run-until-pause':run_until_pause,'restart-check':restart_check,
        'continue-case':continue_case}
    functions[a.command](a.private_root,a.case)
if __name__=='__main__':main()
