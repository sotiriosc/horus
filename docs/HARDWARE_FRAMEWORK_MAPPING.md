# Hardware-to-framework mapping — public-safe draft

**Status: analysis and proposed experiments.** The correspondence is strongest for bounded numerical measurement, local state, and transactional replay. An arithmetic fabric, a finite-state controller, and a routing topology do not by themselves constitute an explorer or a world model. No complete five-part self-correction framework is implemented.

## Forward mapping

### Explorer

- **Requires:** choose actions, observe an environment, revise selection using outcomes.
- **Software approximation:** seeded numerical trials and explicit fault schedules in `sim/tile_skpr_recovery_arc.py` and `sim/horus_block_runtime.py`; these are fixed experimental policies.
- **State requirement:** addressable action IDs, observations, objectives and policy revisions across attempts.
- **Primitive:** [controller](../rtl/horus_controller.v) sequences computation; [router](../rtl/horus_router.v) transports flits through deterministic XY routing.
- **Evidence:** router/mesh benches execute delivery and backpressure checks. They do not measure adaptive exploration.
- **Missing:** outcome-driven action selection and discovery-history representation.
- **Failure test:** change the utility of two actions while keeping their routing identical; the existing fabric has no learned selection policy to switch between them.
- **Confidence:** LOW for Explorer; HIGH that scheduling and routing provide support primitives only.

### Map

- **Requires:** revisable representation of relevant external state and reachable alternatives.
- **Software approximation:** fixed tensor/block layouts and numerical format models; a scalar scale estimate is a narrow state estimate, not a general map.
- **State requirement:** versioned, addressable entity/relationship state plus observation associations.
- **Primitive:** route coordinates, input buffers, block registers and the [scale tracker](../rtl/skpr.v).
- **Evidence:** `tb/tb_tile_skpr_align.v` checks that metadata corresponds to the current block; `sim/test_scale_keeper.py` tests local tracking transitions.
- **Missing:** general map storage, revision protocol, semantic state addressing and independent map validation.
- **Failure test:** attach a correct scale tag to the wrong logical block or provide a stale state estimate; test whether identity/version checks reject it. Such a general protocol is absent.
- **Confidence:** LOW for a framework Map; MEDIUM for narrow local estimation support.

### Measure

- **Requires:** compare realized outcomes with an explicit expectation using a stated authoritative evidence source.
- **Software policy:** numerical scoreboards and [structured-output contracts](../experiments/structured_output/structured_output_controller.py); the controller compares against caller-supplied facts whose truth it assumes.
- **State requirement:** expectation, measured value, threshold, configuration and transaction identity.
- **Primitive:** [exponent-gap detector](../rtl/skpr_block_detect.v), tracker comparators and tags; arithmetic counters report local conditions.
- **Evidence:** detector golden vectors, keeper co-simulation, MLP/RTL comparison, and nine structured-output tests.
- **Missing:** independently authenticated expected outcomes in the deployed datapath; shared-code Python checks are not independent implementations.
- **Failure test:** corrupt a measurement and its derived comparison input together. A detector using only those descendants can accept a jointly incorrect state.
- **Confidence:** HIGH for implemented local predicates; LOW for general semantic or independent validation.

### Memory

- **Requires:** preserve relevant realized outcomes, associate them with their origin, and let them constrain later processing.
- **Software policy:** event traces, logical block counters, validation history and budget ledger.
- **State requirement:** persistent, addressable history or bounded sufficient statistics, with identity/version and retention rules.
- **Primitive:** [input delay buffer](../rtl/horus_input_buffer.v), router buffers, arithmetic accumulators, captured/repaired block registers, and persistent tracker registers.
- **Evidence:** keeper tests demonstrate history-dependent tags/reseeding; alignment tests exercise stalls/reset. The replay bench checks commit/update counts.
- **Missing:** durable event memory, lineage graph, authenticated origin/version fields and checkpoint restoration. Buffers are transient storage, not an evidence archive.
- **Failure test:** reset or roll a transaction counter while stale data remains in another stage; look for accepted old results under a new identity. Cross-module epoch protection is not supplied.
- **Confidence:** HIGH for bounded state affecting later local classifications; LOW for complete provenance-preserving Memory.

### Recovery

