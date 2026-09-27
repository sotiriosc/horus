# Follow-up: cost, trace, provenance and broader faults

This follow-up was requested after the predeclared experiment passed. It does not retune that experiment's thresholds or replace its checker. The original 4,200-transaction campaign was rerun successfully after the extension. The independent checker source is byte-identical to the initial implementation; its expected result still depends only on protected pre-fault evidence and fixed configuration. Private predecessor mechanisms were not substituted.

## 1. What makes up the roughly 29,929 µm² gate without its trace ring?

Separate synthesis probes use the same two-entry storage depth, reset, indexed write and selected read structure as the real gate. All use the same Sky130 corner and mapped-flop flow.

| Component probe | Area (µm²) | Stored bits / mapped flip-flops |
|---|---:|---:|
| Protected source bank (including tuple and configuration) | 12,475.7152 | 316 |
| Quarantine bank (including candidate tuple and diagnostic fields) | 12,318.0640 | 312 |
| Independent source-domain/numerical checker | 3,439.5488 | 0 |
| ID, epoch and record-ID comparators | 441.6736 | 0 |
| Complete gate without trace ring | 29,928.7040 | 746 |

**These probes are standalone estimates, not an exact additive partition of an optimized netlist.** They sum to 28,675.0016 µm²; the 1,253.7024 µm² difference is not a clean measurement of control logic because joint optimization changes sharing and muxing. Do not present the rows as an exact silicon-area pie chart. They do establish that storage and its access/reset logic dominate; numerical checking is smaller, and tuple comparison itself is small.

Tuple storage is already included in the bank rows (160 total bits across protected and candidate banks), rather than charged again to the comparator row. The remaining gate also stores ages, valid/arrival state, FIFO controls, halt, and a decision record. Protected capture and quarantine are separate on purpose; removing one by deriving truth from the other would invalidate independence.

## 2. Can tracing be cheaper or moved away from authorization?

Yes, **lossless packing is implemented and tested** as `TRACE_BITS=63`, retaining all required fields. The original 96-bit record has 33 reserved zero bits. Packing only the ring saves 8 × 33 = 264 flip-flops; the externally visible decision record remains 96 bits with zero extension.

| Standalone gate | Area (µm²) | Flip-flops |
|---|---:|---:|
| Original 96-bit × 8 trace | 58,937.7760 | 1,517 |
| Packed 63-bit × 8 trace | 50,065.5168 | 1,253 |
| Ring disabled, decision output retained (cost control) | 29,928.7040 | 746 |

Packing saves **8,872.2592 µm²**, about 15.1% of the original gate area. The packed and original variants produced bit-identical decision streams, metrics AND retained eight-entry ring contents on 21 paired schedules (all seeds/controls). Default remains the original 96-bit variant so the measured predeclared configuration is explicit. The packed option is a separate tested variant, not a hidden rewrite of old cost figures.

The trace write is observational: acceptance/rejection does not wait for a trace consumer or read stored trace data. This removes a logical control dependency, but **does not establish absence of physical timing/fanout cost**; no STA was run. Sampling could reduce writes or exported bandwidth, but would not meet the requested per-transaction local record contract if the sole required record were sampled away. Keep the bounded local minimum; sample richer optional diagnostics only. The decision port can feed an off-core logger through a separately bounded, non-blocking observation path, but that extension and its explicit drop accounting are proposed, not implemented. Disabling the ring was a cost probe, not the default tested logging policy.

## 3. Minimum provenance tuple

`(transaction_id, epoch, source_record_id)` is sufficient **within this protocol's assumptions**: one trusted source, immutable protected record, fixed captured configuration, in-order reservation, no identifier wrap/reuse within an epoch, and fresh epoch on reset. It binds candidate labels to the reserved pre-fault source record; it does not authenticate an untrusted source or prove complete causal lineage.

The fields are 16, 8 and 16 bits respectively. If the trusted source guarantees `(epoch, transaction_id)` uniquely identifies exactly one immutable record, `source_record_id` is logically redundant and could be derived. Retaining it makes channel/record misbinding explicit and testable; 300 wrong-record-ID cases were rejected despite matching numbers. No larger tuple, lineage graph or hash was necessary here. A changing configuration would require binding its value/version; target, threshold and mode are already captured and checked. Multiple sources, wrapping epochs, mutable records or hostile replay would change these assumptions and need a new protocol specification.

