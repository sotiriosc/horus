# Qwen Role-Grounded Temporal Reduction v0 — completed report

Registered interpretation: **ROLE_GROUNDING_NOT_ESTABLISHED**. Primary Arm C gate: **FAIL**. Generic Arm B descriptive indicator: **FAIL**.

Ninety scheduled / attempted / completed calls; **30 matched semantic units**, not 90 independent observations. Every state, class definition and non-instruction parameter is identical across its three arms. Only the frozen system instruction changes.

Neither role arm improves aggregate or historical accuracy. A scores 24/30 (T 2/6), B 22/30 (T 1/6), and C 21/30 (T 1/6). Relative to A, C repairs one historical state but regresses four states overall: two historical and two current-defect states. C current-defect accuracy falls from 5/6 to 3/6. Only the stable-pair condition passes among the six primary conditions. This is not the registered historical-gain tradeoff pattern: there is no net historical gain.

## Provenance

- Branch: `research/qwen-role-grounded-temporal-reduction-v0`
- Verified base: `01112fa7770ae885418d20e91a3227e15a8c3ba3`
- Method Freeze: `39934eaf6f14f581089b24f882c2ce57420a6dd9`
- Case Freeze: `3855137cc51f1b178c50f2672404410ba460914f`
- Raw pre-scoring: `f726051278be94ff94b3efe371414b71afb322a9`
- Publication SHA: verified remote branch head reported in the final handoff; this document cannot contain its own commit SHA.
- New seed: `1846059237`
- Qwen3-14B Q4_K_M SHA256: `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`
- llama.cpp b11242 commit: `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`
- Runtime executable SHA256: `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`

Context 16384; one slot; f16 KV; flash attention on; reasoning enabled / DeepSeek / budget 512; temperature .2, top_p .9, top_k 40, min_p .05, max_tokens 2048. Cache disabled and slot erased before every call. All 41 offloadable layers on the RTX 4090; original CPU-mapped embedding allocation retained. Same configuration and seed across arms. Native reasoning remains private and non-authoritative.

## Arm outcomes

| Arm | Exact accuracy | Schema-valid | Historical | Non-historical | Changing pairs | Stable pairs |
|---|---:|---:|---:|---:|---:|---:|
| A | 24/30 | 30/30 | 2/6 | 22/24 | 2/5 | 2/3 |
| B | 22/30 | 30/30 | 1/6 | 21/24 | 1/5 | 2/3 |
| C | 21/30 | 30/30 | 1/6 | 20/24 | 1/5 | 2/3 |

| Class | A | B | C |
|---|---:|---:|---:|
| SUPPORTED_CURRENT_DEFECT | 5/6 | 4/6 | 3/6 |
| NO_SUPPORTED_DIAGNOSIS | 5/6 | 5/6 | 5/6 |
| INSUFFICIENT_EVIDENCE | 6/6 | 6/6 | 6/6 |
| HISTORICAL_DEFECT_NOT_CURRENT | 2/6 | 1/6 | 1/6 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 6/6 | 6/6 | 6/6 |

Matrices: rows gold, columns selected. D=current defect, N=no diagnosis, U=insufficient, T=historical, X=contradictory.

### Arm A confusion

| Gold / selected | D | N | U | T | X | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| D | 5 | 0 | 1 | 0 | 0 | 0 |
| N | 0 | 5 | 1 | 0 | 0 | 0 |
| U | 0 | 0 | 6 | 0 | 0 | 0 |
| T | 0 | 3 | 1 | 2 | 0 | 0 |
| X | 0 | 0 | 0 | 0 | 6 | 0 |

### Arm B confusion

| Gold / selected | D | N | U | T | X | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| D | 4 | 0 | 2 | 0 | 0 | 0 |
| N | 0 | 5 | 1 | 0 | 0 | 0 |
| U | 0 | 0 | 6 | 0 | 0 | 0 |
| T | 0 | 4 | 1 | 1 | 0 | 0 |
| X | 0 | 0 | 0 | 0 | 6 | 0 |

### Arm C confusion

| Gold / selected | D | N | U | T | X | Invalid |
|---|---:|---:|---:|---:|---:|---:|
| D | 3 | 0 | 3 | 0 | 0 | 0 |
| N | 0 | 5 | 0 | 1 | 0 | 0 |
| U | 0 | 0 | 6 | 0 | 0 | 0 |
| T | 0 | 5 | 0 | 1 | 0 | 0 |
| X | 0 | 0 | 0 | 0 | 6 | 0 |

## Frozen gate assessment

