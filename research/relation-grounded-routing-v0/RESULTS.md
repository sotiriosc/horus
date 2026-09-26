# Horus v0.6 relation-grounded routing result

## Result

The bounded architecture and fixed A→B→A campaign completed. For the exact
relation `(pre_state=1, action=HOLD)`, authenticated experience changed control
from G2 to G3 after the B reversal and back from G3 to G2 after the A2
restoration. Both adapters and all earlier Memory records remained unchanged.

This establishes the requested mechanism in one small deterministic campaign:
receipt-scored evidence can change which retained specialist governs one exact
relation and later change it back. It does not establish a general relation
representation or aggregate performance advantage.

## Frozen rule and identity

The routing identity was exactly `(pre_state, action)`, based on authenticated
action identity rather than presentation alias. Each relation cold-started at
G2, used its own most recent six shared receipt-scored observations, required at
least three observations, and switched only when the challenger led by at least
two correct predictions. Ties retained the local incumbent, with the same
hysteresis after switching.

G2 remained globally `ACTIVE` and G3 remained globally `REJECTED`; both were
`ROUTABLE_SPECIALIST`. The pool contained exactly these artifacts:

- G2: `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a`
- G3: `edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24`

The relation-routing registry payload SHA-256 is
`a9b04335dec7eaeacf267a858315bbd474555fdbd0fefd4dbaae99c28a2dc664`.
No model, router, Explorer, or next-state component was trained.

## Exact schedule and calls

| Segment | Hidden regime | Work | Calls |
|---|---|---|---:|
| A1 | A | six target calibrations; one nonexecuting ordinary comparison | 63 |
| B1 | B | three target calibrations | 27 |
| B2 | B | three target calibrations after restart; one nonexecuting ordinary comparison | 36 |
| A2 | A | six target calibrations; one ordinary production execution | 63 |

The campaign issued exactly 189 real model calls: 63 joint next-state, 63 G2
consequence, and 63 G3 consequence calls. All 21 prediction batches completed.
All 19 scheduled executions produced authorized original receipts: 18 clearly
labeled `ROUTING_CALIBRATION_EXECUTION` and one
`EXPLORER_SELECTED_EXECUTION`. No retry, replacement call, synthetic outcome,
or outcome-based extension occurred.

## Complete `(1,HOLD)` receipt trace

Receipt source abbreviations expand to:

- R1: `HORUS:fc3ca9b9fb46c8652ed6779e8a68d1aa:runtime:1:6377b05d180b686e`
- R2: `HORUS:fc3ca9b9fb46c8652ed6779e8a68d1aa:runtime:2:075d0570ca138bfe`
- R3: `HORUS:fc3ca9b9fb46c8652ed6779e8a68d1aa:runtime:3:6131f7755c2fdccf`
- R4: `HORUS:fc3ca9b9fb46c8652ed6779e8a68d1aa:runtime:4:14adb2f663d930d6`

The receipt column is `source/event/epoch/transaction`.
The final column gives the two correct-count numerators, G2/G3, in the local
window; its common denominator is the evidence count up to six.

| Evidence | Phase | Kind | Receipt | G2 | G3 | Realized | Local selection | Score after G2/G3 |
|---:|---|---|---|---:|---:|---:|---|---|
| 1 | A1 | calibration | R1/1/2001/1 | +1 | +1 | +1 | G2→G2 | 1/1 |
| 2 | A1 | calibration | R1/2/2001/2 | +1 | +1 | +1 | G2→G2 | 2/2 |
| 3 | A1 | calibration | R1/3/2001/3 | +1 | +1 | +1 | G2→G2 | 3/3 |
| 4 | A1 | calibration | R1/4/2001/4 | +1 | +1 | +1 | G2→G2 | 4/4 |
| 5 | A1 | calibration | R1/5/2001/5 | +1 | +1 | +1 | G2→G2 | 5/5 |
| 6 | A1 | calibration | R1/6/2001/6 | +1 | +1 | +1 | G2→G2 | 6/6 |
| 7 | B | calibration | R2/1/2002/1 | +1 | +1 | -1 | G2→G2 | 5/5 |
| 8 | B | calibration | R2/2/2002/2 | +1 | -1 | -1 | G2→G2 | 4/5 |
| 9 | B | calibration | R2/3/2002/3 | +1 | -1 | -1 | **G2→G3** | 3/5 |
| 10 | B | calibration | R3/1/2003/1 | +1 | -1 | -1 | G3→G3 | 2/5 |
| 11 | B | calibration | R3/2/2003/2 | +1 | -1 | -1 | G3→G3 | 1/5 |
| 12 | B | calibration | R3/3/2003/3 | +1 | -1 | -1 | G3→G3 | 0/5 |
| 13 | A2 | calibration | R4/1/2004/1 | +1 | -1 | +1 | G3→G3 | 1/5 |
| 14 | A2 | calibration | R4/2/2004/2 | +1 | -1 | +1 | G3→G3 | 2/4 |
| 15 | A2 | calibration | R4/3/2004/3 | +1 | -1 | +1 | G3→G3 | 3/3 |
| 16 | A2 | calibration | R4/4/2004/4 | +1 | -1 | +1 | **G3→G2** | 4/2 |
| 17 | A2 | calibration | R4/5/2004/5 | +1 | -1 | +1 | G2→G2 | 5/1 |
| 18 | A2 | calibration | R4/6/2004/6 | +1 | -1 | +1 | G2→G2 | 6/0 |
| 19 | A2 | Explorer-selected | R4/7/2004/7 | +1 | +1 | +1 | G2→G2 | 6/1 |

