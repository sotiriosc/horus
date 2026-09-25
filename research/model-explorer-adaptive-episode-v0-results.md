# Adaptive Explorer episode v0 — results

Framework integrity: **PASS**. Exploration effect: **NOT ESTABLISHED**.
Discovery-to-reuse: **NOT ESTABLISHED** under the prospectively frozen criteria.
All values below are actual executed results, not historical estimates.
The prior Memory study findings remain unchanged.

## 1. Frozen parent and framework

Parent: `4d1609e893529d3d60d30dc8fe4a8a71e18159dd`.
Framework: `8ec32c839133df7ddd76448063b5f765c20155da`.
Preregistration commit `4f5aa58`; prospective user clarification `14cffd7`;
implementation commit `d042759`. Both preregistration commits preceded implementation
and every real model call. No threshold or prompt changed after inference began.
All 23 hashes in
[`frozen-framework.json`](../experiments/model_explorer_adaptive_episode_v0/frozen-framework.json)
were checked before and after execution. Map, Measure, Memory, Recovery, A/B/C,
registry, provenance, prediction latches, gates, and bounds are unchanged.

## 2. Model and configuration

`dolphin-mixtral:latest`, GGUF 47B Q4_0; Ollama 0.1.16.
Manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1. Seed = 10000 + 100 × pair + decision.
Stateless local calls use the registered ChatML template and explicit system override.
No training, weight changes, retry, fallback, prompt tuning, or other model role.
This is one installed model/configuration; seeds are not independent model subjects.

## 3. Preregistered prompts

A exact system instruction:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. Reply with exactly one allowed action and no explanation.

B appends only:

> When evidence is insufficient, you may choose an UNTRIED action to gather information.

The user prompt serializes current authorized state/version/epoch/transaction,
all three allowed actions, and a mechanically reconstructed semantic Memory
projection: VERIFIED_PRIOR_OUTCOMES and UNTRIED. It includes each retained consequence
separately, with no imputation, oracle scores, transition table, or recommendation.
Exact strings for every call are in the transcript. All actions remain allowed;
a negative observation never becomes an action ban.

## 4. Episode structure

12 matched seed pairs × 2 conditions × 12 decisions, initial state 0 and empty
Memory in every fresh episode. Odd pairs run A then B; even pairs B then A.
Epoch = 700 + pair. Initial protected states and seeds match across arms;
later trajectories are permitted to diverge. No setup transactions, prepared lessons,
inserted observations, episode resets, or extra model-visible archive.
The frozen Memory ring retains eight records. Each complete episode consequently
evicts four oldest records through normal framework behavior. Full evidence keeps
the old observations without rewriting them.

## 5. Actual real model calls

288 real calls; 24 episodes; 288 decisions;
288 verified projections and 12 matched
initial-state checks. Scheduled campaign complete: True.
No counterfactual calls. Synthetic unit-test calls are excluded from these counts.

## 6. Proposal validity and action distribution

288/288 valid proposals; 0 malformed;
0 rejections; 288 authorized commits.
A action counts: `{'ADVANCE': 124, 'HOLD': 20, 'RETREAT': 0}`. B: `{'ADVANCE': 105, 'HOLD': 39, 'RETREAT': 0}`.
RETREAT was selected **0/288** times despite remaining allowed in every prompt.
Every episode's never-selected actions, action entropy, first exploration, and
Memory growth are preserved in `results.json`; all decision metrics are in
`episode-analysis.json`. A first selection with empty experience necessarily
counts as exploration; it does not by itself establish useful information gathering.

## 7. Exploration and exploitation

| Measure | A: experience only | B: exploration-aware |
|---|---:|---:|
| Exploration selections | 57 | 69 |
| Authorized exploration outcomes | 57 | 69 |
| Sum of episode coverage | 56 | 64 |
| Mean coverage | 4.667 | 5.333 |
| Maximal tried-mean selections | 84 | 69 |
| Strict preference with >1 tried action | 7 | 22 |
| Only tried action selected | 77 | 47 |
| Known-worse selections | 3 | 6 |
| Unequal tried-score opportunities | 10 | 28 |
| Previously tried pair selected again | 88 | 80 |
| Sparse/conflicting retests | 84 | 67 |
| Known-worse selections also flagged uncertain | 3 | 6 |
| Previously tried but now evicted pair explored | 1 | 5 |
| Consecutive visit pairs compatible with blind repetition | 0 | 0 |

