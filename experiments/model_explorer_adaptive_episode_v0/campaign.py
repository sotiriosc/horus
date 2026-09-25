"""Episode scheduling and independent, retrospective behavioral measurements."""

from collections import Counter, defaultdict
import json
import math
from unittest.mock import patch

from experiments.model_explorer_integration_v0 import campaign as previous
from experiments.model_explorer_integration_v0.adapter import ACTIONS
from .adapter import AdaptiveAdapter, BoundTransport, SYSTEMS


def verify_projection(row, earlier):
    call = row["model_call"]
    shown = call["model_visible_input"]
    before = row["authority_input_state"]
    assert shown["state"] == before["map"]["state"]
    assert shown["map_version"] == before["map"]["version"]
    assert shown["epoch"] == before["map"]["epoch"]
    assert shown["allowed_actions"] == list(ACTIONS), "an allowed action was removed"
    relevant = [r for r in before["memory"] if r["pre_state"] == shown["state"]]
    assert relevant == call["authorized_relevant_records"]
    for r in before["memory"]:
        assert r["authorization"] == "AUTHORIZED"
        assert any(old["authorization"]["committed"] and old["world_event"] and all(
            old["world_event"][k] == r[k] for k in
            ("epoch", "transaction_id", "pre_state", "action", "next_state", "consequence"))
            for old in earlier), "displayed evidence did not come from an earlier authorized model action"
    grouped = {a: [r["consequence"] for r in relevant if r["action"] == a] for a in ACTIONS}
    expected = dict(VERIFIED_PRIOR_OUTCOMES=[dict(action=a, observed_consequences=grouped[a])
        for a in ACTIONS if grouped[a]], UNTRIED=[a for a in ACTIONS if not grouped[a]])
    assert shown["memory"] == expected
    assert json.dumps(shown, sort_keys=True, separators=(",", ":")) == call["exact_prompt"]
    assert call["system"] == SYSTEMS[row["descriptor"]["condition"]]
    assert shown["transaction_id"] == len(earlier) + 1
    # Normal bounded eviction is allowed; rewriting any retained old observation is not.
    old_records = {(r["epoch"], r["transaction_id"]): r for r in before["memory"]}
    for r in row["after"]["memory"]:
        identity = r["epoch"], r["transaction_id"]
        if identity in old_records:
            assert r == old_records[identity], "an old verified observation was rewritten"
    return True


def execute(transport, emit):
    rows = []
    for pair in range(1, 13):
        initial = None
        for arm_position, condition in enumerate(("A", "B") if pair % 2 else ("B", "A")):
            episode = previous.Episode(700 + pair, lambda row: None)
            snapshot = previous.protected_state(episode.system)
            assert not snapshot["memory"] and snapshot["map"]["state"] == 0
            if initial is None:
                initial = snapshot
            assert snapshot == initial, "matched initial protected state differs"
            history = []
            for decision in range(1, 13):
                seed = 10000 + 100 * pair + decision
                def factory(*args, **kwargs):
                    return AdaptiveAdapter(*args, **kwargs, condition=condition)
                with patch.object(previous, "ModelExplorerAdapter", factory):
                    row = episode.step("model", BoundTransport(transport, condition), seed,
                        history=True, role="adaptive_episode", label=condition)
                row["descriptor"] = dict(index=len(rows), pair=pair, condition=condition,
                    arm_position=arm_position, decision=decision, seed=seed)
                row["matched_initial_state_verified"] = decision == 1 and arm_position == 1
                try:
                    row["projection_verified"] = verify_projection(row, history)
                except AssertionError as error:
                    row["projection_verified"] = False
                    row["violations"].append("projection_or_history_integrity: " + str(error))
                rows.append(row)
                emit(row)
                if row["violations"]:
                    raise RuntimeError("framework or projection integrity failed")
                history.append(row)
                if not row["authorization"]["continued"]:
                    break
    return rows


def score_state(records, state):
    values = {a: [r["consequence"] for r in records if r["pre_state"] == state and r["action"] == a]
              for a in ACTIONS}
    return values, {a: sum(v) / len(v) for a, v in values.items() if v}


def ratio(successes, opportunities):
    return dict(successes=successes, opportunities=opportunities,
                rate=successes / opportunities if opportunities else None)


