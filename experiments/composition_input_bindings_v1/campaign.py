"""Deterministic input-binding and composed-transaction evidence. No inference."""
from copy import deepcopy
from dataclasses import asdict
from itertools import permutations
import json

from experiments.base_framework_v0.framework import MapModel
from experiments.base_framework_v1.framework import PairDecision
from experiments.model_explorer_semantic_prior_study_v0.adapter import render as old_explorer_render
from experiments.model_map_proposal_v0.adapter import render as old_map_render, INVALID as MAP_INVALID
from experiments.model_map_proposal_v0.boundary import execute
from experiments.model_recovery_proposal_v0.diagnostic import FixedExplorer
from experiments.model_recovery_proposal_v1.adapter import RecoveryProposer, render as recovery_render, INVALID as RECOVERY_INVALID
from experiments.model_recovery_proposal_v1.campaign import observe
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
from experiments.state_recovery_proposal_interface_v1.framework import DecisionContext, RecoveryOpportunity
from .adapters import ACTIONS, FAMILIES, ExplorerBinding, MapBinding, explorer_payload, map_payload, serialize


def mappings():
    return [(f'O{family+1}', index, dict(zip(tokens, actions)))
            for family, tokens in enumerate(FAMILIES)
            for index, actions in enumerate(permutations(ACTIONS))]


def encoded(value): return json.dumps(value, indent=2, sort_keys=True) + '\n'


class Tape:
    """Only string/scalar I/O, with exact recorded synthetic response replay."""
    def __init__(self, replay=None): self.calls, self.replay = [], replay

    def source(self, name, role, raw, forbid=False):
        return Source(self, name, role, raw, forbid)

    def done(self):
        if self.replay is not None: assert len(self.calls) == len(self.replay)


class Source:
    def __init__(self, tape, name, role, raw, forbid):
        self.tape, self.name, self.role, self.raw, self.forbid = tape, name, role, raw, forbid
        self.calls = 0

    def generate(self, prompt, seed):
        self.calls += 1
        if self.forbid: raise AssertionError('unexpected Recovery source invocation')
        assert type(prompt) is str and type(seed) is int
        raw = self.raw
        row = dict(case=self.name, role=self.role, seed=seed, prompt=prompt,
                   input=json.loads(prompt), raw_response=raw, synthetic=True)
        if self.tape.replay is not None:
            prior = self.tape.replay[len(self.tape.calls)]
            raw = prior['raw_response']
            row['raw_response'] = raw
            assert row == prior
        self.tape.calls.append(row)
        return raw, {'synthetic': True}


def setup(state, name):
    world = TestWorld(state, False)
    source = ExternalExecutionBoundary(world, name)
    return StatusBoundFramework(source.reader(), state, 1001), source, world, {}


def ordinary(bundle, action):
    system, source, world, authentic = bundle
    system.inner.explorer = FixedExplorer(action)
    row = execute(system, source, world, authentic)
    assert not row['errors'] and row['authorization']['committed']
    return row


def expected(state, action):
    # Test-only source schedule, never a renderer/transport input or authority.
    p = MapModel.predict_from(state, action, 1001, 1)
    return dict(next_state=p.next_state, consequence=p.consequence)


