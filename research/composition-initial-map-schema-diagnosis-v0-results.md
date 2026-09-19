# Composition initial Map schema diagnosis v0

**A — CONCRETE MODEL/PARSER SPECIFICATION GAP IDENTIFIED. Zero new model calls.**
All nine recorded Map responses are single valid JSON objects with the required
keys and integer `next_state: 1`, but a **string-valued consequence**. The unchanged
parser requires exact integers and finite domains that the visible instruction
does not explicitly specify. This establishes a contract gap, **not its causal
effect on the outputs**. Composition-v1 remains C — NOT ESTABLISHED.

## 1. Parent/checkpoint identities

Parent: `0dcc5d810f5b03ce2479d8f151e3603f85906500`, composition-v1 C.
Forensic preregistration: `b5f39ac`; diagnostic implementation: `7b74ebc`.
Input-bindings-v1 `e10fbb8` remains A; composition-v0 `106e431` remains C.
Map v0 `f7b16c4`, established-prior Map v1 `b576b3a`, Recovery and all earlier
scientific sources/results remain unchanged. Of 442 inherited files, 440 retain
their original bytes; only root README and public manifest are extended. Main
and existing branches/tags are unchanged. Nothing pushed.

## 2. Preserved composition-v1 C

The original live counts remain Explorer 12 calls / 9 valid / 3 malformed;
Map 9 calls / 0 valid / 9 malformed; Recovery 0 calls; executions 0; Memory
commits 0. This diagnosis does not reinterpret any rejected text as a prediction,
repair any response, or change the original C classification.

## 3. Exact question

Which model-visible and parser contracts did the nine responses satisfy or violate,
and what observable conditions distinguish them from historical successful Map
calls? We identify the immediate parser rejection and the visible specification
gap. The evidence does not reveal why the model internally produced these strings.

## 4. Zero-call evidence sources

The retained composition-v1 `model-calls.jsonl`, `steps.jsonl`, `schedule.json`,
`metadata.json` and results were read without mutation. That study stores exact
prompts per call rather than in a separate `registered-prompts.json`. All nine
requests were reconstructed from its frozen schedule/renderer, admitted action,
empty Memory, recorded role system/options and template. Each reconstructed prompt
equals the archived string exactly. Reconstructed API bodies and template text
are retained privately; these are reconstructions, not new network captures.

Historical Map-v0 and established-prior-v1 retained call/registration/metadata
archives supply 144 real recorded responses each. Every registered history is
checked against its authenticated fixture records and recorded receipt provenance.
Raw strings, exact diffs and full classifications remain private. Input hashes
and compact findings are public.

Two deterministic diagnosis runs matched both output files byte-for-byte. Four
focused zero-inference replays also passed: composition-v1 (still C), input-bindings
v1 (still A), Map v0 and established-prior Map v1. All six commands returned expected
exit 0; a replay's successful execution does not change the checkpoint's scientific
classification. No whole-history campaign, server or model inference was run.

## 5. Nine raw Map failure classes

| Episode | Family / mapping | Seed | Admitted action / target | Consequence form |
| --- | --- | ---: | --- | --- |
| 0 | O1 / 0 | 80003 | ADVANCE / K1 | bare K2 token |
| 2 | O1 / 2 | 80005 | HOLD / K1 | bare K2 token |
| 4 | O1 / 4 | 80007 | RETREAT / K1 | bare K2 token |
| 5 | O1 / 5 | 80008 | RETREAT / K1 | bare K2 token |
| 7 | O2 / 1 | 80004 | ADVANCE / Q7 | sentence mentioning Q7 |
| 8 | O2 / 2 | 80005 | HOLD / Q7 | sentence mentioning Q7 |
| 9 | O2 / 3 | 80006 | RETREAT / M4 | sentence mentioning M4 |
| 10 | O2 / 4 | 80007 | RETREAT / Q7 | sentence mentioning Q7 |
| 11 | O2 / 5 | 80008 | RETREAT / Q7 | sentence mentioning Q7 |

