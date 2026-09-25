# Cross-episode stale-Memory Explorer revision v1 — preregistration

Parent: `82e04f31a8a532547e4a1858ef22643dd1986843`, Map revision REPLICATED. One prospective Explorer-only campaign. All earlier results, architecture, main and tags are preserved. No push.

## Question and fixture

Does a stateless Explorer move from previously favored HOLD toward RETREAT when authentic new-episode HOLD outcomes contradict retained true older history, relative to matched stationary CONTROL?

Every measured context is reconstructed independently using the existing authority path and trusted initialization. Start at state 1, epoch 1001. Execute exactly:

| Transaction | Action | Transition | Consequence |
| --- | --- | --- | --- |
| 1 | HOLD | 1→1 | +1 |
| 2 | RETREAT | 1→0 | 0 |
| 3 | ADVANCE | 0→1 | +1 |
| 4 | ADVANCE | 1→2 | −1 |
| 5 | RETREAT | 2→1 | +1 |
| 6 | RETREAT | 1→0 | 0 |

Navigation remains in full protected Memory. Trusted `start_episode(1002,1)` resets external and authorized current state 0→1 with no event, receipt or Memory entry. Preserve original receipt/package identity and source lifetime. Capture P0, then alter CHANGED's external state-1 HOLD consequence +1→−1 before any episode-2 event or measured request. No other relation changes; HOLD still self-loops. CONTROL stays stationary.

P1 executes one ordinary HOLD; P2 executes a second. The measured current state is always 1, epoch 1002. Memory lengths are 6/7/8 with no eviction or capacity increase. All data come from external execution→authentic receipt→Measure→ordinary authorization→Memory publication. No prompt-history injection or measured proposal execution.

| Stage | CONTROL HOLD | CHANGED HOLD | RETREAT, both | ADVANCE, both |
| --- | --- | --- | --- | --- |
| P0 | [+1] | [+1] | [0,0] | [−1] |
| P1 | [+1,+1] | [+1,−1] | [0,0] | [−1] |
| P2 | [+1,+1,+1] | [+1,−1,−1] | [0,0] | [−1] |

Old observations remain authentic, unchanged and present. All actions remain offered. No negative consequence bans an action. UNKNOWN means zero retained matching observations; all three actions are tried here. Any UNTRIED rendering fails the fixture audit.

## Model contract

Use the exact unchanged system instruction:

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

Unchanged generalized Explorer projection: `state` and `actions`, with each row containing only opaque `action` and chronologically ordered `verified_outcomes`. No epoch labels, stale/regime flags, averages, rankings, recency guidance, predictions, Recovery metadata or hidden current-best answer.

Unchanged strict opaque parser accepts one offered alias (with its inherited outer whitespace handling). Reject canonical names, JSON, multiple actions, explanation and unknown tokens. No extraction, repair, coercion or retry. Invalids stay in all denominators.

Pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0. Verify complete manifest blobs before inference. Inherited Explorer options: temperature .2, top_p .9, top_k 40, num_predict 16, num_ctx 2048, repeat_penalty 1.1. No weights or returned context reuse; no persistent chat. Measured actions do not execute, mutate history, latch state or influence later samples. Zero model Map/Recovery calls; deterministic fixture components only.

## Exact schedule

144 real calls = two families × two arms × three stages × twelve schedules. O1 K1/K2/K3; O2 Q7/M4/Z2. All six complete mappings, twice each per family. j=0..11, mapping index j mod 6, seed 93001+j shared across six matched arm/stage requests and corresponding families.

j ascends. Even j: O1 then O2; odd j: O2 then O1. Within family P0→P1→P2. Even (j+family_index+stage_index): CONTROL then CHANGED; odd reverses. Family/stage indices are zero-based. The [144-entry annex](../experiments/cross_episode_stale_memory_explorer_revision_v1/schedule.json) freezes descriptors and exact request/prompt SHA-256 values. P0 request pairs are byte-identical. No extra seed, retry, replacement, extension or adaptive ordering.

