# Horus Temporal State Representation Gate v0 — prospective method

Exact base: `19c50c06caf99736acbf5c728da0148840e665a5`. This is the hard project gate requested by the user. Sole question: can the pinned Qwen construct current and prior violation states from resolved primitives without five-class compression? No active Horus change, deterministic operational reducer, action selection, training, new comparator or follow-on study.

## Exact task and semantic boundary

Only the two-field primary arm is included. The optional third-field arm is omitted to keep the hard gate focused and avoid extra inference. Exactly 36 scientific calls. Exact output is the strict object with current_violation and prior_violation, each YES/NO/UNKNOWN. Exact output definitions and aggregation semantics are frozen in common.py; the prompt supplies no diagnostic ontology labels or definitions, diagnosis/action request, answer examples, demonstrations, gold summary or class recommendation.

YES means the supplied determinate facts establish violation; NO means they establish compliance; UNKNOWN means they do not decide. Current refers only to the explicitly deployed trial. Prior is YES if at least one explicitly older trial is determinately violating, NO if all are determinately compliant, and UNKNOWN if none is demonstrated violating but at least one remains underdetermined. These are the user-specified output semantics, not case-specific answers. Every case contains at least one prior trial. All input facts are already resolved. No evidence lookup, arithmetic, opaque IDs, component binding or provenance discovery is needed.

The reference input is admissible. KNOWN/NO_ALTERNATIVE and UNKNOWN/ALTERNATIVE_EXISTS are coherent input states. UNKNOWN input can still yield determinate compliance across all admissible completions. An underdetermined trial can have either reference MATCH or MISMATCH. Package consistency concerns separate immutable provenance assertions; by frozen scope, it does not change the authoritative resolved trial propositions or these mechanical temporal fields. Thus contradiction controls are possible without asking for a valid operational diagnosis. No current/prior violation field or computed summary appears in the input object.

## Cases and balance

Exactly 36 states, all new IDs and normalized semantic signatures. Exactly 12 historical-focus states have current=NO/prior=YES. Subject to this mandatory oversampling, distribute the remaining 24 as evenly as possible over the other seven requested combinations: YES/NO 4, NO/NO 4, UNKNOWN/YES 4, UNKNOWN/NO 3, YES/YES 3, NO/UNKNOWN 3, UNKNOWN/UNKNOWN 3. YES/UNKNOWN is not a sampled gold cell (it remains a legal possible model output and is included in confusion reporting). No claims are made about competence in that unsampled cell.

Eighteen disjoint matched pairs cover all 36 endpoints: ten changing and eight stable. Every pair differs in exactly one prospectively declared primitive field. Changing pairs cover current NO↔YES with prior YES, prior NO↔YES with current NO or YES, current NO↔UNKNOWN with prior YES or UNKNOWN, prior YES↔UNKNOWN with current NO, and prior YES↔NO with current UNKNOWN. Stable pairs change package consistency or the reference relation within an underdetermined older trial. The latter stays irrelevant either because another older trial demonstrates a violation or because prior uncertainty remains. Historical-focus cases vary current knownness, old-trial structure, and consistent/contradictory provenance.

Freshness excludes every complete normalized signature from the prior 50 primitive-state cases, 30 role-state cases, and 56 aligned-state projections (136 prior state objects). Normalization ignores IDs, explanation wording, identity/equality decorations and prior-trial order; it retains package consistency and every current/prior primitive proposition. This prevents cosmetic renaming or list reordering from qualifying as fresh. Prior predictions and diagnostic gold are never consulted. Primitive definitions and abstract output combinations are intentionally reused; no conceptual novelty is claimed.

The author constructs finite offline trial witnesses and gold. The independent auditor imports no author/gold procedure: it enumerates admissible trial-completion worlds, recomputes every input primitive, computes the current violation truth set and the existential prior violation truth set, and converts singleton true/false or mixed sets into the target fields. It verifies coherence, exact balance, focus membership, every delta and gold transition. Offline witnesses/proofs never enter inference. The validator is scientific gold verification only, not a reducer added to Horus.

## Hard gate and exact scoring

TEMPORAL_STATE_REPRESENTATION_ESTABLISHED iff ALL seven conditions hold:

- Joint exact at least 32/36.
- current_violation correct at least 34/36.
- prior_violation correct at least 34/36.
- Historical-focus joint exact at least 11/12.
- Changing-pair exact passes at least 9/10 (90%).
- Stable-pair exact retention 8/8 (ceil(90% × 8) = 8).
- Schema-valid at least 35/36.

Otherwise TEMPORAL_STATE_REPRESENTATION_NOT_ESTABLISHED. No threshold relaxation. Schema validity requires exactly the two named keys with exact uppercase labels, no extras, duplicate keys, fences or prose. JSON key order and surrounding whitespace do not matter. A schema-invalid response counts wrong for BOTH fields and joint accuracy; no partial salvage, repair or manual interpretation.

