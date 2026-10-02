# Horus Triangulation Learning v0

Classification: **TRIANGULATION_EVIDENCE_ACQUISITION_NOT_ESTABLISHED**. All 120 prediction worlds and 40 control worlds were completed with P/A/T, twelve discovery probes per arm, and 9,600 complete model responses. Results are bounded to the frozen family, model, prompts and budgets.

For control, the same frozen target was available before discovery to all arms. Passive remained independent of it. Observations alone changed the exact evaluator hypothesis set; model hypotheses never became authenticated truth.

## Provenance

| Artifact | Identity |
| --- | --- |
| branch | `research/horus-triangulation-learning-v0` |
| base_sha | `b4f195ff651fca5b31b2182aa4e56a6cfcd425ad` |
| design_commit | `f03613c19ac066056335b4125e478d3bf824d63b` |
| selection_rules_commit | `16088162e40c1160c8f0f6391950dae5d67307a5` |
| method_freeze_sha | `6ce7dd5065fe794e3044f391cd45d52ce43418c4` |
| world_data_freeze_sha | `41834a8a20be148711c8de5e2c6a719b0a6e473b` |
| raw_pre_score_freeze_sha | `a3cc82262d0d6b6d9f7ac49a1f0c96fb91191611` |
| private_raw_sha256 | `39bfbe67d173c3281466574bfb291bf1c5ced0867986ecb5d043682eea942cdd` |
| private_worlds_sha256 | `04a26dcc392f1e7a9e6f228ef6bc86e48589f87a875ea14a7bf3804516d687d6` |
| model_repository | `Qwen/Qwen3-14B` |
| model_revision | `231c69a380487f6c0e52d02dcf0d5456d1918201` |
| adapter_sha256 | `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01` |
| simulator_sha256 | `f6f1f9e0b89701bb2d7464259bbd24d392795d385d7963cb826502c081cd8101` |
| hypothesis_source_sha256 | `64a85782a9a5c36c98396afc43cce2d8f480d4993d10955be573cb2895e6f7ee` |
| hypothesis_catalogue_sha256 | `acb9a39f51525325216b20c16f275aee35b86be2db3ea1912236362e394d6fda` |

Seeds: `{"control":914072,"control_targets_and_candidates":914073,"engineering":817031,"primary":914071,"runtime":20260930}`. Populations: `{"arms":["P","A","T"],"control_worlds":40,"discovery_probes":12,"long_endpoints_per_arm":360,"long_lengths":[4,5,6],"long_queries_per_primary_world":3,"planned_model_calls":9600,"primary_worlds":120,"short_endpoints_per_arm":600,"short_queries_per_primary_world":5}`. All base shard/configuration hashes are in identity-preflight.json and post-run-identity.json.

## Predictions and control

| Arm | Short exact /600 | Long exact /360 | Control success /40 | Model calls | Inference seconds |
| --- | --- | --- | --- | --- | --- |
| P | 14 | 0 | 26 | 1280 | 8833.2 |
| A | 12 | 0 | 19 | 3200 | 14728.89 |
| T | 4 | 0 | 25 | 5120 | 56077.69 |

Full bit/step accuracy, confusion counts, error categories, baseline matches and model token costs are in results.json. Invalid traces receive zero credit; no prediction is repaired.

| Comparison | Short gain pp | Short paired p | Long gain pp | Long paired p | Median paired bits | Uncertainty area ratio | Control success gain | Control paired p |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-P | -0.333 | 0.7187957763671875 | 0.0 | 1.0 | -3.3389 | 0.926987640226941 | -7 | 0.18924713134765625 |
| T-A | -1.333 | 1.0 | 0.0 | 1.0 | 0.0 | 1.0237726633397228 | 6 | 0.2919921875 |
| T-P | -1.667 | 1.0 | 0.0 | 1.0 | -5.787 | 0.9490246053181403 | -1 | 1.0 |

Prediction inference uses exact whole-world paired sign flips. T-P/T-A p-values are Holm adjusted within each named prediction gate. Control uses two-sided exact paired McNemar and Holm for T comparisons. A-P values are unadjusted. Endpoint McNemar is descriptive only. Information uses a separate exact paired sign test.

