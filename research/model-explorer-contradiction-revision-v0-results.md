# Contradiction-revision v0 — infeasible under the frozen evidence boundary

**FROZEN FRAMEWORK COULD NOT SUPPORT THE TESTED NONSTATIONARITY.**
The mandatory preflight stopped at the first changed event: SHIFT transaction 4,
state-1 HOLD. The external event produced **−1**, while frozen A/B/C agreed on the
old **+1** relation and the framework committed **+1** to Memory. This is **one
externally audited false accept**, not safe rejection or successful adaptation.

**Real model calls: 0 of the planned 144. Behavioral revision: UNTESTED.**
No evidence path or framework implementation was patched to continue the study.

## 1. Frozen identities

Parent `4a25129948e7eb57917cefae1af2e3fd0f1235e9`; framework checkpoint
`8ec32c839133df7ddd76448063b5f765c20155da`. All 23 framework source hashes remain
unchanged and were checked before and after preflight. Protocol commit `85b36dd`;
diagnostic implementation commit `f2609c6`.

The planned model was unchanged dolphin-mixtral:latest / Ollama 0.1.16, with the
manifest and weights digests retained in `frozen-framework.json`. It was never
loaded or called for this study. No new model runtime identity check is claimed.

## 2. External-world implementation boundary

The new [overlay](../experiments/model_explorer_contradiction_revision_v0/overlay.py)
wraps the existing TrueWorldOracle. Every state transition is delegated unchanged.
Only the two registered state-1 consequences change after execution 3 in SHIFT.
The schedule controls the regime; no prediction, model output, evidence receipt,
registry or authorizer supplies world truth. CONTROL is unchanged.

The [diagnostic](../experiments/model_explorer_contradiction_revision_v0/preflight.py)
uses ordinary begin_step, prediction latch, world execution, unchanged clean A/B/C
generation and submit_package. Its external audit observes the result and halts
the experiment; it grants no runtime authority and repairs no record.

## 3. Mandatory feasibility result

**INFEASIBLE_UNDER_FROZEN_FRAMEWORK.** Eleven scripted preflight transactions ran:
seven CONTROL and four SHIFT. Ten committed their actual events correctly. The
eleventh, SHIFT transaction 4, committed the wrong consequence. SHIFT stopped
immediately afterward; transactions 5–7 were not attempted in that arm.
The diagnostic returned exit code 2 for the failed feasibility requirement.

| Transaction 4, state 1, HOLD | Observed value |
|---|---|
| Actual external next state / consequence | 1 / −1 |
| Frozen Map prediction | 1 / +1 |
| Source A evidence | 1 / +1 |
| Source B evidence | 1 / +1 |
| Witness C relation code | 5, encoding 1 / +1 |
| Code corresponding to actual event | 3, encoding 1 / −1 |
| Final Memory record | 1 / +1, AUTHORIZED |
| Internal measurement_matches | true |
| External committed-record audit | FALSE ACCEPT |

No receipt corruption, witness injection, common-mode fault flag or registry edit
was used. The mismatch arose from retaining the frozen stationary evidence logic
while changing the actual external consequence as requested.

## 4. Exact old/new regime

At state 1, OLD is HOLD +1 and ADVANCE −1. NEW is HOLD −1 and ADVANCE +1.
Their next states remain 1 and 2 respectively. Other consequences/transitions remain
unchanged. The external overlay's two changed cases were checked in unit tests.
Only NEW HOLD reached the framework preflight; NEW ADVANCE was not attempted after
the mandatory stop. Do not claim both changed actions were framework-validated.

## 5. Authorized H0/H1/H2 construction

Sequence: HOLD, ADVANCE, RETREAT, HOLD, ADVANCE, RETREAT, HOLD.
Both arms start at state 1, epoch 1001. RETREAT navigates state 2→1.

| Fixture | Authorized records | Actual verified target histories |
|---|---:|---|
| CONTROL H0 | 3 | HOLD [+1]; ADVANCE [−1] |
| CONTROL H1 | 6 | HOLD [+1,+1]; ADVANCE [−1,−1] |
| CONTROL H2 | 7 | HOLD [+1,+1,+1]; ADVANCE [−1,−1] |
| SHIFT H0 | 3 | HOLD [+1]; ADVANCE [−1] |
| SHIFT H1 | Not safely constructible | Stop at transaction 4 |
| SHIFT H2 | Not safely constructible | Not attempted |

CONTROL and SHIFT H0 are identical. The first four intended action/state/identity
shapes match across arms; their transaction-4 actual consequences differ. The wrong
SHIFT record was preserved as failure evidence, never used as model input.

## 6. Chronological Memory projection

