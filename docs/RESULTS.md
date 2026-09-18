# Selected numerical results

Status vocabulary: **IMPLEMENTED** describes code; **OBSERVED** describes executed measurements; **EXPERIMENTAL** limits maturity; **PROPOSED** and **HYPOTHESIS** are not completed results.

| Check | Reference baseline / candidate target | Reproduce |
|---|---|---|
| Current tile | 2,258 checks, zero failures | `make test` |
| Lean v2 tile | 2,005 checks, zero failures | `make test` |
| Detector / alignment / replay | Directed and generated cases pass within configured modes | `make test` |
| Scaled MAC / arrays | W32/W34/W36 pass; 4-tile and 16-tile smoke checks pass | `make test` |
| Structured output | 9 unit tests; 7 scenario outcomes; supplied facts are assumed authoritative | `make test` |
| MLP digits | 360/360 predictions agree; one image has a one-LSB activation discrepancy | `make experiments` |
| Hopfield | 120/120 tested recalls; zero divergent shared iterations; 7/8 random starts reach spurious attractors | `make experiments` |
| Jacobi MAC | 200/200 convergence; 38,408 products and 23,333 accumulation steps match | `make experiments` |
| Normalization | Three RTL confirmations; acceptable intervals depend on workload | `make experiments` |
| Block floating point | E0M6 fails tested gradient-fidelity criterion; E0M9 passes with higher multiplier area | `make experiments` |
| MAC synthesis | Baseline top areas: 4,071.4048 versus 3,702.3008 square micrometres | `make synthesis` |
| Block multiplier synthesis | Baseline areas: 1,848.0224 and 3,836.1792 square micrometres | `make synthesis` |
| Independent authorization | 4,200 protected transactions and 2,700 broader-fault transactions; zero protected false accepts | `make independent-commit && make independent-commit-followup` |
| Base framework v0 | 12 unit tests and 42 clean/failure scenario runs; zero protected false accepts, false rejects, or duplicate authorizations | `make base-framework-v0` |
| Base framework v1 | 10 unit tests and 69 scenarios; zero protected false accepts/false rejects, plus 3 explicitly out-of-model common-mode false accepts | `make base-framework-v1` |

These observations are specific to the code, seeds, tolerances, tools and library described in [reproducibility](REPRODUCIBILITY.md). Area measurements are pre-timing; they do not establish dynamic power, clock rate or full-system efficiency.

The feedback-chain experiment leaves its first prediction unconfirmed because the tested RTL lacks that alternative datapath. The other measured predictions remain separate. Precision-losing and unnormalized controls are useful falsification evidence, not bugs to conceal.

Earlier experimental narratives and long campaign records are not bundled as public claims in this candidate. Comments in retained source can refer to that historical context; the commands and prerequisites documented here define this candidate's reproducible scope. A self-contained public specification for scale tracking is in [SCALE_TRACKING.md](SCALE_TRACKING.md).
