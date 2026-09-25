# Horus: current technical state

Review snapshot of research commit **`9219d313f3fca720c99bf7af9876d35e52ed89b9`**.
Start here, then use [REVIEW_GUIDE.md](REVIEW_GUIDE.md). This snapshot adds
navigation and verification records; inherited source, prompts, thresholds,
results and historical classifications are unchanged.

**Read the [grounded clean-root manifest](experiments/grounded_lineage_rebaseline_v0/clean-root-manifest.json)
and [claim-eligibility firewall](experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json)
before treating any historical experiment as current grounded evidence.** The
manifest's evidence categories A–D are distinct from individual experiments'
decision letters. The historical root README and `docs/PROVENANCE.md` /
`docs/EVIDENCE.md` describe the original hardware baseline; their inventory and
scope statements are not descriptions of this entire later research tree.

## Intended loop and implemented boundaries

Horus is a bounded research framework for proposals checked against externally
realized evidence. Its intended loop is:

`proposal → prediction → execution → realized receipt → Measure → Recovery if required → independent authorization → authenticated Memory → future proposal`.

| Component | Responsibility and authority |
|---|---|
| Explorer | Proposes an allowed action. A model response has no execution, receipt, authorization or Memory-writing capability. |
| Map | Proposes next state and consequence from the permitted view. A prediction is not an observation; diagnostic probes can remain entirely detached from the protected prediction latch. |
| External execution | The trusted simulator boundary executes an action and issues its original event receipt. It is the reality source within this software experiment. |
| Measure | Checks the latched prediction against the admitted realized event; disagreement does not make the prediction true. |
| Recovery | Proposes a bounded correction/re-observation when required. A repair proposal cannot authorize itself or change the original receipt. |
| Authorizer | Checks receipt, identity, values and required status independently of the proposal. The trusted coordinator determines recovery scope; the candidate must satisfy that scope. |
| Memory | Publishes authorized observations atomically with protected state and aligned evidence. Retained contradictory observations coexist; negative outcomes do not remove allowed actions. |
| Mechanical exploitation | Strict finite argmax over detached consequence forecasts; invalid inputs and tied maxima abstain. This is the reference comparison mechanism, currently a standalone read-only chooser, not an integrated general closed-loop policy. |

The concrete current entry is
[`StatusBoundFramework`](experiments/state_recovery_authorizer_status_binding_v1/framework.py),
supplied the actual `ExternalExecutionBoundary.reader()` from
[`receipt.py`](experiments/realized_event_grounding_v0/receipt.py).
The [grounded wrapper](experiments/realized_event_grounding_v0/framework.py)
requires a realized-event package at ingress, validates the original receipt
object, domain and pending transaction binding, and preserves the original
pre-execution prediction. It stages updates before publishing state, Memory,
pair and package together. Failed admission leaves the protected publication
unchanged; quarantine and bounded recovery do not confer authority.

Receipt identity is `(source_identity, event_id, epoch, transaction_id)`;
content binding also covers pre-state, action, next state and consequence.
Compatibility fields called A and B share this original receipt root: they are
not independent physical truth sources. Receipt authentication is a Python
object-capability contract, not a cryptographic proof across hostile processes.

The [role adapters](experiments/composition_input_bindings_v1/adapters.py)
bind finite aliases and inputs to their role and context. The
[cross-episode boundary](experiments/cross_episode_initialization_boundary_v1/boundary.py)
stages a copyable simulator and framework, then changes one publication
reference; it retains issuer/event continuity and history without manufacturing
observations. The [projection](experiments/cross_episode_initialization_boundary_v1/projection.py)
uses epoch plus transaction identity. This is tested simulator initialization,
not arbitrary real-world rollback. The optional
[Map-to-Explorer interface](experiments/map_guided_explorer_interface_v0/interface.py)
checks authenticated snapshots and freshness while keeping forecasts detached.

The tested profile bounds Memory and aligned pair/package storage at eight,
trace at 24, episodes at 12 transactions, epochs at two, authorization ledger
and external execution counter at 24, and recovery/re-observation at one. These are finite fixtures,
not an endurance guarantee. FIFO eviction is explicit; retained observations
are not rewritten to erase contradiction. `UNTRIED` / empty permitted history
means unknown, not consequence zero. A later authenticated different outcome
is new evidence, not automatically an integrity failure. Retesting remains
allowed; blind repetition, uncertain retests and behavioral revision are
different measurements, none by itself establishes causal inference.

