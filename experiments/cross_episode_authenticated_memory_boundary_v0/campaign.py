"""Bounded deterministic diagnostics. No new reset API or authority mechanism."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import inspect
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from experiments.base_framework_v1.framework import MEMORY_LIMIT, PAIR_LIMIT, EPOCH_LIMIT, AUTHORIZATION_LIMIT
from experiments.realized_event_grounding_v0.campaign import TestWorld, execute, published
from experiments.realized_event_grounding_v0.framework import evidence, PACKAGE_LIMIT
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary, EXECUTION_LIMIT
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework, StatusBoundAuthorizer
from experiments.composition_input_bindings_v1.adapters import explorer_payload, map_payload, serialize

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=Path(__file__).parent
PARENT='46d01e1e6d09a24191aea1ddf9e413f04711b14b'
E=1001
MAPPING={'K1':'ADVANCE','K2':'HOLD','K3':'RETREAT'}


def encoded(value):return json.dumps(value,sort_keys=True,indent=2)+'\n'
def sha(value):return hashlib.sha256(value).hexdigest()
def frozen():
    r=json.loads((PACKAGE/'frozen-inputs.json').read_text())
    for name,digest in r['sha256'].items():assert sha((ROOT/name).read_bytes())==digest,name
    return r


def setup(name):
    world=TestWorld(0,False)
    source=ExternalExecutionBoundary(world,'CROSS_EPISODE_BOUNDARY_'+name)
    return StatusBoundFramework(source.reader(),0,E),source,world


def snapshot(system,source,world):
    return dict(protected=published(system),world_state=world.oracle.state,world_executions=world.oracle.execution_count,
        epoch=system.inner.epoch,epochs_started=system.inner.epochs_started,next_transaction_id=system.inner.next_transaction_id,
        episode_steps=system.inner.episode_steps,continuation=system.inner.continuation_authorized,
        authorization_keys=sorted(system.inner.state_authorizer.authorized),
        authorizer_type=type(system.inner.state_authorizer).__name__,pending_core=system.inner.pending is not None,
        pending_root=int(source.reader().current() is not None),evictions=system.inner.memory.evictions)


def views(system,state=0,records=None):
    records=system.inner.memory.records if records is None else records
    return dict(Explorer=explorer_payload(state,records,MAPPING),
        Map={a:map_payload(state,a,records,MAPPING) for a in MAPPING.values()})


def audit(system,authentic):
    system.assert_bounds();rows=[]
    for p,d,m in zip(system.packages,system.inner.pairs.decisions,system.inner.memory.records):
        assert authentic[p.receipt.identity()] is p.receipt
        assert p.package_id==p.receipt.identity() and p.pair_decision_id==d.pair_decision_id==m.pair_decision_id
        assert system.inner.memory.matches(m,d)
        rows.append(dict(package_id=p.package_id,pair_id=d.pair_decision_id,
            memory_identity=(m.epoch,m.transaction_id,m.pair_decision_id),receipt=asdict(p.receipt),
            exact_original_receipt_object=True,full_binding_verified=True))
    return rows


def commit(bundle,action,authentic):
    system,source,world=bundle
    row,receipt=execute(system,source,world,action)
    assert row['result']['committed'] and not row['actual_mismatch_accept'] and not row['receipt_mismatch_accept']
    assert row['old_records_unchanged'] and row['prediction_unchanged']
    authentic[receipt.identity()]=receipt
    assert source.reader().current() is None
    row['retained_provenance']=audit(system,authentic)
    return row,receipt


def carry_fixture():
    bundle=setup('SAME_LIFETIME');s,source,world=bundle;authentic={};rows=[]
    actions=('HOLD','ADVANCE','RETREAT','HOLD')
    for action in actions:row,_=commit(bundle,action,authentic);rows.append(row)
    old=deepcopy(published(s));old_receipts=[p.receipt for p in s.packages]
    before=snapshot(*bundle);prior_view=views(s)
    assert before['world_state']==before['protected']['map']['state']==0
    s.start_epoch(E+1)
    after=snapshot(*bundle);boundary_view=views(s)
    assert all(after['protected'][k]==old[k] for k in ('memory','pairs','packages'))
    assert all(p.receipt is r for p,r in zip(s.packages,old_receipts))
    assert before['world_executions']==after['world_executions']==4
    assert after['next_transaction_id']==1 and after['episode_steps']==0 and after['authorization_keys']==[]
    assert after['authorizer_type']=='StatusBoundAuthorizer' and after['continuation']
    assert prior_view==boundary_view
    assert boundary_view['Explorer']['actions'][2]['verified_outcomes']=='UNTRIED'
    assert boundary_view['Map']['RETREAT']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
    assert boundary_view['Map']['HOLD']['VERIFIED_CHRONOLOGICAL_HISTORY']
    audit(s,authentic)
    for action in actions:row,_=commit(bundle,action,authentic);rows.append(row)
    at_eight=snapshot(*bundle);mixed=views(s);assert len(s.inner.memory.records)==8
    assert published(s)['memory'][:4]==old['memory']
    assert encoded(views(s,records=list(reversed(s.inner.memory.records))))==encoded(mixed)
    ordered_hold=[(r.epoch,r.transaction_id) for r in s.inner.memory.records if r.pre_state==0 and r.action=='HOLD']
    assert ordered_hold==[(E,1),(E,4),(E+1,1),(E+1,4)]
    all_ids=[(r['record']['epoch'],r['record']['transaction_id'],r['record']['pair_decision_id']) for r in rows]
    assert len(set(all_ids))==8
    before_ninth=deepcopy(published(s));ninth,_=commit(bundle,'HOLD',authentic);rows.append(ninth)
    final=snapshot(*bundle)
    assert final['protected']['memory'][:-1]==before_ninth['memory'][1:]
    assert final['protected']['pairs'][:-1]==before_ninth['pairs'][1:]
    assert final['protected']['packages'][:-1]==before_ninth['packages'][1:]
    assert final['evictions']==1 and len(s.inner.memory.records)==8
    ids=[r['receipt'] for r in rows]
    assert [r['event_id'] for r in ids]==list(range(1,10))
    assert len({tuple(r[k] for k in ('source_identity','event_id','epoch','transaction_id')) for r in ids})==9
    assert len({r['record']['pair_decision_id'] for r in rows})==9
    assert 'UNTRIED' not in encoded(final['protected'])
    return dict(interpretation='SAME_SOURCE_LIFETIME_E1001_TO_E1002_NO_STATE_RESET',
        complete_requested_reset_fixture=False,naturally_returns_to_zero=True,
        boundary_before=before,boundary_after=after,prior_view=prior_view,boundary_view=boundary_view,
        at_eight=at_eight,mixed_views=mixed,ordered_hold_identities=ordered_hold,reverse_input_projection_stable=True,
        after_ninth=final,evicted_record=before_ninth['memory'][0],evicted_pair=before_ninth['pairs'][0],
        evicted_package=before_ninth['packages'][0],rows=rows,
        historical_receipt_objects_survive=True,all_event_pair_full_identities_unique=True,
        original_history_content_unchanged_until_fifo_eviction=True)


def state_reset_probe():
    bundle=setup('NONZERO_RESET');s,source,world=bundle;authentic={}
    for action in ('HOLD','ADVANCE'):commit(bundle,action,authentic)
    before=snapshot(*bundle);assert before['world_state']==before['protected']['map']['state']==1
    s.start_epoch(E+1);after=snapshot(*bundle)
    assert after['world_state']==after['protected']['map']['state']==1
    assert before['protected']['memory']==after['protected']['memory']
    try:s.start_epoch(E+2,initial_state=0)
    except TypeError as exc:unsupported=str(exc)
    else:raise AssertionError('new reset API unexpectedly exists')
    fresh=setup('FRESH_INSTANCE');fresh_state=snapshot(*fresh)
    assert fresh_state['world_state']==fresh_state['protected']['map']['state']==0
    assert not fresh_state['protected']['memory'] and not fresh_state['protected']['pairs'] and not fresh_state['protected']['packages']
    return dict(before=before,after_epoch=after,fresh_instance=fresh_state,
        fresh_zero_with_retained_history_supported=False,start_epoch_signature=str(inspect.signature(s.start_epoch)),
        reset_parameter_rejected=unsupported,manual_state_rewrite_attempted=False,
        conclusion='Existing epoch boundary retains history but does not initialize world/current state to zero; fresh constructor discards history.')


def guards():
    rows=[]
    for mode in ('same_epoch','third_epoch','pending_core','pending_root'):
        bundle=setup('GUARD_'+mode);s,source,world=bundle;target=E+1;receipt=None
        if mode=='same_epoch':target=E
        elif mode=='third_epoch':s.start_epoch(E+1);target=E+2
        else:
            p=s.begin_step(forced_action='HOLD')
            if mode=='pending_root':receipt=source.execute(p.epoch,p.transaction_id,p.action)
        before=snapshot(*bundle)
        try:s.start_epoch(target)
        except (RuntimeError,ValueError) as exc:error=str(exc)
        else:raise AssertionError('invalid epoch boundary accepted')
        after=snapshot(*bundle);assert before==after
        if receipt is not None:source.release(receipt)
        rows.append(dict(mode=mode,rejected=True,reason=error,state_unchanged=True,before=before,after=after))
    return rows


def rejection_controls():
    rows=[]
    for mode in ('old_receipt_after_epoch','equal_copy_of_current_receipt','missing_pairs','missing_packages'):
        bundle=setup('REJECTION_'+mode);s,source,world=bundle;authentic={}
        _,old=commit(bundle,'HOLD',authentic);s.start_epoch(E+1)
        if mode.startswith('missing_'):
            if mode=='missing_pairs':s.inner.pairs.decisions=[]
            else:s.packages=[]
            before=published(s);result=s.begin_step(forced_action='HOLD');receipt=None
        else:
            p=s.begin_step(forced_action='HOLD');receipt=source.execute(p.epoch,p.transaction_id,p.action)
            before=published(s);candidate=old if mode=='old_receipt_after_epoch' else replace(receipt)
            result=s.submit_package(evidence(candidate))
        assert not result.committed and published(s)==before
        assert not s.inner.continuation_authorized
        if receipt is not None:source.release(receipt)
        rows.append(dict(mode=mode,rejected=True,reason=result.reason,no_partial_publication=True,
            scope='throwaway negative control; detached state is never used as a retention design'))
    return rows


def lifetime_diagnostic():
    systems=[]
    for name in ('LIFETIME_A','LIFETIME_B'):
        b=setup(name);row,r=commit(b,'HOLD',{});systems.append((row,r))
    a,b=systems
    same_record_key=tuple(a[0]['record'][k] for k in ('epoch','transaction_id','pair_decision_id'))==tuple(b[0]['record'][k] for k in ('epoch','transaction_id','pair_decision_id'))
    assert same_record_key and a[1].identity()!=b[1].identity()
    return dict(fresh_instances_restart_epoch_transaction_event=True,core_memory_pair_key_would_collide_if_naively_combined=same_record_key,
        complete_receipt_package_ids_differ=True,earlier_receipt=asdict(a[1]),later_receipt=asdict(b[1]),
        histories_combined=False,registered_carryover_uses_same_lifetime_and_new_epoch=True,
        source_uniqueness_is_driver_obligation_not_global_registry=True)


def contradiction_projection(path):
    reg=frozen();assert sha(path.read_bytes())==reg['historical_setup_sha256']
    fixture=next(json.loads(line) for line in path.read_text().splitlines() if json.loads(line)['call_index']==2 and json.loads(line)['setup_step']==3)
    step=fixture['step'];records=step['after']['memory'];assert [r['consequence'] for r in records]==[1,1,-1]
    assert step['authorization']['committed'] and step['old_history_unchanged'] and step['receipt_unchanged']
    for record,p in zip(records,step['provenance']):
        assert p['full_binding_verified'] and p['exact_authentic_object']
        assert all(record[k]==p['receipt'][k] for k in ('epoch','transaction_id','pre_state','action','next_state'))
        assert record['consequence']==p['receipt']['realized_consequence']
    digest=sha(encoded(records).encode());rs=[SimpleNamespace(**r) for r in records]
    payload=map_payload(1,'HOLD',rs,MAPPING)
    assert [r['consequence'] for r in payload['VERIFIED_CHRONOLOGICAL_HISTORY']]==[1,1,-1]
    assert digest==sha(encoded(records).encode())
    return dict(source_call_index=2,setup_step=3,source_file_sha256=reg['historical_setup_sha256'],
        history=records,provenance=step['provenance'],projection=payload,original_records_unchanged=True,
        grouping_metadata=[dict(group='earlier',transaction_ids=[1,2]),dict(group='later',transaction_ids=[3])],
        observed_consequences=[1,1,-1],new_regime_executed=False,epochs_relabelled=False,
        scope='Read-only representation control from existing authenticated SHIFT archive. Group labels are diagnostic metadata only; not evidence of a new reset or new cross-epoch contradiction.')


def run(contradiction_source):
    frozen()
    with patch('socket.socket',side_effect=AssertionError('network/model I/O forbidden')) as network:
        carry=carry_fixture();reset=state_reset_probe();boundary_guards=guards();negative=rejection_controls()
        lifetime=lifetime_diagnostic();contradiction=contradiction_projection(contradiction_source)
        assert network.call_count==0
    invariants=dict(prior_authenticated_records_unchanged=True,provenance_traceable=True,
        no_identity_collision_in_registered_same_lifetime_epochs=True,
        fresh_zero_current_state_without_history_rewrite=reset['fresh_zero_with_retained_history_supported'],
        known_retained_pairs_not_UNKNOWN=True,untouched_pairs_remain_UNKNOWN=True,
        new_observations_append_chronologically=True,no_boundary_fake_event=True,memory_bound_8=True,
        ordinary_eviction_unchanged=True,pending_authentic_receipt_at_most_1=True,receipt_authority_unchanged=True,
        Measure_unchanged=True,Recovery_unchanged=True,no_model_chat_persistence=True,
        exact_replay=None,historical_regressions=None)
    details=dict(carry_fixture=carry,state_reset_probe=reset,boundary_guards=boundary_guards,
        rejection_controls=negative,lifetime_diagnostic=lifetime,contradiction_representation=contradiction)
    result=dict(study='cross-episode-authenticated-memory-boundary-v0',parent=PARENT,actual_model_calls=0,
        network_attempts=0,ollama_started=False,core_changes=False,classification='C — NOT ESTABLISHED',
        missing_property='No existing supported boundary resets a nonzero world/current authorized state to zero while preserving authenticated history.',
        semantic_failures_in_supported_epoch_boundary=[],invariants=invariants,
        registered_source_lifetime='same external source across E=1001 to E+1=1002',
        complete_requested_two_episode_reset_fixture=False,limited_epoch_continuity_fixture_completed=True,
        basic_commits_by_group=[4,4],ninth_commit=True,ordinary_fifo_evictions=1,
        evicted_memory_identity=[E,1,carry['evicted_record']['pair_decision_id']],
        capacities=dict(memory=MEMORY_LIMIT,pairs=PAIR_LIMIT,packages=PACKAGE_LIMIT,epochs=EPOCH_LIMIT,
            authorization_per_epoch=AUTHORIZATION_LIMIT,source_executions_lifetime=EXECUTION_LIMIT,pending_authentic=1),
        cases=dict(epoch_carry_and_ninth=1,nonzero_reset=1,epoch_guards=len(boundary_guards),authority_negative_controls=len(negative),new_lifetime_key_diagnostic=1,archived_contradiction_representation=1),
        projection_limitation='Map output sorts by (epoch, transaction_id) but exposes transaction_id only; repeated displayed IDs are not globally identifying.',
        chronology=carry['ordered_hold_identities'],contradiction_control_scope=contradiction['scope'],
        final_assurance_pending=True,details_sha256=sha(encoded(details).encode()))
    assert len(invariants)==17
    return result,details
