# R2 deterministic postmortem

Status: `R2_DETERMINISTIC_POSTMORTEM_COMPLETE`. This is a descriptive completion status, not a capability PASS/FAIL. The R2 primary classification remains **`BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0`**, `replacement_id: R2`. Its score bytes and every original credit are unchanged.

Branch: `analysis/blind-diagnostic-r2-postmortem-v0`, based on published R2 head `f4becaf11220f853a87e741fa84009bd0de715b2`. The final publication SHA is the audited remote head returned in the publication report; it cannot be embedded in its own commit.

The decomposition accounts for **80/80 rendering rows, 20/20 semantic cases, 24/24 current-defect outputs and 6/6 matched pairs**. The 20 designed semantic cases are the scientific units. Their four renderings are correlated; no independent-sample or statistical-generalization claim is made.

## Freeze order and method

| Milestone | Commit |
|---|---|
| Published R2 base | `f4becaf11220f853a87e741fa84009bd0de715b2` |
| Codebook and example-selection freeze | `36a2f7f4b498707cbb71b26e68cc25226918982a` |
| Tested implementation freeze | `b8ddfb4d05ad1745b1c78bcdd08c464c0c5dfe84` |
| Deterministic results and replay freeze, before prose review | `7b8ba59444df26ef4e4fdb40dab678f6d031e337` |

The codebook is retrospective: the published R2 negative result and prior summary were known. It was committed before generating these new aggregates. Eleven synthetic edge-case tests passed. A second analyzer invocation reproduced all eight deterministic artifacts byte for byte. No scientific scorer function was invoked; the original strict parser and frozen full schema checked output validity, and all rendering, semantic and pair credits were copied from published `scores.json`.

Field checks use identical Python type and value and only the frozen accepted alternatives. Each field marginal may match any accepted alternative for that field; a full witness must match one entire accepted alternative. Components use the frozen exact-list comparison. No prose meaning is part of deterministic classification, witness checking, or counts. The only deterministic scan over prose finds the exact opaque-ID regex and records its locations.

## Primary deterministic code counts

Rendering counts are rows bearing a code. Semantic counts are distinct worlds with at least one such row, **not** the original three-of-four credit. Codes overlap and must not be summed as distinct failures. Pass markers are labeled. Representation codes attached to renderings are distinguished from native contrast counts below.

| Code | Renderings | Worlds with any | Kind |
|---|---|---|---|
| `HEALTHY_FALSE_CURRENT` | 3 | 2 | failure |
| `INSUFFICIENT_AS_CURRENT` | 14 | 4 | failure |
| `INSUFFICIENT_OTHER_MISCLASSIFICATION` | 2 | 2 | failure |
| `HISTORICAL_AS_CURRENT` | 10 | 3 | failure |
| `HISTORICAL_OTHER_MISCLASSIFICATION` | 1 | 1 | failure |
| `INVALID_EVIDENCE_AS_CURRENT` | 8 | 3 | failure |
| `INVALID_EVIDENCE_OTHER_MISCLASSIFICATION` | 2 | 2 | failure |
| `CURRENT_DEFECT_MISSED` | 0 | 0 | failure |
| `COMPONENT_MISMATCH` | 1 | 1 | failure |
| `STRUCTURED_WITNESS_MISMATCH` | 24 | 6 | failure |
| `DECISIVE_FIELD_MISMATCH` | 24 | 6 | failure |
| `CAUSE_WITNESS_MISMATCH` | 0 | 0 | failure |
| `EFFECT_WITNESS_MISMATCH` | 4 | 2 | failure |
| `CONTRACT_WITNESS_MISMATCH` | 0 | 0 | failure |
| `DECISIVE_EVIDENCE_MISMATCH` | 12 | 4 | failure |
| `OBSERVED_VALUE_MISMATCH` | 24 | 6 | failure |
| `REQUIRED_VALUE_MISMATCH` | 24 | 6 | failure |
| `MISSING_REQUIRED_EVIDENCE` | 77 | 20 | failure |
| `INVENTED_ID` | 2 | 2 | failure |
| `EVIDENCE_GROUNDING_PASS` | 2 | 1 | pass_marker |
| `STRICT_JSON_FAILURE` | 0 | 0 | failure |
| `SCHEMA_FAILURE` | 3 | 3 | failure |
| `CLASSIFICATION_SCHEMA_PASS` | 77 | 20 | pass_marker |
| `LABEL_MAP_CLASS_DISAGREEMENT` | 18 | 7 | failure |
| `ORDER_CLASS_DISAGREEMENT` | 14 | 6 | failure |
| `SEMANTIC_REPRESENTATION_INCONSISTENT` | 36 | 9 | failure |