def composed(bundle, tape, name, mapping, action, *, prediction=None,
             recovery_value=None, explorer_raw=None, map_raw=None, recovery_raw=None,
             instrument=True):
    system, source, world, authentic = bundle
    state, tx = system.inner.map.current.state, system.inner.next_transaction_id
    truth = expected(state, action)
    prediction = truth if prediction is None else prediction
    genuine = truth['next_state'] != state and prediction != truth
    alias = next(k for k, v in mapping.items() if v == action)
    explorer_raw = ' \n' + alias + '\n ' if explorer_raw is None else explorer_raw
    map_raw = '\n' + serialize(prediction) + ' \n' if map_raw is None else map_raw
    value = truth['next_state'] if recovery_value is None else recovery_value
    recovery_raw = '\n' + serialize(dict(replacement_state=value)) + '\n' if recovery_raw is None else recovery_raw
    e = tape.source(name, 'Explorer', explorer_raw)
    m = tape.source(name, 'Map', map_raw)
    r = tape.source(name, 'Recovery', recovery_raw, forbid=not genuine)
    context = DecisionContext(1001, tx, 0, state, action, truth['next_state'], truth['consequence'], False)
    recovery = RecoveryProposer(r, dict(mapping=mapping, seed=90000+tx*10+3,
        exact_prompt=recovery_render(context, mapping), index=tx))
    system.inner._state_recovery_source = recovery
    system.inner.explorer = ExplorerBinding(e, mapping, 90000+tx*10+1)
    base = system.inner.map.base if isinstance(system.inner.map, MapBinding) else system.inner.map
    system.inner.map = MapBinding(base, system.inner.memory, m, mapping, 90000+tx*10+2)
    before_calls = len(tape.calls)
    with observe(instrument) as events:
        row = execute(system, source, world, authentic, instrument=False)
    assert not row['errors'], row['errors']
    assert system.inner.map.memory is system.inner.memory, 'staging detached Memory reference'
    calls = tape.calls[before_calls:]
    # Compare exact inputs to authoritative before snapshots, never to a transcript.
    records_before = row['before']['memory']
    from types import SimpleNamespace
    records = [SimpleNamespace(**record) for record in records_before]
    assert calls[0]['input'] == explorer_payload(state, records, mapping)
    if m.calls:
        assert calls[1]['input'] == map_payload(state, action, records, mapping)
        assert calls[1]['input']['target_action'] == alias
    if r.calls:
        receipt = row['receipt']
        assert calls[-1]['input'] == dict(pre_state=state, action=alias,
            VERIFIED_REALIZED_EVENT=dict(next_state=receipt['next_state'],consequence=receipt['realized_consequence']),
            measurement_matches=False, allowed_replacement_states=[0,1,2,3])
        assert recovery.invocations == r.calls == 1
    if row['authorization']['executed']:
        assert row['latched_before_execution'] and row['prediction_unchanged'] and row['receipt_unchanged']
        assert row['receipt']['action'] == action and row['prediction']['action'] == action
        if instrument:
            assert any(x['kind']=='measure' and x['verified'] for x in events)
    if r.calls and instrument:
        kinds=[x['kind'] for x in events]
        positions=[kinds.index(k) for k in ('receipt','measure','quarantine','native_attempt','model_proposal')]
        assert positions == sorted(positions)
        assert kinds.count('native_attempt') == kinds.count('model_proposal') == 1
        native=next(x for x in events if x['kind']=='native_attempt')
        assert native['attempts'] == 1 and native['candidate']['status'] == 'RECOVERING'
        for auth in (x for x in events if x['kind']=='status_authorizer'):
            assert auth['state_recovery'] is True
            assert auth['accepted'] == row['authorization']['committed']
            for field in ('epoch','transaction_id','pair_decision_id','status'):
                assert auth['candidate'][field] == native['candidate'][field]
    no_next_request = None
    if not row['authorization']['committed']:
        assert row['before']==row['after'] and row['commit_delta']==0
        assert not row['authorization']['continued']
        count=len(tape.calls); protected=published(system)
        retry=system.begin_step()
        assert not retry.executed and not retry.committed and not retry.continued
        assert len(tape.calls)==count and published(system)==protected
        no_next_request=True
    return dict(name=name, mapping=mapping, events=events, probe=row,
        calls=dict(Explorer=e.calls,Map=m.calls,Recovery=r.calls),
        input_calls=calls, staged_memory_identity=True, no_next_request=no_next_request)


