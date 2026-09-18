# Frozen minimum-framework completion definition

Baseline: `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`, containing frozen v0,
v1, and v2. This definition is frozen before the new code/outcome audit and
before designing or running its stress campaign. Prior published observations
are known; this is not a claim of blindness to them.

## Essential functions

The minimum framework is complete for its declared bounded scope if the
following fourteen functions exist together and their covered invariants
survive the preregistered audit/stress campaign:

1. Explorer proposes bounded actions.
2. Map maintains revisable state/prediction distinct from ground truth.
3. Measure compares a prediction/expected relation with realized consequence.
4. Memory preserves authorized consequence and provenance and changes later
   behavior.
5. Recovery proposes a bounded correction after verified failure.
6. An external consequence route exists that is not created by the candidate
   being judged.
7. Proposal and authorization are separate; proposers cannot certify themselves.
8. Evidence binds the correct transaction, state, epoch, and source relation.
9. Verified failure can withdraw continuation authority.
10. Recovery cannot continue before the required independent recheck passes.
11. A valid incumbent may survive; invalidity cannot be excused by incumbency.
12. Memory, retries, candidates, quarantine, and traces remain bounded.
13. Return with difference: verified prior consequence changes a later decision
    or state, and removing that history restores the original decision.
14. Insufficient evidence may stop without fabricated certainty.

Completion is functional and scoped, not philosophical. Source counts,
architectural novelty, deployment maturity, and elimination of every external
assumption are not completion criteria.

## Permitted roots of trust and stopping principle

A root of trust is permitted if it is named, bounded, outside candidate control
under the stated model, experimentally attackable, and not represented as
solved. Verification may terminate at a declared evidence boundary when the
candidate cannot write that boundary, assumptions are explicit, failures beyond
them are acknowledged, and the experiment can independently measure violations.
This does not require a verifier for every verifier.

Distinguish normal supported APIs, modeled corruption of proposal/state objects,
and deliberate replacement of trusted runtime/harness code. Python object access
alone does not establish candidate authority; an actual supported data flow or
modeled state corruption must demonstrate it. Likewise, a trusted-coordinator
failure must not be relabeled as a protected candidate failure. Internal
contract assertions, which halt execution before a false commit, are stopping
outcomes, not successful recovery.

## Evidence and classification

Use implemented code, frozen contracts, fresh tests, retained negative controls,
and explicit assumptions. A matrix row must have one of these statuses:
IMPLEMENTED + TESTED; IMPLEMENTED BUT WEAKLY TESTED; ASSUMED / TRUST ROOT;
MISSING CORE CAPABILITY; OPTIONAL EXTENSION; EFFICIENCY / SCALING ONLY.

Stress expectations and coverage classifications must be preregistered before
execution. A covered protected false accept, unauthorized/duplicate commit,
invalid recovery authorization, provenance crossover, premature continuation,
silent corrupt-Memory influence, exceeded bound, post-outcome prediction rewrite
that manufactures agreement, loss of causal Memory influence, invalid incumbent
retention, or failure of a declared recoverable case is a core failure.

Combination tests are not automatically guaranteed recovery. If the frozen
contracts promise recovery only for a single fault, a combination must still
avoid false authorization within the declared evidence boundary, but may stop.
Unmodeled concurrency, identity wrap, hostile trusted-code replacement, total
trust-root corruption, and malicious oracle behavior are reported separately.

The absent features listed below are not automatic core failures: general causal
discovery, open-ended learning, LLMs, larger worlds, silicon/FPGA deployment,
physical fault testing, lower area, or protection against undeclared common
causes. No new runtime mechanism will be implemented during this audit.

## Decision rule

- **A — MINIMUM FRAMEWORK COMPLETE FOR DECLARED SCOPE:** all essential functions
  exist and covered stress criteria pass. Do not add architecture.
- **B — CORE CORRECTION REQUIRED:** an existing essential contract has a
  reproducible covered failure. Describe the smallest correction; do not implement it.
- **C — INCONCLUSIVE:** a required invariant remains unestablished without a
  demonstrated failure. Recommend the smallest resolving experiment.

B takes precedence over C or A if a covered invariant fails. Complete remaining
independent audit cases after finding a failure to characterize its limits;
never repair the runtime or weaken the frozen criterion during this task.
