# Frozen Epistemic Primitive gpt-oss Comparator v0

SECOND_COMPARATOR_PRIMITIVE_LIMITATIONS

This is the final planned comparator. No further comparator, benchmark, model promotion or Horus intervention is authorized by this result. See completion.json for the freeze chain, model-runtime.json for exact identity/configuration, and method.md for the prospective rules.

112 scheduled; 112 attempted; 112 completed. gpt-oss schema-valid: primitives 55/56; reduction 54/56.

Q = published Qwen3-14B; M = published Ministral-3-14B-Reasoning; G = newly measured gpt-oss-20b. Prior scores are reused without inference or rescoring. These are descriptive comparisons of correlated states/pairs, not an overall model ranking.

## Seven primitive capabilities

Each cell: endpoints; matched pairs; competence gate. Thresholds >=7/8 AND >=3/4.

| Primitive | Qwen | Ministral | gpt-oss |
| --- | --- | --- | --- |
| IDENTITY_EQUALITY | 8/8; 4/4; PASS | 8/8; 4/4; PASS | 8/8; 4/4; PASS |
| CURRENTNESS | 8/8; 4/4; PASS | 7/8; 3/4; PASS | 8/8; 4/4; PASS |
| KNOWN_VS_UNKNOWN | 8/8; 4/4; PASS | 5/8; 1/4; FAIL | 6/8; 2/4; FAIL |
| CONTRADICTION | 8/8; 4/4; PASS | 8/8; 4/4; PASS | 8/8; 4/4; PASS |
| ALTERNATIVE_COMPLETION_EXISTENCE | 8/8; 4/4; PASS | 5/8; 1/4; FAIL | 8/8; 4/4; PASS |
| OBSERVATION_REQUIREMENT_COMPARISON | 8/8; 4/4; PASS | 7/8; 3/4; PASS | 8/8; 4/4; PASS |
| EVIDENCE_SUFFICIENCY | 8/8; 4/4; PASS | 4/8; 0/4; FAIL | 8/8; 4/4; PASS |

## IDENTITY_EQUALITY

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 8 | 4 | 8 | True |
| gpt_oss | 8 | 4 | 8 | True |

| Model | same_referent /8 | equal_value /8 | joint /8 |
| --- | --- | --- | --- |
| qwen | 8 | 8 | 8 |
| ministral | 8 | 8 | 8 |
| gpt_oss | 8 | 8 | 8 |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s6cdeffc06513 | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | True | True | True |
| s0f8ca39efe1a | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | True | True | True |
| s9a67fca88b40 | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | True | True | True |
| s86867ae27e30 | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | True | True | True |
| s9dd0670c8d6e | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` | True | True | True |
| s9a4508a6b7ca | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":true}` | True | True | True |
| see461eaf3749 | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` | True | True | True |
| s0a88b08259e2 | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":false}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pcb75442d46cf | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":true,"same_referent":false}` | True | True | True |
| pb83de3daa4c9 | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":false,"same_referent":true}` | True | True | True |
| p6a9d06a11205 | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | `{"equal_value":true,"same_referent":true}` → `{"equal_value":false,"same_referent":true}` | True | True | True |
| pc41b9ceb9742 | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | `{"equal_value":false,"same_referent":false}` → `{"equal_value":true,"same_referent":false}` | True | True | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
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
  },
  "ministral": {
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
  },
  "gpt_oss": {
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
}
```

## CURRENTNESS

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 7 | 3 | 8 | True |
| gpt_oss | 8 | 4 | 8 | True |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| scba9cc461d2b | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` | True | False | True |
| s6e13e0d63044 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| s45f64a8ae9fd | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| sb7e1cc7ef7e3 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| sccf2acfbfa18 | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| s0bf0c65011cf | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |
| s915d60919d64 | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | `{"answer":"CURRENT"}` | True | True | True |
| s839c64090ee5 | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| p9147188c88d5 | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"NOT_CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | False | True |
| p54186fe7d147 | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True | True |
| p6573d8bb3bcc | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True | True |
| p4448c687622e | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | `{"answer":"CURRENT"}` → `{"answer":"NOT_CURRENT"}` | True | True | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
    "confusion": {
      "CURRENT": {
        "CURRENT": 4,
        "NOT_CURRENT": 0,
        "INVALID_OUTPUT": 0
      },
      "NOT_CURRENT": {
        "CURRENT": 0,
        "NOT_CURRENT": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "ministral": {
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
  },
  "gpt_oss": {
    "confusion": {
      "CURRENT": {
        "CURRENT": 4,
        "NOT_CURRENT": 0,
        "INVALID_OUTPUT": 0
      },
      "NOT_CURRENT": {
        "CURRENT": 0,
        "NOT_CURRENT": 4,
        "INVALID_OUTPUT": 0
      }
    }
  }
}
```

## KNOWN_VS_UNKNOWN

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 5 | 1 | 8 | False |
| gpt_oss | 6 | 2 | 7 | False |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s0d42cacc76e1 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` | True | False | True |
| s8eba35a1979e | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| sea9358dce992 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | False |
| sacf7733e9675 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| s2bb230536616 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | INVALID | True | False | False |
| s3d1adf0ce938 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |
| s5a4643f8f3d5 | `{"answer":"KNOWN"}` | `{"answer":"KNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` | True | False | True |
| s134eea583827 | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pfe5134c8aba6 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | True | False | True |
| pfea0877e44e6 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | True | True | False |
| p85beaefc6d27 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | INVALID → `{"answer":"UNKNOWN"}` | True | False | False |
| p3b126a65a170 | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"UNKNOWN"}` → `{"answer":"UNKNOWN"}` | `{"answer":"KNOWN"}` → `{"answer":"UNKNOWN"}` | True | False | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
    "confusion": {
      "KNOWN": {
        "KNOWN": 4,
        "UNKNOWN": 0,
        "INVALID_OUTPUT": 0
      },
      "UNKNOWN": {
        "KNOWN": 0,
        "UNKNOWN": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "ministral": {
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
  },
  "gpt_oss": {
    "confusion": {
      "KNOWN": {
        "KNOWN": 2,
        "UNKNOWN": 1,
        "INVALID_OUTPUT": 1
      },
      "UNKNOWN": {
        "KNOWN": 0,
        "UNKNOWN": 4,
        "INVALID_OUTPUT": 0
      }
    }
  }
}
```