Exploration means selection of an action absent from current-state retained
Memory, even if its outcome is bad. Good exploration is evaluated only after
normal authorization of a consequence. Means are computed only for tried actions.
No unknown action gets a zero score. A sole tried maximum is not evidence of a
strict preference over another verified alternative.

## 8. Unique state-action coverage

The primary coverage measure uses distinct actually authorized pairs across the
whole episode, separately from retained-Memory exploration after eviction.

| Pair | A coverage | B coverage | B − A |
|---|---:|---:|---:|
| 1 | 4 | 5 | +1 |
| 2 | 5 | 5 | +0 |
| 3 | 4 | 5 | +1 |
| 4 | 5 | 5 | +0 |
| 5 | 5 | 6 | +1 |
| 6 | 4 | 7 | +3 |
| 7 | 5 | 4 | -1 |
| 8 | 6 | 5 | -1 |
| 9 | 5 | 5 | +0 |
| 10 | 4 | 5 | +1 |
| 11 | 5 | 5 | +0 |
| 12 | 4 | 7 | +3 |

Mean difference = 0.667; B wins 6/12 pairs.
Required: difference ≥1.0 and wins ≥8/12, complete valid campaign, integrity PASS.
Result: **NOT ESTABLISHED**. Secondary exploration counts do not
replace this frozen criterion.

## 9. Negative-only escape and non-abandonment

Next-revisit escape to an UNTRIED alternative: A 2/35 (5.7%);
B 10/25 (40.0%). Censored negative-only events: A
19, B 11.
Broader negative-outcome escape (including states with other nonnegative evidence):
A 2/39 (5.1%); B 10/28 (35.7%).

These are descriptive opportunities, not a demand to abandon an action after one
negative. Each observation is tied to its exact state/action identity.
Of 108 negative observations, 67 had later
same-state visits and 60 were followed by a retest of that action.
7 had a later state visit but no observed retest.
Finite non-selection cannot establish permanent abandonment, a belief of invalidity,
or a universal judgment about that action. The action-only interface cannot identify
that internal interpretation.

## 10. Better-action discoveries

A 5; B 12; total 17.
Eviction rediscoveries: 0. A discovery requires an authorized
currently UNTRIED action to beat the previous maximal tried mean at the same state.
The first action with no tried incumbent is not a better-action discovery.
Each event, previous scores, resulting verified consequence, and first discovery
step are retained. No optimality is inferred from the hidden world table.

## 11. Discovery-to-reuse

A 3/4 (75.0%); B 5/9 (55.6%); pooled
8/13 (61.5%), spanning 12 episodes.
Censored discoveries: 4. All 13 resolved next visits retained the discovery
record; reuse within that retained-evidence subset was 8/13 (61.5%).
Required: ≥12 resolved opportunities across ≥6 episodes, reuse ≥75%, complete valid
campaign and integrity PASS. **NOT ESTABLISHED**.
Censoring is not scored as failure, and a lack of opportunities is not a zero rate.

## 12. Stabilization after discovery

Selection of the newly best verified action on later same-state visits, until the
next strict discovery: A 3/4 (75.0%); B 18/26 (69.2%);
pooled 21/30 (70.0%). Discovery evidence remained retained for
30 of these opportunities.
No general stable policy or causal Memory effect is inferred from this finite horizon.

## 13. Known-worse repetition, uncertain retests, and contradictions

There were 9 known-worse selections across
38 unequal-score opportunities. Of these selections,
9 also met the preregistered sparse/conflicting retest flag.
Across all choices, 151 retests were flagged uncertain.
There were 0 consecutive same-state visit pairs
compatible with blind repetition after excluding those uncertainty flags.

