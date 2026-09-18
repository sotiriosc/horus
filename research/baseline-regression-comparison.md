# Baseline-to-public regression comparison

This public-safe comparison records how the sanitized baseline was carried into
the public repository. It omits private regression machinery and private test
details. Exclusion is not reported as a pass.

| Public check family | Baseline | Public repository | Comparison |
|---|---|---|---|
| NFE, controller, routing, wrapper, mesh | Passed | `make test` | Match; displayed NFE values are explicitly checked |
| Current and v2 tile arithmetic | Passed | `make test` | Match |
| Detector sidecar | Passed | `make test` | Match for the exported detect-only sidecar |
| Alignment and repair/replay models | Passed | `make test` | Match |
| Width-preserving MAC/array variants | Passed | `make test` | Match |
| Normalizers and format codecs | Passed | `make test` | Match |
| Structured-output controller | Passed | `make test` | Match within its caller-supplied-facts scope |
| Keeper documented invocation | Path failure | `make skpr_sim` and `make -C sim skpr_sim` | Intended public path fix; arithmetic unchanged |
| MLP, Hopfield, feedback, normalization, Jacobi, block floating point | Passed selected experiments | `make experiments` | Match for exported selected experiments |
| Selected mapped area probes | Passed | `make synthesis` | Match under documented tool/library assumptions |
| Non-exported model/corpus campaigns | Mixed or incomplete | Not included | Excluded; no equivalence or pass claim |

The initial sanitized candidate executed 53 core steps, 24 selected experiment
steps, and 4 synthesis steps successfully. The step count includes compilation
and vector preparation and is not a count of independent scientific
hypotheses. The public test runner creates fresh work directories, checks process
status and expected measured output, and rejects silent or marker-only success.

The later independent-authorization experiment is not part of this baseline
comparison. Its separate controls and results are recorded in
`research/bounded-independent-authorization-results.md`.

