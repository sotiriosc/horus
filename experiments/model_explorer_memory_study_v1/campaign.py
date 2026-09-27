"""Preregistered schedules and independent presentation/behavior observers."""

from collections import Counter
from pathlib import Path
import json
from unittest.mock import patch

from experiments.model_explorer_integration_v0 import campaign as previous
from experiments.model_explorer_memory_study_v1.adapter import ACTIONS, SYSTEM, MemoryStudyAdapter


CELLS = (("A", "raw"), ("A", "semantic"), ("B", "raw"), ("B", "semantic"))
BIAS_SEEDS = tuple(range(9001, 9009))
PAIR_SEEDS = tuple(range(1001, 1025))
ROOT = Path(__file__).resolve().parents[2]


def plan():
    calls = []
    for phase, seeds in (("bias", BIAS_SEEDS), ("paired", PAIR_SEEDS)):
        for index, seed in enumerate(seeds):
            for study, form in (CELLS if index % 2 == 0 else CELLS[::-1]):
                fixed_index = CELLS.index((study, form))
                arms = (False,) if phase == "bias" else ((True, False) if (index + fixed_index) % 2 == 0 else (False, True))
                for history in arms:
                    calls.append(dict(index=len(calls), phase=phase, seed=seed, study=study,
                                      form=form, history=history, arm_position=arms.index(history)))
    return calls


def fixture(study, emit):
    e = previous.Episode(501 if study == "A" else 502, emit)
    for _ in range(5 if study == "A" else 6):
        result = e.step("deterministic", None, 0, role="setup")
        if not result["authorization"]["committed"] or result["violations"]:
            raise AssertionError("authorized fixture construction failed")
    return e


def verify_projection(row, descriptor, registered):
    """Independent of the presentation helper: reconstruct from protected Memory."""
    call = row["model_call"]
    shown = call["model_visible_input"]
    retained = row["authority_input_state"]["memory"]
    relevant = [r for r in retained if r["pre_state"] == shown["state"]]
    assert relevant == call["authorized_relevant_records"], "raw audited projection differs"
    assert all(r["authorization"] == "AUTHORIZED" for r in relevant)
    fields = ("epoch", "transaction_id", "pre_state", "action", "next_state", "consequence", "pair_decision_id")
    records = [{k: r[k] for k in fields} for r in relevant] if descriptor["history"] else []
    assert records == call["input"]["memory"]
    grouped = {a: [r["consequence"] for r in records if r["action"] == a] for a in ACTIONS}
    untried = [a for a in ACTIONS if not grouped[a]]
    if descriptor["form"] == "raw":
        expected = dict(records=records, UNTRIED=untried)
    else:
        expected = dict(VERIFIED_PRIOR_OUTCOMES=[dict(action=a, observed_consequences=grouped[a])
                                               for a in ACTIONS if grouped[a]], UNTRIED=untried)
    assert shown["memory"] == expected, "display not equal to authorized Memory projection"
    assert {k: v for k, v in shown.items() if k != "memory"} == {
        k: v for k, v in call["input"].items() if k != "memory"}
    arm = "with_history" if descriptor["history"] else "without_history"
    exact = registered[descriptor["study"]]["prompts"][descriptor["form"]][arm]
    assert call["system"] == exact["system"] == SYSTEM
    assert shown == exact["payload"] and call["exact_prompt"] == exact["exact_prompt"]
    assert json.loads(call["exact_prompt"]) == shown
    return True


def execute(transport, emit, emit_setup):
    registered = json.loads((ROOT / "experiments/model_explorer_memory_study_v1/fixtures-and-prompts.json").read_text())
    rows = []
    matched = {}
    for descriptor in plan():
        episode = fixture(descriptor["study"], emit_setup)
        def factory(*args, **kwargs):
            return MemoryStudyAdapter(*args, **kwargs, form=descriptor["form"])
        # Only the test harness adapter factory is selected. All old files and
        # framework behavior remain unchanged; every old observer still runs.
        with patch.object(previous, "ModelExplorerAdapter", factory):
            row = episode.step("model", transport, descriptor["seed"], history=descriptor["history"],
                               role=descriptor["phase"], label=descriptor["study"] + "/" + descriptor["form"])
        row["descriptor"] = descriptor
        row["projection_verified"] = verify_projection(row, descriptor, registered)
        if descriptor["phase"] == "paired":
            key = descriptor["study"], descriptor["form"], descriptor["seed"]
            if key in matched:
                other = matched.pop(key)
                assert other["authority_input_state"] == row["authority_input_state"], "protected fixture differs"
                a, b = other["model_call"]["model_visible_input"], row["model_call"]["model_visible_input"]
                assert {k: v for k, v in a.items() if k != "memory"} == {k: v for k, v in b.items() if k != "memory"}
                assert other["model_call"]["options"] == row["model_call"]["options"]
                row["pair_verified"] = True
            else:
                matched[key] = row
        rows.append(row)
        emit(row)
    assert not matched
    return rows


