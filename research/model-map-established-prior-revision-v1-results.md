# Established-prior Map revision v1 — results

**ESTABLISHED-PRIOR MAP REVISION REPLICATED.** Framework integrity: **PASS**. Exactly 144 real calls; no retry, output repair, extension or vocabulary pooling. The previous Map-v0 result remains **NOT ESTABLISHED**.

Both O1 and O2 had 12/12 exact old SHIFT-P0 predictions, 12/12 exact new SHIFT-P2 predictions, 12/12 exact old CONTROL-P2 predictions and 12/12 favorable matched pairs; reverse pairs were zero. All 144 outputs were valid. The 24 prediction/receipt disagreements occurred at SHIFT P0, where the visible old history differed from the hidden changed world; every actual commit remained receipt-authoritative.

## 1. Parent identities

Parent `f7b16c4997625e902b59800ec1110806342a1069`; protocol `ca05bf4`; passing zero-call preflight, implementation and annex `5e4283e`, all before inference. Realized-event repair `ca131869b97dd5c96dd60eb7329f65b1a293246f`; minimum repair `8ec32c839133df7ddd76448063b5f765c20155da`. [Frozen inherited hashes](../experiments/model_map_established_prior_revision_v1/frozen-inputs.json) bind the unchanged Map-v0 adapter, parser, boundary, deterministic Explorer and historical sources/results. [Representation-prior checkpoint](representation-priors-and-neutrality-checkpoint.md) governs interpretation. Main and tags unchanged; nothing pushed.

## 2. Why Map-v0 remains NOT ESTABLISHED

The [preserved v0 report](model-map-proposal-v0-results.md) and [compact evidence](../experiments/model_map_proposal_v0/results.json) remain unchanged. Both families had 0/12 exact old SHIFT-H0 predictions, below the frozen ≥10 prerequisite. Two invalid responses additionally failed the all-valid requirement. Perfect 12/12 favorable H2 pairs in each family did not satisfy that registered claim. This follow-up cannot retroactively change it.

## 3. Specific motivating failure

One-observation v0 H0 produced 46 valid responses predicting next_state=2 across 48 calls, with two out-of-domain responses. Valid responses usually supplied the observed +1 consequence but missed the stable next-state relation. All 96 H1/H2 responses predicted next_state=1 correctly. The prospectively registered hypothesis is that two consistent old observations may establish the exact old relation in this fixture; two observations are not assumed generally sufficient.

## 4. Mandatory zero-call preflight

**PASS**, zero model calls. All six requested histories were constructed through authentic receipts. Twelve synthetic probes compared (1,+1) and (0,0) proposals across the six stages/arms: actual receipts were identical for differing predictions within each fixture; latches preceded execution; Measure/Memory followed the actual receipt; old observations remained unchanged. Maximum probe Memory was five. The full 144-prompt annex constructed correctly, with matched P0 prompts byte-identical and P1/P2 differing only in consequences. Preflight and annex replayed byte-for-byte. [Preflight summary/digests](../experiments/model_map_established_prior_revision_v1/preflight-results.json). No authority or architecture edit was needed.

## 5. World regimes

Both worlds start at state 1. CONTROL stays HOLD→(1,+1). In SHIFT, the external driver performs exactly two old HOLD events and then invokes the fixture world’s switch; subsequent HOLD events return (1,−1). Only the external consequence law changes. The trusted receipt emitter, read port, authorization and frozen framework do not change. The proposer receives neither a world reference nor a regime field.

## 6. Direct HOLD-only construction

Each measured sample reconstructs a fresh independent 2/3/4-event HOLD-only prefix using deterministic Explorer and ordinary execution/receipt publication. No navigation, fabricated Memory, alternate action or cross-sample probe carryover. Consecutive transaction IDs are 1…2/3/4, and every pre/next state is 1. Full receipt identity/provenance is checked before projection. With the measured probe, at most five records are retained, within the unchanged bound of eight.

## 7. P0 histories

