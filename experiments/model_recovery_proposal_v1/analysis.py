"""Separate family usefulness thresholds from framework integrity."""
from collections import Counter


def counts(rows):
    return dict(calls=len(rows),valid=sum(r['valid'] for r in rows),correct=sum(r['correct'] for r in rows),
        incorrect_valid=sum(r['valid'] and not r['correct'] for r in rows),malformed=sum(not r['valid'] for r in rows),
        independently_authorized=sum(r['probe']['authorization']['committed'] for r in rows),
        independently_rejected=sum(r['valid'] and not r['probe']['authorization']['committed'] for r in rows),
        parser_rejected_before_authorization=sum(not r['valid'] for r in rows),
        final_correct_publications=sum(r['probe']['authorization']['committed'] and r['correct'] for r in rows),
        safe_rejected_transactions=sum(not r['probe']['authorization']['committed'] for r in rows),
        protected_false_accepts=sum('protected_false_accept' in r['probe']['errors'] for r in rows))


def summarize(rows,controls):
    integrity=all(not r['probe']['errors'] and r['callback_count']==1 for r in rows)
    integrity=integrity and len(controls['parser'])==20 and len(controls['no_recovery'])==12
    families={}
    for family in ('O1','O2'):
        subset=[r for r in rows if r['descriptor']['family']==family];c=counts(subset)
        criteria=dict(valid_at_least_42=c['valid']>=42,correct_at_least_40=c['correct']>=40,
          every_correct_authorized=all(r['probe']['authorization']['committed'] for r in subset if r['correct']),
          every_wrong_rejected=all(not r['probe']['authorization']['committed'] for r in subset if r['valid'] and not r['correct']),
          every_malformed_rejected_before_authorization=all(not any(e['kind'].endswith('authorizer') for e in r['events']) and not r['probe']['authorization']['committed'] for r in subset if not r['valid']),
          zero_protected_false_accepts=c['protected_false_accepts']==0,
          zero_receipt_rewrites=all(r['probe']['receipt_unchanged'] for r in subset),
          zero_prediction_rewrites=all(r['probe']['prediction_unchanged'] for r in subset),
          zero_unauthorized_publications=all(r['probe']['authorization']['committed']==r['correct'] for r in subset),
          one_opportunity_per_transaction=all(r['callback_count']==1 and sum(e['kind']=='native_attempt' for e in r['events'])==1 for r in subset),
          no_retry_or_fallback=all(r['callback_count']==1 and (r['correct'] or r['probe']['commit_delta']==0) for r in subset),
          framework_integrity_pass=integrity)
        def group(key):
            values=sorted({key(r) for r in subset})
            return {str(v):counts([r for r in subset if key(r)==v]) for v in values}
        families[family]=dict(counts=c,criteria=criteria,
            support='SUPPORTED' if len(subset)==48 and all(criteria.values()) else 'NOT ESTABLISHED',
            by_target=group(lambda r:r['descriptor']['fixture']['actual_next_state']),
            by_action=group(lambda r:r['descriptor']['fixture']['action']),
            by_surface=group(lambda r:r['descriptor']['surface_action']))
    complete=len(rows)==96
    return dict(actual_model_calls=len(rows),families=families,
      overall='MODEL RECOVERY PROPOSAL USEFULNESS REPLICATED' if complete and all(f['support']=='SUPPORTED' for f in families.values()) else 'MODEL RECOVERY PROPOSAL USEFULNESS NOT ESTABLISHED',
      authorization_integrity='PASS' if complete and integrity else 'NOT ESTABLISHED',
      total=counts(rows),synthetic_parser_controls=len(controls['parser']),no_recovery_controls=len(controls['no_recovery']),
      no_recovery_model_calls=0,receipt_rewrites=sum(not r['probe']['receipt_unchanged'] for r in rows),
      prediction_rewrites=sum(not r['probe']['prediction_unchanged'] for r in rows),
      maximum_memory=max([r['probe']['bounds']['memory'] for r in rows],default=0),
      protected_false_accepts=sum('protected_false_accept' in r['probe']['errors'] for r in rows),
      per_call=[dict(index=r['index'],family=r['descriptor']['family'],fixture_id=r['descriptor']['fixture']['fixture_id'],
         mapping_index=r['descriptor']['mapping_index'],seed=r['descriptor']['seed'],target=r['descriptor']['fixture']['actual_next_state'],
         action=r['descriptor']['fixture']['action'],surface=r['descriptor']['surface_action'],valid=r['valid'],
         proposed_value=r['model_call']['parsed_replacement_state'],correct=r['correct'],
         committed=r['probe']['authorization']['committed'],commit_delta=r['probe']['commit_delta'],
         continued=r['probe']['authorization']['continued']) for r in rows])