## CONTRADICTION

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 8 | 4 | 8 | True |
| gpt_oss | 8 | 4 | 8 | True |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sa7bd8a6a8528 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s05ec96a2a6dc | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| s6dfa7b546adb | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s42de03a09167 | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| s2697ff347b99 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s04e9ee967879 | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |
| sb8f321279191 | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | `{"answer":"CONSISTENT"}` | True | True | True |
| s0f2956ae97be | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | `{"answer":"CONTRADICTORY"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pe769b04b8bb4 | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True | True |
| p1b34b0fb1fdb | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True | True |
| pe89e1cbd08fd | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True | True |
| p9b6e9ea58666 | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | `{"answer":"CONSISTENT"}` → `{"answer":"CONTRADICTORY"}` | True | True | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
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
  },
  "ministral": {
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
  },
  "gpt_oss": {
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
}
```

## ALTERNATIVE_COMPLETION_EXISTENCE

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 5 | 1 | 8 | False |
| gpt_oss | 8 | 4 | 8 | True |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| sd96aa46e6676 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` | True | False | True |
| saf58342c12c0 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| sfb25a574ca20 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` | True | False | True |
| s7702e20ad7b4 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| s0765f4605459 | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` | True | False | True |
| s69eb6a090d10 | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |
| s05ba8d17548c | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | `{"answer":"NO_ALTERNATIVE"}` | True | True | True |
| sab307858b73d | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pe6150a0d0f53 | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| p290c1440f38a | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| p09c35169512d | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"ALTERNATIVE_EXISTS"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | False | True |
| p8205c60fcc6a | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | `{"answer":"NO_ALTERNATIVE"}` → `{"answer":"ALTERNATIVE_EXISTS"}` | True | True | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
    "confusion": {
      "ALTERNATIVE_EXISTS": {
        "ALTERNATIVE_EXISTS": 4,
        "NO_ALTERNATIVE": 0,
        "INVALID_OUTPUT": 0
      },
      "NO_ALTERNATIVE": {
        "ALTERNATIVE_EXISTS": 0,
        "NO_ALTERNATIVE": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "ministral": {
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
  },
  "gpt_oss": {
    "confusion": {
      "ALTERNATIVE_EXISTS": {
        "ALTERNATIVE_EXISTS": 4,
        "NO_ALTERNATIVE": 0,
        "INVALID_OUTPUT": 0
      },
      "NO_ALTERNATIVE": {
        "ALTERNATIVE_EXISTS": 0,
        "NO_ALTERNATIVE": 4,
        "INVALID_OUTPUT": 0
      }
    }
  }
}
```

## OBSERVATION_REQUIREMENT_COMPARISON

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 7 | 3 | 8 | True |
| gpt_oss | 8 | 4 | 8 | True |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s2dcbcbc31e7d | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| s299b5eeddb41 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |
| s37bc9fbd4c28 | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| s95eb3f9311a7 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MISMATCH"}` | True | False | True |
| s7074290a7c0e | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| sb576e9584f1c | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |
| sf759b3af8e75 | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | `{"answer":"MATCH"}` | True | True | True |
| sefdd360d92e4 | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | `{"answer":"MISMATCH"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pa7fdd2bdb981 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True | True |
| p869553eb45c8 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | False | True |
| pc4e6e87979b9 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True | True |
| p9464ebed4ef3 | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | `{"answer":"MATCH"}` → `{"answer":"MISMATCH"}` | True | True | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
    "confusion": {
      "MATCH": {
        "MATCH": 4,
        "MISMATCH": 0,
        "INVALID_OUTPUT": 0
      },
      "MISMATCH": {
        "MATCH": 0,
        "MISMATCH": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "ministral": {
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
  },
  "gpt_oss": {
    "confusion": {
      "MATCH": {
        "MATCH": 4,
        "MISMATCH": 0,
        "INVALID_OUTPUT": 0
      },
      "MISMATCH": {
        "MATCH": 0,
        "MISMATCH": 4,
        "INVALID_OUTPUT": 0
      }
    }
  }
}
```