| Condition | Observed | Pass |
|---|---|---|
| historical_at_least_5 | 1/6 | False |
| historical_gain_at_least_2 | -1 states | False |
| overall_at_least_26 | 21/30 | False |
| each_nonhistorical_at_least_5 | D 3/6, N 5/6, U 6/6, X 6/6 | False |
| changing_at_least_4 | 1/5 | False |
| stable_at_least_2 | 2/3 | True |

Generic B historical gain: -1; indicator: False. Tradeoff arms: []. Partial improvement without primary pass: False.

Bare-control replication-difference flag: False. Previous reduction study: 43/50 overall, T 5/10. New A: 24/30 overall; T 2/6; non-T 22/24. These are fresh cases with multiple older trials, not the same benchmark. No causal cross-dataset improvement percentage is computed. A strong bare arm cannot be credited to grounding; a ceiling does not relax the required two-state gain.

## Temporal pairs and stable controls

Five changing pairs and three stable pairs. rt-p01 and rt-p04 share one historical endpoint; pair observations are dependent. Every declared delta is one primitive field, with no coupled changes.

| Pair | Gold A→B | Changing? | Arm A selected; pass | Arm B selected; pass | Arm C selected; pass |
|---|---|---|---|---|---|
| rt-p01 | N→T | True | N→T; True | N→N; False | N→N; False |
| rt-p02 | D→T | True | D→N; False | D→T; True | U→N; False |
| rt-p03 | T→U | True | U→U; False | N→U; False | T→U; True |
| rt-p04 | T→X | True | T→X; True | N→X; False | N→X; False |
| rt-p05 | N→T | True | U→N; False | N→U; False | T→N; False |
| rt-p06 | T→T | False | N→T; False | N→N; False | N→N; False |
| rt-p07 | X→X | False | X→X; True | X→X; True | X→X; True |
| rt-p08 | U→U | False | U→U; True | U→U; True | U→U; True |

## Exact three-arm semantic-state table

Correctness uses 1=correct, 0=incorrect in A/B/C order. The full class-name outputs are also retained in scores.json.

| State | Gold | A | B | C | Correct A/B/C | C regression |
|---|---|---|---|---|---|---|
| rt-v0-1cc44ec3288a7e | N | N | N | N | 111 | False |
| rt-v0-2dc375f671f278 | T | T | N | N | 100 | True |
| rt-v0-9eb8892011584b | D | D | D | U | 110 | True |
| rt-v0-c1506b1fe9703e | T | N | T | N | 010 | True |
| rt-v0-fd5fadc4e925f7 | T | U | N | T | 001 | False |
| rt-v0-af729fc63d0636 | U | U | U | U | 111 | False |
| rt-v0-e0a6ac9ed94a7b | X | X | X | X | 111 | False |
| rt-v0-bccf6a7602a8fa | N | U | N | T | 010 | True |
| rt-v0-a0a4a90564473d | T | N | U | N | 000 | False |
| rt-v0-38289da8e4a7e5 | T | N | N | N | 000 | False |
| rt-v0-874117a61d630b | T | T | N | N | 100 | True |
| rt-v0-f13e7880c44234 | X | X | X | X | 111 | False |
| rt-v0-40eaf1b673d172 | X | X | X | X | 111 | False |
| rt-v0-83991af78d099d | U | U | U | U | 111 | False |
| rt-v0-10e9b16d45b619 | U | U | U | U | 111 | False |
| rt-v0-451f83c73053da | X | X | X | X | 111 | False |
| rt-v0-858d5ad79018d9 | X | X | X | X | 111 | False |
| rt-v0-6621f29d4d885d | D | D | D | D | 111 | False |
| rt-v0-682820e53475e2 | D | D | U | D | 101 | False |
| rt-v0-c75015bbb376ed | U | U | U | U | 111 | False |
| rt-v0-5c0d14b3113e18 | U | U | U | U | 111 | False |
| rt-v0-bf02ae88ee745f | X | X | X | X | 111 | False |
| rt-v0-b83de2a456510a | D | U | U | U | 000 | False |
| rt-v0-0d9cb793780de4 | N | N | N | N | 111 | False |
| rt-v0-ec383ba1726b60 | U | U | U | U | 111 | False |
| rt-v0-6e74c48cbe02f8 | D | D | D | U | 110 | True |
| rt-v0-a97885b7c98c6e | D | D | D | D | 111 | False |
| rt-v0-a3e970ac987a74 | N | N | N | N | 111 | False |
| rt-v0-b4d4f79c7ae2dc | N | N | N | N | 111 | False |
| rt-v0-0ef72b75ab0cd3 | N | N | U | N | 101 | False |