The `EVIDENCE_GROUNDING_PASS` marker appears in two renderings of one world, but original semantic grounding credit remains 0/20 because that world lacks three grounded renderings.

## Classification, abstention, temporal and integrity behavior

D = current defect; H = no supported diagnosis; U = insufficient evidence; T = historical defect not current; X = invalid/contradictory evidence. The exact enum strings are in the codebook. Counts below describe selected classes, including schema-invalid finals.

| Selected label | Rendering selections | Worlds with any selection |
|---|---|---|
| D | 59 | 18 |
| H | 17 | 8 |
| U | 0 | 0 |
| T | 2 | 2 |
| X | 2 | 1 |

There are **59 current-defect selections**: 24 on true current defects, 3 on healthy evidence, 14 on insufficient evidence, 10 on historical evidence and 8 on invalid evidence. Current defect is selected at least once in 18/20 worlds, including every true-current, insufficient, historical and invalid world and 2/4 healthy worlds. There are no missed current-defect selections.

| Gold / selected | D | H | U | T | X | Original semantic classification credit |
|---|---|---|---|---|---|---|
| D | 24 | 0 | 0 | 0 | 0 | 6/6 |
| H | 3 | 13 | 0 | 0 | 0 | 3/4 |
| U | 14 | 1 | 0 | 1 | 0 | 0/4 |
| T | 10 | 1 | 0 | 1 | 0 | 0/3 |
| X | 8 | 2 | 0 | 0 | 2 | 0/3 |

**Abstention:** U was selected zero times. Gold U renderings selected D 14 times, H once and T once, spanning all four insufficient worlds; semantic U correctness is 0/4. This records behavior without attributing motives.

**Temporal/currentness:** historical-as-current occurred in 10/12 renderings and in all three historical worlds. The other incorrect historical rendering selected H; one selected T correctly. Original semantic historical correctness remains 0/3.

**Evidence integrity:** gold X renderings selected X correctly twice (one world), D eight times (all three worlds), and H twice (two worlds). Original invalid-evidence semantic correctness remains 0/3. No new evidence-integrity diagnosis or causal attribution is assigned.

## Localization field decomposition

All field denominators are the 24 gold-current renderings or their six worlds. “Any” and “all four” are descriptive exact-match coverage, not new localization credit.

| Exact field/check | Renderings /24 | Worlds any /6 | Worlds all four /6 |
|---|---|---|---|
| affected_component_exact | 23 | 6 | 5 |
| contract_evidence_id | 24 | 6 | 6 |
| cause_evidence_id | 24 | 6 | 6 |
| effect_evidence_id | 20 | 6 | 4 |
| decisive_evidence_id | 12 | 4 | 2 |
| decisive_field | 0 | 0 | 0 |
| observed_value | 0 | 0 | 0 |
| required_value | 0 | 0 | 0 |
| all_required_evidence_cited | 0 | 0 | 0 |
| structured_witness_exact | 0 | 0 | 0 |

The zero full-witness result is not caused by a single mismatched field: **all 24 outputs mismatch decisive field, observed value and required value**. Contract and cause IDs are exact in all 24; effect IDs are exact in 20 and decisive evidence IDs in 12. Of seven witness fields, 10 outputs mismatch three, 12 mismatch four, and two mismatch five. These are exact frozen-structure comparisons; they do not measure semantic equivalence of prose.

The [24-output table](deterministic/current-defect-postmortem.json) records each returned component and structured field, every accepted witness, exactness flags, required-citation status and original localization credit. No accepted alternative is broadened or assembled from marginal matches.

## Evidence citations, invented IDs and output validity

Required evidence is missing in **77/80 renderings**, touching **20/20 worlds**, with **121 missing required-ID occurrences**. Exact missing IDs are retained in every rendering row. Missing-ID distribution:

| Missing required IDs in one rendering | Renderings |
|---|---|
| 0 | 3 |
| 1 | 46 |
| 2 | 19 |
| 3 | 11 |
| 4 | 1 |