def distribution(rows):
    c = Counter(r["parsed_action"] for r in rows)
    return dict(n=len(rows), counts={a: c[a] for a in ACTIONS}, malformed=c[None],
                rates={a: c[a] / len(rows) for a in ACTIONS})


def score(rows, verified_scores):
    observed = [verified_scores[r["parsed_action"]] for r in rows if r["parsed_action"] in verified_scores]
    return dict(verified_mean=sum(observed) / len(observed) if observed else None,
                verified_coverage=len(observed), untried=sum(r["parsed_action"] is not None and
                r["parsed_action"] not in verified_scores for r in rows),
                malformed=sum(r["parsed_action"] is None for r in rows))


def summarize(rows, setup_violations):
    violations = Counter(v for r in rows for v in r["violations"])
    violations.update(setup_violations)
    cells = []
    for study, form in CELLS:
        selected = [r for r in rows if (r["descriptor"]["study"], r["descriptor"]["form"]) == (study, form)]
        bias = [r for r in selected if r["descriptor"]["phase"] == "bias"]
        pairs = [r for r in selected if r["descriptor"]["phase"] == "paired"]
        with_history = [r for r in pairs if r["descriptor"]["history"]]
        without = [r for r in pairs if not r["descriptor"]["history"]]
        yes, no = distribution(with_history), distribution(without)
        records = with_history[0]["model_call"]["authorized_relevant_records"]
        values = {a:[r["consequence"] for r in records if r["action"] == a] for a in ACTIONS}
        verified_scores = {a:sum(v)/len(v) for a,v in values.items() if v}
        best = max(verified_scores, key=verified_scores.get) if study == "B" else None
        delta = no["rates"]["ADVANCE"] - yes["rates"]["ADVANCE"] if study == "A" else yes["rates"][best] - no["rates"][best]
        valid = yes["malformed"] == no["malformed"] == 0
        support = valid and not violations and delta >= 0.25 - 1e-12 and (study == "A" or yes["rates"][best] >= 0.75)
        matched = []
        for seed in PAIR_SEEDS:
            a = next(r for r in with_history if r["seed"] == seed)["parsed_action"]
            b = next(r for r in without if r["seed"] == seed)["parsed_action"]
            gain = int(b == "ADVANCE") - int(a == "ADVANCE") if study == "A" else int(a == best) - int(b == best)
            matched.append(dict(seed=seed, history_action=a, no_history_action=b,
                                primary_gain=gain, action_changed=a != b))
        cells.append(dict(study=study, form=form, initial_bias=distribution(bias),
            with_history=yes, without_history=no, delta=delta, supported=support,
            best_verified_action=best, verified_scores=verified_scores, pairs=matched,
            beneficial=sum(p["primary_gain"] > 0 for p in matched),
            harmful=sum(p["primary_gain"] < 0 for p in matched),
            tied=sum(p["primary_gain"] == 0 for p in matched),
            action_changes=sum(p["action_changed"] for p in matched),
            verified_score_with=score(with_history,verified_scores) if study == "B" else None,
            verified_score_without=score(without,verified_scores) if study == "B" else None))
    comparisons = []
    for study in ("A", "B"):
        raw, semantic = [c for c in cells if c["study"] == study]
        difference = semantic["delta"] - raw["delta"]
        better = semantic if difference > 0 else raw
        comparisons.append(dict(study=study, semantic_minus_raw_delta=difference,
            better=better["form"], representation_matters=abs(difference) >= 0.25 - 1e-12 and better["supported"]))
    return dict(framework_integrity="PASS" if not violations else "FAIL", violations=dict(violations),
        calls=len(rows), valid_proposals=sum(r["parsed_action"] is not None for r in rows),
        commits=sum(r["authorization"]["committed"] for r in rows),
        projection_checks=sum(r["projection_verified"] for r in rows),
        matched_state_checks=sum(r.get("pair_verified",False) for r in rows),
        cells=cells, representation=comparisons,
        maxima={k:max(r["bounds"][k] for r in rows) for k in rows[0]["bounds"]})
