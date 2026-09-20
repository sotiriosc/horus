# Composition empty-history schema contract v0 — results

**SCHEMA-CONTRACT EFFECT SUPPORTED**

Exactly 18 real calls; schema compliance only.

## 1. Parent identities

Parent forensic branch `research/composition-initial-map-schema-diagnosis-v0`,
commit `28b87365e1f768ef7bf176997126fbffe250e059`. New branch
`research/composition-empty-history-schema-contract-v0`. Preregistration frozen in
`0bee856b93c3ea6c352ca11aed234400c5a8eacc`; implementation frozen in
`c2e7d6a6429d6aed21aec05d5f434a796244af5b` before inference.
Recorded UTC timestamps are retained in verification; no public main/tag updates or push.

## 2. Preserved composition-v1 C

Composition-v1 `0dcc5d810f5b03ce2479d8f151e3603f85906500` remains
**C — NOT ESTABLISHED**. Its 21 real calls (12 Explorer, nine Map, zero Recovery),
three malformed Explorer proposals and nine malformed Map proposals remain
unchanged. All 12 original episodes stopped before execution. The old Map strings
are neither repaired nor reclassified as valid.

## 3. Forensic reference

The [forensic report](composition-initial-map-schema-diagnosis-v0-results.md)
remains **A — CONCRETE MODEL/PARSER SPECIFICATION GAP IDENTIFIED**, with
**EMPTY-HISTORY ASSOCIATION OBSERVED** and no causal attribution. This follow-up
intervenes on the visible system contract; it does not test history depth.

## 4. Exact question

When empty history removes implicit numeric examples, does explicitly telling
the model the parser's existing type/domain contract restore schema compliance
in the same nine reached contexts? This is a bounded interface-specification test.

## 5. Nine reused contexts

| Context | Original episode | Family/mapping | State | Target | Admitted action | Seed |
|---|---|---|---|---|---|---|
| 0 | 0 | O1/0 | 0 | K1 | ADVANCE | 80003 |
| 1 | 2 | O1/2 | 0 | K1 | HOLD | 80005 |
| 2 | 4 | O1/4 | 0 | K1 | RETREAT | 80007 |
| 3 | 5 | O1/5 | 0 | K1 | RETREAT | 80008 |
| 4 | 7 | O2/1 | 0 | Q7 | ADVANCE | 80004 |
| 5 | 8 | O2/2 | 0 | Q7 | HOLD | 80005 |
| 6 | 9 | O2/3 | 0 | M4 | RETREAT | 80006 |
| 7 | 10 | O2/4 | 0 | Q7 | RETREAT | 80007 |
| 8 | 11 | O2/5 | 0 | Q7 | RETREAT | 80008 |

Only the nine original reached Map calls are included. Original episodes 1, 3 and 6 never admitted an Explorer action and are excluded. Full bijections and payload digests are in compact results.

## 6. Conditions A/B

Condition A (exact one-line system text):

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Condition B (exact one-line system text):

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

## 7. Exact prompt difference

B replaces “containing next_state and consequence, and no explanation” with an
exclusive two-field contract, exact integer requirements, and both finite domains.
The exact strings above were frozen prospectively. Nothing else model-visible was
changed. This tests the bundled specification change, not individual clause effects.

## 8. Identical user payload proof

Each request is checked against the original archived compact sorted JSON bytes,
then paired A/B bodies are compared excluding only `system`. All nine pairs pass.
The three existing fields remain `state`, `target_action`, and
`VERIFIED_CHRONOLOGICAL_HISTORY`; every history is `[]`. No examples, domain lists,
canonical action names or explanatory text were added to user payloads.

Private registration SHA256: `d6f1d5ab4fc54ef18432167a3549639d361c9df550ecd7084dc791b4c96b862e`.
Exact requests and per-context payload SHA256s are retained; the latter are public
in `results.json`. The independent raw recount also checks the original archive.

## 9. Model/config