## Mandatory zero-call preflight

Before inference require all seventeen: exact six-event sequence; authentic original receipts; episode 1 ends at 0; genuine reset 0→1; zero reset events; identical P0 histories; all three actions tried; no UNTRIED; exact P1; exact P2; current state 1 throughout probes; P2 Memory eight; no eviction; old records unchanged; authentic negative receipts normally authorized; no forbidden labels; exact 144-request annex freezeable. Failure means STOP WITH ZERO MODEL CALLS, no automatic patch. Native Measure/Recovery is observed, never forced or suppressed.

## Frozen decision

Each family is SUPPORTED iff all twelve gates pass:

1. CHANGED P0 HOLD ≥10/12.
2. CHANGED P2 RETREAT ≥9/12.
3. CONTROL P2 HOLD ≥9/12.
4. Matched P2 CONTROL=HOLD and CHANGED=RETREAT ≥8/12.
5. Reverse matched P2 CONTROL=RETREAT and CHANGED=HOLD ≤1/12.
6. All 144 registered calls complete.
7. At least 140/144 globally valid, and at least 11/12 valid in **each family × arm × stage cell**. This denominator resolves “family/stage” to each registered twelve-call cell; it does not pool arms. The full validity gate applies to both families.
8. All histories derive from authentic receipts.
9. Original episode-1 +1/0/−1 records remain present and unchanged.
10. Stage-appropriate new CHANGED HOLD −1 records remain present and unchanged.
11. Provenance/framework integrity passes.
12. Exact replay passes.

Both families independently supported → **CROSS-EPISODE STALE-MEMORY EXPLORER REVISION REPLICATED**. Otherwise **CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**. No pooling or threshold changes.

P1 is descriptive only: HOLD/RETREAT/ADVANCE/invalid counts. Do not introduce a P1 threshold. Report both arms' P0→P1→P2 paths for each family/mapping/seed; preserve invalids and reversals. Conditional behavioral latency includes only CHANGED schedules selecting HOLD at P0: first RETREAT at P1, else P2, else never. Others are excluded, never counted as latency successes. These trajectories join independent stateless requests, not persistent internal beliefs.

Secondary current-best is HOLD in CONTROL and RETREAT in CHANGED at every stage after the external change. P0 HOLD is the required old-preference prerequisite despite hidden current truth; do not call it irrational. Retain exact consequence lists. Optional evaluator means are +1/0/−1 at P0, HOLD 0 at CHANGED P1 and −1/3 at P2; never prompt means or claim the model averaged.

## Durability, replay and preservation

Durable intent before each send; raw response fsynced before parsing; parsed result fsynced before the next call. Unique call IDs and fixed campaign reservation prevent duplicate/ambiguous reissue. Stop on transport ambiguity; no automatic replacement. Full original private evidence stays outside the public tree.

Replay saved outputs with network forbidden, reconstructing actual authenticated fixtures and exact requests. Require eight output files and 144 snapshots byte-identical, plus independently checked parsing, counts, pairs, latency and final decisions. Raw pre-verification metrics remain unchanged; final results set replay passed only after successful verification.

Verify parent Map revision REPLICATED, feasibility A, depth SUPPORTED, historical transfer unchanged including Explorer SUPPORTED, initialization A, ablation SUPPORTED, R1 A, prior contradiction/grounding and representation/UNKNOWN checkpoints unchanged. No unrelated live rerun.

## Scope and stop

Report the required 38 sections, per-family gates and negative results. This tests stateless input→proposal behavior in a bounded fixture, not persistent learning, RL, policy learning, internal belief revision, general drift detection, weight learning, AGI or RSI. Source/registry and trusted simulation reset remain the authority boundary.

After 144 calls, replay and preservation, STOP. No composed adaptation, extra value sample, recency teaching, Memory/world enlargement or follow-up campaign.