Three renderings contain every required citation; only two receive original evidence-grounding credit. Complete citation is a separate descriptive check and cannot override classification/schema/ID requirements. Original grounding remains 2/80 renderings and 0/20 worlds.

Under this codebook's authorized **nonexistent-ID** definition, `INVENTED_ID` occurs in **two renderings / two worlds**, with **two rendering-ID pairs, two globally distinct IDs and four textual occurrences**. The exact IDs are `z7c07a05ecc99376d` and `zef9e7c395c2dc489`. The first appears at `/evidence_ids/3` in `08853493bcfdacd9e8c1`; the second appears at `/evidence_ids/0`, `/causal_mechanism/cause_evidence_id` and `/causal_mechanism/decisive_evidence_id` in `1265fa2e94f736b89310`.

**The frozen primary ID gate still reports three failing outputs and four bad-ID pairs.** Its `invented_ids` field also flags existing IDs used in incorrect categories. In `dc30870373ebc287fff2`, `z59fe799b77469f35` is a component ID and `z7ed9ef3aca2f765f` is an event ID; both exist in the rendered case but are used in evidence-record slots. The original score fields are copied unchanged beside the narrower nonexistent-ID field. This distinction neither repairs an output nor changes a gate.

Strict JSON failures: 0/80. Schema failures: 3/80, in three worlds. Classification/schema pass markers: 77/80. All three schema failures retain the published validator keyword `type` and instance path `["causal_mechanism"]`, with full published schema paths in each row. Original `ids_valid=false` after schema failure does not independently establish an invented-ID error.

## Representation and matched pairs

Native contrast counts are **9/40 A/B disagreements** across seven worlds and **7/40 order disagreements** across six worlds. Both endpoints carry each disagreement code, giving 18 and 14 tagged renderings respectively. Original representation inconsistency is **9/20 worlds**, attaching to their 36 renderings; original consistency remains 11/20.

| Gold class | A/B disagreements | Order disagreements | Contrasts per factor | Inconsistent worlds |
|---|---|---|---|---|
| D | 0 | 0 | 12 | 0 |
| H | 3 | 1 | 8 | 2 |
| U | 2 | 2 | 8 | 3 |
| T | 2 | 1 | 6 | 2 |
| X | 2 | 3 | 6 | 2 |

Original factor accuracy remains A 19/40, B 21/40, order 1 21/40, order 2 19/40. No significance or causal-generalization claim is added.

| Pair | Endpoint gold classes | Original result | Jointly correct cells /4 | Semantic failed endpoint | Failed-cell reasons |
|---|---|---|---|---|---|
| P1 | D / H | FAIL | 2 | right | classification_only: 2 |
| P2 | D / T | FAIL | 0 | right | classification_only: 4 |
| P3 | D / H | PASS | 4 | none | none |
| P4 | D / H | PASS | 3 | none | both: 1 |
| P5 | D / U | FAIL | 0 | right | classification_only: 3, both: 1 |
| P6 | D / H | PASS | 4 | none | none |

P1, P2 and P5 fail at the right semantic endpoint; all true-current left endpoints retain credit. P4 passes despite one failing right cell because its original three-of-four criteria still hold. “Both” means wrong selected class plus schema/ID invalidity within the cell; it is not a causal explanation. Each cell retains selected classes, schema and ID states and endpoint-specific reasons in [matched-pair-postmortem.json](deterministic/matched-pair-postmortem.json).

## Per-family breakdown

| Family | Correct renderings | Correct worlds | A/B disagreements | Order disagreements | Contrasts each | Inconsistent worlds |
|---|---|---|---|---|---|---|
| version_selection | 6/20 | 1/5 | 4 | 2 | 10 | 4 |
| authority_precedence | 4/8 | 1/2 | 0 | 0 | 4 | 0 |
| entity_binding | 8/12 | 2/3 | 0 | 0 | 6 | 0 |
| publication_update | 9/16 | 2/4 | 3 | 4 | 8 | 3 |
| operation_idempotence | 5/12 | 1/3 | 2 | 1 | 6 | 2 |
| boundary_comparison | 8/12 | 2/3 | 0 | 0 | 6 | 0 |

Current-defect exact matches by family (each denominator is four renderings):

