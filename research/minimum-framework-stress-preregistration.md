# Minimum-framework stress preregistration

Frozen after static code/contract inspection, before implementing or executing
the new campaign. Runtime baseline is public checkpoint
`b8e4245ef14b11ee5d94ce851aec4d8dc059963f`; the completion definition was
committed separately first. Static inspection motivated the edge cases below;
they are not claimed to be blind discoveries.

## Scope and intervention rules

Keep all v0/v1/v2 runtime files byte-for-byte unchanged. Test harnesses may call
existing APIs, inject faults into existing mutable state/proposal/evidence
fields, and make isolated, explicitly labeled weakened test variants. No new
source, witness, authorizer, world state, policy, hardware, or v3 implementation.

Use identity seeds 1, 2, 3. These are deterministic identity repetitions. Each
case starts a fresh system, with at most 12 transitions per epoch and two
distinct positive epochs, eight Memory/pair/package entries, three package
items per round, two rounds, one retry, and existing trace/quarantine bounds.
External test logs are bounded to 24 transaction records per case. Copying a
system for an ablation does not enlarge an individual system's runtime bounds.

Protected acceptance-safety tests may combine the existing faults without
claiming every combination is recoverable. A safe reject or explicit exception
before false commit is allowed where listed. Post-commit exceptions do not erase
a bad mutation. Recovery-attempt counts are interpreted per existing Recovery
object; any difference from the preregistration's transaction-level wording
must be reported as a contract ambiguity, not silently generalized.

Source numeric corruption may change next-state/consequence integers. It does
not change the four-state/ternary world. The authorizer must not commit a
non-world consequence merely because an unchecked encoding aliases the correct
witness code. This is an acceptance-safety stress of the existing A+B fault
boundary with normal C, registry, authorizers, coordinator, and oracle.

The public v2 facade is audited for callable routes that skip its mandatory
package gate. Calling an exposed delegated v1 ingress without rewriting any
trusted code is an API-boundary probe. Results must distinguish this from the
normal `submit_package` driver and from malicious trusted-code replacement.

## Protected cases and predeclared expectations

| ID/name | Injection or sequence | Required result |
|---|---|---|
| clean_loop | 12 normal v2 transitions | correct commits; aligned bounded rings |
| memory_causal_v0/v1/v2 | same pre-state, identity, policy; history versus all paired history removed | HOLD with history; ADVANCE without; no oracle/policy mutation |
| map_memory | existing Map and one Memory consequence corrupted | recover correctly or stop; no false commit |
| measure_stale | wrong Measure plus first-round stale C | one retry, fresh package, Measure correction, correct commit |
| explorer_stale_map | invalid action plus stale Map | reject before world execution |
| recovery_wrong_epoch | wrong Recovery candidate plus persistently wrong epoch | no commit/continuation |
| memory_eviction | corrupt oldest Memory record at eight entries, then commit | recover; atomic paired eviction; eight entries |
| epoch_disagreement | new distinct epoch; first-round A disagreement | one retry, correct commit |
| valid_incumbent | state 1 HOLD plus bad candidate | valid incumbent retained |
| invalid_incumbent | state 0 ADVANCE plus bad candidate | independently valid recovery or safe stop; invalid incumbent not retained |
| delayed_partial | stage A, then A+B, delay by inspecting unchanged state; try another begin | no provisional commit; one pending transaction; eventual full package works |
| final_retry_success | first-round bad C, second-round good C | exactly one retry and correct commit |
| final_retry_reject | bad C both rounds, then attempt third submission | reject; no third authorization |
| quarantine_capacity | occupy one Map quarantine slot before another recovery | stop without exceeding one slot or false commit |
| repeated_rejection | persistent disagreement in each of two epochs | both stop; third epoch prohibited |
| alternating_evidence | six transactions alternate transient bad/clean first rounds | only full corrected packages commit |
| fault_after_recovery | Map recovery followed immediately by C transient | both independently checked and correctly committed |
| fault_before_behavior | corrupt the state-1 negative outcome just before its later use | detect/rebuild before Explorer; HOLD remains |
| combined_faults | Map, one Memory record, Measure, and transient A | correct commit or stop; no contaminated history |
| legacy_ingress | call the public v2 facade's delegated A/B receipt method without C | mandatory package invariant: no commit before C |
| alias_s{0..3}_{ADVANCE,HOLD,RETREAT} | A+B agree on another in-range state and an out-of-range consequence with the same arithmetic code as correct C | reject; never commit false state/history (12 finite-world cases) |
| stale_package | replay a complete earlier authorized package into a later transaction | reject persistently |
| old_prediction | stale prior Prediction installed before executing the next action | never score it as confirmation; valid consequence may recover state |
| old_consequence | old A plus current B/C after Map version advances | reject bad round; fresh retry may commit |
| epoch_stale | old full package with repeated transaction number but different epoch | reject bad round; fresh retry may commit |
| evicted_reinsert | replace one current Memory slot with evicted authorized record | stop or repair before Explorer; no stale influence |
| duplicate_delivery | resubmit package after its transaction committed | no duplicate authorization/history |
| delayed_old_b | deliver earlier B after two transactions progress | reject bad round; fresh retry may commit |
| descending_epoch_repair | two distinct positive epochs in decreasing numeric order; one Memory corruption | single-record recovery keeps Memory/pair/package correspondence; no unpaired rotation |

