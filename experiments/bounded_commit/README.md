# Bounded independent commit checking: experimental result

**IMPLEMENTED / OBSERVED, as a separate development after the approved baseline.** The protected-source protocol passed 4,200 transactions under the declared narrow fault model. The correlated-reference negative control falsely agreed on 300 corrupted proposals. The result supports bounded local authorization under explicit trust assumptions; it does not establish that the added hardware is cheap.

## Baseline and exact implementation changes

The approved public candidate was preserved byte-for-byte before implementation, with its 143-file manifest. Existing arithmetic, detector, repair, normalizer, tests and the original research/proposal documents are unchanged. The original `docs/NEXT_EXPERIMENT.md` is retained as the historical pre-implementation proposal; this document records the subsequent experiment, not a retrospective change to baseline capability.

New files in this directory:

- `independent_spec.v`: independent integer specification, source-domain validation and numerical check.
- `commit_gate.v`: two protected-source slots, two matching proposal/quarantine slots, identity checks, timeout, external acceptance and an eight-record trace ring.
- `bounded_commit_top.v`: connects one unchanged public repair wrapper to the new gate; captures source evidence, then launches the separately faulted copy one cycle later. Fault controls exist only for this experiment.
- `descendant_control.v`: deliberately incorrect shadow checker, visibly separate from the real sink.
- `tb_campaign.v`, `tb_spec.v`, `tb_gate_edges.v`: fixed campaign and adversarial protocol checks.
- `run.py`, `synthesize.py`: actual tool invocation, bounded execution, failure propagation and provenance.
- This report and `results.json`: compact measured evidence. Raw logs and mapped netlists stay outside the source tree.

Only the development README, Makefile and public manifest are updated to expose the new experiment. The baseline manifest is preserved as `BASELINE_MANIFEST.json`.

## Reproduction and tests added

With Python 3.10+ and Icarus Verilog/vvp:

```sh
make independent-commit
# Optional: choose a new output directory OUTSIDE this source tree.
python3 experiments/bounded_commit/run.py --output /tmp/horus-commit-run
```

The command executes 21 fixed schedules: seeds 1, 2, 3 × seven modes. Each schedule has 200 positions: 100 clean and 100 fault-designated positions; the clean counterfactual disables faults at all 200 positions. The provenance control is split into ID and epoch variants, and source-record identity adds one further control. Each seed uses the same deterministic stall sequence across modes. Numerical input is intentionally constant, so equal values cannot substitute for identity.

`tb_spec` tests the known clean answer, every one-bit mutation of 104 output bits, every one-bit mutation of the protected source outside the supported domain, and wrong target/threshold/mode/scale (213 checks). `tb_gate_edges` covers duplicate proposals, paused checking without authorization, missing/late proposal, checker timeout, sink timeout and reset followed by stale epoch. Campaign assertions verify fault localization, replay counts, exactly-once acceptance, FIFO association, queue bounds, timeout bounds and retained trace contents. The established `make test` suite also passed all 53 steps after integration.

## All control results

| Control | Transactions | Correct accepts | Rejections | False accepts (protected) | Wrong-shadow false accepts |
|---|---:|---:|---:|---:|---:|
| Clean counterfactual | 600 | 600 | 0 | 0 | 0 |
| Corruption + working repair | 600 | 600 | 0 | 0 | 0 |
| Corrupted repair | 600 | 300 | 300 | 0 | 0 |
| Swapped transaction ID | 600 | 300 | 300 | 0 | 0 |
| Stale epoch | 600 | 300 | 300 | 0 | 0 |
| Shared-descendant shadow | 600 | 300 | 300 | 0 | 300 |
| Wrong source-record identity | 600 | 300 | 300 | 0 | 0 |


Each rejection-control schedule includes 100 clean transactions that must still succeed. The shared-descendant row reports the protected gate rejecting the bad proposals AND the separate wrong architecture accepting them. Its 300 false accepts are the expected negative result, not failures of the protected-source architecture.

Fault injection raises lane 3's exponent from 10 to 40 after protected capture; KEEP mode, threshold 13, target 32. Each clean source word is sign 0, exponent 10, fraction 16 (integer 656). Each expected normalized word is sign 0, exponent 32, fraction 16 (integer 2064); expected block-scale metadata is 10. Failed-repair control flips one mantissa bit AFTER repair/replay. Provenance faults alter ID, epoch or source-record identity while leaving numerical values correct. The wrong shadow supplies its reference from that same corrupted candidate and consequently agrees with itself.

## Metric table

