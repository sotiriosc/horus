"""Post-run allowlist export from signed private sessions; never emits raw calls or keys."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from experiments.grounded_autonomous_agent_v0_2.analyze import analyze_run
from experiments.grounded_autonomous_agent_v0_2.protocol import RUNS,DECISIONS,MODEL,ACTION_OPTIONS,COMMENTARY_OPTIONS,REVIEW_OPTIONS

ARCHIVE_COMMIT='5f4f4cff4fbf4447c58f35c6b1582e4ce4f4de2d'
SELECT_DECISION=(
    'decision_id','index','state','selected_action','action_parse_status','commentary_status',
    'selected_grounded_before','grounded_state_change','realized','receipt_identity',
    'receipt_provenance_sha256','event_identity','event_stream_sequence',
    'agent_grounded_state_disagreement','disagreement_reasons','stated_reliance',
    'claimed_status','claimed_consequence','raw_action_output_sha256',
    'raw_commentary_output_sha256','action_call_id','commentary_call_id')

def cap_counts(root,run):
    path=root/'runs'/run/'session/model-calls.private.jsonl'
    caps={'ACTION':ACTION_OPTIONS['num_predict'],'COMMENTARY':COMMENTARY_OPTIONS['num_predict'],
          'SELF_REVIEW':REVIEW_OPTIONS['num_predict']}
    counts=Counter();truncated=Counter()
    for line in path.read_text().splitlines():
        x=json.loads(line)
        if x['kind']!='TRANSPORT_ATTEMPT_RESULT':continue
        role=x['record']['call_id'].split(':')[2]
        tokens=x['record']['response']['response_metadata'].get('eval_count')
        counts[role]+=1
        if tokens==caps[role]:truncated[role]+=1
    return dict(response_counts=dict(counts),responses_at_generation_ceiling=dict(truncated))

def export(root):
    runs={}
    for run in RUNS:
        a=analyze_run(root,run)
        runs[run]=dict(behavioral_run_status=a['behavioral_run_status'],
            self_review_status=a['self_review_status'],metrics=a['metrics'],
            adaptation=a['adaptation'],timeline=a['timeline'],restart=a['restart'],
            decisions=[{k:d[k] for k in SELECT_DECISION} for d in a['decisions']],
            reviews=[{k:r[k] for k in ('review_id','after_decision','reviewed_decisions',
                'review_status','proposal_status','raw_model_output_sha256','no_memory_or_state_change')}
                for r in a['reviews']],
            excluded_private_files_sha256=a['private_files_sha256'],
            output_metadata=cap_counts(root,run))
    assert all(x['behavioral_run_status']=='VALID' and x['metrics']['decisions']==DECISIONS for x in runs.values())
    return dict(campaign='grounded-autonomous-agent-v0.2',
        behavioral_campaign_status='VALID',self_analysis_status='SELF_ANALYSIS_NOT_ESTABLISHED',
        model=MODEL,runs=runs,full_private_evidence_local_commit=ARCHIVE_COMMIT,
        excluded_private_artifact_categories=['authentication keys','raw model-call streams',
            'signed private event/training streams','checkpoints','grounded Memory databases'],
        provenance_statement='Complete private evidence remains preserved locally and is intentionally absent from publication ancestry.',
        prior_campaigns={'v0':'INVALID','v0.1':'INVALID'})

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    x=export(a.private_root)
    a.output.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in x.items() if k!='runs'}|{'runs':{r:v['metrics'] for r,v in x['runs'].items()}},indent=2,sort_keys=True))
