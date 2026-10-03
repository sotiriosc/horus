# Horus Delta Prediction Pilot v0

**DELTA_PREDICTION_PILOT_NO_SCALE_UP**. Do not scale this intervention from this pilot.

All 544 scientific responses completed: 16 fresh matched worlds, six discovery probes and two shared sealed predictions per B/D/T arm, plus 160 fresh analyses before D/T decisions 2–6. The prior NEITHER_INTERVENTION_CONFIRMED result remains unchanged. No training, integration, merge or automatic follow-up.

B is grounded bookkeeping. D compares executed evidence, describes a provisional relation and predicts an untested case. T applies Time/Relation/Direction to that relation and extrapolation, including an explicit alternative outcome. Each fresh analysis enters only its own independent legal selector. Previous prose, proposals and receipt scores never enter later model contexts. INSUFFICIENT_DELTA is legitimate.

## Provenance

| Artifact | Identity |
| --- | --- |
| branch | `research/horus-delta-prediction-pilot-v0` |
| base_sha | `e3aefc6ea33395f7b8fd6dd0d57f7917d774c4ca` |
| selection_rules_commit | `c11cd57a86c465b89fd9a4a16f8dc10a2e4b066d` |
| method_freeze_sha | `2aaecdcbae9827f384607cb8c15c6b8976fef054` |
| world_data_freeze_sha | `231480337ff2b2e975e618dfa6f4b101473fb4ff` |
| raw_pre_score_freeze_sha | `8e2f17ac04ad2d89ce3d73c8a629a247d8c0f055` |
| private_raw_sha256 | `cb2808b757518e438f68a489eed4ae56a6905291d62859b4ddd74c734984b184` |
| private_worlds_sha256 | `384f9fdce34dfe75e92e97717f09d1dd067d5edc482a6f68e527f5e9bf9831d1` |
| model_repository | `Qwen/Qwen3-14B` |
| model_revision | `231c69a380487f6c0e52d02dcf0d5456d1918201` |
| adapter_sha256 | `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01` |
| simulator_sha256 | `f6f1f9e0b89701bb2d7464259bbd24d392795d385d7963cb826502c081cd8101` |
| hypothesis_source_sha256 | `4abc58f56abf79a810d7ccd97b3ba1b123786e2cce0f468e277edacde153421e` |
| hypothesis_catalogue_sha256 | `5d82f1711b0fa14f84c9e10e5badb38c608184068c9bce6ff6a5fa168ccf491e` |
| seeds | `{'engineering': 100401, 'runtime': 20260930, 'scientific_worlds': 100403, 'synthetic_context': 100402}` |
| populations | `{'worlds': 16, 'arms': 3, 'discovery_probes': 6, 'sealed_queries': 2, 'scientific_calls': 544}` |
| collection_wall_seconds | `6263.856` |
| total_recorded_inference_seconds | `5743.085143000002` |

The containing commit identifies the report; exact remote publication is verified in the private publication receipt.

## Matched outcomes

| Arm | Repeats /96 | Zero-info /96 | Unique probes | Mean information bits | Median final H | Median log2 H | Useful contrasts | Sealed exact /32 | Sealed bit accuracy | Mean rank | Mean regret |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B | 0 | 7 | 96 | 25.9925 | 79.0 | 6.2944 | 7 | 1 | 0.7135 | 38.417 | 3.101 |
| D | 0 | 7 | 96 | 25.4294 | 91.5 | 6.4421 | 10 | 1 | 0.7083 | 41.979 | 3.6065 |
| T | 0 | 6 | 96 | 25.753 | 104.0 | 6.6832 | 8 | 1 | 0.7083 | 40.521 | 3.4302 |

| Arm | Calls | Prompt tokens | Generated tokens | Inference seconds |
| --- | --- | --- | --- | --- |
| B | 128 | 254290 | 3104 | 554.51 |
| D | 208 | 498356 | 18004 | 2121.89 |
| T | 208 | 514771 | 27704 | 3066.68 |

## Learning curves