All nine decode as one JSON object. Returned keys, in order, are `next_state` and
`consequence`. All next_state values are integer 1, within the allowed state domain.
All consequence values are strings. All strict rejections are `exact integers required`;
the parser rejects at the type check before its finite-domain check.

There are **zero** extra keys, missing keys, duplicate keys, multiple objects,
prose outside JSON, numeric strings, booleans, floats, nulls or canonical-action
strings in these responses. Five have prose *inside consequence*, distinct from
prose appended outside JSON. That prose may also conflict with the instruction's
“no explanation” direction; it does not make the missing integer requirement explicit.

## 6. Parser contract

The exact function is the unchanged
[`experiments.model_map_proposal_v0.adapter.parse`](../experiments/model_map_proposal_v0/adapter.py),
also used by the generalized binding and both historical studies. Its source hash
matches all three archived source records/frozen-input records:
`0195cc2b5fdb657dcb53f6991ed5494f6ffeb2f279cdb4ae0d4f6b9589dc0494`.

It requires text that decodes as one JSON object, exactly the keys `next_state`
and `consequence`, Python exact integer types for both values, next_state in
{0,1,2,3}, and consequence in {-1,0,1}. `type(value) is int` rejects booleans,
floats, numeric strings and nulls. A duplicate-key hook rejects repeated names.
Extra/missing keys and trailing objects/prose reject. Surrounding JSON whitespace
is allowed. No coercion or response repair occurs.

## 7. Model-visible contract

The actual Map system instruction is identical across all three studies:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object containing next_state and consequence, and no explanation.

Each composition Map user payload has exactly `state: 0`, an opaque `target_action`
(K1, Q7 or M4), and `VERIFIED_CHRONOLOGICAL_HISTORY: []`. It contains no declaration
of either output type, no allowed-state list and no consequence-domain list.
Field names alone are not explicit integer/domain requirements.

The per-call system and `metadata.role_systems.Map` identify what Map actually
received. The inherited flat `metadata.system` field names the Recovery instruction;
it must not be mistaken for the Map request's instruction. The recorded template
inserts the actual request's system and prompt. Its stored default assistant
instruction adds no output-schema specification and is overridden by the request.

## 8. Explicit versus implicit requirements

| Requirement | Explicitly visible? | Evidence / enforcement |
| --- | --- | --- |
| One JSON object | yes | “exactly one JSON object” |
| Both named fields present | yes | “containing next_state and consequence” |
| No explanation | yes | “and no explanation” |
| No multiple objects | yes | follows explicit one-object instruction |
| No additional fields | not explicit | “containing” does not enumerate an exclusive schema; parser requires exact keys |
| next_state exact integer | no | parser-only type constraint |
| next_state restricted to 0,1,2,3 | no | parser-only domain constraint |
| consequence exact integer | no | parser-only type constraint; relevant to all nine failures |
| consequence restricted to -1,0,1 | no | parser-only domain constraint |
| No bool/float/numeric-string/null values | no | follows parser's exact-int check, not an explicit prompt restriction |
| No duplicate field names | not explicit | enforced by parser hook |

Current state 0 supplies a numeric input value; it does not explicitly define an
output type or legal domain. Historical numeric examples are implicit demonstrations,
not explicit complete contracts. Types/domains documented for researchers or in
code are not thereby communicated to the model.

## 9. Opaque-token leakage

**4/9** consequences are bare opaque tokens: K2 in every O1 response. None equals
the target K1. Under the registered mappings, that K2 denotes HOLD in episodes 0/5
and ADVANCE in episodes 2/4, always a different action from the admitted target.

**5/9** consequences are sentences containing the target token: Q7 four times and
M4 once. These entire strings are not equal to the target token; they contain it.
Across both forms, consequence-field token mentions are K2=4, Q7=4, M4=1.
No token appears in next_state; all leakage is consequence-only, inside otherwise
well-formed JSON with the required keys. This is an output-shape pattern, not a
causal token prior or a mapping from tokens to numeric consequences.