## Clean root, trust and claim firewall

The [rebaseline report](research/grounded-lineage-rebaseline-v0-results.md),
[dependency inventory](experiments/grounded_lineage_rebaseline_v0/legacy-import-inventory.json)
and exact file hashes define the approved current entrypoints. Old Base
Framework v1/v2 A/B/C stationary-law observers and process registries remain
historical artifacts. Their law agreement must never substitute for an original
realized receipt as current reality authority. Shared primitives imported from
old modules do not make their old authority paths current.

The claim manifest is reviewed evidence policy, not runtime prevention of
deliberately constructing a legacy framework. Its 42 checkpoint entries cover
the rebaseline's historical inventory; later diagnostics retain their own
explicit scopes. Historical decisions remain immutable even when current use
is restricted. In particular, interrupted original composition v2 evidence
remains ambiguous; replacement R1 is a separately recorded campaign.

Trusted roots remain the external emitter/source issuer, host Python process,
enrollment/coordinator, finite parsers and projections, and evidence recorder.
Model-behavior claims additionally depend on the recorded inference runtime.
Hashes bind retained bytes; they cannot establish physical truth or restore
original Python object identity from JSON. Compromised trusted roots,
common-mode corruption and hostile-host isolation are outside these guarantees.

Within the firewall, the evidence supports bounded receipt-grounded publication,
status-scoped recovery authorization, finite cross-role bindings, contradictory
receipt history, and trusted cross-episode initialization. R1 supports tested
multi-role publication integrity and descriptive behavior, not reasoning
synergy. Authenticated Map-history effects and revision results are bounded to
their tested inputs; some read-only proposal scores still use declared laws,
as recorded per checkpoint. The temporal Map result supports a bounded negative
for forecasting beyond recency. Mechanical comparison and retained-data
forensics remain synthetic/detached evidence, not newly executed improvements.

Not established: general world modeling, general temporal inference, reliable
model Explorer exploitation, persistent/weight learning, reinforcement
learning, general closed-loop intelligence, hardware deployment, or AGI/RSI.

## Current Map problem and unchanged evidence chain

Mechanical exploitation removed seven Explorer comparison errors on the retained
dataset. The remaining bottleneck is what Map predicts. The following counts
are historical results, not new inference in this snapshot:

| Checkpoint | Frozen result and narrow observation |
|---|---|
| [Grounded rebaseline](research/grounded-lineage-rebaseline-v0-results.md), `79921b1` | A — grounded research baseline established, with the claim firewall. |
| [Mechanical exploitation](research/mechanical-exploitation-baseline-v0-results.md), `004ec5a` | A — ready. True-best selection 25/48 versus historical model pipeline 18/48; 19 Map ties and four wrong maxima remain. These retrospective choices were never executed. |
| [Ranking forensics](research/map-ranking-failure-forensics-v0-results.md), `bf26f6a` | All 23 residual failures underpredict the true-best positive consequence: W0 seven, W1 twelve, W3 four. Latest-value ranking would yield 48/48 in this retained dataset. Internal diagnosis: NOT DETERMINABLE FROM RETAINED EVIDENCE. |
| [Positive evidence depth](research/map-positive-evidence-depth-v0-results.md), `1b1f756` | B — NO DEPTH RESCUE OBSERVED. Depth one 0/4 versus depth two 1/4; one improvement did not meet the frozen rescue rule. |
| [Self-loop coupling](research/map-self-loop-consequence-coupling-v0-results.md), `543b4c5` | A — SELF-LOOP / CONSEQUENCE COUPLING EFFECT OBSERVED. Positive self-loop 0/4 versus positive movement 4/4 in the registered comparison. |
| [Consequence-only isolation](research/map-consequence-only-isolation-v0-results.md), `9646927` | A — JOINT-OUTPUT COUPLING EFFECT OBSERVED. Joint 0/4 versus consequence-only 4/4 on the registered self-loop case. |
| [Output-schema isolation](research/map-output-schema-isolation-v0-results.md), `bf74d7e` | C — NOT ESTABLISHED. Joint consequence 2/4 versus consequence-only 4/4; two improvements. Joint exactness 1/4 is a separate metric and cannot replace consequence accuracy. |
| [Moving consequence-schema transfer](research/map-consequence-schema-transfer-v0-results.md), `9219d31` | C — NOT ESTABLISHED. Joint consequence 7/8 versus consequence-only 8/8, one improvement, zero regressions; 16/16 valid. WA 3/4 versus 4/4; WR 4/4 versus 4/4. The frozen A requirements included joint positive ≤4/8 and ≥3 improving pairs; neither was met. |

