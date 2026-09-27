# Zakhor durable-memory trial v0 — results

Status: **COMPLETE**. Decision gate: **MODERN_MEMORY_SUFFICIENT**.

The experiment completed exactly 48 model calls and 24 protected external
executions. No call, event, or inference was retried. M and Z selected identical
memory identities and produced identical predictions on all 24 opportunities.
Zakhor's persistent regime index changed internal retrieval labels on 23
opportunities but did not change the selected evidence, model context, or
behavior.

The preregistered runner encountered a reporting-only duplicate-keyword exception
after the final call and final protected checkpoint. Two further reporting audits
corrected the prior-evidence denominator and a vacuous recency count. These
zero-inference recoveries are documented in `reporting-amendment.md`; v3 is the
authoritative analysis. Raw evidence was not changed and the campaign was not
rerun.

## Protected harness verification

The zero-inference gate passed before behavioral work:

- the original `RealizedEventReceipt` object was retained by protected
  publication;
- an equal-valued substituted receipt was rejected without Memory mutation;
- a failed external execution created neither a receipt nor Memory;
- unauthorized evidence was rejected by the durable-store admission boundary;
- a fresh reopen reconciled only authenticated `SessionStore` events;
- event, call, and scoring chains replayed.

The campaign used the existing `ExternalExecutionBoundary`,
`StatusBoundFramework`, and `SessionStore`. Final replay verified 24 authenticated
events, 144 call-chain records for 48 calls, 24 receipt-bound score records, no
retry identities, exact analysis reproduction, and the fresh-process restart
hash match.

## Durable store

The common SQLite store contains append-only `events`, persistent
`zakhor_state`, persistent `zakhor_regimes`, schema metadata, and a relation/order
index. Each event retains chronological order, receipt/source/event/epoch/
transaction identity, state and relation, action, realized consequence and next
state, receipt provenance hash, authorization identity/status, context identity,
and authenticated event-stream sequence/head. All 24 observations remain
separate; contradictory values were never overwritten.

M and Z read the same `events` table. Only an already authenticated current
publication can call `record`. Restore reconciles every database row against the
authenticated event chain before retrieval.

## Retrieval rules

**M — modern baseline:** exact relation lookup; four most recent records; newest
anchor for any missing consequence; recency fill to six; chronological prompt
order.

**Z — Zakhor memory:** the same six-record bound plus a durable regime index. A
different outcome is retained as a stranger; three consecutive equal strangers
confirm regime rebirth. Retrieval prioritizes unassimilated strangers, recent
active-regime evidence, prior-regime anchors, then recency fill.

Activation keeper hooks were excluded because they would confound retrieval with
model computation.

## Schedule and budget

- Events 1–6: stable state-1 HOLD, consequence +1.
- Events 7–12: changed HOLD, consequence −1.
- Fresh-process restart after event 12.
- Events 13–16: continued changed HOLD, consequence −1.
- Events 17–24: restored HOLD, consequence +1.
- Exactly two calls per event, M and Z: **48 total**.

Protected runtimes were prospectively segmented at events 1, 7, 13, and 17 and
stayed below the episode bound.

## Behavioral and retrieval results

| Metric | M | Z |
|---|---:|---:|
| Consequence accuracy | 14/24 (58.3%) | 14/24 (58.3%) |
| Invalid outputs | 0 | 0 |
| Change adaptation latency | Not observed | Not observed |
| Old-regime false persistence | 10/10 | 10/10 |
| Restoration latency | 0 | 0 |
| Changed-regime false persistence after restoration | 0 | 0 |
| Contradictions preserved | 17/17 | 17/17 |
| Relevant-history retrieval | 92.6% | 92.6% |
| Stale selected records | 38.2% | 38.2% |
| Most recent prior event retrieved | 23/23 | 23/23 |
| Current-phase evidence visible when available | 21/21 | 21/21 |
| Context tokens, total / mean / max | 3948 / 164.5 / 189 | 3948 / 164.5 / 189 |

Both conditions predicted +1 on every opportunity. They were correct throughout
the initial stable period, wrong throughout all ten changed-regime events, and
immediately correct at restoration because their prediction had never revised.
The zero restoration latency therefore does not demonstrate learned switchback.

