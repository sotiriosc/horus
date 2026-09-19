# Composition empty-history schema contract v0 — prospective protocol

Parent `28b8736`, forensic specification-gap A finding; composition-v1 `0dcc5d8`
remains C and its nine malformed Map responses remain malformed. Preserve all
historical sources/results, absence-marker invariant, authority, main and tags.
No push. Freeze this protocol before inference. Do not rerun composition.

## Exact question and single intervention

Does communicating the existing output type/domain contract improve Map schema
compliance under the same nine empty-history contexts? Only system instruction
changes. No prediction-accuracy, learning, Recovery, Explorer or execution test.

Condition A, exact bytes (one line):

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Condition B, exact bytes (one line):

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

No other prompt bytes change. No examples, schemas or domain lists in the user
payload; no parser relaxation, constrained decoding, repair or coercion.

## Fixed contexts, pairing and budget

Extract the nine reached Map requests in chronological archived call order from
composition-v1. Context indices i=0..8 correspond to original episodes
0,2,4,5,7,8,9,10,11. Exclude the three episodes that never reached Map.
Preserve exact recorded user-payload bytes, admitted action, state 0, family,
mapping, target, empty history, original Map seed, model/options and serialization.

For even i use A then B; for odd i B then A. A/B share that context's registered
seed. O1 has four pairs; O2 five. Exactly 18 real calls, no replacement, retry,
additional seed or extension. A is rerun contemporaneously; historical responses
are separate evidence, not substituted for A. A transport/infrastructure failure
stops the campaign with incomplete-call classification; no retry to fill the budget.

dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0. Verify frozen manifest and
full weights before inference: manifest SHA256
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`, weights SHA256
`bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Sampler: temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1. Stateless requests with no returned context or chat carryover.

## Parser and absence invariant

Reuse `experiments.model_map_proposal_v0.adapter.parse` without edits. One JSON
object, exactly next_state/consequence, exact integer types (not bool, float,
numeric string or null), next_state 0..3, consequence -1/0/1, no duplicate keys
or trailing prose/object. Evaluate original raw text only.

Reconstruct each payload from zero original authorized Memory records using the
frozen renderer and require exact archived bytes. [] is a current view, never a
stored observation. No framework event executes and no Memory/package/receipt is
created. Verify no placeholder event or UNTRIED record is introduced. No fake prior,
dummy zero, pseudo-receipt or actual-world answer is available to this experiment.

## Frozen primary decision

SCHEMA-CONTRACT EFFECT SUPPORTED iff all eight conditions hold:

1. B valid >=8/9.
2. At least 7/9 pairs are A invalid → B valid.
3. A valid → B invalid pairs <=1/9.
4. Both O1 and O2 have improved or equal compliance under B.
5. All 18 registered calls complete.
6. Parser unchanged.
7. Paired user payloads byte-identical.
8. Model/config/seed matching passes.

Otherwise SCHEMA-CONTRACT EFFECT NOT ESTABLISHED. Never alter thresholds afterward.
Independently report original-contract replication: the historical **all-nine
schema-failure pattern** is observed only if all nine new A responses are invalid;
otherwise that full pattern is not observed, with exact/partial counts retained.
Historical raw-string equality is descriptive only, never a support criterion.
Report explicit B compliance as counts separately from both decisions.

## Fixed descriptive extraction

Per condition: valid, JSON-decodable, exact-key, exact-integer next_state and
consequence, each finite-domain count, bare opaque consequence token, prose-string
consequence, numeric string, bool/float/null, extras/missing/duplicate fields,
multiple objects and outside prose. Domain compliance requires exact integer type;
Python bool must not count as an in-domain integer. Embedded token mentions are
separate from bare-token consequence values. Show every A/B pair and O1/O2 counts.
Do not score the resulting integer values against the world or infer mechanisms.

## Evidence, replay and preservation

Privately retain the frozen 18-entry request schedule and each exact request/raw
response, context identity, system/user text, metadata, original-parser result and
failure categories. Flush responses before the next request. Replaying all recorded
responses must produce byte-identical calls, diagnostics and compact results with
zero inference. Register input/source hashes before the first call.

Afterward run only focused zero-inference preservation replays: composition-v1,
forensic diagnosis-v0, input-bindings-v1, Map-v0 and established-prior Map-v1.
Check inherited source/result bytes and refs. Produce all 27 requested report
sections. Stop after 18 calls/replay/preservation; do not implement or start
composition-v2, adjust Explorer, change authority or introduce more examples.