The last study was already completed in the inspected workspace after the
request's listed `bf74d7e` anchor. It is preserved here, not launched or rerun.
Earlier W0 ADVANCE and W3 RETREAT moving-positive failures remain part of the
record; they did not reproduce strongly under the later one-row-history,
alias/seed schedule. That C result does not establish a general transfer effect
or resolve the earlier failures.

**Working hypothesis only:** Map's joint representation of `next_state` and
`consequence` may influence consequence prediction. Output contrasts have not
identified an internal cause. Whether consequence-only prediction reliably
helps moving-positive relations remains unresolved after the bounded transfer
test. The consequence-only isolation, output-schema isolation and schema-transfer
probes are detached and scored against new original simulated receipts after
response; successful non-model framework controls are not model prediction
credit. Positive-depth and self-loop-coupling studies instead latch model
predictions before execution, as their unchanged fixtures document.

The [temporal negative](research/map-temporal-relation-forecast-v0-results.md),
[representation/comparison negative](research/explorer-finite-value-comparator-v0-results.md)
and [decomposition negative](research/map-explorer-oracle-decomposition-v0-results.md)
remain visible and unchanged. No new cutoff, prompt adjustment or relabeling
has been applied to improve the presentation.

## Hardware and fabric status

Public `rtl/`, `tb/`, `sim/` and [bounded-commit fixtures](experiments/bounded_commit/)
retain arithmetic, normalization, MAC/array, routing/fabric and detector/repair
research. Selected RTL benches run under Icarus; inclusion of a module does not
mean it is fully validated. The protected-source commit gate separates repair
proposals from authorization with protected records, quarantine and epoch/
transaction binding. Its trusted protected source and checker must remain
causally independent of the repaired output.

The [hardware mapping](docs/HARDWARE_FRAMEWORK_MAPPING.md) describes the earlier
v0–v2 mapping and proposed integration. It is not a complete RTL implementation
of the current grounded software loop. The [bounded authorization report](research/bounded-independent-authorization-results.md)
preserves simulation and mapped estimates: standalone gate with trace ring
disabled (decision output retained) 29,928.7040 µm²; default gate with the
96×8 trace ring 58,937.7760 µm²;
protected-bank, quarantine, checker and identity probes about 12,475.7152,
12,318.0640, 3,439.5488 and 441.6736 µm². These separate synthesis probes are
**not an additive partition** of the full gate. Trace reduction 96→63 bits was
tested on 21 paired schedules, with an 8,872.2592 µm² mapped estimate reduction.

Broader-fault tests reject unsupported patterns; recovery remains specific to
the declared exponent-spike case. Gate rejection is not rollback of every DUT
internal side effect. Sky130 mapping is an area estimate, not timing closure,
place-and-route, power validation, FPGA deployment or fabricated silicon.
Synthesis was not rerun for this handoff; simulation regressions were.

## Reproduction and next review questions

[REVIEW_GUIDE.md](REVIEW_GUIDE.md) gives exact clean-checkout setup, public
deterministic/replay commands and current-issue inspection. The actual commands
and counts run for this handoff are in [review/VERIFICATION.md](review/VERIFICATION.md).
They require no model server or credentials. Full historical replay of recent
campaigns requires separately retained private archives; compact public results
permit inspection but do not recreate those archives. No live inference ran.

Questions for a separate decision: whether to split next-state and consequence
prediction; when moving-positive effects transfer; what genuine exploration or
uncertainty reduction should require; and how to integrate the bounded pieces
into an eventual closed loop. Future Zakhor/Horus interaction and long-duration
Zakhor coherence remain untested here. Endurance should be a primary outcome,
including early/middle/late windows, cumulative drift, worst-window degradation,
perturbation recovery and restart recovery. No such study or redesign is part
of this snapshot.