A changing-pair exact pass requires both full output vectors correct, including the required flip direction and preservation of the other field. A stable-pair pass requires both vectors correct and equal to the stable gold. Report overall exact pair passes /18, changing exact /10, stable exact /8. Also report changed-field-only direction accuracy descriptively, and raw stable-vector agreement separately; neither can replace the exact pair gates or excuse a consistently wrong pair.

Report each field's three-by-three confusion with invalid-output column, plus the nine-by-nine joint confusion (including the unsampled YES/UNKNOWN row and prediction column) and invalid-output column. Report all 36 exact selections, 18 pair outcomes, historical focus, and descriptive controls for contradictory packages, multiple older trials, current uncertainty and prior uncertainty. No subset creates an extra success gate.

## Registered interpretation and project decision

Pass: Qwen can reliably construct the explicit current/prior violation state from supplied primitives on these frozen cases. This supports the hypothesis that previous historical-label failures may arise at or after compression into the five-class ontology, rather than establishing absence of the underlying relation. It does NOT prove an internal mechanism: datasets and requested output semantics differ. It permits consideration of a separately authorized engineering test of factorized grounded state; it does not authorize changing Horus here or establish improved real behavior.

Fail: reliable temporal relation construction is not established even after removing the five-class output. Publish, preserve and stop. Recommend putting this current Horus research direction on hold pending a genuinely new hypothesis, model capability or architecture. Do not compensate with a hidden deterministic solution or attribute that software's capability to Qwen. Do not launch another ontology, prompt-framing workaround, comparator, decomposition benchmark or subsequent study.

Regardless of result: no merge, promotion, architecture change or automatic follow-on experiment. The only possible later engineering target is separately authorized authenticated evidence → factorized grounded epistemic state → persistent temporal relations → action/evidence-selection policy, with the five-class ontology at most a reporting/compatibility layer. That later work must test actual behavior.

No RSI claim follows. A future system must prospectively: perform a useful task; accumulate authenticated consequences; improve later behavior from them; diagnose an implementation limitation; propose a bounded modification; predict measurable improvement before applying it; apply it only through an external/sandboxed authorization boundary; prospectively test it; retain it only when real consequences support it; and successfully repeat with the improved system. Require at least TWO prospectively separated successful improvement cycles before BOUNDED_RECURSIVE_SELF_IMPROVEMENT_SUPPORTED, scoped strictly to the tested environment and modification class. One self-modification is insufficient.

## Runtime and schedule

New prospective seed 1264087953. Qwen3-14B Q4_K_M model SHA256 500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0. llama.cpp b11242 / commit 526c43b8f7dfea9032e9f35e7a1be9183ca7cc20. Runtime executable SHA256 778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5. Context 16384, one slot, thinking on, DeepSeek reasoning format, reasoning budget 512, temperature .2, top_p .9, top_k 40, min_p .05, max_tokens 2048. F16 KV, flash attention on, original 41/41 GPU layer offload with CPU-mapped embedding allocation retained. Identical launch except isolated private slot directory. Cache disabled; erase slot before each request; no tools/web/repository access, target conversation history, slot restoration or prior answers. Native private reasoning remains private and non-authoritative.

Deterministic 36-call schedule, each endpoint exactly once. Six blocks of six each contain two historical-focus endpoints. Every sampled output combination appears in both halves. Nine pairs A-first and nine B-first. No adjacent matched endpoints. Schedule is frozen before inference and cannot depend on answers. Runner reports elapsed time and estimated remaining time only, permitting spaced status checks.

## Freeze, qualification, raw-first and publication

Generate and independently verify all states, field gold, pair deltas and freshness first. Commit Method Freeze (method, generator, auditor, scorer, schemas, tests and launch configuration), then Case Freeze (cases, requests, schedule, proofs and all hashes). Qualify the frozen transport afterward using synthetic mock replies only, with full schedule dispatch and failure paths; qualify scorer boundaries without model calls. Verify pinned hashes and zero-completion startup. Qualification evidence may be committed after Case Freeze; the launch guard permits only the three named qualification/runtime evidence files to change after that commit and verifies every frozen byte. No scientific cases or prompts may be adjusted in response to any model output.

One server, exactly 36 scientific requests, no retries, repairs or critics. Transport failure stops and invalidates an incomplete campaign; wrong or malformed answers remain data. No correctness inspection during execution. Preserve final strings verbatim, request/response hashes and safe metadata; private envelopes, reasoning and logs remain outside Git. After all calls, hash and make raw files read-only, COMMIT RAW BEFORE SCORING, then run the frozen scorer and zero-inference replay; require byte-identical output. Frozen scorer verifies exact raw-commit and scorer bytes.

Preserve all inherited files and prior heads, main, role/primitive/real-task/comparator studies, S/E, grounded state, Memory, policy and thresholds. Audit full reachable history and private artifacts. Publish only this new branch, verify the final remote SHA, report the hard-gate decision and STOP. No private archive, raw reasoning, credentials, signed streams or private databases are published.
