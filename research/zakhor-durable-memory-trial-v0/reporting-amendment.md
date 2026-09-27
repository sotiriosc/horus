# Reporting-only amendment

The 48th and final model call, 24th protected publication, Stage-2 checkpoint,
and fresh-process restart proof all completed. The frozen parent runner then
failed before writing `results.json` because `analyze.py` constructed a Python
dictionary with `event_number` supplied both explicitly and inside the already
stored condition record.

No inference retry or campaign extension is authorized or performed.

`postrun.py` is a separately recorded zero-inference recovery. It removes only
the duplicate dictionary keyword by merging the stored record and phase. It
imports the frozen metric functions and changes no event, model response,
retrieval, classification order, threshold, or decision rule. The pre-inference
source manifest remains unchanged so the executed implementation stays
content-addressed exactly.

A subsequent audit found a second reporting-only defect: raw scoring computed
`relevant_available` after publication and therefore included the current event,
which could not have been retrieved before execution. Selected identities,
positions, values, predictions, and receipts were correct. `postrun_v2.py`
recomputes the preregistered *prior* relevant count as `event - phase_start`,
recomputes relevant/stale selected counts from the frozen chronological positions
and values, and reruns the unchanged metric and error-priority functions. The v2
result was an intermediate recovery. The initial postrun output is not used for
inference.

One presentation count in the frozen metric helper treated the empty first-event
retrieval as a vacuous “most recent retrieved” success. `postrun_v3.py` makes the
count non-vacuous (a prior record must exist), adds direct paired counts for
selected identities, predictions, and internal reason labels, and applies the
preregistered descriptive decision gate. It changes no primary metric. The v3
result is the authoritative report.