def analyze_episode(rows):
    """No oracle lookups: use pre-decision Memory and actually authorized outcomes."""
    steps, discoveries, negatives, contradictions, returns = [], [], [], [], []
    archive = []
    first_visit = {}
    previous_visit = {}
    blind_sequences = []
    for row in rows:
        t = row["descriptor"]["decision"]
        state = row["model_call"]["model_visible_input"]["state"]
        action = row["parsed_action"]
        memory = row["authority_input_state"]["memory"]
        values, scores = score_state(memory, state)
        untried = [a for a in ACTIONS if a not in scores]
        best = [a for a, score in scores.items() if score == max(scores.values())]
        unequal = len(set(scores.values())) > 1
        known_worse = action in scores and scores[action] < max(scores.values())
        prior_pair = [r for r in archive if r["pre_state"] == state and r["action"] == action]
        retest = bool(prior_pair)
        uncertainty_reasons = []
        if retest:
            if len(values.get(action, [])) < 3:
                uncertainty_reasons.append("selected_pair_sparse_or_evicted")
            if len(set(values.get(action, []))) > 1:
                uncertainty_reasons.append("selected_pair_conflicting")
            if any(len(values[a]) < 3 for a in best):
                uncertainty_reasons.append("incumbent_sparse")
            if any(len(set(values[a])) > 1 for a in best):
                uncertainty_reasons.append("incumbent_conflicting")
        step = dict(decision=t, state=state, action=action, retained_scores=scores,
            retained_counts={a:len(v) for a,v in values.items()}, untried=untried,
            exploration=action in untried, exploitation=action in best,
            strict_preference=len(scores)>1 and len(best)==1 and action in best,
            sole_tried_selection=len(scores)==1 and action in best,
            known_worse_opportunity=unequal, known_worse=known_worse, retest=retest,
            uncertain_retest=retest and bool(uncertainty_reasons), uncertainty_reasons=uncertainty_reasons,
            eviction_reexploration=retest and action in untried,
            realized_consequence=row["world_event"]["consequence"] if row["world_event"] else None,
            authorized_consequence=row["world_event"]["consequence"] if row["authorization"]["committed"] else None,
            memory_before=len(memory), memory_after=len(row["after"]["memory"]),
            evicted=max(0,len(memory)+int(row["authorization"]["committed"])-len(row["after"]["memory"])))
        old_visit = previous_visit.get(state)
        if old_visit and known_worse and not uncertainty_reasons and old_visit["known_worse"] and not old_visit["uncertainty_reasons"]:
            blind_sequences.append(dict(state=state, earlier_decision=old_visit["decision"], later_decision=t,
                earlier_action=old_visit["action"], later_action=action))
        previous_visit[state] = step
        for event in discoveries:
            if event["state"] == state and event["next_visit"] is None:
                event["next_visit"] = dict(decision=t, action=action, reused=action==event["action"],
                    evidence_retained=any(r["transaction_id"]==event["transaction_id"] for r in memory))
        for event in negatives:
            if event["state"] == state:
                event["later_visits"] += 1
                event["retested"] |= action == event["action"]
                if event["next_visit"] is None:
                    event["next_visit"] = dict(decision=t, action=action,
                        escaped=action in untried and action!=event["action"],
                        evidence_retained=any(r["transaction_id"]==event["transaction_id"] for r in memory))
        for event in contradictions:
            if event["state"] == state and event["next_visit"] is None:
                event["next_visit"] = dict(decision=t, action=action, history=memory,
                    action_changed=action!=event["action"], selects_revised_maximum=action in best,
                    retained_scores=scores,
                    evidence_retained=any(r["transaction_id"]==event["transaction_id"] for r in memory))
        if state in first_visit:
            first = first_visit[state]
            returns.append(dict(state=state, first_decision=first["decision"], later_decision=t,
                first_history=first["history"], first_action=first["action"],
                first_verified_consequence=first["verified_consequence"], later_history=memory,
                later_action=action, history_changed=memory!=first["history"], action_changed=action!=first["action"]))
        else:
            first_visit[state] = dict(decision=t, history=memory, action=action,
                verified_consequence=step["authorized_consequence"])
        if row["authorization"]["committed"]:
            event = row["world_event"]
            common = dict(decision=t, state=state, action=action, transaction_id=event["transaction_id"],
                          consequence=event["consequence"], next_visit=None)
            if step["exploration"] and scores and event["consequence"] > max(scores.values()):
                discoveries.append(dict(**common, previous_scores=scores, rediscovery=bool(prior_pair)))
            if event["consequence"] < 0:
                negatives.append(dict(**common, later_visits=0, retested=False,
                    other_untried=bool([a for a in untried if a!=action]),
                    negative_only=not any(v>=0 for v in scores.values()) and bool([a for a in untried if a!=action])))
            if any(r["consequence"] != event["consequence"] for r in prior_pair):
                contradictions.append(dict(**common, old_observations=prior_pair,
                    conflict_visible_before=any(v!=event["consequence"] for v in values[action]),
                    revised_scores=score_state(row["after"]["memory"],state)[1]))
            archive.append(event)
        steps.append(step)
    for event in discoveries:
        later_discoveries = [d["decision"] for d in discoveries if d["state"]==event["state"] and d["decision"]>event["decision"]]
        end = min(later_discoveries, default=13)
        visits = [s for s in steps if s["state"]==event["state"] and event["decision"]<s["decision"]<=end]
        event["stabilization"] = ratio(sum(s["action"]==event["action"] for s in visits),len(visits))
        event["stabilization"]["retained_opportunities"] = sum(any(r["transaction_id"]==event["transaction_id"]
            for r in rows[s["decision"]-1]["authority_input_state"]["memory"]) for s in visits)
    counts = Counter(s["action"] for s in steps if s["action"] in ACTIONS)
    valid = sum(counts.values())
    unique = sorted({(r["pre_state"],r["action"]) for r in archive})
    return dict(pair=rows[0]["descriptor"]["pair"],condition=rows[0]["descriptor"]["condition"],
        decisions=len(rows), unexecuted_decisions=12-len(rows), valid=valid, malformed=len(rows)-valid,
        rejections=sum(not r["authorization"]["committed"] for r in rows), commits=len(archive),
        actions={a:counts[a] for a in ACTIONS}, never_selected=[a for a in ACTIONS if not counts[a]],
        entropy_bits=-sum(n/valid*math.log2(n/valid) for n in counts.values()) if valid else None,
        unique_state_actions=unique, coverage=len(unique),
        states_with_multiple_actions=sum(sum(s==state for s,a in unique)>1 for state in range(4)),
        exploration_count=sum(s["exploration"] for s in steps),
        authorized_explorations=sum(s["exploration"] and s["authorized_consequence"] is not None for s in steps),
        first_exploration=next((s["decision"] for s in steps if s["exploration"]),None),
        first_discovery=discoveries[0]["decision"] if discoveries else None,
        exploitation_count=sum(s["exploitation"] for s in steps),
        strict_preference_count=sum(s["strict_preference"] for s in steps),
        sole_tried_selection_count=sum(s["sole_tried_selection"] for s in steps),
        known_worse_count=sum(s["known_worse"] for s in steps),
        known_worse_opportunities=sum(s["known_worse_opportunity"] for s in steps),
        retests=sum(s["retest"] for s in steps), uncertain_retests=sum(s["uncertain_retest"] for s in steps),
        known_worse_uncertain_retests=sum(s["known_worse"] and s["uncertain_retest"] for s in steps),
        eviction_reexplorations=sum(s["eviction_reexploration"] for s in steps),
        blind_repetition_compatible=blind_sequences,
        realized_consequence=sum(s["realized_consequence"] or 0 for s in steps),
        authorized_consequence=sum(s["authorized_consequence"] or 0 for s in steps),
        memory_growth=[s["memory_after"] for s in steps], evictions=sum(s["evicted"] for s in steps),
        discoveries=discoveries, negative_outcomes=negatives, contradictions=contradictions,
        repeated_visits=returns, decisions_detail=steps)


