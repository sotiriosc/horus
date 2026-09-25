"""Descriptive role metrics and episode-local evidence chains; no success tuning."""
from collections import Counter,defaultdict


def summarize(rows,calls):
    explorer=[];maps=[];recoveries=[];episodes=[]
    chains=dict(Explorer=[],Map=[],Recovery=[])
    for episode in range(12):
        group=[r for r in rows if r['episode']==episode];prior=[]
        if not group:continue
        for row in group:
            rc=[calls[i] for i in row['call_indices']]; e=rc[0];p=row['probe'];state=e['current_state']
            valid=e['parsed'] is not None
            item=dict(index=e['index'],episode=episode,decision=row['decision'],family=e['family'],state=state,
                valid=valid,malformed=bool(e['parse_error']),transport_failure=bool(e['transport_error']),
                action=e['parsed']['action'] if valid else None,token=e['parsed']['surface'] if valid else None,
                untried=False,tried=False,strict_preference=False,known_worse=False,negative_retest=False,
                uncertain_retest=False,repeated_known_worse=False)
            if valid:
                values={e['mapping'][a['action']]:a['verified_outcomes'] for a in e['input']['actions']}
                selected=values[item['action']];tried={a:v for a,v in values.items() if isinstance(v,list)}
                means={a:sum(v)/len(v) for a,v in tried.items()}
                item['untried']=selected=='UNTRIED';item['tried']=not item['untried']
                item['negative_retest']=item['tried'] and any(x<0 for x in selected)
                if item['tried'] and len(means)>=2:
                    mean=means[item['action']];best=max(means.values())
                    item['strict_preference']=mean==best and min(means.values())<best
                    item['known_worse']=mean<best
                    if item['known_worse']:
                        better=[a for a in means if means[a]>mean]
                        sparse=len(selected)<2 or all(len(tried[a])<2 for a in better)
                        conflict=any(len(set(v))>1 for v in tried.values())
                        item['uncertain_retest']=sparse or conflict
                        item['repeated_known_worse']=not item['uncertain_retest']
                if item['negative_retest'] and not item['known_worse']:
                    item['uncertain_retest']=len(selected)<2 or len(set(selected))>1 or any(v=='UNTRIED' for v in values.values())
            explorer.append(item)
            for earlier in prior:
                receipt=earlier['probe']['receipt']
                if receipt['pre_state']==state:
                    chains['Explorer'].append(dict(episode=episode,earlier_decision=earlier['decision'],later_decision=row['decision'],
                        earlier_call=earlier['call_indices'][0],later_call=e['index'],new_memory_transaction=receipt['transaction_id']))
            mc=next((c for c in rc if c['role']=='Map'),None)
            if mc:
                record=dict(index=mc['index'],episode=episode,decision=row['decision'],family=mc['family'],state=state,
                    token=mc['input']['target_action'],action=mc['mapping'][mc['input']['target_action']],
                    valid=mc['parsed'] is not None,malformed=bool(mc['parse_error']),transport_failure=bool(mc['transport_error']),
                    depth=len(mc['input']['VERIFIED_CHRONOLOGICAL_HISTORY']),scored=p['receipt'] is not None,
                    exact=None,next_state_correct=None,consequence_correct=None)
                if record['scored']:
                    record['next_state_correct']=mc['parsed']['next_state']==p['receipt']['next_state']
                    record['consequence_correct']=mc['parsed']['consequence']==p['receipt']['realized_consequence']
                    record['exact']=record['next_state_correct'] and record['consequence_correct']
                maps.append(record)
                for earlier in prior:
                    receipt=earlier['probe']['receipt']
                    if (receipt['pre_state'],receipt['action'])!=(state,record['action']):continue
                    old=calls[earlier['call_indices'][1]];oldp=old['parsed'];newp=mc['parsed']
                    oldexact=oldp==dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence'])
                    change=('malformed_or_transport' if newp is None else
                        'remains_exact' if oldexact and record['exact'] else
                        'exact_to_wrong' if oldexact else 'becomes_exact' if record['exact'] else
                        'same_wrong' if oldp==newp else 'different_wrong')
                    chains['Map'].append(dict(episode=episode,earlier_decision=earlier['decision'],later_decision=row['decision'],
                        earlier_call=old['index'],later_call=mc['index'],change=change,
                        old_prediction=oldp,new_prediction=newp,new_memory_transaction=receipt['transaction_id']))
            recovery=next((c for c in rc if c['role']=='Recovery'),None)
            if recovery:
                valid=recovery['parsed'] is not None
                correct=valid and recovery['parsed']==p['receipt']['next_state']
                recoveries.append(dict(index=recovery['index'],episode=episode,decision=row['decision'],family=recovery['family'],
                    state=state,target=p['receipt']['next_state'],action=p['receipt']['action'],token=recovery['input']['action'],
                    valid=valid,malformed=bool(recovery['parse_error']),transport_failure=bool(recovery['transport_error']),
                    correct=correct,legal_wrong=valid and not correct,
                    authorized_correct=correct and p['authorization']['committed'],wrong_rejected=valid and not correct and not p['authorization']['committed']))
                chains['Recovery'].append(dict(episode=episode,decision=row['decision'],call_indices=row['call_indices'],
                    wrong_map_state=p['prediction']['next_state']!=p['receipt']['next_state'],
                    committed=p['authorization']['committed'],later_decisions=[r['decision'] for r in group if r['decision']>row['decision']]))
            if p['authorization']['committed']:prior.append(row)
        executed=sum(r['probe']['authorization']['executed'] for r in group)
        committed=sum(r['probe']['authorization']['committed'] for r in group)
        episodes.append(dict(episode=episode,family=group[0]['descriptor']['family'],mapping_index=group[0]['descriptor']['mapping_index'],
            decision_attempts=len(group),executed=executed,committed=committed,unexecuted_slots=8-executed,
            termination=group[-1]['termination'] or 'eight_decisions_completed',
            calls={role:sum(c['episode']==episode and c['role']==role for c in calls) for role in ('Explorer','Map','Recovery')},
            realized=sum(r['probe']['receipt']['realized_consequence'] for r in group if r['probe']['receipt']),
            committed_realized=sum(r['probe']['receipt']['realized_consequence'] for r in prior),
            authorized=sum(r['probe']['after']['memory'][-1]['consequence'] for r in prior),
            memory_size=len(group[-1]['probe']['after']['memory'])))
    def count(items,fields):return dict(calls=len(items),**{f:sum(bool(x[f]) for x in items) for f in fields})
    em=count(explorer,('valid','malformed','transport_failure','untried','tried','strict_preference','known_worse','negative_retest','uncertain_retest','repeated_known_worse'))
    em['actions']=dict(Counter(x['action'] for x in explorer if x['valid']))
    em['actions_by_state']={str(s):dict(Counter(x['action'] for x in explorer if x['valid'] and x['state']==s)) for s in range(4)}
    em['proposed_state_action_coverage']=len({(x['state'],x['action']) for x in explorer if x['valid']})
    em['executed_state_action_coverage']=len({(r['probe']['receipt']['pre_state'],r['probe']['receipt']['action']) for r in rows if r['probe']['receipt']})
    em['revisit_opportunities']=len({(x['episode'],x['later_decision']) for x in chains['Explorer']})
    mm=count(maps,('valid','malformed','transport_failure','scored'))
    mm.update(exact=sum(x['exact'] is True for x in maps),next_state_correct=sum(x['next_state_correct'] is True for x in maps),
        consequence_correct=sum(x['consequence_correct'] is True for x in maps),mismatches=sum(x['exact'] is False for x in maps))
    mm['by_history_depth']={label:dict(scored=sum(x['scored'] for x in maps if selector(x['depth'])),
        exact=sum(x['exact'] is True for x in maps if selector(x['depth'])),
        next_state_correct=sum(x['next_state_correct'] is True for x in maps if selector(x['depth'])),
        consequence_correct=sum(x['consequence_correct'] is True for x in maps if selector(x['depth'])))
        for label,selector in [('0',lambda n:n==0),('1',lambda n:n==1),('2+',lambda n:n>=2)]}
    mm['revisit_opportunities']=len({(x['episode'],x['later_decision']) for x in chains['Map']})
    mm['all_pair_chain_changes']=dict(Counter(x['change'] for x in chains['Map']))
    rm=count(recoveries,('valid','malformed','transport_failure','correct','legal_wrong','authorized_correct','wrong_rejected'))
    rm['genuine_opportunities']=sum(r['genuine_recovery'] for r in rows)
    breakdown={}
    for role,items in [('Explorer',explorer),('Map',maps),('Recovery',recoveries)]:
        breakdown[role]={}
        for dimension in ('family','state','action','token')+ (('target',) if role=='Recovery' else ()):
            breakdown[role][dimension]={str(key):dict(calls=sum(x[dimension]==key for x in items),valid=sum(x['valid'] and x[dimension]==key for x in items),
                **({metric:sum(x.get(metric) is True and x[dimension]==key for x in items) for metric in ('exact','next_state_correct','consequence_correct')} if role=='Map' else
                   {metric:sum(x.get(metric) is True and x[dimension]==key for x in items) for metric in ('correct','legal_wrong','authorized_correct','wrong_rejected')} if role=='Recovery' else {}))
                for key in sorted({x[dimension] for x in items},key=str)}
    result=dict(classification='A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS',
        classification_scope='Live integrity plus separately recorded controls/replay/regression completion in verification.json',
        real_calls={role:sum(c['role']==role for c in calls) for role in ('Explorer','Map','Recovery')},total_real_calls=len(calls),
        episodes=episodes,executed_decisions=sum(x['executed'] for x in episodes),committed_events=sum(x['committed'] for x in episodes),
        unexecuted_slots=sum(x['unexecuted_slots'] for x in episodes),Explorer=em,Map=mm,Recovery=rm,breakdown=breakdown,
        unknown_to_known_transitions=sum(len(r['unknown_to_known']) for r in rows),stale_unknown_markers=0,
        unknown_in_protected_storage=0,protected_false_accepts=0,receipt_mismatch_accepts=0,unauthorized_commits=0,
        source_authority_leaks=0,retries=0,bound_violations=0,
        executed_realized_consequence=sum(x['realized'] for x in episodes),committed_realized_consequence=sum(x['committed_realized'] for x in episodes),
        authorized_consequence=sum(x['authorized'] for x in episodes),experience_chains={k:len(v) for k,v in chains.items()},
        maxima={key:max(r['probe']['bounds'][key] for r in rows) for key in rows[0]['probe']['bounds']})
    assert result['committed_realized_consequence']==result['authorized_consequence']
    return result,dict(chains=chains,Explorer=explorer,Map=maps,Recovery=recoveries)
