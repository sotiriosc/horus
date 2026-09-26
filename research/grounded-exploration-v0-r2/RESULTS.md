# Horus v0.7 grounded exploration R2 result

## Result

The registered 54-decision, six-runtime R2 campaign completed with exactly 486
real model calls and no forced calibration. The result is mixed:

- Autonomous exploration acquired the evidence that exposed the B-regime
  change at `(1,HOLD)` and enabled a local G2→G3 routing switch.
- The campaign did not acquire any restoring A2 receipt and did not switch back
  G3→G2. At state 2, ADVANCE and RETREAT remained tied for the routed maximum;
  the mechanical Explorer failed closed on that tie for decisions 30–54.

Therefore autonomous adaptation is established for the observed A→B change,
but complete A→B→A adaptation is **NOT ESTABLISHED**. Under-exploration after
the return to A is the observed limitation, not an infrastructure failure.

## Lineage and runtime correction

R2 identity is `HORUS_GROUNDED_EXPLORATION_V0_R2`. It descends from the original
frozen implementation `72cdc095`, original unavailable-service evidence
`5edc8894`, and preserved R1 protected-bound failure `d5620234`. The repair was
frozen at `a460bd9106dc1c80885b50f8d6e07c3a6f190de6`.

The protected `EPISODE_LIMIT` remained 12. The 54 unchanged scientific decision
attempts were prospectively divided into six runtimes of nine attempts. All six
runtimes used fresh source identities and epochs 2001–2006. Execution counts by
runtime were 9, 9, 8, 2, 0, and 0; no runtime approached or exceeded the bound.
No `INTERNAL_ROUTE_PROBLEM` occurred.

Authenticated history survived every rollover. In runtime 2, 54 of 81 model
requests included prior exact-relation history with depth up to three. By
runtimes 5 and 6, all 81 requests included prior history. Routing and confidence
state replayed exactly across the same boundaries; old receipt objects were not
reconstructed.

## Calls and execution

| Role | Issued | Valid | Failure |
|---|---:|---:|---|
| joint next-state | 162 | 161 | one `TimeoutError` |
| G2 consequence | 162 | 162 | none |
| G3 consequence | 162 | 162 | none |
| **Total** | **486** | **485** | **one** |

The joint timeout occurred in decision 25. The frozen protocol issued no retry;
that decision abstained before execution. The persistent Ollama supervisor
remained alive through campaign completion.

There were 54 autonomous attempts, 28 authorized executions, and 26
non-executions:

- one `INVALID_MAP_COMPONENT` abstention at decision 25;
- 25 `EXPLOIT_TIED_MAXIMUM` abstentions at decisions 30–54;
- zero framework rejections.

## Exploration

Ten probes executed and 18 exploits executed.

| Probe reason | Count | Useful | Redundant |
|---|---:|---:|---:|
| `PROBE_UNTRIED` | 7 | 7 | 0 |
| `PROBE_CONTRADICTION` | 1 | 1 | 0 |
| `PROBE_STALE` | 2 | 0 | 2 |
| **Total** | **10** | **8** | **2** |

Probe rates by frozen nine-decision window were:

| Window | Probes / decisions |
|---|---:|
| early A1 | 3/9 |
| late A1 | 3/9 |
| early B | 3/9 |
| late B | 1/9 |
| early A2 | 0/9 |
| late A2 | 0/9 |

The two stale probes occurred at decisions 16 and 29. Neither resolved a
disagreement, revealed a contradiction, supplied first evidence, or contributed
to a later switch, so both are classified as redundant under the frozen
descriptive rule.

At each state's last encounter, authenticated relation coverage was 2/3 for
state 0 and 3/3 for states 1, 2, and 3. The corresponding unresolved counts were
3, 1, 2, and 1. These are last-encounter snapshots, not a claim that unvisited
relations remained current through decision 54.

## `(1,HOLD)` discovery and routing

The exact target-relation trace was:

| Decision | Phase | Mode | G2 | G3 | Receipt | Selected after |
|---:|---|---|---:|---:|---:|---|
| 11 | A1 | exploit | 1 | 1 | 1 | G2 |
| 12 | A1 | exploit | 1 | 1 | 1 | G2 |
| 15 | A1 | exploit | 1 | 1 | 1 | G2 |
| 23 | B | exploit | 1 | 1 | -1 | G2 |
| 24 | B | exploit | 1 | -1 | -1 | G2 |
| 26 | B | contradiction probe | 1 | -1 | -1 | **G3** |

Decision 23 supplied the first contradictory B receipt after three identical A
receipts. The contradiction remained unresolved until the autonomous
`PROBE_CONTRADICTION` at decision 26. That probe produced the sixth local scored
receipt and changed the six-receipt window to G2 3/6 versus G3 5/6, satisfying
the frozen two-correct-prediction lead and switching G2→G3. The switch's scoring
window includes autonomous probe 26, so probe evidence enabled the routing
change.

No later `(1,HOLD)` receipt exists. After decision 29 the system remained at
state 2 and the mechanical routed values were ADVANCE=1, HOLD=0, RETREAT=1.
The tied maximum caused fail-closed abstention through all 18 A2 decisions.
Consequently there was no first restoring A receipt and no evidence on which a
G3→G2 switchback could occur.

## Action trajectory

- A1 decisions 1–18:
  `ADVANCE, HOLD, HOLD, ADVANCE, HOLD, HOLD, ADVANCE, HOLD, HOLD, ADVANCE,
  HOLD, HOLD, RETREAT, ADVANCE, HOLD, ADVANCE, ADVANCE, HOLD`.
- B decisions 19–29:
  `RETREAT, ADVANCE, RETREAT, RETREAT, HOLD, HOLD, ABSTAIN, HOLD, RETREAT,
  ADVANCE, ADVANCE`.
- B decisions 30–36 and A2 decisions 37–54: all abstained on the unchanged
  ADVANCE/RETREAT routed-value tie.

The complete per-decision trajectory, forecasts, reasons, coverage, receipts,
and switch dependencies are retained in `exploration-report.json`.

## Exploit-only replay

Offline exploit-only comparison reused the 54 frozen pre-execution contexts and
created no counterfactual receipts. It selected the same action as the actual
policy in 45 contexts and a different action in nine. Nineteen actual receipts
were legitimate shared evidence because both policies selected the same action.
This comparison establishes decision differences only; it does not estimate
unobserved counterfactual outcomes.

## Integrity and limitations

- Exact analysis replay is byte-identical; report SHA-256 is
  `50de3429619db46d20d6d5ef2dcd277c2212ece1f3ad244cc25cf56449d4d35e`.
- All 81 package-qualified Horus tests passed after the R2 repair, and the
  documented core regression passed all 53 checks. The focused exploration
  suite passed all 23 tests again against the completed-evidence analyzer.
- Every public evidence copy matches its original completed R2 artifact, and R1
  remains byte-identical to its committed failure manifest.
- All 486 requests passed the hidden regime/router/Explorer prompt audit.
- G2 and G3 artifact hashes were reverified in every runtime.
- No weights changed, no training occurred, and G3 remained globally rejected
  while eligible only as a routed specialist.
- The campaign encountered one fail-closed transport timeout.
- The fixed tie-abstention rule prevented all A2 execution and makes switchback
  performance unobservable in this campaign.
- Results cover this bounded deterministic regime schedule and these retained
  model artifacts; they do not establish general exploration optimality.
