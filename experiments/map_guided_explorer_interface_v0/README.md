# Map-guided Explorer interface v0

Zero-inference architectural study. Read the [registration](../../research/map-guided-explorer-interface-v0-preregistration.md). There is no live mode or model transport.

```sh
python3 -m unittest experiments.map_guided_explorer_interface_v0.test_interface -v
```

Set INTERFACE_EVIDENCE and INTERFACE_REPLAY to fresh durable folders outside the public checkout:

```sh
python3 -m experiments.map_guided_explorer_interface_v0.run --output "$INTERFACE_EVIDENCE"
python3 -m experiments.map_guided_explorer_interface_v0.run --replay "$INTERFACE_EVIDENCE" --output "$INTERFACE_REPLAY"
```

Sockets are forbidden. Both deterministic evidence files must match byte-for-byte. Full synthetic request/response and provenance records remain private. Public compact results report every control and all eighteen gates. Synthetic invocations are not model calls; no result establishes model behavior or authorizes a later live campaign.