## EVIDENCE_SUFFICIENCY

| Model | Correct /8 | Pairs /4 | Schema /8 | Gate |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 8 | True |
| ministral | 4 | 0 | 8 | False |
| gpt_oss | 8 | 4 | 8 | True |

| State | Gold | Q selected | M selected | G selected | Q correct | M correct | G correct |
| --- | --- | --- | --- | --- | --- | --- | --- |
| s4e4487eb947a | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | True | False | True |
| s3619d857b3d1 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s88cda4031925 | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | True | False | True |
| sfea7d23cd93b | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s8c353e553e52 | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | True | False | True |
| s059455a331cf | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |
| s93bb85d7f07a | `{"answer":"DETERMINATE"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | True | False | True |
| se8ae05e202d5 | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | True | True | True |

| Pair | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pf2edb8d17b19 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | True | False | True |
| p2d668f50a4c4 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | True | False | True |
| pb9fcb5be062e | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | True | False | True |
| p05e943ec08b0 | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` → `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` → `{"answer":"UNDERDETERMINED"}` | True | False | True |

Confusion counts (rows gold, columns selected):
```json
{
  "qwen": {
    "confusion": {
      "DETERMINATE": {
        "DETERMINATE": 4,
        "UNDERDETERMINED": 0,
        "INVALID_OUTPUT": 0
      },
      "UNDERDETERMINED": {
        "DETERMINATE": 0,
        "UNDERDETERMINED": 4,
        "INVALID_OUTPUT": 0
      }
    }
  },
  "ministral": {
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
  },
  "gpt_oss": {
    "confusion": {
      "DETERMINATE": {
        "DETERMINATE": 4,
        "UNDERDETERMINED": 0,
        "INVALID_OUTPUT": 0
      },
      "UNDERDETERMINED": {
        "DETERMINATE": 0,
        "UNDERDETERMINED": 4,
        "INVALID_OUTPUT": 0
      }
    }
  }
}
```

## Five-class reduction

| Measure | Qwen | Ministral | gpt-oss |
| --- | --- | --- | --- |
| Endpoints /56 | 41 | 27 | 42 |
| Schema /56 | 56 | 56 | 54 |
| Competence gate | False | False | False |
| Exact pairs /28 | 16 | 6 | 16 |
| Diagnostic flips /19 | 11 | 3 | 11 |
| Stable retention /9 | 5 | 3 | 5 |

| Class | Qwen | Ministral | gpt-oss | Required floor |
| --- | --- | --- | --- | --- |
| SUPPORTED_CURRENT_DEFECT | 7/12 | 6/12 | 7/12 | 9 |
| NO_SUPPORTED_DIAGNOSIS | 11/12 | 5/12 | 8/12 | 9 |
| INSUFFICIENT_EVIDENCE | 6/11 | 4/11 | 6/11 | 9 |
| HISTORICAL_DEFECT_NOT_CURRENT | 7/11 | 2/11 | 11/11 | 9 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 10/10 | 10/10 | 10/10 | 8 |

Confusion rows are gold, columns selected. D=current defect; N=no supported diagnosis; U=insufficient; H=historical; X=invalid/contradictory; I=invalid output.

qwen

| Gold | D | N | U | H | X | I |
| --- | --- | --- | --- | --- | --- | --- |
| SUPPORTED_CURRENT_DEFECT | 7 | 0 | 5 | 0 | 0 | 0 |
| NO_SUPPORTED_DIAGNOSIS | 0 | 11 | 0 | 1 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 0 | 3 | 6 | 2 | 0 | 0 |
| HISTORICAL_DEFECT_NOT_CURRENT | 2 | 2 | 0 | 7 | 0 | 0 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 0 | 0 | 0 | 0 | 10 | 0 |

ministral

| Gold | D | N | U | H | X | I |
| --- | --- | --- | --- | --- | --- | --- |
| SUPPORTED_CURRENT_DEFECT | 6 | 0 | 3 | 0 | 3 | 0 |
| NO_SUPPORTED_DIAGNOSIS | 2 | 5 | 3 | 2 | 0 | 0 |
| INSUFFICIENT_EVIDENCE | 6 | 1 | 4 | 0 | 0 | 0 |
| HISTORICAL_DEFECT_NOT_CURRENT | 2 | 0 | 4 | 2 | 3 | 0 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 0 | 0 | 0 | 0 | 10 | 0 |

gpt_oss

| Gold | D | N | U | H | X | I |
| --- | --- | --- | --- | --- | --- | --- |
| SUPPORTED_CURRENT_DEFECT | 7 | 0 | 5 | 0 | 0 | 0 |
| NO_SUPPORTED_DIAGNOSIS | 0 | 8 | 2 | 1 | 0 | 1 |
| INSUFFICIENT_EVIDENCE | 0 | 3 | 6 | 1 | 0 | 1 |
| HISTORICAL_DEFECT_NOT_CURRENT | 0 | 0 | 0 | 11 | 0 | 0 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 0 | 0 | 0 | 0 | 10 | 0 |