### Correctness transitions

| Pattern A/B/C | Meaning | States |
|---|---|---:|
| 000 | wrong → wrong → wrong | 3 |
| 001 | wrong → wrong → correct | 1 |
| 010 | wrong → correct → wrong | 2 |
| 011 | wrong → correct → correct | 0 |
| 100 | correct → wrong → wrong | 2 |
| 101 | correct → wrong → correct | 2 |
| 110 | correct → correct → wrong | 2 |
| 111 | correct → correct → correct | 18 |

### Paired repairs and regressions

| Contrast | Subset | N | Wrong→correct | Correct→wrong | Both correct | Both wrong |
|---|---|---:|---:|---:|---:|---:|
| A→B | all | 30 | 2 | 4 | 20 | 4 |
| A→B | historical | 6 | 1 | 2 | 0 | 3 |
| A→B | non_historical | 24 | 1 | 2 | 20 | 1 |
| A→B | explicit_noncurrent_mismatch | 22 | 2 | 3 | 13 | 4 |
| A→B | no_explicit_noncurrent_mismatch | 8 | 0 | 1 | 7 | 0 |
| B→C | all | 30 | 3 | 4 | 18 | 5 |
| B→C | historical | 6 | 1 | 1 | 0 | 4 |
| B→C | non_historical | 24 | 2 | 3 | 18 | 1 |
| B→C | explicit_noncurrent_mismatch | 22 | 2 | 4 | 11 | 5 |
| B→C | no_explicit_noncurrent_mismatch | 8 | 1 | 0 | 7 | 0 |
| A→C | all | 30 | 1 | 4 | 20 | 5 |
| A→C | historical | 6 | 1 | 2 | 0 | 3 |
| A→C | non_historical | 24 | 0 | 2 | 20 | 2 |
| A→C | explicit_noncurrent_mismatch | 22 | 1 | 4 | 12 | 5 |
| A→C | no_explicit_noncurrent_mismatch | 8 | 0 | 0 | 8 | 0 |

All six historical gold states contain an explicit non-current MISMATCH: this follows the representation of a demonstrated older violation. Therefore historical gains cannot independently identify whether that lexical/primitive feature drives the response. The broader mismatch-present and mismatch-absent subsets above show where repairs and regressions occur, without claiming a controlled feature effect.

## Exact historical temporal primitive facts

### rt-v0-2dc375f671f278

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": true,
    "equal_value": true,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "KNOWN",
    "alternative_completion": "NO_ALTERNATIVE",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    }
  ]
}
```

### rt-v0-c1506b1fe9703e

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": false,
    "equal_value": false,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "UNKNOWN",
    "alternative_completion": "ALTERNATIVE_EXISTS",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    }
  ]
}
```

### rt-v0-fd5fadc4e925f7

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": false,
    "equal_value": true,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "UNKNOWN",
    "alternative_completion": "ALTERNATIVE_EXISTS",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "UNDERDETERMINED"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    }
  ]
}
```

### rt-v0-a0a4a90564473d

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": true,
    "equal_value": true,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "UNKNOWN",
    "alternative_completion": "ALTERNATIVE_EXISTS",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    }
  ]
}
```

