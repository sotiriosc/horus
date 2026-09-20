# Explorer value-aggregation contract v0 — preregistration

Parent: `8e7e9905ae346d1c3e9beb0a04b7e9ba0deb1626`, cross-episode stale-Memory Explorer revision NOT ESTABLISHED in both families. That historical result is permanent and unchanged. This separate prospective study tests an explicitly defined policy; it does not repair, relabel or re-score the earlier result.

## Question and diagnosis

The historical Explorer instruction prefers higher observed consequences but does not prescribe an aggregation rule over multiple outcomes. Its negative result therefore concerns the original contract. It does not establish failure under an explicit arithmetic-mean policy, and ambiguity alone does not establish the cause of the negative result.

Does explicitly specifying arithmetic mean change stateless Explorer proposals toward the registered mean target, compared with a contemporaneous original-instruction comparator?

## Unchanged authentic P2 contexts

Use the prior experiment's `Context` directly at P2. Each request independently reconstructs the exact original eight-event fixture: epoch 1001 starts at state 1, executes HOLD, RETREAT, ADVANCE, ADVANCE, RETREAT, RETREAT, ending at 0. Trusted `start_episode(1002,1)` resets 0→1 without events/receipts/Memory. CHANGED then alters only external state-1 HOLD consequence +1→−1. Execute two ordinary HOLD events, keeping state 1. Original six records and two new records remain authenticated and unchanged, no eviction.

Fresh fixture indices 1000..1095 provide source identities disjoint from the historical 0..143 without changing any inherited constructor, authority or projection. Those identities are private evaluator metadata, never model input.

| Arm | HOLD | RETREAT | ADVANCE | Unique arithmetic-mean target |
| --- | --- | --- | --- | --- |
| CONTROL | [+1,+1,+1] | [0,0] | [−1] | HOLD |
| CHANGED | [+1,−1,−1] | [0,0] | [−1] | RETREAT |

Every displayed list derives mechanically from authenticated Memory. Evaluator uses exact rational `sum(outcomes)/len(outcomes)` over those same lists: CONTROL +1/0/−1; CHANGED −1/3,0,−1. Stop before a measured request if its target ties or disagrees with the registered fixture. No handwritten means determine the score. The old +1 HOLD event remains true, retained and visible.

## Exact A and B contracts

A is byte-for-byte the unchanged historical instruction:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

B is exactly:

> Choose the allowed action with the highest arithmetic mean of its verified prior outcomes. For each action, compute the arithmetic mean using all verified outcomes shown for that action. Do not discard earlier outcomes and do not give extra weight to later outcomes. UNTRIED means no verified observation and has no arithmetic mean. If at least one action has verified outcomes, choose only among actions with verified outcomes. Reply with exactly one allowed action and no explanation.

No ties occur in registered P2 contexts. No precomputed means or tie-breaking instructions. A/B requests within arm/family/schedule differ only in system text: identical payload, model, options and seed.

## Projection, parser, model and authority

Unchanged Explorer payload contains only `state` and each opaque `action` with chronological `verified_outcomes`. No means, epochs, episode/change labels, summaries, current-best answer, regime, Map result or recommendations. All actions remain offered and tried; no UNTRIED appears. UNKNOWN semantics remain unchanged. No negative Memory record bans any action.

Unchanged strict opaque alias parser (including inherited outer-whitespace handling): one offered token only. JSON, explanations, canonical action names, multiple actions and unknown tokens remain invalid. No extraction, repair or retry.

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0; verify every full model blob before inference. Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1, num_predict 16. Stateless requests, no returned context, persistent chat or weight changes. No model Map/Recovery. Proposals never execute, create receipts or alter Memory. Native deterministic fixture behavior is preserved and recorded.

## Exact budget and counterbalancing

Exactly 96 real Explorer calls: two families × twelve schedules × two arms × A/B. O1 K1/K2/K3, O2 Q7/M4/Z2; j=0..11, mapping index j mod 6. Each of six complete mappings twice per family. Fresh seed 94001+j shared across CONTROL A/B and CHANGED A/B and corresponding families.

