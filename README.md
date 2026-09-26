# Horus

Horus is a reproducible research implementation of reduced-precision
arithmetic, block normalization, scale tracking, and bounded local fault
detection and recovery. It combines Verilog RTL with small Python reference
models and falsifiable experiments. It is a research codebase, not a
production-qualified processor or a general safety system.

## Current status

**Learning stability v0.4:** a hidden deterministic A-to-B outcome shift
produced 60 new authenticated receipts. Pure continuation improved the fresh
set from 8/12 to 10/12 but fell from 18/24 to 12/24 on the historical bank, so
the frozen lifecycle rejected it. The one permitted grounded-rehearsal
candidate also reached 10/12 fresh but only 14/24 historical and was rejected.
Generation 2 remains ACTIVE. See [the stability design](docs/HORUS_V0_4_LEARNING_STABILITY.md)
and [the completed result](research/learning-stability-v0/RESULTS.md).

**Grounded learning cycle v0.3:** Horus now keeps explicit consequence-model
generations, trains candidates outside the ACTIVE model, compares incumbent and
candidate on identical heldout receipt-grounded requests, and atomically
promotes or rejects under a frozen rule. The first cycle collected 60 new
authorized outcomes and promoted generation 2 after a 2/12 versus 12/12
comparison, with 10 corrections and no regressions in that small repetitive
heldout set. See [the lifecycle design](docs/HORUS_V0_3_LEARNING_CYCLE.md) and
[the completed result](research/learning-cycle-v0/RESULTS.md).

**Grounded consequence learning v0.2:** the independent consequence role now
has a checked-in rank-8 LoRA adapter trained only from 42 authorized realized
receipts. A session-separated held-out set improved from 6/12 to 8/12, with
four corrections and two regressions. A fresh-process reload and a six-step
live run verify that the adapter participates in the unchanged authority path
while authenticated Memory remains in later requests. See [the v0.2 design and
reproduction guide](docs/HORUS_V0_2_GROUNDED_LEARNING.md) and [the complete
result](research/grounded-learning-v0/RESULTS.md).

**Restartable Horus v0.1:** `python -m horus.run --live --steps 4 --session
/path/outside/the/repository` uses the established local joint Map model for
`next_state`, a separately requested consequence-only response, and the
unchanged grounded publication chain. Resume with the same command plus
`--resume`. Each process gets a fresh source identity and framework epoch;
signed prior outcomes enter model prompts only as imported proposal evidence.
See [the live runtime and trust boundary](docs/HORUS_V0_1_LIVE.md).

**Runnable Horus v0:** `python -m horus.run` now executes a grounded two-episode
closed loop. An original receipt from episode 1 is authorized into Memory and
changes episode 2's mechanical action selection. The application uses the
existing joint Map path for next state, an independent authenticated-history
consequence adapter, mechanical reconciliation and Explorer comparison, and the
existing receipt/Measure/authorization/Recovery/Memory chain. See
[the v0 architecture and limits](docs/HORUS_V0.md).

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

### Contradiction revision v1 feasibility

The [complete contradiction fixture](research/model-explorer-contradiction-revision-v1-feasibility-results.md)
constructed CONTROL and SHIFT H0/H1/H2 through the unchanged realized-event repair.
All 14 primary transactions committed correctly, including three authenticated
contradictions, with old history and original predictions preserved. Exact replay
and historical regressions passed; the old stationary-path failure remains intact.
Zero model calls were made. This establishes safely constructed contradictory
histories within the software trust root, not model revision.
[Reproduction and compact evidence](experiments/model_explorer_contradiction_revision_v1_feasibility/README.md)
include chronological previews, provenance checks and the final feasibility criteria.

### Contradiction revision v1 behavioral study

The [144-call contradiction study](research/model-explorer-contradiction-revision-v1-results.md)
ran the frozen Explorer-only design through authenticated CONTROL/SHIFT histories.
O1 met every registered revision criterion. O2 reached 8/12 SHIFT-H2 ADVANCE choices
and 7/12 favorable matched pairs, below the required 9/12 and 8/12. Overall
replication was therefore **not established**; no pooling, prompt change or extra
calls were used. All 144 proposals were valid, with zero protected false accepts
and old history preserved. Exact replay and historical regressions passed.
[Reproduction and compact evidence](experiments/model_explorer_contradiction_revision_v1/README.md)
retain the family-specific findings and the unchanged software trust boundary.

