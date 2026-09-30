# Horus Real Task v0 — Local Inference Runtime Optimization

REAL_TASK_INTEGRITY_ONLY

Execution, authenticated Memory and restart succeeded, but prospective experience-conditioned improvement and E-benefit gates failed. S+E cumulative consequence was -5 versus -10 for S-only and -1 for static HOLD. This descriptive five-point advantage does not satisfy the full E-benefit gate.

All 45 ordinary model selections were ADVANCE. E caused the three HOLD selections in arm A; the model subsequently continued selecting ADVANCE. RETREAT was never executed, so no campaign evidence establishes its outcomes. Exact-output hash mismatches caused all 22 integrity failures (A: 10; B: 12). Every final remained structurally valid and stopped normally; there were no OOM/resource/runtime failures. Faster timings on non-equivalent outputs are not useful latency improvement under the frozen rule.

A early-to-late cumulative consequence changed from -3 to -2, below the required +4 gain. Only one of four A profiles improved mean normalized latency by at least 10%, and one regressed by more than 10%. Static HOLD drift was approximately +0.89%, inside the frozen control band.

This is executed local inference work. All scientific decisions and raw evidence were frozen before analysis. Prior branches and the promoted selector source remain unchanged.

| Measure | S+E (A) | S-only (B) | Static HOLD (C) |
| --- | --- | --- | --- |
| decisions | 24 | 24 | 24 |
| consequence | -5 | -10 | -1 |
| valid | 14 | 12 | 24 |
| invalid | 10 | 12 | 0 |
| resource_failures | 0 | 0 | 0 |
| truncated | 0 | 0 | 0 |
| normalized_latency_mean | 0.9264682273346616 | 0.929343392852934 | 1.0106183924654017 |
| normalized_latency_median | 0.9157451161357377 | 0.9223570764107094 | 0.9965328877623185 |
| request_seconds_total | 51.2110354337492 | 49.970016974781174 | 54.67802350013517 |
| executor_seconds_total | 328.05588297895156 | 318.78572280996013 | 320.66819109703647 |
| policy_seconds_total | 715.2450235590804 | 825.4425666230964 | 0 |
| generation_tokens_per_second_mean | 64.88104452389824 | 62.55780267047284 | 60.560210821087104 |
| unique_action_context_relations | 7 | 4 | 4 |
| memory_admissions | 24 | 24 | 0 |
| E_acquisitions | 3 | 0 | 0 |
| S_escapes | 0 | 0 | 0 |
| grounded_mechanical | 0 | 0 | 0 |
| ordinary_model_decisions | 21 | 24 | 0 |

Outcome counts and route ownership:

```json
{
  "A": {
    "outcome_counts": {
      "-1": 12,
      "0": 5,
      "1": 7
    },
    "route_counts": {
      "EMPIRICAL_EVIDENCE_ACQUISITION": 3,
      "MODEL_FOR_UNRESOLVED": 17,
      "MODEL_FOR_UNSEEN": 4
    },
    "negative_repetitions": [
      2,
      3,
      6,
      8,
      9,
      11,
      12,
      13,
      15,
      16,
      17,
      18,
      19,
      21,
      22,
      24
    ]
  },
  "B": {
    "outcome_counts": {
      "-1": 13,
      "0": 8,
      "1": 3
    },
    "route_counts": {
      "MODEL_FOR_UNRESOLVED": 20,
      "MODEL_FOR_UNSEEN": 4
    },
    "negative_repetitions": [
      2,
      3,
      8,
      9,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24
    ]
  },
  "C": {
    "outcome_counts": {
      "-1": 2,
      "0": 21,
      "1": 1
    },
    "route_counts": {
      "STATIC_HOLD": 24
    },
    "negative_repetitions": [
      5,
      6,
      16,
      17,
      18
    ]
  }
}
```

## Prospectively registered gates

```json
{
  "experience_gate": {
    "A_all_valid": false,
    "aggregate_improves": false,
    "integrity": true,
    "late_consequence_gain_at_least_four": false,
    "later_action_changed_after_experience": true,
    "no_profile_regresses": false,
    "static_drift_control": true,
    "three_profiles_improve": false
  },
  "E_benefit_gate": {
    "E_acquisition": true,
    "consequence_advantage": true,
    "experience_gate": false,
    "invalid_no_worse": true,
    "latency_advantage": false,
    "three_profiles_no_worse": true
  },
  "static_late_early_ratio": 1.008856499364197,
  "A_improved_profiles": 1
}
```

