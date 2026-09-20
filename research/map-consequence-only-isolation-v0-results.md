# Map consequence-only isolation v0 — results

**A — JOINT-OUTPUT COUPLING EFFECT OBSERVED.** Exactly eight real calls completed
and were valid. Joint-output J predicted consequence +1 in **0/4** cases;
consequence-only C did so in **4/4**. All four pairs improved 0→+1, with zero
regressions. Matching, authentic histories, post-response original receipts,
future-answer canaries, detachment, integrity and exact replay all passed.

> Removing the requirement to jointly predict next_state changed consequence
> forecasts for the registered positive self-loop case.

This is the registered small prompt/output-decomposition contrast. It does not
identify an internal mechanism, establish interference as its cause, or justify
a production split without a separate architectural study.

## Registration and evidence

The [preregistration](map-consequence-only-isolation-v0-preregistration.md),
code, exact instructions, counterbalanced schedule and authenticated-request
hashes were committed before inference as
`3f8a9535f568b235f4ea99d56e8711cee52c5c00`.
Parent: `543b4c550bdff461c88dbc77ac976df15483a8a6`.

[Compact results](../experiments/map_consequence_only_isolation_v0/results.json)
retain all raw and parsed responses, per-call receipt scores, all four paired
comparisons, authentic visible histories, original setup and scored receipts,
actual executions, non-model control predictions, Measure counts, authorizations,
Memory publications and source-record hashes.
[Verification](../experiments/map_consequence_only_isolation_v0/verification.json)
records controls, model hashes, replay evidence hashes and preservation checks.
[Replay instructions](../experiments/map_consequence_only_isolation_v0/README.md)
use the retained private raw archive; compact public evidence alone is not the
full replay archive.

## All eight calls

All trials had current state 1 and exactly one authentic HOLD history outcome
(1,+1). Every new scored original receipt was also (1,+1). Call numbers are
one-based; the machine-readable index is zero-based.

| Call | Block | Seed | Arm | Raw JSON response | Consequence correct | next_state correct | Joint exact |
|---:|---|---:|---|---|---|---|---|
| 1 | O1 | 99101 | J | `{"next_state":1,"consequence":0}` | no | yes | no |
| 2 | O1 | 99101 | C | `{"consequence":1}` | yes | n/a | n/a |
| 3 | O2 | 99101 | C | `{"consequence":1}` | yes | n/a | n/a |
| 4 | O2 | 99101 | J | `{"next_state":1,"consequence":0}` | no | yes | no |
| 5 | O2 | 99102 | J | `{"next_state":1,"consequence":0}` | no | yes | no |
| 6 | O2 | 99102 | C | `{"consequence":1}` | yes | n/a | n/a |
| 7 | O1 | 99102 | C | `{"consequence":1}` | yes | n/a | n/a |
| 8 | O1 | 99102 | J | `{"next_state":1,"consequence":0}` | no | yes | no |

The table displays JSON values compactly; `results.json` preserves exact raw
response strings, including whitespace. J next_state accuracy was independently
**4/4**, and joint exactness **0/4**. C has no next_state or joint exactness score;
no missing next_state was inferred or manufactured.

| Pair | J consequence | C consequence | Transition | Improvement | Regression |
|---|---:|---:|---|---|---|
| O1 / 99101 | 0 | +1 | 0→+1 | yes | no |
| O1 / 99102 | 0 | +1 | 0→+1 | yes | no |
| O2 / 99101 | 0 | +1 | 0→+1 | yes | no |
| O2 / 99102 | 0 | +1 | 0→+1 | yes | no |

There were zero 0→0, +1→+1, +1→0 or other/invalid pairs. The joint-arm neutral
forecast error reproduced in all four registered positive self-loop cases.

## Scientific matching and separation from authority

Each trial began independently with empty Memory, state 1 and epoch 1001. One
genuine setup HOLD produced an original receipt that published through the
ordinary Measure/authorization/Memory path. Its visible identity was epoch 1001,
transaction 1; surface HOLD alias K2 in O1 or M4 in O2. No moving fixture,
handwritten history or navigation event was used.

All four pairs had byte-identical task data. Replacing only C's `system` value
with J's instruction made complete request bytes identical. State, alias,
authenticated history, row order/depth, historical next_state/consequence,
epoch/transaction, model, seed, sampler and envelope matched. Both arms retained
num_predict=32. Only the exact user-specified system instructions differed.