### Representation priors and first model Map proposal

The [representation-prior checkpoint](research/representation-priors-and-neutrality-checkpoint.md)
preserves the finding that opaque aliases do not establish neutrality, without a
new Explorer token campaign or any upgrade to earlier claims.

The [first Map-proposal study](research/model-map-proposal-v0-results.md)
passed its 16-case zero-call boundary gate, then completed exactly 144 real calls:
142 valid predictions and two safe schema rejections, with zero protected false
accepts. Both families achieved 12/12 exact SHIFT-H2 predictions and favorable H2
pairs, but both had 0/12 exact old predictions at SHIFT H0; the all-valid gate also
failed. **Contradiction-driven Map revision was not established** under the frozen
criteria. Predictions remained distinct from receipt-authoritative reality.
Exact replay and all 20 regression commands returned their expected outcomes.
[Reproduction and compact evidence](experiments/model_map_proposal_v0/README.md)
retain the failed prerequisites, state/consequence decomposition and trust boundary.

### Established-prior Map revision v1

The [bounded follow-up](research/model-map-established-prior-revision-v1-results.md)
uses two authentic old HOLD observations before an external consequence change,
with the Map adapter, parser, prompt, deterministic Explorer and authority unchanged.
**ESTABLISHED-PRIOR MAP REVISION REPLICATED**.
O1: SHIFT P0 exact old 12/12, SHIFT P2 exact new 12/12, favorable P2 pairs 12/12; O2: SHIFT P0 exact old 12/12, SHIFT P2 exact new 12/12, favorable P2 pairs 12/12.
All 144 registered calls completed: 144 valid and 0 safely rejected,
with zero protected false accepts. Exact replay and 23 regression commands returned
their expected outcomes. The original Map-v0 NOT ESTABLISHED result is unchanged;
no studies were pooled and no persistent/weight-learning claim is made.
[Reproduction and compact evidence](experiments/model_map_established_prior_revision_v1/README.md)
retain the complete criteria, component analyses and software trust boundary.

### Recovery proposal v0 interface checkpoint

The [zero-call Recovery checkpoint](research/model-recovery-proposal-v0-results.md)
stopped at the mandatory interface gate: the frozen coordinator constructs native
Recovery inline and exposes no configurable proposal source. **Model Recovery
usefulness is UNTESTED / NOT ESTABLISHED; zero model calls were made.**
The 32-transaction native diagnostic preserved authorization and atomic rejection,
with zero protected false accepts. Eight of the 12 world transitions require state
Recovery; HOLD retains a valid incumbent. Exact diagnostic replay and all 25
regression commands returned their expected outcomes. No architecture was changed.
[Reproduction and compact evidence](experiments/model_recovery_proposal_v0/README.md)
distinguish native integrity from the untested model adapter.

### State Recovery proposal interface v1

The [separate zero-call interface layer](research/state-recovery-proposal-interface-v1-results.md)
lets a deterministic external source propose only a bounded replacement-state value.
Native Recovery owns the attempt and identity/status envelope; the existing authorizer
and receipt-bound staged publication remain unchanged. All 32 default diagnostic cases
matched exactly; correct/wrong proposals and malformed/failing sources passed the
operational checks. **C — NOT ESTABLISHED:** the mandatory low-level wrong-status
rejection failed in both historical and new unchanged authorizers (8/8 acceptances each).
No model calls were made. Exact replay and all 28 regression commands returned their
expected outcomes. The old Recovery-v0 checkpoint remains blocked and unchanged.
[Reproduction and compact evidence](experiments/state_recovery_proposal_interface_v1/README.md)
retain this unresolved requirement; no model campaign was launched.

### State Recovery authorizer status binding v1