## 10. Empty-history context

All nine exact-pair histories are [], generated from zero Memory records. Current
state 0 is the only numeric JSON value in each payload. Digits inside an opaque
token are characters, not numeric outcome examples. There is no allowed-state
domain, consequence-domain example or prior outcome row.

Across these prompt structures, history rows are the only prompt-local examples
of numeric `next_state` and `consequence` output fields. Their absence leaves no
numeric consequence example in the composition prompts. This describes visible
content; it does not establish what the model inferred from it.

## 11. Historical Map-v0 comparison

144 calls: **142 valid, 2 malformed**. Scope is state 1 / HOLD. Exact-pair depths
1,2,3 occur 48 times each; valid counts are 46/48, 48/48 and 48/48 respectively.
All 144 prompts contain authenticated numeric next_state and consequence examples.
The two malformed responses have integer consequence 2, outside the unchanged
domain; they remain malformed. Non-empty history did not guarantee domain compliance.

The same system, parser and payload shape are used. Historical outcome rows have
next_state 1 and consequence +1 or -1. They do not enumerate the complete state
domain or demonstrate consequence 0. CONTROL/SHIFT history conditions and this
restricted state/action scope differ from the initial composition setting.

## 12. Established-prior-v1 comparison

144 calls: **144 valid, 0 malformed**. Same state 1 / HOLD scope, instruction,
parser and payload shape. Depths 2,3,4 occur 48 times each, all valid. All prompts
contain authenticated numeric next_state/consequence rows (next_state 1;
consequences +1/-1). These are numerical examples, not explicit declarations of
all allowed types/domains. The earlier positive result remains unchanged.

Combined historical compliance is 286/288 with non-empty history, compared with
0/9 at empty history in composition. **EMPTY-HISTORY ASSOCIATION OBSERVED**;
these are different studies/conditions, not randomized evidence that history
absence caused the format errors.

## 13. Representative exact prompt diffs

The preregistered selection chooses the earliest live HOLD call with matching
historical family/mapping/alias: composition episode 2, call index 4. Historical
CONTROL H0 and CONTROL P0 both use index 24, O1 mapping 2, target K1 / HOLD.

| Field | A: composition | B: Map-v0 H0 | C: Map-v1 P0 |
| --- | --- | --- | --- |
| Current state | 0 | 1 | 1 |
| Target alias / underlying action | K1 / HOLD | K1 / HOLD | K1 / HOLD |
| Mapping | K1=HOLD, K2=ADVANCE, K3=RETREAT | same | same |
| History length | 0 | 1 | 2 |
| Prior transaction IDs | none | 1 | 1,2 |
| Prior next_state values | none | 1 | 1,1 |
| Prior consequence values | none | +1 | +1,+1 |
| Seed | 80005 | 50003 | 60003 |
| Serialization | sorted compact JSON | same | same |
| System instruction | quoted above | exact same bytes | exact same bytes |

All history rows use surface_action K1. Non-seed sampler settings are identical:
temperature .2, top_p .9, top_k 40, num_predict 32, num_ctx 2048, repeat_penalty 1.1.
Model/runtime match: dolphin-mixtral:latest, Ollama 0.1.16, 47B Q4_0, identical
manifest/weights digests and exact chat template. Stored parameter text places the
num_ctx line differently in Map-v1 metadata; the parameter lines/values match,
and actual per-request options match except seed. Full exact private prompt diffs
retain this distinction rather than claiming all metadata bytes are identical.

This holds target/mapping/action constant but differs in current state, seed and
history. It is not a controlled estimate of an empty-history or schema effect.

## 14. Family/mapping/action patterns

