"""Prospectively defined matched-choice sensitivity and call-integrity analysis."""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from horus.core import digest
from experiments.modern_memory_vs_horus_v0.storage import canonical,file_hash
from .protocol import (MODEL,ACTION_OPTIONS,ACTION_FORMAT,ACTIONS,ORDERS,PAIRS,
    SYSTEMS,PREFERRED,PRIMARY_CALLS,call_schedule)
from .worker import validate_contexts,payload

def analyze(root,doc):
    validate_contexts(doc)
    path=root/'inference'
    with SessionStore(path/'session',True) as store:
        rows=[x['record'] for x in store.records['training'] if x['kind']=='DIAGNOSTIC_ACTION']
        requests=[x['record'] for x in store.records['calls'] if x['kind']=='REQUEST_INTENT']
        parsed=[x['record'] for x in store.records['calls'] if x['kind']=='PARSED']
        transport=[x['record'] for x in store.records['calls'] if x['kind']=='TRANSPORT_ATTEMPT_INTENT']
        if len(rows)!=PRIMARY_CALLS or len(requests)!=PRIMARY_CALLS or len(parsed)!=PRIMARY_CALLS or len(transport)!=PRIMARY_CALLS:
            raise RuntimeError('INVALID: diagnostic call count')
        if store.records['events'] or store.checkpoint['completed_steps']!=0:
            raise RuntimeError('INVALID: diagnostic world execution')
        for spec,row,request_intent,parse_record in zip(call_schedule(),rows,requests,parsed):
            if any(row[k]!=v for k,v in spec.items()):raise RuntimeError('INVALID: schedule mismatch')
            body=payload(doc,spec['pair'],spec['order'],spec['prompt_condition'],spec['variant'])
            request=dict(model=MODEL,system=SYSTEMS[spec['prompt_condition']],
                prompt=canonical(body),stream=False,format=ACTION_FORMAT,
                options={**ACTION_OPTIONS,'seed':spec['seed']})
            if row['prompt_sha256']!=digest(body) or row['request_sha256']!=digest(request):
                raise RuntimeError('INVALID: request mismatch')
            if request_intent['request_sha256']!=digest(request) or parse_record['call_id']!=row['call_id']:
                raise RuntimeError('INVALID: signed call mismatch')
            if parse_record['status']!=row['action_parse_status'] or parse_record['selected_action']!=row['selected_action']:
                raise RuntimeError('INVALID: parse record mismatch')
            if row['action_parse_status']=='VALID' and row['selected_action'] not in ACTIONS:
                raise RuntimeError('INVALID: disallowed action')
        metrics={};choice_rows=[]
        for condition in SYSTEMS:
            subset=[r for r in rows if r['prompt_condition']==condition]
            sensitive=sum(r['selected_action']==PREFERRED[r['variant']] for r in subset)
            pairs=[]
            for pair,(first,second) in PAIRS.items():
                for order in ORDERS:
                    variants={r['variant']:r for r in subset if r['pair']==pair and r['order']==order}
                    a,b=variants[first],variants[second]
                    preferred_both=(a['selected_action']==PREFERRED[first] and
                        b['selected_action']==PREFERRED[second])
                    pairs.append(dict(pair=pair,order=order,first_choice=a['selected_action'],
                        second_choice=b['selected_action'],preferred_both=preferred_both,
                        choice_changed=a['selected_action']!=b['selected_action'],
                        same_action_name=a['selected_action']==b['selected_action'],
                        same_display_position=(a['selected_action'] in ORDERS[order] and
                            b['selected_action'] in ORDERS[order] and
                            ORDERS[order].index(a['selected_action'])==ORDERS[order].index(b['selected_action']))))
            by_name=0;by_position=0
            for pair,variants in PAIRS.items():
                for variant in variants:
                    group=[r for r in subset if r['pair']==pair and r['variant']==variant]
                    if len({r['selected_action'] for r in group})==1:by_name+=1
                    positions=[ORDERS[r['order']].index(r['selected_action']) for r in group if r['selected_action'] in ORDERS[r['order']]]
                    if len(positions)==3 and len(set(positions))==1:by_position+=1
            kinds=Counter();negative=positive=0
            for r in subset:
                action=r['selected_action'];assessment=doc['contexts'][r['variant']]['grounded_assessments'].get(action,{})
                kind=assessment.get('kind','INVALID_ACTION');kinds[kind]+=1
                value=assessment.get('established_value') or {}
                if kind=='ESTABLISHED' and value.get('consequence',0)<0:negative+=1
                if kind=='ESTABLISHED' and value.get('consequence',0)>0:positive+=1
            core=[p for p in pairs if p['pair'] in ('A','B')]
            metrics[condition]=dict(grounding_sensitive_choices=sensitive,
                grounding_insensitive_choices=len(subset)-sensitive,
                choice_changes_under_value_swap=sum(p['choice_changed'] for p in pairs),
                matched_pairs_following_grounded_preference=sum(p['preferred_both'] for p in pairs),
                core_A_B_pairs_following_value=sum(p['preferred_both'] for p in core),
                per_pair_following_value={pair:sum(p['preferred_both'] for p in pairs if p['pair']==pair) for pair in PAIRS},
                established_negative_choices=negative,established_positive_choices=positive,
                unresolved_relation_choices=kinds['UNRESOLVED_CHANGE'],unseen_relation_choices=kinds['UNSEEN'],
                action_name_persistence_under_swap=sum(p['same_action_name'] for p in pairs),
                display_position_persistence_under_swap=sum(p['same_display_position'] for p in pairs),
                action_name_persistence_across_orders=by_name,
                display_position_persistence_across_orders=by_position,
                paired_results=pairs)
            choice_rows.extend(subset)
        valid=all(r['action_parse_status']=='VALID' for r in rows)
        n,g=metrics['N'],metrics['G']
        def strong(m):return (m['core_A_B_pairs_following_value']>=5 and
            m['per_pair_following_value']['A']>=2 and m['per_pair_following_value']['B']>=2)
        if not valid:classification='INVALID'
        elif strong(n):classification='GROUNDING_SENSITIVE_WITHOUT_DIRECTIVE'
        elif strong(g):classification='GROUNDING_SENSITIVE_WITH_DIRECTIVE'
        elif (n['core_A_B_pairs_following_value']<=1 and g['core_A_B_pairs_following_value']<=1 and
            n['action_name_persistence_under_swap']>=4 and g['action_name_persistence_under_swap']>=4):
            classification='GROUNDING_INSENSITIVE'
        else:classification='MIXED'
        return dict(status='PASS' if valid else 'INVALID',classification=classification,
            exact_calls=PRIMARY_CALLS,valid_action_outputs=sum(r['action_parse_status']=='VALID' for r in rows),
            transport_attempts=len(transport),diagnostic_world_executions=0,
            prompt_conditions=metrics,choices=rows,
            private_session_files_sha256={p.name:file_hash(p) for p in (path/'session').iterdir() if p.is_file() and p.name!='.lock'})

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--contexts',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    result=analyze(a.private_root,json.loads(a.contexts.read_text()))
    _atomic_write(a.output,result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('choices','private_session_files_sha256')},indent=2,sort_keys=True))