The [separate zero-call status repair](research/state-recovery-authorizer-status-binding-v1-results.md)
is **A — STATE RECOVERY STATUS BINDING COMPLETE**. In trusted coordinator-owned
Recovery scope, the authorizer now requires RECOVERING status and delegates all
remaining checks to the historical implementation. Ordinary PROPOSED transactions
remain unchanged. The 136-cell enum matrix preserved 16 RECOVERING acceptances and
rejected all 120 other-status candidates; 25 wrong-status transactions rejected
atomically. Default and injected interface records matched exactly. Exact replay
and all 31 regression commands returned expected outcomes. The old interface-v1 C
and Recovery-v0 blocked checkpoints remain unchanged. Zero model calls; no model
campaign was launched. [Reproduction and verification](experiments/state_recovery_authorizer_status_binding_v1/README.md)
record the scoped contract, evidence and unchanged software trust boundary.

### Model Recovery proposal v1

The [96-call Recovery-only study](research/model-recovery-proposal-v1-results.md)
used the unchanged repaired value-only boundary after verified failure.
**MODEL RECOVERY PROPOSAL USEFULNESS REPLICATED.**
O1: 48/48 valid, 41/48 receipt-consistent, 0 malformed.
O2: 48/48 valid, 44/48 receipt-consistent, 0 malformed.
Recovery authorization integrity **PASS**, with zero protected false accepts.
The realized next state was visible in verified context; this is bounded proposal
generation, not hidden-state inference or general Recovery reasoning. Exact replay
and all 33 regression commands returned expected outcomes. No retries, replacement
calls, extensions or role combinations occurred. Historical A/C/blocked checkpoints
remain unchanged. [Reproduction and compact evidence](experiments/model_recovery_proposal_v1/README.md)
retain family thresholds, target/action/token breakdowns and the software trust boundary.

### Model proposal role composition v0

The [zero-call composition checkpoint](research/model-proposal-role-composition-v0-results.md)
is **C — NOT ESTABLISHED**. The unchanged Map adapter only admits state 1 / HOLD;
all three required state-0 first actions reject safely before execution. Existing
opaque Explorer projections also reject empty Memory. No model calls or interface
changes occurred. Full sequential composition and model behavior remain untested.
Diagnostic replay matched exactly and all 33 historical regression commands
returned expected outcomes, including preserved negative checkpoints.
[Reproduction and compact evidence](experiments/model_proposal_role_composition_v0/README.md)
distinguish this domain blocker from an authority failure.

### Composition input bindings v1

The [zero-call binding checkpoint](research/composition-input-bindings-v1-results.md)
is **A — COMPOSITION INPUT BINDINGS READY**. Separate Explorer/Map inputs support
empty experience and all 12 state/action pairs while historical adapters and
authority remain unchanged. All A–O properties have executed synthetic evidence;
36 initial transactions and an eight-step episode publish authentic events, and
12 correct/12 wrong Recovery proposals authorize/reject independently. Exact
replay, the old blocked composition-v0 checkpoint and historical regressions pass
with their expected outcomes. No model calls; the live campaign remains unrun.
[Reproduction and compact evidence](experiments/composition_input_bindings_v1/README.md)
record the finite scope and unchanged trust boundaries.

### Model proposal role composition v1

The [first live composition study](research/model-proposal-role-composition-v1-results.md)
is **C — NOT ESTABLISHED**: 21 real calls (12 Explorer, 9 Map, 0 Recovery).
All 12 episodes stopped before their first execution: 3 malformed Explorer
responses and 9 malformed Map responses. No world events or Memory records were
produced, so real sequential composition remains untested. The observed parser
boundaries held; no retry, replacement or additional inference followed. The
288-context UNKNOWN preflight, 41 post-live synthetic controls, seven-file exact
replay and 39 post-campaign validation commands returned expected outcomes.
[Compact evidence and reproduction](experiments/model_proposal_role_composition_v1/README.md)
keep the negative live finding separate from the preserved synthetic parent A.

### Composition initial Map schema diagnosis v0

The [zero-call forensic diagnosis](research/composition-initial-map-schema-diagnosis-v0-results.md)
identifies a **concrete model/parser specification gap**: all nine live Map objects
return a string consequence, while exact integer types/domains are not explicitly
stated in the visible contract. Four consequences are bare K2 tokens; five are
sentences mentioning the target token. Historical non-empty Map prompts contain
numeric outcome examples and show 286/288 schema compliance, versus 0/9 in the
empty-history composition calls. This is an association, not a causal explanation.
Composition-v1 remains C; no prompt, parser, projection or response was changed.
[Compact findings and reproduction](experiments/composition_initial_map_schema_diagnosis_v0/README.md)
retain deterministic regeneration and four focused historical replays. No new
model calls or next experiment.