| Metric | Protected campaign result |
|---|---:|
| Logical transactions | 4,200 |
| Correct accepts | 2,700 |
| Expected checker rejections | 1,500 |
| False accepts | 0 |
| False rejects | 0 |
| Duplicate accepts | 0 |
| Transaction-ID mismatches rejected | 300 |
| Epoch mismatches rejected | 300 |
| Source-record mismatches rejected | 300 |
| Timeout rejections in normal bounded-stall campaign | 0 |
| Replay retries | 1,800 |
| Minimum / maximum cycles to decision | 5 / 36 |
| Maximum quarantined proposals | 2 |
| Maximum outstanding protected records | 2 |
| Trace slots retained in hardware | 8 |
| Declared additional sequential storage | 1,673 bits |
| Integrated mapped flip-flops, including DUT | 2,280 |

Three additional directed timeout cases reject as intended: missing proposal, checker withheld and sink permanently stalled. These are tested fault/liveness outcomes, separate from false rejects in the normal campaign. Detailed per-seed metrics, including backpressure cycles and cycle sums, are in `results.json`.

## Minimal provenance and authority

The implemented tuple is `(transaction_id:16, epoch:8, source_record_identity:16)`. A trusted source supplies monotonically increasing transaction IDs, a fresh epoch on reset, unique record identities, original eight words, target, threshold and mode. Evidence occupies its own register bank before injection. A trusted local slot reservation associates each in-flight DUT operation with one protected record; supplied candidate labels cannot choose a different reference record. All three candidate tuple fields must match that slot's protected tuple. Equal numerical values cannot overcome identity failure.

For this single-source, in-order, non-wrapping experiment, `(epoch, transaction_id)` could identify the record by convention: a separate record ID is logically redundant if that binding is guaranteed. It is retained explicitly and tested to expose source-channel misbinding. No hash, signature or general lineage graph is needed for the declared model. The protection and trusted allocation assumptions do the work; a matching tuple is not cryptographic authenticity. Mutable configuration would require preserving/binding its version or value; here target/threshold/mode are immutable, captured and domain-checked. Epoch or ID wrap, reuse and cross-reset replay beyond the trusted-source contract are excluded, not solved.

Internal `commit_valid` is only availability of a proposal. The gate requires a protected record, identity agreement and independently computed numerical agreement. Only `sink_valid && sink_ready` transfers a value. Paused checking produces no authorization. Neither detector flags nor repair validity certify numerical truth. No correction retries follow a checker rejection; the existing DUT performs at most one repair replay.

## Bounded state and delayed decisions

Reservations are limited to two across source and quarantine together, rather than allowing an additional hidden unbounded evidence queue. A full reservation bank backpressures admission; source identity/data are captured only on handshake. One DUT operation is active at a time. Pending proposal data cannot overwrite a slot already containing a proposal. Decisions are FIFO; an accepted or rejected slot is retired once.

The age counter saturates at 63. An unresolved head transaction rejects at that limit (within 64 rising-edge intervals from admission). Timeout enters fail-stop: new admission and late proposal acceptance stop until reset with a fresh trusted epoch; already reserved slots drain by rejection at their deadlines. Thus a late result cannot be reassigned to a newly recycled slot. A sink stall reaching the deadline cancels the transaction; this is a bounded experimental transfer protocol, not an AXI interface promising to hold VALID forever.

The hardware trace is a fixed eight-entry ring of 96-bit records, plus one 96-bit decision output register. Older records are overwritten; exhaustive historical trace is intentionally not a runtime requirement. The external simulation emits at most 200 fixed-size records per schedule. Host log files are experiment evidence, not queues or memory available to the hardware protocol. No private history/log implementation was reused.

Trace bit layout (remaining high bits reserved): ID `[62:47]`, epoch `[46:39]`, source-record identity `[38:23]`, detector-reported fault `[22]`, localized lane `[21:19]`, proposal arrived `[18]`, ID/epoch/record verdicts `[17:15]`, numerical verdict `[14]`, authorization `[13]`, retries `[12:11]`, accepted `[10]`, rejected `[9]`, timeout `[8]`, age `[7:0]`. When no proposal arrives, detector diagnostics are unreported; zero is not proof that no fault occurred. A paused/timed-out checker has false verdict bits, explicitly qualified by timeout/proposal status.

Additional declared RTL state (excludes existing DUT, combinational wires/integers):

