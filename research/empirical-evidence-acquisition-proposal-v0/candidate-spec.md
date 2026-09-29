# E: bounded empirical evidence acquisition — frozen Phase 3 specification

Status: **prospective inactive candidate**. Parent diagnosis is `293c205cea3e3e24b22119ed322c7030c75e8551`, classified `EMPIRICAL_STAGNATION_DIAGNOSIS_SUPPORTED`; its selected H2 hypothesis is preserved. The active incumbent remains grounded authority plus the exact `BOUNDED_STAGNATION_ESCAPE` (S). E is neither called by `grounded_agent.decide` nor authorized to execute an action in this milestone.

Name: `BOUNDED_EMPIRICAL_EVIDENCE_ACQUISITION`; short ID `E`. If E were evaluated later, its action source would be `EMPIRICAL_EVIDENCE_ACQUISITION` and trigger reason `DETERIORATED_EMPIRICAL_RELATION_WITH_MISSING_EVIDENCE`. The objective is one missing **relation observation**, never a claim that the alternative is better.

At a pre-decision boundary with current state `s`, the caller supplies current admissible actions, their grounded assessments, and the *complete chronological event projection* independently checked by the existing signed receipt/authorization/Memory replay. E's pure function checks projection shape, sequence continuity, receipt identity/hash presence, grounded count and recent-window agreement. It does **not** cryptographically authenticate signatures itself. A missing, reordered, or inconsistent projection raises an error and yields no action. Non-authorized events remain in history but are not empirical observations; any such event at the tail breaks the qualifying suffix. No future event, unexecuted outcome, hidden regime, world schedule, model text, or mutable counter is an input.

All of the following must hold simultaneously:

1. The immediately preceding authorized events form a consecutive suffix of **at least four** executions of one exact `(s,a)`, each with pre-state and realized next-state `s`. Any intervening state change, other selected action, or non-authorized event breaks this suffix. `a` remains admissible now.
2. Assessment `(s,a)` is of type `EMPIRICAL` and kind exactly `EMPIRICALLY_STABLE` or `VARIABLE_RELATION`, with no active possible-change flag. `POSSIBLE_REGIME_CHANGE` is excluded.
3. That relation has a full four-observation authenticated recent window. The supplied recent values must equal its last four receipt-backed observations, and the grounded observation count must match the complete supplied relation history. No padding or inferred observations.
4. The sum of the four recent realized consequences is **≤0**.
5. The sum of **all** authenticated realized consequences of `(s,a)` is **≤0**. Both signs are exact observed sums; neither estimates unseen payoffs.
6. At least one *other*, currently admissible `(s,b)` is `UNSEEN` with observation count zero. Unresolved or already empirical relations do not qualify.
7. No admissible deterministic relation is `ESTABLISHED` with consequence **+1**. The existing grounded ceiling retains priority.

When eligible, E reports the **first** eligible unseen alternative in canonical `ADVANCE, HOLD, RETREAT` order, independent of display order. It makes no model call. The returned recommendation does not execute anything in Phase 3. In a future evaluation, a real action would use the original protected world, receipt, Measure, authorization, and Memory path. Consequences +1, 0, and -1 would all be admitted without reinterpretation. A state-changing receipt would be accepted without an automatic return action.

The one acquisition action differs from `a`, so it breaks the same-action suffix. Immediate E retrigger is impossible. Eligibility could recur only after a **fresh** four-execution same-relation suffix with both sign tests and a still-unseen alternative. The function has no persistent exploration counter; restart reconstruction depends only on authenticated history and current grounded assessments. A later Phase 4 study must verify the real protected path and bound any later repeated acquisitions.

S and E remain mechanically separate. S is the promoted deterministic `ESTABLISHED 0` neutral-fallback suffix rule with its frozen threshold 3. E is an empirical rule whose recent and cumulative observed sums are nonpositive. They share a bounded reality-query motivation, but E cannot inherit S's deterministic guarantee. Neither S implementation nor active selector is changed here.

The source of truth for this specification is [candidate.py](../../experiments/empirical_evidence_acquisition_proposal_v0/candidate.py). [Synthetic tests](../../experiments/empirical_evidence_acquisition_proposal_v0/test_candidate.py) exercise the frozen boundary without execution. [Replay source](../../experiments/empirical_evidence_acquisition_proposal_v0/replay.py) reads only already published R128 decisions and empirical control prefixes.