| Family | Component | Contract | Cause | Effect | Decisive ID | Field | Observed | Required | Full witness |
|---|---|---|---|---|---|---|---|---|---|
| version_selection | 4 | 4 | 4 | 2 | 4 | 0 | 0 | 0 | 0 |
| authority_precedence | 4 | 4 | 4 | 4 | 2 | 0 | 0 | 0 | 0 |
| entity_binding | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 |
| publication_update | 4 | 4 | 4 | 4 | 2 | 0 | 0 | 0 | 0 |
| operation_idempotence | 4 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 |
| boundary_comparison | 3 | 4 | 4 | 2 | 0 | 0 | 0 | 0 | 0 |

Every family has 0/4 current-defect outputs citing all required evidence and 0/4 full witnesses. The aggregate JSON also contains all 26 code counts, both rendering and semantic incidence, separately for every family and gold class.

## Reproducibility, preservation and publication

Remote-reference note: before publication, all nine protected research/runtime remote heads matched the inherited baseline. Remote `main` was observed at `f79b1e5df3deae6941e62349aeea5eeec310e581`, while preserved local `main` remains `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`. Neither was modified. [Remote preservation baseline](remote-preservation-baseline.json) records this discrepancy and all ten observed remote heads for post-push comparison; it does not claim an earlier unobserved remote state.

Artifacts: [codebook](codebook.json), [80 rendering rows](deterministic/rendering-postmortem.jsonl), [20 semantic rows](deterministic/semantic-postmortem.json), [aggregate counts](deterministic/aggregate-postmortem.json), [representation contrasts](deterministic/representation-contrasts.json), [pair cells](deterministic/matched-pair-postmortem.json), [24 current outputs](deterministic/current-defect-postmortem.json), [example selection](deterministic/qualitative-selection.json), [hash manifest](deterministic/deterministic-manifest.json), [exact replay](deterministic-replay.json), and [preservation verification](preservation-verification.json). The [runbook](RUNBOOK.md) provides the deterministic invocation; it accepts a new output directory and refuses overwrite.

Postflight verifies all **1,829 inherited tracked files**, all **257 public input hashes**, all **162 R2 raw hashes**, all frozen analysis files and **ten protected public branch heads**. Original Method Freeze `587ffedd39516b633376d222d6d84e6af186fcf8`, Case Freeze `2866e6bcf94539513c135df878b72058048e99cd`, scorer, gold, protocol, gates, R2 raw evidence and scores remain unchanged. R2 score SHA-256 remains `961dbaec40add7673aba15328efe9fd3f8d8eae5cd676b7da0c9043dc52f1883`.

Original v0 (`bb58926e0f2581bee38393e179b758b18d0879e4`) and R1 (`b156dd01ce6f1deed049fa2589581888d36f34fb`) remain INVALID_STUDY with zero calls. Engineering (`df2d0ebc41d7c1b53a85779c38dab45cb21ec2e9`) remains REAL_RUNTIME_CONTROL_PATH_QUALIFIED with zero model calls. R2 stays at `f4becaf11220f853a87e741fa84009bd0de715b2`. Active S (`afc1c856aecbae65a1389d0abf144b6a50d09133`) and E (`69947aa243a69e7ae26db534727a7122922d978d`) remain unchanged, as do architecture, Memory, policy and thresholds. The verification records all protected refs.

**Qwen calls: 0; other model calls: 0; hidden semantic-grader calls: 0; scientific scorer invocations: 0; Horus world executions: 0; receipts: 0; Memory writes: 0; policy changes: 0; training: 0; improvement proposals: 0.** No private reasoning, response envelopes, server logs or Memory databases were opened. Only public records and finals were used. No model server was launched and no architecture was implemented.

Publication is restricted to this separate analysis branch. The unchanged reachable-history publication audit checks every reachable commit/path and unique blob. Its passing artifact is committed as `publication-audit.json`, followed by a second audit of the exact final head before pushing that SHA alone with follow-tags disabled. Remote verification checks the analysis head and protected heads. Fifteen private-archive heads are excluded from reachable ancestry. The final remote SHA and final-head audit are returned in the publication report. No merge or subsequent study follows.

## QUALITATIVE ILLUSTRATIONS — NOT SCORED

Selection rules were committed in codebook freeze
`36a2f7f4b498707cbb71b26e68cc25226918982a`. Exact example IDs and public-final hashes
were committed with all deterministic results at
`7b8ba59444df26ef4e4fdb40dab678f6d031e337`, before reviewing their prose. Each example
is the first qualifying rendering in the original request schedule, not a
representative sample. Only these five selected examples receive qualitative
interpretation. These notes introduce no quantitative categories, semantic grades,
corrections, or changes to the frozen result.

