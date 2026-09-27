# Grounded uncertainty state v0

The [prospective registration](preregistration.md), [frozen schedules](schedules.json), and [source manifest](source-manifest.json) were committed at `426e967` before live inference. The parent grounded-reducer study remains at `a9c113e8c4dfc714522b426896bd112650be5c71`; its evidence was not modified.

The completed four-arm campaign is in [evidence](evidence). The [result](evidence/results.json), [exact replay](evidence/replay.json), and [interpretation](report.md) are read-only products of the original authenticated receipts. Each schedule's `current` symlink points to one committed four-arm snapshot; `work` is private transaction state. A completed campaign is not rerun in place.

Validation:

```sh
python -m unittest experiments.grounded_uncertainty_state_v0.test_study -v
python -m experiments.grounded_uncertainty_state_v0.preflight
python -m experiments.grounded_uncertainty_state_v0.replay --output research/grounded-uncertainty-state-v0/evidence
```