Both arms show exactly [(1,+1),(1,+1)] from executions 1–2. SHIFT has switched before the measured probe, but that probe sees only the two authentic old observations. Its actual outcome is (1,−1); predicting the old consequence here is compatible with the available evidence and is required for the old-Map prerequisite.

## 8. P1 histories

CONTROL: [(1,+1),(1,+1),(1,+1)]. SHIFT: [(1,+1),(1,+1),(1,−1)]. The two old records coexist with the first authenticated contradiction. P1 is descriptive: no mandatory switch, mean/recency interpretation or post-hoc success threshold.

## 9. P2 histories

CONTROL: [(1,+1),(1,+1),(1,+1),(1,+1)]. SHIFT: [(1,+1),(1,+1),(1,−1),(1,−1)]. Both old observations remain intact alongside two contradictions. Current actual outcomes are CONTROL=(1,+1), SHIFT=(1,−1).

## 10. Unchanged prompt, payload and parser

Exact v0 system instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Compact sorted-key JSON contains state=1, target_action=<opaque HOLD alias>, and VERIFIED_CHRONOLOGICAL_HISTORY rows with transaction_id, surface_action, next_state, consequence. No regime, canonical action, evaluator truth, old prediction, Measure/Recovery, average, recency advice or recommendation. Output is exactly `{"next_state":<integer>,"consequence":<integer>}`; domains {0,1,2,3} and {−1,0,1}. The unchanged parser rejects bool, float, malformed text, duplicate/missing/extra fields, explanation and multiple objects. No repair or retry. Coordinator-supplied identity enters the original pre-execution latch; model text cannot supply identity or authorization.

## 11. Representation families

Only O1=K1/K2/K3 and O2=Q7/M4/Z2. All six full action mappings, twice each per cell; only the HOLD alias is shown. No semantic arm, third vocabulary or neutrality study. Cross-family replication was required prospectively; neither opacity nor matching behavior proves representation neutrality.

## 12. Frozen schedule and runtime

Exactly **144/144** calls: 2 families × 2 arms × 3 stages × 12 schedules. Fresh seeds 60001–60012; mapping index j mod 6; exact counterbalanced order frozen in the [preregistration](model-map-established-prior-revision-v1-preregistration.md) and [prompt digests](../experiments/model_map_established_prior_revision_v1/registration-digests.json). Within each schedule, arms/stages match mapping, seed, sampler and schema. No extension. 432 authenticated setup transactions are separate from the 144 measured proposals.

Pinned dolphin-mixtral:latest / Ollama 0.1.16 / GGUF 47B Q4_0. Complete manifest and all 26,441,544,128 weight bytes matched their frozen digests before inference. Unchanged sampler: temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1. Stateless requests, no training/weight changes/context carryover. Server logs independently record 144 generation requests.

## 13. Validity

**144/144 valid; 0 invalid.** Invalid responses retain their denominator and fail the global validity criterion if present; safe rejection is distinct from an integrity failure. No responses were repaired, replaced or retried. Exact invalid-response details, if any, are in [verification](../experiments/model_map_established_prior_revision_v1/verification.json); full raw evidence stays private.

## 14. P0 old Map — O1

SHIFT exact (1,+1): **12/12**, required ≥10. CONTROL P0 exact old: **12/12**, reported separately. **TWO-OBSERVATION OLD MAP PREREQUISITE ESTABLISHED IN THIS FIXTURE**. This criterion uses the exact pair, not consequence alone.

## 15. P0 old Map — O2

SHIFT exact (1,+1): **12/12**, required ≥10. CONTROL P0 exact old: **12/12**, reported separately. **TWO-OBSERVATION OLD MAP PREREQUISITE ESTABLISHED IN THIS FIXTURE**. This criterion uses the exact pair, not consequence alone.

## 16. CONTROL trajectories

### O1

| Stage | (1,+1) | (1,0) | (1,−1) | Other valid | Invalid | State correct | Consequence correct | Exact current outcome | Mismatches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |
| P1 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |
| P2 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |

