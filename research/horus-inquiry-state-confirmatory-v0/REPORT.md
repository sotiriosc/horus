# Horus Inquiry State Confirmatory v0

**NEITHER_INTERVENTION_CONFIRMED**

All 1,968 scientific responses completed across 48 fresh matched worlds: eight discovery probes and three shared sealed predictions per arm. O adds 384 fresh interpretation calls. The pilot and earlier studies are preserved unchanged. No training, merge or automatic follow-up.

A is generic Active; B adds grounded bookkeeping and the deterministic-reset reminder; O adds a new model interpretation before each choice, reconstructed from the full authenticated ledger. Only the current interpretation enters that step. All interpretations remain unverified. The finite hypothesis evaluator, utility, candidate programs and sealed outcomes are hidden. Known actions and untried actions are explicitly not exhaustive reality.

## Provenance

| Artifact | Identity |
| --- | --- |
| branch | `research/horus-inquiry-state-confirmatory-v0` |
| base_sha | `dd681039bdd6e2c20837e1f5ac6cec7957ca35b3` |
| selection_rules_commit | `ba9b9eb57fd9a352eeeb5b69945198e5ff32e4ef` |
| method_freeze_sha | `d75213b535907fd8b1c1430913122f5413922c08` |
| world_data_freeze_sha | `a674e7523253c9fa09c497a1c7c9a673961f0c6c` |
| raw_pre_score_freeze_sha | `552b09bb425ca5d55d63218bae2cdaad5f4f6b4f` |
| private_raw_sha256 | `50c7533d3cf54fa18e8970cd71f80e5576441ff903cf2873e3c53f78b9c970ad` |
| private_worlds_sha256 | `661b19e41bdf56c87a80700f7377ec1bcc60f4bb67123d35ee554bc1aaeb66ca` |
| model_repository | `Qwen/Qwen3-14B` |
| model_revision | `231c69a380487f6c0e52d02dcf0d5456d1918201` |
| adapter_sha256 | `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01` |
| simulator_sha256 | `f6f1f9e0b89701bb2d7464259bbd24d392795d385d7963cb826502c081cd8101` |
| hypothesis_source_sha256 | `4abc58f56abf79a810d7ccd97b3ba1b123786e2cce0f468e277edacde153421e` |
| hypothesis_catalogue_sha256 | `5d82f1711b0fa14f84c9e10e5badb38c608184068c9bce6ff6a5fa168ccf491e` |
| seeds | `{'bootstrap_B_A': 100306, 'bootstrap_O_B': 100307, 'engineering': 100301, 'power': 100305, 'runtime': 20260930, 'scientific_worlds': 100303, 'synthetic_context': 100302}` |
| populations | `{'worlds': 48, 'arms': 3, 'discovery_probes': 8, 'sealed_queries': 3, 'scientific_calls': 1968}` |
| collection_wall_seconds | `13414.618` |
| total_recorded_inference_seconds | `12152.152776999992` |

Remote publication is verified in the private publication receipt; the containing Git commit identifies this report without a self-referential SHA.

## Matched outcomes

| Arm | Repeats /384 | Zero-info /384 | Unique total | Mean information bits | Median final H | Median log2 H | Mean uncertainty area | Useful contrasts | Exact /144 | Bit accuracy | Mean rank | Mean regret |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 74 | 111 | 310 | 24.6025 | 206.0 | 7.6864 | 16.949 | 22 | 2 | 0.66493 | 46.771 | 4.1902 |
| B | 5 | 64 | 379 | 26.4273 | 110.0 | 6.7811 | 14.7374 | 27 | 4 | 0.7037 | 39.475 | 3.0114 |
| O | 16 | 82 | 368 | 25.7323 | 144.0 | 7.1699 | 15.034 | 27 | 6 | 0.71759 | 42.238 | 3.1864 |

| Arm | Calls | Prompt tokens | Generated tokens | Inference seconds |
| --- | --- | --- | --- | --- |
| A | 528 | 888274 | 13488 | 2215.37 |
| B | 528 | 1072641 | 13488 | 2446.1 |
| O | 912 | 2175646 | 57464 | 7490.68 |

## Learning curves

