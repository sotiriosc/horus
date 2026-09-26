# Horus v0.5 grounded expert-routing result

## Decision

The bounded implementation and A→B→A run completed. Horus retained the exact
generation-2 and pure generation-3 adapters without updating either adapter or
training the router. Both specialists predicted before every execution, and
both predictions were scored only after the matching authorized original
receipt.

The router switched from G2 to G3 during B, but did not switch back during A2.
This is a mixed result. It establishes the intended authenticated routing and
restart mechanics on this run. It does not establish reliable context-sensitive
recovery: G2 and G3 tied throughout A2 at the aggregate and final-window levels,
so the frozen rule had no grounded reason to return control to G2.

## Retained specialists and lifecycle

The routing pool contained exactly two specialists. Generation 3R was excluded.

| Specialist | Generation | Artifact SHA-256 | Global lifecycle | Routing eligibility |
|---|---:|---|---|---|
| G2 | 2 | `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a` | `ACTIVE` | `ROUTABLE_SPECIALIST` |
| G3 | 3 | `edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24` | `REJECTED` | `ROUTABLE_SPECIALIST` |

The routing registry payload SHA-256 is
`df3bdedda64941fe6fb634e4250035dd95bfc9cf565bf4799e76b879590ae91b`.
It binds the artifact, lineage, source-generation manifest, base-model identity,
global lifecycle status, and independent routing eligibility for each
specialist. The v0.4 lifecycle decision was not rewritten. The source v0.4
registry state remained
`fcb3207684f13c092e76bf7c91e97a28701f5eb88a9bb7a83ebe3be107b5b05d`.

## Frozen router and schedule

The policy SHA-256 is
`8bc94d20875ea303f50062f4708a91bb6b748c68fa7d3cdff7147bc4784743e8`.
G2 was the cold-start default. The router considered the most recent six shared,
authorized, receipt-scored events; required at least four shared events; and
switched only when the challenger led the incumbent by at least two correct
predictions. Ties retained the incumbent, and the same hysteresis applied after
a switch.

The prospective schedule was executed without extension:

| Phase | Hidden simulator regime | Attempts/executions | Runtime |
|---|---|---:|---:|
| A1 | A | 12/12 | 1 |
| B first half | B | 6/6 | 2 |
| B after required restart | B | 6/6 | 3 |
| A2 | A | 12/12 | 4 |

Each attempt made three joint next-state calls, three G2 consequence calls, and
three G3 consequence calls. The run therefore made exactly 324 real model calls:
108 for each role. All 36 attempts executed; there were no retries, extra calls,
nonexecuted attempts, or invalid specialist predictions.

## Phase results

All shadow accuracies below score the already-frozen prediction on the action
the routed system actually executed. They do not claim what action or outcome a
single-specialist policy would have produced.

| Phase | Selected specialist distribution | G2 | G3 | Routed | Actions | Realized consequences | Switches |
|---|---|---:|---:|---:|---|---|---|
| A1 | G2 12 | 12/12 | 12/12 | 12/12 | HOLD 12 | `+1`: 12 | none |
| B | G2 3, G3 9 | 5/12 | 7/12 | 5/12 | ADVANCE 7, HOLD 4, RETREAT 1 | `-1`: 4, `0`: 2, `+1`: 6 | G2→G3 at evidence 15 |
| A2 | G3 12 | 11/12 | 11/12 | 11/12 | ADVANCE 6, RETREAT 6 | `+1`: 12 | none |

Overall routed accuracy was 28/36 (77.8%). Always-G2 was 28/36 and always-G3
was 30/36 on the same executed actions. The worst routed rolling six-event
window was 1/6 beginning at evidence 13.

A1 did not distinguish the specialists: both were 12/12, so G2 remained in
control by the cold-start and tie rules. B favored G3 by two correct predictions
overall. A2 again did not distinguish them: both were 11/12, and both were 6/6
in the final routing window.

## Switch evidence