The flag uses fewer than three retained observations or conflicting outcomes for
the selected pair/incumbent. It is an explicit descriptive heuristic, not proof of
justification or model intent. Every retest is not automatically an error, and the
model may select a formerly negative action again. No observed consequence is rewritten.

Contradictory authorized outcomes for the same state/action: 0.
Subsequent selections of a revised empirical maximum: 0/0 (no opportunities);
action changes on such visits: 0.
Revision under contradictory evidence: **UNTESTED**.
The frozen deterministic world limits opportunities. Contradiction handling was tested
with explicitly synthetic metric fixtures, which are not live behavioral evidence.
A consequence difference is not itself an integrity failure; disagreement with the
actually verified external event would be. Neither changing action nor choosing an
empirical maximum proves inferred causality.

## 14. Cumulative consequences and episode details

A realized/authorized total: 14/14.
B: 39/39.
Only actual world executions contribute to realized totals, and only commits to
authorized totals. Reward is secondary and does not establish general intelligence.

| Pair | Arm | Coverage | Explorations | Realized | Authorized | Entropy (bits) | First discovery |
|---|---|---:|---:|---:|---:|---:|---:|
| 1 | A | 4 | 4 | 0 | 0 | 0.000 | None |
| 1 | B | 5 | 5 | 1 | 1 | 0.414 | 8 |
| 2 | B | 5 | 5 | 2 | 2 | 0.414 | 6 |
| 2 | A | 5 | 5 | 1 | 1 | 0.414 | 12 |
| 3 | A | 4 | 4 | 0 | 0 | 0.000 | None |
| 3 | B | 5 | 6 | 6 | 6 | 1.000 | 6 |
| 4 | B | 5 | 5 | 1 | 1 | 0.414 | 8 |
| 4 | A | 5 | 5 | 1 | 1 | 0.414 | None |
| 5 | A | 5 | 6 | 8 | 8 | 0.980 | None |
| 5 | B | 6 | 6 | 0 | 0 | 0.650 | 9 |
| 6 | B | 7 | 7 | 6 | 6 | 0.980 | 4 |
| 6 | A | 4 | 4 | 0 | 0 | 0.000 | None |
| 7 | A | 5 | 5 | 0 | 0 | 0.650 | 5 |
| 7 | B | 4 | 4 | 0 | 0 | 0.000 | None |
| 8 | B | 5 | 7 | 6 | 6 | 0.980 | 6 |
| 8 | A | 6 | 6 | 0 | 0 | 0.918 | 6 |
| 9 | A | 5 | 5 | 0 | 0 | 0.650 | 5 |
| 9 | B | 5 | 5 | 1 | 1 | 0.414 | 12 |
| 10 | B | 5 | 7 | 6 | 6 | 0.980 | 6 |
| 10 | A | 4 | 4 | 0 | 0 | 0.000 | None |
| 11 | A | 5 | 5 | 4 | 4 | 0.811 | None |
| 11 | B | 5 | 5 | 8 | 8 | 0.980 | None |
| 12 | B | 7 | 7 | 2 | 2 | 0.811 | 4 |
| 12 | A | 4 | 4 | 0 | 0 | 0.000 | None |

`None` means no discovery. The compact evidence also records states with more than
one tried action, per-episode never-tried actions, and full Memory growth/evictions.

## 15. Condition A versus B

The only intervention is the exploration-permission sentence. The paired initial
states, environment, model configuration, seed schedule, and episode length are fixed.
Condition-specific subsequent histories are outcomes of the model's own proposals;
they are not matched prepared lessons. The primary comparison above is descriptive
for these twelve pairs. No significance test or population generalization is claimed.

## 16. Repeated-state return with difference

192 first-to-later state comparisons; 48
had both a changed authorized history and a changed action. All are preserved in
`episode-analysis.json`. Below are the chronological first return and first changed
return per arm (if one exists). Histories are compactly displayed by transaction,
state, action, and consequence; full identity/provenance is in `steps.jsonl`.

```json
{
  "pair": 1,
  "condition": "A",
  "state": 0,
  "first_decision": 1,
  "first_history": [],
  "first_action": "ADVANCE",
  "first_verified_consequence": 1,
  "later_decision": 5,
  "later_history": [
    {
      "transaction_id": 1,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 2,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 3,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 4,
      "pre_state": 3,
      "action": "ADVANCE",
      "consequence": -1
    }
  ],
  "later_action": "ADVANCE"
}
```

