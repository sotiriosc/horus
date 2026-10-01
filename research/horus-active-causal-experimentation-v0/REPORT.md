# Horus Active Causal Experimentation v0 — protocol termination

**Classification: `ACTIVE_CAUSAL_STUDY_TERMINATED_INVALID_DISCOVERY_SELECTION`.** This is an interface/protocol failure, not a completed negative comparison of active and passive evidence acquisition. All three registered scientific gates are **not evaluable**.

The unchanged frozen runner stopped at `primary-002:A:discovery:7`. A0 returned a structurally valid probe using known actuators, but that probe was one of the machine's five sealed reservations and was absent from its 79-item allowed catalogue. The independent validator rejected it. The probe was not executed and its outcome was not exposed. The frozen method explicitly requires termination at an invalid discovery selection; there was no repair, retry, fallback, replacement query, or substituted policy.

## Preserved provenance

| Artifact | Commit |
|---|---|
| Exact published base | `0325e055f87e9dd24796aeb5d444dfc30b2dcbaa` |
| Prospective selection rules | `8ffee24b42d51f2a3fad8eea711fe98dda37d427` |
| Method Freeze | `6fba86981600cd1622343313c4c5daad41e6099a` |
| World/Data Freeze | `fcc62f20014dc354c8f0133e91a6a25c002a4754` |
| Partial raw evidence, before diagnostic analysis | `de596c5a037b4238a39d852066404b5a83f406b1` |

Branch: `research/horus-active-causal-experimentation-v0`.

A0 remained `Qwen/Qwen3-14B@231c69a380487f6c0e52d02dcf0d5456d1918201` plus temporal M1 adapter SHA256 `ba679e10cac31b5b17c8589c0740d74ac98c2db1882d7edd39419cb9110a0b01`. The failed causal C1 adapter was not used. Exact base-file hashes are in `identity-preflight.json`; loaded base and adapter fingerprints matched before inference.

Simulator/DSL identity: `411654e1b1d93d651e45bdca6933d53fb889ce4b0a36c64963f00ffd232f8c30`. Seeds: primary 851703; control 851704; planner 851705; engineering 715019. Neither frozen commit nor any file bound by the Method Freeze was altered.

## Planned and observed counts

| Item | Planned | Completed |
|---|---:|---:|
| Fully paired prediction machines | 120 | 1 |
| Passive primary discovery probes | 1,440 | 24 |
| Active primary discovery probes | 1,440 | 18 |
| Active primary selection calls | 1,440 | 19, including the rejected choice |
| Passive sealed predictions | 600 | 10 |
| Active sealed predictions | 600 | 5 |
| Control machines | 40 | 0 |
| All model calls including control | 3,760 | 34 |

The first machine completed both arms, including five predictions per arm. On the second machine, Passive completed twelve discovery probes and five sealed predictions; Active executed six probes before its seventh proposal triggered the stop. In total, 42 discovery probes were executed and 15 sealed predictions were preserved. The process exited as required after approximately 282 seconds, including model loading. There were no ambiguous incomplete model requests.

## Scientific outcomes

| Registered outcome | Status |
|---|---|
| `ACTIVE_CAUSAL_EVIDENCE_ACQUISITION_SUPPORTED` | Not evaluable: protocol terminated |
| `INFORMATIVE_EXPERIMENT_SELECTION_SUPPORTED` | Not evaluable: protocol terminated |
| `ACTIVE_DISCOVERY_CONTROL_BENEFIT_SUPPORTED` | Not evaluable: control not reached |
| Prediction exact/bit/step accuracy, errors and paired tests | Not estimated for the incomplete registered population |
| Learning curves, final hypothesis counts, information gain, probe ranks/regret and repetitions | Not estimated for the incomplete registered population |
| Control successes, action counts, prediction errors and paired test | Not evaluated |

We do not substitute a smaller posthoc population, select the one completed pair as a scientific comparison, or interpret unavailable gates as failed statistical tests. No scientific correctness or information-value scoring was performed. The partial raw evidence remains authenticated and available for integrity review.

Prospective qualification of all frozen worlds remains valid. The 600 reserved primary queries were constructed to make reset-state and constant last-observation persistence score exactly 0%, and to bound every actuator-independent common-trace predictor at 20%, below the registered 30% ceiling. These are pre-inference environment properties, not model-performance results. The oracle qualification identified every reserved query and achieved at least two bits of final uncertainty advantage over the fixed passive schedule on each admitted machine.

## Integrity and replay

The post-stop diagnostic analysis occurred only after the partial raw manifest was committed. The preserved Horus verifier authenticated the raw chain. Replay through the unchanged collector reproduced every signed record byte for byte, including the same terminal rejection, with zero new inference. Two independent diagnostic runs produced byte-identical reports. Every executed observation and ledger was reconstructed, all semantic messages matched, and the preserved HF template hashes, prompt-token counts and decoded generated tokens matched the recorded responses.

The attempted reservation violation did not become a leakage event: validation prevented execution, and the sealed outcome never entered discovery history. The model worker had no oracle or hidden-program interface. Its proposal alone did not authorize a prohibited experiment.

Raw model outputs, signed streams, authority keys, private world programs and model binaries remain local. The public report contains aggregate counts, artifact hashes, the failure category and verification code. Full reachable-history publication checks and prior-branch preservation checks accompany publication. No merge, promotion, parameter update, S/E modification, or model switch occurred.

## Required questions

1. **Did Active choose more informative experiments?** Not established; the registered comparison did not complete.
2. **Did it avoid already-resolved questions?** Not established; incomplete discovery is not used as a replacement evaluation.
3. **Did it deliberately test interactions, order or context more often?** Not established. Even a completed descriptive count would not by itself establish deliberateness.
4. **Did its evidence reduce uncertainty faster?** Not evaluated on the registered population.
5. **Did better evidence improve sealed prediction?** Not established; only one matched machine completed.
6. **Did it improve goal-directed control?** Not evaluated; no control machine ran.
7. **Were repeated experiments used intelligently?** Not established. The frozen deterministic-reset setting mathematically makes exact repeats uninformative after their first observation; no anti-repeat policy was added.
8. **Did the result survive persistence baselines?** The environment passed its prospective baseline qualification, but there is no completed scientific result to compare with those baselines.
9. **What exact capability is established?** This run verifies enforcement of the sealed-query boundary and authenticated fail-closed execution. It does not establish improved causal evidence acquisition.
10. **What is required before experiment-selection training is justified?** A separately registered study must first complete reliable legal-probe selection and demonstrate informative selection and predictive benefit under its prospective gates. This termination does not justify parameter training.

The active-causal study is terminal. Its frozen settings and evidence are preserved. The separately authorized triangulation study may begin only after this outcome has been published and the remote branch verified.