## Learning and contribution

| Arm | Median final H | Mean bits/probe | Mean useful contrasts/world | Time contrasts | Relation contrasts | Zero-information probes | Exact repeats |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P | 6.5 | 2.5064 | 7.258333333333334 | 240 | 960 | 5 | 0 |
| A | 107.0 | 2.0806 | 0.48333333333333334 | 90 | 159 | 859 | 714 |
| T | 457.5 | 1.9222 | 0.6 | 128 | 232 | 872 | 717 |

| Probe count | P median log2 H | A median log2 H | T median log2 H | P unique fraction | A unique fraction | T unique fraction |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 33.3594 | 33.3594 | 33.3594 | 0.0 | 0.0 | 0.0 |
| 1 | 30.0944 | 24.1633 | 24.7377 | 0.0 | 0.0 | 0.0 |
| 2 | 27.1207 | 22.7813 | 20.8365 | 0.0 | 0.0 | 0.0 |
| 3 | 22.5512 | 18.8668 | 18.3769 | 0.0 | 0.0 | 0.0 |
| 4 | 20.9651 | 16.7943 | 16.7066 | 0.0 | 0.0 | 0.0 |
| 6 | 16.5402 | 13.2823 | 13.8855 | 0.0 | 0.0 | 0.0 |
| 8 | 12.5947 | 10.3458 | 12.0844 | 0.0 | 0.016666666666666666 | 0.016666666666666666 |
| 12 | 2.6962 | 6.7399 | 8.8359 | 0.0 | 0.05 | 0.09166666666666666 |

The full learning curves, abstract experiment-selection frequencies, legal-action ranks/regret, actuator costs, temporal/relational cards and control contribution metrics are in results.json. Every executed decision and all 79 evaluator probe values are preserved privately and committed by SHA256; they were never model-visible.

| Arm | Target information/probe | Target-zero-information fraction | Target propositions resolved/world | Successful control mean actions | Failed control probes |
| --- | --- | --- | --- | --- | --- |
| P | 0.025726331405545547 | 0.0625 | 7.2 | 6.8076923076923075 | 89 |
| A | 0.011463344567287651 | 0.7291666666666666 | 3.225 | 6.7894736842105265 | 108 |
| T | 0.00996046430998865 | 0.7645833333333333 | 2.475 | 7.44 | 97 |

Grounded T alternatives/falsifications: `{"control":{"favored_expectation_falsified":46,"parsed_alternatives":467,"viable_discriminating_alternatives":74},"primary":{"favored_expectation_falsified":133,"parsed_alternatives":1438,"viable_discriminating_alternatives":281}}`. These require opposite observable alternatives viable under pre-experiment H; prose does not establish a true explanation.

## Frozen gates

| Gate | Supported |
| --- | --- |
| ACTIVE_EVIDENCE_ACQUISITION_SUPPORTED | False |
| SHORT_TO_LONG_CAUSAL_EXTRAPOLATION_SUPPORTED | False |
| TRIANGULATION_CONTROL_BENEFIT_SUPPORTED | False |
| TRIANGULATION_EVIDENCE_ACQUISITION_SUPPORTED | False |
| TRIANGULATION_OVER_ACTIVE_SUPPORTED | False |