| Arm | Probe | Median log2 H | Mean cumulative bits | Repeats | Zero-info | Useful contrasts |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1 | 24.5777 | 8.5795 | 0 | 0 | 0 |
| A | 2 | 22.6811 | 11.3386 | 23 | 24 | 0 |
| A | 3 | 18.1916 | 15.3129 | 38 | 40 | 0 |
| A | 4 | 14.197 | 18.1077 | 50 | 55 | 4 |
| A | 6 | 10.9421 | 22.0894 | 64 | 82 | 7 |
| A | 8 | 7.6864 | 24.6025 | 74 | 111 | 22 |
| B | 1 | 24.5777 | 8.5795 | 0 | 0 | 0 |
| B | 2 | 19.1682 | 14.0595 | 0 | 3 | 1 |
| B | 3 | 14.2216 | 18.6436 | 0 | 4 | 4 |
| B | 4 | 11.6013 | 21.4088 | 1 | 7 | 9 |
| B | 6 | 8.0194 | 24.612 | 3 | 29 | 16 |
| B | 8 | 6.7811 | 26.4273 | 5 | 64 | 27 |
| O | 1 | 24.5777 | 8.5795 | 0 | 0 | 0 |
| O | 2 | 19.379 | 13.6662 | 1 | 6 | 1 |
| O | 3 | 14.74 | 18.321 | 1 | 7 | 6 |
| O | 4 | 11.8738 | 21.2876 | 3 | 14 | 9 |
| O | 6 | 8.8661 | 24.3147 | 9 | 40 | 16 |
| O | 8 | 7.1699 | 25.7323 | 16 | 82 | 27 |

## Preregistered comparisons

| Comparison | Median paired bits | Mean bits/probe advantage | Wins/ties/losses | Information sign p | Area ratio | Area sign p | Zero-info ratio | Exact difference | Bit difference | 97.5% lower bit bound |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B-A | 0.0498 | 0.2281 | 24/23/1 | 7.748603820800781e-07 | 0.8695131238570404 | 1.4551915228366852e-11 | 0.5765765765765766 | 2 | 0.03877314814814815 | 0.013888888888888888 |
| O-B | 0.0 | -0.0869 | 1/28/19 | 0.9999990463256836 | 1.0201252640221983 | 0.9999947547912598 | 1.28125 | 2 | 0.013888888888888888 | -0.005208333333333333 |

**GROUNDED_INQUIRY_BOOKKEEPING_NOT_CONFIRMED**. Failed conditions: median_paired_information_at_least1bit, uncertainty_area_at_least15pct_lower.

**OPEN_INQUIRY_FRONTIER_NOT_SUPPORTED**. Failed conditions: all_frontier_schemas_valid, area_sign_p_below_025, information_sign_p_below_025, mean_information_per_probe_advantage_at_least_eighth_bit, median_paired_information_at_least_half_bit, question_linked_informative_fraction_exceeds_B_positive_fraction_by5pp, uncertainty_area_at_least5pct_lower, zero_information_at_least12_lower, zero_information_at_least20pct_lower.

The two claim families use alpha 0.025 each. Each claim requires its complete conjunction of exact paired sign tests, effect thresholds, retention and integrity; no metric can substitute for a failed gate. Bit noninferiority uses 100,000 paired world bootstrap samples and a two-percentage-point margin. Exact prediction count may not decline. Exact accuracy noninferiority is not a powered claim. All 48 paired differences are in results.json.

## O question accounting

| Measure | Count |
| --- | --- |
| already_observed_question_targets | 54 |
| fresh_interpretation_calls | 384 |
| generated_questions | 382 |
| invalid_frontier_schema | 2 |
| questions_finitely_ambiguous_at_generation | 226 |
| questions_followed_by_any_informative_execution | 300 |
| questions_followed_by_informative_target_execution | 288 |
| questions_followed_immediately_by_target_execution | 369 |
| questions_repeated_without_new_target_evidence | 2 |
| questions_unobserved_at_generation | 328 |
| unobserved_questions_later_answered_by_execution | 328 |
| valid_frontier_schema | 382 |

Question-linked informative fraction: 0.7539267015706806. B positive-experiment fraction: 0.8333333333333334. B does not generate questions; this comparison is the preregistered asymmetric behavioral benchmark, not a B question-resolution rate.

