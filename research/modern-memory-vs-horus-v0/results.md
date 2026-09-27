# Modern memory versus Horus v0 — stopped result

Status: **STOPPED**. Classification: **INVALID**.

The campaign completed four matched Stage-A events. On event 5, M completed its
prospectively ordered HOLD execution under regime B. MH then durably issued all
nine batch calls, but the ADVANCE joint next-state call ended with
`TimeoutError`. The strict parser recorded an invalid component and the existing
Horus all-components-valid rule failed closed. MH created no event-5 receipt,
Memory record, or routing evidence.

The resulting 5-versus-4 event histories are no longer a matched observation
sequence. The campaign was not continued, repaired, retried, or restarted.

## Preserved evidence

| Condition | Issued calls | Complete call chains | Authenticated events | Consequence correct | Exact correct |
|---|---:|---:|---:|---:|---:|
| M | 30 | 30 | 5 | 4/5 | 4/5 |
| MH | 45 | 45 | 4 | 4/4 | 4/4 |

All four matched events used identical stable-regime schedules and semantically
matched authenticated history. The failure occurred at the first changed-regime
event. The preregistered perturbation, fresh-process restart, restoration phase,
and autonomous Stage B were not reached.

The protected boundary remained intact through the stop: all earlier receipts
and Memory publications replay, the failed MH opportunity created no receipt or
Memory, and no unauthorized evidence entered either durable store. Exact replay
confirms 75 issued calls, no duplicate identities, M 5 authenticated events, MH
4 authenticated events, and four MH routing records.

The only narrow behavioral observation is that current Horus failed closed when
one required Map component was unavailable. It does not answer whether Horus
helps interpret grounded memory. Adaptation, restoration, endurance, autonomous
trajectory, intervention, and full component-attribution metrics are not
estimable from this stopped campaign.

## Requested report fields

1. Branch: `research/modern-memory-vs-horus-v0`.
2. Commit: recorded by the final evidence commit; the pre-inference commit is
   `c0a0e88`.
3. Protected harness: passed through the failure boundary; exact partial replay
   verifies original receipts, authenticated publications, and no MH event-5
   receipt or Memory.
4. M: authenticated append-only modern memory, exact relation, recent four,
   contradiction anchors, fill to six, G2, joint next-state Map, and mechanical
   Explorer.
5. MH: the same memory and joint Map plus frozen G2/G3 relation routing and the
   established grounded Explorer. No new Horus feature was added.
6. Schedule: four matched stable events completed; M alone completed the first
   changed event. Later change, restart, restoration, and Stage B were not run.
7. Budget: 255 preregistered calls; 75 actually issued before the mandatory
   stop; no retry.
8. Stage-A M: 4/4 on the matched prefix and 4/5 including its unmatched event 5.
9. Stage-A MH: 4/4 on the matched prefix; event 5 invalid before execution.
10. Correct-memory/model-wrong: not assessable in the planned changed regime.
11. Intervention ledger: empty; matched executed predictions were identical.
12. Adaptation/restoration: not assessable.
13. Endurance windows: not reached.
14. Restart: not reached.
15. Perturbation: the registered perturbation was not reached. The unplanned
    timeout was rejected fail-closed, with no operational retry.
16. Stage-B trajectories: not reached.
17. Realized consequences: M `[1,1,1,1,-1]`; MH `[1,1,1,1]`.
18. Horus activity: four HOLD routing records, no switch; its shadow Explorer
    proposed `PROBE_UNTRIED / ADVANCE` on each forced-observation event but did
    not control execution. Problem, scoped-route, repair, and reacquisition
    components remained dormant.
19. Overhead: 30 M calls and 45 MH calls; full latency/context comparison is not
    interpretable after the unmatched stop.
20. Classification: **INVALID**.
21. Component worth isolating: none can be selected from this invalid run. The
    fail-closed Map validity gate behaved correctly but is not an outcome gain.
22. Limitations: the comparison ended before change adaptation, restart,
    restoration, autonomous action, or any controlled Horus intervention.
