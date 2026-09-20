# Explorer finite-value comparator v0

Detached finite forecast comparison only: no Map call, world execution or Memory change. Read the research preregistration and results.

```sh
python3 -m unittest experiments.explorer_finite_value_comparator_v0.test_study -v
python3 -m experiments.explorer_finite_value_comparator_v0.run --replay "$COMPARATOR_LIVE" --output "$DURABLE_REPLAY"
```

Supply the separately retained private archive. Replay output must be new, durable and outside the public tree. Live mode is exclusively reserved for the one144-call campaign; never automatically repeat it. R1/R2 are descriptive controls. No mechanical production Explorer is introduced.