### Composition empty-history schema contract v0

The [18-call paired contract study](research/composition-empty-history-schema-contract-v0-results.md)
meets its frozen **SCHEMA-CONTRACT EFFECT SUPPORTED** criterion: the original
instruction yields 0/9 valid outputs, versus 9/9 for an explicit integer/domain
contract. All nine pairs improve; O1 improves 0/4 → 4/4 and O2 0/5 → 5/5.
The original contexts, user bytes, seeds, sampler and parser are unchanged.
No world event executes and no Memory is fabricated. This is schema compliance,
not prediction accuracy or composition success; composition-v1 remains C.
[Compact evidence and reproduction](experiments/composition_empty_history_schema_contract_v0/README.md)
record five-file exact replay and five unchanged historical checkpoints.
No composition rerun or next experiment followed.


### Model proposal role composition v2 — interrupted

The [v2 checkpoint](research/model-proposal-role-composition-v2-results.md) is
**C — NOT ESTABLISHED** after a reported computer crash removed the temporary live
evidence directory. The preregistration and frozen implementation survived; exact
live totals and replay are unavailable. Surviving console output reports at least
18 calls and seven commits, not a complete auditable campaign. No replacement
inference was performed. The recovered preflight, bounded controls and historical
regressions passed, with all previous results unchanged.
[Compact status and verification](experiments/model_proposal_role_composition_v2/README.md)
keep missing live evidence distinct from synthetic or historical success.


### Composition v2 replacement R1

The [independent replacement checkpoint](research/model-proposal-role-composition-v2-replacement-r1-results.md)
is **A — MULTI-ROLE PROPOSAL COMPOSITION INTEGRITY PASS**: 164 real calls,
68 executions and 66 authenticated commits.
The scientific protocol is unchanged; durable write-ahead call and transaction
records distinguish intent, response, parsing and finalized state. R1's ten-file
replay plus Memory snapshots match exactly, and all 41 post-campaign checks return
expected outcomes. The original interrupted v2 remains C with unavailable live
evidence; no partial data was pooled. [Compact evidence and reproduction](experiments/model_proposal_role_composition_v2_replacement_r1/README.md)
separate integrity, predictive accuracy and behavioral metrics. No R2 or push.

## Composition Map Memory ablation v0

The separate [42-context paired Map-only study](research/composition-map-memory-ablation-v0-results.md)
supports the frozen authenticated-history visibility effect: exact predictions
33/42 with history versus 11/42 withheld, 22 favorable and zero reverse exact
discordances. Both families passed. All 84 responses were valid; nine history-visible
predictions remained wrong, and one next-state comparison worsened. Eight evidence
files replayed byte-identically with zero inference; R1 and prior checkpoints remain
unchanged. No experimental world execution or Memory writes. This result concerns
input information visibility, not weights or persistent model learning.

## Cross-episode authenticated Memory boundary v0

The [zero-call boundary feasibility study](research/cross-episode-authenticated-memory-boundary-v0-results.md)
is **C — NOT ESTABLISHED**. Existing epoch transitions preserve authenticated
Memory/pairs/packages, chronology, UNKNOWN and ordinary FIFO eviction, but retain
current state. Fresh construction resets state and discards history. The required
fresh-state initialization with retained provenance has no existing supported API.
No core repair or model campaign was started; prior checkpoints remain unchanged.

## Cross-episode initialization boundary v1

The [separate zero-call repair](research/cross-episode-initialization-boundary-v1-results.md)
is **A — CROSS-EPISODE INITIALIZATION BOUNDARY COMPLETE**. A trusted staged boundary
resets external/current state from 3 to 0 while preserving authenticated history,
source lifetime and ordinary authority. A separate Map projection exposes epoch
identity; historical projections stay unchanged. All 24 reset-failure cases were
atomic; exact replay, six new tests and 49 historical tests passed. The old v0 C
remains preserved. Atomicity is limited to the in-process simulator; no model
campaign, main/tag changes or push.

## Cross-episode model transfer v0

