"""Inherited descriptive metrics plus explicit integrity and live-path coverage."""
from collections import Counter
import json
from .runtime import views, records
from .protocol import SYSTEMS, OPTIONS, MODEL, schedule, seed
from experiments.model_proposal_role_composition_v1.analysis import summarize as old_summary
from experiments.model_recovery_proposal_v1.adapter import render as recovery_render
from experiments.model_map_proposal_v0.adapter import serialize
from types import SimpleNamespace

A='A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS'
B='B — MULTI-ROLE AUTHORITY FAILURE'
C='C — NOT ESTABLISHED'


def summarize(rows,calls,baseline):
    result,chains=old_summary(rows,calls)
    checks={k:True for k in ('zero_protected_false_accepts','zero_receipt_mismatch_accepts','zero_unauthorized_commits',
        'zero_stale_duplicate_authorizations','zero_model_identity_status_authority','all_predictions_latched',
        'all_commits_authentic','genuine_recovery_only','correct_recovery_accepts','legal_wrong_recovery_rejects',
        'malformed_at_role_boundary','atomic_recovery_rejection','no_recovery_retry_fallback','no_raw_cross_role_leakage',
        'no_direct_protected_mutation','no_prediction_history_receipt_rewrite','unknown_is_not_memory','inherited_bounds')}
    commits=set();source_events={};unknown_transitions=[];request_audit=[];recovery_auth=[]
    descriptors=schedule()
    for row in rows:
        p=row['probe'];ep=row['episode'];d=descriptors[ep];state=p['before']['map']['state'];rc=[calls[i] for i in row['call_indices']]
        assert not p['errors'] and row['unknown_audit_pass']
        assert row['descriptor']==d
        before=views(state,p['before'],d['mapping']);after=views(state,p['after'],d['mapping'])
        for snapshot in (p['before'],p['after']):
            assert 'UNTRIED' not in json.dumps(snapshot)
            assert all(type(r['consequence']) is int and type(r['next_state']) is int for r in snapshot['memory'])
        assert p['old_history_unchanged'] and p['prediction_unchanged'] and p['receipt_unchanged']
        for call in rc:
            assert call['system']==SYSTEMS[call['role']] and call['model']==MODEL
            assert call['options']=={**OPTIONS[call['role']],'seed':seed(d,row['decision'],call['role'])}
            assert call['memory']==p['before']['memory'] and call['mapping']==d['mapping']
            if call['role']=='Explorer':expected=serialize(before['Explorer'])
            elif call['role']=='Map':expected=serialize(before['Map'][d['mapping'][call['input']['target_action']]])
            else:
                context=next(e['context'] for e in row['events'] if e['kind']=='proposal')
                # render consumes the same immutable field context as the callback.
                expected=recovery_render(SimpleNamespace(**context),d['mapping'])
            assert call['exact_prompt']==expected and call['input']==json.loads(expected)
            request_audit.append(dict(index=call['index'],role=call['role'],structured_projection_exact=True,
                only_finite_role_output_crosses_boundary=True,model_context_reused=False))
        if p['authorization']['executed']:
            assert p['latched_before_execution']
            assert p['prediction']['action']==p['receipt']['action']==rc[0]['parsed']['action']
        if p['authorization']['committed']:
            receipt=p['receipt'];record=p['after']['memory'][-1]
            key=(ep,receipt['epoch'],receipt['transaction_id']);assert key not in commits;commits.add(key)
            for field in ('epoch','transaction_id','pre_state','action','next_state'):assert record[field]==receipt[field]
            assert record['consequence']==receipt['realized_consequence'] and record['authorization']=='AUTHORIZED'
            assert all(x['exact_authentic_object'] and x['full_binding_verified'] for x in p['provenance'])
            source_events[key]=row['decision']
        if row['termination']:
            assert p['before']==p['after'] and not p['authorization']['committed'] and not p['authorization']['continued']
        malformed=[c for c in rc if c['parse_error']]
        if malformed:assert p['authorization']['executed']==(malformed[0]['role']=='Recovery')
        if row['genuine_recovery']:
            recovery=rc[-1];assert recovery['role']=='Recovery'
            auth=[e for e in row['events'] if e['kind']=='status_authorizer'];native=next(e for e in row['events'] if e['kind']=='native_attempt')
            assert len(auth)==int(recovery['parsed'] is not None)
            for event in auth:
                assert event['scope'] and event['accepted']==(recovery['parsed']==p['receipt']['next_state'])
                assert event['accepted']==p['authorization']['committed']
                for field in ('epoch','transaction_id','pair_decision_id','status'):assert event['candidate'][field]==native['candidate'][field]
                recovery_auth.append(dict(episode=ep,decision=row['decision'],call=recovery['index'],accepted=event['accepted'],correct=recovery['parsed']==p['receipt']['next_state']))
            assert native['attempts']==1
        for transition in row['unknown_to_known']:
            assert transition['before_explorer']['verified_outcomes']=='UNTRIED' and transition['before_map']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
            assert transition['after_explorer']['verified_outcomes'] and transition['after_map']['VERIFIED_CHRONOLOGICAL_HISTORY']
            unknown_transitions.append(dict(episode=ep,decision=row['decision'],**transition))
    # Paths must be model-visible live inputs, not synthetic post-commit projections.
    explorer_evidence=[];map_evidence=[];later_after_commit=[];consumption=[]
    for c in calls:
        prior=[r for r in rows if r['episode']==c['episode'] and r['decision']<c['decision'] and r['probe']['authorization']['committed']]
        if prior:later_after_commit.append(c['index'])
        if c['role']=='Explorer' and any(isinstance(a['verified_outcomes'],list) and a['verified_outcomes'] for a in c['input']['actions']):explorer_evidence.append(c['index'])
        if c['role']=='Map' and c['input']['VERIFIED_CHRONOLOGICAL_HISTORY']:
            history=c['input']['VERIFIED_CHRONOLOGICAL_HISTORY'];action=c['mapping'][c['input']['target_action']]
            earlier=[r for r in prior if r['probe']['receipt']['pre_state']==c['current_state'] and r['probe']['receipt']['action']==action]
            assert earlier and any(calls[r['call_indices'][1]]['input']['VERIFIED_CHRONOLOGICAL_HISTORY']==[] for r in earlier)
            map_evidence.append(c['index'])
        if c['index'] in explorer_evidence+map_evidence:
            assert prior
            for record in c['memory']:
                key=(c['episode'],record['epoch'],record['transaction_id']);assert key in source_events and source_events[key]<c['decision']
            consumption.append(c['index'])
    coverage=dict(A_external_execution=bool(result['executed_decisions']),B_authentic_memory_commit=bool(commits),
        C_later_decision_after_commit=bool(later_after_commit),D_live_explorer_absence_to_evidence=bool(explorer_evidence),
        E_live_map_empty_to_same_pair_history=bool(map_evidence),F_later_proposal_consumes_same_episode_memory=bool(consumption),
        G_genuine_live_recovery_reaches_authorizer=bool(recovery_auth))
    matched=[]
    for old in baseline:
        candidates=[c for c in calls if c['episode']==old['episode'] and c['decision']==old['decision'] and c['role']=='Map']
        now=candidates[0] if candidates else None
        exact=now is not None and all(now[k]==old[k] for k in ('exact_prompt','mapping','current_state','options','model'))
        matched.append(dict(episode=old['episode'],family=old['family'],v1_call=old['index'],v1_valid=old['parsed'] is not None,
            v2_reached=now is not None,v2_exact_context=exact,v2_call=now['index'] if now else None,
            v2_valid=now['parsed'] is not None if exact else None,
            unavailable_reason=None if exact else 'Explorer terminated before Map' if now is None else 'admitted action/context differs; unmatched'))
    maps=chains['Map'];empty=[m for m in maps if m['depth']==0]
    result['Map']['empty_history_schema_compliance']=dict(calls=len(empty),valid=sum(m['valid'] for m in empty),malformed=sum(m['malformed'] for m in empty))
    for label,select in [('0',lambda n:n==0),('1',lambda n:n==1),('2+',lambda n:n>=2)]:
        items=[m for m in maps if select(m['depth'])]
        result['Map']['by_history_depth'][label].update(calls=len(items),valid=sum(m['valid'] for m in items),malformed=sum(m['malformed'] for m in items),mismatches=sum(m['exact'] is False for m in items))
    result.update(classification=C,classification_status='PROVISIONAL: exact replay and historical regressions pending',
        live_eligible_classification=A if all(checks.values()) and all(coverage.values()) else C,
        classification_scope='Final A requires all 20 integrity requirements and all seven live paths; finalization follows replay/regressions.',
        integrity_requirements={**checks,'exact_replay_passes':None,'historical_regressions_pass':None},
        live_path_coverage=coverage,missing_live_paths=[k for k,v in coverage.items() if not v],
        live_path_witnesses=dict(explorer_evidence_calls=explorer_evidence,map_history_calls=map_evidence,later_calls_after_commit=later_after_commit,
            same_episode_memory_consumption=consumption,recovery_authorizations=recovery_auth),
        matched_v1_v2_format=matched,raw_cross_role_leaks=0,stale_duplicate_authorizations=0,
        model_originated_identity_status=0,initial_absence_projection_count=12)
    chains.update(unknown_transitions=unknown_transitions,request_projection_audit=request_audit)
    return result,chains
