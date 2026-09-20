# Map temporal-relation forecast v0

See the preregistration and results in research/. The model predicts event seven from six authenticated HOLD events; its authentic receipt supplies the target.

Zero-inference tests:

```sh
python3 -m unittest experiments.map_temporal_relation_forecast_v0.test_study -v
```

Recorded-response reproduction (private archive supplied separately):

```sh
python3 -m experiments.map_temporal_relation_forecast_v0.run --replay "$TEMPORAL_LIVE" --output "$DURABLE_REPLAY"
```

The replay directory must be new, durable and outside the public tree. Raw prompts/responses and receipt archives are private. Public results include all 96 parsed outcomes and 24 F/P pairs. Live mode is a one-shot registered campaign; never automatically rerun it. No authority implementation changes.
