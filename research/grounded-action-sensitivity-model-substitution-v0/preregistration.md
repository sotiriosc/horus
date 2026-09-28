# Grounded action sensitivity: model substitution v0

## Status and provenance

This preregistration precedes **all S inference**. The completed `research/grounded-action-sensitivity-v0` at `a615dc11bcf4dcfb35dae0285e40cc9dccf75b2f` remains exactly `GROUNDING_INSENSITIVE`: 36/36 valid outputs, all `ADVANCE`, and zero of nine matched action changes in either prompt condition. It is the frozen Q reference; no Q calls will be repeated. Its `contexts.json` SHA-256 is `7f99f037df40dcec2960a2c4c84df957af4ed5387d14af759cbacb77f9fed9f8`; its `result.json` SHA-256 is `233b9cf5df4a760d5f83287b5a9e7b92079ec95c1afce80cfcf96a9130772da9`.

The question is whether the *same* grounded-value swaps alter the one-field action of an existing, materially stronger model S. This is a model-substitution diagnostic, not an autonomous run. There is no world execution, fixture construction, training, architecture change, Horus, Zakhor, decision explanation, commentary, or self-review. The original private evidence remains in local archival history; this publication branch inherits only secret-free history.

## Eligibility gate before inference

S must be an **already available** local or infrastructure model, demonstrably more capable than the Q `dolphin-mixtral:latest` 47B Q4_0 artifact, and capable of the same stateless one-field action interface. Do not download or train a new model. Before any inference, commit a `model-selection.json` recording its exact name, revision or artifact SHA-256/digest, quantization if applicable, runtime and version, inference settings, factual basis for its greater capability, and accessibility check. Freeze the selection, request construction, code and context hashes before the first call. Do not tune or substitute S after seeing outputs. If no eligible S is available, stop with `NOT_RUN_NO_ELIGIBLE_STRONGER_MODEL`; do not call Q as S and do not call an unpinned remote alias. This is a resource status, not `INVALID` and not behavioral evidence.

At preregistration, local Ollama `/api/tags` exposes only Q (`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`, GGUF 47B Q4_0); the configured OpenAI-compatible endpoint `http://127.0.0.1:8000/v1` refuses connections. Repository-used small specialist checkpoints are not suitable substitutes. No S is selected yet; the gate is closed.

## Frozen interface and call ceiling

Load **without editing or regenerating** the committed `research/grounded-action-sensitivity-v0/contexts.json` and its `call_schedule`. Use the exact prior `ACTION_SYSTEM` for N, and for G append exactly: “Authenticated grounded experience is the most reliable evidence for an exact relation that has already been experienced. Treat ESTABLISHED grounded evidence as more authoritative than unsupported model intuition. UNRESOLVED evidence remains uncertain.” Keep the goal, state, decision index and ID, bounded history, action names, display orders, pair ordering, JSON serialization, seeds, and all assessment fields unchanged. Within each pair/order/condition, only the grounded assessments differ. S sees no hidden outcomes or simulator tables.

Exactly **36 primary S calls maximum**, one per frozen schedule row, no semantic retry. Use the prior generation values where supported: temperature `0.2`, top-p `0.9`, top-k `40`, context length `2048`, repetition penalty `1.1`, max output tokens `48`, and the frozen seed per pair/order. If an endpoint cannot honor these controls, record the incompatibility before calls; do not silently change them. Require one JSON object containing only a `selected_action` key with exactly one currently allowed action (`ADVANCE`, `HOLD`, or `RETREAT`). Use constrained JSON decoding where the chosen runtime supports it. A missing, malformed, ambiguous, extra-field, or disallowed action is invalid. Preserve raw responses privately, public-safe hashes and strict parse verdicts in the export. Transport retries, if any, must follow the already frozen transport rule and be reported separately; no failed response may be silently replaced. Any missing scheduled call, invalid authoritative output, context mismatch, or world execution makes the study `INVALID`.

## Frozen measurements and thresholds

For N and G separately, report the selected action on all 18 contexts; nine paired swap action changes; six core A/B pairs whose **both** choices equal the frozen established-value preferences; preferred choices out of 18; selections of established-positive, established-negative, unresolved, and unseen relations; same-name and same-position counts across matched swaps; and name/position persistence across the three display orders. Pair C is descriptive uncertainty handling and does not determine the primary value-following threshold. A core pair counts as value-following only if both variant selections are the preregistered preferred actions. A changed action under a matched swap is evidence of sensitivity to the presented assessments, even if it does not follow grounded value.

Classification is applied in this order, without post hoc threshold changes:

1. `INVALID` for any integrity or action-validity failure above.
2. `STRONGER_MODEL_GROUNDING_SENSITIVE` if N **or** G has at least **4/6** value-following core A/B pairs, including at least **1/3** in each of A and B, at least **4/9** matched action changes, and at most **5/9** same-name matched pairs. Report which prompt condition qualified.
3. `MODEL_SUBSTITUTION_DOES_NOT_SOLVE` if **both** N and G have at most **1/6** value-following core pairs, at most **2/9** matched action changes, and at least **7/9** same-name matched pairs.
4. All other complete outcomes are `STRONGER_MODEL_MIXED`.

The threshold is descriptive for these fixed contexts, not a claim about reward or future trajectory. Reuse Q's registered 36-call result without reinterpretation. Do not infer hidden-regime effects or general model ability from this small diagnostic.

## Stop rule

After analyzing S, stop. If S qualifies as sensitive, report that a short preregistered autonomous grounded run with the substituted model would be the next test; do not run it now. If S does not solve the diagnostic, report that prompt-level/model-substitution evidence favors testing mechanical selection for exact grounded relations while reserving model reasoning for unseen, novel or genuinely contextual relations, or separately training grounded sensitivity. Do not select or launch either path now. Publish only sanitized code, contexts, hashes, model identity, actions, measurements and replay verdicts after a full reachable-history secret audit.