No threshold, workload, action mapping or output validator was changed after Method Freeze. Static C has no policy or Memory; its target inference is engineering control work. Negative-action repetitions mean the same profile/action had a prior executed -1, not deterministic knowledge.

## Matched early/later workload profiles

| Arm/profile | Early consequence | Late consequence | Early normalized mean | Late normalized mean |
| --- | --- | --- | --- | --- |
| A/P0 | 1 | 1 | 0.9803280881716427 | 0.8450124056550008 |
| A/P1 | 1 | -1 | 0.8541580707391566 | 0.9558925796302487 |
| A/P2 | -2 | 0 | 0.9686201277333918 | 0.9227582874143699 |
| A/P3 | -3 | -2 | 0.9167381874434067 | 0.9682380718900753 |
| B/P0 | 0 | 2 | 1.0444493694230281 | 0.8803566319583762 |
| B/P1 | -1 | -1 | 0.9199114115380801 | 0.9225185901582791 |
| B/P2 | -2 | -2 | 0.9797922359995557 | 0.9136895569234252 |
| B/P3 | -3 | -3 | 0.9482513356499777 | 0.8257780111727496 |
| C/P0 | -1 | 0 | 1.0413822806467268 | 1.0789688040761822 |
| C/P1 | 0 | 0 | 0.9862834130748178 | 0.9866170897840717 |
| C/P2 | 0 | 0 | 0.9975011570899616 | 0.9994984361712754 |
| C/P3 | 0 | 0 | 0.9994845577296714 | 0.9952114011505078 |

## Exact repeated prompts

| Arm/workload | Early action | Late action | Early consequence | Late consequence | Early normalized | Late normalized |
| --- | --- | --- | --- | --- | --- | --- |
| A/P0-0 | ADVANCE | ADVANCE | -1 | 0 | 1.2529496324251375 | 0.9437464359928667 |
| A/P0-1 | ADVANCE | ADVANCE | 1 | 1 | 0.8417026349838707 | 0.6425984632574383 |
| A/P0-2 | ADVANCE | ADVANCE | 1 | 0 | 0.8463319971059201 | 0.9486923177146974 |
| A/P1-0 | ADVANCE | HOLD | 1 | -1 | 0.8342362418172041 | 1.1206609983952718 |
| A/P1-1 | ADVANCE | ADVANCE | 1 | 1 | 0.8211036939009093 | 0.8447230951482909 |
| A/P1-2 | ADVANCE | ADVANCE | -1 | -1 | 0.9071342764993564 | 0.9022936453471834 |
| A/P2-0 | ADVANCE | ADVANCE | -1 | -1 | 1.0855967810035947 | 0.9524425724743563 |
| A/P2-1 | ADVANCE | ADVANCE | 0 | 0 | 0.9089950960550017 | 0.9202217261298966 |
| A/P2-2 | ADVANCE | HOLD | -1 | 1 | 0.911268506141579 | 0.895610563638857 |
| A/P3-0 | ADVANCE | ADVANCE | -1 | -1 | 0.99003394420015 | 0.9676363625668175 |
| A/P3-1 | ADVANCE | ADVANCE | -1 | -1 | 0.9228136295328588 | 0.9208229266763844 |
| A/P3-2 | ADVANCE | HOLD | -1 | 0 | 0.8373669885972115 | 1.016254926427024 |
| B/P0-0 | ADVANCE | ADVANCE | 0 | 0 | 1.0159513869898125 | 0.9792484096833637 |
| B/P0-1 | ADVANCE | ADVANCE | -1 | 1 | 1.2269669267767522 | 0.8429033237641785 |
| B/P0-2 | ADVANCE | ADVANCE | 1 | 1 | 0.8904297945025198 | 0.8189181624275864 |
| B/P1-0 | ADVANCE | ADVANCE | 0 | 0 | 0.9338166938884465 | 0.9374382194125738 |
| B/P1-1 | ADVANCE | ADVANCE | 0 | 0 | 0.9317515693930873 | 0.9254292702708903 |
| B/P1-2 | ADVANCE | ADVANCE | -1 | -1 | 0.8941659713327064 | 0.9046882807913732 |
| B/P2-0 | ADVANCE | ADVANCE | -1 | -1 | 1.044680618283279 | 0.8990193517408427 |
| B/P2-1 | ADVANCE | ADVANCE | 0 | 0 | 0.9213663235694586 | 0.9187014897774726 |
| B/P2-2 | ADVANCE | ADVANCE | -1 | -1 | 0.9733297661459295 | 0.9233478292519604 |
| B/P3-0 | ADVANCE | ADVANCE | -1 | -1 | 0.9869779251465711 | 0.8754292992503324 |
| B/P3-1 | ADVANCE | ADVANCE | -1 | -1 | 0.9075875614567914 | 0.8122528448415475 |
| B/P3-2 | ADVANCE | ADVANCE | -1 | -1 | 0.9501885203465705 | 0.7896518894263689 |
| C/P0-0 | HOLD | HOLD | 0 | 0 | 0.9461986997977403 | 1.037224533455574 |
| C/P0-1 | HOLD | HOLD | 0 | -1 | 0.9854778554252787 | 1.3164260825276755 |
| C/P0-2 | HOLD | HOLD | -1 | 1 | 1.1924702867171615 | 0.883255796245297 |
| C/P1-0 | HOLD | HOLD | 0 | 0 | 1.0130681844488312 | 0.9958656298486337 |
| C/P1-1 | HOLD | HOLD | 0 | 0 | 0.9818176345837751 | 0.9546850898085792 |
| C/P1-2 | HOLD | HOLD | 0 | 0 | 0.9639644201918472 | 1.009300549695002 |
| C/P2-0 | HOLD | HOLD | 0 | 0 | 1.056020878888578 | 1.0283438301360428 |
| C/P2-1 | HOLD | HOLD | 0 | 0 | 1.018375506651488 | 0.987847445857806 |
| C/P2-2 | HOLD | HOLD | 0 | 0 | 0.9181070857298186 | 0.9823040325199773 |
| C/P3-0 | HOLD | HOLD | 0 | 0 | 1.0108155956194336 | 0.9972001456760033 |
| C/P3-1 | HOLD | HOLD | 0 | 0 | 1.0089337552351199 | 1.000307527719662 |
| C/P3-2 | HOLD | HOLD | 0 | 0 | 0.9787043223344607 | 0.9881265300558579 |