M and Z selected the exact same memory identities 24/24 times. Their retrieval
reason labels differed 23/24 times because Z named active regimes, stranger
candidates, and prior-regime anchors, while M named recency and contradiction
anchors. Those labels did not alter the retrieved set. Predictions were identical
24/24.

## Endurance

| Window | M accuracy | Z accuracy | Relevant retrieval | Stale selection |
|---|---:|---:|---:|---:|
| Early, events 1–8 | 75.0% | 75.0% | 100% | 40.7% |
| Middle, events 9–16 | 0.0% | 0.0% | 89.5% | 29.2% |
| Late, events 17–24 | 100% | 100% | 92.6% | 45.8% |
| Worst rolling 6, starts event 7 | 0.0% | 0.0% | 100% | 58.3% |

Context reached the six-record bound and 189 tokens in the middle and late
windows. No context-size or retrieval drift separated the conditions. Both
preserved contradictions, but neither induced the model to revise during the
changed regime even when relevant evidence dominated the selected set.

## Error audit

Both conditions had the same ten errors:

| Cause | Count |
|---|---:|
| `CORRECT_MEMORY_RETRIEVED_MODEL_WRONG` | 6 |
| `STALE_MEMORY_OVERWEIGHTED` | 3 |
| `RETRIEVAL_AMBIGUOUS` | 1 |
| `RELEVANT_MEMORY_NOT_RETRIEVED` | 0 |
| `CONTRADICTORY_MEMORY_LOST` | 0 |

The first changed event had no prior changed-regime evidence and was ambiguous.
The next three errors had more stale than relevant selected evidence. For the
remaining six errors, current-regime evidence outweighed stale evidence but the
model still predicted the old value. This separates the main observed failure
from durable storage: the right evidence was present, yet the frozen model did
not use it behaviorally.

No `MEMORY_CORRECT_NO_BEHAVIORAL_EFFECT` event is assigned as an error cause.
At the paired-system level, however, Zakhor's different organizational labels
had no behavioral effect because they resolved to the same identities as M.

## Restart

Before process exit, hashes covered the SQLite file/logical event store, M policy,
Z state/index, authority key, protected checkpoint, and event/call/scoring files.
The fresh Stage-2 process reproduced every hash exactly before creating a new
runtime. It reconciled all 12 authenticated prior events. The first post-restart
retrieval selected the same six identities in M and Z; both predicted +1 and were
wrong against the still-active −1 regime. Durable recovery succeeded; behavioral
adaptation did not.

## Overhead

| Timing | M | Z |
|---|---:|---:|
| Retrieval total | 3.620 ms | 4.584 ms |
| Retrieval mean | 0.151 ms | 0.191 ms |
| Retrieval maximum | 0.244 ms | 0.361 ms |
| Model time total | 1.911 s | 1.102 s |

Z added about 0.964 ms total retrieval work plus two persistent index tables.
The apparent model-time advantage is not attributed to memory: calls shared one
model per process and alternated order, so load/warmup and system timing dominate
this short run. Context size was identical.

## Decision

**MODERN_MEMORY_SUFFICIENT.** The ordinary baseline supplied every useful
property observed here—durability, exact restart, recency, contradiction
preservation, relevant evidence, bounded context, and identical behavioral
results—with less retrieval machinery. The three-observation Zakhor regime
rebirth index is the smallest tested Zakhor mechanism, but it produced no useful
selection or behavioral distinction in this workload.

This result does not show that all possible durable Zakhor-style memory is
useless. It shows that the specific minimal, predeclared regime/stranger adapter
did not improve on a strong ordinary retrieval policy. It also shows that merely
making memory durable did not repair the frozen model's failure to revise during
the changed regime.

## Limitations

- One relation, one model artifact, one deterministic 24-event schedule, and no
  statistical replication limit generalization.
- M and Z converged to identical selected sets; this workload did not force a
  capacity conflict where their organization would select different evidence.
- The model predicted +1 throughout, limiting the ability to compare adaptation
  once retrieval differed.
- Phase relevance is evaluator-only and was never exposed to either condition.
- Model timing is confounded by shared-process call order and warmup.
- The post-campaign analyzer required documented zero-inference recovery. Raw
  inference and protected evidence completed before the reporting exception.
- No Horus adaptive machinery was used, and no follow-on or scale-up was started.
