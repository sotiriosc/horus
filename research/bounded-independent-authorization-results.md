# Bounded independent authorization: public results

This document records the implemented experiment that followed the historical
proposal in `docs/NEXT_EXPERIMENT.md`. It describes a bounded local protocol
under a narrow fault model. It does not establish a complete five-component
framework, general safety, or universal fault tolerance.

## Initial protected-source campaign

The campaign ran seeds 1, 2, and 3 across seven fixed schedules, with 200
transactions per schedule: 4,200 protected-path transactions total.

| Metric | Result |
|---|---:|
| Correct accepts | 2,700 |
| Expected checker rejections | 1,500 |
| False accepts | 0 |
| False rejects | 0 |
| Duplicate accepts | 0 |
| Transaction-ID mismatches rejected | 300 |
| Epoch mismatches rejected | 300 |
| Source-record mismatches rejected | 300 |
| Minimum / maximum cycles to decision | 5 / 36 |
| Maximum quarantine occupancy | 2 |
| Maximum outstanding protected records | 2 |

Clean transactions and the declared recoverable exponent-spike case were
accepted exactly once. The positive repair case raised lane 3's exponent after
protected capture; the existing KEEP repair restored the declared result, and
the independent checker authorized it from the original protected record.
Corrupted repair, mismatched identity, stale epoch, and wrong source-record
identity were rejected.

The checker uses a deliberately small integer specification over protected
pre-fault words and fixed configuration. It does not call repair logic,
normalizer helpers, DUT-derived expected values, repaired-output truth, or the
repair path's validity bits as evidence.

## Negative descendant-reference control

A deliberately wrong shadow architecture derived its reference from the
corrupted candidate itself. It falsely accepted all 300 corrupted proposals
presented to that control. Its output is disconnected from the protected sink.

This result supports the narrow invariant that evidence causally descended from
a candidate cannot independently certify that candidate. The failure belongs to
the negative control, not to the protected-source path.

## Broader-fault follow-up

The follow-up ran nine fault patterns, 100 transactions per pattern, and three
seeds: 2,700 additional transactions.

| Pattern | Accepted | Rejected | False accepts | Interpretation |
|---|---:|---:|---:|---|
| Declared exponent spike | 300 | 0 | 0 | Recovered and independently authorized |
| Sign flip | 0 | 300 | 0 | Safely rejected |
| Mantissa flip | 0 | 300 | 0 | Safely rejected |
| Two equal exponent maxima | 0 | 300 | 0 | Safely rejected |
| Downward exponent fault | 0 | 300 | 0 | Safely rejected |
| Block-wide exponent shift | 0 | 300 | 0 | Safely rejected |
| Two near-equal large exponents | 0 | 300 | 0 | Safely rejected |
| Exponent spike plus mantissa fault | 0 | 300 | 0 | Replay occurred; checker rejected |
| Post-replay sign corruption | 0 | 300 | 0 | Replay occurred; checker rejected |

The follow-up demonstrates broader rejection coverage, not broader recovery. In
several patterns the earlier magnitude detector did not flag, while the
independent protected-source comparison still prevented downstream acceptance.

## Trace follow-up

The initial gate retained eight 96-bit trace records. Thirty-three high bits
were reserved zeros, so a 63-bit representation preserves all required fields.
The two variants produced identical decisions, metrics, and retained ring
records across 21 paired schedules.

| Trace configuration | Mapped area | Flip-flops |
|---|---:|---:|
| 96-bit × 8 | 58,937.7760 µm² | 1,517 |
| 63-bit × 8 | 50,065.5168 µm² | 1,253 |
| Ring disabled, decision output retained | 29,928.7040 µm² | 746 |

Lossless packing saved 8,872.2592 µm² in this synthesis probe. The trace is
observational and is not consumed by the authorization decision. No static
timing analysis was performed, so absence of physical timing/fanout cost is not
claimed. Further trace or hardware optimization is deferred until functional
architecture validation.

## Resource probes

All values below are standalone mapped Sky130 HD TT/025C/1v80 synthesis probes.
They are useful cost indicators but are not an exact additive partition of the
jointly optimized gate.

| Probe | Mapped area | Stored bits / mapped flops |
|---|---:|---:|
| Protected-record storage/access | 12,475.7152 µm² | 316 |
| Quarantine storage/access | 12,318.0640 µm² | 312 |
| Independent numerical checker | 3,439.5488 µm² | 0 |
| ID/epoch/record-ID comparisons | 441.6736 µm² | 0 |
| Complete gate without trace ring | 29,928.7040 µm² | 746 |

The component probes sum to 28,675.0016 µm². The remaining difference must not
be labeled exact control-logic area because synthesis sharing and mux
optimization change when modules are measured together. Storage and its access
logic dominate the observed overhead. That cost is accepted at this research
stage.

## Narrow provenance assumptions

The implemented provenance tuple is:

```text
(transaction_id, epoch, source_record_id)
```

It is sufficient for this protocol only under these assumptions: one trusted
source; immutable protected records; fixed captured configuration; in-order
bounded reservation; no transaction-ID reuse within an epoch; and a fresh epoch
after reset. A matching tuple is not cryptographic authentication.

`source_record_id` may be redundant if `(epoch, transaction_id)` uniquely and
immutably identifies one protected record. It was retained to make record-
channel misbinding explicit and testable. Multiple sources, wrapping epochs,
mutable records, or hostile replay require a new protocol specification.

## Reproduction

```bash
make test
make independent-commit
make independent-commit-followup
```

Optional synthesis:

```bash
python3 experiments/bounded_commit/synthesize.py --liberty "$SKY130_HD_LIB"
python3 experiments/bounded_commit/synthesize.py --followup --liberty "$SKY130_HD_LIB"
```

The compact `results.json` and `followup-results.json` files retain the measured
summaries and source hashes. Raw logs and netlists are regenerated outside the
source tree.

## Limitations

- The protected source, checker, allocator, and gate-control path are trusted;
  common-mode faults in them are outside the tested model.
- The numerical checker covers the declared constant-scale domain, not
  arbitrary Horus computations or semantic correctness.
- Unsupported fault classes were rejected rather than repaired.
- The protocol gates the downstream sink. It does not roll back every internal
  side effect: the unchanged repair wrapper may update keeper state when it
  raises its internal commit proposal.
- The result is bounded simulation plus mapped synthesis evidence, not formal
  verification, timing closure, power characterization, or physical fault
  protection.
- Zero observed false accepts is scoped to the executed campaigns. It is not a
  proof of general safety or universal fault tolerance.

The narrowest supported conclusion is that the tested protected-source design
implements a bounded, independently checked local correction/authorization
protocol under its declared fault and trust model.
