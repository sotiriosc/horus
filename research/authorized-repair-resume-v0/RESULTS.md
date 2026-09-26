# Horus v0.10 authorized repair-resume results

## Result

The single authorized operational repair succeeded. Horus retained the v0.9
timeout, restarted and verified the frozen model service once, reissued the
exact unresolved request once under a new transport identity, and resumed the
unchanged `PR-0001 -> PR-0002` problem. It then acquired the missing
problem-specific RETREAT receipt without repeating ADVANCE.

The bounded continuation ended honestly as `INCONCLUSIVE_AT_BOUND`. Both tied
actions now have authenticated immediate consequence +1, with distinct
realized continuation states, but the unchanged Explorer did not return from
state 1 to state 2 for the required ordinary reassessment within the five
fresh-decision allowance. Therefore v0.10 does not establish
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`, does not establish
`VALUE_TIE_RESOLVED`, and did not emit `LONGER_HORIZON_VALUE`.

## Repair lineage and authority

- Branch: `build/horus-v0.10-authorized-repair-resume`
- Parent v0.9: `3ad28c5a22942abc12ec3532113469112be7cbc1`
- Implementation: `49599c2`
- Preregistration: `f2586c3`
- Preflight: `7497074`
- Failed logical prediction:
  `a67e675004193a13c31485bad53fbb86:e2007:b57:HOLD:J`
- Request SHA-256:
  `beb7997f877f396815a9e3100e35db6314f0e967ce03c2565bf74746edbf6e22`
- Attempt 1: retained `TimeoutError`
- Attempt 2: same logical prediction, new transport identity, valid strict parse

The lifecycle replayed as `REQUESTED -> AUTHORIZED -> REPAIR_ATTEMPTED ->
REPAIR_SUCCEEDED -> REISSUE_ATTEMPTED -> RESUMED`. There was one restart and
one reissue. Repair records created no receipt, Memory record, routing
evidence, training target, or world action.

The broker allowed only `RESTART_MODEL_SERVICE`, `VERIFY_MODEL_ARTIFACT`, and
`REISSUE_UNEXECUTED_PREDICTION_REQUEST`. It could not train, change the
architecture or objective, synthesize a receipt, or execute a world action.

## Service restoration

The persistent Ollama process and `127.0.0.1:11434` listener were live before
reissue. The installed `dolphin-mixtral:latest` manifest matched SHA-256
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
The one infrastructure-only health call completed with a valid strict joint
parse. It was not published as behavioral evidence.

## Live continuation

| Measure | Result |
|---|---:|
| Operational health calls | 1 |
| Exact repaired transport calls | 1 |
| Fresh ordinary prediction calls | 45 |
| Total live calls | 47 / 47 maximum |
| Behavioral decisions | 6 / 6 maximum |
| Authorized executions | 1 |
| Abstentions | 5 |
| Fresh runtimes | 1 |
| Training runs | 0 |

Decision 58 used the reconstructed valid state-2 batch and selected RETREAT by
the frozen coverage-first rule. Its ordinary execution produced consequence
+1 and next state 1. Decision 59 had one fresh joint `TimeoutError` and
abstained; it was not eligible for another repair because the one-repair bound
was consumed. Decisions 60–63 had valid predictions but tied state-1 maxima;
the unchanged Explorer abstained because its ordinary probe budget was
unavailable. No action occurred during those five decisions.

## Completed problem-specific evidence

| Action | Decision | Predicted next state | Realized consequence | Realized next state |
|---|---:|---:|---:|---:|
| ADVANCE | 55 | 3 | +1 | 3 |
| RETREAT | 58 | 1 | +1 | 1 |

Immediate consequences are equal, while authenticated continuation states
differ. That observation alone does not identify which continuation is
better. The frozen classification also requires a later valid ordinary
state-2 tied ranking, which did not occur.

The current retained request remains `MORE_RELATION_EVIDENCE`, localized to
`EVIDENCE_COVERAGE`, through the already implemented behavioral route. This
result does not grant or request a new run. `LONGER_HORIZON_VALUE` remains
external-approval-only and unimplemented.

## Verification and limitations

The v0.9 source session and registry commitments were unchanged after the
campaign. The private repair journal, private transport-attempt journal,
session, routing, exploration, and capability-gap stores all reopened and
replayed successfully. Two independently serialized public reports were
byte-identical before public-path scrubbing. The committed public report has
SHA-256 `4c9e19a7f9fdb9f7b2402d6c6279770243224972b28226169c091f6fa51591d0`.

- 16/16 focused v0.10 tests passed.
- 130/130 full Horus Python tests passed in 26.916 seconds.
- 53/53 core regression steps passed.
- No raw private model-call stream, repair key, authority key, prompt, or model
  response is included in public evidence.

The operational repair route is established, as is acquisition of the missing
RETREAT receipt. The capability question remains unresolved because the
bounded unchanged policy could not revisit state 2. Extending the decision
bound or changing the state-1 action policy would require a new prospective
authorization and cannot be inferred from this run.