## Executed timeline

| Arm/index | Profile/workload | Action | Source | Consequence | Valid | Request seconds |
| --- | --- | --- | --- | --- | --- | --- |
| A/1 | P1/P1-2 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 1.6683712200028822 |
| A/2 | P1/P1-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 1.2370411930023693 |
| A/3 | P1/P1-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 1.7364331799908541 |
| A/4 | P0/P0-2 | ADVANCE | MODEL_FOR_UNSEEN | 1 | True | 0.19376358995214105 |
| A/5 | P0/P0-0 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | True | 0.23801797395572066 |
| A/6 | P0/P0-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 0.16983943100785837 |
| A/7 | P2/P2-0 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 2.6347524359589443 |
| A/8 | P2/P2-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 2.274256002972834 |
| A/9 | P2/P2-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 2.0481318929814734 |
| A/10 | P3/P3-0 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 4.436824696022086 |
| A/11 | P3/P3-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.105005802994128 |
| A/12 | P3/P3-1 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.45292004395742 |
| A/13 | P1/P1-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 1.6594684920273721 |
| A/14 | P1/P1-0 | HOLD | EMPIRICAL_EVIDENCE_ACQUISITION | -1 | True | 1.6617640770273283 |
| A/15 | P1/P1-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 1.7863824279629625 |
| A/16 | P0/P0-2 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 0.21719848696375266 |
| A/17 | P0/P0-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 0.17927984398556873 |
| A/18 | P0/P0-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 0.12966403196332976 |
| A/19 | P2/P2-0 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 2.3115860620164312 |
| A/20 | P2/P2-2 | HOLD | EMPIRICAL_EVIDENCE_ACQUISITION | 1 | True | 2.235178421018645 |
| A/21 | P2/P2-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 2.073427540017292 |
| A/22 | P3/P3-0 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.336450215021614 |
| A/23 | P3/P3-2 | HOLD | EMPIRICAL_EVIDENCE_ACQUISITION | 0 | True | 4.981964212958701 |
| A/24 | P3/P3-1 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.443314159987494 |
| B/1 | P1/P1-2 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 1.6445203440380283 |
| B/2 | P1/P1-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 1.3847033479833044 |
| B/3 | P1/P1-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 1.9704263330204412 |
| B/4 | P0/P0-2 | ADVANCE | MODEL_FOR_UNSEEN | 1 | True | 0.20385956595418975 |
| B/5 | P0/P0-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 0.1929963380098343 |
| B/6 | P0/P0-1 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | True | 0.24757836799835786 |
| B/7 | P2/P2-0 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 2.5354485679999925 |
| B/8 | P2/P2-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 2.4291425069677643 |
| B/9 | P2/P2-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 2.0760065270005725 |
| B/10 | P3/P3-0 | ADVANCE | MODEL_FOR_UNSEEN | -1 | False | 4.423129184986465 |
| B/11 | P3/P3-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.6580883209826425 |
| B/12 | P3/P3-1 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 4.3794485849794 |
| B/13 | P1/P1-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 1.663872625969816 |
| B/14 | P1/P1-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 1.3900735009810887 |
| B/15 | P1/P1-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 1.9570562190492637 |
| B/16 | P0/P0-2 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 0.18748732598032802 |
| B/17 | P0/P0-0 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 0.1860240160021931 |
| B/18 | P0/P0-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 1 | True | 0.170081706950441 |
| B/19 | P2/P2-0 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 2.1819274600129575 |
| B/20 | P2/P2-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 2.3044024119735695 |
| B/21 | P2/P2-1 | ADVANCE | MODEL_FOR_UNRESOLVED | 0 | True | 2.0700021699885838 |
| B/22 | P3/P3-0 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 3.923225417966023 |
| B/23 | P3/P3-2 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 3.8710931199602783 |
| B/24 | P3/P3-1 | ADVANCE | MODEL_FOR_UNRESOLVED | -1 | False | 3.919423010025639 |
| C/1 | P1/P1-2 | HOLD | STATIC_HOLD | 0 | True | 1.7728913319879211 |
| C/2 | P1/P1-0 | HOLD | STATIC_HOLD | 0 | True | 1.5022208490408957 |
| C/3 | P1/P1-1 | HOLD | STATIC_HOLD | 0 | True | 2.0763037970173173 |
| C/4 | P0/P0-2 | HOLD | STATIC_HOLD | -1 | True | 0.27301026601344347 |
| C/5 | P0/P0-0 | HOLD | STATIC_HOLD | 0 | True | 0.17974569101352245 |
| C/6 | P0/P0-1 | HOLD | STATIC_HOLD | 0 | True | 0.19885051000164822 |
| C/7 | P2/P2-0 | HOLD | STATIC_HOLD | 0 | True | 2.562971475010272 |
| C/8 | P2/P2-2 | HOLD | STATIC_HOLD | 0 | True | 2.2913230700069107 |
| C/9 | P2/P2-1 | HOLD | STATIC_HOLD | 0 | True | 2.2945859259925783 |
| C/10 | P3/P3-0 | HOLD | STATIC_HOLD | 0 | True | 4.529957406048197 |
| C/11 | P3/P3-2 | HOLD | STATIC_HOLD | 0 | True | 4.797880710975733 |
| C/12 | P3/P3-1 | HOLD | STATIC_HOLD | 0 | True | 4.868481779994909 |
| C/13 | P1/P1-2 | HOLD | STATIC_HOLD | 0 | True | 1.8562720349873416 |
| C/14 | P1/P1-0 | HOLD | STATIC_HOLD | 0 | True | 1.47671216505114 |
| C/15 | P1/P1-1 | HOLD | STATIC_HOLD | 0 | True | 2.0189251110423356 |
| C/16 | P0/P0-2 | HOLD | STATIC_HOLD | 1 | True | 0.20221711398335174 |
| C/17 | P0/P0-0 | HOLD | STATIC_HOLD | 0 | True | 0.1970375149976462 |
| C/18 | P0/P0-1 | HOLD | STATIC_HOLD | -1 | True | 0.26562950800871477 |
| C/19 | P2/P2-0 | HOLD | STATIC_HOLD | 0 | True | 2.495799046999309 |
| C/20 | P2/P2-2 | HOLD | STATIC_HOLD | 0 | True | 2.4515396149945445 |
| C/21 | P2/P2-1 | HOLD | STATIC_HOLD | 0 | True | 2.2258006319752894 |
| C/22 | P3/P3-0 | HOLD | STATIC_HOLD | 0 | True | 4.468939938000403 |
| C/23 | P3/P3-2 | HOLD | STATIC_HOLD | 0 | True | 4.844070993014611 |
| C/24 | P3/P3-1 | HOLD | STATIC_HOLD | 0 | True | 4.826857013977133 |