def domain_checks(tape):
    empty=[]; mixed=[]; full_explorer=[]; map_rows=[]; setups=[]
    for state in range(4):
        for family,index,mapping in mappings():
            payload=explorer_payload(state, [], mapping)
            assert [x['action'] for x in payload['actions']] == list(mapping)
            assert all(x['verified_outcomes']=='UNTRIED' for x in payload['actions'])
            assert serialize(payload)==serialize(explorer_payload(state, [], mapping))
            assert not any(action in serialize(payload) for action in ACTIONS)
            empty.append(dict(state=state,family=family,mapping_index=index,payload=payload))
        bundle=setup(state,f'MIXED_{state}')
        for action in ('HOLD','HOLD','ADVANCE','RETREAT'): setups.append(ordinary(bundle,action))
        records=bundle[0].inner.memory.records
        before=deepcopy(records)
        for family,index,mapping in mappings():
            payload=explorer_payload(state, reversed(records), mapping)
            by_action={mapping[r['action']]:r['verified_outcomes'] for r in payload['actions']}
            assert by_action=={'HOLD':[expected(state,'HOLD')['consequence']]*2,
                'ADVANCE':[expected(state,'ADVANCE')['consequence']], 'RETREAT':'UNTRIED'}
            assert before==records
            mixed.append(dict(state=state,family=family,mapping_index=index,payload=payload))
        for action in ('RETREAT','ADVANCE'): setups.append(ordinary(bundle,action))
        records=bundle[0].inner.memory.records
        for family,index,mapping in mappings():
            old=old_explorer_render(state,records,dict(surface_to_underlying=mapping,
                                                      underlying_option_order=list(mapping.values())))
            new=explorer_payload(state,records,mapping)
            assert [x['action'] for x in new['actions']]==old['available_actions']
            assert [x['verified_outcomes'] for x in new['actions']]==[x['observed_consequences'] for x in old['VERIFIED_PRIOR_OUTCOMES']]
            full_explorer.append(dict(state=state,family=family,mapping_index=index,evidence_order_equal=True))
        for action in ACTIONS:
            bundle=setup(state,f'DOMAIN_{state}_{action}')
            for n in range(3):
                if n:
                    setups.append(ordinary(bundle,action))
                    if action != 'HOLD': setups.append(ordinary(bundle,'RETREAT' if action=='ADVANCE' else 'ADVANCE'))
                system=bundle[0]
                assert system.inner.map.current.state==state
                for family,index,mapping in mappings():
                    before=published(system)
                    payload=map_payload(state,action,system.inner.memory.records,mapping)
                    assert len(payload['VERIFIED_CHRONOLOGICAL_HISTORY'])==n
                    assert not any(a in serialize(payload) for a in ACTIONS)
                    name=f'domain_{state}_{action}_{n}_{family}_{index}'
                    source=tape.source(name,'Map',serialize(dict(next_state=0,consequence=0)))
                    adapter=MapBinding(system.inner.map,system.inner.memory,source,mapping,91000)
                    prediction=adapter.predict(action,1001,system.inner.next_transaction_id)
                    assert prediction.pre_state==state and prediction.action==action and source.calls==1
                    assert published(system)==before
                    assert json.loads(tape.calls[-1]['prompt'])==payload
                    map_rows.append(dict(state=state,action=action,history_length=n,
                        family=family,mapping_index=index,payload=payload,admitted=True))
    return dict(empty=empty,mixed=mixed,complete_explorer_equivalence=full_explorer,map=map_rows,setup_steps=setups)


def historical_map_equivalence():
    from experiments.model_map_proposal_v0.campaign import schedule as schedule0, fixture as fixture0
    from experiments.model_map_established_prior_revision_v1.campaign import schedule as schedule1, fixture as fixture1
    rows=[]
    for version,schedule,fixture in (('v0',schedule0,fixture0),('v1',schedule1,fixture1)):
        for descriptor in schedule():
            system,_,_,_=fixture(descriptor)
            records=system.inner.memory.records
            before=deepcopy(records)
            old=serialize(old_map_render(records,descriptor))
            new=serialize(map_payload(1,'HOLD',records,descriptor['mapping']))
            assert old==new and before==records
            rows.append(dict(version=version,index=descriptor['index'],exact_bytes=True))
    return rows