Each cell has denominator 12; invalid responses earn no admitted component or exact-pair accuracy.

### O2

| Stage | (1,+1) | (1,0) | (1,−1) | Other valid | Invalid | State correct | Consequence correct | Exact current outcome | Mismatches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |
| P1 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |
| P2 | 12 | 0 | 0 | 0 | 0 | 12 | 12 | 12 | 0 |

Each cell has denominator 12; invalid responses earn no admitted component or exact-pair accuracy.

## 17. SHIFT trajectories

### O1

| Stage | (1,+1) | (1,0) | (1,−1) | Other valid | Invalid | State correct | Consequence correct | Exact current outcome | Mismatches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 12 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 12 |
| P1 | 0 | 0 | 12 | 0 | 0 | 12 | 12 | 12 | 0 |
| P2 | 0 | 0 | 12 | 0 | 0 | 12 | 12 | 12 | 0 |

Each cell has denominator 12; invalid responses earn no admitted component or exact-pair accuracy.

### O2

| Stage | (1,+1) | (1,0) | (1,−1) | Other valid | Invalid | State correct | Consequence correct | Exact current outcome | Mismatches |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 12 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 12 |
| P1 | 0 | 0 | 12 | 0 | 0 | 12 | 12 | 12 | 0 |
| P2 | 0 | 0 | 12 | 0 | 0 | 12 | 12 | 12 | 0 |

Each cell has denominator 12; invalid responses earn no admitted component or exact-pair accuracy.

P1 distribution is descriptive only. Current-outcome accuracy at P0 measures disagreement with a hidden changed world; it does not label an old prediction irrational.

## 18. Matched P2 — O1

Favorable CONTROL=(1,+1), SHIFT=(1,−1): **12/12**, required ≥8. Reverse pairs: **0/12**, allowed ≤1. SHIFT exact new: **12/12**, required ≥9. CONTROL exact old: **12/12**, required ≥9. Full per-schedule pairs are retained in [compact results](../experiments/model_map_established_prior_revision_v1/results.json).

## 19. Matched P2 — O2

Favorable CONTROL=(1,+1), SHIFT=(1,−1): **12/12**, required ≥8. Reverse pairs: **0/12**, allowed ≤1. SHIFT exact new: **12/12**, required ≥9. CONTROL exact old: **12/12**, required ≥9. Full per-schedule pairs are retained in [compact results](../experiments/model_map_established_prior_revision_v1/results.json).

## 20. Primary decision — O1

**SUPPORTED**. All nine frozen checks:

- shift_p0_old: **PASS**
- shift_p2_new: **PASS**
- control_p2_old: **PASS**
- favorable_pairs: **PASS**
- reverse_pairs: **PASS**
- all_144_complete_valid: **PASS**
- framework_integrity: **PASS**
- latched_before_execution: **PASS**
- actual_commits_equal_receipts: **PASS**

## 21. Primary decision — O2

**SUPPORTED**. All nine frozen checks:

- shift_p0_old: **PASS**
- shift_p2_new: **PASS**
- control_p2_old: **PASS**
- favorable_pairs: **PASS**
- reverse_pairs: **PASS**
- all_144_complete_valid: **PASS**
- framework_integrity: **PASS**
- latched_before_execution: **PASS**
- actual_commits_equal_receipts: **PASS**

## 22. Overall decision

**ESTABLISHED-PRIOR MAP REVISION REPLICATED.** Both families independently must pass every frozen requirement. No family pooling, retrospectively altered threshold or substitution of a component score. This result applies to this registered fixture/model/run only and does not alter Map-v0.

## 23. Next-state component analysis

| Family / arm | P0 next_state=1 | P1 next_state=1 | P2 next_state=1 |
|---|---:|---:|---:|
| O1 / CONTROL | 12/12 | 12/12 | 12/12 |
| O1 / SHIFT | 12/12 | 12/12 | 12/12 |
| O2 / CONTROL | 12/12 | 12/12 | 12/12 |
| O2 / SHIFT | 12/12 | 12/12 | 12/12 |

