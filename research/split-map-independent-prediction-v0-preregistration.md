# Split Map independent prediction v0 — preregistration

## Question and boundary

Can Map preserve useful next-state forecasting while avoiding the consequence
underprediction seen in the joint response by producing next state and
consequence independently, freezing both, and reconciling them mechanically?

This is a bounded research implementation. It does not establish an internal
mechanism and does not modify production Map, Explorer, Recovery, Memory,
authorization, world behavior or the protected authority chain. It uses exactly
eleven retained failure contexts and 33 real Map attempts: 11 joint (J), 11
next-state-only (N), and 11 consequence-only (C). There are no retries,
replacements, votes, adaptive calls or prompt changes after registration.

## Frozen contexts

Descriptors are derived from the forensic and retained-evidence artifacts and
checked against their response, history, provenance and request hashes.

| Context | World/state | Family | Mapping | Alias/action | Seed | History tx2 | Historical J | Realized | Call order |
|---:|---|---|---:|---|---:|---|---|---|---|
| 2 | W0 / 0 | O2 | 1 | Q7 / ADVANCE | 96012 | (1,+1) | (1,0) | (1,+1) | J,N,C |
| 3 | W0 / 0 | O1 | 1 | K1 / ADVANCE | 96012 | (1,+1) | (1,0) | (1,+1) | N,C,J |
| 5 | W0 / 0 | O2 | 2 | M4 / ADVANCE | 96022 | (1,+1) | (1,0) | (1,+1) | C,J,N |
| 7 | W0 / 0 | O1 | 3 | K3 / ADVANCE | 96032 | (1,+1) | (1,0) | (1,+1) | J,C,N |
| 8 | W0 / 0 | O1 | 4 | K2 / ADVANCE | 96042 | (1,+1) | (1,0) | (1,+1) | N,J,C |
| 9 | W0 / 0 | O2 | 4 | M4 / ADVANCE | 96042 | (1,+1) | (1,0) | (1,+1) | C,N,J |
| 10 | W0 / 0 | O2 | 5 | Z2 / ADVANCE | 96052 | (1,+1) | (1,0) | (1,+1) | J,N,C |
| 27 | W3 / 3 | O1 | 1 | K2 / RETREAT | 96214 | (2,+1) | (1,−1) | (2,+1) | N,C,J |
| 30 | W3 / 3 | O2 | 3 | M4 / RETREAT | 96234 | (2,+1) | (1,−1) | (2,+1) | C,J,N |
| 32 | W3 / 3 | O1 | 4 | K1 / RETREAT | 96244 | (2,+1) | (0,−1) | (2,+1) | J,C,N |
| 33 | W3 / 3 | O2 | 4 | Q7 / RETREAT | 96244 | (2,+1) | (0,−1) | (2,+1) | N,J,C |

W0 reconstructs `HOLD, ADVANCE, RETREAT, RETREAT, ADVANCE`; W3 reconstructs
`HOLD, RETREAT, ADVANCE, ADVANCE, RETREAT`. The target observation is the
authenticated transaction 2 record. `schedule.json` freezes all context
descriptor hashes and all 33 exact request hashes before inference. Every J
request must reproduce its retained historical request hash.

## Frozen requests

Model: `dolphin-mixtral:latest`. Every request uses temperature 0.2, top-k 40,
top-p 0.9, repeat penalty 1.1, context 2048, `num_predict=32`, and the historical
seed above. Within a context all three roles receive the same serialized object,
containing exactly `state`, `target_action`, and
`VERIFIED_CHRONOLOGICAL_HISTORY`. The prompts and sampler bytes are identical;
only the system response schema differs.

J uses the existing exact joint instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

N uses the direct one-field projection of that instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: next_state must be an integer in {0,1,2,3}. Do not include any other fields or explanation.

C uses the existing exact consequence-only instruction from the immediately
preceding schema-transfer study:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Strict parsers require exactly the named fields and exact integers in the finite
domains. Invalid output consumes its attempt and is not repaired.

## Independence and reconciliation

All three request bodies are constructed before the first response. In
particular, C does not accept and must not contain the N output, a predicted
next state, reconciliation state, hidden future, declared world law or execution
result. N and C have distinct call IDs and durable intent, response and parse
records. Call order is counterbalanced with all six permutations used before a
repeat; order never changes request bytes.

Only after J, N and C have each completed and their parse results are durable,
the reconciler either constructs exactly
`{"next_state": N.next_state, "consequence": C.consequence}` or abstains if N
or C is invalid. It performs no inference, correction, retry, voting,
reinterpretation or hidden-law lookup. C cannot alter the already-frozen N
record, and N cannot alter C. Reconciliation precedes the grounded execution but
has no execution or publication capability.

Each context then follows:

`three durable detached predictions → mechanical reconciliation → ordinary non-model control → execution → new original receipt → Measure/authorization/Memory → score`.

## Frozen scoring

All accuracy denominators are 11. Invalid or abstained predictions count as not
correct.

- Historical joint consequence failure reproduced: new valid J consequence
  differs from the new receipt.
- Independent consequence repair: a reproduced J failure and valid C consequence
  equal to the receipt.
- J next-state, consequence and exact correctness are scored against the receipt.
- Split next-state is N correctness; split consequence is C correctness; split
  exact requires a valid reconciliation and both correct.
- Reconciliation error: the reconciled object differs from the two parsed frozen
  component values, or a component is manufactured when either is invalid.
- Consequence regression: J consequence is correct and C is invalid or wrong.
- Exact regression: J is exact and the split prediction is invalid or not exact.

For the original ranking implication, retain the two non-target historical
consequence forecasts and replace only the target forecast with the new J or C
consequence. Report whether this makes the retained actual true-best action the
unique predicted maximum. This is a descriptive counterfactual on the recorded
three-action ranking; no new Explorer call is made.

The interpretation rule is frozen. At most 5/11 reproduced J consequence
failures is insufficient reproducibility to evaluate Split Map. Above 5/11,
repair of every reproduced failure with zero exact regressions and zero
reconciliation errors is reported as positive on the reproduced failures.
Anything else is mixed evidence. Next-state accuracy, all regressions and the
ranking counts are always reported; no threshold is added after inference.

## Zero-inference controls and stopping

Before inference, preflight must verify all historical J hashes and 33 registered
hashes; strict J/N/C parsers; invariance of C request bytes under five synthetic
N outputs per context; absence of N output, shared mutable reconciliation state
and future execution fields from C; C inability to alter frozen N; durable parse
of both components before reconciliation; reconciliation before execution;
abstention for either invalid component; detached authority under future-event
canaries and output variations; ambiguous-call stopping; a 33-response synthetic
campaign; and byte-identical zero-network replay.

A transport ambiguity, durable-write failure, request mismatch or control
failure stops without reissue. After 33 attempts, stop. Exact replay must match
all deterministic archive files and snapshots. Publish compact results and
hashes only; retain full prompts, journal and transport records in the private
durable archive. Do not implement production Split Map or begin another study.
