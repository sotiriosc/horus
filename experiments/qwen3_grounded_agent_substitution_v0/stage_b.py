"""Independent 30-decision promoted-policy campaigns with model-only D/Q substitution."""
from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch
import json
import os
import time

from horus.live import SessionStore, ModelClient, _atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of, snapshot
from experiments.grounded_authority_autonomous_agent_v0 import worker as authority
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import qualifying_suffix
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as frozen
from grounded_agent.policy import promoted_decide
from .shared import STUDY, verify_sources, verify_q_model, q_action

PRIVATE_STUDY='QWEN3_GROUNDED_AGENT_SUBSTITUTION_V0'


def metric(store, info, arm):
    if info['call_id'] is None:
        return dict(call_id=None, input_tokens=0, output_tokens=0,
            prompt_eval_seconds=0, generation_seconds=0, wall_seconds=0,
            runner_load_seconds=0, action_parse_status='NOT_CALLED')
    if arm=='Q':
        return dict(call_id=info['call_id'], input_tokens=info['context_tokens'],
            output_tokens=info['output_tokens'], prompt_eval_seconds=info['prompt_eval_duration_seconds'],
            generation_seconds=info['generation_duration_seconds'],wall_seconds=info['latency_seconds'],
            runner_load_seconds=0,action_parse_status=info['status'])
    matches=[e['record'] for e in store.records['calls'] if e['kind']=='TRANSPORT_ATTEMPT_RESULT'
             and e['record']['call_id']==info['call_id']]
    if not matches:raise RuntimeError('D physical attempt metadata missing')
    accepted=matches[-1]['response']['response_metadata']
    return dict(call_id=info['call_id'],input_tokens=info['context_tokens'],
        output_tokens=info['output_tokens'],prompt_eval_seconds=accepted.get('prompt_eval_duration',0)/1e9,
        generation_seconds=accepted.get('eval_duration',0)/1e9,wall_seconds=info['latency_seconds'],
        runner_load_seconds=accepted.get('load_duration',0)/1e9,
        action_parse_status=info['status'],physical_attempts=len(matches))


def audit_source(source):
    if source in ('MODEL_FOR_UNSEEN','MODEL_FOR_UNRESOLVED','MODEL_WITH_KNOWN_NEGATIVE_FALLBACK'):
        return 'MODEL_FOR_UNSEEN_OR_MIXED'
    if source in ('GROUNDED_MECHANICAL','SAFE_GROUNDED_FALLBACK','STAGNATION_ESCAPE'):
        return source
    raise RuntimeError('unrecognized frozen decision source: '+str(source))


def exact_snapshot(store,memory,path):
    return dict(durable=snapshot(store,memory,path),
                stagnation_suffix=qualifying_suffix(store,memory))