## Provenance, restart and ownership

Method Freeze `45981835d12a95a0044a270cb7cc31870f3d26b7`; Environment/Implementation Freeze `14cbcc1e12d7e1079b6e63e116b2507d403392cb`; raw pre-analysis `9cb640ffc64ad1e971ff4bde3852dcb1274b62d8`.

All 4562 inherited files, 153 local heads and 80 remote heads were preserved. Original HMAC streams, keys, databases, server logs and full model responses remain private; their hashes and safe original-event projections are published. All 48 Horus receipts passed authentication, measurement binding, original protected authorization and grounded-policy replay. Exact reconstruction covered all eight context sessions. See replay.json and publication-audit.json for scoring and ancestry checks.

Target requests use one fixed Qwen3-14B Q4_K_M artifact and fully GPU-resident llama.cpp configuration. The historical ordinary decision model remains Dolphin/Mixtral; no model selection or intelligence comparison occurred. All runtime tensors, context, cache, sampling, hardware and command pins appear in runtime-manifest.json. Engineering qualification used synthetic data only. HOLD references were established before the autonomous campaign and never entered policy Memory.

The apparatus optimizes warm HTTP request latency. It launches and warms servers and sometimes reloads the ordinary model between decisions. Executor and policy overhead can exceed saved inference time; this campaign does not establish production end-to-end economic benefit. Measurements include existing desktop background activity under the frozen admission limit; static controls constrain drift interpretation.