Neither probe output entered the framework's Prediction object or had proposal,
publication or authorization capability. Ordinary unchanged `MapModel` supplied
the same registered **non-model (1,+1)** control in all eight trials. Its full
identity was epoch 1001, transaction 2, pre-state 1, action HOLD. No model adapter
was installed and no production prompt was replaced. The control prediction was
not included in model input; the authentic history necessarily shared its finite
outcome values.

After each response and parse were durably recorded, the ordinary control was
latched and a new HOLD executed. The original post-response receipt, not the
control prediction, was the diagnostic scoring target. Every scored event invoked
Measure once and obtained committed, continued `AUTHORIZED` publication of its
actual outcome. Framework measurement_matches was **true in 8/8** because it
compared the non-model control to reality. That is separate from probe correctness
(J 0/4, C 4/4), and was never used to award model credit.

There were eight genuine setup executions and eight scored executions: **16
unique original live receipts and 16 Memory publications**. Old observations
remained unchanged. There were zero native state Recovery authorizations in setup
or scoring, zero model Recovery calls and zero Explorer calls.

## Executed validation

Before inference, eight throwaway canaries changed only the hidden next HOLD
consequence to −1 after authentic +1 setup. Both J and C requests remained
byte-identical to their unmodified versions. Subsequent original receipts and
Memory contained −1, while old +1 history remained intact. These used zero model
calls and are not extra behavioral arms.

Eight synthetic detachment variants covered J/C finite consequences −1,0,+1,
wrong J next_state and invalid outputs. Holding the fixture fixed produced
identical grounded control, execution, receipt, authorization and Memory records
for every variant. Invalid probes gained no authority or substitute prediction.
Additional checks passed: eleven existing J-parser rejections, twenty strict
C-parser rejections, all three valid C integers, extra request-field mismatch
rejection, twelve classification controls and two durability controls. Eight
synthetic campaign responses also reproduced under exact synthetic replay.

For the real campaign, all 72 hash-chained journal records passed integrity and
ordering checks: intent → response → parse → non-model control latch → execution
intent → original receipt → Measure/publication. Original object identity and
full provenance binding were verified during execution and replay. Serialized
receipt equality alone is not treated as an object-identity attestation.

Exactly eight server generation requests matched eight recorded responses. No
retry, repair, replacement or extra call occurred; the owned server was stopped.
Network-blocked real-response replay issued **zero model calls** and reproduced
seven data files, eight snapshots and the empty writer-lock file byte for byte
(**16 files**). Raw live and replay metrics retain provisional C /
`AWAITING_EXACT_REPLAY`; final public A was computed only after replay passed.

Total simulated execution accounting: 8 registration setup + 64 preflight/control
+ 16 live + 16 replay = **104**. Only the eight live calls are real-model
behavioral evidence. Model blobs were verified against the registered hashes.

## Frozen decision, preservation and limits

All A gates passed: 8/8 complete and valid; J positive 0/4 ≤1/4; C positive
4/4 ≥3/4; four improving pairs ≥2; zero regressions; authentic histories and
post-response score receipts; matching; leak controls; integrity; exact replay.
The final classification was independently recomputed from consequence results.
No threshold, instruction, protocol or decision rule changed after inference.

This small result supports considering a separate study of next-state and
consequence prediction. It does not implement or validate a production split.
The exact supplied instruction changes both requested target wording and output
schema; the observed contrast cannot identify hidden computation separately from
those instruction effects. It covers one model configuration, two alias blocks,
two paired seeds and a single registered W1/self-loop relation in an external
software simulator, not a physical device or general end-to-end deployment.

**W0 ADVANCE and W3 RETREAT are moving +1 relations that also produced errors.**
This result does not explain those failures or all positive underprediction.

All **718 parent tracked files**, including executable modes, remain unchanged:
grounded baseline A and its claim firewall, mechanical A, ranking forensics,
positive-depth **B — NO DEPTH RESCUE OBSERVED**, self-loop coupling **A**, temporal
Map and Explorer negatives, stale-Memory results and authority history. Detached
probe scores here do not upgrade historical scores or establish protected model
proposal integration.

The authorized eight-call campaign is complete and stopped. No split Map,
production architecture change, new production prompt, tuning, extra arms,
seeds, mappings or extension. No push, main-branch modification or tag change.
