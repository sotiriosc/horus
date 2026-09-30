# Qwen Primitive-to-Ontology Reduction v0 — prospective method

Base: `67053bb802a7851e91b4e7aeb675a687875b8115`. Sole question: can the pinned Qwen map supplied correct primitive conclusions into the existing five-class ontology? No active Horus changes or intervention.

## Inputs and semantics

The frozen input schema is in schemas.json. Each request supplies only the primitive state (including its fixed declarative proposition-scope legend), verbatim class definitions, and output schema. The legend disambiguates what each primitive means; it contains no diagnostic rules, worked examples, gold, decision tree, or precedence instructions. All bindings and upstream discovery are resolved. A historical trial is the same mechanism/contract at an older version; the declared scope has no unlisted trials/defects. No state IDs, pair metadata, stratum tags, witness, author/auditor proof or earlier responses enter prompts.

Identity and equality describe two selected mark assertions; consistency describes the whole package, which may include other conflicting immutable provenance assertions. This allows a coherent single-field consistency delta without falsifying identity/equality. Under contradiction, the supplied trial propositions remain well-defined conditional facts, but the operational package is invalid. The reference completion is always admissible. KNOWN therefore co-occurs with NO_ALTERNATIVE; UNKNOWN with ALTERNATIVE_EXISTS. A current reference MATCH or MISMATCH may accompany UNDERDETERMINED. Alternative completions can agree in compliance, yielding DETERMINATE. These are the existing primitive meanings, now explicitly supplied, not novel concepts.

## Case construction and validation

Exactly 25 new pairs, 50 unique endpoint vectors, 10 per class. Fifteen changing pairs and ten stable pairs. All 25 pairs differ in exactly one primitive field. The pair inventory contains all ten unordered class transitions plus five repetitions; five sufficiency pairs, six contradiction pairs, two historical-observation pairs, two current-observation pairs. Stable pairs test identity/equality, current observations under contradiction, and historical observations under current uncertainty. Independent alternative-completion toggles are omitted because the reference-admissible convention couples that primitive to knownness; no incoherent fillers are used.

A deterministic author creates primitive objects and finite offline witnesses. A separate validator imports no author/gold procedure: it enumerates each witness's admissible input outcomes, recomputes every primitive, checks immutable assertions, and selects exactly one mutually exclusive ontology condition. It verifies exact class balance, unique objects, all single-field deltas, expected transitions, hashes, and prompt isolation. Offline witnesses and proofs never enter inference.

Descriptive strata are frozen: SIMPLE 2, PRECEDENCE 28, IRRELEVANT_CHANGE 20. The small SIMPLE stratum has no competence claim or separate gate. Pair tags are applied to both endpoints. The schedule has five blocks of ten with exactly two endpoints per class in each. Both large strata appear in every block; the two SIMPLE endpoints are split across the two run halves. A-first 13 / B-first 12. No adjacent matched endpoints. The seeded candidate schedule search is entirely prospective and never uses model responses.

## Runtime and zero-model qualification

New seed: 739182647, fixed for construction, schedule and every inference. Qwen3-14B Q4_K_M, model SHA256 500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0. llama.cpp b11242, commit 526c43b8f7dfea9032e9f35e7a1be9183ca7cc20, executable SHA256 778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5. Exact prior launch except isolated slot directory. Context 16384, one slot, all 41 offloadable layers on RTX 4090, original CPU-mapped embedding allocation retained. F16 KV, flash attention on. Native thinking on; DeepSeek reasoning format; reasoning budget 512. Temperature .2, top_p .9, top_k 40, min_p .05, max_tokens 2048. No tools, no retrieval, no target repository/filesystem access, no conversation history. HTTP JSON schema constraint via response_format type json_object with frozen schema. Cache disabled (request and server), slot erased before each request; no slot save/restore.

Zero-model qualification exercises real HTTP orchestration with synthetic mock replies, including all 50 dispatches, exact bytes, no answer carryover, failures, dropped connections, malformed finals, truncation, no retry, and hash/read-only handling. A separate zero-completion startup checks the pinned engine, context and offload. No scientific calls are used to tune anything.

## Raw-first execution

Exactly 50 one-shot scientific calls, one server. Frozen payload bytes only. Runner imports no scorer or gold. It reports completion counts, elapsed time and estimated remaining time only. No correctness inspection during execution. Verbatim final strings and safe usage/transport metadata are public; response envelopes, native reasoning, server logs and controls are private. Preserve their hashes. Errors stop the campaign without retries; a transport-incomplete campaign is invalid rather than repaired. Wrong, malformed or truncated final answers count as data, never grounds for retry.

All raw files are hashed and made read-only, then committed before running the frozen scorer. Scorer requires a raw commit containing the identical scorer and exact raw bytes. Duplicate JSON keys, extra keys, nonexact labels, fenced prose and malformed JSON fail schema. Whitespace around a valid JSON object is allowed. Schema-invalid means incorrect, with an INVALID_OUTPUT column alongside the five-by-five confusion matrix. Replay uses zero inference and must be byte-identical. No manual reinterpretation.

## Frozen gates and interpretations

Primary PRIMITIVE_TO_ONTOLOGY_REDUCTION_ESTABLISHED iff at least 43/50 AND at least 8/10 in EACH of the five classes. Otherwise PRIMITIVE_TO_ONTOLOGY_REDUCTION_NOT_ESTABLISHED.

Changing pair pass requires both exact endpoint labels and change in the required direction. Stable pair pass requires both exact endpoint labels and the same gold class. Secondary sensitivity gate requires at least 12/15 changing AND 8/10 stable passes (80% each). This tests counterfactual control separately from endpoint accuracy; never combine into one score.

Endpoint pass registers EXPLICIT_PRIMITIVE_REDUCTION_SUPPORTED. It supports this mapping on these supplied-correct-primitive cases; older failures are consistent with joint extraction/maintenance/composition difficulty, without proving internal cause. Endpoint failure registers EXPLICIT_PRIMITIVE_REDUCTION_NOT_ESTABLISHED: reduction remains unresolved even with discovery removed. If endpoint passes but pair gate fails, retain the primary interpretation AND report REDUCTION_ACCURACY_WITH_UNRELIABLE_COUNTERFACTUAL_SENSITIVITY as a caveat. If endpoint fails with strong strata, report the literal mixed result; no stratum rescues the gate.

Report sufficiency pairs (all other fields controlled), contradiction pairs and contradictory endpoints with current mismatch, historical mismatch, or current underdetermination, historical pairs and full D/N/T class accuracy, stable pairs and descriptive strata. These are descriptive, no new post-hoc gates. After scoring only, compare published Qwen 41/56, gpt-oss 42/56 and Ministral 27/56 qualitatively. Fresh cases plus supplied primitive conclusions change the task; no causal improvement percentage or identical-benchmark claim.

## Preservation and publication

All inherited files and prior heads remain unchanged. Publish only this new branch after full reachable-history and private-artifact audit, verify remote head, STOP. No merge, promotion, deterministic reducer in Horus, training, model switch, new comparator or subsequent study. No result establishes raw-evidence or end-to-end diagnosis, primitive discovery, autonomous Horus reasoning, learning, self-improvement, RSI, or architectural authorization.