Every table row is backed by the full receipt identity, receipt provenance hash,
context hash, artifact hashes, prediction commitments, and local before/after
scores in `routing-evidence.jsonl` and `routing-report.json`.

## Switches and latency

The first A→B contradiction was evidence 7. Evidence 9 produced G2 3/6 and
G3 5/6, so the exact two-answer lead switched `(1,HOLD)` from G2 to G3. The
latency was three authenticated B observations including the first
contradiction, or two additional observations after it.

The first B→A2 restoring contradiction was evidence 13. Evidence 16 produced
G2 4/6 and G3 2/6, switching the same relation from G3 back to G2. The latency
was four authenticated A2 observations including the first restoration, or
three additional observations after it.

The final state-1 routing table was:

| Relation | Local evidence | Final specialist | Final score G2/G3 |
|---|---:|---|---|
| `(1, ADVANCE)` | 0 | G2 | 0/0 |
| `(1, HOLD)` | 19 | G2 | 6/1 |
| `(1, RETREAT)` | 0 | G2 | 0/0 |

Between evidence 9 and 16, batches 11–18 simultaneously used G2 for ADVANCE,
G3 for HOLD, and G2 for RETREAT. Thus the target evidence did not leak into
the other action relations.

## Global versus local replay

The v0.5 global router was replayed offline over the identical frozen
predictions and receipts, with no model calls. Because every scored action in
the campaign was HOLD, the global and local routers switched the executed
relation at the same evidence points, 9 and 16, and had zero disagreements on
the executed relation.

Their treatment of unexecuted relations differed. During batches 11–18, the
global router applied G3 to ADVANCE, HOLD, and RETREAT, while the local router
applied G3 only to HOLD and retained G2 for ADVANCE and RETREAT. This is the
intended evidence-isolation distinction. It is a selection comparison, not a
counterfactual outcome claim.

## Ordinary decisions

At A1, G2-only chose HOLD, G3-only chose ADVANCE, and local routing chose HOLD;
the comparison was intentionally not executed.

The fixed B comparison batch preserved the mixed specialist selection, but its
HOLD joint next-state request reached the existing 600-second transport timeout.
All three Explorer policies therefore abstained on an invalid component set.
No retry or replacement call was made, and no receipt or routing evidence was
created from that batch. The campaign had 188 valid model responses and this
one timed-out response.

The final A2 production batch produced G2-only=HOLD, G3-only=ADVANCE, and
relation-routed=HOLD. Horus executed only the routed HOLD path and received
`+1`. The routed decision differed from G3-only but matched G2-only; by then
all three local relations selected G2. This run therefore does not establish
that a simultaneously mixed local selection changed an executed production
choice. During mixed-selection calibration batches, the computed routed choice
was ADVANCE while the registered calibration path still executed HOLD; those
forced events are not presented as Explorer choices.

## Restart, Memory, and integrity

The required restart occurred after evidence 9. Runtime 3 reverified both
artifact hashes, recovered HOLD→G3, retained ADVANCE/RETREAT as independent G2
cold starts, and continued with a fresh source identity and epoch. Twelve
post-restart model requests carried permitted imported authenticated history.
Both artifacts were reverified in all four runtimes.

Memory preserves the exact chronological target consequences:

```text
+1 +1 +1 +1 +1 +1
-1 -1 -1 -1 -1 -1
+1 +1 +1 +1 +1 +1 +1
```

No earlier record was overwritten or treated as corruption. A fresh process
after inference authenticated 19 events, 567 ordered call records, 21 decision
records, 19 routing records, all receipt bindings, and the complete router
replay. All 189 model requests passed the hidden-regime and router-state prompt
audit.

The final validation passed all 58 Horus unit/lifecycle/routing tests and all
53 core regression steps. The new tests cover relation isolation, cross-action
non-borrowing, minimum evidence, both switch directions, ties, hysteresis,
simultaneous specialist selections, receipt-only updates, rejection of
untrusted/corrupt state, restart continuity, hidden-label exclusion, causal
prediction ordering, contradiction preservation, calibration provenance, and
lifecycle separation.

## Limitations

This is one deterministic state/action relation and one 19-receipt trajectory.
Eighteen actions were forced calibration probes, so they do not demonstrate
ordinary Explorer visitation. The B ordinary comparison was invalid and could
not test a production choice at the strongest mixed-routing point. The offline
global and local routers switched HOLD identically because the executed stream
contained no other relation, so no executed-outcome benefit of isolation was
measured. The only ordinary production execution occurred after switchback,
when every state-1 relation selected G2.

The `(pre_state, action)` key does not generalize evidence across related
states, aliases, or dynamics and may fragment evidence in larger systems. No
claim is made about learned causality, broad mixture-of-experts behavior,
stochastic environments, more specialists, or long-run adaptation.