`dolphin-mixtral:latest`, Ollama 0.1.16, GGUF 47B Q4_0. All five manifest-referenced
blobs were fully hashed before inference, including all 26,441,544,128 weight bytes.
Manifest SHA256 `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`;
weights SHA256 `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
The live server version, manifest, 47B/Q4_0 details and exact chat template match.

Every request: temperature 0.2, top_p 0.9, top_k 40, num_predict 32, num_ctx 2048,
repeat_penalty 1.1, original registered seed. Requests are stateless, stream=false;
returned context is archived but never sent onward. No constrained decoding,
repair, retry, replacement, extension or additional seed.

## 10. Exact 18-call schedule

| Call (1-based) | Context | Original episode | Condition | Seed |
|---|---|---|---|---|
| 1 | 0 | 0 | A | 80003 |
| 2 | 0 | 0 | B | 80003 |
| 3 | 1 | 2 | B | 80005 |
| 4 | 1 | 2 | A | 80005 |
| 5 | 2 | 4 | A | 80007 |
| 6 | 2 | 4 | B | 80007 |
| 7 | 3 | 5 | B | 80008 |
| 8 | 3 | 5 | A | 80008 |
| 9 | 4 | 7 | A | 80004 |
| 10 | 4 | 7 | B | 80004 |
| 11 | 5 | 8 | B | 80005 |
| 12 | 5 | 8 | A | 80005 |
| 13 | 6 | 9 | A | 80006 |
| 14 | 6 | 9 | B | 80006 |
| 15 | 7 | 10 | B | 80007 |
| 16 | 7 | 10 | A | 80007 |
| 17 | 8 | 11 | A | 80008 |
| 18 | 8 | 11 | B | 80008 |

All 18 registered calls completed. Even context indices used A/B; odd indices B/A. The original seed is shared within each pair. Order was not adapted to output.

## 11. Parser contract

The original `experiments.model_map_proposal_v0.adapter.parse` is imported unchanged.
One JSON object; exactly `next_state` and `consequence`; exact integers only;
next_state 0..3; consequence -1/0/1; reject duplicate keys and trailing prose/object.
No coercion, extraction, response repair or substitution of world truth.

Original adapter SHA256: `0195cc2b5fdb657dcb53f6991ed5494f6ffeb2f279cdb4ae0d4f6b9589dc0494`.
Thirteen malformed-input cases were rejected; five category fixtures checked
noncoercion/counting, and paired-byte tampering was rejected, all with zero inference.

## 12. Condition A validity

| Metric | Count / 9 |
|---|---|
| valid | 0/9 |
| JSON_decodable | 9/9 |
| exact_keys | 9/9 |
| integer_next_state | 9/9 |
| in_domain_next_state | 9/9 |
| integer_consequence | 0/9 |
| in_domain_consequence | 0/9 |
| opaque_token_consequence | 4/9 |
| prose_string_consequence | 5/9 |
| embedded_token_consequence | 5/9 |

Malformed reasons: `{"exact integers required": 9}`.

Other category counts: `{"bool_fields": 0, "duplicate_keys": 0, "extra_fields": 0, "float_fields": 0, "missing_fields": 0, "multiple_objects": 0, "null_fields": 0, "numeric_string_fields": 0, "out_of_domain_integer": 0, "prose_outside_json": 0}`.

Original-contract all-nine failure-pattern replication: **OBSERVED**. Historical raw-text equality is 3/9 and is descriptive only.

## 13. Condition B validity

| Metric | Count / 9 |
|---|---|
| valid | 9/9 |
| JSON_decodable | 9/9 |
| exact_keys | 9/9 |
| integer_next_state | 9/9 |
| in_domain_next_state | 9/9 |
| integer_consequence | 9/9 |
| in_domain_consequence | 9/9 |
| opaque_token_consequence | 0/9 |
| prose_string_consequence | 0/9 |
| embedded_token_consequence | 0/9 |

Malformed reasons: `{}`.

Other category counts: `{"bool_fields": 0, "duplicate_keys": 0, "extra_fields": 0, "float_fields": 0, "missing_fields": 0, "multiple_objects": 0, "null_fields": 0, "numeric_string_fields": 0, "out_of_domain_integer": 0, "prose_outside_json": 0}`.

These are schema-compliance counts, not correctness scores.

## 14. Paired outcomes

| Context | A valid | B valid |
|---|---|---|
| 0 | False | True |
| 1 | False | True |
| 2 | False | True |
| 3 | False | True |
| 4 | False | True |
| 5 | False | True |
| 6 | False | True |
| 7 | False | True |
| 8 | False | True |

Pair counts: `{"A_invalid_B_valid": 9, "A_valid_B_invalid": 0, "both_invalid": 0, "both_valid": 0}`.

## 15. O1 breakdown

A valid **0/4**; B valid **4/4**. Full type/category counts are in compact results. The frozen family condition requires B to be at least as compliant as A; no separate family success threshold or representation-neutrality claim.

## 16. O2 breakdown

A valid **0/5**; B valid **5/5**. Full type/category counts are in compact results. The frozen family condition requires B to be at least as compliant as A; no separate family success threshold or representation-neutrality claim.

## 17. Consequence-type failures

Condition A: consequence types `{"str": 9}`; integer/in-domain counts 0/9 and 0/9.

Condition B: consequence types `{"int": 9}`; integer/in-domain counts 9/9 and 9/9.

Categories describe original text. Values are never repaired or mapped from an action token to a number.

## 18. Token/prose leakage

Condition A: bare opaque consequence 4/9, prose-string consequence 5/9, embedded opaque-token prose 5/9.

Condition B: bare opaque consequence 0/9, prose-string consequence 0/9, embedded opaque-token prose 0/9.

Raw strings and parser results are retained privately. These shape changes do not identify an internal model mechanism.

## 19. UNKNOWN IS NOT MEMORY preservation

Each payload was reconstructed from zero original authorized observations and
matched the archived bytes. `[]` is the current projection of zero matching
records, never an event. The experiment creates no Memory, package, receipt,
placeholder observation or external event; the generation transport receives only
the fixed request body. Original composition snapshots have zero Memory/packages
and absent receipts, verified during registration. No UNTRIED or [] event was
introduced. Existing input-binding replay remains unchanged, including removal of
absence representations when authenticated observations exist. This study itself
does not execute that transition or seed Memory to demonstrate numeric output.

## 20. Frozen primary criterion

| Frozen requirement | Observed | Pass |
|---|---|---|
| B valid >=8/9 | B 9/9 | True |
| A invalid / B valid >=7/9 | 9 | True |
| A valid / B invalid <=1/9 | 0 | True |
| Both families improved or equal | O1 and O2 B >= A | True |
| All 18 complete | 18/18 | True |
| Parser unchanged | original SHA256 | True |
| User payloads byte-identical | 9/9 exact paired/original bytes | True |
| Model/config/seed matching | pinned model, sampler, original paired seeds | True |

Primary decision: **SCHEMA-CONTRACT EFFECT SUPPORTED**. All eight prospective requirements are required; none was changed after inference.

## 21. What is established

Original-contract replication: **OBSERVED**. Explicit-contract compliance: **9/9**. The independently frozen primary decision is **SCHEMA-CONTRACT EFFECT SUPPORTED**. In these nine matched empty-history contexts the explicit visible contract improved schema admission under the unchanged parser.

## 22. What is not established

Prediction accuracy, reward, learning, receipt agreement, causal world inference,
Recovery usefulness, Explorer behavior, sequential composition and representation
neutrality are untested here. A valid integer pair may be entirely wrong about the
world. This experiment does not establish empty history as the cause of the old
failure, nor separate effects of type, domain and exact-field instructions.

## 23. Exact replay

All 18 recorded raw responses were replayed with zero new inference. Five files
matched byte-for-byte: registration, runtime metadata, attempted requests, complete
model-call records, and compact results. An independent recount reapplied the old
parser and checked original payloads, seeds, request-body differences, counts and
primary decision. Exact transcripts remain outside the public Git tree.
`verification.json` records actual command timestamps, exits and file digests.

## 24. Historical preservation

Five focused post-study checks executed successfully with zero inference:
composition-v1 (seven files), forensic diagnosis-v0 (two), input-bindings-v1 (three),
Map-v0 (seven), established-prior Map-v1 (seven). Each regenerated file matches its
original archive byte-for-byte. Composition remains C; forensic diagnosis and
input bindings remain their historical A findings. All 447 substantive historical
files match parent bytes; only root README and public manifest gain this checkpoint.
Main, tags and other branches are unchanged. No full historical campaign universe
was rerun.

## 25. Limitations

Nine selected prior-failure contexts, one pinned model/runtime and fixed original
seeds. All states are 0, histories empty, aliases and seeds repeat, and payloads
have only three distinct target renderings. The nine contexts are not nine
independent linguistic tasks; no broad statistical generalization follows.
Counterbalancing reduces simple order confounding but does not erase runtime
nondeterminism. No world event tests prediction content. The specification is a
bundled intervention. Public summaries support inspection, while exact replay
requires the retained private original and new response archives.

## 26. Narrowest defensible conclusion

With unchanged payloads, parser, original seeds and sampler in these nine selected empty-history contexts, explicit schema instructions yielded 9/9 valid outputs versus 0/9 under the original instruction. **SCHEMA-CONTRACT EFFECT SUPPORTED** under the prospective rule. Historical composition-v1 remains C.

## 27. Recommendation

A separate research decision may consider composition-v2 using the now-explicit Map contract. Stop here: no composition-v2 implementation or live composition rerun is authorized by this checkpoint. No parser, Explorer, authority, Memory, examples or decoding changes were made.