### rt-v0-38289da8e4a7e5

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": false,
    "equal_value": true,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "KNOWN",
    "alternative_completion": "NO_ALTERNATIVE",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "UNDERDETERMINED"
    }
  ]
}
```

### rt-v0-874117a61d630b

```json
{
  "proposition_scope": {
    "package": "The two mark assertions are independent of trial inputs. same_referent compares their immutable subjects; equal_value compares their asserted values. consistency is the already-resolved consistency of the entire package, including other immutable provenance assertions.",
    "trials": "All component, version and event bindings are already resolved. current_trial is the deployed trial; each non_current_trials entry is an already-bound older trial of the same mechanism and contract scope. List positions carry no identity-resolution task. There are no other trials or defects within this declared scope.",
    "knownness": "Whether the trial input is uniquely determined by its supplied evidence; no assumption that observations obey requirements.",
    "alternative_completion": "Whether an admissible input other than the reference input exists. The reference input is admissible in these states.",
    "observation_requirement": "Already-resolved equality of observed and required output at the reference input.",
    "evidence_sufficiency": "Whether all admissible inputs imply the same truth value for this trial observation violating its requirement. DETERMINATE means one truth value; UNDERDETERMINED means both violation and compliance remain possible."
  },
  "package": {
    "same_referent": false,
    "equal_value": false,
    "consistency": "CONSISTENT"
  },
  "current_trial": {
    "currentness": "CURRENT",
    "knownness": "KNOWN",
    "alternative_completion": "NO_ALTERNATIVE",
    "observation_requirement": "MATCH",
    "evidence_sufficiency": "DETERMINATE"
  },
  "non_current_trials": [
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "KNOWN",
      "alternative_completion": "NO_ALTERNATIVE",
      "observation_requirement": "MISMATCH",
      "evidence_sufficiency": "DETERMINATE"
    },
    {
      "currentness": "NOT_CURRENT",
      "knownness": "UNKNOWN",
      "alternative_completion": "ALTERNATIVE_EXISTS",
      "observation_requirement": "MATCH",
      "evidence_sufficiency": "UNDERDETERMINED"
    }
  ]
}
```

## Integrity, preservation and limits

36 zero-model qualification checks passed, covering exact transport bytes, malformed/truncated finals, dropped connections, no retry/answer carryover, full synthetic three-arm scoring, and every primary gate boundary. All 30 input states satisfy the frozen schema. An independent witness auditor verified every primitive, gold and pair delta. All Method Freeze content and Case Freeze hashes stayed unchanged.

Freshness: 30 new state IDs and unique complete objects; no reused prior state object or copied diagnostic tuple, and no prior prediction used in construction. All new states contain two or three already-bound older trials, versus at most one in the previous study. Primitive meanings are deliberately reused. Across arms the entire user message and response schema are byte-identical; the sole intervention is the frozen system charter. No gold, offline proof, pair tag, examples, class-specific rule or class label in the added charter leaked into prompts.

All 90 scientific calls completed once, with no repairs, critics or retries. Raw finals and safe metadata were hash-frozen, made read-only and committed before scoring. Zero-inference replay is byte-identical: `29763f29ed9f03cea9e12618a8d0a689e849e17d2faed5a790ff9c5113fd3500`. Total completion wall time 978.86s; mean 10.88s. Private envelopes and reasoning are stored outside the repository with a public hash-only manifest.

Preservation and publication audits accompany the final branch: all inherited files and prior heads, main and protected S/E sources are unchanged; all reachable commit/path names and unique blobs are audited. Private archives, response envelopes, reasoning, logs, authentication keys, signed streams and Memory databases are excluded. Only the new study branch is published; no merge or promotion.

The real-task campaign previously observed authenticated negative consequences alongside repeated ADVANCE choices. This study tests no action selection and establishes no shared cause. Any test of action-selection role grounding with authenticated Memory would require separate authorization and has not been started.

## Requested answers

1. **Does generic role grounding improve reduction?** Arm B: 22/30 overall; T 1/6; non-T 21/24; historical net change versus A -1. The frozen generic-role descriptive indicator does not pass. This descriptive comparison does not replace the primary C gate.

2. **Does temporal-role grounding improve historical/current composition?** Arm C: 21/30 overall; T 1/6; non-T 20/24; historical net change versus A -1. Its temporal changing pairs score 1/5 and stable pairs 2/3. Matched repairs and regressions are reported separately, not inferred from aggregate totals.

3. **Does the temporal intervention meet its prospective gate?** No. All six frozen conditions are shown below; no threshold was revised.

4. **Does it preserve performance on D/N/U/X?** C minus A non-historical correct counts: D -2, N +0, U +0, X +0. C does not meet the 5/6 floor in every non-historical class. State-level regressions remain visible in the matched table.

5. **Is the effect temporal-specific or general?** ROLE_GROUNDING_NOT_ESTABLISHED. The registered evidence does not establish a reliable general improvement; partial gains, regressions and control ceiling effects must be read literally.

6. **Does Qwen appear to need a clearer representation of what operation it is performing?** A clearer role description has not met the registered sufficient-repair criterion. This does not identify Qwen’s internal representation or prove that role information is irrelevant.

7. **Does this justify replacing the reducer with hard-coded logic?** No. This experiment tests instruction framing; it neither compares a hard-coded reducer nor authorizes installing one.

8. **Does it justify adding an operational role representation to Horus?** No. Even a positive task-level result is not evidence of Horus action-selection efficacy and does not authorize an architecture change.

9. **What remains unresolved?** The internal failure cause, broader generalization, robustness across cases/seeds, effects beyond this interface, and whether role grounding would improve action selection using authenticated Memory remain unresolved.

10. **What has NOT been demonstrated?** No consciousness, subjective self-awareness, persistent identity, general self-model, autonomous introspection, primitive discovery, raw-evidence/end-to-end diagnosis, action-selection improvement, learning, self-improvement or RSI has been demonstrated.

