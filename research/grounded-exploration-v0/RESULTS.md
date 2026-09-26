# Horus v0.7 grounded exploration result

## Result

The fixed 54-decision A→B→A schedule completed, but the research question is
**NOT ESTABLISHED because of an external joint-model service failure**.

All 162 joint next-state calls ended with `URLError`. Both retained consequence
specialists remained healthy: all 162 G2 and all 162 G3 responses parsed. Since
each action requires the joint next-state component, every one of the 54
autonomous decisions failed closed before action execution. There were zero
receipts, zero Memory publications, zero routing observations, and zero probes
or exploits. No retry or replacement campaign was run.

This is valid evidence for fail-closed behavior, pre-execution reason integrity,
fixed scheduling, and restart persistence. It provides no evidence about whether
grounded exploration discovers a changing relation.

## Frozen rule

The implementation was committed before live inference at `72cdc09`. Relation
identity remained exactly `(pre_state, action)`. Local routing retained the
v0.6 six-observation window, minimum three observations, two-correct-prediction
challenger lead, G2 cold start, and incumbent-preserving ties.

Probe priority was frozen as:

1. `PROBE_CONTRADICTION`
2. `PROBE_UNTRIED`
3. `PROBE_DISAGREEMENT`
4. `PROBE_STALE`

Relations become stale after eight completed executions without local
execution. Disagreement is unresolved without at least three observations and
an absolute two-correct-prediction lead. Contradiction uses an immediately prior
run of three identical authenticated outcomes and resolves on the same
qualifying local lead. A probe requires a distance of three completed decisions
from the prior probe. Ties use oldest execution and canonical action order.

The Explorer decision, action, reason, forecasts, and confidence record were
HMAC-frozen before any possible external execution. Only an authorized original
receipt could update confidence, Memory, or routing.

## Schedule and calls

| Segment | External regime | Attempts | Calls | Executions |
|---|---|---:|---:|---:|
| A1 | A | 18 | 162 | 0 |
| B1 | B | 9 | 81 | 0 |
| B2, after restart | B | 9 | 81 | 0 |
| A2 | A | 18 | 162 | 0 |
| **Total** | A→B→A | **54** | **486** | **0** |

The exact role totals were 162 joint next-state, 162 G2 consequence, and 162 G3
consequence calls. The private call stream contains 1,458 authenticated records
(request, response, parse for every issued call). No extra call was issued.

## Failure diagnosis

| Role | Issued | Valid | Failure |
|---|---:|---:|---|
| joint next-state | 162 | 0 | 162 `URLError` |
| G2 consequence | 162 | 162 | none |
| G3 consequence | 162 | 162 | none |

The local Ollama process had been started by a transient command environment and
was terminated when that launcher exited. The persistent campaign then reached
an unavailable joint endpoint. This was not a model-format failure and did not
affect the two local Qwen specialist paths.

## Autonomous behavior and coverage

All 54 attempts recorded `ABSTAIN / INVALID_MAP_COMPONENT`. Therefore:

- probes by reason: none;
- exploits: none;
- useful probes: 0;
- redundant probes: 0;
- probe rate in early/late A, B, and A2: 0/9 in every interval;
- `(1,HOLD)` discovery trace: empty;
- G2→G3 switch: not observed;
- G3→G2 switchback: not observed;
- switch dependence on autonomous probe evidence: not applicable.

State 1 was the only encountered state. At every decision it had three legal
relations, zero relations with authenticated evidence, zero recently grounded
relations, and three unresolved relations. No evidence was invented to improve
coverage.

## Exploit-only replay

The offline exploit-only replay also abstained on the same invalid joint
component in all 54 frozen contexts. It produced zero legitimate shared
receipts, zero counterfactual receipts, and no information-acquisition
comparison. The comparison is inconclusive rather than a tie between policies.

## Restart and integrity

The required restart boundary was preserved: runtimes 2 and 3 covered the two B
segments, with 27 decision attempts on each side of the restart. Confidence
state replayed exactly, probe-budget state remained empty, and fresh source and
epoch identities were created in all four runtimes. Both specialist artifact
hashes were reverified on every runtime:

- G2: `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a`
- G3: `edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24`

G2 remained globally `ACTIVE`; G3 remained globally `REJECTED` and only
`ROUTABLE_SPECIALIST`. No weights changed and no training occurred. All 486
requests passed the hidden-regime/router/Explorer-state prompt audit.

The final authenticated state contains 54 attempted decisions, zero authorized
decisions, 108 exploration freeze/completion records, no pending decision, no
relation routing records, and no Memory events. The absence of receipts is the
correct fail-closed outcome for invalid required predictions.

## Narrowest defensible conclusion

Horus v0.7 mechanically preserved the frozen schedule, authenticated each
pre-execution decision, survived the planned restart, and refused all execution
when its required joint component was unavailable. The campaign does **not**
answer whether the Explorer can autonomously acquire evidence, detect the B
change, switch G2→G3, or switch back G3→G2.

A replacement campaign would require explicit authorization because this run
already issued its frozen 486 calls. None was started automatically.