## Family-aligned reduction subsets

IDENTITY_EQUALITY

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 8 | 4 | 2/2 | 2/2 |
| ministral | 6 | 2 | 1/2 | 1/2 |
| gpt_oss | 7 | 3 | 2/2 | 1/2 |

CURRENTNESS

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 6 | 2 | 1/3 | 1/1 |
| ministral | 3 | 1 | 0/3 | 1/1 |
| gpt_oss | 5 | 2 | 1/3 | 1/1 |

KNOWN_VS_UNKNOWN

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 5 | 2 | 2/2 | 0/2 |
| ministral | 3 | 0 | 0/2 | 0/2 |
| gpt_oss | 6 | 2 | 1/2 | 1/2 |

CONTRADICTION

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 7 | 3 | 3/4 | N/A |
| ministral | 5 | 1 | 1/4 | N/A |
| gpt_oss | 8 | 4 | 4/4 | N/A |

ALTERNATIVE_COMPLETION_EXISTENCE

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 5 | 2 | 1/2 | 1/2 |
| ministral | 3 | 0 | 0/2 | 0/2 |
| gpt_oss | 3 | 0 | 0/2 | 0/2 |

OBSERVATION_REQUIREMENT_COMPARISON

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 7 | 3 | 2/2 | 1/2 |
| ministral | 5 | 2 | 1/2 | 1/2 |
| gpt_oss | 7 | 3 | 1/2 | 2/2 |

EVIDENCE_SUFFICIENCY

| Model | Endpoints /8 | Exact pairs /4 | Diagnostic flips | Stable retention |
| --- | --- | --- | --- | --- |
| qwen | 3 | 0 | 0/4 | N/A |
| ministral | 2 | 0 | 0/4 | N/A |
| gpt_oss | 6 | 2 | 2/4 | N/A |

## Every aligned state and reduction selection