| Arm | Probe | Median log2 H | Mean cumulative bits | Repeats | Zero-info | Useful contrasts |
| --- | --- | --- | --- | --- | --- | --- |
| B | 1 | 24.26 | 8.6778 | 0 | 0 | 0 |
| B | 2 | 18.4634 | 15.3829 | 0 | 0 | 2 |
| B | 3 | 13.8911 | 18.9351 | 0 | 2 | 3 |
| B | 4 | 10.688 | 21.6005 | 0 | 2 | 5 |
| B | 6 | 6.2944 | 25.9925 | 0 | 7 | 7 |
| D | 1 | 24.26 | 8.6778 | 0 | 0 | 0 |
| D | 2 | 20.6154 | 13.9794 | 0 | 1 | 2 |
| D | 3 | 17.0951 | 16.8101 | 0 | 3 | 4 |
| D | 4 | 10.264 | 20.8331 | 0 | 3 | 6 |
| D | 6 | 6.4421 | 25.4294 | 0 | 7 | 10 |
| T | 1 | 24.26 | 8.6778 | 0 | 0 | 0 |
| T | 2 | 19.2304 | 14.7976 | 0 | 0 | 2 |
| T | 3 | 15.1597 | 18.1595 | 0 | 2 | 3 |
| T | 4 | 10.8648 | 21.4152 | 0 | 2 | 5 |
| T | 6 | 6.6832 | 25.753 | 0 | 6 | 8 |

## Paired screening

| Comparison | Median paired bits | Mean bits/probe advantage | Wins/ties/losses | Useful contrast advantage/world | Zero-info reduction | Sealed exact difference | Sealed bit difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D-B | 0.0 | -0.0938 | 3/6/7 | 0.1875 | 0 | 0 | -0.005208333333333259 |
| T-B | 0.0 | -0.0399 | 1/11/4 | 0.0625 | 1 | 0 | -0.005208333333333259 |
| T-D | 0.0 | 0.0539 | 4/8/4 | -0.125 | 1 | 0 | 0.0 |

- D-B: FAIL: at_least12_valid_evidence_linked_comparisons, information_improved_at_least10worlds, mean_information_per_probe_advantage_at_least_quarter_bit, median_paired_information_advantage_at_least1bit, prediction_linked_information_advantage_over_matched_B_at_least_quarter_bit, useful_contrast_advantage_at_least_half_per_world
- T-B: FAIL: at_least12_valid_evidence_linked_comparisons, information_improved_at_least10worlds, mean_information_per_probe_advantage_at_least_quarter_bit, median_paired_information_advantage_at_least1bit, prediction_linked_information_advantage_over_matched_B_at_least_quarter_bit, useful_contrast_advantage_at_least_half_per_world
- T-D additional benefit: FAIL: information_improved_at_least10worlds, mean_information_per_probe_advantage_at_least_twelfth_bit, median_paired_information_advantage_at_least_half_bit, useful_contrast_advantage_at_least_quarter_per_world

Every condition is mandatory. No formal competence or significance claim is made. All sixteen paired differences are available in results.json. T is recommended only if T-B and T-D both pass; otherwise D is preferred if D-B passes. Neither a conceptual preference nor one favorable metric can replace the gate.

## Prediction receipts and evidence fidelity

| Count | D | T |
| --- | --- | --- |
| alternative_supported | 0 | 0 |
| analysis_calls | 80 | 80 |
| contradictions_with_subsequent_decision | 62 | 64 |
| current_prediction_selected | 80 | 80 |
| endpoint_claims_match_executed_evidence | 18 | 14 |
| input_comparison_labels_valid | 39 | 44 |
| outcome_separated_primary_and_alternative | 0 | 0 |
| partially_matched | 78 | 80 |
| predictions_eventually_tested | 80 | 80 |
| predictions_generated | 80 | 80 |
| predictions_with_any_bit_contradiction | 78 | 80 |
| subsequent_prediction_available | 62 | 64 |
| subsequent_prediction_target_or_trace_changed | 62 | 64 |
| subsequent_selected_probe_changed | 62 | 64 |
| supported | 2 | 0 |
| tested_bits | 888 | 900 |
| tested_correct_bits | 499 | 491 |
| valid_analyses | 80 | 80 |
| valid_controlled_observed_endpoint_deltas | 2 | 3 |
| valid_evidence_linked_comparisons | 6 | 5 |

| Arm | Exact accuracy among tested | Bit accuracy among tested | Fraction selecting current prediction | Mean bits testing prediction | Mean bits ignoring a valid prediction | Mean paired B advantage on prediction-testing steps | Worlds testing predictions |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 0.025 | 0.5619369369369369 | 1.0 | 3.3503211365272554 | None | -0.11261129450469713 | 16 |
| T | 0.0 | 0.5455555555555556 | 1.0 | 3.4150244621241344 | None | -0.047907968907818864 | 16 |