| Component | Bits | Role |
|---|---:|---|
| Protected evidence, 2 × (40 identity + 104 words + 14 configuration) | 316 | Pre-fault truth in distinct bounded channel |
| Quarantine, 2 × (40 identity + 104 words + 6 scale + 6 diagnostics) | 312 | Candidate proposals |
| Per-slot validity, arrival and age | 16 | Bounded ownership and deadline |
| Head/tail/count, halt and decision-valid | 6 | Gate control |
| Decision record | 96 | Fixed output record |
| Trace ring and write index | 771 | Eight 96-bit entries plus 3-bit index |
| Capture/launch/identity/diagnostics around DUT | 156 | One active transaction |
| **Total** | **1,673** | All declared additional sequential bits |

Maximum occupied reservations and quarantine entries reached two in every campaign; the trace ring wrapped and its retained entries were checked. This is simulation plus structural bounds, not formal verification against arbitrary faults.

## Checker-independence review

The independent specification reads only protected original words/configuration and proposed values/scale. It contains no module instantiation, imported golden model, DUT normalization function or repair function. Its own integer expression applies the known common offset in the explicitly validated constant-scale domain. The repaired result never constructs protected expected truth. The old normalizer remains solely in the DUT. The positive clean test and exhaustive single-bit mutation probes audit this intentionally tiny specification.

Implementation independence is not immunity to a wrong specification, common-mode hardware fault, corrupted protected source, malicious source allocator or faulty checker. Those remain trusted/outside the tested fault model. `descendant_control` intentionally violates evidence independence; it is isolated from the protected sink and labeled negative throughout.

## Hardware/resource overhead

Synthesis used Yosys 0.9 (git sha1 1979e0b), Icarus 11.0 for simulation, and separately installed Sky130 HD TT 025C/1v80 liberty. Library SHA-256: `8e78e14442062dba34d414fca6490b2f6b96038d4510d1438ca44fee31487135`. All reported cells are mapped, including flip-flops; no unmapped sequential cells are omitted from area.

| Build | Mapped area (µm²) | Cells | Flip-flops |
|---|---:|---:|---:|
| checker | 3,439.5488 | 488 | 0 |
| gate_without_trace | 29,928.7040 | 2964 | 746 |
| gate_with_trace | 58,937.7760 | 5436 | 1517 |
| integrated | 88,376.0096 | 8178 | 2280 |
| original_wrapper_all_ports | 36,471.2288 | 3951 | 841 |


The standalone gate measures the added authorization primitive with protected records, quarantine and checking. Its checker-only row is INCLUDED in the gate, not additive. Identity/epoch/record checking uses three equality comparisons over 40 bits and stores both tuples (80 bits across two protected slots plus 80 across two candidate slots); exact separate cell area is not attributable after optimization. Protected and quarantine storage costs are itemized in bits above; cells include reset, selection and control muxing.

Removing only the trace ring by a synthesis parameter reduces the standalone gate by **29,009.0720 µm² and 771 flip-flops**. The measured default retains the required trace. The original-wrapper row exposes a different set of ports/counters from the integrated experiment, so subtracting those two areas is NOT a controlled incremental-overhead estimate. Both absolute figures are retained to prevent a misleading subtraction. No timing/STA, routed delay, power or clock-frequency measurement was performed; these areas establish no timing guarantee.

The 29,929 µm² gate even without the ring is substantial. This first implementation tests the protocol, not an optimized cell budget. Bounded/local does not imply cheap; compact trace encoding and storage implementation deserve separate evaluation without weakening evidence independence.

Optional reproduction:

```sh
python3 experiments/bounded_commit/synthesize.py --liberty "$SKY130_HD_LIB"
```

## Unexpected behavior and conclusion

No unexpected behavioral failure occurred in the final control campaign. During development, a SystemVerilog reserved instance name required a syntax correction; it did not change the protocol or thresholds. The sizable trace/record cost is the main caution from synthesis. Timing remains unmeasured and no physical protection mechanism for the trusted source was implemented.

The hypothesis survived this bounded test: a local repaired proposal can be held until its identity and exact numerical result agree with protected pre-fault evidence, and all tested accepted transactions transfer exactly once. A descendant-only reference can falsely agree, as the negative control demonstrates.

The narrowest defensible conclusion is **a bounded, independently checked local correction/authorization protocol under the tested fault model**. It adds one concrete Measure/Memory/Recovery connection: protected local evidence plus checking can authorize replayed output. It adds no adaptive Explorer, semantic Map, complete provenance graph or general five-component architecture. It establishes neither general recursive self-improvement nor semantic correctness, global fault tolerance, common-mode protection or general safety. No larger redesign follows automatically from this result.

## Subsequent follow-up

The [separate follow-up](FOLLOWUP.md) addresses component cost, lossless trace packing, minimal provenance and broader fault patterns. It preserves the predeclared result above. The current integration adds four test-only selector bits; its updated cost is reported there.