All runtime relations are empirical. S and grounded mechanical authority therefore retain their rules but may be ineligible; zero activations are not evidence those mechanisms would never matter in a different domain. Profile-partitioned durable sessions avoid fabricated context-transition receipts. Memory does not cross profile or arm boundaries. Exact prompt identities and unexecuted outcomes are absent from policy input.

Model outputs are model behavior; acquisition/authority/authorization/scoring are deterministic mechanisms; authenticated evidence changes available policy state; configuration latency is engineering performance. No source is credited with another component’s capability. No oracle grid, transfer cases, training, model promotion, policy change or follow-on study was performed.

## Required questions

1. **Did Horus successfully perform the real task?** The instrumented campaign completed 24 executed decisions per Horus arm, with 14/24 output-integrity successes for S+E and 12/24 for S-only. Each executed consequence was authenticated and admitted through the preserved boundary. Completion alone is not the growth result.

2. **Did authenticated consequences alter later decisions?** Yes for the 3 receipt-derived E acquisitions: the exact deterministic rule changed selection using prior authenticated events. Other model choices are conditioned on Memory, but their causal dependence is not isolated by a memory-ablation control.

3. **Did those changed decisions improve measured real-world performance?** No prospective experience-conditioned improvement gate passed. Any descriptive latency differences do not establish the requested growth claim.

4. **Did that improvement survive restart?** Durable state and policy-relevant reconstruction survived restart exactly; a performance improvement surviving restart was not established.

5. **Did promoted E improve performance beyond S-only rollback?** No. The frozen matched E-benefit gate did not pass; do not claim net E reward improvement.

6. **Was any improvement exact-context adaptation or bounded transfer?** Neither successful adaptation nor transfer was established. The design tested exact repeats only.

7. **Which component actually caused the improvement?** E caused all three action changes to HOLD from authenticated empirical history. All 45 ordinary model selections remained ADVANCE, including after negative experience. No component established the registered performance-improvement claim. Receipt execution, authentication, state derivation, E and scoring are deterministic software; no model learning was demonstrated.

8. **What concretely can Horus do now that it could not do before this campaign?** The new study adapter can execute a permitted local inference configuration, measure actual latency and output integrity, authenticate its realized consequence, store it durably and reconstruct policy state after restart. That new integration is engineering work; acquired optimization capability requires the separately reported improvement gate.

9. **What has NOT been demonstrated?** No weight learning, intelligence increase, RSI, recursive self-improvement, generalization, held-out transfer, global model/policy superiority, deployment readiness or automatic promotion. Warm-request latency does not imply lower total autonomous-system cost; model selection, loading and instrumentation overheads are reported separately.

10. **Is there enough evidence to justify a separately authorized next engineering change?** The result provides concrete implementation and failure evidence for a separately authorized engineering decision, but not evidence to promote E, replace a model or claim autonomous reward improvement.