| State | Family | Gold R | Q P/R correct | M P/R correct | G P/R correct | Q R selected | M R selected | G R selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s6cdeffc06513 | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/True | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s0f8ca39efe1a | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s9a67fca88b40 | IDENTITY_EQUALITY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s86867ae27e30 | IDENTITY_EQUALITY | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s9dd0670c8d6e | IDENTITY_EQUALITY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | True/True | True/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s9a4508a6b7ca | IDENTITY_EQUALITY | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| see461eaf3749 | IDENTITY_EQUALITY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/True | True/False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s0a88b08259e2 | IDENTITY_EQUALITY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/True | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| scba9cc461d2b | CURRENTNESS | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | False/True | True/False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s6e13e0d63044 | CURRENTNESS | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s45f64a8ae9fd | CURRENTNESS | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | True/False | True/False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sb7e1cc7ef7e3 | CURRENTNESS | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/False | True/False | True/False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| sccf2acfbfa18 | CURRENTNESS | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/False | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s0bf0c65011cf | CURRENTNESS | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s915d60919d64 | CURRENTNESS | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s839c64090ee5 | CURRENTNESS | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s0d42cacc76e1 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | False/True | True/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s8eba35a1979e | KNOWN_VS_UNKNOWN | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/False | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sea9358dce992 | KNOWN_VS_UNKNOWN | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/True | False/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| sacf7733e9675 | KNOWN_VS_UNKNOWN | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/False | True/False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s2bb230536616 | KNOWN_VS_UNKNOWN | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/False | False/False | False/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s3d1adf0ce938 | KNOWN_VS_UNKNOWN | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/False | True/False | True/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s5a4643f8f3d5 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | False/True | True/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s134eea583827 | KNOWN_VS_UNKNOWN | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/False | True/False | True/False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sa7bd8a6a8528 | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s05ec96a2a6dc | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s6dfa7b546adb | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/False | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s42de03a09167 | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s2697ff347b99 | CONTRADICTION | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | True/True | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s04e9ee967879 | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sb8f321279191 | CONTRADICTION | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s0f2956ae97be | CONTRADICTION | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sd96aa46e6676 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | False/False | True/False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | INVALID |
| saf58342c12c0 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| sfb25a574ca20 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | False/True | True/False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s7702e20ad7b4 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/False | True/False | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s0765f4605459 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | False/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s69eb6a090d10 | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/True | True/False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s05ba8d17548c | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/False | True/False | True/False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sab307858b73d | ALTERNATIVE_COMPLETION_EXISTENCE | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/False | True/True | True/False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | INVALID |
| s2dcbcbc31e7d | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/True | True/False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s299b5eeddb41 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/True | True/True | True/True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| s37bc9fbd4c28 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | True/True | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s95eb3f9311a7 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/True | False/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s7074290a7c0e | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/False | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sb576e9584f1c | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/False | True/False | True/True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| sf759b3af8e75 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| sefdd360d92e4 | OBSERVATION_REQUIREMENT_COMPARISON | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` |
| s4e4487eb947a | EVIDENCE_SUFFICIENCY | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True/True | False/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s3619d857b3d1 | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/False | True/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s88cda4031925 | EVIDENCE_SUFFICIENCY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/False | False/False | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sfea7d23cd93b | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/False | True/False | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s8c353e553e52 | EVIDENCE_SUFFICIENCY | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True/False | False/False | True/True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s059455a331cf | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/False | True/True | True/False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s93bb85d7f07a | EVIDENCE_SUFFICIENCY | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True/False | False/False | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| se8ae05e202d5 | EVIDENCE_SUFFICIENCY | `{"classification":"INSUFFICIENT_EVIDENCE"}` | True/True | True/True | True/True | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |

## Every reduction matched pair

Flip/stable classification is fixed by gold; exact pass requires both endpoints correct with the expected transition.

| Pair | Family | Gold changes | Gold A → B | Q A → B | M A → B | G A → B | Q pass | M pass | G pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pcb75442d46cf | IDENTITY_EQUALITY | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | True |
| pb83de3daa4c9 | IDENTITY_EQUALITY | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True |
| p6a9d06a11205 | IDENTITY_EQUALITY | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True |
| pc41b9ceb9742 | IDENTITY_EQUALITY | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | True | False |
| p9147188c88d5 | CURRENTNESS | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | False |
| p54186fe7d147 | CURRENTNESS | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | False | False | False |
| p6573d8bb3bcc | CURRENTNESS | True | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | False | False | True |
| p4448c687622e | CURRENTNESS | False | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True |
| pfe5134c8aba6 | KNOWN_VS_UNKNOWN | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | True | False | True |
| pfea0877e44e6 | KNOWN_VS_UNKNOWN | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | False | False |
| p85beaefc6d27 | KNOWN_VS_UNKNOWN | False | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | False | False | True |
| p3b126a65a170 | KNOWN_VS_UNKNOWN | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | False |
| pe769b04b8bb4 | CONTRADICTION | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True |
| p1b34b0fb1fdb | CONTRADICTION | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | False | False | True |
| pe89e1cbd08fd | CONTRADICTION | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True |
| p9b6e9ea58666 | CONTRADICTION | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | False | True |
| pe6150a0d0f53 | ALTERNATIVE_COMPLETION_EXISTENCE | False | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | INVALID → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | False | False |
| p290c1440f38a | ALTERNATIVE_COMPLETION_EXISTENCE | False | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | False | False | False |
| p09c35169512d | ALTERNATIVE_COMPLETION_EXISTENCE | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | True | False | False |
| p8205c60fcc6a | ALTERNATIVE_COMPLETION_EXISTENCE | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → INVALID | False | False | False |
| pa7fdd2bdb981 | OBSERVATION_REQUIREMENT_COMPARISON | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | True | True | False |
| p869553eb45c8 | OBSERVATION_REQUIREMENT_COMPARISON | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | True | False | True |
| pc4e6e87979b9 | OBSERVATION_REQUIREMENT_COMPARISON | False | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | True |
| p9464ebed4ef3 | OBSERVATION_REQUIREMENT_COMPARISON | False | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | True | True | True |
| pf2edb8d17b19 | EVIDENCE_SUFFICIENCY | True | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | True |
| p2d668f50a4c4 | EVIDENCE_SUFFICIENCY | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | False | False | False |
| pb9fcb5be062e | EVIDENCE_SUFFICIENCY | True | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` → `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | False | False | False |
| p05e943ec08b0 | EVIDENCE_SUFFICIENCY | True | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` → `{"classification":"INSUFFICIENT_EVIDENCE"}` | False | False | True |

## Exact matched memberships

P is the isolated primitive corresponding to the state’s family. Sets can overlap.

