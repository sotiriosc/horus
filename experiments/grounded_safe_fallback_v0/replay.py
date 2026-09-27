"""Read-only replay of epistemic statuses, safe fallback, and protected receipts."""
from argparse import ArgumentParser
import json
from pathlib import Path
from horus.live import SessionStore
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_uncertainty_state_v0.uncertainty import fold
from .protocol import ARMS,SCENARIOS,MODEL_LOGICAL_CEILING,TOTAL_LOGICAL_CEILING,TOTAL_PHYSICAL_CEILING
from .policy import choose
from .analyze import analyze

def replay(output):
    saved=json.loads((output/'results.json').read_text());proof={};logical=physical=0
    for name,spec in SCENARIOS.items():
        root=output/'scenarios'/name;prefixes=[];sessions=[];sources=[];proof[name]={}
        for arm in ARMS:
            with SessionStore(root/'work'/arm/'session',True) as store,ModernMemory(root/'work'/arm/'memory.sqlite3',False) as memory:
                memory.reconcile(store);full=memory.rows();events=store.records['events']
                if len(events)<len(spec['seed']):raise RuntimeError('incomplete protected seed')
                prefix=[(e['record']['receipt']['pre_state'],e['record']['receipt']['action'],
                    e['record']['receipt']['next_state'],e['record']['receipt']['realized_consequence'],
                    e['record']['external_regime_version']) for e in events[:len(spec['seed'])]]
                if [(p[1],p[4]) for p in prefix]!=[(action,regime) for regime,action in spec['seed']]:
                    raise RuntimeError('seed action or regime drift')
                prefixes.append(prefix);sessions.append(store.checkpoint['session_id'])
                sources.append({e['record']['receipt']['source_identity'] for e in events})
                decisions=[e['record'] for e in store.records['training'] if e['kind']=='SAFE_FALLBACK_DECISION']
                if len(decisions)!=1+bool(spec.get('probe')):raise RuntimeError('decision count')
                parsed={e['record']['call_id']:e['record'] for e in store.records['calls'] if e['kind']=='PARSED'}
                for d in decisions:
                    if d['candidate_actions']!=list(spec['candidates']) or d['pre_event_count']>len(full):
                        raise RuntimeError('candidate or prefix drift')
                    before=full[:d['pre_event_count']]
                    for a in d['assessments']:
                        state=fold([r for r in before if r['relation']==a['relation']])
                        if any((state[k]!=a[k] for k in ('receipt_provenance','established_value',
                            'candidate_value','candidate_count','established_support','candidate_support')
                            if k!='receipt_provenance')) or state['receipt_provenance']!=a['provenance'] or state['kind']!=a['grounded_state_kind']:
                            raise RuntimeError('epistemic state not receipt-derived')
                        if arm in ('H_ABSTAIN','H_SAFE'):
                            expected={'UNSEEN':'MODEL_GENERALIZATION','ESTABLISHED':'GROUNDED',
                                'UNRESOLVED_CHANGE':'UNRESOLVED'}[state['kind']]
                            if a['status']!=expected or (expected!='MODEL_GENERALIZATION' and a['model_calls']!=0):
                                raise RuntimeError('hybrid authority boundary violated')
                            if expected=='GROUNDED' and a['value']!=state['established_value']:
                                raise RuntimeError('grounded value mismatch')
                            if expected=='UNRESOLVED' and a['value'] is not None:
                                raise RuntimeError('unresolved relation flattened')
                        elif arm=='FORCED_GROUNDED':
                            rows=[r for r in before if r['relation']==a['relation']]
                            point=(dict(next_state=rows[-1]['realized_next_state'],consequence=rows[-1]['realized_consequence'])
                                if rows else dict(next_state=d['pre_state'],consequence=0))
                            if a['value']!=point or a['model_calls']!=0:raise RuntimeError('forced point mismatch')
                        if a['model_calls']:
                            ids=a['model_call_ids']
                            if len(ids)!=2 or any(cid not in parsed for cid in ids):raise RuntimeError('unbound model calls')
                            j,g=parsed[ids[0]],parsed[ids[1]]
                            if j['outcome']!='VALID' or g['outcome']!='VALID' or a['value']!=dict(
                                next_state=j['parsed']['next_state'],consequence=g['parsed']['consequence']):
                                raise RuntimeError('model point not bound to parsed response')
                    expected=choose(d['assessments'],arm)
                    if any(d[key]!=expected[key] for key in ('selected_action','reason','action_justified',
                        'optimality_established','unresolved_relations') if key!='selected_action') or d['selected_action']!=expected['action']:
                        raise RuntimeError('policy choice or epistemic decision status mismatch')
                    if d['selected_action'] is None:
                        if d['authorized_event_sequence'] is not None or d['realized'] is not None:
                            raise RuntimeError('abstention minted a receipt')
                    else:
                        event=next((e['record'] for e in events if e['sequence']==d['authorized_event_sequence']),None)
                        if event is None or event['action_source']!='AUTONOMOUS_POLICY' or event['receipt']['action']!=d['selected_action']:
                            raise RuntimeError('autonomous action not bound to receipt')
                        actual=dict(next_state=event['receipt']['next_state'],consequence=event['receipt']['realized_consequence'])
                        if d['realized']!=actual:raise RuntimeError('realized consequence mismatch')
                    if d['reason']=='SAFE_GROUNDED_FALLBACK':
                        selected=next(a for a in d['assessments'] if a['action']==d['selected_action'])
                        if (arm!='H_SAFE' or selected['status']!='GROUNDED' or
                            selected['value']['consequence']<0 or d['optimality_established'] or
                            not d['action_justified'] or not d['unresolved_relations']):
                            raise RuntimeError('unsafe or falsely optimal fallback')
                calls=store.records['calls'];intents=[e['record'] for e in calls if e['kind']=='REQUEST_INTENT']
                attempts=[e['record'] for e in calls if e['kind']=='TRANSPORT_ATTEMPT_INTENT']
                responses=[e['record'] for e in calls if e['kind']=='RESPONSE']
                if len(intents)!=sum(d['model_calls'] for d in decisions) or len(parsed)!=len(intents) or len(responses)!=len(intents):
                    raise RuntimeError('model call chain mismatch')
                if arm=='MODEL' and len(intents)!=2*len(spec['candidates'])*len(decisions):
                    raise RuntimeError('model baseline skipped action')
                if arm=='FORCED_GROUNDED' and intents:raise RuntimeError('forced reducer called model')
                if any(not e['record']['experience_unchanged'] for e in calls if e['kind']=='PREPARATION_GUARD'):
                    raise RuntimeError('preparation altered experience')
                logical+=len(intents);physical+=len(attempts)
                proof[name][arm]=dict(seed_receipts=len(prefix),decisions=len(decisions),
                    autonomous_receipts=sum(e['record']['action_source']=='AUTONOMOUS_POLICY' for e in events),
                    model_calls=len(intents))
        if not all(p==prefixes[0] for p in prefixes) or len(set(sessions))!=len(ARMS):
            raise RuntimeError('unmatched seed or shared session')
        if any(sources[i]&sources[j] for i in range(len(ARMS)) for j in range(i)):
            raise RuntimeError('cross-arm receipt source')
        if spec.get('restart'):
            before=json.loads((root/'before-restart.json').read_text())
            after=json.loads((root/'restart.json').read_text())
            if before['conditions']!=after['conditions'] or before['decision_status']!=after['decision_status']:
                raise RuntimeError('restart state or decision status mismatch')
            perturb=json.loads((root/'perturbation.json').read_text())
            if perturb['status']!='PASS' or not perturb['no_receipt_or_memory']:
                raise RuntimeError('failed operation changed experience')
    def fixture(name):
        root=output/'scenarios'/name/'work/H_SAFE/session'
        with SessionStore(root,True) as store:
            return ([(e['record']['receipt']['pre_state'],e['record']['receipt']['action'],
                e['record']['receipt']['next_state'],e['record']['receipt']['realized_consequence'])
                for e in store.records['events'][:4]],
                [e['record']['receipt']['realized_consequence'] for e in store.records['events']
                    if e['record']['step']=='PROBE'])
    confirm,confirm_probe=fixture('P2_SAFE_ZERO_CONFIRM_WORSE')
    reject,reject_probe=fixture('P6_REJECTED_CHANGE')
    restart,_=fixture('P8_RESTART_SAFE')
    if confirm!=reject or confirm!=restart or confirm_probe!=[-1] or reject_probe!=[1]:
        raise RuntimeError('matched-prefix information boundary failed')
    if logical>TOTAL_LOGICAL_CEILING or physical>TOTAL_PHYSICAL_CEILING:
        raise RuntimeError('campaign call ceiling')
    if saved!=analyze(output):raise RuntimeError('analysis not exactly reproducible')
    result=dict(status='PASS',scenarios=proof,logical_model_calls=logical,
        physical_model_attempts=physical,matched_seed_histories=True,
        receipt_derived_epistemic_states=True,exact_policy_replay=True,
        autonomous_action_receipt_binding=True,information_boundary_twin=True,
        exact_restart_and_perturbation=True,exact_analysis_replay=True)
    (output/'replay.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result
if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--output',type=Path,required=True)
    print(json.dumps(replay(p.parse_args().output),sort_keys=True))
