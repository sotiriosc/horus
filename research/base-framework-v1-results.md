# Base framework v1 cross-source results

**Status:** IMPLEMENTED and OBSERVED on 2026-09-18. The protected
independent-single-source-fault experiment passed all frozen criteria. The
separate common-mode control produced **COMMON-MODE FALSE ACCEPT OBSERVED** in
3/3 runs.

The design and criteria were frozen in the
[pre-registration](base-framework-v1-preregistration.md) at commit `8f157ae`
before implementation. V0 remains frozen at
`6752f0adf591bf6ceacfe4b07cee967075f49c20`.

## 1. Frozen preregistration

The preregistration fixes the unchanged world and five-component semantics,
source contracts, hidden-oracle boundary, structural independence rule, one
re-observation policy, bounds, 23 scenario classes, result classes, and
falsification criteria. None was weakened after execution.

## 2. Exact source contracts

Both sources accept only `(epoch, transaction_id, pre_state, action,
channel_sequence)` and emit the minimal immutable receipt defined in
`types.py`.

| Property | Source A | Source B |
|---|---|---|
| Implementation | Explicit 12-entry table | Conditional/arithmetic branches |
| Registered identity | `SOURCE_A` | `SOURCE_B` |
| Declared domain | `OBSERVATION_A` | `OBSERVATION_B` |
| Imports other source/oracle | No | No |
| Authorization power | None | None |

They share the receipt/request dataclasses only. Neither imports or calls the
other, and neither consumes the other's result.

## 3. Hidden oracle design

`hidden_oracle.py` uses a third flat-vector transition implementation and owns
true world state. Only `campaign.py` and tests import it. Runtime `framework.py`
and both sources do not. The driver executes the oracle, gives each source the
transaction pre-state/action rather than oracle next-state/consequence, and
uses hidden truth only after the runtime verdict to score acceptance.

## 4. Authority model

The coordinator stages the first receipt as `OBSERVED_PARTIAL` with no commit.
The complete pair reaches `OBSERVED_PAIRED` only through the cross-source gate.
Disagreement becomes `REOBSERVING` once, then `REJECTED` if unresolved.
Measure proposes a verdict; a separate auditor recomputes it. Recovery proposes
state/measurement/Memory corrections; state and record authorizers decide.
Map and Memory update atomically only after every mandatory gate. Data
production alone grants no authority.

## 5. Provenance and fault-domain model

Per-source provenance binds epoch, transaction, observation, registered port,
source identity, channel sequence, pre-state, action, lineage, and fault domain.
A pair also receives a decision identity. Authorization requires registered A
and B ports, different observation IDs, exact paired provenance, allowed
distinct domains, external lineage, and agreement on next-state/consequence.

These are declared structural relationships. Metadata does not prove physical
or causal independence.

## 6. Implementation tree

```text
experiments/base_framework_v1/
├── types.py           shared immutable receipt/request types
├── source_a.py        table-driven observation channel
├── source_b.py        conditional observation channel
├── hidden_oracle.py   campaign-only truth implementation
├── framework.py       pairing, authority, Memory, Recovery, coordinator
├── campaign.py        scenarios and independent external audit
├── test_framework.py  boundary and full-campaign tests
├── run.py             fail-closed runner
├── results.json       compact approved result
└── README.md          reproduction and scope
```

## 7. Bounds

| Resource | Frozen | Maximum observed |
|---|---:|---:|
| States / actions / source channels | 4 / 3 / 2 | 4 / 3 / 2 |
| Receipts per round / rounds | 2 / 2 | 2 / 2 |
| Re-observation attempts | 1 | 1 |
| Pending transactions | 1 | 1 |
| Memory records / pair decisions | 8 / 8 | 8 / 8 |
| Recovery attempts | 1 | 1 |
| Episode transitions / epochs | 12 / 2 | 12 / 2 |
| Runtime / driver trace | 24 / 24 | 24 / 12 |
| Authorization identities per epoch | 24 | 12 |