| Category | Count | States |
| --- | --- | --- |
| all_three_P_correct | 43 | s6cdeffc06513, s0f8ca39efe1a, s9a67fca88b40, s86867ae27e30, s9dd0670c8d6e, s9a4508a6b7ca, see461eaf3749, s0a88b08259e2, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s915d60919d64, s839c64090ee5, s8eba35a1979e, sacf7733e9675, s3d1adf0ce938, s134eea583827, sa7bd8a6a8528, s05ec96a2a6dc, s6dfa7b546adb, s42de03a09167, s2697ff347b99, s04e9ee967879, sb8f321279191, s0f2956ae97be, saf58342c12c0, s7702e20ad7b4, s69eb6a090d10, s05ba8d17548c, sab307858b73d, s2dcbcbc31e7d, s299b5eeddb41, s37bc9fbd4c28, s7074290a7c0e, sb576e9584f1c, sf759b3af8e75, sefdd360d92e4, s3619d857b3d1, sfea7d23cd93b, s059455a331cf, se8ae05e202d5 |
| Qwen_P_correct_both_comparators_P_wrong | 1 | s2bb230536616 |
| Qwen_and_gpt_oss_P_correct | 54 | s6cdeffc06513, s0f8ca39efe1a, s9a67fca88b40, s86867ae27e30, s9dd0670c8d6e, s9a4508a6b7ca, see461eaf3749, s0a88b08259e2, scba9cc461d2b, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s915d60919d64, s839c64090ee5, s0d42cacc76e1, s8eba35a1979e, sacf7733e9675, s3d1adf0ce938, s5a4643f8f3d5, s134eea583827, sa7bd8a6a8528, s05ec96a2a6dc, s6dfa7b546adb, s42de03a09167, s2697ff347b99, s04e9ee967879, sb8f321279191, s0f2956ae97be, sd96aa46e6676, saf58342c12c0, sfb25a574ca20, s7702e20ad7b4, s0765f4605459, s69eb6a090d10, s05ba8d17548c, sab307858b73d, s2dcbcbc31e7d, s299b5eeddb41, s37bc9fbd4c28, s95eb3f9311a7, s7074290a7c0e, sb576e9584f1c, sf759b3af8e75, sefdd360d92e4, s4e4487eb947a, s3619d857b3d1, s88cda4031925, sfea7d23cd93b, s8c353e553e52, s059455a331cf, s93bb85d7f07a, se8ae05e202d5 |
| all_three_P_correct_reduction_answers_differ | 24 | s0f8ca39efe1a, s9a67fca88b40, see461eaf3749, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s8eba35a1979e, sacf7733e9675, s3d1adf0ce938, sa7bd8a6a8528, s6dfa7b546adb, sb8f321279191, saf58342c12c0, s7702e20ad7b4, s69eb6a090d10, sab307858b73d, s2dcbcbc31e7d, s7074290a7c0e, sb576e9584f1c, s3619d857b3d1, sfea7d23cd93b, s059455a331cf |
| Qwen_and_gpt_oss_P_correct_reduction_answers_differ | 19 | see461eaf3749, scba9cc461d2b, s45f64a8ae9fd, sccf2acfbfa18, sacf7733e9675, s3d1adf0ce938, s6dfa7b546adb, sd96aa46e6676, sfb25a574ca20, s7702e20ad7b4, s69eb6a090d10, sab307858b73d, s2dcbcbc31e7d, sb576e9584f1c, s3619d857b3d1, s88cda4031925, sfea7d23cd93b, s8c353e553e52, s93bb85d7f07a |
| Qwen_R_wrong_gpt_oss_R_correct | 10 | sccf2acfbfa18, s2bb230536616, s3d1adf0ce938, s6dfa7b546adb, s7702e20ad7b4, sb576e9584f1c, s3619d857b3d1, s88cda4031925, s8c353e553e52, s93bb85d7f07a |
| Qwen_R_correct_gpt_oss_R_wrong | 9 | see461eaf3749, scba9cc461d2b, s45f64a8ae9fd, sacf7733e9675, sd96aa46e6676, sfb25a574ca20, s69eb6a090d10, s2dcbcbc31e7d, sfea7d23cd93b |
| all_three_R_wrong | 3 | sb7e1cc7ef7e3, s134eea583827, s05ba8d17548c |
| all_three_R_correct | 20 | s6cdeffc06513, s86867ae27e30, s9dd0670c8d6e, s9a4508a6b7ca, s0a88b08259e2, s915d60919d64, s839c64090ee5, s0d42cacc76e1, sea9358dce992, s5a4643f8f3d5, s05ec96a2a6dc, s42de03a09167, s2697ff347b99, s04e9ee967879, s0f2956ae97be, s299b5eeddb41, s37bc9fbd4c28, sf759b3af8e75, sefdd360d92e4, se8ae05e202d5 |

qwen_vs_gpt_oss

| Disagreement | Exact members |
| --- | --- |
| primitive_answer_states | sea9358dce992, s2bb230536616 |
| reduction_answer_states | see461eaf3749, scba9cc461d2b, s45f64a8ae9fd, sccf2acfbfa18, sacf7733e9675, s2bb230536616, s3d1adf0ce938, s6dfa7b546adb, sd96aa46e6676, sfb25a574ca20, s7702e20ad7b4, s69eb6a090d10, sab307858b73d, s2dcbcbc31e7d, sb576e9584f1c, s3619d857b3d1, s88cda4031925, sfea7d23cd93b, s8c353e553e52, s93bb85d7f07a |
| primitive_pair_passes | pfea0877e44e6, p85beaefc6d27 |
| reduction_pair_passes | pc41b9ceb9742, p9147188c88d5, p6573d8bb3bcc, pfea0877e44e6, p85beaefc6d27, p1b34b0fb1fdb, pe6150a0d0f53, p09c35169512d, pa7fdd2bdb981, pc4e6e87979b9, pf2edb8d17b19, p05e943ec08b0 |

ministral_vs_gpt_oss