## 4. Broader faults: protection versus recovery

New deterministic follow-up: nine patterns × 100 transactions × seeds 1, 2, 3 = **2,700**. The numerical source domain remains the predeclared constant-scale block. These tests broaden fault patterns, not workloads or supported arithmetic.

| Follow-up pattern | Transactions | Correctly accepted | Safely rejected | Detector flagged | False accepts |
|---|---:|---:|---:|---:|---:|
| Original exponent spike | 300 | 300 | 0 | 300 | 0 |
| Lane 3 sign flip | 300 | 0 | 300 | 0 | 0 |
| Lane 3 mantissa flip | 300 | 0 | 300 | 0 | 0 |
| Two equal exponent maxima | 300 | 0 | 300 | 0 | 0 |
| Lane 3 exponent lowered to zero | 300 | 0 | 300 | 0 | 0 |
| All eight exponents shifted to 40 | 300 | 0 | 300 | 0 | 0 |
| Two near-equal large exponents | 300 | 0 | 300 | 0 | 0 |
| Exponent spike plus mantissa error | 300 | 0 | 300 | 300 | 0 |
| Sign corruption after replay | 300 | 0 | 300 | 300 | 0 |


The unchanged KEEP repair recovers the original single exponent spike. All eight other tested fault patterns are safely rejected; none demonstrates broader repair. In six patterns the old magnitude detector raises no flag, yet the independent checker prevents acceptance. In the whole-block scale shift, normalized words happen to match but block-scale metadata is wrong: checking that metadata rejects the transaction. In spike-plus-mantissa and post-replay-sign faults, replay occurs but does not establish correctness, and the checker rejects.

No corrupted or misidentified value reached the protected sink in these tests. This does not cover faults in the protected source, checker, allocator, gate control or common-mode paths; nor asynchronous/metastability faults, arbitrary queue-state corruption, general semantic correctness or unrestricted numerical inputs. There is no general fault-tolerance or safety claim.

## Follow-up implementation and resources

`bounded_commit_top.v` adds a four-bit test-only fault-pattern selector and one four-bit held selector; `commit_gate.v` adds the trace-width parameter. `tb_broader.v` exercises the broader fault patterns. `cost_components.v` contains synthesis-only probes. `followup.py` executes actual simulations and exact trace-variant comparison; `synthesize.py --followup` measures the probes/packed gate/final integration. The checker is unchanged.

Default additional declared sequential state is now **1,677 bits** (initial 1,673 + four diagnostic selector bits); packed-trace variant is **1,413 bits**. Final integrated default with fault controls maps to **88,036.9344 µm², 7,982 cells, 2,284 flip-flops**, including the unchanged DUT and experiment injection logic. The earlier 88,376.0096 µm² / 2,280-flop result belongs to the frozen pre-follow-up integration. Mapping optimization changed cell area despite the four added flops; this is not evidence that broader checking is intrinsically cheaper. The 29,928.7040 µm² standalone no-ring gate remains the useful primitive estimate. Timing and power remain unmeasured.

```sh
make independent-commit-followup
PYTHONDONTWRITEBYTECODE=1 python3 experiments/bounded_commit/synthesize.py --followup --liberty "$SKY130_HD_LIB"
```

`followup-results.json` records per-seed observations, source hashes and synthesis figures. All tooling stores raw logs/netlists outside the source tree. This follow-up supports stronger rejection coverage within a narrow trusted protocol, not an expanded self-correction architecture.

Internal side-effect boundary: the unchanged repair wrapper still updates its keeper at its internal proposal commit. External rejection does not roll back that state. In this tested datapath the keeper does not feed the independent checker or choose the normalizer/repair result, so it cannot supply the evidence authorizing the sink. The result concerns downstream acceptance, not atomic rollback of all DUT state. A future design with feedback from speculative state would need a separate state-commit policy and new tests.
