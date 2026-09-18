# Horus

Horus is a research implementation of reduced-precision arithmetic, block normalization, and local fault-detection/repair experiments. The research question is which numerical and control mechanisms preserve useful behavior under constrained precision and injected faults, and where those mechanisms fail.

## What is implemented

- `rtl/`: NFE-13 arithmetic, E4M3/E3M6 multipliers, normalization, width-preserving MACs, tiles, routing, and experimental block detection/repair.
- `sim/`: numerical reference models, vector generators, and synthesis scripts.
- `tb/` and `tests/`: hardware benches and Python checks.
- `experiments/structured_output/`: an experimental JSON contract/budget controller using caller-supplied facts.
- `research/`: the [grounded self-correction note](research/grounded-rsi-note-2026-09-17.md).

The arithmetic models and benches form an established research baseline, not a production-qualified processor. Block recovery and the software controller are experimental. The complete five-part framework is proposed, not implemented.

## Install and test

Use Python 3.10+ (tested on 3.10.12), GNU Make, and Icarus Verilog/vvp 11.0. On Debian/Ubuntu, install the system packages `python3-venv`, `make`, and `iverilog` through your package manager.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
make test
```

`make test` compiles RTL, prepares inputs, runs simulations, and checks their measured output. It also executes the standalone assertion scripts, structured-output unittest suite, and runner failure checks. A missing tool, missing measurement, nonzero exit, or reported simulation failure makes the command fail. Tests run in a fresh temporary work directory and print its location; existing generated outputs cannot seed a run.

## Reproduce selected experiments

```bash
python -m pip install -r requirements-experiments.txt
make experiments
```

This runs the MLP digit experiment, Hopfield comparison, feedback-chain and normalization experiments, Jacobi MAC comparison, and block-floating-point comparison. On the tested CPU environment it takes roughly a few minutes; timings are not performance claims. All required data is generated locally or supplied by scikit-learn's bundled digits dataset. No model download or LLM package is required.

For four selected area measurements, install Yosys/ABC and supply an installed Sky130 HD liberty file:

```bash
export SKY130_HD_LIB="$PDK_ROOT/your-installation/sky130_fd_sc_hd__tt_025C_1v80.lib"
make synthesis
```

Adjust the example to your PDK layout; the library is not redistributed. See [tested versions and provenance](docs/REPRODUCIBILITY.md). To retain evidence in a named new directory:

```bash
python scripts/run_checks.py core --output results/core-run
```

Outputs include commands, per-step logs, package versions, source hashes, and a fail-closed completion status. Review generated logs before sharing them; they can contain machine-specific paths. `make -C sim skpr_sim` and `make skpr_sim` both execute the same keeper co-simulation.

## Observed results and limits

The reference baseline observed 2,258 passing current-tile checks and 2,005 v2 checks; 360/360 MLP prediction matches (one activation rounding difference); 120/120 tested Hopfield recalls with zero divergent shared trajectories; and 200/200 Jacobi convergence for the specified small systems. These are scoped experiments, not guarantees over arbitrary inputs. [Results and commands](docs/RESULTS.md) distinguish fresh candidate checks from retained historical context.

Negative results matter: random Hopfield starts can reach spurious attractors; per-product precision loss harms iterative corrections; normalization has workload-dependent limits; a smaller block-only representation fails the tested gradient criterion. Detection alone need not improve damaged outputs. A replayed block is not automatically independently certified.

LLM runners, language corpora, model weights, and their generated outputs are not included in this candidate. Earlier model runs used a bundled fallback corpus after dataset loading failed; they were not WikiText reproductions and are not offered as reproducible results of this export.

The [hardware-to-framework mapping draft](docs/HARDWARE_FRAMEWORK_MAPPING.md) identifies real local mechanisms and missing capabilities. The [minimal next experiment](docs/NEXT_EXPERIMENT.md) is a proposal; it has not been implemented or run. None of these results establishes AGI, general recursive self-improvement, or a general safety/recovery system.

## Evidence and license

Four small numerical fixture files are retained with [individual reasons and hashes](docs/EVIDENCE.md). Other outputs are regenerated. Original historical measurements are not silently replaced by new runs.

Project source is distributed under [CERN-OHL-S-2.0](LICENSE). See [third-party data and tool provenance](docs/PROVENANCE.md). This candidate contains no downloaded model weights or PDK library.