### Historical evidence selected as current: schedule position 11

Render `c87f1c5cf6b59ecb5c54`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/c87f1c5cf6b59ecb5c54.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/c87f1c5cf6b59ecb5c54.json).

The structured class is `SUPPORTED_CURRENT_DEFECT`, but the diagnostic statement
says: “The current system has no active defect related to this rule.” Deployment
record `z4704a5c2dfcafa63` identifies current version `ze7eb460a5b8fafa7`. Its output
`z5cb258823ac8c0aa` reports `DENY`, while the older version's output
`z06955534bb7133f3` reports `ALLOW`. The final's prose itself distinguishes those
versions and says the current one correctly implements priority. This illustrates
a prose/class self-inconsistency in this example only. It does not create a new
counted category or earn historical-class credit.

### Insufficient evidence selected as current: schedule position 1

Render `e24ffa812432f3e62a4e`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/e24ffa812432f3e62a4e.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/e24ffa812432f3e62a4e.json).

Input `z4628edd3b127c8d2` records `attempt_total_before: 14` and
`batch_size: "UNKNOWN"`; publication fields and other writes are also `UNKNOWN`.
Output `zd19ba4a4149299b8` records `attempt_total_after: 19`. The final infers
“batch_size must be 5 to satisfy attempt_total_after=14+5=19” and treats the omitted
batch size as a component defect. Contract `z587ffca10dd5d46a` says UNKNOWN denotes
omitted information, never a default. This illustrates the selected
`INSUFFICIENT_AS_CURRENT` example; it does not establish that all insufficient
cases failed through the same interpretation.

### Invalid evidence selected as current: schedule position 5

Render `3b310ba249b0818e7e77`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/3b310ba249b0818e7e77.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/3b310ba249b0818e7e77.json).

Output `z61f8caf436dd1ea7` gives `published_reading: 27` and capture
`z038c0dac75a7b8fb` gives `published_reading: 28` for the same immutable event
`z6d8c6b5036566bf3`. Capture contract `z3f993a58ccd56c74` states that one immutable
event ID has one payload. The final notices the contradiction, yet says the
input/output worker “is responsible for the discrepancy” and selects a current
component defect. This illustrates diagnosis despite contradictory evidence in
this particular final. No causal attribution is credited or generalized.

### Correct component with an inexact witness: schedule position 7

Render `1fa86b8dd54b091e3ad3`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/1fa86b8dd54b091e3ad3.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/1fa86b8dd54b091e3ad3.json).

The final selects the correct component `z93b99a7c7cf13c6b` and describes a command
issued at equality. Its witness points to the input record, uses decisive field
`/data`, and puts serialized input objects into the observed/required value
strings. The frozen accepted witness instead uses output `zee9b747d8c7b724b`,
field `/command_issued`, and boolean values `true` and `false`. It also omits the
required deployment citation `z14c06969d2d49e5a`. These exact mismatches already
appear in the deterministic artifact; the prose earns no informal localization
credit.

### Healthy evidence selected as current: schedule position 20

Render `514366f8d50c91a4fba2`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/514366f8d50c91a4fba2.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/514366f8d50c91a4fba2.json).

Contract `z299561fbc696df15` explicitly says: “Repeated identical requests may
return identical values indefinitely.” The final instead says the contract
“prohibits identical outputs for repeated identical requests” and selects a
current defect. Both execution versions use the active configuration's value 23
and return 23. This example illustrates the already-counted healthy false-current
selection. The apparent reversal of the contract statement is not introduced as
a new quantitative category.


## DESIGN QUESTIONS MOTIVATED BY R2 — NOT TESTED

These are questions for a future preregistered study, not a proposed architecture, implementation plan, claim of efficacy, or authorization to proceed:

- Which facts in these published cases are mechanically derivable, and which require semantic judgment?
- Which exact contract, cause, effect, decisive-record, decisive-field and value fields could software construct without access to gold?
- Should evidence-integrity checks precede semantic diagnosis?
- Should deployment and current-version binding be mechanically precomputed?
- Should UNKNOWN-bearing decisive facts prevent a mechanically supported current-defect classification?
- Should evidence-ID and exact-witness assembly be separated from model prose?
- How should a future study test agreement between a structured class and its prose without granting retrospective credit?