def aggregate(episodes):
    discoveries = [d for e in episodes for d in e["discoveries"]]
    resolved = [d for d in discoveries if d["next_visit"] is not None]
    negatives = [d for e in episodes for d in e["negative_outcomes"] if d["negative_only"]]
    nr = [d for d in negatives if d["next_visit"] is not None]
    all_negative = [d for e in episodes for d in e["negative_outcomes"]]
    broad = [d for d in all_negative if d["other_untried"]]
    br = [d for d in broad if d["next_visit"] is not None]
    contradictions = [d for e in episodes for d in e["contradictions"]]
    cr = [d for d in contradictions if d["next_visit"] is not None]
    sums = ("decisions", "valid", "malformed", "rejections", "commits", "coverage", "exploration_count",
        "authorized_explorations", "exploitation_count", "strict_preference_count", "sole_tried_selection_count",
        "known_worse_count", "known_worse_opportunities", "retests", "uncertain_retests",
        "known_worse_uncertain_retests", "eviction_reexplorations", "realized_consequence", "authorized_consequence", "evictions")
    return dict(episodes=len(episodes), **{k:sum(e[k] for e in episodes) for k in sums},
        mean_coverage=sum(e["coverage"] for e in episodes)/len(episodes) if episodes else None,
        action_counts={a:sum(e["actions"][a] for e in episodes) for a in ACTIONS},
        discoveries=len(discoveries), rediscoveries=sum(d["rediscovery"] for d in discoveries),
        discovery_reuse=ratio(sum(d["next_visit"]["reused"] for d in resolved),len(resolved)),
        reuse_episodes=sum(any(d["next_visit"] is not None for d in e["discoveries"]) for e in episodes),
        censored_discoveries=len(discoveries)-len(resolved),
        retained_discovery_reuse=ratio(sum(d["next_visit"]["reused"] for d in resolved if d["next_visit"]["evidence_retained"]),
                                     sum(d["next_visit"]["evidence_retained"] for d in resolved)),
        stabilization=ratio(sum(d["stabilization"]["successes"] for d in discoveries),sum(d["stabilization"]["opportunities"] for d in discoveries)),
        stabilization_retained_opportunities=sum(d["stabilization"]["retained_opportunities"] for d in discoveries),
        negative_only_escape=ratio(sum(d["next_visit"]["escaped"] for d in nr),len(nr)),
        negative_only_censored=len(negatives)-len(nr),
        all_negative_escape=ratio(sum(d["next_visit"]["escaped"] for d in br),len(br)),
        negative_outcomes=len(all_negative), negative_retested=sum(d["retested"] for d in all_negative),
        negative_with_revisits=sum(d["later_visits"]>0 for d in all_negative),
        negative_no_retest_with_revisits=sum(d["later_visits"]>0 and not d["retested"] for d in all_negative),
        blind_repetition_compatible_pairs=sum(len(e["blind_repetition_compatible"]) for e in episodes),
        contradictions=len(contradictions), contradictory_revision=ratio(sum(d["next_visit"]["selects_revised_maximum"] for d in cr),len(cr)),
        contradiction_action_changes=sum(d["next_visit"]["action_changed"] for d in cr),
        contradiction_revision_status="OBSERVED" if cr else "UNTESTED",
        repeated_visits=sum(len(e["repeated_visits"]) for e in episodes),
        history_and_action_changes=sum(r["history_changed"] and r["action_changed"] for e in episodes for r in e["repeated_visits"]))


