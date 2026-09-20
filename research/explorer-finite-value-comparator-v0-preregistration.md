# Explorer finite-value comparator v0: preregistration

Parent: research/map-explorer-oracle-decomposition-v0, commit 2679cff20b28079b4358fe463f68e5822e5cc205. Preserve its PIPELINE NOT FULLY ESTABLISHED and all three primary stage negatives; preserve the temporal Map negative, interface A, both earlier Explorer negatives, stale-Memory Map REPLICATED and every authority/grounding/UNKNOWN/representation checkpoint. Main/tags unchanged; push nothing.

## Question and scope

Can the real Explorer model select the unique highest finite predicted consequence, especially 0 rather than +1? Separately, do irrelevant next_state fields change the choice under the SAME seed? This is a detached comparator diagnostic, not a Memory, world-model or temporal forecasting study. In the prior Oracle decomposition D1 scored O1 3/6 and O2 2/6 despite accurate forecasts with consequences {0,-1,-1}; that negative remains unchanged.

Exactly144 real Explorer calls. Zero Map/model Recovery calls, zero world execution, zero Memory changes. No framework/world/Memory instance is needed. Runtime guards forbid world execution, episode-controller construction, Map prediction and Memory construction. No measured choice executes or obtains authority. Detached experimental values are not receipts or authenticated facts.

## Consequence relations and balance

R1: {+1,0,-1}; R2: {+1,-1,-1}; R3: {0,-1,-1}. Unique-best consequence is +1,+1,0 respectively. R3 is primary. No easy/hard, relation, oracle, evaluator, confidence or history label enters the prompt.

Canonical underlying order is ADVANCE,HOLD,RETREAT. Enumerate itertools.permutations((1,0,-1)) lexicographically by that input order:

0:(1,0,-1); 1:(1,-1,0); 2:(0,1,-1); 3:(0,-1,1); 4:(-1,1,0); 5:(-1,0,1).

For schedules j=0..11, R1 assignment indices are prospectively fixed as:

`0,3,2,0,3,2,4,1,5,5,4,1`.

Every full R1 assignment appears twice. R2/R3 retain that schedule's unique-best underlying action and set the two other consequences to -1; best is +1 for R2,0 for R3. Target actions in order are ADVANCE,RETREAT,HOLD,ADVANCE,RETREAT,HOLD,HOLD,ADVANCE,RETREAT,RETREAT,HOLD,ADVANCE. Each block of three contains all actions; each action is best four times per relation/family. Each opaque alias is likewise best four times. The same mapping's two occurrences have different underlying targets. This is prospective balance, not a choice based on model responses.

## Matched next-state conditions

N: all three next_state values are1.

V: enumerate permutations((0,1,2)) in the same canonical underlying action order and use index (j+1) mod6. All six assignments appear twice; all values are valid and distinct. The best action's V next_state is0,1,2 four times each per relation/family. This avoids making the maximum next_state a systematic target cue.

N/V have exactly the same current state1, mapping, aliases, row order and consequences. Only next_state changes. Use the identical seed and sampler within each pair. Corresponding families also have matched seeds. No oracle/world is evaluated to produce these intentionally detached experimental forecasts.

## Model-facing view and instruction

Exactly state and actions. Each of three action rows has only action (opaque alias) and map_prediction with next_state (finite integer) and consequence (-1,0,+1). No history, confidence, depth, means, target or evaluator information enters the payload.

Use exactly the existing instruction:

> Choose the allowed action whose current Map prediction has the highest predicted consequence. Reply with exactly one allowed action and no explanation.

The historical strict opaque parser is unchanged. Outer whitespace is handled as before. Canonical action names, JSON, explanations and unknown labels are invalid; no extraction/coercion/retry. Two invalid responses do not count as same action; invalid pairs are reported as not comparable in addition to same/different counts.

Pinned model/sampler remain unchanged: dolphin-mixtral:latest, Ollama0.1.16, GGUF47B Q4_0; verify every manifest/blob byte before inference. temperature .2, top_p .9, top_k40, num_ctx2048, repeat_penalty1.1, num_predict16. Stateless requests, no returned context/chat history/weight updates.

## Representations, schedule and budget

O1=K1/K2/K3; O2=Q7/M4/Z2. Use all six historical complete mappings, mapping index j mod6, j=0..11. Rows remain in the family's fixed alias order.

Freeze relation order R1,R2,R3, then j ascending. Family order is O1,O2 when relation_index+j is even, otherwise O2,O1. Within family, N then V when relation_index+j+family_index is even, otherwise V then N. This counterbalances paired condition order. No output-adaptive order.

