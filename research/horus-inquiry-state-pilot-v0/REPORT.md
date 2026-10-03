# Horus Inquiry State Pilot v0

Diagnostic screening result: **INQUIRY_STATE_PILOT_SUPPORTS_CONFIRMATORY_PROPOSAL**. Recommend a separately authorized confirmatory proposal for Arm B.

All 384 scientific calls completed: 16 fresh matched worlds, A/B/C, six discovery probes and two sealed predictions per arm/world. No parameter learning, full Triangulation claim or larger study. The completed triangulation result at 50713caf9b95dadefbf3951ed892909e459effd0 is preserved unchanged.

A reproduces generic Active, including its existing repeat-count field. B adds tested/untried IDs, budget bookkeeping and the explicit deterministic-reset/no-new-evidence fact. C additionally exposes the complete syntactic contrast frontier. Repeats remain legal in all arms. No provisional model narratives are carried forward.

## Provenance and runtime

| Artifact | Identity |
| --- | --- |
| branch | `research/horus-inquiry-state-pilot-v0` |
| base_sha | `50713caf9b95dadefbf3951ed892909e459effd0` |
| selection_rules_commit | `e390a4c8669cd7bac23e24446f5f30aecc6cf4c7` |
| method_freeze_sha | `308c5b18687ff23afc5811dbb5c475beada97d72` |
| world_data_freeze_sha | `86e74f778fa3acb7cbf5acb6b3abd3283effd95e` |
| raw_pre_score_freeze_sha | `527375389aa03b722526da902f5fd469a0824a05` |
| private_raw_sha256 | `994eb3e5bfd220b6f43a158cbf031053570e98ff1a9f32ec1aebdccc20c1054a` |
| private_worlds_sha256 | `15968bc4707db0ae9f0f66a1eaf55e25d2d5e81b6be521d3844f37003387b942` |
| model_repository | `Qwen/Qwen3-14B` |
| model_revision | `231c69a380487f6c0e52d02dcf0d5456d1918201` |
| adapter_sha256 | `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01` |
| simulator_sha256 | `f6f1f9e0b89701bb2d7464259bbd24d392795d385d7963cb826502c081cd8101` |
| hypothesis_source_sha256 | `4abc58f56abf79a810d7ccd97b3ba1b123786e2cce0f468e277edacde153421e` |
| hypothesis_catalogue_sha256 | `5d82f1711b0fa14f84c9e10e5badb38c608184068c9bce6ff6a5fa168ccf491e` |
| collection_wall_seconds | `2308.198` |
| total_recorded_inference_seconds | `1997.9386069999996` |

Seeds: `{"engineering":100201,"runtime":20260930,"scientific_worlds":100203,"synthetic_context":100202}`. Population: `{"arms":3,"discovery_probes":6,"scientific_calls":384,"sealed_queries":2,"worlds":16}`. All model/base file hashes, runtime packages and post-run identity checks are preserved in the identity reports.

## Matched arm outcomes

| Arm | Repeats /96 | Zero-information /96 | Unique probes total | Mean information bits | Median final H | Median final log2 H | Useful contrasts | Short exact /32 | Bit accuracy | Mean rank | Mean regret bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 40 | 42 | 56 | 17.9703 | 20976.0 | 14.2605 | 2 | 0 | 0.6562 | 57.953 | 5.9688 |
| B | 0 | 8 | 96 | 24.0124 | 842.0 | 9.7086 | 11 | 1 | 0.6901 | 40.448 | 3.4457 |
| C | 0 | 9 | 96 | 24.1081 | 828.0 | 9.6811 | 14 | 1 | 0.6693 | 41.281 | 3.4352 |

| Arm | Time contrasts | Relation contrasts | Temporal cards added | Relational cards added | Model calls | Prompt tokens | Generated tokens | Recorded inference seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | 6 | 6 | 158 | 519 | 128 | 200499 | 3104 | 594.7 |
| B | 5 | 16 | 232 | 1113 | 128 | 247544 | 3104 | 680.5 |
| C | 5 | 20 | 232 | 1127 | 128 | 268656 | 3104 | 722.75 |

## Learning curves

| Arm | Probes | Median log2 H | Mean cumulative bits | Repeats | Zero-information | Useful contrasts |
| --- | --- | --- | --- | --- | --- | --- |
| A | 1 | 25.8318 | 7.3151 | 0 | 0 | 0 |
| A | 2 | 24.1158 | 9.7476 | 10 | 10 | 1 |
| A | 3 | 23.7832 | 11.2457 | 21 | 21 | 1 |
| A | 4 | 20.0562 | 12.9075 | 28 | 28 | 1 |
| A | 6 | 14.2605 | 17.9703 | 40 | 42 | 2 |
| B | 1 | 25.8318 | 7.3151 | 0 | 0 | 0 |
| B | 2 | 19.8747 | 13.0285 | 0 | 0 | 1 |
| B | 3 | 16.5304 | 17.3468 | 0 | 0 | 3 |
| B | 4 | 12.9558 | 20.5458 | 0 | 1 | 5 |
| B | 6 | 9.7086 | 24.0124 | 0 | 8 | 11 |
| C | 1 | 25.8318 | 7.3151 | 0 | 0 | 0 |
| C | 2 | 19.8747 | 12.8717 | 0 | 1 | 2 |
| C | 3 | 16.5304 | 17.2201 | 0 | 1 | 5 |
| C | 4 | 12.9558 | 20.8614 | 0 | 2 | 8 |
| C | 6 | 9.6811 | 24.1081 | 0 | 9 | 14 |

