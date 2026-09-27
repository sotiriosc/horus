# Reporting clarification

The frozen analyzer records model-call `completion_rate=1.0` for L and R3 as a
vacuous truth when they require zero model calls. The human report prints N/A
for those two arms. The frozen analyzer also divides M prediction time including
the registered perturbation by 47 scheduled events in its `mean_prediction_seconds`
field. The report separately gives the ordinary-event mean over exactly 47
ordinary M forecasts. Neither clarification changes raw evidence, scoring,
classification, or the source manifest.