All bound assertions passed. Clean episodes performed four paired
Memory/evidence evictions without identity corruption.

## 8. All scenario outcomes

Each row ran for epoch seeds 1, 2, and 3.

| Scenario | Result class | Outcome |
|---|---|---|
| Clean dual-source | SAFE AUTHORIZATION | 12/12 commits per seed |
| A transient corruption | SUCCESSFUL RECOVERY | Disagree, re-observe, commit |
| B transient corruption | SUCCESSFUL RECOVERY | Symmetric |
| A persistent corruption | SAFE REJECTION | No source chosen |
| B persistent corruption | SAFE REJECTION | Symmetric |
| Stale A / stale B | SUCCESSFUL RECOVERY | Bad round rejected; fresh round committed |
| Wrong epoch A / B | SAFE REJECTION | Persistent provenance failure stopped |
| Wrong transaction A / B | SAFE REJECTION | Persistent provenance failure stopped |
| Delayed B | SAFE AUTHORIZATION | A alone made no commit; A+B committed |
| Duplicate A | SAFE REJECTION | A never occupied registered B port |
| Source-ID spoof | SAFE REJECTION | Port/identity binding rejected it |
| Derived B | SAFE REJECTION | Naive equality agreed; lineage gate rejected |
| Shared ancestor | SAFE REJECTION | Numerical agreement; lineage/domain gate rejected |
| Wrong Measure verdict | SUCCESSFUL RECOVERY | Auditor detected and corrected it |
| Corrupted Memory | SUCCESSFUL RECOVERY | Audited before Explorer; rebuilt from pair decision |
| Invalid Recovery | SAFE REJECTION | Wrong candidate rejected |
| Valid incumbent | SAFE AUTHORIZATION | Valid incumbent retained over bad candidate |
| Stale incumbent | SUCCESSFUL RECOVERY | Quarantined; pair-grounded candidate committed |
| Epoch transition | SAFE AUTHORIZATION | Fresh epoch pair committed |
| Common mode | OUT-OF-MODEL COMMON-MODE FAILURE | Wrong agreeing pair committed in 3/3 |

All 69 runs completed with their frozen protected outcomes. The common-mode
result is separated from the protected claim.

## 9. False accepts

Protected in-model false accepts: **0**. Out-of-model common-mode false accepts:
**3**. Internal generic false-accept counter: 0; the three common-mode failures
were found by the external oracle, illustrating why internal counters alone
were insufficient.

## 10. False rejects

Externally recomputed false rejects: **0**. The 33 safe rejections involved
persistently invalid evidence or invalid recovery, so they are not false
rejects and are not described as recovery.

## 11. Re-observation outcomes

There were 42 re-observations. Twelve recovered: transient A, transient B,
stale A, and stale B across three seeds. Each used exactly one additional round.
No transaction used a second retry.

## 12. Persistent-disagreement outcomes

Thirty transactions stopped after the bounded second round: persistent A/B
value corruption, wrong epoch A/B, wrong transaction A/B, duplicated A,
source spoof, derived B, and shared ancestor. The coordinator never selected a
source as truth.

## 13. Derived-source negative control

B was constructed by copying A and relabeling the port fields. The naive value
checker agreed in 3/3 runs. The real gate rejected both rounds in every run from
the `DERIVED_SOURCE` lineage, yielding six derived-source rejections and zero
commits.

## 14. Shared-ancestor negative control

A and B agreed numerically but declared `SHARED_ANCESTOR` lineage and
`SHARED_OBSERVATION` domain. Naive equality agreed; the real gate produced six
rejections and zero commits.

## 15. Common-mode negative control

**COMMON-MODE FALSE ACCEPT OBSERVED.** A and B were corrupted to the same wrong
next-state and consequence while retaining otherwise acceptable separate
metadata. The pair gate showed false confidence in 3/3 runs. Measure correctly
found disagreement with Map prediction, but Recovery treated the agreeing pair
as authoritative ground, replaced the Map state, and committed the wrong
outcome. Only the hidden oracle exposed all three false commits.