- **Requires:** detect and localize failure, restrict continuation, correct or restore state, independently recheck, then authorize continuation.
- **Software policy:** numerical repair modes and an experimental JSON controller that serializes supplied facts and checks the result.
- **State requirement:** failed transaction, original evidence, candidate correction, verification verdict, budget and authorization state.
- **Primitive:** [repair/replay wrapper](../rtl/horus_block_skpr_repair.v), [masked repair](../rtl/skpr_block_repair.v), valid/ready interfaces and reset.
- **Evidence:** `tb/tb_horus_tile_skpr_repair.v` checks replay/flag and commit/update counts. Clean and repaired numerical paths execute in the baseline.
- **Missing:** an independent post-repair semantic checker and an acceptance gate controlled by it; persistent known-good checkpoint and rollback protocol.
- **Failure test:** corrupt a repaired value after repair but before the wrapper's commit. In `ST_WAIT_REPLAY`, `norm_valid` triggers commit; no independent acceptance input is consulted.
- **Confidence:** HIGH for local transactional replay; LOW for the complete Recovery contract.

## Reverse mapping

| Existing primitive | Possible role | What it does not establish |
|---|---|---|
| NFE arithmetic, multipliers, MACs, normalizers | Execute proposed actions and numerical transformations | Exploration, truth, or semantic success |
| Controller FSM | Bounded scheduling and host handshake | Global reasoning or validation-based authorization |
| Router/mesh valid-ready interfaces | Transport and local backpressure | Fault-aware rerouting, verified provenance, or trustworthy content |
| Input/router buffers and captured block registers | Short-lived local state | Durable observation history or known-good checkpoint |
| `skpr` state/counters/tags | History-dependent local estimation and measurement | A world model or verified restoration |
| Gap detector and repair mask | Narrow detection/localization | Detection of every corrupt value or causal origin |
| Repair/replay wrapper | Withhold original flagged commit; replay and count one logical update | Independent proof that the replayed value is correct |
| Depth gate / accumulator clear | Restrict work by count; reset arithmetic state | Restriction triggered by a semantic validation verdict; rollback |
| RTL scoreboards and host assertions | External experiment-time comparison | An integrated on-device verifier |
| Structured-output controller | Scoped software validation, budget and recovery policy | Truth of supplied facts or general safety |

## Ten concrete questions

**A — Locality.** Detection, scale tracking and replay use bounded block/register state (`skpr_block_detect`, `skpr`, `horus_block_skpr_repair`). A global supervisor is not needed for those predicates. This does not prove that every useful semantic check is local.

**B — Consequence preservation.** The tracker changes its estimate/counters from past maxima and thereby changes later classifications. Software traces preserve outcomes during a run. Durable evidence-linked history is absent.

**C — Provenance.** Routing coordinates and logical counters identify limited transport/ordering context. They are not origin authentication or a causal graph; the relevant input/output interfaces do not carry a checked lineage certificate.

**D — Measurement.** Expected-versus-realized comparisons occur in host scoreboards and Python evaluators. Hardware detectors compare exponents against local criteria, not externally established task truth.

**E — Authority.** `commit_valid` is withheld for a flagged original block when repair is enabled. `horus_pgate_ctrl` limits execution by count, and the JSON controller refuses invalid results. No common hardware semantic-verdict gate connects these into the full proposed protocol.

**F — Restoration.** A block can be repaired and replayed; reset clears state. Reset and capture of the current block are not restoration of an independently known-good historical state. XY routing is not an adaptive recovery route.

**G — Independent verification.** A host RTL scoreboard can be implemented separately from the DUT. The deployed replay wrapper nevertheless commits on normalizer completion; proposer/checker separation is not an enforced hardware contract.

**H — Memory as computation.** Tracker state affects later tags and reseeding decisions, a real local computation using history. Evidence that it drives general policy improvement or semantic correction is absent.

**I — Local cross-reference.** The alignment bench compares detector, normalizer and tracker feeds for the same block. Those values share an origin and establish consistency, not necessarily independent truth.

**J — Descendant evidence.** No inspected module records/enforces causal independence of its validation evidence. The software runtime's clean oracle is a simulation control, not a deployed independent source. Agreement between two descendants of a corrupt input remains possible.

These conclusions follow from public candidate code and its scoped checks. The [next experiment](NEXT_EXPERIMENT.md) tests a small missing connection; it is not a claim that it already exists.