No software observation timeout exists in v1/v2. `delayed_partial` tests bounded
waiting and absence of provisional commit, not an invented cycle deadline. The
separate RTL authorization gate's existing timeout regressions remain applicable
only to that RTL. Exhausted retries and full quarantine test actual existing
bounds. Identity wrap is outside scope; cross-epoch transaction-number reuse and
duplicate delivery are tested without changing the trusted allocator.

## Isolated paired ablations

Each A-G experiment gets a complete-framework control on identical input and a
separate weakened instance. Temporary monkeypatches are test-only and scoped to
that instance. They must not alter files or survive into another case.

| Ablation | Weakened relationship | Observable failure or residual defense |
|---|---|---|
| A provenance | ignore stale transaction/epoch coordinates at package and inherited pair gates | stale evidence can cross into a later authorization |
| B self_authorization | state proposer accepted without state-authorizer comparison | incorrect recovery may change Map |
| C memory_audit | return corrupt Memory as audited | corrupt consequence may change the next action |
| D descendant | ignore declared path overlap | candidate-derived agreeing witness may validate wrong A+B |
| E incumbent | always propose incumbent as selected state, retaining downstream state check | downstream gate may still reject; do not remove extra gates to force failure |
| F quarantine | skip Map quarantine while retaining recheck | downstream gate may still reject invalid recovery |
| G early_continuation | admit A+B directly to inherited commit path despite invalid/missing C | commit/continuation may precede package grant |

At least one paired ablation must expose a forbidden effect absent in its normal
control to support a causal architecture claim. Not every ablation must fail;
surviving downstream defenses are useful results, not reasons to weaken more.

## Boundary and out-of-model controls

- `prediction_replacement`: the trusted driver replaces `pending.prediction`
  after outcome revelation, with a forged matching Prediction. Record whether
  the frozen Prediction object blocks field edits and whether its containing
  reference is still replaceable. This is a core *boundary weakness* if no latch
  validation exists, but trusted-coordinator replacement alone is not a protected
  source-fault counterexample. No normal candidate API receives this reference.
- `abc_common`: repeat the existing identical A+B+C trust-root attack.
- `registry_corrupt`: repeat the existing false-registry trust-root attack.

No physical, malicious-oracle, arbitrary hidden-cause, or wrap tests are silently
classified as covered. The normal registry and C stay unchanged in alias tests.

## Independent observation and scoring

The harness must record a Prediction snapshot before world execution, then
execute the unchanged test oracle, construct existing A/B/C evidence from the
world-side pre-state/action, and call the unchanged runtime. After each call,
compare every retained outcome with the oracle event for its exact epoch/ID,
compare Map with truth after commit, verify paired ring correspondence, inspect
authorization counts, and retain the actual evidence coordinates used.
Recompute graph overlap in the harness rather than trusting the runtime method.
Do not count an internal false-accept counter as an external audit.

Report commits, rejections, exceptions before/after mutation, oracle false
accepts, provenance crossover, premature commit/continuation, Memory influence,
ring/bound violations, prediction confirmation, recoveries, and ablation effects.
An unexpected harness error is INCONCLUSIVE for that case, not a safe rejection.
The full campaign continues through independent cases after a failure, but the
global verdict remains failed if any covered criterion fails.

## Frozen falsification criteria and output

F1 protected false accept; F2 unauthorized history; F3 duplicate authorization;
F4 invalid recovery authorized; F5 provenance crossover; F6 premature
continuation; F7 silent corrupt Memory affecting Explorer; F8 bounded-state or
paired-rotation failure; F9 post-outcome manufactured prediction agreement in a
covered path; F10 no causal Memory influence; F11 invalid incumbent retained;
F12 declared recoverable case not recovered.

Protected observations determine recommendation A/B/C under the previously
frozen completion definition. Ablations and trust-root controls have their own
columns and cannot improve or dilute protected error counts. Full logs remain
outside the source tree; only compact public-safe observations and source hashes
are retained in the repository. Never repair runtime code during this audit.
