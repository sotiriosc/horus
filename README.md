# Horus

Horus is a reproducible research implementation of reduced-precision
arithmetic, block normalization, scale tracking, and bounded local fault
detection and recovery. It combines Verilog RTL with small Python reference
models and falsifiable experiments. It is a research codebase, not a
production-qualified processor or a general safety system.

## Current status

**Implemented:** NFE-13 arithmetic, E4M3/E3M6 components, normalization,
width-preserving MACs, tiles, routing, scale tracking, selected block
detection/repair paths, reference models, and a fail-closed public test runner.

**Experimental:** bounded independent authorization around the existing repair
wrapper, followed by a software base framework connecting Explorer, Map,
Measure, Memory, and Recovery. The framework uses a four-state environment,
bounded protected evidence, explicit provenance and continuation authority, and
history-dependent action selection.

**Proposed:** a second independently implemented observation channel and a
common-mode fault campaign for the current protected-source/authorizer trust
boundary. Hardware cost optimization remains deferred.

## Hardware baseline

The verified baseline includes reduced-precision arithmetic and formats,
normalizers, scale-aware MAC and array variants, tiles, routing/control,
scale-tracking state, block anomaly detection, and repair/replay experiments.
The `rtl/`, `tb/`, `sim/`, and `tests/` directories contain the implementation,
benches, reference models, and public checks.

The baseline existed before the independent-authorization experiment. Its exact
contents are recorded in `BASELINE_MANIFEST.json`, and the first Git commit is
the baseline itself. The [public development sequence](research/DEVELOPMENT_HISTORY.md)
explains how the later work relates to it.

## Bounded independent authorization experiment

Repair completion is not the same as permission to continue. The baseline
repair wrapper can propose a replayed result, but that proposal does not by
itself establish identity or numerical correctness.

The later bounded experiment adds this local protocol:

```text
protected source evidence
→ candidate computation / fault injection / repair
→ two-entry quarantine
→ independent identity and epoch check
→ independent numerical check
→ downstream authorization
→ sink
```

The checker computes the expected result from a protected pre-fault record with
a small integer specification. It does not call the repair implementation or
normalizer helpers and does not derive expected truth from the repaired output.
The deliberately wrong descendant-reference checker is isolated as a negative
control and cannot authorize the protected sink.

Implementation and test harnesses live in `experiments/bounded_commit/`. The
[historical proposal](docs/NEXT_EXPERIMENT.md) and the later
[measured results](research/bounded-independent-authorization-results.md) are
kept separately.

## Results

### Protected path

- 4,200 transactions across the declared seeds and controls.
- Zero false accepts, false rejects, or duplicate accepts.
- The clean and recoverable exponent-spike cases were accepted exactly once.
- Corrupted repair and identity/provenance mismatches were rejected.
- The two-entry bound and backpressure were exercised.

### Correlated descendant-reference control

The deliberately incorrect checker compared a corrupted candidate with
reference evidence derived from that same candidate. It falsely accepted 300
corrupted proposals. This is the expected negative result and demonstrates why
correlated evidence is not independent verification.

### Broader faults

A follow-up ran 2,700 additional transactions covering sign, mantissa,
exponent, tied/near-tied, block-wide, multi-lane, and post-replay faults. It
observed zero false accepts. Only the declared single exponent-spike case was
recovered; unsupported cases were safely rejected rather than reported as
repaired.

### Synthesis and trace observations

Standalone Sky130 synthesis probes measured approximately 12,475.7152 µm² for
protected-record storage/access, 12,318.0640 µm² for quarantine storage/access,
3,439.5488 µm² for the numerical checker, and 441.6736 µm² for identity
comparisons. These probes are not an exact additive decomposition of the
optimized gate. Storage dominates the measured overhead.

Lossless packing of the eight-entry trace from 96 to 63 bits preserved decisions
and retained records across 21 paired schedules and reduced the mapped
standalone gate estimate by 8,872.2592 µm². The research default remains the
original trace configuration; cost optimization is deferred until the broader
functional architecture is validated.

## Reproducing results

Use Python 3.10+, GNU Make, and Icarus Verilog/vvp. Core Python dependencies are
separate from optional scientific experiments.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
make test
make independent-commit
make independent-commit-followup
make base-framework-v0
```

Optional baseline numerical experiments require the packages in
`requirements-experiments.txt`:

```bash
python -m pip install -r requirements-experiments.txt
make experiments
```

Optional synthesis requires Yosys/ABC and a separately installed Sky130 HD
TT/025C/1v80 liberty file:

```bash
export SKY130_HD_LIB=/path/to/sky130_fd_sc_hd__tt_025C_1v80.lib
make synthesis
python3 experiments/bounded_commit/synthesize.py --liberty "$SKY130_HD_LIB"
python3 experiments/bounded_commit/synthesize.py --followup --liberty "$SKY130_HD_LIB"
```

Run artifacts are written to new temporary directories unless an explicit new
output directory outside the source tree is supplied. See
[reproducibility details](docs/REPRODUCIBILITY.md) and the
[experiment report](experiments/bounded_commit/README.md).

## Base framework v0

The implemented bounded software loop connects:

- **Explorer:** chooses from a finite action set;
- **Map:** maintains a small revisable state;
- **Measure:** compares realized consequence with an external target;
- **Memory:** preserves authorized outcome and provenance; and
- **Recovery:** restricts continuation and proposes a correction that is
  independently checked.

The clean control completed 12 transitions for each of three identity seeds.
At state 1, preserved negative consequence changed Explorer's later choice from
`ADVANCE` to `HOLD`. Across 42 clean/failure scenario runs, the campaign
observed zero protected false accepts, zero false rejects, and zero duplicate
authorizations. Twenty-one recoveries were authorized and nine deliberately
invalid recoveries were rejected. A correlated descendant-reference control
showed false confidence in all three presentations while the protected path
rejected their lineage.

See the [pre-registration](research/base-framework-v0-preregistration.md),
[results](research/base-framework-v0-results.md), [hardware mapping](docs/HARDWARE_FRAMEWORK_MAPPING.md),
and [Dream-RSI comparison](research/dream-rsi-comparison.md). The earlier RTL
authorization milestone remains unchanged and separately reproducible.

## Limitations

- Results apply to fixed seeds, bounded schedules, explicit configurations, and
  tested fault models; they do not establish universal fault tolerance.
- The protected source, checker, allocator, and gate control are trusted. The
  experiment does not protect against their common-mode corruption.
- `(transaction_id, epoch, source_record_id)` is sufficient only under the
  documented single-source, immutable-record, no-reuse assumptions. It is not a
  general causal provenance system.
- Unsupported faults were rejected, not repaired.
- External rejection does not roll back every internal side effect. The
  unchanged wrapper may update its internal keeper when it proposes a commit.
- Area figures are mapped synthesis estimates. No static timing, routed delay,
  power, or physical protection result is claimed.
- Clean-machine dependency installation has not been independently verified;
  the commands have been exercised in the recorded development environment.
- The complete five-component loop exists only as a bounded software research
  prototype. The repository does not implement a general agent, recursive
  self-improvement, general semantic correctness, or proof of safety.

Project source is licensed under [CERN-OHL-S-2.0](LICENSE). Third-party tools,
PDK files, and datasets keep their own licenses and are not redistributed. See
[provenance](docs/PROVENANCE.md) and [retained evidence policy](docs/EVIDENCE.md).