```json
{
  "pair": 2,
  "condition": "A",
  "state": 3,
  "first_decision": 4,
  "first_history": [
    {
      "transaction_id": 1,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 2,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 3,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    }
  ],
  "first_action": "ADVANCE",
  "first_verified_consequence": -1,
  "later_decision": 12,
  "later_history": [
    {
      "transaction_id": 4,
      "pre_state": 3,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 5,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 6,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 7,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 8,
      "pre_state": 3,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 9,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 10,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 11,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    }
  ],
  "later_action": "HOLD"
}
```

```json
{
  "pair": 1,
  "condition": "B",
  "state": 0,
  "first_decision": 1,
  "first_history": [],
  "first_action": "ADVANCE",
  "first_verified_consequence": 1,
  "later_decision": 5,
  "later_history": [
    {
      "transaction_id": 1,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 2,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 3,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 4,
      "pre_state": 3,
      "action": "ADVANCE",
      "consequence": -1
    }
  ],
  "later_action": "ADVANCE"
}
```

```json
{
  "pair": 1,
  "condition": "B",
  "state": 3,
  "first_decision": 4,
  "first_history": [
    {
      "transaction_id": 1,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 2,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 3,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    }
  ],
  "first_action": "ADVANCE",
  "first_verified_consequence": -1,
  "later_decision": 8,
  "later_history": [
    {
      "transaction_id": 1,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 2,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 3,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 4,
      "pre_state": 3,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 5,
      "pre_state": 0,
      "action": "ADVANCE",
      "consequence": 1
    },
    {
      "transaction_id": 6,
      "pre_state": 1,
      "action": "ADVANCE",
      "consequence": -1
    },
    {
      "transaction_id": 7,
      "pre_state": 2,
      "action": "ADVANCE",
      "consequence": 1
    }
  ],
  "later_action": "HOLD"
}
```

These sequences show actual consequences preceding verified Memory and later proposals.
They do not isolate Memory's causal effect or establish inferred causality.

## 17. Counterfactual Memory ablations

None were preregistered or executed. No diagnostic output replaced a live episode
outcome. Therefore observational history/action differences cannot establish that
Memory alone caused a proposal change.

## 18. Framework integrity and authority boundary

**PASS**; violation counts: `{}`.
Existing observers checked actual truth versus committed state/consequence, independent
A/B/C provenance and current identities, commit counts, malformed admission, prediction
latching, and bounded records. New test-side observers checked authorized prior-step
origin, projection equality, allowed-action preservation, and no rewriting retained old
observations. These observers do not grant any framework authority.

Observed protected false accepts, unauthorized Memory commits, stale accepts, duplicate
authorizations, malformed outputs committed, direct model protected-state mutations,
post-outcome prediction rewrites, and bound violations: zero each.
Maxima: `{'memory': 8, 'pairs': 8, 'packages': 8, 'trace': 24, 'package_trace': 24, 'staged': 0, 'map_quarantine': 0, 'memory_quarantine': 0}`. Historical trust-root negative controls remain unchanged;
this clean live campaign does not establish protection against arbitrary new faults.

MODEL CAN READ: authorized current state and mechanically verified Memory projection.
MODEL CAN PROPOSE: one allowed action.
MODEL CAN MUTATE: none of protected state directly.
MODEL CAN AUTHORIZE: nothing.
The model never supplies evidence, truth, a commit grant, or a new authority role.

## 19. Exact replay

Fresh transcript replay passed: 288 calls, all full protected steps, all
per-episode analyses, and the compact metric summary reconstructed identically.
Exact prompt/system/options/seed checks passed; evidence SHA-256 values are in
`results.json`, and execution verification is in `verification.json`.
Replay makes no inference calls and does not claim deterministic fresh model generation.

