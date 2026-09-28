# Run C: authenticated decision trace (Phase 1/2)

Source: the completed [grounded-authority result](../grounded-authority-autonomous-agent-v0/result.md) and its [sanitized per-decision trajectory](../grounded-authority-autonomous-agent-v0/public-result.json). All consequences below are realized, authorized events with preserved receipt/event identities and provenance hashes in that trajectory. Unchosen outcomes and hidden regime labels are excluded.

| Decision | Pre-state and pre-decision evidence | Route / selected action | Authorized consequence and grounded change |
| --- | --- | --- | --- |
| C:D01–D03 | At states 1, 2, 3 respectively, all three local actions `UNSEEN` | Model chose `ADVANCE` each time | `−1`→state 2; `+1`→state 3; `−1`→state 0. Each selected relation became deterministic `ESTABLISHED`. |
| C:D04 | State 0: `ADVANCE`, `HOLD`, `RETREAT` all `UNSEEN` | Model chose `HOLD`, `MODEL_FOR_UNSEEN` | `0`→state 0; `0:HOLD` became `ESTABLISHED` zero, one supporting receipt. |
| C:D05 | State 0: `ADVANCE` and `RETREAT` `UNSEEN` (0 receipts); `HOLD` `ESTABLISHED` zero (1) | All three admissible; model chose `HOLD`, labeled `SAFE_GROUNDED_FALLBACK` | `0`→state 0; HOLD support 1→2, kind unchanged. |
| C:D06 | Same epistemic kinds; HOLD support 2 | Model chose HOLD fallback | `0`→state 0; HOLD support 2→3. |
| C:D10 | Same kinds; HOLD support 6 | Model chose HOLD fallback | `0`→state 0; support 6→7. |
| C:D15 | Same kinds; HOLD support 11 | Model chose HOLD fallback | `0`→state 0; support 11→12. |
| C:D20 | Same kinds; HOLD support 16 | Model chose HOLD fallback | `0`→state 0; support 16→17. |
| C:D25 | Same kinds; HOLD support 21 | Model chose HOLD fallback | `0`→state 0; support 21→22. |
| C:D30 | Same kinds; HOLD support 26 | Model chose HOLD fallback | `0`→state 0; support 26→27. |

The D05–D30 pattern comprises **26 consecutive model-mediated zero fallbacks**, not mechanical selections. For each of those decisions, `0:ADVANCE` and `0:RETREAT` remained `UNSEEN` and were offered as candidates. No `UNRESOLVED_CHANGE` relation appeared at state 0; the uncertain alternatives were unseen. The exact source label is assigned by [`source_for_model_choice`](../../experiments/grounded_authority_autonomous_agent_v0/protocol.py) after the model selects established nonnegative HOLD. The candidate route excludes inferior **known** relations but retains every uncertain one, so exploration was permitted. The record supports “unselected,” not a claim about the model's internal reason or the unexecuted alternatives' outcomes.

Only HOLD's receipt count, support identities, and bounded recent decision history changed. Its established value remained zero; state stayed 0; the other two relations gained no observations. The [route](../../experiments/grounded_authority_autonomous_agent_v0/protocol.py) contains no information-value score, repeated-fallback counter, or stagnation trigger, and the [decision payload](../../experiments/grounded_authority_autonomous_agent_v0/worker.py) carries at most three recent decisions. Repeated zero receipts reinforced the known relation's provenance without reducing uncertainty about the alternatives. This explains the observed possibility of the loop under the frozen interface. It does not establish that an alternative would have improved realized reward.

For contrast, A:D06 and B:D16 each had an exact deterministic `ADVANCE` relation established at `+1`, the registered ceiling. [`select_route`](../../experiments/grounded_authority_autonomous_agent_v0/protocol.py) selected that action mechanically, with no action-model call, and each authorized consequence was `+1`. The [sensitivity study](../grounded-action-sensitivity-v0/report.md) found the earlier model-only action choice unchanged under nine paired assessment swaps; the mechanical ceiling route addresses that observed known-fact authority issue. Run C instead sits in the mixed route where there is no ceiling evidence.
