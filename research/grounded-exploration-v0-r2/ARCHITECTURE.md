# Horus v0.7 R2 protected-runtime scheduling

R2 preserves the v0.7 scientific question and policy while correcting the
higher-level runtime schedule that exhausted the protected framework in R1.
The protected `EPISODE_LIMIT` remains 12 and is neither increased nor bypassed.

## Prospective schedule

The unchanged 54-decision A→B→A schedule is divided before inference into six
fresh protected runtimes:

| Registered segment | Decisions | Regime | Maximum attempts and executions |
|---|---:|---|---:|
| `R2_A1_1` | 1–9 | A | 9 |
| `R2_A1_2` | 10–18 | A | 9 |
| `R2_B1` | 19–27 | B | 9 |
| `R2_B2` | 28–36 | B | 9 |
| `R2_A2_1` | 37–45 | A | 9 |
| `R2_A2_2` | 46–54 | A | 9 |

Rollover depends only on those registered decision ranges. Outcomes, model
accuracy, probe/exploit mode, router state, abstentions, and discovered regime
information cannot move a boundary. Every rollover uses the existing durable
restart path: a fresh source identity and epoch are created while authenticated
prior Memory is imported read-only and routing and confidence state replay from
their authenticated journals. Historical receipt objects are not reconstructed.

## Protected rejection boundary

`begin_step` legitimately returns either an accepted `PendingTransaction` or a
rejected `StepResult`. R2 checks that sum type before reading the accepted
transaction's pre-execution prediction. A rejection produces no execution,
receipt, Memory publication, or routing evidence. The already-frozen Explorer
decision is completed as `FRAMEWORK_REJECTED` so the fixed attempt schedule and
authenticated decision journal remain exact.

A rejected begin also emits an `INTERNAL_ROUTE_PROBLEM`. This record describes
the component, requested operation, observed protected constraint, rejection,
and possible need for a new runtime route. It has no authority to create that
route, alter the schedule, execute, publish Memory, update routing, or train a
model. The registered six-runtime schedule is the sole authority for R2
rollover.

Problem types remain distinct:

- `EXTERNAL_SERVICE_PROBLEM`: an external dependency is unavailable or fails.
- `INTERNAL_ROUTE_PROBLEM`: a protected internal boundary refuses a requested
  operation.
- `UNRESOLVED_RELATION_PROBLEM`: grounded evidence leaves a relation unresolved.

R2 does not add a general repair planner.

## Architectural invariant

The higher-level component submits its request to the protected boundary. The
boundary accepts or rejects it. A rejection may describe the unmet need, and an
already-authorized route may later satisfy that need. The rejection never
weakens or bypasses the protected boundary.
