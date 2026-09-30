# Frozen Cross-Model Epistemic Comparator v0

COMPARATOR_PRIMITIVE_LIMITATIONS

Comparator: mistralai/Ministral-3-14B-Reasoning-2512, official Q8_0 GGUF. Source publication: 2cfcf8097c99d13df2156dde47409af0f65cb42a. See model-runtime.json for exact artifact/runtime hashes, method.md for preregistration, and completion.json for all freeze/publication references.

Scheduled 112; attempted 112; completed 112. Comparator schema-valid: primitives 56/56; reduction 56/56. Qwen's immutable reference has 112/112 schema-valid.

Q = published Qwen; C = comparator. All endpoint/pair comparisons are descriptive, with correlated states/pairs. No pooled intelligence score or causal percentages.

## Primitive overview

| Primitive | Q endpoints | C endpoints | Q pairs | C pairs | C schema | C gate |
| --- | --- | --- | --- | --- | --- | --- |
| IDENTITY_EQUALITY | 8/8 | 8/8 | 4/4 | 4/4 | 8/8 | True |
| CURRENTNESS | 8/8 | 7/8 | 4/4 | 3/4 | 8/8 | True |
| KNOWN_VS_UNKNOWN | 8/8 | 5/8 | 4/4 | 1/4 | 8/8 | False |
| CONTRADICTION | 8/8 | 8/8 | 4/4 | 4/4 | 8/8 | True |
| ALTERNATIVE_COMPLETION_EXISTENCE | 8/8 | 5/8 | 4/4 | 1/4 | 8/8 | False |
| OBSERVATION_REQUIREMENT_COMPARISON | 8/8 | 7/8 | 4/4 | 3/4 | 8/8 | True |
| EVIDENCE_SUFFICIENCY | 8/8 | 4/8 | 4/4 | 0/4 | 8/8 | False |

## IDENTITY_EQUALITY
Identity fields: same_referent 8/8; equal_value 8/8; joint exact 8/8.

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| s6cdeffc06513 | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | True | True | True |
| s0f8ca39efe1a | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | True | True | True |
| s9a67fca88b40 | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | True | True | True |
| s86867ae27e30 | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | True | True | True |
| s9dd0670c8d6e | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | True | True | True |
| s9a4508a6b7ca | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | True | True | True |
| see461eaf3749 | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | True | True | True |
| s0a88b08259e2 | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pcb75442d46cf | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | True | True |
| pb83de3daa4c9 | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | True | True |
| p6a9d06a11205 | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | True | True |
| pc41b9ceb9742 | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | True | True |

Endpoint answer disagreements: none. Endpoint correctness disagreements: none. Pair pass disagreements: none. Pair transition disagreements: none.

