# Map positive-evidence depth v0 — prospective registration

Parent: `bf26f6a65ac844676e6c35da2a4ed782b71de8f7`; grounded root
`79921b1da735e1495dffb695c00d7e7a21a234a6`; mechanical reference
`004ec5a6952d6b1c2c793eabe7200215611ea7b0`.

Exactly eight real Map calls. No Explorer, model Recovery, prompt or architecture
change, additional arm, retry, replacement, seed extension or tuning. Every
trial starts independently at state 1, epoch 1001, empty Memory. Target HOLD
self-loops to state 1 with consequence +1 in the existing stationary external
world. D1 and D2 below denote depths, not the earlier changed-world D1 fixture.

D1 acquires one ordinary HOLD execution/receipt/publication; D2 acquires two
separate ordinary HOLD executions with separate original receipts and identities.
The model receives the unchanged authenticated, epoch-visible exact-pair
projection: state, target alias and chronological epoch/transaction/alias/
next_state/consequence records only. No hand-written or duplicated history.
Depth is the only paired input difference (the second genuine record necessarily
adds its chronological transaction identity). Source identities are independent
and are not model-visible. Both latest observed consequences and current truth
are +1. No depth label, hint or confidence field enters a request.

| Index | Alias block | Seed | Condition | HOLD alias |
|---:|---|---:|---|---|
| 0 | O1 mapping 0 | 98001 | D1 | K2 |
| 1 | O1 mapping 0 | 98001 | D2 | K2 |
| 2 | O2 mapping 0 | 98001 | D2 | M4 |
| 3 | O2 mapping 0 | 98001 | D1 | M4 |
| 4 | O2 mapping 0 | 98002 | D1 | M4 |
| 5 | O2 mapping 0 | 98002 | D2 | M4 |
| 6 | O1 mapping 0 | 98002 | D2 | K2 |
| 7 | O1 mapping 0 | 98002 | D1 | K2 |

Model and transport remain `dolphin-mixtral:latest`, Ollama 0.1.16, Q4_0,
47B; manifest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`,
weights `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Sampler: temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1, registered seed. Stateless requests, unchanged template;
no constrained decoding. Exact established system instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

The existing strict Map parser is unchanged. Prediction is parsed, supplied
through the existing MapProposalAdapter and latched by the unchanged framework
before the scored HOLD executes. Score next_state, consequence and exact pair
against the newly issued original receipt; audit actual execution, receipt,
Measure, ordinary authorization and Memory publication. No declared-law or
aggregate-history score substitutes for the receipt. Prediction mismatch is not
an integrity failure; correct realized evidence may still publish normally.

An invalid response remains invalid and scores incorrect. No repaired/fallback
prediction is latched, and its scored event is not executed. Continue the other
registered calls, but a missing valid latch/receipt requires C. Transport failure
or an ambiguous interrupted intent stops the campaign without automatic reissue;
no response is invented to reach eight. B requires a completed, valid,
receipt-scored eight-call set with integrity/replay passing; invalid or missing
requirements are conservatively C under the user's missing-requirement rule.

Four consequence transitions: 0→+1, +1→+1, 0→0, +1→0; all others or invalid
are separately labeled. Also preserve both complete finite predictions and their
next_state/consequence/exact scores. Pair improvement means D1 valid but not
exact and D2 exact; regression means D1 exact and D2 valid but not exact.

**A — POSITIVE-EVIDENCE DEPTH SENSITIVITY OBSERVED** iff all eight calls complete
and are valid, D2 exact ≥3/4, improvements ≥2/4, regressions 0/4, every scored
receipt authentic and post-prediction, integrity passes and exact replay passes.

**B — NO DEPTH RESCUE OBSERVED** iff D2 exact ≤1/4 with the completed
receipt-scored set and integrity/replay otherwise passing.

**C — NOT ESTABLISHED** for intermediate/mixed outcomes or missing requirements.
Strong D1 and D2 must be reported as non-reproduction of historical W1
underprediction in this fresh small sample, not forced into a depth-effect claim.

Before inference: verify requests against authenticated history and absence of
future execution; change only the hidden next HOLD consequence in throwaway
canaries and require unchanged exact request bytes. Execute the canary only after
a synthetic latched prediction to verify its changed real receipt and publication.
Canaries, synthetic software controls and replay use zero inference and are
separately labeled. They are not experimental arms or extra model calls.

Use the established fsync write-ahead journal, immutable per-call IDs, exclusive
writer and one live reservation. Persist intent before dispatch; persist raw
response before parse; persist latch before execution and original receipt
before Measure/publication. Replay the eight retained responses through fresh
grounded histories and post-latch executions with network blocked. Require
byte-identical deterministic records and snapshots.

The inherited manifest/firewall and every parent tracked file are frozen by hash.
Old grounded/mechanical/forensic, temporal, Explorer, stale-Memory and authority
results remain unchanged. This new study may claim receipt-scored one-step
forecast counts only after demonstrating its actual execution chain. It does
not upgrade the historical detached decomposition into receipt-grounded evidence.

If A, the narrow permitted statement is: “Repeated authenticated positive
evidence changed Map behavior in this small W1 HOLD feasibility contrast.”
No general sufficiency, probability learning, confidence estimation, sole-cause,
general world-modeling or closed-loop improvement claim. Eight calls are a
feasibility diagnostic, not statistical evidence of a general mechanism.

Freeze this document, code and exact authenticated request hashes in Git before
inference. After eight calls, replay and report, stop. No push or main/tag change.
