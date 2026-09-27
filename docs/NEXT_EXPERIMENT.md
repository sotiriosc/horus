# Proposed minimal experiment: bounded independent commit checking

> **Historical status:** this document is the proposal written against the
> verified baseline. The experiment was implemented later as a distinct
> milestone. See `experiments/bounded_commit/` and
> `research/bounded-independent-authorization-results.md`. The proposal text is
> retained so the implementation is not read retrospectively into the baseline.

**Not implemented or run.** Test whether two bounded local checks plus preserved source evidence can complete a small corrective transaction. This tests a necessary local mechanism, not general recursive self-improvement or absence of every global dependency.

Use one existing `horus_block_skpr_repair` instance and a two-entry downstream quarantine buffer. Keep its internal `commit_valid` meaning unchanged: it proposes an output. Add a separate acceptance signal at the downstream boundary; internal commit is not external authorization.

A deterministic source supplies eight NFE words, a monotonically increasing transaction ID, an epoch, and a protected source record. The record travels through a separate bounded channel and is captured before fault injection. It is input evidence, not a copy of the repaired result. A separate checker computes the expected clean normalized block directly from that record using a small integer specification, without calling the repair implementation or accepting its own reported “valid” bit as evidence.

There are two local policies: (1) identity/epoch matching; (2) numerical comparison with the independently computed clean target. For this deliberately narrow test, use a constant-scale clean block. Inject one controlled exponent spike into one lane after the source record is captured. Use KEEP mode, threshold 13, and clean words with sign 0, stored exponent 10 and mantissa 16; raise lane 3 to exponent 40. The expected normalized clean words have exponent 32 and the same sign/mantissa. Assert input validity only when the wrapper is not busy. The existing block detector localizes the lane; the quarantine boundary restricts downstream continuation; repair/replay proposes a correction; both independent checks must pass before downstream acceptance. Record the mismatch lane, transaction ID, epoch and verdict in a fixed-size local trace.

Required paired controls, under the same seed and input schedule:

1. Clean transactions: accepted once, with the expected values.
2. Corrupted input, working correction: no corrupt output accepted; corrected transaction accepted exactly once after both checks.
3. Corrupted correction: deliberately alter the repaired output after replay. The independent checker must reject it; no downstream acceptance is permitted.
4. Provenance mismatch: swap the two source-record IDs or use an old epoch. Numerical equality alone must not authorize acceptance.
5. Shared-descendant control: intentionally give the checker a reference derived from the corrupted/corrected output. Demonstrate why this can hide corruption; it is not the protected-source configuration.

Run a predeclared fixed schedule (for example 100 clean and 100 injected transactions for seeds 1, 2, 3), with bounded input stalls. A transaction may retry at most once; no match or no checker result within a fixed cycle limit ends in rejection. A full quarantine buffer backpressures input rather than dropping an identity association.

Measure false accepts, correct accepts, false rejects, duplicate accepts, transaction/epoch mismatches, and cycles until acceptance/rejection. The hypothesis fails for this scope if any corrupted or misidentified value reaches the sink, any unverified repair is accepted, or state grows beyond the declared bound. Zero false accepts with successful recovery in the positive control supports only this restricted local protocol.

The new pieces are the quarantine/acceptance boundary, protected identity record and independent checker. The protected source and checker are explicit trust assumptions; common-mode faults there are not solved. No world map, adaptive explorer, durable lineage system, general checkpoint store or general safety result is claimed.