The [48-call paired study](research/cross-episode-model-transfer-v0-results.md)
is **CROSS-EPISODE AUTHENTICATED-MEMORY BEHAVIORAL TRANSFER NOT ESTABLISHED**.
Explorer met its frozen rule: CARRY selected ADVANCE 10/12 versus FRESH 5/12.
Map exact prediction was 3/12 versus 0/12, but its three favorable pairs fell
below the required four. All calls completed once, exact replay and preservation
passed, and no model probe changed protected state. The result concerns authenticated
external history supplied to stateless requests; no persistent model learning.
See the [frozen thresholds](research/cross-episode-model-transfer-v0-preregistration.md)
and [compact paired results](experiments/cross_episode_model_transfer_v0/results.json).

## Cross-episode Map history depth v1

The [36-call Map-only depth study](research/cross-episode-map-history-depth-v1-results.md)
is **TWO-OBSERVATION CROSS-EPISODE MAP EFFECT SUPPORTED**.
Exact predictions were D0 0/12, D1 7/12 and D2 10/12;
D2-versus-D0 favorable/reverse pairs were 10/0.
All 36 calls completed once. Exact replay, independent scoring audit and historical
preservation passed. Authentic one/two-observation histories survived trusted
fresh-state initialization; probes remained read-only. The prior transfer-v0
overall NOT ESTABLISHED result is unchanged. This concerns stateless proposals
conditioned on authenticated external history, not persistent model learning.
See the [frozen criteria](research/cross-episode-map-history-depth-v1-preregistration.md)
and [compact results](experiments/cross_episode_map_history_depth_v1/results.json).

## Cross-episode stale-Memory feasibility v0

The [zero-model feasibility study](research/cross-episode-stale-memory-feasibility-v0-results.md)
is **A — CROSS-EPISODE STALE-MEMORY FIXTURE FEASIBLE**. After trusted reset,
authentic new −1 target events coexist with the preserved old +1 observations:
CONTROL [+1,+1,+1,+1], CHANGED [+1,+1,−1,−1]. P0/P1/P2 are at actual state 0;
the primary history uses seven records without eviction. Existing native state
Recovery ran twice in CHANGED and zero in CONTROL, without rewriting predictions,
receipts or history. Four invalid receipt submissions were rejected; separate
FIFO controls, exact replay and all seventeen completion gates passed. Zero model
calls; historical results and authority architecture remain unchanged. This is
history/provenance feasibility, not a model adaptation result.
See [preregistration](research/cross-episode-stale-memory-feasibility-v0-preregistration.md)
and [compact results](experiments/cross_episode_stale_memory_feasibility_v0/results.json).

## Cross-episode stale-Memory Map revision v1

The [144-call Map-only study](research/cross-episode-stale-memory-map-revision-v1-results.md)
is **CROSS-EPISODE STALE-MEMORY MAP REVISION REPLICATED**.
Valid responses: 144/144. O1 CHANGED P0 old / CHANGED P2 new /
CONTROL P2 old: 12/12/12 of twelve each;
O2: 12/12/12.
Both families were evaluated independently against unchanged preregistered gates.
All calls completed once; exact replay and historical preservation passed.
Authentic old/new evidence remained present, and measured proposals never executed
or changed Memory. This concerns stateless proposal behavior, not persistent learning.
See [frozen thresholds](research/cross-episode-stale-memory-map-revision-v1-preregistration.md)
and [compact trajectories/results](experiments/cross_episode_stale_memory_map_revision_v1/results.json).

## Cross-episode stale-Memory Explorer revision v1

The [144-call Explorer-only study](research/cross-episode-stale-memory-explorer-revision-v1-results.md)
is **CROSS-EPISODE STALE-MEMORY EXPLORER REVISION NOT ESTABLISHED**. Valid responses: 144/144.
O1: CHANGED P0 HOLD 12/12; CHANGED P2 RETREAT 1/12; CONTROL P2 HOLD 12/12.
O2: CHANGED P0 HOLD 12/12; CHANGED P2 RETREAT 0/12; CONTROL P2 HOLD 12/12.
Both opaque families use their own unchanged preregistered gates.
All calls completed once; exact replay and historical preservation passed.
Older true history and new contradictory outcomes coexist; no measured action
executes or writes Memory. This concerns stateless proposals, not persistent learning.
See [frozen thresholds](research/cross-episode-stale-memory-explorer-revision-v1-preregistration.md)
and [compact results/trajectories](experiments/cross_episode_stale_memory_explorer_revision_v1/results.json).