Supported means all predicted bits matched; contradicted means none matched; partially matched means some but not all matched. Any-bit contradiction includes partial matches and is reported separately. Never-tested proposals receive no correctness credit. Only actual later execution of the exact predicted probe ID scores a receipt. T discrimination requires the executed full trace to match exactly one of two distinct forecasts. An outcome matching neither does not force a winner.

Evidence fidelity checks validate referenced executions, copied endpoints and input-comparison labels. They do not certify causal prose. Prediction-testing versus ignoring comparisons and later changes after contradiction are descriptive, with different selected cases and correlated receipts. The screening benchmark compares prediction-testing choices with B choices at the same world/step. B choices do not carry model predictions.

## Integrity and limitations

Complete raw evidence was committed before scoring. Authentication, ordered non-authoritative receipts, exact prompt/ledger reconstruction, public-only grammar validation, legal choices and sealing passed zero-inference replay. Two scoring passes were byte-identical.

Audits: `{"byte_identical_durable_execution_replay":true,"complete_population":true,"evidence_analysis_and_prediction_receipts_reconstructed":true,"full_ledger_and_prompt_reconstruction":true,"legal_ID_support":true,"model_responses":544,"new_inference_calls":0,"no_reserved_probe_execution":true,"oracle_boundary":true,"prediction_shape_language":true,"receipt_authentication":true,"rendered_template_and_generated_tokens":true,"technical_interrupted_attempts":0}`. Replay: `{"byte_identical_artifacts_sha256":{"contribution-details.private.jsonl":"fecd793bc80042505a65aafee2d429940431a3892b695070acc9828061133e47","per-world-results.private.json":"f96b37ba3812baafdbb0a61ba20c90dfdc3838238d2d2abf72e07dd9c34e179a","results.json":"cc5c1b8c03efb146cbbd50491d075ed5ffde0d100c5f6ee15fbe12b30b8dcf2c"},"new_inference_calls":0,"raw_freeze_sha":"8e2f17ac04ad2d89ce3d73c8a629a247d8c0f055","status":"PASS"}`. Preservation: `{"inherited_tracked_content_unchanged":true,"preceding_study_head":"e3aefc6ea33395f7b8fd6dd0d57f7917d774c4ca","prior_local_heads_unchanged":163,"prior_remote_heads_unchanged":90,"private_archive_heads_unreachable":15,"status":"PASS"}`.

The analysis grammar constrains only public references, JSON structure, trace dimensions, bounded ASCII prose and distinct alternatives. Every substantive choice and predicted bit remains model-generated. No hidden H, program list, best probe, utility or unexecuted world output enters the worker. D/T use extra inference versus B; T also uses a different prompt and explicit alternative forecast versus D. Results apply to these bundles. Fixed sensors/actions and finite machines do not establish unrestricted open-world inquiry.

## Ten requested answers

1. **Did comparing observations before selecting an experiment improve inquiry?** The D-B and T-B screening outcomes above govern the answer. Median paired information advantages are 0.0 and 0.0 bits respectively.

2. **Were meaningful deltas identified rather than unsupported relations invented?** Copied-endpoint accuracy, input-label validity and valid controlled endpoint differences are counted above. Those establish limited grounding; the causal relation prose itself is not certified.

3. **Did evidence-grounded relations produce testable predictions?** D generated 80 valid predictions and T generated 80. Their exact forecast and eventual-execution counts distinguish testability from correctness.

4. **Did prediction-testing experiments gain more information?** Both within-arm testing/ignoring means and matched B comparisons are reported above. Empty groups remain unmeasured; associations are not causal proof that the prose improved the choice.

5. **Did contradictions lead to different subsequent behavior?** The receipt counts report subsequent target/trace changes and selected-probe changes after any-bit contradiction. Previous proposals were not supplied again. These are observed changes, not proof of causal adaptation or effective falsification.

6. **Did D outperform bookkeeping B?** False under the complete frozen screening gate.

7. **Did prediction-stage Triangulation improve over D?** False under the separate T-D gate. Conceptual richness receives no credit.

8. **Did either method improve sealed prediction?** D-B exact/bit differences: 0/-0.005208333333333259; T-B: 0/-0.005208333333333259. Only 32 endpoints per arm; no powered prediction noninferiority claim.

9. **Did the mechanism operate without a complete hypothesis map?** No finite hypothesis catalogue or oracle value was model-visible. Whether the intervention helped is determined by the gates, and this fixed-action simulator still does not establish general open-world capability.

10. **Which piece deserves a larger confirmatory test?** Neither qualifies. The placement hypothesis is unsupported by this screening gate; stop.

STOP. No training, architecture integration, merge or automatic follow-up.
