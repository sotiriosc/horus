"""Three protected 30-decision R128 runs using the unchanged promoted selector."""
from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch
import json,os,time

from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of,snapshot
from experiments.grounded_authority_autonomous_agent_v0 import worker as authority
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import qualifying_suffix
from experiments.grounded_stagnation_escape_promotion_controlled_v0 import worker as frozen
from grounded_agent.policy import promoted_decide
from .shared import PRIVATE_STUDY,live_action,verify_sources,verify_model


def exact_snapshot(store,memory,path):
    return dict(durable=snapshot(store,memory,path),stagnation_suffix=qualifying_suffix(store,memory))


def audit_source(source):
    if source in ('MODEL_FOR_UNSEEN','MODEL_FOR_UNRESOLVED','MODEL_WITH_KNOWN_NEGATIVE_FALLBACK'):
        return 'MODEL_FOR_UNSEEN_OR_MIXED'
    if source in ('GROUNDED_MECHANICAL','SAFE_GROUNDED_FALLBACK','STAGNATION_ESCAPE'):
        return source
    raise RuntimeError('unrecognized frozen source: '+str(source))


def model_metric(info):
    if info['call_id'] is None:
        return dict(call_id=None,input_tokens=0,completion_tokens=0,reasoning_tokens=0,
            final_output_tokens_proxy=0,prompt_eval_seconds=0,generation_seconds=0,
            wall_seconds=0,action_parse_status='NOT_CALLED')
    m=info['reasoning_metrics']
    return dict(call_id=info['call_id'],input_tokens=m['prompt_tokens'],
        completion_tokens=m['completion_tokens'],reasoning_tokens=m['reasoning_tokens'],
        reasoning_token_method=m['reasoning_token_method'],
        final_output_tokens_proxy=m['final_output_tokens_proxy'],
        final_token_method=m['final_token_method'],
        reasoning_sha256=m['reasoning_sha256'],final_sha256=m['final_sha256'],
        prompt_eval_seconds=m['prompt_seconds'],
        generation_seconds=m['reasoning_generation_seconds'],wall_seconds=m['wall_seconds'],
        finish_reason=m['finish_reason'],action_parse_status=info['status'],
        request_sha256=info['request_sha256'],request_bytes_sha256=info['request_bytes_sha256'],
        raw_response_sha256=info['raw_response_sha256'],physical_attempts=1)


def run(private,pair,stage):
    verify_sources();verify_model()
    if pair not in (1,2,3):raise ValueError('invalid run')
    if (pair==2)!=(stage in ('first','second')):raise ValueError('T2 requires first/second fresh processes')
    path=private/'runs'/f'T{pair}';create=stage!='second'
    if create and path.exists():raise RuntimeError('refusing to overwrite prior run')
    if not create and not (path/'before-restart.json').is_file():raise RuntimeError('missing T2 midpoint')
    path.mkdir(parents=True,exist_ok=True)
    store=SessionStore(path/'session',not create)
    memory=ModernMemory(path/'memory.sqlite3',create)
    authority.STUDY=PRIVATE_STUDY
    started=time.perf_counter()
    try:
        memory.reconcile(store)
        if stage=='second':
            before=json.loads((path/'before-restart.json').read_text())
            if before['pid']==os.getpid():raise RuntimeError('T2 did not use a fresh process')
            if exact_snapshot(store,memory,path)!=before['snapshot']:
                raise RuntimeError('durable restart/grounded state/suffix mismatch')
            _atomic_write(path/'restart-verdict.json',dict(status='PASS',fresh_process=True,
                durable_memory_exact=True,grounded_state_exact=True,
                current_state_exact=True,signed_stagnation_suffix_exact=True,
                first_post_restart_decision_pending=True))
        first=16 if stage=='second' else 1
        last=15 if stage=='first' else 30
        for index in range(first,last+1):
            if len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))!=index-1:
                raise RuntimeError('decision index discontinuity')
            before_suffix=qualifying_suffix(store,memory)
            with patch.object(frozen,'canonical_action_decision',
                              lambda session,_client,step,ctx:live_action(session,step,ctx)):
                action,source,route,info,assessments,suffix=promoted_decide(store,memory,object(),index)
            if suffix!=before_suffix:raise RuntimeError('promoted suffix changed during selection')
            if source in ('STAGNATION_ESCAPE','GROUNDED_MECHANICAL') and info['call_id'] is not None:
                raise RuntimeError('model called on escape/mechanical route')
            if action not in route['candidates']:raise RuntimeError('action outside frozen candidates')
            metric=model_metric(info)
            row=authority.execute_choice(store,memory,f'T{pair}',index,action,source,route,info,assessments)
            if row['action_parse_status'] not in ('VALID','NOT_CALLED'):
                raise RuntimeError('invalid action executed')
            after_suffix=qualifying_suffix(store,memory)
            step=dict(index=index,run=f'T{pair}',selected_action=action,
                decision_source=source,audit_source=audit_source(source),
                pre_state=row['state'],next_state=row['realized']['next_state'],
                realized_consequence=row['realized']['consequence'],
                selected_kind=row['selected_grounded_before']['kind'],
                selected_relation_type=row['selected_grounded_before']['relation_type'],
                selected_assessment_status=row['selected_grounded_before']['assessment_status'],
                known_negative_with_better_established=row['known_negative_with_better_established'],
                grounded_change=row['grounded_state_change'],
                admissible_actions=row['admissible_actions'],
                receipt_sha256=row['receipt_provenance_sha256'],
                receipt_identity=row['receipt_identity'],event_identity=row['event_identity'],
                suffix_before=before_suffix,suffix_after=after_suffix,
                inference=metric,authorization_status='AUTHORIZED')
            with (path/'step-summaries.private.jsonl').open('a') as stream:
                stream.write(json.dumps(step,sort_keys=True)+'\n')
            print(json.dumps({k:step[k] for k in ('run','index','selected_action',
                'decision_source','realized_consequence','next_state')}),flush=True)
            if stage=='second' and index==16:
                verdict=json.loads((path/'restart-verdict.json').read_text())
                verdict['first_post_restart_decision_pending']=False
                verdict['first_post_restart_decision_valid']=True
                _atomic_write(path/'restart-verdict.json',verdict)
        marker=dict(status='COMPLETE' if stage!='first' else 'MIDPOINT',
            run=f'T{pair}',stage=stage,pid=os.getpid(),
            decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION')),
            elapsed_seconds=time.perf_counter()-started,snapshot=exact_snapshot(store,memory,path))
        _atomic_write(path/'before-restart.json' if stage=='first' else path/'complete.json',marker)
    except Exception as exc:
        _atomic_write(path/'stop.json',dict(status='INVALID',run=f'T{pair}',stage=stage,
            error=repr(exc),completed_decisions=len(rows_of(store,'AUTONOMOUS_AGENT_DECISION'))))
        raise
    finally:
        memory.close();store.close()

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('pair',type=int,choices=(1,2,3))
    p.add_argument('--stage',choices=('single','first','second'),default='single')
    p.add_argument('--private-root',required=True,type=Path)
    args=p.parse_args();run(args.private_root,args.pair,args.stage)