- ACTIVE_EVIDENCE_ACQUISITION_SUPPORTED: failed conditions: conditions.median_paired_bits_at_least_1, conditions.prediction_p_below_001, conditions.short_gain_at_least_48, conditions.smaller_H_at_least_78, conditions.uncertainty_area_at_most_90pct.
- SHORT_TO_LONG_CAUSAL_EXTRAPOLATION_SUPPORTED: failed conditions: common.T_exact_at_least_half, comparisons.T-A.exact_gain_at_least_29, comparisons.T-A.paired_holm_p_below_001, comparisons.T-P.exact_gain_at_least_29, comparisons.T-P.paired_holm_p_below_001.
- TRIANGULATION_CONTROL_BENEFIT_SUPPORTED: failed conditions: comparisons.T-A.paired_holm_p_below_005, comparisons.T-P.paired_holm_p_below_005, comparisons.T-P.success_gain_at_least_6.
- TRIANGULATION_EVIDENCE_ACQUISITION_SUPPORTED: failed conditions: common.T_useful_contrast_fraction_at_least_quarter, common.useful_contrast_advantage_at_least_1, comparisons.T-A.median_paired_bits_at_least_1, comparisons.T-A.paired_information_sign_p_below_001, comparisons.T-A.prediction_p_below_001, comparisons.T-A.short_gain_at_least_48, comparisons.T-A.smaller_H_at_least_78, comparisons.T-A.uncertainty_area_at_most_90pct, comparisons.T-P.median_paired_bits_at_least_1, comparisons.T-P.paired_information_sign_p_below_001, comparisons.T-P.prediction_p_below_001, comparisons.T-P.short_gain_at_least_48, comparisons.T-P.smaller_H_at_least_78, comparisons.T-P.uncertainty_area_at_most_90pct.
- TRIANGULATION_OVER_ACTIVE_SUPPORTED: failed conditions: conditions.T_useful_contrast_fraction_at_least_quarter, conditions.median_paired_bits_at_least_1, conditions.paired_information_sign_p_below_001, conditions.prediction_p_below_001, conditions.short_gain_at_least_48, conditions.smaller_H_at_least_78, conditions.uncertainty_area_at_most_90pct, conditions.useful_contrast_advantage_at_least_1.

The 120/40 populations were retained prospectively. Power planning did not guarantee the conjunction of all demanding gates, especially small or strongly correlated effects. Failed gates mean the corresponding bounded claim was not established.

## Integrity and preservation

Raw evidence was committed before scoring. Zero-inference collector reconstruction checked every prompt, rendered template, generated token path, legal selection, receipt, complete ledger and control execution. Two scoring runs produced byte-identical results, per-world results and per-decision contributions. Replay receipt: `{"byte_identical_artifacts_sha256":{"contribution-details.private.jsonl":"28acbd49a4d91fd38ac7b3c2051aadc53d55d148ee42fb50f738075bfc97a477","per-world-results.private.json":"34f83c679156bab66d50c3c9c8b5a77c2eb09b6dd6d7d814e80565cbdc30cd2f","results.json":"79c979fe5ef32f95c60715bab0453e38c9ecfd69d5ebdcba23fffe86e68a0f14"},"new_inference_calls":0,"raw_freeze_sha":"a3cc82262d0d6b6d9f7ac49a1f0c96fb91191611","status":"PASS"}`.

Persistence references: `{"long":{"A":{"last_observation":{"accuracy":0.0,"endpoints":360,"exact":0},"marginal":{"accuracy":0.0,"endpoints":360,"exact":0},"repeat_last_probe":{"accuracy":0.0,"endpoints":360,"exact":0},"reset":{"accuracy":0.0,"endpoints":360,"exact":0}},"P":{"last_observation":{"accuracy":0.0,"endpoints":360,"exact":0},"marginal":{"accuracy":0.0,"endpoints":360,"exact":0},"repeat_last_probe":{"accuracy":0.0,"endpoints":360,"exact":0},"reset":{"accuracy":0.0,"endpoints":360,"exact":0}},"T":{"last_observation":{"accuracy":0.0,"endpoints":360,"exact":0},"marginal":{"accuracy":0.0,"endpoints":360,"exact":0},"repeat_last_probe":{"accuracy":0.0,"endpoints":360,"exact":0},"reset":{"accuracy":0.0,"endpoints":360,"exact":0}}},"short":{"A":{"last_observation":{"accuracy":0.0,"endpoints":600,"exact":0},"marginal":{"accuracy":0.0016666666666666668,"endpoints":600,"exact":1},"repeat_last_probe":{"accuracy":0.006666666666666667,"endpoints":600,"exact":4},"reset":{"accuracy":0.0,"endpoints":600,"exact":0}},"P":{"last_observation":{"accuracy":0.0,"endpoints":600,"exact":0},"marginal":{"accuracy":0.0,"endpoints":600,"exact":0},"repeat_last_probe":{"accuracy":0.0016666666666666668,"endpoints":600,"exact":1},"reset":{"accuracy":0.0,"endpoints":600,"exact":0}},"T":{"last_observation":{"accuracy":0.0,"endpoints":600,"exact":0},"marginal":{"accuracy":0.0,"endpoints":600,"exact":0},"repeat_last_probe":{"accuracy":0.0033333333333333335,"endpoints":600,"exact":2},"reset":{"accuracy":0.0,"endpoints":600,"exact":0}}}}`. Short common-trace qualification capped accuracy at20%; constant persistence at0%. Long traces exclude all period1–3 repeats and holding the third-step estimate. Registered ceiling is30%.