The preregistration expected the unchanged Map/Measure check might reject this
pattern. The observed Recovery path disproved that expectation. The result was
not repaired or removed. It is outside the declared independent-single-source
fault assumption, but it sharply limits what v1 establishes.

## 16. Memory → Explorer evidence

In every clean episode, state 1 initially selected `ADVANCE`. Its authorized
consequence was `-1`. On the next state-1 visit, audited cross-source Memory
made `HOLD` score higher, changing the action to `HOLD`. The behavior occurred
in 3/3 runs while the eight-record/eight-decision rings rotated correctly.

## 17. Recovery results

Successful re-observation recoveries: 12. Separate Measure corrections: 3.
Memory corruptions detected and rebuilt: 3. Stale incumbent recoveries: 3.
Invalid state recoveries rejected: 3. Recovery never edited receipts, selected
a source, or called an authorization method on its own output.

## 18. External recomputation and audit

After every transaction, campaign code compared committed state and Memory
against the hidden oracle and retained a bounded independent audit summary. It
also reimplemented structural-pair validation without calling the runtime pair
authorizer. Maximum external trace occupancy was 12 of 24 records. This audit
found the three common-mode false accepts that runtime counters did not.

## 19. Falsification table

| Frozen protected criterion | Result |
|---|---|
| One corrupted source commits false state | PASS: 0 protected false accepts |
| Stale/wrong epoch/transaction accepted | PASS: 30 provenance rejections |
| Duplicate A counted as A+B | PASS: zero duplicate commits |
| Derived B accepted as independent | PASS: 6 rejections |
| Shared ancestor accepted | PASS: 6 rejections |
| Commit before complete pair | PASS: delayed/partial checks |
| Persistent disagreement arbitrarily resolved | PASS: 30 safe stops |
| Invalid recovery authorized | PASS: 3 rejected |
| Corrupt Memory influences Explorer | PASS: 3 detected before policy use |
| Duplicate authorization | PASS: 0 |
| Bound exceeded | PASS: none |
| Declared transient cannot recover | PASS: 12/12 recovered |
| Memory behavior change lost | PASS: 3/3 changed |

The out-of-model common-mode false accepts do not change these protected results
and must accompany any statement of the v1 claim.

## 20. Updated hardware mapping

The updated [hardware mapping](../docs/HARDWARE_FRAMEWORK_MAPPING.md) identifies
Source A/B adapters, pair buffer, disagreement detector, one-round
re-observation controller, cross-source authorizer, quarantine, and Memory
commit gate. They remain PROPOSED RTL. No synthesis, timing, area optimization,
or complete v1 RTL was performed.

## 21. Remaining trust assumptions

- Actual diversity and integrity of both source implementations.
- Integrity of port registration, source IDs, and declared fault domains.
- Cross-source authorizer, coordinator, Measure auditor, and pair store.
- Absence of hidden common causes within the protected claim.
- Independence and correctness of the test oracle for experiment scoring.
- No hostile collusion, identity forgery outside the modeled spoof, wrap,
  concurrency, power loss, or physical fault in trusted control.

## 22. Narrowest defensible conclusion

SUPPORTED UNDER TESTED CONDITIONS: the bounded framework required two
structurally separate, provenance-matched channels; made no provisional commit;
recovered from declared transient single-channel faults using one
re-observation; stopped on persistent disagreement; and used only authorized
pair history to change later behavior. Two agreeing channels did not guarantee
truth: identical common-mode corruption caused three externally detected false
accepts.

## 23. Recommended next experiment

The next problem is diversity and fault-domain establishment. Keep the same
world, two-source count, loop, and bounds. Pre-register a test in which the
authorizer receives evidence about source implementation diversity or an
orthogonal renewed interaction, then fault that evidence and the registration
path. Determine whether common-mode agreement can be detected without treating
Map prediction as unquestionable truth. Do not add a third source automatically.

## Reproduction

```bash
make test
make independent-commit
make independent-commit-followup
make base-framework-v0
make base-framework-v1
```