Seed=97001+100*relation_index+j, identical for N/V and matched O1/O2. schedule.json freezes all144 exact request hashes before inference. Budget:3 relations ×2 conditions ×12 schedules ×2 families = exactly144 Explorer calls. No retries, replacements or extensions. A transport ambiguity/storage/integrity failure stops without automatic reissue; malformed completed responses are recorded as invalid and the fixed schedule continues.

## Primary R3 family rule

ZERO-OVER-NEGATIVE COMPARATOR SUPPORTED iff ALL:

1. All24 R3 calls complete.
2. Valid>=23/24.
3. N correct>=10/12.
4. V correct>=10/12.
5. Matched same valid action>=10/12.
6. Every underlying target action has>=3/4 correct in N.
7. Exact replay passes.

Overall ZERO-OVER-NEGATIVE COMPARATOR REPLICATED requires both O1 and O2 independently. Otherwise NOT ESTABLISHED. No pooling or threshold changes.

## Positive-best controls

Report R1 and R2 separately by family/condition: valid, correct, underlying-action and alias distributions. No support threshold was specified for these controls; they remain descriptive and must not be retroactively labeled pass/fail or used to rescue R3. Differences across relations can describe a concentration of errors but do not identify an internal mechanism.

## Next-state invariance family rule

NEXT_STATE IRRELEVANCE SUPPORTED iff ALL:

1. All72 family calls complete.
2. Valid>=70/72.
3. Same valid N/V action>=32/36.
4. Absolute difference between total N and V correct selections<=3.
5. R3 same-action>=10/12.
6. Exact replay passes.

Report this separately from R3. Replication requires both families. This is bounded behavioral invariance only, not proof of internal feature use or non-use.

## Diagnostics and interpretation

Retain every call's relation/family/schedule/mapping/alias/underlying target/condition, original choice and correctness. Every matched pair records N choice, V choice, same/different/not-comparable, N correctness and V correctness. Report aggregates by relation, condition, representation, mapping, target alias and underlying target. All values are finite experimental forecasts; the unique numeric maximum defines scoring, not a mechanical production Explorer.

Strong R1/R2 with weak R3 can suggest concentration in the registered0-over-negative relation, without inference about why internally. If R3 N meets the registered N accuracy threshold while V does not, the observed paired difference may suggest irrelevant-field/representation interference; it does not prove an internal mechanism. If R3 fails even in N, that is evidence against using this model role as a reliable deterministic argmax comparator in this bounded task.

Prospective architectural consequence, NOT implemented here: if reliable finite argmax fails even with neutral next_state, a later separately authorized architecture decision should compare MODEL EXPLORER with MECHANICAL ARGMAX EXPLORER. A deterministic comparison does not require a language model unless Explorer contributes something beyond exploitation. This campaign adds no mechanical Explorer or closed loop.

## Preflight, durability, replay and preservation

Before inference verify all144 schema/request hashes, relation values/unique maxima, all target/mapping/alias balances, V target next-state balance, pair equality except next_state, exact same pair/family seeds, instruction/parser identity and world/Memory/Map isolation. Run pure scoring controls and write-ahead crash/torn-record/fsync tests on durable storage. Run an explicitly synthetic recording/replay control with invalid replies. These are preflight controls, not model evidence.

Use a durable private archive outside the public tree. Before each send fsync descriptor, detached view, exact prompt/request bytes and hash; fsync raw response before parse; fsync parsed result before the next request. Exclusive campaign reservation, no ambiguous reissue. Replay all144 saved responses with sockets forbidden, the same isolation guards and zero inference. Require all nine deterministic files to match byte-for-byte; finalized results/replay gates are stored separately from original live evidence.

Historical preservation is read-only: verify every inherited substantive file, earlier results, refs/main/tags and sealed private archive checksums. Do not rerun older world-based experiments because this task explicitly prohibits world execution. Report preservation checks as hashes/read-only checks, never as newly executed historical tests/replays.

Public tree contains implementation, preregistration, compact parsed results, reproduction instructions and report. Raw prompts/responses and complete journals stay private. Preserve all old negatives and positives unchanged.

Stop after144 calls, exact replay and preservation. No Map changes/calls, world execution, Memory changes, closed loop, mechanical Explorer, prompt tuning, new relations, threshold changes, main/tag edits or push. The bounded question is whether observed comparison weakness is concentrated in0>-1 and/or sensitivity to irrelevant next_state values.
