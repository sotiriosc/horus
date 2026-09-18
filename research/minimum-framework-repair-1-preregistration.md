# Minimum framework repair 1 — frozen criteria

Baseline: `412de7bb02a4cedfab5d648debffe54b8b5a94bb` on
`research/minimum-framework-audit`. Its worktree was clean before branching.
Public main remains `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`.
This document precedes runtime edits on `research/minimum-framework-repair-1`.
The completion definition, audit harness/preregistration/results, and historical
v0/v1/v2 result files are frozen and will not be rewritten.

## Reproduced failures

* Numeric domain alias: **36/36 false accepts** caused by values outside the
  declared state/consequence domain aliasing the witness encoding.
* Mandatory-authorization bypass: **3/3 package-less commits** through exposed
  delegated `submit_receipt` ingress.
* Temporal pairing: **3/3 descending-epoch Memory recoveries** lose
  Memory/pair/package correspondence and expose a commit before final audit failure.

## Bounded repairs and acceptance conditions

1. Validate integer pre/next states in 0..3, the three existing actions, and
   integer consequences in -1..1 before encoding; validate C's integer code in
   0..11. Keep the encoding and independent C implementation unchanged.
   All 12 legitimate transitions must pass; all 12 aliases at seeds 1/2/3
   must reject without authorized-state mutation or continuation. Test direct
   state -1/4, consequence -2/+2, and C code boundaries.
2. Remove generic method delegation and enforce a current transaction package
   grant in the existing inner commit ingress. Direct A/B submissions without C
   fail closed. Enumerate public methods and test ordinary package ingress.
   Mutable Python diagnostic objects are not a hostile-process security boundary.
3. Recover a retained record in its original slot, using its immutable identity
   and paired evidence. Never sort identities. Validate package/pair/Memory
   correspondence before publishing bounded transaction state. Stage existing
   coordinator state; final-check failures must publish no Map, Memory, pair,
   package, or authorization-ledger changes.
4. Privately latch the original prediction at begin; replacement of the exposed
   pending reference must not change the prediction used by Measure.
5. Document the existing one-attempt-per-Recovery-instance rule and measure its
   finite per-transaction subsystem total. Do not redesign Recovery.

Temporal checks include epochs 101,101,1 with retained corruption and a following
transaction; increasing/decreasing epochs; eight-record capacity; recovery
before eviction and after rotation; old package replay; reused transaction
numbers under a new epoch; delayed evidence. Successful commits must preserve
identical chronological Memory/pair/package identities.

## Frozen campaign and adapter policy

Run the same 126 protected, 21 full-framework controls, 21 weakened variants,
and 9 boundary controls. Target: **126 protected passes, zero violations**, with
36 safe alias rejections, 3 blocked legacy ingresses, and 3 aligned descending
recoveries; all previously passing scenarios must remain passing.

Keep the original harness byte-for-byte. A repair-local adapter may catch the
now-explicit ingress rejection, inject an old prediction at the pre-outcome
producer instead of replacing the latched reference, and observe the actual
latched prediction. If staging/mandatory admission makes a weakening adapter
inoperative, explicitly remove the same invariant locally and document the
equivalence. Do not alter the oracle, completion functions, expected protected
behavior, source faults, or force an isolated ablation to fail. Report redundant
gates honestly. Prediction replacement is expected to become harmless; the six
common-mode/registry boundary runs remain out-of-model negative results.

Repeat the nine v0/v1/v2 × seed 1/2/3 Memory causal pairs: authorized history
selects HOLD; removing history selects ADVANCE. Reproduce all seven authority
ablations: provenance, self-authorization, Memory audit, descendant overlap,
incumbent selection, quarantine, and early continuation.

Run fresh `make test`, `make independent-commit`,
`make independent-commit-followup`, and `make base-framework-v0`, `-v1`, `-v2`
(the latter names expand to the full Make targets). Store fresh evidence
separately from historical evidence. Add direct final-validation fault probes
that require zero visible commit delta, including at ring rotation.

## Decision and stop rule

Evaluate the existing 14-function completion definition, unchanged: A means
complete for the bounded declared scope; B requires the smallest demonstrated
core correction; C requires the smallest resolving experiment. Errors in the
test harness cannot establish A. Publish actual counts, failures, trust roots,
ingress table, recovery budget, adapter details, and source/evidence hashes.
No new architecture, sources, witnesses, checkers, states, actions, learning,
optimization, or hardware work. No main/tag changes or push. If A, stop
architecture development. No claims of general truth/grounding, common-mode
immunity, hostile-process isolation, universal fault tolerance, or hardware
validation follow from this campaign.