| Disagreement | Exact members |
| --- | --- |
| primitive_answer_states | scba9cc461d2b, s0d42cacc76e1, sea9358dce992, s2bb230536616, s5a4643f8f3d5, sd96aa46e6676, sfb25a574ca20, s0765f4605459, s95eb3f9311a7, s4e4487eb947a, s88cda4031925, s8c353e553e52, s93bb85d7f07a |
| reduction_answer_states | s0f8ca39efe1a, s9a67fca88b40, see461eaf3749, scba9cc461d2b, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s8eba35a1979e, s2bb230536616, s3d1adf0ce938, sa7bd8a6a8528, s6dfa7b546adb, sb8f321279191, sd96aa46e6676, saf58342c12c0, sfb25a574ca20, s7702e20ad7b4, s0765f4605459, s69eb6a090d10, sab307858b73d, s2dcbcbc31e7d, s95eb3f9311a7, s7074290a7c0e, sb576e9584f1c, s4e4487eb947a, s3619d857b3d1, s88cda4031925, sfea7d23cd93b, s8c353e553e52, s059455a331cf, s93bb85d7f07a |
| primitive_pair_passes | p9147188c88d5, pfe5134c8aba6, pfea0877e44e6, p3b126a65a170, pe6150a0d0f53, p290c1440f38a, p09c35169512d, p869553eb45c8, pf2edb8d17b19, p2d668f50a4c4, pb9fcb5be062e, p05e943ec08b0 |
| reduction_pair_passes | pcb75442d46cf, pb83de3daa4c9, pc41b9ceb9742, p6573d8bb3bcc, pfe5134c8aba6, p85beaefc6d27, pe769b04b8bb4, p1b34b0fb1fdb, p9b6e9ea58666, pa7fdd2bdb981, p869553eb45c8, pc4e6e87979b9, pf2edb8d17b19, p05e943ec08b0 |

qwen_vs_ministral

| Disagreement | Exact members |
| --- | --- |
| primitive_answer_states | scba9cc461d2b, s0d42cacc76e1, s2bb230536616, s5a4643f8f3d5, sd96aa46e6676, sfb25a574ca20, s0765f4605459, s95eb3f9311a7, s4e4487eb947a, s88cda4031925, s8c353e553e52, s93bb85d7f07a |
| reduction_answer_states | s0f8ca39efe1a, s9a67fca88b40, s6e13e0d63044, s45f64a8ae9fd, sb7e1cc7ef7e3, sccf2acfbfa18, s0bf0c65011cf, s8eba35a1979e, sacf7733e9675, s2bb230536616, s3d1adf0ce938, sa7bd8a6a8528, s6dfa7b546adb, sb8f321279191, sd96aa46e6676, saf58342c12c0, s7702e20ad7b4, s0765f4605459, sab307858b73d, s95eb3f9311a7, s7074290a7c0e, sb576e9584f1c, s4e4487eb947a, s3619d857b3d1, sfea7d23cd93b, s8c353e553e52, s059455a331cf, s93bb85d7f07a |
| primitive_pair_passes | p9147188c88d5, pfe5134c8aba6, p85beaefc6d27, p3b126a65a170, pe6150a0d0f53, p290c1440f38a, p09c35169512d, p869553eb45c8, pf2edb8d17b19, p2d668f50a4c4, pb9fcb5be062e, p05e943ec08b0 |
| reduction_pair_passes | pcb75442d46cf, pb83de3daa4c9, p9147188c88d5, pfe5134c8aba6, pfea0877e44e6, pe769b04b8bb4, p9b6e9ea58666, pe6150a0d0f53, p09c35169512d, p869553eb45c8 |

| Within-model joint outcome | Qwen | Ministral | gpt-oss |
| --- | --- | --- | --- |
| P_correct_R_correct | 41 | 23 | 40 |
| P_correct_R_wrong | 15 | 21 | 14 |
| P_wrong_R_correct | 0 | 4 | 2 |
| P_wrong_R_wrong | 0 | 8 | 0 |

## Evidence sufficiency

| Measure | Qwen | Ministral | gpt-oss |
| --- | --- | --- | --- |
| P_correct | 8 | 4 | 8 |
| P_pair_passes | 4 | 0 | 4 |
| R_correct | 3 | 2 | 6 |
| R_exact_pair_passes | 0 | 0 | 2 |