## Explorer value-aggregation contract v0

The separate [96-call Explorer A/B study](research/explorer-value-aggregation-contract-v0-results.md)
is **EXPLICIT-MEAN EXPLORER POLICY NOT ESTABLISHED**. Valid responses: 96/96.
O1: CONTROL B HOLD 12/12; CHANGED A/B RETREAT 2/12 and 4/12; favorable CHANGED pairs 2/12.
O2: CONTROL B HOLD 12/12; CHANGED A/B RETREAT 0/12 and 2/12; favorable CHANGED pairs 2/12.
A preserves the original instruction; B explicitly specifies arithmetic mean over
all verified outcomes. Only the system instruction differs within matched pairs.
Exact replay and historical preservation passed; no measured action executed.
The preceding Explorer NOT ESTABLISHED checkpoint remains unchanged.
This tests an explicitly instructed policy, not spontaneous adaptation or learning.
See [frozen thresholds](research/explorer-value-aggregation-contract-v0-preregistration.md)
and [compact results/pairs](experiments/explorer_value_aggregation_contract_v0/results.json).

## Map-guided Explorer interface v0

The separate [zero-call architectural study](research/map-guided-explorer-interface-v0-results.md)
is **A — MAP-GUIDED EXPLORER INTERFACE READY** within its read-only input-binding scope.
All 18 invariants and 82 deterministic cases passed, including wrong forecasts,
invalid/missing forecasts, stale rejection and empty-history handling.
Only finite parsed forecasts enter Explorer; neither role gains truth or authority.
Exact replay, 75 tests and ten historical replays passed. Both Explorer negatives
and the Map REPLICATED result remain unchanged. No live model calls or behavior claim.
See [registration](research/map-guided-explorer-interface-v0-preregistration.md)
and [compact controls/results](experiments/map_guided_explorer_interface_v0/results.json).

## Map temporal-relation forecast v0

The [receipt-scored Map-only study](research/map-temporal-relation-forecast-v0-results.md)
completed exactly 96 calls. **MAP TEMPORAL-RELATION FORECASTING BEYOND PURE RECENCY NOT ESTABLISHED**.
The registered F/P histories share counts and latest value but differ in order and seventh realized outcome.
All earlier results remain unchanged. See [preregistration](research/map-temporal-relation-forecast-v0-preregistration.md),
[all parsed outcomes and frozen gates](experiments/map_temporal_relation_forecast_v0/results.json),
and [executed verification](experiments/map_temporal_relation_forecast_v0/verification.json).

## Map–Explorer oracle decomposition v0

The [registered proposal-only diagnostic](research/map-explorer-oracle-decomposition-v0-results.md)
completed 269 real calls: 240 mandatory and 29 eligible conditional calls.
**PIPELINE NOT FULLY ESTABLISHED**. Forecast ranking, oracle comparison and following-Map
remain separate decisions; ties intentionally leave conditional slots unissued.
The prior temporal negative remains unchanged. See [preregistration](research/map-explorer-oracle-decomposition-v0-preregistration.md),
[compact per-context results](experiments/map_explorer_oracle_decomposition_v0/results.json),
and [verification](experiments/map_explorer_oracle_decomposition_v0/verification.json).

## Explorer finite-value comparator v0

The [detached comparator study](research/explorer-finite-value-comparator-v0-results.md)
completed exactly 144 real Explorer calls with no Map call, world execution or Memory change.
**ZERO-OVER-NEGATIVE COMPARATOR NOT ESTABLISHED**; independently, **NEXT_STATE IRRELEVANCE NOT ESTABLISHED**.
The two positive-best controls remain descriptive; prior results are unchanged. See
[preregistration](research/explorer-finite-value-comparator-v0-preregistration.md),
[compact results including all 72 matched pairs](experiments/explorer_finite_value_comparator_v0/results.json),
and [verification](experiments/explorer_finite_value_comparator_v0/verification.json).
