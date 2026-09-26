# Horus v0.10 authorized repair-resume preregistration

## Frozen lineage and question

- Parent evidence commit: `3ad28c5a22942abc12ec3532113469112be7cbc1`
- Frozen implementation commit: `49599c2`
- Source report SHA-256: `70e1b60a80bfd1e819de5e4433c912500b02f3ded4176c8ee6855a2a7c556592`
- Source problem lineage: `PR-0001 -> PR-0002`
- Source state: attempted decision 57, 52 authorized executions, state 2

The question is whether an explicitly authorized, causally safe operational
repair can resume the exact unresolved problem, acquire the missing RETREAT
receipt, and distinguish `VALUE_TIE_RESOLVED` from
`CURRENT_OBJECTIVE_CANNOT_DISTINGUISH` without converting repair into world
evidence or design authority.

## Frozen repair rule

A prediction request is reissuable only when no external action, receipt,
Memory publication, routing evidence, or training target followed the failed
batch; the decision remains unresolved; exact request bytes are retained; and
the repair has an explicit external authorization.

Attempt 1 remains a `TimeoutError`. Attempt 2 uses the same logical prediction
identity and a new transport-attempt identity. There is at most one service
restart and one reissue. A second failure produces `REPAIR_FAILED` and stops.

The service proof requires a persistent Ollama process, listener liveness,
exact `dolphin-mixtral:latest` manifest SHA-256
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`,
one infrastructure-only health response, and a valid strict joint parse.

## Frozen continuation

The unresolved decision-57 prediction batch is reconstructed from its eight
successful durable components plus only the repaired HOLD joint component.
The fresh runtime must reproduce the exact state/action/history request inputs.
The repaired batch is assigned prospective behavioral decision 58; its model
outputs remain predictions and do not authorize execution.

The coverage-first rule must select the still-unprobed RETREAT action. The
existing ADVANCE probe must not repeat. Ordinary Measure, authorization,
Memory, routing, and receipt publication remain unchanged.

After RETREAT, allow at most five fresh ordinary behavioral decisions to
return to and reassess state 2. Stop at the first terminal classification.

- Maximum behavioral decisions: 6, including the repaired RETREAT decision
- Maximum fresh ordinary prediction calls: 45
- Operational health calls: 1
- Exact repaired transport calls: 1
- Maximum total live model calls: 47
- Fresh runtimes: 1
- Training: none
- G2/G3, routing, simulator, objective, and protected episode limit: unchanged

If both tied actions have authenticated problem-specific receipts with equal
immediate consequences and the later ordinary state-2 ranking remains tied,
emit `CURRENT_OBJECTIVE_CANNOT_DISTINGUISH`, localize to `REPRESENTATION`, and
request `LONGER_HORIZON_VALUE` as `REQUEST_REQUIRES_EXTERNAL_APPROVAL`. Include
both realized next states and immediate consequences. Do not infer which
continuation is better and do not implement the requested capability.

If the grounded immediate consequences differ and the ordinary ranking is no
longer tied, emit `VALUE_TIE_RESOLVED`. If the required state-2 reassessment is
not reached within the frozen bound, report inconclusive and stop.

## Frozen implementation hashes

- `repair_resume.py`: `dea037a5e76175d106f3382e0f0e41c3648f1be321c54ddbfc832761942b0502`
- `repair_resume_policy.json`: `0fab258cbdb1fd6ca58e0decfe97f6978d31d452e3d1d26d37650eaa3a12a231`
- `capability_gap.py`: `a33f7d16755743f021a0cf125b1ac8af9f9fab6cb7ab152edc394240f5b4f844`
- `test_repair_resume.py`: `187eff734df9c6ceef5044bbe012aa2c263a932a5419d9ecf6027604acb59ce2`

## Stop rule

Run once. Preserve the outcome, including service failure, invalid response,
inconclusive continuation, or negative result. Do not retry, start another
runtime, alter the frozen rules, implement `LONGER_HORIZON_VALUE`, train, or
begin a follow-up milestone.