def run(private, arm, pair, stage):
    verify_sources()
    gate=json.loads((STUDY/'stage-a-gate.json').read_text())
    if gate['status']!='PASS' or not gate['stage_b_authorized_by_preregistration']:
        raise RuntimeError('Stage A gate has not passed')
    if arm not in ('D','Q') or pair not in (1,2,3):raise ValueError('invalid arm/pair')
    if (pair==2)!=(stage in ('first','second')):
        raise ValueError('D2/Q2 require distinct first and second processes')
    if arm=='Q':verify_q_model()
    path=private/'runs'/f'{arm}{pair}'
    path.mkdir(parents=True,exist_ok=True)
    create=stage!='second'
    store=SessionStore(path/'session',not create)
    memory=ModernMemory(path/'memory.sqlite3',create)
    authority.STUDY=PRIVATE_STUDY
    client=ModelClient() if arm=='D' else object()
    started=time.perf_counter()
    try:
        memory.reconcile(store)
        if stage=='second':
            before=json.loads((path/'before-restart.json').read_text())
            if before['pid']==os.getpid():raise RuntimeError('midpoint is not a fresh process')
            actual=exact_snapshot(store,memory,path)
            if actual!=before['snapshot']:
                raise RuntimeError('durable restart snapshot or suffix mismatch')
            _atomic_write(path/'restart-verdict.json',dict(status='PASS',fresh_process=True,
                durable_memory_exact=True,grounded_state_exact=True,
                signed_stagnation_suffix_exact=True,first_post_restart_decision_pending=True))
        first=16 if stage=='second' else 1
        last=15 if stage=='first' else 30
        for index in range(first,last+1):
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=index-1:
                raise RuntimeError('decision index discontinuity')
            suffix_before=qualifying_suffix(store,memory)
            if arm=='Q':
                with patch.object(frozen,'canonical_action_decision',
                                  lambda session, _client, step, ctx: q_action(session, step, ctx)):
                    action,source,route,info,assessments,suffix=promoted_decide(store,memory,client,index)
            else:
                action,source,route,info,assessments,suffix=promoted_decide(store,memory,client,index)
            if suffix!=suffix_before:
                raise RuntimeError('promoted suffix changed during selection')
            if source=='STAGNATION_ESCAPE' and info['call_id'] is not None:
                raise RuntimeError('escape made action-model call')
            if source=='GROUNDED_MECHANICAL' and info['call_id'] is not None:
                raise RuntimeError('mechanical decision made action-model call')
            if action not in route['candidates']:
                raise RuntimeError('selected action outside frozen candidate route')
            m=metric(store,info,arm)
            row=authority.execute_choice(store,memory,f'{arm}{pair}',index,action,source,route,info,assessments)
            if row['action_parse_status'] not in ('VALID','NOT_CALLED'):
                raise RuntimeError('invalid action executed')
            after=qualifying_suffix(store,memory)
            step=dict(index=index,arm=arm,pair=pair,selected_action=action,
                decision_source=source,audit_source=audit_source(source),
                pre_state=row['state'],next_state=row['realized']['next_state'],
                realized_consequence=row['realized']['consequence'],
                selected_kind=row['selected_grounded_before']['kind'],
                selected_relation_type=row['selected_grounded_before']['relation_type'],
                known_negative_with_better_established=row['known_negative_with_better_established'],
                grounded_change=row['grounded_state_change'],
                admissible_actions=row['admissible_actions'],
                receipt_sha256=row['receipt_provenance_sha256'],
                event_identity=row['event_identity'],
                suffix_before=suffix_before,suffix_after=after,
                inference=m,authorization_status='AUTHORIZED')
            with (path/'step-summaries.private.jsonl').open('a') as stream:
                stream.write(json.dumps(step,sort_keys=True)+'\n')
            print(json.dumps({k:step[k] for k in ('arm','pair','index','selected_action',
                'decision_source','realized_consequence','next_state')}),flush=True)
            if stage=='second' and index==16:
                verdict=json.loads((path/'restart-verdict.json').read_text())
                verdict['first_post_restart_decision_pending']=False
                verdict['first_post_restart_decision_valid']=True
                _atomic_write(path/'restart-verdict.json',verdict)
        result=dict(status='COMPLETE' if stage!='first' else 'MIDPOINT',
            arm=arm,pair=pair,stage=stage,pid=os.getpid(),
            decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
            wall_seconds=time.perf_counter()-started,
            snapshot=exact_snapshot(store,memory,path))
        _atomic_write(path/'before-restart.json' if stage=='first' else path/'complete.json',result)
    except Exception as exc:
        _atomic_write(path/'stop.json',dict(status='INVALID',arm=arm,pair=pair,stage=stage,
            error=repr(exc),completed_decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))))
        raise
    finally:
        memory.close();store.close()


def main():
    p=ArgumentParser();p.add_argument('arm',choices=('D','Q'));p.add_argument('pair',type=int,choices=(1,2,3))
    p.add_argument('--stage',choices=('single','first','second'),default='single')
    p.add_argument('--private-root',required=True,type=Path)
    a=p.parse_args();run(a.private_root,a.arm,a.pair,a.stage)

if __name__=='__main__':main()