A pure projection was tested on actual authorized CONTROL history. It selects
pre_state=1 and offered HOLD/ADVANCE records in chronological transaction order,
rendering transaction_id, surface_action and consequence. At H2 the visible IDs
are 1,2,4,5,7; navigation IDs 3,6 remain in full Memory. No records are averaged,
rewritten, deleted or marked obsolete.

The intended exact prompt and payload rules are in the
[preregistration](model-explorer-contradiction-revision-v0-preregistration.md).
No 144-prompt verified-history annex was completed: SHIFT H1/H2 could not supply
the required safely authorized contradiction records. No hypothetical history
was substituted for actual evidence, and no prompt was sent to a model.

## 7. Opaque families, mappings and option balance

Planned O1=(K1,K2,K3), O2=(Q7,M4,Z2), all six mappings twice, schedules 0–11,
seeds 40001–40012. The second occurrence reverses old-best HOLD's option position.
Mappings, seeds and options match across arms/stages; evidence order stays chronological.
This schedule was frozen but **not executed**. No neutrality claim.

## 8. Total calls

Planned real calls: 144. Actual real calls: **0**. Model parser controls: **0**.
The eleven scripted diagnostic transactions are not model calls. Unit tests and
diagnostic replay are separately recorded and also use no inference. No model
server was started for this study.

## 9. Proposal validity

Model proposal validity is **UNTESTED**, with zero opportunities and null rates.
Scripted preflight actions all passed the existing finite-action admission path;
that does not establish model-output validity.

## 10. H0 old-preference replication

UNTESTED for O1 and O2. The planned >=10/12 SHIFT H0 HOLD prerequisite has no
observations. Safe H0 fixtures alone do not demonstrate a model preference.

## 11. CONTROL H0/H1/H2 behavior

No model probes at any stage. Selection counts/rates are unavailable, not zero
success rates. Only the authorized scripted histories in section 5 were measured.

## 12. SHIFT H0/H1/H2 behavior

No model probes at any stage. H0 exists; safely authorized H1/H2 do not.
The contradiction-response curve is UNTESTED.

## 13. Matched action-change tables

No H0→H1, H1→H2, H0→H2 model pairs or CONTROL/SHIFT model comparisons exist.
The diagnostic's matched action/state/identity prefix is not a behavioral sample.

## 14. Revision criterion O1

UNTESTED / NOT ESTABLISHED. No evidence for any behavioral threshold; feasibility
and integrity prerequisites failed before inference. This is not an observed model
failure to revise.

## 15. Revision criterion O2

UNTESTED / NOT ESTABLISHED for the same reason. No pooling or substitute vocabulary.

## 16. Overall replication decision

**CONTRADICTION-DRIVEN BEHAVIORAL REVISION NOT ESTABLISHED — UNTESTED.**
The required verified contradiction could not be supplied under the frozen boundary.

## 17. Behavioral revision latency

UNTESTED. No model stage transitions, monotonic response curve or behavioral latency
can be computed. No inference about hidden beliefs or causal understanding.

## 18. Old-evidence retention

Original HOLD +1 and ADVANCE −1 remained byte-for-byte unchanged in SHIFT through
transaction 4. No eviction or rewritten old record occurred. Maximum Memory length
was seven in CONTROL, within the existing bound of eight. Retaining old truth
worked; safely recording the new true consequence did not.

## 19. Contradiction event verification

The experiment-side actual event genuinely changed to HOLD −1 at transaction 4.
Its normal A/B/C package did **not** authenticate that event. Safely authorized
changed events: **0 of 1 attempted**. A valid new contradiction record was therefore
never published. Do not call the old +1 Memory publication a verified contradiction.

The cause is visible in the unchanged source paths:

- [Source A](../experiments/base_framework_v1/source_a.py), `observe`: fixed table.
- [Source B](../experiments/base_framework_v1/source_b.py), `observe`: fixed conditional relation.
- [Witness C](../experiments/base_framework_v2/witness_c.py), `observe`: fixed relation codes.
- [Evidence generation](../experiments/base_framework_v2/campaign.py), `make_evidence`:
  uses an observation request containing the actual pre-state and pending action;
  clean A/B/C do not consume the event's realized consequence.

All three evidence producers remained consistent with the old stationary world.
Their declared process separation and fresh provenance still passed. Agreement
and provenance did not detect the shared obsolete relation to actual world truth.

## 20. Map and Recovery during the changed event

At SHIFT transaction 4, the original latched prediction was HOLD, next state 1,
consequence +1. It disagreed with the actual −1 event and remained unchanged.
There was **no post-outcome prediction rewrite**.

