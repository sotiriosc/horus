"""Reproduce the unchanged-adapter domain blocker without any model transport.

Canonical Explorer probes isolate the Map domain guard; they are explicitly not
the proposed opaque-family composition episodes. No historical class is patched.
"""
import argparse
from dataclasses import asdict
from itertools import permutations
import json
from pathlib import Path

from experiments.base_framework_v0.framework import MapModel
from experiments.model_explorer_integration_v0.adapter import (
    Coordinates, ForcedOutput, ModelExplorerAdapter,
)
from experiments.model_explorer_semantic_prior_study_v0.adapter import render as semantic_render
from experiments.model_explorer_prior_factorial_v1.adapter import render as factorial_render
from experiments.model_map_proposal_v0.adapter import MapProposalAdapter
from experiments.model_recovery_proposal_v1.adapter import RecoveryProposer
from experiments.model_map_proposal_v0.boundary import execute
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework

ACTIONS = ('ADVANCE', 'HOLD', 'RETREAT')
FAMILIES = {'O1': ('K1', 'K2', 'K3'), 'O2': ('Q7', 'M4', 'Z2')}


class SyntheticMap:
    def __init__(self): self.calls = 0
    def __call__(self, prompt, seed):
        self.calls += 1
        return '{"next_state":1,"consequence":1}'


def run():
    domains = []
    for state in range(4):
        for action in ACTIONS:
            source = SyntheticMap()
            adapter = MapProposalAdapter(MapModel(state, 1001), source, '', 80003)
            try:
                prediction = asdict(adapter.predict(action, 1001, 1))
                error = None
            except ValueError as exc:
                prediction, error = None, str(exc)
            assert bool(prediction) == (state == 1 and action == 'HOLD')
            assert source.calls == int(prediction is not None)
            domains.append(dict(state=state, action=action, prediction=prediction,
                                error=error, synthetic_map_calls=source.calls))

    transactions = []
    for action in ACTIONS:
        world = TestWorld(0, False)
        boundary = ExternalExecutionBoundary(world, 'COMPOSITION_GATE_' + action)
        recovery = RecoveryProposer(ForcedOutput('{"replacement_state":1}'),
            dict(mapping=dict(zip(FAMILIES['O1'], ACTIONS)), seed=80004,
                 exact_prompt='', index=0))
        system = StatusBoundFramework(boundary.reader(), 0, 1001, recovery)
        explorer = ModelExplorerAdapter(ForcedOutput(action), Coordinates(0, 1001, 1), 80002)
        map_source = SyntheticMap()
        system.inner.explorer = explorer
        system.inner.map = MapProposalAdapter(system.inner.map, map_source, '', 80003)
        row = execute(system, boundary, world, {})
        assert explorer.observation['parsed_action'] == action
        assert not row['errors'] and row['before'] == row['after']
        assert not row['authorization']['executed'] and not row['authorization']['committed']
        assert not row['authorization']['continued'] and row['prediction'] is None
        assert map_source.calls == recovery.invocations == world.oracle.execution_count == 0
        observation = explorer.observation
        protected = published(system)
        repeated = system.begin_step()
        assert not repeated.executed and not repeated.committed and not repeated.continued
        assert explorer.observation is observation  # no second synthetic request
        assert published(system) == protected and map_source.calls == recovery.invocations == 0
        # Raw prompts/observations are intentionally not copied into public evidence.
        transactions.append(dict(action=action, synthetic_explorer_calls=1,
            synthetic_map_calls=map_source.calls, synthetic_recovery_calls=recovery.invocations,
            world_executions=world.oracle.execution_count, probe=row,
            attempted_continuation=asdict(repeated), no_second_request=True))

    projections = []
    for family, tokens in FAMILIES.items():
        for index, actions in enumerate(permutations(ACTIONS)):
            descriptor = dict(surface_to_underlying=dict(zip(tokens, actions)),
                underlying_option_order=list(ACTIONS), underlying_evidence_order=list(ACTIONS))
            for name, render in (('semantic', semantic_render), ('factorial', factorial_render)):
                try: render(0, [], descriptor)
                except ValueError as exc: error = str(exc)
                else: raise AssertionError('empty Memory unexpectedly accepted')
                assert error == 'an offered action lacks authorized experience'
                projections.append(dict(family=family, mapping_index=index,
                    mapping=descriptor['surface_to_underlying'], renderer=name, error=error))

    result = dict(classification='C — NOT ESTABLISHED',
        gate='BLOCKED_EXISTING_ADAPTER_INPUT_DOMAIN',
        blocker='MapProposalAdapter admits only state 1 / HOLD; every required state-0 first action rejects before Map proposal and execution.',
        secondary_finding='Existing opaque semantic/factorial projections require prior experience for every offered action; empty Memory is unsupported.',
        actual_model_calls=dict(Explorer=0, Map=0, Recovery=0, total=0),
        live_episodes_started=0, live_decisions_executed=0,
        planned_episodes=12, maximum_planned_decisions=96, unlaunched_decision_slots=96,
        maximum_model_calls=288, model_behavior='UNTESTED',
        diagnostic=dict(map_domain_cases=12, map_domain_admitted=1,
            state_zero_transactions=3, safe_preexecution_rejections=3,
            opaque_empty_memory_projection_checks=24,
            synthetic_explorer_invocations=3, synthetic_map_invocations=1,
            synthetic_recovery_invocations=0, world_executions=0,
            protected_false_accepts=0, memory_records_published=0),
        composition_integrity='UNESTABLISHED; safe rejection is not proof of full composition',
        gate_properties={letter: ('BLOCKED_REQUIRED_STATE_0_TRANSACTION' if letter == 'M'
            else 'NOT_ESTABLISHED_END_TO_END') for letter in 'ABCDEFGHIJKLMNO'},
        live_behavior_metrics=None, experience_chains=[], correction_chains=[],
        post_live_controls='NOT_RUN_GATE_BLOCKED', live_response_replay='NOT_APPLICABLE_NO_CALLS',
        interfaces_changed=False, real_inference_implemented=False)
    return dict(results=result, map_domains=domains, transactions=transactions,
                empty_memory_projections=projections)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--replay', type=Path, help='prior diagnostic output directory')
    args = parser.parse_args()
    data = run()
    files = {'results.json': data['results'], 'diagnostic.json': data}
    args.output.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        encoded = json.dumps(value, indent=2, sort_keys=True) + '\n'
        if args.replay:
            assert encoded == (args.replay / name).read_text(), name
        (args.output / name).write_text(encoded)
    print('C — NOT ESTABLISHED; unchanged-adapter gate blocked; ZERO real model calls')
    if args.replay: print('Diagnostic replay: both evidence files byte-identical')


if __name__ == '__main__': main()