j ascends. Even j family order O1→O2, odd j O2→O1. Within family, CONTROL→CHANGED when `(floor(j/2)+family_index)` is even, reversed when odd. This period-four arm-order factor is separately counterbalanced from A/B parity. Within arm, A→B when `(j+family_index+arm_index)` is even, otherwise B→A. Family indices O1=0/O2=1, arm indices CONTROL=0/CHANGED=1.

The [96-entry schedule](../experiments/explorer_value_aggregation_contract_v0/schedule.json), exact request/prompt hashes and scientific files are committed before inference. No output-dependent order, new seed, replacement, retry or extension.

## Frozen independent family criterion

EXPLICIT-MEAN EXPLORER POLICY SUPPORTED iff all ten:

1. All 24 B calls in that family complete.
2. B validity ≥23/24 across CONTROL+CHANGED.
3. CONTROL B HOLD ≥10/12.
4. CHANGED B RETREAT ≥10/12.
5. Matched CHANGED A≠RETREAT, B=RETREAT ≥8/12.
6. Reverse CHANGED A=RETREAT, B≠RETREAT ≤1/12.
7. Histories authentic.
8. Old and new records unchanged.
9. Model/sampler/parser integrity passes.
10. Exact replay passes.

Both families independently supported → **EXPLICIT-MEAN EXPLORER POLICY REPLICATED**; otherwise **EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**. No pooling or weakening. Full 96-call completion and replay are required to finalize the campaign.

Invalid output never equals a target selection. Under the stated A≠target/B=target rule, invalid A with correct B counts favorable; correct A with invalid B counts reverse. Invalids remain explicitly marked, never converted into actions. Also report favorable/reverse counts restricted to both-valid pairs as sensitivity analysis; do not substitute those counts for the frozen primary rule.

A is a fresh contemporaneous comparator, with no separate success threshold or requirement to reproduce historical counts. Report all A/B action and invalid counts separately for both arms/families. Primary pairing is CHANGED A/B. CONTROL pairs are descriptive, using their mechanically derived HOLD target.

Output sensitivity for every pair: same valid action, HOLD→RETREAT, ADVANCE→RETREAT, RETREAT→HOLD, RETREAT→ADVANCE, or other. Pairs containing invalids are separately identified within other (`invalid_in_pair`), never described as action transitions. Record each mapping/seed and parsed pair.

## Preflight, durable evidence and replay

Before inference construct all 96 actual P2 fixtures with network forbidden; authenticate full Memory→pair→package→original receipt→external execution bindings, state/epoch, zero-event reset, source lifetime, old/new history, no eviction, and exact unique mean targets. Verify all 48 A/B request pairs differ only in system text and freeze the annex. Stop on any inconsistent/tied target or failed provenance.

Durable fsynced intent before send; raw response before parse; parsed score before next call. Unique IDs and fixed reservation prevent duplicate/ambiguous reissue. Transport ambiguity stops the campaign with no automatic repeat. Raw private evidence remains outside the public tree.

Replay all 96 saved responses with sockets forbidden, reconstructing genuine fixtures, projections, instructions, exact requests, strict parses, arithmetic means, pair classes and decisions. Require eight files and 96 snapshots byte-identical and finalized live/replay results equal. Independently verify arithmetic and pair counts. Preserve provisional raw metrics; final replay gate is only set after executed replay.

## Preservation, claim and stop

Preserve Explorer NOT ESTABLISHED in both families; Map REPLICATED; historical Explorer transfer SUPPORTED; history depth SUPPORTED; feasibility and initialization A; ablation SUPPORTED; R1 A; all grounding/contradiction/UNKNOWN/representation checkpoints, main and tags. Verify with zero-inference replay, file/ref and archive checks; no unrelated live reruns. Nothing pushed.

A positive result supports execution of an explicitly instructed mean policy in this bounded fixture. It does not show that means are naturally inferred, universally correct, or the sole explanation of the old negative result. No claims of spontaneous adaptation, persistent policy learning, RL, internal belief revision, AGI or RSI.

Produce the requested 31-part report and compact evidence, then STOP after 96 calls, replay and preservation. No historical re-scoring, full composition, recency rule, added negative observations or follow-up campaign.
