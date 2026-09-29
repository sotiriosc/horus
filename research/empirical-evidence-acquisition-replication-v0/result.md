# Frozen empirical evidence acquisition E — replication v0

**Classification: `EMPIRICAL_EVIDENCE_ACQUISITION_REPLICATED`. Recommendation: `CONSIDER_PROMOTION_E`.** This recommendation does not activate E. The completed Phase 4 evaluation, frozen candidate, promoted S, and active grounded-authority incumbent are unchanged. This study establishes bounded mechanism behavior in registered contexts; it makes no reward-improvement claim.

The protocol, world schedules, relation types and acquisition outcomes were committed at `814d7e2` before any execution. Candidate SHA-256 remained `fcef478a02beb69a1d29988c5ce12929ad2ba077591131e0dcd114e7ccab99b4`. Across **26 matched cases and 52 independent protected arms**, all **9 eligible cases triggered**, all **17 boundary controls stayed silent**, and every acquisition changed its target relation from UNSEEN/count 0 to observed/count exactly 1. All **P1–P10 passed**, with **zero unsafe boundary triggers** and **zero Qwen, Dolphin or other model calls**. No model training occurred.

| Case | Repeated relation | E target | C consequence | E consequence | E next state |
| --- | --- | --- | --- | --- | --- |
| R1 | 0:ADVANCE | HOLD | 0 | +1 | 0 |
| R2 | 2:RETREAT | ADVANCE | 0 | 0 | 2 |
| R3 | 1:HOLD | ADVANCE | 0 | -1 | 1 |
| R4 | 0:RETREAT | HOLD | 0 | +1 | 0 |
| R5 | 2:ADVANCE | HOLD | +1 | 0 | 2 |
| R6 | 1:RETREAT | ADVANCE | 0 | -1 | 1 |
| R7 | 2:HOLD | RETREAT | 0 | -1 | 2 |
| R8 | 1:ADVANCE | HOLD | 0 | 0 | 2 (from 1) |
| R9 | 2:RETREAT | ADVANCE | 0 | +1 | 2 |

Acquisition costs were **3 positive, 3 neutral, 3 negative**, including one neutral state transition. All negative receipts remained -1. R8 accepted the authentic transition and did not return automatically. The C arm continued the registered empirical action; it is a scientific control, not a surrogate for Dolphin/Qwen behavior. These consequences are descriptive, not an aggregate reward-benefit argument. See [cost-audit.json](cost-audit.json).

Eligible trigger rates by repeated action were **ADVANCE 3/3, HOLD 2/2, RETREAT 4/4**, across eight distinct state/action relations. Correct-target rates were ADVANCE 4/4, HOLD 4/4, RETREAT 1/1. All six action-list and assessment-dictionary permutations returned identical candidate outputs in both arms of every case: 312 boundary permutation checks. The harness explicitly supplied registered empirical relation types through the existing typed grounded-state API. No action-name condition was added to E, and no deployed relation map was changed. See [order-invariance-audit.json](order-invariance-audit.json).

Every acquisition immediately broke eligibility. R3 rebuilt four fresh HOLD observations and remained ineligible at counts 1–3, then requalified at 4 for still-unseen RETREAT. R5 rebuilt four ADVANCE observations but remained ineligible throughout because restored positive evidence failed H2. R1's two arms reconstructed suffix 3 in fresh processes before their fourth observations; R2's two arms reconstructed full eligibility exactly; R8 E reconstructed post-acquisition ineligibility. All five restart checks passed without mutable reset state. See [requalification-audit.json](requalification-audit.json) and [restart-audit.json](restart-audit.json).

The hard controls include exact +1 sign boundaries, strongly positive empirical history with missing alternatives, isolated anomalies, benign variability, possible change, established deterministic +1, observed/unresolved alternatives, broken suffixes and malformed history. C15 produced two genuine original receipts whose deliberately misbound evidence submissions were rejected; neither entered Memory. Their authenticated rejection records remained in the complete candidate projection and broke the suffix. C16's omitted first projection element caused ValueError and no acquisition output; the controller used the registered continuation. These are registered input/authorization challenges, not fabricated grounded evidence.

Signal timing is explicit in the protected action timelines. On the common R9/C17 shift prefix, observation 10 produced POSSIBLE_REGIME_CHANGE and E stayed off. Observation 11 confirmed the observed change but cumulative sum remained +1, so E stayed off. Observation 12 reached recent=-4/cumulative=0 and turned E on; observation 13 kept it on. R9 then acquired evidence and reset. On C17's restoration prefix, observation 14 kept E on (recent=-2/cumulative=0); observation 15 turned it off because cumulative became +1 while recent=0; observation 16 kept it off with recent=+2/cumulative=+2. C17's registered evaluation boundary is after observation 16. Prefix eligibility is recorded prospectively, but setup does not execute E; zero unsafe triggers refers to the registered control boundaries. No hidden regime was inferred.

Independent replay passed for **416 authorized original receipts and Memory admissions**, plus the two separately retained rejected receipts. It checked every authorized action's grounded before/after state, world schedule, receipt identity/hash, source/action binding and absence of model requests. A supplemental independent replay checked all 416 post-action candidate results and exact trigger source/reason. All 29 applicable frozen-candidate, grounded-state, S and incumbent-promotion regression tests passed. See [protected-path-audit.json](protected-path-audit.json), [supplemental-integrity-audit.json](supplemental-integrity-audit.json), and [prediction-audit.json](prediction-audit.json).

Complete private authenticated evidence is preserved locally at archive commit `8809373e8a7565dd0b20bbd367cb926f1809cab5`, branch `research/empirical-evidence-acquisition-replication-v0-private-archive`. All **482 private artifact hashes** match the archival copy, and that private commit is absent from publication ancestry. Only sanitized results, source and hashes are published. The full reachable-history secret audit is recorded separately in [reachable-history-audit.json](reachable-history-audit.json).

The result supports considering a separately reviewed promotion, not claiming universal safety, acceptable costs in every world, or successful autonomous-model integration. The study-local empirical typing and rejection-projection adapter would need explicit review in any integration. The frozen candidate and all active/historical source files remain unchanged. Work stops here: no activation, selector change, model inference, training or further campaign.
