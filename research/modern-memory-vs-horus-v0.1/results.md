# Modern memory versus Horus v0.1 — report

Classification: **HORUS_NET_HARMFUL**. Status: COMPLETE. The original question is answered descriptively for this frozen workload: adding Horus produced one improved and seven degraded realized comparisons, plus one no-net-effect comparison. Operational transport reliability is reported separately and does not drive this classification.

1. **Branch:** `research/modern-memory-vs-horus-v0.1`.
2. **Commit:** preregistration `d213a3b30a618da12b332a837843cd396fdbce90`; the final evidence commit is the commit containing this report. Preserved v0: `ad790661bacd63e7d9bc22988a8adfa3c41c10a2`, pushed unchanged with its INVALID classification.
3. **Pair protocol:** M prepare → MH prepare → validate both → execute independently in private transaction state → validate matching → one atomic committed-snapshot publication. Five zero-inference tests passed, including interrupted second execution. Full synthetic schedule and analysis replay passed. Live replay: PASS. The atomicity guarantee is committed visibility for simulated worlds; private sequential execution is not simultaneous external actuation.
4. **Transport rule:** at most one exact-byte reissue per eligible failed request, distinct attempt identity, failed attempt retained, no sibling regeneration or semantic retry. Rule SHA-256: `f9580f849a2baec25cda5ef9bb9eee3cf7be1d3b992411b5ba25decdfe17eb20`. See [rule](transport-rule.json).
5. **M:** authenticated append-only durable memory with receipt provenance and contradiction retention; exact relation retrieval; recent four; newest missing-consequence anchors; deterministic recency fill to six in chronological order; frozen G2 consequence specialist; common joint next-state Map; mechanical Explorer.
6. **MH:** exactly M plus frozen G3, relation-local rolling-six G2/G3 router (minimum three observations, lead two), and grounded Explorer; original projections and existing triggers. No Horus, model, prompt, memory or routing policy was changed.
7. **Schedule:** original v0 schedule reused unchanged: HOLD events 1–4 in A, 5–8 in B, 9–12 restored A; fresh-process restart and malformed-parser perturbation after event 6; then four autonomous decisions per arm in A.
8. **Ceiling:** 255 logical calls (102 M, 153 MH); at most 510 physical attempts (204 M, 306 MH).
9. **Failures/repairs:** M 0/0; MH 1/1. Unrepaired: M 0, MH 0.
10. **Stage-A invariant:** PASS; M = MH = 12 authenticated matched observations. Exact scheduled identities, independent sessions and disjoint receipt sources verified. Every published snapshot replayed.
11. **M Stage A:** 8/12 consequence-correct; 8/12 exact next-state/consequence matches.
12. **MH Stage A:** 5/12 consequence-correct; 5/12 exact matches.
13. **Correct-memory/model-wrong:** M events [6, 7, 8]; MH events [6, 7, 9, 10, 11, 12]. Full per-event RIGHT_MEMORY_PRESENT, correctness, changed output and improvement indicators are in results.json. Matching consequence presence does not establish temporal understanding.
14. **Intervention ledger:** 9 rows; effects {'DEGRADED': 7, 'IMPROVED': 1, 'NO_NET_EFFECT': 1}. Each row retains eligible raw history, supplied history, predictions, responsible mechanism and realized consequence. See [ledger](intervention-ledger.json).
15. **Adaptation/restoration:** zero-based latency from the first event in each phase: M None/0; MH 3/None. Null means no correct prediction observed within that phase. Changed-regime incorrect predictions: M 4, MH 3.
16. **Endurance:** 12/12 Stage-A observations completed per arm; phase accuracies and worst rolling four are below. This is short registered persistence, not evidence of long-horizon endurance.
17. **Restart:** PASS — registered new worker process, exact stored file/memory hashes and matched histories verified.
18. **Perturbation:** both arms rejected the intentionally malformed HOLD joint response; no external event, receipt or memory was created; ordinary event 7 followed. Injected invalidity is separate from transport and genuine model-invalid output.
19. **Stage B:** M actions ['HOLD', 'HOLD', 'HOLD', 'HOLD']; MH actions ['ADVANCE', 'HOLD', 'HOLD', 'ADVANCE']. M abstentions 0; MH abstentions 0. Full decisions, probes and receipts are in results.json.
20. **Realized consequences:** Stage-A totals M 4, MH 4; autonomous totals M 4, MH 0. No unexecuted outcome is imputed.
21. **Horus activity:** 2 specialist switches; 2 autonomous probes. Problem objects, route execution, repair recovery and reacquisition: zero; these remain dormant in the frozen harness.
22. **Operational overhead:** see the accounting table below. Prediction accuracy excludes transport failures and intentionally malformed perturbation outputs.
23. **Classification:** **HORUS_NET_HARMFUL**, using the prospectively frozen descriptive rule. It is conditional on this workload and protected/replay validity.
24. **Smallest indicated mechanisms:** relation-local specialist selection helped at Stage-A event 8 (G3 correctly predicted −1 while G2 predicted +1). The same router retained G3 through restoration events 9–12, degrading all four predictions despite correct +1 evidence being supplied. It switched back to G2 only after scoring event 12. Grounded Explorer probing chose ADVANCE at Stage-B decision 1, realizing −1 while M realized +1 and sending MH into a different state; subsequent HOLD outcomes were 0, 0. A second probe at decision 4 realized +1, equal to M at that decision. This indicates one useful routing intervention, delayed routing reversal as a harmful mechanism, and probe cost within this short horizon. There is no component ablation or evidence of longer-term probe payoff.
25. **Limitations:** Single deterministic small simulated workload; descriptive, not population inference. Atomicity is committed snapshot visibility, not simultaneous irreversible external actuation. Private transaction workspace can contain a partial pair on commit failure; it is never published or resumed. Active arm wall time excludes waiting for the sibling and model loading; worker wall time includes both. Problem/route components remain dormant in this frozen harness. Right-memory metric means a matching consequence is supplied, not that the model understood its temporal relevance.