def check(replay=None):
    tape=Tape(replay); domains=domain_checks(tape); equivalence=historical_map_equivalence()
    first=[]; recovery=[]; no_recovery=[]; controls=[]
    for family,index,mapping in mappings():
        for action in ACTIONS:
            name=f'first_{family}_{index}_{action}'
            row=composed(setup(0,name),tape,name,mapping,action)
            assert row['probe']['authorization']['committed'] and row['calls']==dict(Explorer=1,Map=1,Recovery=0)
            receipt=row['probe']['receipt']
            alias_context=DecisionContext(1001,1,0,0,action,receipt['next_state'],receipt['realized_consequence'],True)
            recovery_alias=json.loads(recovery_render(alias_context,mapping))['action']
            assert recovery_alias==row['input_calls'][1]['input']['target_action']
            row['recovery_alias_projection_only']=recovery_alias
            first.append(row)
        for correct in (True,False):
            name=f'recovery_{family}_{index}_{correct}'
            row=composed(setup(0,name),tape,name,mapping,'ADVANCE',
                prediction=dict(next_state=0,consequence=0),recovery_value=1 if correct else 2)
            assert row['calls']==dict(Explorer=1,Map=1,Recovery=1)
            assert row['probe']['authorization']['committed']==correct
            recovery.append(row)
    mapping=mappings()[0][2]
    for state in range(4):
        truth=expected(state,'HOLD')
        for mode in ('state','consequence','both'):
            prediction=dict(next_state=(state+1)%4 if mode!='consequence' else state,
                consequence={-1:0,0:1,1:-1}[truth['consequence']] if mode!='state' else truth['consequence'])
            name=f'no_recovery_{state}_{mode}'
            row=composed(setup(state,name),tape,name,mapping,'HOLD',prediction=prediction)
            assert row['calls']['Recovery']==0 and row['probe']['authorization']['committed']
            assert row['probe']['measurement_matches'] is False
            no_recovery.append(row)

    episode=[]; bundle=setup(0,'EPISODE')
    for index,action in enumerate(('HOLD','HOLD','ADVANCE','HOLD','RETREAT','HOLD','ADVANCE','HOLD')):
        row=composed(bundle,tape,f'episode_{index}',mapping,action,
            prediction=dict(next_state=0,consequence=0) if index==2 else None)
        assert row['probe']['authorization']['committed']
        assert len(row['probe']['after']['memory'])==index+1
        episode.append(row)
    a,b=episode[:2]
    assert a['input_calls'][1]['input']['VERIFIED_CHRONOLOGICAL_HISTORY']==[]
    later=b['input_calls'][1]['input']['VERIFIED_CHRONOLOGICAL_HISTORY']
    assert len(later)==1 and later[0]['transaction_id']==a['probe']['receipt']['transaction_id']
    assert a['input_calls'][0]['input']['actions'][1]['verified_outcomes']=='UNTRIED'
    assert b['input_calls'][0]['input']['actions'][1]['verified_outcomes']==[0]
    assert sum(r['calls']['Recovery'] for r in episode)==1

    invalid_explorer=['{"next_state":1,"consequence":1}', 'K1 K2',
        '{"action":"K1","authorization":true}', 'ADVANCE', 'K1 retry']
    invalid_map=list(MAP_INVALID)+['K1','{"next_state":1,"consequence":1,"action":"HOLD"}',
        '{"next_state":1,"consequence":1,"receipt_id":"fake"}',
        '{"next_state":1,"consequence":1,"epoch":1001}',
        '{"next_state":1,"consequence":1,"next_state":1}']
    invalid_recovery=list(RECOVERY_INVALID)+['{"replacement_state":1,"retry":true}',
        '{"replacement_state":1,"next_state":1,"consequence":1}']
    for role,raws in (('Explorer',invalid_explorer),('Map',invalid_map),('Recovery',invalid_recovery)):
        for index,raw in enumerate(raws):
            name=f'invalid_{role}_{index}'
            kwargs={role.lower()+'_raw':raw}
            row=composed(setup(0,name),tape,name,mapping,'ADVANCE',
                prediction=dict(next_state=0,consequence=0),**kwargs)
            assert not row['probe']['authorization']['committed']
            assert row['calls']==dict(Explorer=1,Map=int(role!='Explorer'),Recovery=int(role=='Recovery'))
            assert row['probe']['authorization']['executed']==(role=='Recovery')
            controls.append(row)

    # Same native owner cannot ask a value source twice, even for a real decision.
    decision=PairDecision(**next(x for x in recovery[0]['events'] if x['kind']=='native_attempt')['decision'])
    class CountSource:
        calls=0
        def propose(self,context): self.calls+=1;return context.next_state
    owner=RecoveryOpportunity();source=CountSource();candidate=owner.candidate(decision,source)
    try: owner.candidate(decision,source)
    except RuntimeError: pass
    else: raise AssertionError('second Recovery attempt allowed')
    assert source.calls==1 and candidate.status=='RECOVERING'
    budget=dict(callbacks=1,second_attempt_rejected=True,candidate=asdict(candidate))

    # A read-only observer must not alter the actual transaction or source routing.
    comparison=[]
    for correct in (True,False):
        name=f'noninterference_{correct}'
        rows=[]
        for enabled in (True,False):
            local=tape
            row=composed(setup(0,name),local,name,mapping,'ADVANCE',
                prediction=dict(next_state=0,consequence=0),recovery_value=1 if correct else 2,instrument=enabled)
            row.pop('events');rows.append(row)
        assert rows[0]==rows[1]
        comparison.append(dict(correct=correct,protected_trace_and_calls_identical=True,trace=rows[0]))

    tape.done()
    transactions=first+recovery+no_recovery+episode+controls
    assert all(not r['probe']['errors'] for r in transactions)
    properties={
        'A':('finite Explorer proposal and rejected cross-role schema','first + invalid_Explorer'),
        'B':('finite Prediction content and rejected capability fields','map domains + invalid_Map'),
        'C':('value-only candidate with native identity/status envelope','recovery + invalid_Recovery'),
        'D':('Explorer Map object rejected before Map invocation','invalid_Explorer_0'),
        'E':('Map action text/field rejected before execution','invalid_Map_9 + invalid_Map_10'),
        'F':('Map receipt field rejected; executed receipts stay authentic','invalid_Map_11 + first + recovery'),
        'G':('Recovery receipt/prediction fields rejected; latch/receipt unchanged','invalid_Recovery + recovery'),
        'H':('Measure/quarantine/native attempt precede Recovery; valid incumbent suppresses it','recovery + no_recovery'),
        'I':('one native attempt and no second source callback','recovery + budget'),
        'J':('RECOVERING candidate independently accepted','12 correct recovery cases'),
        'K':('wrong value independently rejects with unchanged protected snapshot','12 wrong recovery cases'),
        'L':('committed Memory equals authenticated receipt, not proposed outcome','first + episode + no_recovery'),
        'M':('all adapters in staged transactions and same staged Memory reference','recovery + episode'),
        'N':('failed Recovery prevents any later role request','wrong recovery + invalid_Recovery'),
        'O':('inherited assert_bounds and eight-record maximum','all transactions + episode'),
    }
    result=dict(classification='A — COMPOSITION INPUT BINDINGS READY',actual_model_calls=0,
        classification_scope='Synthetic campaign; final completion additionally requires verification.json replay/preservation/regression checks.',
        empty_explorer_contexts=len(domains['empty']),mixed_explorer_contexts=len(domains['mixed']),
        complete_explorer_evidence_equivalence=len(domains['complete_explorer_equivalence']),
        map_contexts=len(domains['map']),map_finite_pairs=12,map_history_lengths=[0,1,2],
        historical_map_exact_byte_equivalence=len(equivalence),first_state_zero_transactions=len(first),
        all_action_cross_role_alias_checks=len(first),
        correct_recovery_authorizations=12,wrong_recovery_atomic_rejections=12,
        no_recovery_controls=len(no_recovery),synthetic_episode_decisions=len(episode),
        episode_genuine_recovery_opportunities=1,empty_to_experienced_transition=True,
        capability_controls={role:sum(r['name'].startswith('invalid_'+role+'_') for r in controls)
                             for role in ('Explorer','Map','Recovery')},
        synthetic_role_requests={role:sum(c['role']==role for c in tape.calls) for role in ('Explorer','Map','Recovery')},
        composed_transactions=len(transactions),composed_world_executions=sum(r['probe']['authorization']['executed'] for r in transactions),
        composed_commits=sum(r['probe']['authorization']['committed'] for r in transactions),
        protected_false_accepts=0,receipt_mismatch_accepts=0,raw_text_leakage=0,
        maxima={key:max(r['probe']['bounds'][key] for r in transactions) for key in transactions[0]['probe']['bounds']},
        A_to_O={key:dict(status='PASS',claim=claim,executed_evidence=evidence) for key,(claim,evidence) in properties.items()},
        one_attempt=budget,observer_noninterference_cases=len(comparison),
        auxiliary_observer_transactions=4,synthetic_request_count_includes_observer_controls=True,
        observer_noninterference=True,
        historical_authority_sources_changed=False,model_behavior='UNTESTED_ZERO_INFERENCE')
    details=dict(domains=domains,historical_map_equivalence=equivalence,first=first,
        recovery=recovery,no_recovery=no_recovery,episode=episode,controls=controls,budget=budget,
        observer_noninterference=comparison)
    return result,details,tape.calls