Audits: `{"byte_identical_durable_execution_replay":true,"complete_population":true,"full_ledger_and_prompt_reconstruction":true,"legal_ID_support":true,"model_responses":9600,"new_inference_calls":0,"no_reserved_probe_execution":true,"oracle_boundary":true,"prediction_shape_language":true,"receipt_authentication":true,"rendered_template_and_generated_tokens":true,"target_before_control_discovery":true,"technical_interrupted_attempts":3}`. Preservation: `{"inherited_tracked_content_unchanged":true,"preceding_study_head":"b4f195ff651fca5b31b2182aa4e56a6cfcd425ad","prior_local_heads_unchanged":160,"prior_remote_heads_unchanged":87,"private_archive_heads_unreachable":15,"status":"PASS"}`. Publication scans every reachable commit/path and unique blob, unchanged credential rules, actual authority-key representations and private file hashes. Private archives, model/reasoning outputs, raw signed streams, keys, hidden programs and databases are not publication artifacts. Exact pushed-head verification is kept in the private publication receipt.

## Requested interpretation

1. **Does choosing experiments actively beat passive observation?** The registered A-P evidence gate did not pass; the full bounded claim is not established.

2. **Does Triangulation beat generic active exploration?** The registered T-A gate did not pass.

3. **Does Time constrain later experimentation?** The temporal cards and time-contrast counts measure compatible distinctions acquired. This three-arm design does not isolate the causal effect of the Time instruction; no axis ablation was run.

4. **Do Relation contrasts expose conditional interactions?** Observed endpoint deltas and additional H-entailed relation cards are measured. They support only the tested contexts and finite family, not a global causal rule.

5. **Does Direction reduce irrelevant experimentation?** Known-target mutual information and target-zero-information fractions above measure destination relevance. Any arm difference is descriptive for the whole method; the Direction axis was not separately randomized.

6. **Does T preferentially choose controlled contrasts?** T minus A useful contrasts per primary world = 0.11666666666666664. T useful fraction = 0.05. These are executed structural comparisons.

7. **Does T seek falsification rather than confirmation?** The grounded alternative/falsification counts above test observable predictions, not intent. P/A did not emit comparable analysis, so no between-arm claim about falsification intent is justified.

8. **Does T reduce uncertainty faster per executed experiment?** T/P and T/A normalized area ratios are 0.9490246053181403 and 1.0237726633397228. Values below1 describe faster average reduction; the registered threshold is0.90 together with paired final-information conditions.

9. **Can short experiments support unseen longer sequences?** The separate short-to-long gate did not pass.

10. **Does better experimentation improve control?** The separate matched control-benefit gate did not pass.

11. **Which capabilities came from the model and deterministic machinery?** The model generated hypotheses, selected legal IDs and predicted sensor bits. Deterministic code restricted syntax/action availability, executed machines, authenticated observations, planned from model predictions, and evaluated exact H, contribution and significance. The evaluator never selected A/T discovery experiments.

12. **Does this justify a separate experiment-selection learning study?** This study does not establish the primary prerequisite for an automatic learning progression. Any future diagnostic or learning study needs its own justification and authorization.

13. **What remains before bounded recursive self-improvement?** A separately frozen learning intervention, authenticated training evidence, improved selection on genuinely new worlds, efficient repeated improvement, independent replication and preservation of safety/authority boundaries remain untested.

T received an additional analysis call per discovery step. Results compare complete method bundles and do not isolate framing from extra reasoning compute. No weights were updated. No RSI, consciousness, general causal intelligence or universal truth-discovery claim follows. No merge, promotion or subsequent study. STOP.