Observed shapes separate by family: O1 has 4/4 bare-token consequences; O2 has 5/5
prose consequences mentioning the target. All nine share the same integer-type
rejection. The failures cover ADVANCE=2, HOLD=2, RETREAT=5. The full seed/mapping
schedule appears in section 5 and compact per-case evidence. Three other scheduled
cells never reached Map because Explorer failed; they are not missing Map successes.
With nine selected calls and differing study conditions, no intrinsic alias,
seed, mapping or action cause is established.

## 15. Three Explorer malformed outputs

| Episode | Family / mapping | Seed | Failure form | Offered token inside |
| --- | --- | ---: | --- | --- |
| 1 | O1 / 1 | 80003 | JSON object with action and verified_outcomes fields | K1 |
| 3 | O1 / 3 | 80005 | JSON object with action and verified_outcomes fields | K1 |
| 6 | O2 / 0 | 80002 | JSON object with action field | Q7 |

Each contains one offered token but returns a structured object instead of exactly
the token. The first two also include the literal UNTRIED in the output object.
None is a multiple-alias choice, canonical action, or extra-prose-only response.
The unchanged parser rejects all three; no token is extracted to repair admission.
Unlike the missing Map type declaration, Explorer explicitly requested exactly one
allowed action. This secondary finding authorizes no Explorer repair.

## 16. UNKNOWN IS NOT MEMORY preservation

All nine Map [] views derive mechanically from empty authorized Memory. All 12
live protected snapshots retain zero records, pairs and packages, and no receipt.
UNTRIED in two invalid Explorer responses remained raw output, never Memory.
Empty container arrays are not stored [] observations. No fake initial evidence,
dummy consequence 0 or pseudo-receipt was added.

The focused composition replay regenerates the projections from Memory and matches
all seven archived files byte-for-byte. Parent binding replay retains its synthetic
unknown→known A result. Exact historical Map replays preserve their response
classifications and numerical evidence. This verifies preservation without running
the entire historical verification set.

## 17. Classification

**A — CONCRETE MODEL/PARSER SPECIFICATION GAP IDENTIFIED.** The exact-integer
consequence constraint responsible for all nine parser rejections is not explicitly
communicated. Both finite domains and the next_state integer type are also absent
from the visible specification. B is unsupported because the visible contract is
not complete for those constraints. The two observed string forms do not obscure
the common, concrete type gap; C is unnecessary for this forensic classification.

Separately, **EMPTY-HISTORY ASSOCIATION OBSERVED**. Neither classification claims
causality. This diagnosis's A names a finding; it is not a successful live-composition
classification. Composition-v1 remains C.

## 18. What is established

All nine responses satisfy JSON decoding and the required field names but violate
the parser's exact-integer consequence requirement. Four leak a non-target bare
alias; five embed the target alias in prose. Output types/domains are not explicitly
specified in the visible Map prompt. Earlier prompts share that gap but contain
authenticated numeric examples, with much higher observed schema compliance.
The exact original parser/results remain unchanged, and all diagnostic outputs
are deterministically regenerated from retained evidence with zero inference.

## 19. What is not established

No internal mechanism, intrinsic token prior, or causal effect of empty history,
state, seed or schema wording is identified. No evidence shows that explicit types
would fix these responses, that fake history is appropriate, or that valid formatting
would imply accurate prediction. Historical numeric examples do not constitute
a complete contract or prove their own causal contribution. This work supplies
no new model behavior, sequential execution, learning or authority result.

## 20. Narrowest defensible conclusion

The immediate rejection reason is string-valued consequence, not broken JSON.
The interface enforced integer/domain requirements it never explicitly told the
model. Empty composition history also lacked the numeric outcome examples present
in the higher-compliance historical calls. A specification gap and an association
are established; why the model generated those strings remains unresolved.

## 21. Next research recommendation

**Option 2:** consider a separately preregistered small EMPTY-HISTORY SCHEMA-CONTRACT
experiment. The conceptual variable is original visible schema versus explicit
output types/domains, holding state, target action, empty history, mapping, seed,
parser, model and sampler matched. No revised prompt, implementation, decoding
constraint or inference is supplied here. Stop at this diagnosis.