No further tuning, training, new generation or automatic follow-up campaign was performed.

| Operational metric | M | MH |
|---|---:|---:|
| logical_model_calls | 102 | 153 |
| physical_transport_attempts | 102 | 154 |
| transport_failures | 0 | 1 |
| repaired_calls | 0 | 1 |
| unrepaired_failures | 0 | 0 |
| model_invalid_outputs | 0 | 0 |
| registered_injected_invalid_outputs | 1 | 1 |
| completion_rate | 1.000 | 1.000 |
| scheduled_stage_a_completion_rate | 1.000 | 1.000 |
| model_seconds | 1200.418 | 1633.382 |
| active_wall_seconds | 1203.958 | 1638.724 |
| context_tokens | 6678 | 8757 |

Combined worker wall time: 2865.718 seconds. Active arm wall time excludes sibling waiting and model loading. Physical-call model time includes request/response transport latency.

| Stage-A phase | M consequence / exact | MH consequence / exact |
|---|---:|---:|
| stable | 4/4 / 4/4 | 4/4 / 4/4 |
| change | 0/4 / 0/4 | 1/4 / 1/4 |
| restoration | 4/4 / 4/4 | 0/4 / 0/4 |

Worst rolling four: M `{'consequence_accuracy': 0.0, 'consequence_correct': 0, 'exact_accuracy': 0.0, 'exact_correct': 0, 'n': 4, 'start_event': 5}`; MH `{'consequence_accuracy': 0.0, 'consequence_correct': 0, 'exact_accuracy': 0.0, 'exact_correct': 0, 'n': 4, 'start_event': 9}`.

[Full results](evidence/results.json) · [Authenticated replay](evidence/replay.json) · [Preregistration](preregistration.md) · [Source manifest](source-manifest.json)


| Intervention | Mechanism | M / MH prediction or action | Realized M / MH | Effect |
|---|---|---|---|---|
| A8 | G2→G3 routing | +1 / −1 consequence | −1 / −1 | IMPROVED |
| A9–A12 | G3 retained during restoration | +1 / −1 consequence | +1 / +1 each | DEGRADED ×4 |
| B1 | Grounded Explorer probe | HOLD / ADVANCE | +1 / −1 | DEGRADED |
| B2–B3 | Diverged state following B1 | HOLD / HOLD | +1 / 0 each | DEGRADED ×2 |
| B4 | Grounded Explorer probe | HOLD / ADVANCE | +1 / +1 | NO_NET_EFFECT |

The B2–B3 rows are downstream comparisons between different actual trajectories, not isolated causal effects of a new component at those decisions. Their machine-readable mechanism label is UNATTRIBUTED_OUTPUT_DIFFERENCE; the recorded states show why the shared G2 inputs and outputs differ.

M supplied a correct changed-regime consequence but remained wrong at events 6–8. MH also remained wrong at 6–7, improved at 8 through specialist selection, and then remained wrong at restoration events 9–12 despite supplied correct evidence. Thus the study does not show a general repair of the interpretation bottleneck.

Stage-B realized sequences: M `[+1, +1, +1, +1]`; MH `[−1, 0, 0, +1]`. Both arms authorized four actions and neither abstained. The two registered perturbation abstentions were separate, non-executing parser rejections.

MH used 50% more logical calls and 50.98% more physical attempts. Measured physical-call time was 36.07% higher, including its one 600-second timeout. This timing comparison is observational and includes service latency; it is not a controlled compute-efficiency estimate.

M’s immediate restoration correctness reflects its continued +1 forecast, not demonstrated relearning: it never adapted during the changed regime. MH switched back to G2 only after the final restoration observation; there is no subsequent matched Stage-A forecast to measure that switch’s benefit. Stage A alone contains one improvement and four degradations, so the net-harmful result does not depend on assigning independent causal effects to diverged Stage-B states.
