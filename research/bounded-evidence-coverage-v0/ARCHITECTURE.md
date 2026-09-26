# Horus v0.11 bounded evidence-coverage extension

V0.11 changes one prospective experimental parameter: the maximum number of
fresh ordinary behavioral decisions after the committed v0.10 endpoint rises
from five to twenty. Map requests, Explorer decisions, capability assessment,
receipts, Memory, routing, model artifacts, sampling, objectives, tie handling,
probe budgets, repair authority, and world transitions remain byte-identical.

The v0.10 repaired batch created one authenticated behavioral decision without
adding nine requests to the ordinary model-call stream. V0.11 therefore binds
new batch identities to the authenticated attempted-decision counter. This is
sequence bookkeeping only; it calls the unchanged `RoutedSplitMap.forecasts`
and inherits the unchanged `CapabilityGapRuntime.execute_autonomous` method.

The twenty decisions are prospectively segmented as 10 + 10. A second runtime
is created exactly before fresh decision 11 if the experiment is still active.
Each segment is below the protected `EPISODE_LIMIT=12`. Rollover uses the
existing `begin_runtime` path, which creates a fresh source identity and epoch
while the durable event history, problem state, routing state, exploration
state, and consumed repair state remain unchanged. The rollover schedule does
not depend on outcomes, state, predictions, accuracy, or evidence acquisition.

The one v0.10 restart and reissue are consumed. V0.11 grants zero repair calls
and zero health model calls. If ordinary execution encounters a model-service
failure that prevents continuation, the campaign stops as
`OPERATIONAL_FAILURE`, localized to `MODEL_SERVICE`; it does not become an
objective or representation conclusion.

Only a new authenticated capability-gap decision record with sequence greater
than 63, pre-state 2, a valid ordinary `EXPLOIT_TIED_MAXIMUM`, and all valid
frozen forecasts counts as the required reassessment. Historical predictions,
receipts alone, health output, repair output, fixtures, and caller-supplied
claims cannot satisfy this filter.