## Exact paired screening comparisons

| Comparison | Repeat ratio | Zero-information ratio | Median paired bits | Information wins/ties/losses | Useful contrasts/world advantage | Exact-prediction difference | Bit-accuracy difference |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B-A | 0.0 | 0.19047619047619047 | 6.3382 | 14/2/0 | 0.5625 | 1 | 0.03385416666666663 |
| C-A | 0.0 | 0.21428571428571427 | 6.5603 | 14/1/1 | 0.75 | 1 | 0.01302083333333337 |
| C-B | None | 1.125 | 0.0 | 3/10/3 | 0.1875 | 0 | -0.02083333333333326 |

Every one of the 16 paired per-world differences is published in results.json under paired_comparisons. No significance threshold or formal competence claim is used; these distributions are available for honest future power planning.

- B-A: PASS
- C-A: PASS
- C-B additional-frontier gate: FAIL — information_improved_at_least10worlds, median_information_advantage_at_least_half_bit, no_more_zero_information, prediction_bit_regression_at_most2pp, useful_contrast_advantage_at_least_quarter_per_world

The frozen screening conjunction requires A to exhibit at least 4 repeats, at least 50% fewer repeats, at least 25% and 4 fewer zero-information probes, at least 1 median paired bit of information advantage, gains on at least 10/16 worlds, at least 0.5 more useful contrasts/world, at most one lost exact prediction and at most 2 percentage points bit-accuracy regression, plus integrity. C-B uses a separate incremental gate: 0.5 bit, 10/16 worlds, 0.25 useful contrasts/world, no extra repeats/zero-information, and the same prediction/integrity bounds.

## Integrity

Raw evidence was committed before scientific scoring. Authentication, every exact prompt, structural-frontier reconstruction, legal token path, sealed query and executed ledger passed zero-inference replay. Two scoring passes produced byte-identical public results, private per-world results and per-decision contributions.

Replay: `{"byte_identical_artifacts_sha256":{"contribution-details.private.jsonl":"1b58dfbc2b98173e19d4b6ecf9c981800ee2189f8a4611fb39fae70b33f6915f","per-world-results.private.json":"1abcb018d5a64de7555553fe2d0bd0e43bd0b2c687ce6f018086f1bbe8b5be7b","results.json":"eb8e2a52eed70ba20b868cd7a7d6ba41949cf1be4989eecde9b53fe7b47038e2"},"new_inference_calls":0,"raw_freeze_sha":"527375389aa03b722526da902f5fd469a0824a05","status":"PASS"}`. Audits: `{"bookkeeping_and_frontier_reconstructed":true,"byte_identical_durable_execution_replay":true,"complete_population":true,"full_ledger_and_prompt_reconstruction":true,"legal_ID_support":true,"model_responses":384,"new_inference_calls":0,"no_reserved_probe_execution":true,"oracle_boundary":true,"prediction_shape_language":true,"receipt_authentication":true,"rendered_template_and_generated_tokens":true,"technical_interrupted_attempts":0}`. Preservation: `{"inherited_tracked_content_unchanged":true,"preceding_study_head":"50713caf9b95dadefbf3951ed892909e459effd0","prior_local_heads_unchanged":161,"prior_remote_heads_unchanged":88,"private_archive_heads_unreachable":15,"status":"PASS"}`. Full reachable-history publication auditing scans paths, actual key representations, credential patterns and private-evidence hashes. The operational process lock is not scientific evidence.

## Eight requested answers

1. **Did explicit bookkeeping stop repeated resolved experiments?** Repeat ratios versus A were {"B-A":0.0,"C-A":0.0}. A ratio<=0.5 is the frozen reduction criterion; stopping repeats entirely would require zero, not merely an improvement.

2. **Did fewer repeats actually produce more information?** Median paired information advantages were B-A 6.338166662962173 bits and C-A 6.560288957319127 bits. Wins/ties/losses and zero-information totals above distinguish repetition reduction from information benefit.

3. **Did the contrast frontier add value beyond bookkeeping?** The separate C-B incremental gate did not pass. This does not substitute for either intervention passing the A comparison.

4. **Did B/C preserve the earlier strong first 2–4-probe behavior?** The full paired pilot curves at 1/2/3/4/6 above show early and later information acquisition. This pilot uses fresh compatible worlds and a shorter budget; it cannot establish exact replication of the prior 12-probe trajectory. Exact H is monotone under authenticated observations; collapse refers to wasted later probes, not evaluator forgetting.

5. **Was the old collapse mainly caused by inquiry-state management?** This pilot cannot establish the main cause. B bundles bookkeeping with an explicit reset fact, A already carried repeat counts, and no arm carries prose hypotheses. Any positive result is evidence for the tested representation bundle, not a diagnosis of internal model state or an isolated narrative-fixation effect.

6. **Is there enough coherent evidence to justify a larger confirmatory study?** The frozen screening decision is yes, recommend a separately authorized confirmatory proposal.

7. **Which intervention should scale, if any?** Arm B under the frozen preference rule; no larger study has been launched.

8. **What remains unexplained if the screen is negative?** The failed conditions identify whether repeats, information, consistency, useful contrasts or prediction retention remain unresolved. This design cannot separate representation from instruction, test learned strategy changes, or prove a general causal account of exploration collapse. No replacement experiment follows automatically.

The 2 sealed queries per world provide only 32 exact endpoints per arm; the retention screen is not a powered noninferiority claim. The finite evaluator can judge contribution but never chooses the model action or supplies utility labels to it. No training, merge, promotion or automatic scale-up. STOP.
