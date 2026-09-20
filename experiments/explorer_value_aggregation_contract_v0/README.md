# Explorer value-aggregation contract v0

Separate 96-call matched A/B policy-contract study using the unchanged authentic P2 fixture. Read the [frozen preregistration](../../research/explorer-value-aggregation-contract-v0-preregistration.md). Earlier Explorer NOT ESTABLISHED remains untouched.

Zero-inference tests:

```sh
python3 -m unittest experiments.explorer_value_aggregation_contract_v0.test_study -v
```

Set CONTRACT_ARCHIVE to the private retained archive and CONTRACT_REPLAY to a new durable directory outside this public checkout:

```sh
python3 -m experiments.explorer_value_aggregation_contract_v0.run --replay "$CONTRACT_ARCHIVE/live" --output "$CONTRACT_REPLAY"
```

Replay rebuilds authenticated fixtures and exact rational mean targets with sockets forbidden. Eight files and 96 snapshots must match. Public results preserve all parsed pairs, action counts, sensitivity and decision gates. Raw outputs are retained privately for replay. Preserve the live archive and fixed campaign reservation; never automatically reissue a request. A separate replication requires a new identity and explicit authorization.