A scored question names a model-selected probe and sensor. Resolution requires later executed evidence containing that target trace, not an oracle answer. Prose is an unscored gloss. Repeated keyed questions without new target evidence measure persistence descriptively; they do not diagnose internal fixation. Finite H ambiguity can corroborate a limited uncertainty statement, never certify general open-world impossibility or exhaustive truth.

## Integrity

All raw responses were frozen and committed before scoring. Exact prompt/ledger reconstruction, authentication, legal-ID paths, sealed query boundaries and byte-identical scoring replay passed. Replay and scoring made zero model calls. The model receives only the current fresh interpretation; prior interpretation text is absent by construction and replay. Complete invalid frontier outputs are retained, never retried for scientific quality.

Audits: `{"bookkeeping_and_frontier_reconstructed":true,"byte_identical_durable_execution_replay":true,"complete_population":true,"full_ledger_and_prompt_reconstruction":true,"legal_ID_support":true,"model_responses":1968,"new_inference_calls":0,"no_reserved_probe_execution":true,"oracle_boundary":true,"prediction_shape_language":true,"receipt_authentication":true,"rendered_template_and_generated_tokens":true,"technical_interrupted_attempts":0}`. Replay: `{"byte_identical_artifacts_sha256":{"contribution-details.private.jsonl":"7f2a13b3fa598ff8de4b77cf6dc4d86d562415c41dca0756bb99ce1d60f72914","per-world-results.private.json":"2760a27a0c119dfbf4fc20df908f8785ea65ff7d81a10e6f247f05c9479de6b2","results.json":"93f1c398cbecae079bcc3f9ce0de46c81486006c640a64cacf9e9ab0a4408d8b"},"new_inference_calls":0,"raw_freeze_sha":"552b09bb425ca5d55d63218bae2cdaad5f4f6b4f","status":"PASS"}`. Preservation: `{"inherited_tracked_content_unchanged":true,"preceding_study_head":"dd681039bdd6e2c20837e1f5ac6cec7957ca35b3","prior_local_heads_unchanged":162,"prior_remote_heads_unchanged":89,"private_archive_heads_unreachable":15,"status":"PASS"}`.

## Ten requested answers

1. **Did B replicate the pilot?** GROUNDED_INQUIRY_BOOKKEEPING_NOT_CONFIRMED. The complete confirmatory gate is the governing result.

2. **Did bookkeeping prevent active-exploration collapse?** A/B repeats: 74/5; zero-information probes: 111/64. These describe wasted inquiry in this population, not a universal prevention claim.

3. **Did the information benefit survive to eight probes?** B-A median paired final information advantage: 0.0498 bits; exact sign p=7.748603820800781e-07. The full curves show early and final behavior.

4. **Did O generate useful unresolved questions from reality?** O generated 382 measurement-linked questions, of which 328 concerned traces not yet observed and 328 were later answered by executed evidence. This does not certify the associated prose.

5. **Did those questions lead to more informative experiments?** 288 generated questions were immediately followed by an informative execution covering their target. O-B mean information advantage per probe: -0.0869 bits. Association does not isolate causal influence from the extra inference call.

6. **Did O avoid treating previous hypotheses as truth?** Previous interpretations were never carried into later steps; all current interpretations were explicitly marked unverified. This verifies the context boundary, not the model’s internal beliefs. Repeated question counts remain a separate fixation diagnostic.

7. **Did O correctly retain uncertainty rather than force closure?** The explicit unresolved state was used 0 times; 0 coincided with finite-family ambiguity. This is scoped corroboration only. Neither absence nor presence of finite ambiguity establishes all open-world possibilities.

8. **Did O improve over B?** OPEN_INQUIRY_FRONTIER_NOT_SUPPORTED. No conceptual preference overrides that gate.

9. **What remains missing for genuinely open-world inquiry?** This still uses fixed sensors, reset dynamics and known interventions. It does not test discovering new instruments, expanding representations, open-ended causal explanations, calibrated impossibility judgments or environmental change. O also uses extra inference, so any benefit is for that bundle.

10. **Which piece is justified for integration review?** None. This is a result for separate integration review; no architecture, policy or parameters were changed.

STOP. No training, merge or subsequent study.
