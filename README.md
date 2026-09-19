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

**Experimental:** bounded independent authorization and a five-component
software framework through v2. The latest version joins two full observations
with a smaller orthogonal witness and validates their declared production paths
against a fixed process registry before allowing the existing commit gates.

**Observed limitation:** v2 blocked identical wrong A+B evidence while witness C
remained correct, but identical wrong A+B+C evidence and a deliberately false
registry each caused 3/3 out-of-model false accepts detected by the test oracle.

**Minimum-framework repair 1:** the frozen audit's three enforcement failures
are repaired. The [repair report](research/minimum-framework-repair-1-results.md)
records 126/126 protected passes, 109/109 direct checks, retained negative
controls, and fresh public regressions. The minimum framework is complete for
the declared bounded scope; architecture development stops here. Hardware cost
optimization remains deferred.

**Explorer-only model integration:** a local language model made 69 valid action
proposals through the frozen framework with zero observed integrity violations.
Verified history improved its proposal in only 1/6 matched pairs, below the
preregistered threshold. [Results and limits](research/model-explorer-integration-v0-results.md)
keep framework integrity separate from model usefulness. No other model role
was integrated.

**Explorer Memory study v1:** separate matched studies test verified negative
avoidance and preference for a verified positive alternative, using raw records
and semantic summaries. [The study report](research/model-explorer-memory-study-v1-results.md)
records all 224 model calls, the preregistered thresholds, and framework integrity
checks. The earlier integration result remains unchanged.

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
make base-framework-v1
make base-framework-v2
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

## Base framework v1 cross-source boundary

V1 keeps the v0 world, policy, Map, Measure, Memory bound, and Recovery
structure. It replaces the single receipt with registered Source A and Source B
paths. A partial pair cannot commit; disagreement permits one re-observation;
persistent disagreement stops without choosing a source.

Across 69 scenario runs, the protected single-channel-fault model observed zero
false accepts, zero false rejects, and zero duplicate authorizations. Twelve
transient/stale disagreements recovered and 30 persistent evidence failures
stopped. Cross-source-authorized Memory retained the v0 `ADVANCE → HOLD`
behavior in all three clean episodes.

The separate common-mode control corrupted A and B identically. The runtime
accepted all three wrong pairs during recovery, and only the hidden oracle found
the false commits. See the [v1 preregistration](research/base-framework-v1-preregistration.md),
[result report](research/base-framework-v1-results.md), and updated
[hardware mapping](docs/HARDWARE_FRAMEWORK_MAPPING.md).

## Base framework v2 evidence provenance

V2 retains the exact v1 world, sources, policy, and five-component loop. A
nine-node immutable registry now describes declared process dependencies, and
an independently implemented four-bit witness supplies a different relation to
the same transition. A complete A+B+C package must pass provenance, agreement,
role, registry-version, and declared process-separation checks before reaching
the inherited Measure, state, Recovery, Memory, and continuation gates.

Across 57 runs, all protected criteria passed: zero protected false accepts,
zero false rejects, zero duplicate authorizations, 9/9 transient recoveries,
and 12/12 blocks of the tested identical A+B corruptions. Authorized Memory
preserved the `ADVANCE → HOLD` behavior in all three clean episodes.

Two separately scored controls exposed the remaining trust roots. Identical
wrong A+B+C evidence committed falsely in 3/3 runs, and a deliberately corrupt
registry that hid derived paths also caused 3/3 false commits. See the
[v2 preregistration](research/base-framework-v2-preregistration.md),
[results](research/base-framework-v2-results.md), and
[hardware mapping](docs/HARDWARE_FRAMEWORK_MAPPING.md).

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
- Distinct source names, ports, and fault-domain labels do not prove actual
  causal independence. V1's common-mode control produced false accepts.
- V2 validates only dependencies declared in its trusted registry. It cannot
  discover an omitted edge or a shared corruption of A, B, and C; both trusted
  registry integrity and the witness production path remain assumptions.

Project source is licensed under [CERN-OHL-S-2.0](LICENSE). Third-party tools,
PDK files, and datasets keep their own licenses and are not redistributed. See
[provenance](docs/PROVENANCE.md) and [retained evidence policy](docs/EVIDENCE.md).

### Adaptive Explorer episode v0

The [adaptive episode study](research/model-explorer-adaptive-episode-v0-results.md)
ran 24 empty-history episodes and 288 real Explorer proposals through the frozen
framework. Integrity passed; neither the preregistered exploration effect nor
discovery-to-reuse criterion was established. All actions remained allowed;
uncertain retests and absent contradiction opportunities are reported separately.
[Reproduction and bounded evidence](experiments/model_explorer_adaptive_episode_v0/README.md)
include complete episode replay and the documented replay-only serialization fix.

### Semantic-prior study v0

The [semantic-prior study](research/model-explorer-semantic-prior-study-v0-results.md)
compares original action names with six rotated opaque mappings across 288 real,
matched, complete-history decisions. Integrity passed. Opaque rendering improved
selection of verified +1 over 0 and +1 over −1 by the preregistered criteria;
the 0-over−1 naming effect was not established. RETREAT-best selection was 7/36
under original names and 32/36 under aliases, while opaque 0-over−1 responses
always selected the first option. Labels are not assumed neutral. The frozen
framework and all earlier results remain unchanged.
[Reproduction and compact evidence](experiments/model_explorer_semantic_prior_study_v0/README.md)
cover exact replay and fresh regressions; detailed per-call evidence is retained
outside the public tree.

### Prior factorial v1

The [prior factorial study](research/model-explorer-prior-factorial-v1-results.md)
uses 216 real calls to independently cross alias mapping, option order and evidence
order in three targeted comparisons. RETREAT lexical interference replicated in
both positive targets and both opaque vocabularies. Verified +1>−1 value following
was stable across both opaque families and all order cells; stability across every
representation was not established. Target C remains unresolved under its dominance
criteria, with a narrower O2 option-position effect supported. Integrity and all
requested regressions passed; the framework and earlier results remain unchanged.
[Reproduction and compact evidence](experiments/model_explorer_prior_factorial_v1/README.md)
retain the frozen criteria and negative findings without expanding the sample.

### Contradiction-revision v0 feasibility checkpoint

The [contradiction-revision preflight](research/model-explorer-contradiction-revision-v0-results.md)
failed before model inference. The first changed state-1 HOLD event realized -1,
while frozen A/B/C reported +1 and the framework committed +1 to Memory. This
externally audited false accept makes the requested nonstationarity infeasible
under the frozen evidence boundary. Real model calls: zero; behavioral revision
remains untested. No architecture or prior result changed.
[Diagnostic reproduction and compact evidence](experiments/model_explorer_contradiction_revision_v0/README.md)
include exact failure replay and fresh preservation regressions.

### Realized-event grounding v0

The [realized-event grounding repair](research/realized-event-grounding-v0-results.md)
binds authorization to an immutable receipt emitted after external execution.
Changed HOLD −1 and ADVANCE +1 were authorized while retaining their old records
and contrary predictions. The bounded campaign passed 105 protected clean
authorizations and 20 atomic attack rejections with zero protected false accepts;
a deliberately dishonest trusted root still caused one out-of-model wrong accept.
A/B share the receipt root and are not independent truth measurements. Historical
regressions and the preserved old failing diagnostic remain unchanged. No new
model calls were made. [Reproduction and compact evidence](experiments/realized_event_grounding_v0/README.md)
state the software trust boundary and the untested model-revision question.
