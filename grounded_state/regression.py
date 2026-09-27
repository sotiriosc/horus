"""Zero-inference mechanical regression against completed study summaries."""
from argparse import ArgumentParser
from pathlib import Path
import json
from experiments.grounded_uncertainty_state_v0.uncertainty import fold as frozen_d
from experiments.grounded_stochastic_relation_v0.empirical import fold as frozen_e
from experiments.grounded_stochastic_relation_v0.public_replay import replay as public_replay
from experiments.grounded_stochastic_relation_v0.protocol import ARMS,SCHEDULES
from .deterministic import fold as core_d
from .empirical import fold as core_e

def read(path):return json.loads(path.read_text())
def check(root):
    base=root/'research';cases={}
    for dirname,classification in (
        ('grounded-uncertainty-state-v0','EXPLICIT_UNCERTAINTY_SUPPORTED'),
        ('grounded-hybrid-controller-v0','GROUNDED_HYBRID_SUPPORTED'),
        ('grounded-safe-fallback-v0','SAFE_FALLBACK_SUPPORTED')):
        results=read(base/dirname/'evidence/results.json')
        verdict=read(base/dirname/'evidence/replay.json')
        if results['classification']!=classification or results['status']!='COMPLETE' or verdict['status']!='PASS':
            raise RuntimeError('frozen study regression failed: '+dirname)
        cases[dirname]=dict(classification=classification,stored_replay='PASS')
    uncertainty=read(base/'grounded-uncertainty-state-v0/evidence/results.json')
    transitions=uncertainty['uncertainty']['transitions']
    if not transitions or any(t['after_state']!='UNRESOLVED_CHANGE' or t['resolution_receipts']!=1 for t in transitions):
        raise RuntimeError('first-contradiction result changed')
    cases['grounded-uncertainty-state-v0']['first_contradiction_count']=len(transitions)
    hybrid=read(base/'grounded-hybrid-controller-v0/evidence/results.json')
    if not hybrid['model_to_grounded_handoff'] or hybrid['epistemic']['FALSE_CERTAINTY']!=0 or hybrid['epistemic']['MODEL_ONLY_WHEN_UNSEEN']<=0:
        raise RuntimeError('model-to-grounded handoff or certainty result changed')
    cases['grounded-hybrid-controller-v0']['model_to_grounded_handoff']=True
    cases['grounded-hybrid-controller-v0']['false_certainty']=0
    safe=read(base/'grounded-safe-fallback-v0/evidence/results.json')
    fallbacks=[r for scenario in safe['per_scenario'].values() for r in scenario['H_SAFE']
               if r['reason']=='SAFE_GROUNDED_FALLBACK']
    if not fallbacks or any(not r['action_justified'] or r['optimality_established'] for r in fallbacks):
        raise RuntimeError('safe fallback distinction changed')
    cases['grounded-safe-fallback-v0']['justified_not_optimal_fallbacks']=len(fallbacks)
    replay=public_replay(root)
    if replay['classification']!='EMPIRICAL_GROUNDING_SUPPORTED' or replay['status']!='PASS':
        raise RuntimeError('stochastic public replay changed')
    parity=0
    for name,specs in SCHEDULES.items():
        public=read(base/'grounded-stochastic-relation-v0/evidence/schedules'/name/'public.json')
        by_arm={a:[] for a in ARMS}
        for row in public['rows']:by_arm[row['arm']].append(row)
        for arm in ARMS:
            histories={}
            for row in by_arm[arm]:
                history=histories.setdefault(row['relation'],[])
                if not (core_d(history)==frozen_d(history)==row['D_before'] and
                        core_e(history)==frozen_e(history)==row['E_before']):
                    raise RuntimeError('pre-event extracted-fold parity failed')
                history.append(dict(realized_next_state=row['realized']['next_state'],
                    realized_consequence=row['realized']['consequence'],authorization_status='AUTHORIZED',
                    event_identity=row['durable_admission']['event_identity'],
                    receipt_provenance_sha256=row['receipt_provenance_sha256'],
                    event_stream_sequence=row['event_stream_sequence']))
                if not (core_d(history)==frozen_d(history)==row['D_after'] and
                        core_e(history)==frozen_e(history)==row['E_after']):
                    raise RuntimeError('post-event extracted-fold parity failed')
                parity+=1
    analysis=read(base/'grounded-stochastic-relation-v0/evidence/analysis.json')
    if (analysis['aggregate']['false_change_alarms']!=0 or
        analysis['aggregate']['missed_shift_or_restoration']!=0 or
        analysis['information_boundary']['status']!='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH' or
        analysis['restart_integrity']!='PASS'):
        raise RuntimeError('stochastic result changed')
    cases['grounded-stochastic-relation-v0']=dict(classification=analysis['classification'],
        public_semantic_replay='PASS',extracted_fold_parity_events=parity,
        restart_integrity='PASS',information_boundary='EVIDENCE_INSUFFICIENT_TO_DISTINGUISH')
    return dict(status='PASS',model_calls_executed=0,studies=cases,
        limitation='Historical signed-stream verdicts are stored summaries in the publication root; raw HMAC replay requires the unchanged local archives.')

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--root',default='.',type=Path)
    a=p.parse_args();print(json.dumps(check(a.root.resolve()),indent=2,sort_keys=True))