The first contradictory receipt was evidence 13: the same observed state-1
`HOLD` relation that had produced `+1` in A1 produced `-1` in B. At evidence 15,
the six-event grounded scores became G2 3/6 and G3 5/6. That exact two-answer
lead satisfied the frozen rule, so control changed from G2 to G3 for the next
decision. The recorded delay was two scored events after the first
contradictory receipt.

There were no other switches. Under the frozen descriptive test, the switch was
not classified as unnecessary: over the next four executed events the former
and new specialists were each correct once, so the former did not exceed the
new specialist by two. This label does not show that the switch improved those
four events; their observed scores were tied.

No G3→G2 switchback occurred. A2 contained no first receipt on which G2 became
correct while G3 was wrong, and consequently no qualifying contradiction or
lead developed. Final selection remained G3.

## Causal and restart integrity

The durable call stream contains 972 ordered records: nine request intents,
then a response and durable parse for each of the nine calls on every attempt.
All 324 prompt audits excluded the simulator regime and router selection. Each
routing record binds the context hash, both artifact identities, both frozen
selected-action forecasts, prediction call commitments, selected specialist,
selected action, authorized receipt identity and provenance, realized
consequence, both correctness values, before/after scores, and switch result.

The B restart occurred after exactly six B attempts. Runtimes 2 and 3 have
different authenticated source identities and epochs. Both specialist artifacts
were reverified in every one of the four runtimes. Runtime 3 preserved the G3
selection, authenticated routing evidence, chronological Memory, and imported
history. Twenty-four post-restart specialist requests carried permitted old
authenticated history. No hidden regime value was restored into model input.

A fresh process after the campaign authenticated all 36 session events, all
972 call records, all 36 routing records, their receipt bindings, and the
router replay. It recovered G3 with final scores G2 6/6 and G3 6/6.

## Chronological contradiction

Memory retained the 12 A1 `state 1 / HOLD → +1` receipts followed by three B
`state 1 / HOLD → -1` receipts. The earlier facts were not overwritten or
classified as corrupt. A2 produced 12 new `+1` receipts, but its realized
trajectory used ADVANCE and RETREAT from other states; it did not revisit the
same `state 1 / HOLD` relation. This run therefore preserves an old→new
same-relation contradiction, but does not contain a same-relation old→new→old
triple.

## Tests and public evidence

The routing suite contains eight tests covering cold start, minimum evidence,
deterministic G2→G3 and G3→G2 transitions, tie retention, hysteresis, corrupted
evidence, restart continuity, hidden-label exclusion, prediction ordering,
receipt-only updates, lifecycle separation, missing lineage, and the exact
two-specialist pool. The complete repository regression also covers the prior
Horus architecture and lifecycle milestones. At completion, all 52 Horus
unit/lifecycle/routing tests passed, and `make test` passed all 53 core checks.

`routing-report.json` is the compact frozen analysis. `routing-evidence.jsonl`
is the exact append-only receipt-linked routing stream. `routing-registry.json`
and `router-state.json` preserve the exact registry and final router checkpoint.
The stream retains its original HMAC tags and SHA-256 links, while the private
HMAC authority key is deliberately excluded. Raw prompts/responses, the private
session authority key, and private checkpoints are also excluded.

## Limitations

This was one 36-decision trajectory in a deterministic four-state world. The
specialists tied in both A phases, so the experiment did not show that G2 was
preferable under old reality or that the router could restore it after B. The
router matched always-G2 and trailed always-G3 by two correct predictions on the
executed actions. Because each policy could have selected different actions,
these shadow scores are not counterfactual outcome comparisons.

The single observed switch occurred during the worst 1/6 routed window, and the
next-four assessment was tied; this run establishes mechanical responsiveness,
not improved control performance. The exact same-relation contradiction was not
revisited in A2, limiting the switchback test. No claim is made about general
mixture-of-experts behavior, hidden regimes outside this simulator, longer-term
stability, or the usefulness of additional specialists. No model, Explorer,
next-state path, or router was trained in v0.5.
