# Reproducibility

## Public release installation status

Core commands and experiment commands were rerun successfully in the recorded
development environment. Dependency resolution was also exercised offline in a
virtual environment that inherited already-installed system packages. A truly
independent clean-machine download and installation has not been completed.
Accordingly: **Clean-machine installation not yet independently verified.**

The independent-authorization commands require only Python's standard library,
Icarus Verilog, and the RTL in this repository:

```sh
make independent-commit
make independent-commit-followup
```

The base-framework-v0 software experiment uses only Python's standard library:

```sh
make base-framework-v0
```

It runs 12 unit tests and 42 predeclared scenario runs, then writes detailed
evidence to a new directory outside the repository. Its compact checked-in
summary is `experiments/base_framework_v0/results.json`.

Mapped resource reproduction additionally requires Yosys/ABC and a separately
installed compatible Sky130 liberty file; the PDK is not redistributed.

Tested platform: Linux/WSL2, Python 3.10.12; GNU Make 4.3; Icarus Verilog/vvp 11.0; Yosys 0.9 (1979e0b) with ABC. The CPU tests do not require a GPU, GCC, PyTorch, Transformers, or Datasets.

| Dependency group | Tested direct versions |
|---|---|
| Core / tests | NumPy 2.2.6; unittest from the standard library |
| Numerical experiments | scikit-learn 1.7.2, SciPy 1.15.3, Matplotlib 3.10.9 |
| Optional synthesis | installed Sky130 HD TT 025C 1v80 liberty; its checksum is recorded per run |

Requirement ranges express supported installation intent; only the listed environment has been exercised here. They are not a claim that every permitted version reproduces identical numerical results. To recreate the tested direct package versions, supply those versions to pip in a separate environment.

`make test`, `make experiments`, and `make synthesis` use a new work directory. `scripts/run_checks.py` records commands, return codes, required output checks, elapsed times, Python/package versions, and SHA-256 hashes of the executed sources. Synthesis records the liberty checksum. Run directories must be new; existing outputs are not overwritten. Generated outputs contain local paths and must be reviewed before distribution.

Fixed seeds and numerical configurations remain in the reference programs. The digits experiment uses scikit-learn's bundled 1,797-image dataset and an 80/20 split with seed 42; it generates its weights and fixtures. Golden operands for the tile tests are the four deliberate fixtures in `tests/fixtures/tile/`. Normalizer and Jacobi goldens are generated explicitly before dependent benches run.

A previous Make rule called a tile model that did not actually emit its promised files. The four retained inputs prevent dependence on stale working-directory artifacts. The elementary NFE bench prints four results instead of asserting them; the public runner checks the actual printed values. It does not count a printed expectation as a successful assertion.

A program can reproduce an expected negative scientific result and still complete successfully. Block-FP and feedback-chain checks explicitly expect their documented negative outcomes. The wrapper-equivalence tests reuse shared helper code and supplement, rather than replace, RTL checks.

The in-normalizer experimental detector variants, LLM campaigns, long gradient/scaling sweeps, private regressions, and hardware timing/STA are outside this candidate's executed aggregate suites. Included numerical scripts beyond those entry points are research source, not claims of fresh exhaustive validation.
