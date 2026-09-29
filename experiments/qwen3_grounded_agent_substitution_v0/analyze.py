"""Read-only authenticated replay and public-safe metrics for model substitution."""
from argparse import ArgumentParser
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import json

from horus.core import digest
from horus.live import SessionStore, _atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory, file_hash
from experiments.grounded_autonomous_agent_v0_1.analyze import prior_state
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_authority_autonomous_agent_v0.protocol import (
    ACTIONS, select_route, source_for_model_choice)
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import (
    expected_escape, qualifies)
from experiments.grounded_stagnation_escape_evaluation_v0.candidate import PURPOSE
from experiments.grounded_stagnation_escape_promotion_controlled_v0.worker import (
    semantic_assessments, request_for)
from experiments.grounded_authority_autonomous_agent_v0.protocol import GOAL, RECENT_DECISION_LIMIT
from .shared import STUDY, verify_sources


def insist(ok, message):
    if not ok:
        raise RuntimeError('INVALID: ' + message)


def visible_assessment(x):
    return {k: v for k, v in x.items() if k != 'recent_receipt_provenance'}


def run_audit(private, arm, pair):
    path = private / 'runs' / f'{arm}{pair}'
    insist((path / 'complete.json').is_file(), f'{arm}{pair} complete marker')
    with SessionStore(path / 'session', True) as store, ModernMemory(path / 'memory.sqlite3', False) as memory:
        memory.reconcile(store)
        events = store.records['events']
        memory_rows = memory.rows()
        decisions = rows_of(store, 'AUTONOMOUS_AGENT_DECISION')
        calls = store.records['calls']
        freezes = [x['record'] for x in calls if x['kind'] == 'ACTION_FROZEN']
        intents = [x['record'] for x in calls if x['kind'] == 'REQUEST_INTENT']
        insist(len(decisions) == len(events) == len(memory_rows) == len(freezes) == 30,
               f'{arm}{pair} decision/receipt/Memory/freeze cardinality')
        insist(not rows_of(store, 'SELF_REVIEW_NON_AUTHORITATIVE'), f'{arm}{pair} no in-campaign review')
        insist(len(intents) == sum(d['action_call_id'] is not None for d in decisions),
               f'{arm}{pair} model intent cardinality')
        steps = [json.loads(line) for line in (path / 'step-summaries.private.jsonl').read_text().splitlines()]
        insist(len(steps) == 30, f'{arm}{pair} step timing cardinality')
        for n, (d, e, freeze, step) in enumerate(zip(decisions, events, freezes, steps), 1):
            ev = e['record']; receipt = ev['receipt']
            insist(d['index'] == n and ev['decision_index'] == n and d['event_stream_sequence'] == n,
                   f'{arm}{pair}:{n} sequence')
            insist(ev['study'] == 'QWEN3_GROUNDED_AGENT_SUBSTITUTION_V0' and
                   ev['authorization_status'] == 'AUTHORIZED' and
                   ev['execution_kind'] == 'AUTONOMOUS_EXECUTION', f'{arm}{pair}:{n} authorization')
            insist(d['state'] == receipt['pre_state'] and
                   d['selected_action'] == receipt['action'] and
                   d['realized'] == dict(next_state=receipt['next_state'],
                                         consequence=receipt['realized_consequence']),
                   f'{arm}{pair}:{n} receipt outcome')
            insist(digest(receipt) == ev['receipt_provenance_sha256'] == d['receipt_provenance_sha256']
                   == step['receipt_sha256'] and d['receipt_identity'] == ev['receipt_identity'],
                   f'{arm}{pair}:{n} receipt provenance')
            insist(freeze['selected_action'] == d['selected_action'] and
                   freeze['decision_source'] == d['decision_source'] and
                   freeze['action_call_id'] == d['action_call_id'],
                   f'{arm}{pair}:{n} frozen decision')
            for action in ACTIONS:
                insist(d['grounded_assessments_before'][action] ==
                       prior_state(memory_rows, f"{d['state']}:{action}", n),
                       f'{arm}{pair}:{n} grounded pre-state {action}')
            insist(d['grounded_after'] == prior_state(
                memory_rows, f"{d['state']}:{d['selected_action']}", n + 1),
                f'{arm}{pair}:{n} grounded post-state')
            route = select_route(d['grounded_assessments_before'])
            action = d['selected_action']
            insist(d['admissible_actions'] == route['candidates'] and action in route['candidates'],
                   f'{arm}{pair}:{n} candidate scope')
            escape, _ = expected_escape(decisions[:n - 1], d['state'],
                                        d['grounded_assessments_before'])
            if d['decision_source'] == 'STAGNATION_ESCAPE':
                insist(escape == action and d['policy_route'] == 'ESCAPE' and
                       d['policy_reason'] == PURPOSE and d['action_call_id'] is None and
                       d['action_parse_status'] == 'NOT_CALLED' and
                       d['selected_grounded_before']['kind'] == 'UNSEEN',
                       f'{arm}{pair}:{n} frozen escape')
            else:
                insist(escape is None, f'{arm}{pair}:{n} missed frozen escape')
                source = route['source'] if route['route'] == 'MECHANICAL' else \
                    source_for_model_choice(route, d['grounded_assessments_before'], action)
                insist(d['decision_source'] == source and d['policy_route'] == route['route']
                       and d['policy_reason'] == route['reason'], f'{arm}{pair}:{n} authority route')
                if route['route'] == 'MECHANICAL':
                    insist(action == route['action'] and d['action_call_id'] is None and
                           d['action_parse_status'] == 'NOT_CALLED',
                           f'{arm}{pair}:{n} mechanical ceiling')
                else:
                    insist(d['action_call_id'] is not None and d['action_parse_status'] == 'VALID',
                           f'{arm}{pair}:{n} model action')
            insist(step['selected_action'] == action and step['realized_consequence'] ==
                   d['realized']['consequence'] and step['inference']['call_id'] == d['action_call_id'],
                   f'{arm}{pair}:{n} step summary')
            history = [dict(decision_id=x['decision_id'], state=x['state'],
                action=x['selected_action'], authenticated_consequence=x['realized']['consequence'],
                source=x['decision_source']) for x in decisions[:n - 1]][-RECENT_DECISION_LIMIT:]
            projection = dict(goal=GOAL, decision_id=f'C:D{n:02d}', decision_index=n,
                current_state=d['state'], available_actions=route['candidates'],
                grounded_assessments=semantic_assessments(d['grounded_assessments_before']),
                recent_agent_working_context=history)
            if d['action_call_id'] is not None:
                matches = [x for x in intents if x['call_id'] == d['action_call_id']]
                insist(len(matches) == 1, f'{arm}{pair}:{n} unique model request')
                if arm == 'D':
                    insist(matches[0]['request_sha256'] == request_for(projection)['canonical_sha256'],
                           f'{arm}{pair}:{n} frozen model projection/request')
                else:
                    insist(matches[0]['semantic_projection_sha256'] == digest(projection),
                           f'{arm}{pair}:{n} frozen model projection')
        restart = None
        if pair == 2:
            restart = json.loads((path / 'restart-verdict.json').read_text())
            insist(restart['status'] == 'PASS' and restart['fresh_process'] and
                   restart['durable_memory_exact'] and restart['grounded_state_exact'] and
                   restart['signed_stagnation_suffix_exact'] and
                   restart['first_post_restart_decision_valid'] and
                   not restart['first_post_restart_decision_pending'], f'{arm}{pair} restart')
        private_hashes = {str(p.relative_to(path)): file_hash(p) for p in path.rglob('*')
                          if p.is_file() and p.name != '.lock'}
        seen = set(); streak = longest = 0; key = None
        context_actions = defaultdict(Counter)
        public_rows = []
        for d, step in zip(decisions, steps):
            selected = d['selected_grounded_before']
            relation = f"{d['state']}:{d['selected_action']}"
            if selected['kind'] == 'UNSEEN' and d['grounded_after']['kind'] != 'UNSEEN':
                seen.add(relation)
            next_key = (d['state'], d['selected_action'])
            if qualifies(d):
                streak = streak + 1 if key == next_key else 1
                key = next_key
                longest = max(longest, streak)
            else:
                streak = 0; key = None
            semantic_pattern = json.dumps({a: dict(kind=v['kind'],
                relation_type=v['relation_type'],
                known_consequence=(v.get('established_value') or {}).get('consequence')
                if v['kind'] == 'ESTABLISHED' else None)
                for a, v in d['grounded_assessments_before'].items()}, sort_keys=True)
            if d['action_call_id'] is not None:
                context_actions[semantic_pattern][d['selected_action']] += 1
            public_rows.append(dict(decision_id=d['decision_id'], index=d['index'],
                state=d['state'], assessments={a: visible_assessment(v) for a, v in
                    d['grounded_assessments_before'].items()},
                admissible_actions=d['admissible_actions'], action=d['selected_action'],
                decision_source=d['decision_source'], parse_status=d['action_parse_status'],
                selected_kind=selected['kind'], selected_relation_type=selected['relation_type'],
                consequence=d['realized']['consequence'], next_state=d['realized']['next_state'],
                grounded_change=d['grounded_state_change'],
                receipt_identity=d['receipt_identity'],
                receipt_sha256=d['receipt_provenance_sha256'],
                event_identity=d['event_identity'],
                known_negative_with_better_established=d['known_negative_with_better_established'],
                inference=step['inference']))
        model_steps = [s['inference'] for s in steps if s['inference']['call_id'] is not None]
        counters = Counter(d['selected_action'] for d in decisions)
        model_counters = Counter(d['selected_action'] for d in decisions if d['action_call_id'] is not None)
        metrics = dict(consequence_sum=sum(d['realized']['consequence'] for d in decisions),
            known_negative_with_better_known=sum(d['known_negative_with_better_established'] for d in decisions),
            unseen_selections=sum(d['selected_grounded_before']['kind'] == 'UNSEEN' for d in decisions),
            unresolved_selections=sum(d['selected_grounded_before']['assessment_status'] == 'UNRESOLVED'
                                      for d in decisions),
            newly_grounded_relations=len(seen),
            neutral_fallback_model_decisions=sum(d['decision_source'] == 'SAFE_GROUNDED_FALLBACK'
                and d['selected_grounded_before']['kind'] == 'ESTABLISHED'
                and d['selected_grounded_before']['established_value']['consequence'] == 0
                for d in decisions),
            longest_same_relation_neutral_fallback_streak=longest,
            stagnation_escapes=sum(d['decision_source'] == 'STAGNATION_ESCAPE' for d in decisions),
            mechanical_decisions=sum(d['decision_source'] == 'GROUNDED_MECHANICAL' for d in decisions),
            model_decisions=len(model_steps), abstentions=0,
            action_distribution=dict(counters), model_action_distribution=dict(model_counters),
            model_action_by_semantic_pattern=dict(context_actions),
            input_tokens=sum(s['input_tokens'] for s in model_steps),
            output_tokens=sum(s['output_tokens'] for s in model_steps),
            prompt_eval_seconds=sum(s['prompt_eval_seconds'] for s in model_steps),
            generation_seconds=sum(s['generation_seconds'] for s in model_steps),
            inference_wall_seconds=sum(s['wall_seconds'] for s in model_steps),
            runner_load_seconds=sum(s['runner_load_seconds'] for s in model_steps),
            runner_load_events=sum(s['runner_load_seconds'] > 1 for s in model_steps),
            effective_context_tokens=[s['input_tokens'] for s in model_steps],
            physical_attempts=sum(s.get('physical_attempts', 1) for s in model_steps),
            restart=restart, receipt_memory_replay='PASS')
        return dict(metrics=metrics, decisions=public_rows, artifact_sha256=private_hashes)


def analyze(private):
    verify_sources()
    gate=json.loads((STUDY / 'stage-a-gate.json').read_text())
    insist(gate['status'] == 'PASS', 'Stage A gate')
    runs = {f'{arm}{pair}': run_audit(private, arm, pair)
            for arm in ('D', 'Q') for pair in (1, 2, 3)}
    public = dict(stage_a_gate=gate, campaign_integrity='PASS',
        runs={name:dict(metrics=run['metrics'], decisions=run['decisions'])
              for name, run in runs.items()})
    private_manifest = {name: run['artifact_sha256'] for name, run in runs.items()}
    _atomic_write(STUDY / 'stage-b-public.json', public)
    _atomic_write(STUDY / 'private-artifact-hashes.json', private_manifest)
    return public


if __name__ == '__main__':
    p=ArgumentParser();p.add_argument('--private-root', required=True, type=Path)
    args=p.parse_args(); result=analyze(args.private_root)
    print(json.dumps({k:v['metrics'] for k,v in result['runs'].items()}, sort_keys=True))