Comparator confusion counts:
```json
{
  "field_confusion": {
    "same_referent": {
      "False": {
        "False": 4,
        "True": 0,
        "INVALID_OUTPUT": 0
      },
      "True": {
        "False": 0,
        "True": 4,
        "INVALID_OUTPUT": 0
      }
    },
    "equal_value": {
      "False": {
        "False": 4,
        "True": 0,
        "INVALID_OUTPUT": 0
      },
      "True": {
        "False": 0,
        "True": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "joint_confusion": {
    "false,false": {
      "false,false": 2,
      "false,true": 0,
      "true,false": 0,
      "true,true": 0,
      "INVALID_OUTPUT": 0
    },
    "false,true": {
      "false,false": 0,
      "false,true": 2,
      "true,false": 0,
      "true,true": 0,
      "INVALID_OUTPUT": 0
    },
    "true,false": {
      "false,false": 0,
      "false,true": 0,
      "true,false": 2,
      "true,true": 0,
      "INVALID_OUTPUT": 0
    },
    "true,true": {
      "false,false": 0,
      "false,true": 0,
      "true,false": 0,
      "true,true": 2,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## CURRENTNESS

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| scba9cc461d2b | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | False | True |
| s6e13e0d63044 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| s45f64a8ae9fd | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| sb7e1cc7ef7e3 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| sccf2acfbfa18 | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| s0bf0c65011cf | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| s915d60919d64 | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| s839c64090ee5 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| p9147188c88d5 | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | False |
| p54186fe7d147 | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True |
| p6573d8bb3bcc | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True |
| p4448c687622e | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True |

Endpoint answer disagreements: scba9cc461d2b. Endpoint correctness disagreements: scba9cc461d2b. Pair pass disagreements: p9147188c88d5. Pair transition disagreements: p9147188c88d5.

Comparator confusion counts:
```json
{
  "confusion": {
    "CURRENT": {
      "CURRENT": 3,
      "NOT_CURRENT": 1,
      "INVALID_OUTPUT": 0
    },
    "NOT_CURRENT": {
      "CURRENT": 0,
      "NOT_CURRENT": 4,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## KNOWN_VS_UNKNOWN

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| s0d42cacc76e1 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | True | False | True |
| s8eba35a1979e | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| sea9358dce992 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | True | True | True |
| sacf7733e9675 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| s2bb230536616 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | True | False | True |
| s3d1adf0ce938 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| s5a4643f8f3d5 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | True | False | True |
| s134eea583827 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pfe5134c8aba6 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | True | False |
| pfea0877e44e6 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | True | True |
| p85beaefc6d27 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | True | False |
| p3b126a65a170 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | True | False |

Endpoint answer disagreements: s0d42cacc76e1, s2bb230536616, s5a4643f8f3d5. Endpoint correctness disagreements: s0d42cacc76e1, s2bb230536616, s5a4643f8f3d5. Pair pass disagreements: pfe5134c8aba6, p85beaefc6d27, p3b126a65a170. Pair transition disagreements: pfe5134c8aba6, p85beaefc6d27, p3b126a65a170.

Comparator confusion counts:
```json
{
  "confusion": {
    "KNOWN": {
      "KNOWN": 1,
      "UNKNOWN": 3,
      "INVALID_OUTPUT": 0
    },
    "UNKNOWN": {
      "KNOWN": 0,
      "UNKNOWN": 4,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## CONTRADICTION

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| sa7bd8a6a8528 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s05ec96a2a6dc | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| s6dfa7b546adb | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s42de03a09167 | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| s2697ff347b99 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s04e9ee967879 | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| sb8f321279191 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s0f2956ae97be | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pe769b04b8bb4 | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True |
| p1b34b0fb1fdb | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True |
| pe89e1cbd08fd | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True |
| p9b6e9ea58666 | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True |

Endpoint answer disagreements: none. Endpoint correctness disagreements: none. Pair pass disagreements: none. Pair transition disagreements: none.

Comparator confusion counts:
```json
{
  "confusion": {
    "CONSISTENT": {
      "CONSISTENT": 4,
      "CONTRADICTORY": 0,
      "INVALID_OUTPUT": 0
    },
    "CONTRADICTORY": {
      "CONSISTENT": 0,
      "CONTRADICTORY": 4,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## ALTERNATIVE_COMPLETION_EXISTENCE

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| sd96aa46e6676 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| saf58342c12c0 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| sfb25a574ca20 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| s7702e20ad7b4 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| s0765f4605459 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| s69eb6a090d10 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| s05ba8d17548c | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | True | True | True |
| sab307858b73d | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pe6150a0d0f53 | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False |
| p290c1440f38a | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False |
| p09c35169512d | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False |
| p8205c60fcc6a | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | True |

Endpoint answer disagreements: sd96aa46e6676, sfb25a574ca20, s0765f4605459. Endpoint correctness disagreements: sd96aa46e6676, sfb25a574ca20, s0765f4605459. Pair pass disagreements: pe6150a0d0f53, p290c1440f38a, p09c35169512d. Pair transition disagreements: pe6150a0d0f53, p290c1440f38a, p09c35169512d.

Comparator confusion counts:
```json
{
  "confusion": {
    "ALTERNATIVE_EXISTS": {
      "ALTERNATIVE_EXISTS": 4,
      "NO_ALTERNATIVE": 0,
      "INVALID_OUTPUT": 0
    },
    "NO_ALTERNATIVE": {
      "ALTERNATIVE_EXISTS": 3,
      "NO_ALTERNATIVE": 1,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## OBSERVATION_REQUIREMENT_COMPARISON

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| s2dcbcbc31e7d | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| s299b5eeddb41 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |
| s37bc9fbd4c28 | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| s95eb3f9311a7 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` | True | False | True |
| s7074290a7c0e | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| sb576e9584f1c | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |
| sf759b3af8e75 | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| sefdd360d92e4 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pa7fdd2bdb981 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True |
| p869553eb45c8 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MATCH"}` | True | False |
| pc4e6e87979b9 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True |
| p9464ebed4ef3 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True |

Endpoint answer disagreements: s95eb3f9311a7. Endpoint correctness disagreements: s95eb3f9311a7. Pair pass disagreements: p869553eb45c8. Pair transition disagreements: p869553eb45c8.

Comparator confusion counts:
```json
{
  "confusion": {
    "MATCH": {
      "MATCH": 4,
      "MISMATCH": 0,
      "INVALID_OUTPUT": 0
    },
    "MISMATCH": {
      "MATCH": 1,
      "MISMATCH": 3,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## EVIDENCE_SUFFICIENCY

| State | Gold | Q selected | C selected | Q correct | C correct | C schema |
| --- | --- | --- | --- | --- | --- | --- |
| s4e4487eb947a | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | True | False | True |
| s3619d857b3d1 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s88cda4031925 | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | True | False | True |
| sfea7d23cd93b | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s8c353e553e52 | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | True | False | True |
| s059455a331cf | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s93bb85d7f07a | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | True | False | True |
| se8ae05e202d5 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |

| Pair | Gold transition A → B | Q transition | C transition | Q pass | C pass |
| --- | --- | --- | --- | --- | --- |
| pf2edb8d17b19 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | True | False |
| p2d668f50a4c4 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | True | False |
| pb9fcb5be062e | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | True | False |
| p05e943ec08b0 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | True | False |

Endpoint answer disagreements: s4e4487eb947a, s88cda4031925, s8c353e553e52, s93bb85d7f07a. Endpoint correctness disagreements: s4e4487eb947a, s88cda4031925, s8c353e553e52, s93bb85d7f07a. Pair pass disagreements: pf2edb8d17b19, p2d668f50a4c4, pb9fcb5be062e, p05e943ec08b0. Pair transition disagreements: pf2edb8d17b19, p2d668f50a4c4, pb9fcb5be062e, p05e943ec08b0.

Comparator confusion counts:
```json
{
  "confusion": {
    "DETERMINATE": {
      "DETERMINATE": 0,
      "UNDERDETERMINED": 4,
      "INVALID_OUTPUT": 0
    },
    "UNDERDETERMINED": {
      "DETERMINATE": 0,
      "UNDERDETERMINED": 4,
      "INVALID_OUTPUT": 0
    }
  }
}
```

## Five-class reduction

| Metric | Qwen | Comparator |
| --- | --- | --- |
| Correct /56 | 41 | 27 |
| Gate | False | False |
| Schema /56 | 56 | 56 |
| Exact pairs /28 | 16 | 6 |
| Diagnostic flip /19 | 11 | 3 |
| Stable retention /9 | 5 | 3 |

| Class | Q correct | C correct | Frozen floor | C minus Q |
| --- | --- | --- | --- | --- |
| SUPPORTED_CURRENT_DEFECT | 7/12 | 6/12 | 9 | -1 |
| NO_SUPPORTED_DIAGNOSIS | 11/12 | 5/12 | 9 | -6 |
| INSUFFICIENT_EVIDENCE | 6/11 | 4/11 | 9 | -2 |
| HISTORICAL_DEFECT_NOT_CURRENT | 7/11 | 2/11 | 9 | -5 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 10/10 | 10/10 | 8 | 0 |

Confusion rows are gold, columns selected. D=current defect; N=no supported diagnosis; U=insufficient; H=historical; X=invalid/contradictory; I=invalid output.

| Gold | Q D | Q N | Q U | Q H | Q X | Q I | C D | C N | C U | C H | C X | C I |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D | 7 | 0 | 5 | 0 | 0 | 0 | 6 | 0 | 3 | 0 | 3 | 0 |
| N | 0 | 11 | 0 | 1 | 0 | 0 | 2 | 5 | 3 | 2 | 0 | 0 |
| U | 0 | 3 | 6 | 2 | 0 | 0 | 6 | 1 | 4 | 0 | 0 | 0 |
| H | 2 | 2 | 0 | 7 | 0 | 0 | 2 | 0 | 4 | 2 | 3 | 0 |
| X | 0 | 0 | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |

| Aligned family | Q reduction /8 | C reduction /8 | Q exact /4 | C exact /4 | Q flips | C flips | Q stable | C stable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| IDENTITY_EQUALITY | 8 | 6 | 4 | 2 | 2 | 1/2 | 2 | 1/2 |
| CURRENTNESS | 6 | 3 | 2 | 1 | 1 | 0/3 | 1 | 1/1 |
| KNOWN_VS_UNKNOWN | 5 | 3 | 2 | 0 | 2 | 0/2 | 0 | 0/2 |
| CONTRADICTION | 7 | 5 | 3 | 1 | 3 | 1/4 | 0 | N/A |
| ALTERNATIVE_COMPLETION_EXISTENCE | 5 | 3 | 2 | 0 | 1 | 0/2 | 1 | 0/2 |
| OBSERVATION_REQUIREMENT_COMPARISON | 7 | 5 | 3 | 2 | 2 | 1/2 | 1 | 1/2 |
| EVIDENCE_SUFFICIENCY | 3 | 2 | 0 | 0 | 0 | 0/4 | 0 | N/A |

## All reduction endpoints and state joint outcomes

| State | Family | Gold R | Q P | Q R | C P | C R | Q selected R | C selected R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s6cdeffc06513 | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s0f8ca39efe1a | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s9a67fca88b40 | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s86867ae27e30 | IDENTITY_EQUALITY | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s9dd0670c8d6e | IDENTITY_EQUALITY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | True | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s9a4508a6b7ca | IDENTITY_EQUALITY | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| see461eaf3749 | IDENTITY_EQUALITY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s0a88b08259e2 | IDENTITY_EQUALITY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| scba9cc461d2b | CURRENTNESS | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | False | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s6e13e0d63044 | CURRENTNESS | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s45f64a8ae9fd | CURRENTNESS | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | True | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sb7e1cc7ef7e3 | CURRENTNESS | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | False | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sccf2acfbfa18 | CURRENTNESS | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s0bf0c65011cf | CURRENTNESS | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s915d60919d64 | CURRENTNESS | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s839c64090ee5 | CURRENTNESS | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s0d42cacc76e1 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | False | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s8eba35a1979e | KNOWN_VS_UNKNOWN | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sea9358dce992 | KNOWN_VS_UNKNOWN | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| sacf7733e9675 | KNOWN_VS_UNKNOWN | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s2bb230536616 | KNOWN_VS_UNKNOWN | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | False | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s3d1adf0ce938 | KNOWN_VS_UNKNOWN | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | True | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s5a4643f8f3d5 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | False | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s134eea583827 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sa7bd8a6a8528 | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s05ec96a2a6dc | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s6dfa7b546adb | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s42de03a09167 | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s2697ff347b99 | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | True | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s04e9ee967879 | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sb8f321279191 | CONTRADICTION | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s0f2956ae97be | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sd96aa46e6676 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | False | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| saf58342c12c0 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sfb25a574ca20 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | False | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s7702e20ad7b4 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s0765f4605459 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | False | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s69eb6a090d10 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s05ba8d17548c | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sab307858b73d | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s2dcbcbc31e7d | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s299b5eeddb41 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | True | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s37bc9fbd4c28 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | True | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s95eb3f9311a7 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | True | False | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s7074290a7c0e | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sb576e9584f1c | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sf759b3af8e75 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sefdd360d92e4 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True | True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s4e4487eb947a | EVIDENCE_SUFFICIENCY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | False | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s3619d857b3d1 | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s88cda4031925 | EVIDENCE_SUFFICIENCY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | False | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sfea7d23cd93b | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s8c353e553e52 | EVIDENCE_SUFFICIENCY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | False | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s059455a331cf | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s93bb85d7f07a | EVIDENCE_SUFFICIENCY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | False | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| se8ae05e202d5 | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | True | True | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |

| State category | Count | Exact members |
| --- | --- | --- |
| both_P_correct_both_R_correct | 21 | s6cdeffc06513, s86867ae27e30, s9dd0670c8d6e, s9a4508a6b7ca, see461eaf3749, s0a88b08259e2, s915d60919d64, s839c64090ee5, sea9358dce992, s05ec96a2a6dc, s42de03a09167, s2697ff347b99, s04e9ee967879, s0f2956ae97be, s69eb6a090d10, s2dcbcbc31e7d, s299b5eeddb41, s37bc9fbd4c28, sf759b3af8e75, sefdd360d92e4, se8ae05e202d5 |
| both_P_correct_both_R_wrong | 9 | sb7e1cc7ef7e3, sccf2acfbfa18, s3d1adf0ce938, s134eea583827, s6dfa7b546adb, s7702e20ad7b4, s05ba8d17548c, sb576e9584f1c, s3619d857b3d1 |
| both_P_correct_only_Qwen_R_wrong | 2 | sab307858b73d, s059455a331cf |
| both_P_correct_only_comparator_R_wrong | 12 | s0f8ca39efe1a, s9a67fca88b40, s6e13e0d63044, s45f64a8ae9fd, s0bf0c65011cf, s8eba35a1979e, sacf7733e9675, sa7bd8a6a8528, sb8f321279191, saf58342c12c0, s7074290a7c0e, sfea7d23cd93b |
| primitive_answers_differ | 12 | scba9cc461d2b, s0d42cacc76e1, s2bb230536616, s5a4643f8f3d5, sd96aa46e6676, sfb25a574ca20, s0765f4605459, s95eb3f9311a7, s4e4487eb947a, s88cda4031925, s8c353e553e52, s93bb85d7f07a |
| reduction_answers_differ | 28 | s0f8ca39efe1a, s9a67fca88b40, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s8eba35a1979e, sacf7733e9675, s2bb230536616, s3d1adf0ce938, sa7bd8a6a8528, s6dfa7b546adb, sb8f321279191, sd96aa46e6676, saf58342c12c0, s7702e20ad7b4, s0765f4605459, sab307858b73d, s95eb3f9311a7, s7074290a7c0e, sb576e9584f1c, s4e4487eb947a, s3619d857b3d1, sfea7d23cd93b, s8c353e553e52, s059455a331cf, s93bb85d7f07a |

| Within-model category | Q count | C count |
| --- | --- | --- |
| P_correct_R_correct | 41 | 23 |
| P_correct_R_wrong | 15 | 21 |
| P_wrong_R_correct | 0 | 4 |
| P_wrong_R_wrong | 0 | 8 |

## All 28 reduction matched pairs

| Pair | Family | Gold changes | Q A → B | C A → B | Q exact pass | C exact pass | Q flip/stable | C flip/stable |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pcb75442d46cf | IDENTITY_EQUALITY | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | None/True | None/False |
| pb83de3daa4c9 | IDENTITY_EQUALITY | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True/None | False/None |
| p6a9d06a11205 | IDENTITY_EQUALITY | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True/None | True/None |
| pc41b9ceb9742 | IDENTITY_EQUALITY | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | None/True | None/True |
| p9147188c88d5 | CURRENTNESS | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True/None | False/None |
| p54186fe7d147 | CURRENTNESS | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | False | False | False/None | False/None |
| p6573d8bb3bcc | CURRENTNESS | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | False | False | False/None | False/None |
| p4448c687622e | CURRENTNESS | False | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | None/True | None/True |
| pfe5134c8aba6 | KNOWN_VS_UNKNOWN | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True/None | False/None |
| pfea0877e44e6 | KNOWN_VS_UNKNOWN | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | False | True/None | False/None |
| p85beaefc6d27 | KNOWN_VS_UNKNOWN | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | False | False | None/False | None/False |
| p3b126a65a170 | KNOWN_VS_UNKNOWN | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | None/False | None/False |
| pe769b04b8bb4 | CONTRADICTION | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True/None | False/None |
| p1b34b0fb1fdb | CONTRADICTION | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | False | False | False/None | False/None |
| pe89e1cbd08fd | CONTRADICTION | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True/None | True/None |
| p9b6e9ea58666 | CONTRADICTION | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True/None | False/None |
| pe6150a0d0f53 | ALTERNATIVE_COMPLETION_EXISTENCE | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | None/True | None/False |
| p290c1440f38a | ALTERNATIVE_COMPLETION_EXISTENCE | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | False | False | None/False | None/False |
| p09c35169512d | ALTERNATIVE_COMPLETION_EXISTENCE | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True/None | False/None |
| p8205c60fcc6a | ALTERNATIVE_COMPLETION_EXISTENCE | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | False/None | False/None |
| pa7fdd2bdb981 | OBSERVATION_REQUIREMENT_COMPARISON | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | True/None | True/None |
| p869553eb45c8 | OBSERVATION_REQUIREMENT_COMPARISON | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | False | True/None | False/None |
| pc4e6e87979b9 | OBSERVATION_REQUIREMENT_COMPARISON | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | False | False | None/False | None/False |
| p9464ebed4ef3 | OBSERVATION_REQUIREMENT_COMPARISON | False | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | None/True | None/True |
| pf2edb8d17b19 | EVIDENCE_SUFFICIENCY | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | False | False | False/None | False/None |
| p2d668f50a4c4 | EVIDENCE_SUFFICIENCY | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | False | False | False/None | False/None |
| pb9fcb5be062e | EVIDENCE_SUFFICIENCY | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | False/None | False/None |
| p05e943ec08b0 | EVIDENCE_SUFFICIENCY | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | False/None | False/None |

## Evidence-sufficiency subset

| Measure | Q | C |
| --- | --- | --- |
| P_correct | 8 | 4 |
| P_pair_passes | 4 | 0 |
| R_correct | 3 | 2 |
| R_exact_pair_passes | 0 | 0 |

| State | Q P selected | C P selected | Gold R | Q R selected | C R selected |
| --- | --- | --- | --- | --- | --- |
| s4e4487eb947a | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s3619d857b3d1 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s88cda4031925 | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sfea7d23cd93b | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s8c353e553e52 | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s059455a331cf | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s93bb85d7f07a | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| se8ae05e202d5 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |

| Pair | Q primitive flip | C primitive flip | Q reduction exact | C reduction exact |
| --- | --- | --- | --- | --- |
| pf2edb8d17b19 | True | False | False | False |
| p2d668f50a4c4 | True | False | False | False |
| pb9fcb5be062e | True | False | False | False |
| p05e943ec08b0 | True | False | False | False |

## Registered interpretation and limits

{
  "category": "C",
  "pattern": "COMPARATOR_PRIMITIVE_LIMITATIONS",
  "failed_primitives": [
    "KNOWN_VS_UNKNOWN",
    "ALTERNATIVE_COMPLETION_EXISTENCE",
    "EVIDENCE_SUFFICIENCY"
  ],
  "shared_reduction_errors": 13,
  "similarity_rule": "At least 8 of the 15 published Qwen reduction-error states also incorrect for comparator; descriptive majority, not significance"
}

Shared reduction-error states: sb7e1cc7ef7e3, sccf2acfbfa18, s2bb230536616, s3d1adf0ce938, s134eea583827, s6dfa7b546adb, s7702e20ad7b4, s05ba8d17548c, sb576e9584f1c, s3619d857b3d1, s88cda4031925, s8c353e553e52, s93bb85d7f07a.

The comparison is specific to the frozen messages, native model interfaces, quantizations and runtime budgets. Native Ministral reasoning is optional and no reasoning prompt was added to scientific inputs. Separate primitive calls do not establish correct primitive computation inside reduction calls. Similar observed errors do not identify a causal mechanism.

Qwen model capability: immutable published reference. Comparator capability: measured here. Deterministic software capability: verification, transport, hashing and scoring. Combined-system capability: NOT TESTED. No primitive output is passed into reduction, no deterministic helper chooses diagnoses, and no Horus/Memory/policy/weights change, training, promotion or self-improvement occurs.

No result here tests a Horus intervention or automatically authorizes one. No further study is started.

## Execution, replay and handoff

Method Freeze: `acc496be7e2005fe43b948686c81ed1503bd13ab`. Implementation/request Freeze: `3e66cde0df4908a9f81abde383499dc8714dd5da`. Raw pre-scoring commit: `48e4802125a81eaaafec0ca30aac77c8d62f935a`.

Zero-inference score replay is byte-identical: `ac6fb003b9bc46d08d8ab558fc98f231392f4542b0697818626ba32d329c20e1`. All 32 zero-model tests passed. The final publication SHA is the verified remote head reported in the handoff; completion.json records the freeze chain.

Native reasoning was configured on and synthetically verified, but none of the 112 scientific responses included a separated reasoning channel. The preserved scientific messages did not add a thinking instruction or native reasoning prefill. This is a material interface limitation; it does not establish why the answers were right or wrong. Qwen and Ministral use different native templates/tokenizers and quantizations. No scientific outcome triggered a setting change or extra call.

The 3,794 inherited files and all 21 protected local/remote heads passed preservation checks. Full envelopes, raw reasoning from synthetic qualification and server logs remain outside Git. Full reachable-history publication checks are recorded separately.

## Completion questions

1. **Does the comparator establish the same seven primitive capabilities?** No. Four of seven comparator primitive gates are established. KNOWN_VS_UNKNOWN (5/8; 1/4 pairs), ALTERNATIVE_COMPLETION_EXISTENCE (5/8; 1/4), and EVIDENCE_SUFFICIENCY (4/8; 0/4) fail their gates.

2. **Does the comparator pass five-class reduction?** No. Comparator five-class reduction is 27/56 (Qwen 41/56), with 6/28 exact pairs, 3/19 diagnostic flips and 3/9 stable pairs. It fails the overall 48/56 threshold and four of five class floors.

3. **Is Qwen’s primitive-to-reduction gap replicated?** The clean all-seven-primitives-established / reduction-failed pattern is not replicated. There are 21 comparator P-correct/R-wrong states, but comparator primitive limitations prevent a clean reduction-specific comparison. Thirteen of Qwen’s 15 reduction-error states are also comparator errors; this overlap alone does not override Pattern C.

4. **Is the evidence-sufficiency dissociation replicated?** The clean evidence-sufficiency dissociation is not replicated. Comparator primitive is 4/8 and 0/4 pairs, with reduction 2/8 and 0/4 pairs; Qwen is 8/8, 4/4, 3/8 and 0/4 respectively. Weak reduction is observed in both, but the comparator primitive itself is not established.

5. **Is the limitation Qwen-specific, shared, mixed, or unresolved?** Unresolved as a Qwen-specific versus shared reduction limitation: registered Pattern C, COMPARATOR_PRIMITIVE_LIMITATIONS. This comparator does not isolate a shared reduction-only problem or establish that Qwen alone has one.

6. **Does this justify changing Horus yet?** No Horus change is justified by a tested intervention here: no intervention or combined system was tested. These results describe capability under the frozen interface and do not authorize architecture changes, training, promotion or another study.