All authentic actual next states remain 1. Component accuracy counts admitted predictions; invalid response fields remain separately inspectable. State accuracy does not substitute for exact-pair success.

## 24. Consequence component analysis

| Family / arm / stage | Predicted +1 | Predicted 0 | Predicted −1 | Invalid |
|---|---:|---:|---:|---:|
| O1 / CONTROL / P0 | 12 | 0 | 0 | 0 |
| O1 / CONTROL / P1 | 12 | 0 | 0 | 0 |
| O1 / CONTROL / P2 | 12 | 0 | 0 | 0 |
| O1 / SHIFT / P0 | 12 | 0 | 0 | 0 |
| O1 / SHIFT / P1 | 0 | 0 | 12 | 0 |
| O1 / SHIFT / P2 | 0 | 0 | 12 | 0 |
| O2 / CONTROL / P0 | 12 | 0 | 0 | 0 |
| O2 / CONTROL / P1 | 12 | 0 | 0 | 0 |
| O2 / CONTROL / P2 | 12 | 0 | 0 | 0 |
| O2 / SHIFT / P0 | 12 | 0 | 0 | 0 |
| O2 / SHIFT / P1 | 0 | 0 | 12 | 0 |
| O2 / SHIFT / P2 | 0 | 0 | 12 | 0 |

Denominator 12 per cell. CONTROL actual consequence stays +1; every measured SHIFT probe actually realizes −1, including P0. These distributions separate consequence revision from stable-state prediction. No post-hoc rule is applied at P1, and consequence-only success cannot replace the exact-pair criterion.

## 25. Prospective history-depth comparison with v0

Preserved Map-v0 H0: 48 calls, 46 valid responses predicting next_state=2, two invalid; zero admitted next_state=1 predictions. New two-observation P0: **48/48** admitted next_state=1 predictions; **0** invalid responses. Raw next_state=1 fields in invalid P0 responses, if any: 0. Family/arm rates are shown above.

This is a descriptive prospective comparison of the registered history-depth hypothesis, not pooled inference across studies. The new design also removes navigation, changes visible transaction IDs, uses fresh seeds and switches after two target observations. Therefore it does not isolate history depth as a sole cause or show two observations are generally sufficient. No v0 record, threshold or verdict was changed.

## 26. Measure behavior

**24** admitted predictions disagreed with their authentic receipts. Measure compared the original pre-execution latch against receipt-derived evidence; every committed measurement flag matched the independently recomputed comparison. A wrong prediction gained no truth authority and did not prevent an otherwise authentic event from being recorded.

## 27. Recovery behavior

Measured Map probes: **0** Map quarantines; **0** state Recovery authorizations; actual observed Recovery returns `{}`. HOLD leaves the authorized incumbent state at 1. Prediction mismatch alone need not invoke state Recovery in the unchanged framework. No Recovery execution is inferred merely from a mismatch, and no receipt can be rewritten by Recovery.

## 28. Memory preservation

Prior history remained unchanged in **144/144** samples. The two authenticated old +1 observations coexist with every later verified −1 in SHIFT P1/P2. **144** commits record actual receipt outcomes, never substituted predictions. Before/after Memory, pairs, receipt packages, exact object identity and full event binding are retained. Invalid rejection, if any, publishes no protected event. No action ban, rewritten past or cross-sample probe leakage.

## 29. Framework integrity

**MODEL MAP PROPOSAL BOUNDARY INTEGRITY PASS.**

- protected false accepts: **0**
- receipt mismatch accepts: **0**
- unauthorized commits: **0**
- stale duplicate authorizations: **0**
- malformed prediction commits: **0**
- direct protected mutations: **0**
- post execution prediction rewrites: **0**
- historical receipt rewrites: **0**
- bound violations: **0**

