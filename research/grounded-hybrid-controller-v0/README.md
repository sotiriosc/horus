# Grounded hybrid controller v0

The [prospective registration](preregistration.md), [frozen scenarios](scenarios.json), and [source manifest](source-manifest.json) were committed at `8372731` before live inference. The parent grounded-uncertainty study remains unchanged at `b4d8c0761f0b414bcad25da995c060a169e1fbac`.

The completed protected campaign is in [evidence](evidence). Read the [report](report.md), [results](evidence/results.json), and [exact replay](evidence/replay.json). Each scenario contains three independent durable sessions. Their seed observations match before autonomous action selection; actions and post-decision histories may differ. H has a fresh-process restart checkpoint. A completed campaign is not rerun in place.

Validation:

```sh
python -m unittest experiments.grounded_hybrid_controller_v0.test_study -v
python -m experiments.grounded_hybrid_controller_v0.preflight
python -m experiments.grounded_hybrid_controller_v0.replay --output research/grounded-hybrid-controller-v0/evidence
```
