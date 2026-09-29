"""Read-only aggregate of frozen, non-authoritative retrospective attempts."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import _atomic_write
from .shared import STUDY

TRAJECTORIES=('D1','D2','D3','Q1','Q2','Q3')


def audit(private):
    inputs=json.loads((STUDY/'retrospective-inputs.json').read_text())
    records={}
    for arm in ('D','Q'):
        for trajectory in TRAJECTORIES:
            name=f'{arm}-on-{trajectory}'
            public=json.loads((STUDY/f'retrospective-{name}.json').read_text())
            private_record=json.loads((private/'reviews'/name/'response.private.json').read_text())
            assert private_record['public']==public
            response=private_record['response']
            if arm=='D':
                metadata=(response or {})
                phases=dict(prompt_eval_seconds=metadata.get('prompt_eval_duration',0)/1e9,
                    generation_seconds=metadata.get('eval_duration',0)/1e9,
                    runner_load_seconds=metadata.get('load_duration',0)/1e9)
            else:
                timings=(response or {}).get('timings') or {}
                phases=dict(prompt_eval_seconds=timings.get('prompt_ms',0)/1000,
                    generation_seconds=timings.get('predicted_ms',0)/1000,
                    runner_load_seconds=0)
            expected={d['decision_id'] for d in inputs[trajectory]['completed_decisions']}
            assert len(expected)==30
            if public['complete']:
                assert set(public['citations'])<=expected
                citation_status='VALID_IDS_BROAD_CITATION' if len(public['citations'])==30 else 'VALID_IDS_TARGETED'
                schema='COMPLETE'
            elif public['timeout_censored']:
                citation_status='NOT_SCORABLE_TIMEOUT';schema='CENSORED_TIMEOUT'
            else:
                citation_status='NOT_SCORABLE_INCOMPLETE';schema='INCOMPLETE_DESCRIPTIVE_OUTPUT'
            records[name]=dict(trajectory=trajectory,model_arm=arm,
                schema_status=schema,citation_status=citation_status,
                response_received=response is not None,
                wall_seconds=public['wall_seconds'],input_tokens=public['input_tokens'],
                output_tokens=public['output_tokens'],
                prompt_sha256=public['prompt_sha256'],request_sha256=public['request_sha256'],
                raw_response_sha256=public['raw_response_sha256'],
                cited_decisions=public['citations'] if public['complete'] else [],
                phases=phases,non_authoritative=True,
                later_action_prompts_or_memory_writes=0)
    summary={}
    for arm in ('D','Q'):
        selected=[x for x in records.values() if x['model_arm']==arm]
        summary[arm]=dict(attempts=len(selected),responses_received=sum(x['response_received'] for x in selected),
            complete_reviews=sum(x['schema_status']=='COMPLETE' for x in selected),
            censored_timeouts=sum(x['schema_status']=='CENSORED_TIMEOUT' for x in selected),
            incomplete_descriptive=sum(x['schema_status']=='INCOMPLETE_DESCRIPTIVE_OUTPUT' for x in selected),
            valid_citation_reviews=sum(x['citation_status'].startswith('VALID_IDS') for x in selected),
            total_observed_wall_seconds=sum(x['wall_seconds'] for x in selected),
            total_prompt_eval_seconds=sum(x['phases']['prompt_eval_seconds'] for x in selected),
            total_generation_seconds=sum(x['phases']['generation_seconds'] for x in selected),
            total_runner_load_seconds=sum(x['phases']['runner_load_seconds'] for x in selected))
    result=dict(status='COMPLETE',non_authoritative=True,
        no_later_action_prompt_or_memory_feedback=True,summary=summary,records=records)
    _atomic_write(STUDY/'retrospective-audit.json',result)
    return result

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    result=audit(p.parse_args().private_root)
    print(json.dumps(result['summary'],sort_keys=True))