Measure marked the prediction as matching because the authorized A/B pair also
said +1. The incumbent state 1 was retained, Map version advanced 3→4, and the wrong
consequence was committed. Quarantine entries: zero. Recovery proposal path entered:
no; Recovery authorization: false. Reobservations: zero. No normal Map correction
was misclassified as failure. The failure is the incorrect consequence publication.
The internal false_accepts counter stayed zero; the external actual-event audit
detected the false accept.

## 21. Current-world proposal accuracy

UNTESTED. There were no measured model proposals to score. The scripted HOLD
transaction is a feasibility probe, not evidence about Explorer preferences.

## 22. Parser controls

NOT RUN. The conditional twelve-control set was frozen but its model adapter was
not built after feasibility failed. Overlay and projection tests are not represented
as parser tests or synthetic model behavior.

## 23. Framework integrity for the requested world change

**FAIL:** one actual changed event produced one wrong authorized Memory record.
Prediction latches and original history were unchanged; recorded identities were
fresh, no duplicate authorization or bound violation was observed, and no model
had protected-state access. These passing subconditions do not cancel the false accept.

This is a new nonstationarity boundary result outside the old stationary-world
campaigns. Earlier protected-case passes and historical common-mode/registry
negative controls remain unchanged; no previous result is reclassified.

## 24. Exact replay

Fresh diagnostic replay reconstructed all eleven setup transactions, regime state,
receipts, packages, traces, Memory and stop decision. Both `preflight.json` and
`results.json` are byte-identical. Replay exit code 0 means the failure reproduced,
not that feasibility passed. Model calls during replay: zero.

The intended 144-call behavioral replay is **NOT RUN**, since no such transcript
exists. There is no fabricated `model-calls.jsonl`.

## 25. Fresh regressions

All ten preservation commands actually ran and passed, plus diagnostic replay:

| Check | Actual execution |
|---|---|
| Prior factorial v1 replay | 216 recorded calls; unchanged transcript and summary |
| Semantic-prior v0 replay | 288 recorded calls; unchanged transcript and summary |
| Adaptive Explorer v0 replay | 288 recorded calls; unchanged transcript and summary |
| Memory Study v1 replay | 224 recorded calls; unchanged transcript and summary |
| Original Explorer integration replay | 69 recorded calls; unchanged transcript and summary |
| Minimum-framework repair 1 | 177 scenarios; 126 protected passes; 109 direct checks |
| Base framework v0 | 12 tests / 42 scenarios |
| Base framework v1 | 10 tests / 69 scenarios; 3 expected common-mode false accepts |
| Base framework v2 | 13 tests / 57 scenarios; 12 A+B blocks; 3 A+B+C and 3 registry false accepts |
| New overlay/projection tests | 3 tests passed; no model calls |

Repair-1's 15 weakened-control and 6 out-of-model boundary violations remain visible.
These regression passes preserve prior behavior; they do not validate the new world
change. Unimplemented model chronology-adapter, parser and behavioral-threshold
tests were not run or claimed. Exit codes, timestamps and log hashes are in
[verification.json](../experiments/model_explorer_contradiction_revision_v0/verification.json).

## 26. Limitations

One first changed HOLD event is sufficient to fail the mandatory feasibility gate;
it is not a measured failure rate over arbitrary regime changes. NEW ADVANCE and
later SHIFT transactions were not tested through the framework after the stop.
No model behavior or revision capability was measured. Pure overlay tests show
what the external schedule does, not that A/B/C can verify it.

The protocol records an intended model design, not a runnable validated behavioral
campaign. Its full verified-history prompt annex is unavailable because the
required SHIFT fixtures failed. This checkpoint documents the boundary without
altering the evidence architecture to obtain a desired outcome.

## 27. Narrowest defensible conclusion

The frozen prototype's evidence producers continue to report stationary relations
when only the experiment-side realized consequence changes. At the first tested
change, their agreement caused an incorrect consequence to be authorized and stored.
**The requested model-revision question cannot be tested honestly through this
frozen evidence path. Contradiction/revision remains UNTESTED.**

## 28. Recommendation and stop

Preserve this failed feasibility checkpoint. Do not spend the 144-call model budget
or feed the incorrect record as verified new experience. Any future work first
needs a separately scoped evidence-path design that can authenticate actual changing
events while preserving checker independence. Copying one overlay result into all
three receipts would not establish that independence and was not done here.

No architecture patch, additional recovery mechanism, larger Memory, new model
role, or further study was started. Main and historical tags remain unchanged;
nothing was pushed.

[Compact results](../experiments/model_explorer_contradiction_revision_v0/results.json) ·
[Reproduction](../experiments/model_explorer_contradiction_revision_v0/README.md).
