# Research roadmap: minimal grounded correction loop

The next major objective is functional validation of a minimal closed
Explorer / Map / Measure / Memory / Recovery framework. Hardware area
optimization is deferred until the contracts, architecture, and behavior are
tested. The bounded independent-authorization experiment is a local primitive
available at the Measure/Recovery boundary; it is not the complete framework.

## Stage 1 — Define minimal contracts

For every component, freeze these fields before implementation:

| Component | Input | State | Output | Evidence | Validation policy | Failure condition | Continuation authority |
|---|---|---|---|---|---|---|---|
| Explorer | Finite action set, current Map view | Bounded action cursor or policy state | One proposed action and identity | Proposal identity and decision inputs | Action is in the allowed set and refers to the current epoch | Invalid, stale, or unbounded proposal | Measure/Recovery gate, never the proposal alone |
| Map | Grounded observation and prior committed state | Small revisable state representation | Candidate state revision | Observation identity and prior-state identity | Revision agrees with the admitted observation and map invariants | Unsupported rewrite, stale observation, or inconsistent transition | Independent state-commit gate |
| Measure | Proposed/realized consequence and external target | Bounded comparison state | Verdict plus localized discrepancy | Target identity, observation, and comparison record | Compare realized consequence against externally grounded target | Missing target, circular reference, or incorrect verdict | Measure verdict contributes to the gate but cannot rewrite evidence |
| Memory | Authorized outcome, provenance tuple, prior record | Bounded committed record set | Addressable consequence history | Outcome plus origin, epoch, and authorization result | Store only independently authorized records | Corrupt record, identity mismatch, or unbounded growth | Memory controller accepts only gated commits |
| Recovery | Localized failure, protected evidence, bounded candidates | Retry/quarantine state | Repair proposal or explicit rejection | Protected source record and recovery trace | Independent identity and numerical/contract check | Invalid repair, exhausted retry, timeout, or circular evidence | Separate authorization signal controls continuation |

These are starting contracts. Their precise widths, state transitions, trust
assumptions, and falsification thresholds must be predeclared for the chosen
environment.

## Stage 2 — Build the smallest closed loop

Use a tiny deterministic environment rather than a general intelligent agent.
The Explorer selects from a finite action set. The Map holds a small revisable
state. Measure compares realized consequence with an externally grounded
target. Memory stores authorized outcome and provenance in bounded storage.
Recovery handles one deliberately introduced inconsistency through protected
evidence and independent authorization.

The environment must make ground truth inspectable without allowing a
component to silently redefine it. Queue depths, record counts, retries,
timeouts, action count, and trace size are fixed before execution.

## Stage 3 — Inject controlled failures

At minimum, test:

- wrong Map state;
- corrupted Memory;
- incorrect Measure result;
- invalid Explorer proposal;
- failed Recovery proposal;
- stale or incorrect provenance; and
- correlated evidence descended from the value being validated.

Each fault needs a paired clean control and an explicit statement of whether
the expected safe outcome is recovery or rejection.

## Stage 4 — Test the complete bounded sequence

The experiment must observe whether the system can:

```text
ACT
→ OBSERVE CONSEQUENCE
→ PRESERVE EVIDENCE
→ DETECT INCONSISTENCY
→ LOCALIZE IT
→ RESTRICT CONTINUATION
→ CORRECT OR RECOVER
→ INDEPENDENTLY VERIFY
→ UPDATE STATE
→ CONTINUE
```

Every arrow needs an identity-preserving bounded interface. A proposal or
internal valid signal is not continuation authority.

## Stage 5 — Freeze falsification criteria

The framework experiment fails if any predeclared condition occurs, including:

- corrupt state reaches committed history;
- an invalid repair is authorized;
- stale provenance is accepted;
- an explicitly recoverable fault cannot be recovered within its bound;
- validation becomes circular or uses descendant evidence as truth;
- state, retries, queues, or trace grow beyond declared bounds; or
- a component silently rewrites the external target or its own protected
  ground truth.

Preserve negative results and metric defects. Safe rejection is not recovery,
and detection is not authorization.

## Stage 6 — Optimize only after functional validation

After the minimal loop survives its predeclared controls and falsification
tests, investigate smaller protected records, hashes or fingerprints, reduced
quarantine depth, off-core traces, memory compression, latency, area, power,
and scaling. Any optimization must re-run the independence and descendant-
evidence controls. It must not remove the protected evidence or merge proposal
and authorization merely to reduce measured area.

This roadmap proposes a bounded research experiment. It does not claim a
complete Explorer, world model, general recursive self-improvement, general
safety, or universal fault tolerance.
