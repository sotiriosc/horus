# Grounded uncertainty state v0: completed interpretation

**Classification: `EXPLICIT_UNCERTAINTY_SUPPORTED`.** The system can represent “one contradictory receipt; change is unresolved” separately from “the relation has been established at the new value.” It did so after every first contradiction in this campaign. This supports a cleaner evidence architecture than presenting a forced point forecast as knowledge. It does **not** show that U is the best point predictor, or that two matching receipts prove indefinite persistence.

The [preregistration](preregistration.md) and [source manifest](source-manifest.json) were committed before live inference. The protected four-arm campaign produced 41 matched authenticated observations per arm across four new schedules: sustained change and restoration, isolated anomaly, two-event excursion, and noise followed by genuine change, restoration, and two previously unseen exact relations. A and B legitimately yielded +1 and −1 for `1:HOLD`; `2:HOLD` yielded 0 in the existing world. No regime or protected transition rule was added.

## Primary state result

Across the 41 U observations, there were eight first contradictions with an established exact relation. **All eight became `UNRESOLVED_CHANGE`** immediately after their authenticated receipt; missed ambiguity was 0. Every one resolved under the frozen rule after **one additional receipt**. Sustained changes confirmed the candidate, single-event anomalies rejected it, and restorations confirmed the old-world value as the new established value after the second matching receipt. Post-event U was established at 33 events and unresolved at eight. Receipt provenance was complete, and the fresh-process restart exactly recovered the established +1 value, −1 candidate, candidate count 1, and supporting receipt identities. The malformed model operation produced no authorized receipt and left U state byte-identical.

The four schedules shared the same three +1 `1:HOLD` receipts followed by one −1 value at event 4, disregarding run-specific receipt IDs that reveal no regime. At that point the next receipt was −1 in sustained/excursion runs but +1 in anomaly/noise-before-change runs. All four corresponding unresolved events therefore earned `EVIDENCE_INSUFFICIENT_TO_DISTINGUISH`. Four other unresolved prefixes had no divergent twin among the *frozen* schedules; that absence does not establish that reality was distinguishable. The evidence boundary, rather than a model failure, explains why U did not call the first −1 a confirmed change.

The two-event excursion shows the limit of the update rule. Its second −1 established −1; the following +1 reopened uncertainty, and another +1 established restoration. Two consecutive receipts support confirmation by the registered policy but do not establish whether the segment will persist. The preregistered “false certainty” measure counts **8/27** established pre-event states whose *next* value differed, all at transition boundaries. Those mismatches cannot be foreseen from exact-relation receipts before they occur. Once a contradiction arrived, U exposed it as unresolved rather than claiming the prior forced point was certain. Of eight unresolved pre-event states, six next receipts matched the candidate and two matched the old value. All eight post-contradiction uncertainty states were valid under the frozen rule.

## Predictor comparison and costs

| Arm | Point consequence correct / 41 | Exact pair correct / 41 | Previously unseen relation correct / 6 | Ordinary model calls |
| --- | ---: | ---: | ---: | ---: |
| Frozen model M | 29 | 28 | 6 | 82 |
| Latest receipt L | 26 | 26 | 1 | 0 |
| Recent-three R3 | 22 | 22 | 1 | 0 |
| Uncertainty U, forced point only | 22 | 22 | 1 | 0 |

The primary U output is its state, not the forced point. Its point fallback deliberately kept the prior established value while unresolved and used neutral 0 with identity next-state on UNSEEN relations. M won all six cold starts, including the new `1:ADVANCE` and `2:HOLD` relations, which supports a model role where grounded experience is absent. No additional distinguishing context was given to M for a contradictory exact-relation history, so the model's point accuracy cannot resolve the event-4 information boundary.

The model made **84 logical and 84 physical calls** in total: 82 ordinary calls plus two for the registered malformed-output perturbation. Ordinary prompts used 10,122 input context tokens by the frozen tokenizer count; the perturbation used 266 more, for **10,388** total. Ordinary M preparation took 1,014.83 seconds, plus 15.93 seconds for the perturbation. U made zero model calls and used zero model context tokens. Its measured receipt-history fold time totaled **0.00133 seconds across 41 preparations** (about 0.033 ms each on this machine); complete preparation including capture totaled 0.01164 seconds. This is descriptive service timing, not a controlled hardware benchmark.

U is derived on demand from durable authenticated Memory. Its **additional durable state storage is zero** in this implementation; the study's scored-event logs store states for audit, separate from operational Memory. A serialized pre-event U state averaged **1,509 bytes** and ranged from 175 to 3,379 bytes, including the full provenance ledger. This ledger grows with exact-relation history; materializing it as a persistent cache would incur that storage cost and would need receipt reconciliation. The Memory SQLite files were the same page size across arms for each schedule (32 KiB for the three short schedules, 40 KiB for the final schedule).

## Integrity and architecture

The [exact replay](evidence/replay.json) passed: 164 authorized matched receipts, distinct arm sessions and receipt sources, reconstructed U states before and after every U receipt, reconstructed L/R3 predictions, model scores bound to parsed outputs, committed four-arm snapshots, and identical analysis reproduction. The protected and transport preflights passed before inference. The parent evidence remains unchanged.

The supported architecture is protected reality → durable authenticated Memory → explicit exact-relation state. Grounded consumers can distinguish `UNSEEN`, `ESTABLISHED`, and `UNRESOLVED_CHANGE`; they can request a deterministic point fallback without treating it as knowledge. A model is useful on unseen relations or when genuinely additional context exists, but this experiment supplied no such context for same-history contradictions. No agent is added. This is a small deterministic simulated study; it does not establish a universal confirmation threshold or population-level predictive performance.