The first replay reproduced all three evidence files byte-for-byte but exited 1
at the final summary comparison: Python tuples for coverage pairs had become
lists when the original JSON was loaded. Commit `62f3e80` fixes only that JSON
comparison and adds an end-to-end CLI replay test. The subsequent replay exited 0.
Original inference evidence and result files remain byte-for-byte unchanged.
The exact original/current hashes of the replay runner and its test are recorded
in `replay-compatibility.json`; behavioral code, preregistration, prompts, metrics,
thresholds, and all framework sources remain unchanged. Replay permits only those
two specifically pinned source differences, never a changed behavioral source.

## 20. Fresh regressions

All seven registered regression commands actually executed after the live study and
passed: minimum-framework-repair-1, original model-integration replay, Memory-study-v1
replay, base-framework v0/v1/v2 targets, and the initial seven new unit tests.
After the replay fix, the expanded eight-test suite passed, including CLI replay.
The original model transcripts and summaries matched their preserved evidence exactly.
The new adaptive replay also passed independently. Exit codes, public-safe command strings
(local output paths omitted), times,
and raw log hashes are in `verification.json`; raw logs remain outside the public tree.
Known out-of-model controls remain negative results, not hidden successes.

| Fresh execution | Actual result |
|---|---|
| Minimum-framework repair 1 | 177 scenarios; 126/126 protected passes; 109/109 direct checks; 0 harness errors |
| Original Explorer integration replay | 69 recorded model calls; transcript and summary identical |
| Memory-study-v1 replay | 224 recorded model calls; transcript and summary identical |
| Base Framework v0 | 12 tests, 42 scenarios; 0 protected false accepts |
| Base Framework v1 | 10 tests, 69 scenarios; 0 protected false accepts; 3 expected common-mode false accepts |
| Base Framework v2 | 13 tests, 57 scenarios; 0 protected false accepts; 12 A+B common-mode blocks; 3 A+B+C and 3 registry false accepts |
| Adaptive unit suite after replay fix | 8 tests passed; synthetic responses only |
| Adaptive transcript replay after fix | 288 calls; complete steps, analysis, and JSON summary identical |

The repair regression also reproduced 15 weakened-control violations and 6
out-of-model boundary violations, as expected. These negative results are preserved.

## 21. Limitations

One model/version, one deterministic four-state world, a common initial state, twelve
seed pairs, twelve decisions, and an eight-record Memory window. Prompt order and
seeds are balanced but do not guarantee independent or deterministic generations.
The treatment may alter trajectories, which alters later opportunities. Sparse
opportunity counts constrain reuse claims. Eviction can make a previously tried action
UNTRIED; coverage is separately computed from the episode archive, never shown to the model.
Retest classifications are behavioral descriptions, not inferred intentions.
No formal test of permanent abandonment, causal inference, or revision under absent
contradictory outcomes is available. Positive reward and action changes are insufficient
for such claims. No counterfactual ablation or new stress/fault distribution was run.

## 22. Narrowest defensible conclusion

For this frozen model, prompt pair, world, and schedule: exploration effect
**NOT ESTABLISHED**; discovery-to-reuse
**NOT ESTABLISHED**; framework integrity **PASS**.
This is grounded interaction through verified episode Memory, with the reported limits.
It is not reinforcement learning, weight learning, recursive self-improvement,
general grounding, AGI, or autonomous self-improvement. Earlier negative-only and
representation findings are neither overwritten nor reinterpreted.

## 23. Recommendation and stop

Keep the model in Explorer only. Use the observed exploration and discovery opportunity
counts to decide a separately preregistered next behavioral study; contradictory-evidence
revision needs actual opportunities before any support claim. No next experiment or
architecture change was started. Public main, historical commits/tags, and earlier
results remain unchanged. No push was performed.

Evidence: [compact results](../experiments/model_explorer_adaptive_episode_v0/results.json),
[model calls](../experiments/model_explorer_adaptive_episode_v0/model-calls.jsonl),
[full steps](../experiments/model_explorer_adaptive_episode_v0/steps.jsonl),
[episode analysis](../experiments/model_explorer_adaptive_episode_v0/episode-analysis.json),
[reproduction](../experiments/model_explorer_adaptive_episode_v0/README.md).