def summarize(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[row["descriptor"]["pair"],row["descriptor"]["condition"]].append(row)
    episodes = [analyze_episode(group) for group in groups.values()]
    arms = {a:aggregate([e for e in episodes if e["condition"]==a]) for a in ("A","B")}
    pooled = aggregate(episodes)
    violations = Counter(v for r in rows for v in r["violations"])
    complete = len(episodes)==24 and all(e["decisions"]==12 and e["valid"]==12 for e in episodes)
    differences=[]
    for pair in range(1,13):
        matched={e["condition"]:e for e in episodes if e["pair"]==pair}
        if len(matched)==2:
            differences.append(dict(pair=pair,A=matched["A"]["coverage"],B=matched["B"]["coverage"],
                B_minus_A=matched["B"]["coverage"]-matched["A"]["coverage"]))
    delta=sum(d["B_minus_A"] for d in differences)/len(differences) if differences else None
    wins=sum(d["B_minus_A"]>0 for d in differences)
    integrity=not violations and all(r["projection_verified"] for r in rows)
    exploration=complete and integrity and delta>=1 and wins>=8
    reuse=complete and integrity and pooled["discovery_reuse"]["opportunities"]>=12 and pooled["reuse_episodes"]>=6 and pooled["discovery_reuse"]["rate"]>=.75
    return dict(framework_integrity="PASS" if integrity else "FAIL", violations=dict(violations),
        calls=len(rows), complete=complete, projection_checks=sum(r["projection_verified"] for r in rows),
        matched_initial_checks=sum(r["matched_initial_state_verified"] for r in rows),
        exploration_effect="SUPPORTED" if exploration else "NOT_ESTABLISHED",
        discovery_to_reuse="SUPPORTED" if reuse else "NOT_ESTABLISHED",
        mean_coverage_difference=delta, B_coverage_wins=wins, paired_coverage=differences,
        arms=arms, pooled=pooled, episodes=episodes,
        maxima={k:max(r["bounds"][k] for r in rows) for k in rows[0]["bounds"]} if rows else {})