| State | Gold P | Gold R | Q P | M P | G P | Q R | M R | G R |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s4e4487eb947a | `{"answer":"DETERMINATE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s3619d857b3d1 | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |
| s88cda4031925 | `{"answer":"DETERMINATE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| sfea7d23cd93b | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` |
| s8c353e553e52 | `{"answer":"DETERMINATE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | `{"classification":"NO_SUPPORTED_DIAGNOSIS"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s059455a331cf | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"HISTORICAL_DEFECT_NOT_CURRENT"}` |
| s93bb85d7f07a | `{"answer":"DETERMINATE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` | `{"answer":"DETERMINATE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"DETERMINATE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INVALID_OR_CONTRADICTORY_EVIDENCE"}` | `{"classification":"SUPPORTED_CURRENT_DEFECT"}` |
| se8ae05e202d5 | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"answer":"UNDERDETERMINED"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` | `{"classification":"INSUFFICIENT_EVIDENCE"}` |

| Pair | Q P/R pass | M P/R pass | G P/R pass |
| --- | --- | --- | --- |
| pf2edb8d17b19 | True/False | False/False | True/True |
| p2d668f50a4c4 | True/False | False/False | True/False |
| pb9fcb5be062e | True/False | False/False | True/False |
| p05e943ec08b0 | True/False | False/False | True/True |

## Registered interpretation

```json
{
  "category": "C",
  "pattern": "SECOND_COMPARATOR_PRIMITIVE_LIMITATIONS",
  "failed_primitives": [
    "KNOWN_VS_UNKNOWN"
  ],
  "reduction_pass_despite_primitive_failure": false,
  "scope": "Frozen model/interface comparison, no deployment or intervention claim"
}
```

## Capability and real-system boundary

Qwen and Ministral capability are immutable published references. gpt-oss capability is measured only under this frozen configuration. Deterministic software verifies, transports, hashes and scores; it does not solve model tasks or pass primitive outputs into reduction. Combined-system capability and interventions are NOT TESTED. Separate primitive calls do not establish internal primitive computation during reduction. Native templates, quantization, reasoning and decoding differ across models; this is not an equal-compute or causal isolation study.

No Horus, Memory, policy, threshold, architecture or weight change occurs. No training, compiler-assisted diagnosis, model promotion or self-improvement is demonstrated. A benchmark score alone, added deterministic answer rules, prompt tuning or unmeasured model replacement is not durable useful capability. Real progress requires useful behavior surviving prospective testing, an honestly identified cause, and persistence in later operation. Separately authorized engineering may pursue that; this study does not design or build it. Comparator work stops after this publication.

## Execution and verification

Method Freeze: `2092458d12260144c2123f1460232a62bc7cd1f6`; implementation/request Freeze: `ebbdb5b6efe4bf14d34460c24b2e0fbf02e20e9a`; raw pre-scoring commit: `e827100a9e2e4b793480aa510de1906c8037bdd1`.

All 34 zero-model tests passed. Score replay is byte-identical, SHA256 `352edeb5ddec220cb4363edfda5a89c39ef77b6630c51dc12187fbf7a07d35c2`. Scientific native analysis was separated in 112/112 responses. Finish reasons: {'stop': 109, 'length': 3}. Largest completion: 8192 of 8192 permitted tokens. No post-result configuration change or extra call occurred.

All 4,175 inherited files and all 22 protected local/remote heads passed preservation checks. Full reasoning, envelopes and logs remain private outside Git. Qualification passed 22/22 task-shaped/context synthetic fixtures with active native reasoning and valid output, with complete GPU residency. See model-runtime.json for the exact model/runtime hashes and publication-audit.json for reachable ancestry audit. Final remote SHA is verified externally and reported in the handoff.

## Scientific output-limit limitation

The 8,192-token generation limit was nonbinding in all 22 synthetic qualification calls, but bound three scientific calls: one primitive and two reduction calls. Each returned an empty final and remains an invalid, incorrect endpoint under the frozen scorer. The KNOWN_VS_UNKNOWN failure combines one valid wrong answer with one output-limit failure. This establishes a limitation of the frozen model/runtime/budget configuration; it does not isolate an inherent lack of that primitive. No rerun, answer repair, budget change or counterfactual rescoring was performed.

| State | Arm | Completion tokens | Final bytes | Scored outcome |
| --- | --- | --- | --- | --- |
| s2bb230536616 | P | 8192 | 0 | Invalid / incorrect |
| sd96aa46e6676 | R | 8192 | 0 | Invalid / incorrect |
| sab307858b73d | R | 8192 | 0 | Invalid / incorrect |

## Architectural questions

1. **Does gpt-oss establish all seven primitive capabilities?** No. 6/7 gates passed; failed: KNOWN_VS_UNKNOWN.

2. **Does gpt-oss establish five-class reduction?** No. Reduction is 42/56, exact pairs 16/28, diagnostic flips 11/19 and stable retention 5/9; the exact frozen overall and class-floor gate is not established.

3. **Is Qwen’s reduction gap now supported as model-specific?** Unresolved. gpt-oss fails one or more prerequisite primitive gates, so this is not a clean reduction-specific comparator.

4. **Is the reduction problem instead supported as shared?** Unresolved as a shared reduction-only limitation. Primitive failures prevent isolating reduction difficulty, even if reduction also fails.

5. **Is Qwen unusually strong at the frozen primitives relative to both comparators?** Yes, narrowly on this frozen primitive benchmark: Qwen is the only tested model to establish every primitive gate; both independent comparators have primitive limitations. This is not a general model-quality or intelligence ranking.

6. **What architectural uncertainty has actually been resolved?** Both tested alternatives fail to establish all prerequisite primitives under their frozen interfaces. The clean reduction-specific architectural question remains unresolved, and comparator work ends here.

7. **What remains unresolved?** The causal role of model identity versus interface, decoding and reasoning allowance; whether isolated primitive success reflects internal computation during reduction; and downstream real-task, durable learning or intervention benefits remain unresolved. In particular, one failed primitive endpoint and two reduction endpoints exhausted the frozen output budget, so intrinsic model capability cannot be separated from this execution limit.

8. **Does this study itself justify changing Horus?** No. This comparator does not test an intervention or combined Horus system and does not itself justify changing or promoting one. Evidence can inform separately authorized engineering; Horus remains unchanged.