Admitted predictions latched before execution: **144**. Protected maxima: `{"map_quarantine": 0, "memory": 5, "memory_quarantine": 0, "packages": 5, "pairs": 5, "pending_authentic": 1, "trace": 15}`. MODEL CAN READ: authorized state and authenticated target history. CAN PROPOSE: one bounded Map prediction. CAN MUTATE: nothing protected directly. CAN AUTHORIZE: nothing. Cannot choose actions, switch the world, mint receipts, rewrite reality, approve its prediction or alter Recovery. Model transport receives only immutable prompt text and a seed; receipt origin stays external.

## 30. Unchanged post-run parser controls

After all 144 calls, **18** synthetic admission cases ran: nine per family, identical outputs to Map-v0. Malformed JSON, explanation, invalid next state, invalid consequence, bool, float, missing key, extra key and multiple objects all rejected before execution; **0** commits. Separate from preflight/unit tests and not counted as model behavior. No expanded attack campaign.

## 31. Exact replay

Executed with **zero new inference**. All seven files—registered prompts, raw model calls, steps, authenticated setup, controls, metadata, compact results—were **byte-identical**. This verifies identical protected outcomes and the full summary, not just the verdict. Preflight also replayed exactly. Public evidence hashes and [reproduction instructions](../experiments/model_map_established_prior_revision_v1/README.md) identify the private archive needed for replay. The compact public summary cannot substitute for raw evidence.

## 32. Actually executed regressions

**23 commands returned their expected exit statuses**, executed after this run. [Verification](../experiments/model_map_established_prior_revision_v1/verification.json) records exact commands, timestamps, exit codes and log hashes.

| Check | Result |
|---|---|
| Current study + Map-v0 + contradiction-v1 replays | All exact evidence/results byte-identical; historical verdicts unchanged |
| Contradiction feasibility replay | All six old stage histories and original evidence byte-identical |
| Realized-event tests/campaign/replay | 6 tests; original repair evidence and out-of-model root failure preserved |
| Old contradiction-v0 tests/diagnostic | 3 tests; diagnostic exit **2 as expected**, failure evidence byte-identical |
| Factorial / semantic / adaptive / Memory / original Explorer replays | 216 / 288 / 288 / 224 / 69 recorded real responses; no new inference; summaries unchanged |
| Minimum repair 1 | 177 runs; protected pass and expected negative controls preserved |
| Base v0 / v1 / v2 | 12 / 10 / 13 tests; 42 / 69 / 57 scenarios |
| Inherited Map tests/gate and contradiction-v1 tests | Expected passes; no source changes |
| New stage/history tests | 5 passed |
| New zero-call preflight replay | All six histories, twelve synthetic probes and prompt annex byte-identical |

Previous common-mode/registry/root false accepts remain documented out-of-model negatives. No experimental result was edited.

## 33. Limitations

One pinned model/runtime, one state/action, two alias families, 12 seeds, synthetic bounded worlds and independently reconstructed samples. No persistent model state, trained weights or learned framework law. Software receipt authenticity rests on the external root and trusted Python process; it is not proof of physical truth or hostile-process isolation. Representation is controlled only within the registered renderings, not universally neutral. P1 is conflicting evidence without a mandatory interpretation. History-depth comparison changes several registered fixture details and does not isolate a unique causal mechanism. Full replay needs the privately retained archive. Correct predictions confer no authority; trusted root compromise remains outside the protected model.

## 34. Narrowest defensible conclusion

**ESTABLISHED-PRIOR MAP REVISION REPLICATED.** Both opaque families established the exact old relation at P0 and met every registered P2 revision criterion independently. Authenticated contradictory history changed Map proposals relative to stable CONTROL in this bounded fixture; reality remained authoritative throughout. This is prompt-conditioned prediction behavior, not persistent/weight learning, RL, causal understanding, general world-model learning/concept drift, AGI or RSI.

## 35. Recommendation

The current bounded Map-proposal question is answered under this protocol. Stop; do not run a third Map study merely to strengthen the numbers. Do not combine Explorer+Map, move the model into Recovery, change receipt authority or launch another vocabulary study. Historical results remain intact.
