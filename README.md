# Horus

Horus investigates how AI agents can use authenticated consequences of execution
as durable evidence for later decisions, while keeping model predictions and
proposals separate from authority over execution, Memory and modification. It
combines Python agent experiments, local model runtimes and Verilog hardware
research. **This is a bounded research system, not a production autonomous agent;
AGI and recursive self-improvement have not been demonstrated.** Most agent
results concern small simulated worlds, not deployment in an open environment.

## Start here: code and research status

**Default branch and research frontier are different snapshots.** Audited against
`main` at `c214511` and the published research heads on 2026-09-29.

| Where | What is present | What that means |
| --- | --- | --- |
| **`main`** | Hardware baseline, receipt/authorization framework, earlier model-role experiments, runnable Horus v0, restartable v0.1 and bounded v0.2 consequence training. | [Runnable system](docs/HORUS_V0.md) and [training result](research/grounded-learning-v0/RESULTS.md). This checkout does **not** contain the S+E selector. |
| **Promoted research lineage** | Grounded mechanical authority → S → E → ordinary model/mixed route. | [Externally approved S+E promotion][e-promotion] on a preserved research branch; promotion is not a merge into `main` or proof of general reward improvement. |
| **Latest completed analysis** | Verified introspection plus Qwen diagnosis. | [INSUFFICIENT_CURRENT_EVIDENCE][diagnosis]: a post-E campaign evidence gap survived; two other diagnoses were rejected. No proposal or modification followed. |

For a quick technical review, read the architecture and results below. For the
full chronology and immutable branch links, use the [research index](docs/RESEARCH_INDEX.md).

## Research question

Can consequences change later behavior without allowing a model to declare its
own predictions true?

```text
experience → authenticated consequence → grounded Memory → later decisions
```

The longer-term hypothesis adds a separate, externally controlled research loop:

```text
inspect → diagnose → propose → predict/falsify → prospective test
       → external approval or rejection → changed incumbent → repeat
```

That recursive loop remains unestablished. A proposal grants no permission to
rewrite code, policy, grounded state, Memory or protected execution.

## Current promoted research architecture

**Research branches only; this is not the `main` runtime.** The active selector
there is [`grounded_agent.empirical_policy.integrated_decide`][e-code].

```text
authenticated experience in durable Memory
                    ↓
           grounded-state derivation
                    ↓
        decision ownership, in precedence order:
        1. grounded mechanical authority
        2. bounded stagnation escape (S)
        3. bounded empirical evidence acquisition (E)
        4. ordinary model/mixed route
                    ↓
           protected world execution
                    ↓
         original receipt → authorization
                    ↓
          durable Memory → next decision
```

- **Grounded mechanical authority** resolves applicable exact, experienced
  deterministic values in software. It is distinct from S.
- **S** acquires missing relation evidence after qualifying repeated
  deterministic established-zero fallback.
- **E** acquires missing relation evidence after qualifying empirical
  deterioration. S and E select without a model when triggered; neither creates
  or authenticates receipts.
- **Ordinary model route** handles the remaining admissible uncertainty. The
  historical Dolphin/Mixtral reference remains the incumbent on this lineage;
  Qwen3 action substitution was not promoted.
- **Receipts and Memory** bind executed outcomes to provenance. Only authorized
  evidence enters durable grounded Memory; predictions do not overwrite it.

Authenticated context is validated before routing. In a nonmechanical context,
simultaneous S/E eligibility raises an integration error with no action or model
request. Malformed evidence also fails closed. See the [promotion, tests and
rollback record][e-promotion] and [grounded-state contracts][core].

Older full Horus/Zakhor designs were parked in the grounded research lineage;
their retained code is historical, not the active architecture. The [core
consolidation][core] retains receipts, authorization, durable evidence and
grounded epistemic state without reinstating those designs.

## What has been demonstrated—and what has not

Statuses below retain the original studies' scope. A passing integrity gate does
not establish intelligent behavior, and a diagnostic pass does not establish
autonomous performance.

| Area | Result and limit | Evidence location |
| --- | --- | --- |
| Consequence → Memory → behavior | Bounded v0 demonstration changes `ADVANCE` to `HOLD` after an authorized negative receipt. | [`main`: runnable loop](docs/HORUS_V0.md) |
| Cross-episode Memory | Overall transfer **NOT ESTABLISHED**; a separate two-observation Map effect was supported. | [`main`: transfer](research/cross-episode-model-transfer-v0-results.md), [depth](research/cross-episode-map-history-depth-v1-results.md) |
| Contradiction/revision | Stale-Memory Map revision **REPLICATED**; the corresponding Explorer revision **NOT ESTABLISHED**. | [`main`: Map](research/cross-episode-stale-memory-map-revision-v1-results.md), [Explorer](research/cross-episode-stale-memory-explorer-revision-v1-results.md) |
| Model-role composition | R1 **INTEGRITY PASS**, not reasoning synergy; original interrupted v2 remains **NOT ESTABLISHED**. | [`main`: R1](research/model-proposal-role-composition-v2-replacement-r1-results.md) |
| Grounded training | v0.2 adapter heldout accuracy 6/12 → 8/12, including two regressions. No broad learning claim. | [`main`: training](research/grounded-learning-v0/RESULTS.md) |
| S and E | Bounded acquisition mechanisms prospectively tested and promoted. Overall autonomous reward improvement unestablished. | Research: [S][s-promotion], [E replication][e-replication], [E promotion][e-promotion] |
| Runtime/model substitution | Qwen3 runtime qualified; autonomous substitution **BEHAVIORALLY UNSUITABLE** under its frozen gate. | Research: [qualification][qwen-runtime], [comparison][qwen-substitution] |
| Self-model and diagnosis | v0/v0.1 **GROUNDING FAILED** overall; latest diagnosis **INSUFFICIENT_CURRENT_EVIDENCE**. | Research: [v0][self-v0], [v0.1][self-v01], [diagnosis][diagnosis] |

## Selected findings

1. **Agreement is not truth.** Historical common-mode and false-registry
   controls caused false accepts despite source agreement. These failures bound
   the software trust model. [Checkpoint evidence](research/CHECKPOINTS.md).
2. **Interface details change model behavior.** Action-label and order studies
   exposed lexical interference; opaque labels did not establish neutrality.
   [Representation checkpoint](research/representation-priors-and-neutrality-checkpoint.md).
3. **Prediction revision and action revision are different capabilities.**
   Matched cross-episode studies supported Map revision while Explorer failed
   its own gate. Accurate retained evidence did not guarantee better choices.
   [Map](research/cross-episode-stale-memory-map-revision-v1-results.md) /
   [Explorer](research/cross-episode-stale-memory-explorer-revision-v1-results.md).
4. **Faster inference did not justify promotion.** In the frozen substitution
   campaign, Dolphin action inference totaled 1,776.09 seconds for 62 calls;
   Qwen3 took 36.80 seconds for 90 calls. This is a workload-total comparison,
   not a matched per-token benchmark. Qwen chose HOLD in all 90 model-mediated
   decisions and acquired fewer relations. [Measured comparison][qwen-substitution].
5. **Semantic responsiveness did not transfer automatically.** Qwen passed a
   bounded read-only semantic gate, then again chose HOLD throughout the
   subsequent R128 autonomous campaign. [Diagnostic][qwen-semantic] /
   [autonomous result][qwen-r128].
6. **Declarative self-description is not policy execution.** Self-model v0.1
   passed 104 reconstruction checks but matched only 13/20 routing cases; its
   overall classification remains failed. Later diagnosis used deterministic
   introspection and retained only an evidence gap. [v0.1][self-v01] /
   [diagnosis][diagnosis].

## Research methodology

The registered studies freeze interfaces, inputs, seeds, thresholds and stop
rules before prospective evaluation. Matched interventions and negative controls
separate evidence effects from labels, order, model choice and authority wiring.
Receipts, request hashes, replay records and source manifests support inspection
of what actually ran.

Failed gates, invalid studies and interrupted checkpoints stay in the record.
Where retries or extensions are prohibited, outputs are not repaired into
passes. Reporting corrections and separately authorized replacement campaigns
are documented as such. Integrity, feasibility, behavioral performance and
promotion are separate decisions; model text cannot authorize its own adoption.
See the [claim-eligibility record](experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json),
[historical verification](review/VERIFICATION.md) and [research index](docs/RESEARCH_INDEX.md).

Public summaries and semantic replay are not substitutes for omitted signed raw
sessions. Full authentication/replay of some later campaigns requires retained
private archives; raw reasoning, credentials and private Memory are not linked
as reproduction downloads here.

## Repository map

| Path in `main` | Purpose |
| --- | --- |
| [`horus/`](horus/) | Runnable v0/v0.1 loop, durable sessions and bounded v0.2 training/inference interfaces. |
| [`research/`](research/) | Preregistrations, result reports and preserved negative checkpoints. |
| [`experiments/`](experiments/) | Study-specific implementations, fixtures, compact results and replay tools. |
| [`docs/`](docs/) / [`review/`](review/) | Architecture, reproduction, provenance and dated verification records. |
| [`rtl/`](rtl/), [`tb/`](tb/), [`sim/`](sim/) | Reduced-precision arithmetic, normalization, scale tracking and bounded fault/recovery origins. |
| [`tests/`](tests/), [`scripts/`](scripts/), [`Makefile`](Makefile) | Python/RTL checks and reproducible test runner. |
| [`models/`](models/) | The specialized v0.2 consequence adapter and its lineage; not the Qwen3 research runtime. |

`grounded_state/` and `grounded_agent/` belong to the [later research lineage][core],
not this default-branch checkout. The hardware work remains preserved and
reproducible; its presence does not imply an RTL implementation of the agent.

## Reproduction

For the default-branch baseline, use Python 3.10+, GNU Make and Icarus Verilog/vvp:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
make test
```

The deterministic v0 demo needs no model server and executes a small simulated
world. Keep generated artifacts outside the checkout:

```bash
HORUS_DEMO_DIR=$(mktemp -d)
python -m horus.run --output "$HORUS_DEMO_DIR/horus-v0-run.json"
```

See [baseline reproduction](docs/REPRODUCIBILITY.md) for authorization/framework,
optional numerical and synthesis commands; [live sessions](docs/HORUS_V0_1_LIVE.md)
and [v0.2 training](docs/HORUS_V0_2_GROUNDED_LEARNING.md) for their separate model
requirements. The later [review verification](review/VERIFICATION.md) records an
isolated-environment core installation/pass; the older reproduction document
retains its earlier installation-status caveat. Neither establishes universal
platform compatibility.

Research-branch results require their pinned checkout and per-study instructions.
A historical manifest may intentionally require the original README bytes: use
its recorded commit for exact preservation checks. Running a live campaign is
new inference/execution, not merely replaying its public result.

## Current frontier

The latest [verified-introspection diagnosis][diagnosis] recognized the supplied
inventory's absence of a post-E autonomous scientific campaign, within the
preserved lineage. It did not establish a new current behavioral defect or a
useful modification. Selecting the sole surviving gap does not demonstrate
blind diagnostic generalization.

The next question is whether one frozen diagnostic process can distinguish
actual defects, benign behavior, obsolete failures and missing evidence across
blinded systems, before application to Horus. **This is a research question, not
a completed result or a campaign launched by this documentation update.**

## Limitations

- Evidence is bounded by tested worlds, models, interfaces and schedules.
  Authentication establishes origin/integrity under software trust assumptions;
  it does not make a dishonest source correct or protect a compromised host.
- No general safety proof, open-world autonomy or recursive self-improvement is
  established. Acquiring evidence can incur negative consequences.
- Memory-conditioned behavior is not persistent weight learning. The separate
  v0.2 LoRA experiment updates a specialized Qwen2.5-0.5B consequence role on a
  small dataset; it is not the later Qwen3-14B action/analysis work.
- Promotion of S/E establishes a bounded mechanism decision. The latest
  diagnosis found no post-promotion autonomous scientific campaign in its
  preserved lineage, so system-level benefit remains unestablished there.
- Hardware synthesis figures are mapped estimates, not timing closure, physical
  fault protection or fabricated-silicon results.

## Historical research index

The [research index](docs/RESEARCH_INDEX.md) connects hardware origins, the
Explorer/Map/Measure/Memory/Recovery experiments, realized-event grounding,
branch-only policy promotions and current analysis work. It links the original
[development sequence](research/DEVELOPMENT_HISTORY.md), [checkpoint catalogue](research/CHECKPOINTS.md)
and the previous README without rewriting their claims. Older documents titled
“current” are dated snapshots; consult their commit and scope.

Project source is licensed under [CERN-OHL-S-2.0](LICENSE). Third-party tools,
models and datasets retain their own terms. See [provenance](docs/PROVENANCE.md).

[core]: https://github.com/sotiriosc/horus/blob/373b1ec5b6269d6d3bb8bd853da2e692800568c3/research/grounded-state-core-v0/architecture.md
[s-promotion]: https://github.com/sotiriosc/horus/blob/8bc396b96662ff7fa04b87a7a3300008e12228b9/research/grounded-stagnation-escape-promotion-v0/promotion-record.md
[e-promotion]: https://github.com/sotiriosc/horus/blob/69947aa243a69e7ae26db534727a7122922d978d/research/empirical-evidence-acquisition-promotion-v0/result.md
[e-code]: https://github.com/sotiriosc/horus/blob/69947aa243a69e7ae26db534727a7122922d978d/grounded_agent/empirical_policy.py
[e-replication]: https://github.com/sotiriosc/horus/blob/f90a84444ab320e13db4b1573d454c3d0d7f90d5/research/empirical-evidence-acquisition-replication-v0/result.md
[qwen-runtime]: https://github.com/sotiriosc/horus/blob/48ac31cb3f111c74f1ef2eea77af2d7c26435299/engineering/grounded-agent-development-runtime-v0/qualification.md
[qwen-substitution]: https://github.com/sotiriosc/horus/blob/4e3053c05e6bafb5c3f53b08ce1ceedf0ebb65a3/research/qwen3-grounded-agent-substitution-v0/result.md
[qwen-semantic]: https://github.com/sotiriosc/horus/blob/a02af959d18b69a34cfc20ce87c7feb5e0296471/research/qwen3-bounded-thinking-action-v0.1/result.md
[qwen-r128]: https://github.com/sotiriosc/horus/blob/40dbe69673e9b146888fdbb08c3df713aef6f336/research/qwen3-r128-autonomous-grounded-agent-v0/result.md
[self-v0]: https://github.com/sotiriosc/horus/blob/ba698e948e2ae27427bac1e9f772cf6c8b485de8/research/agent-led-self-improvement-proposal-v0/result.md
[self-v01]: https://github.com/sotiriosc/horus/blob/ecd097af2f007cb431e3ae736832960f86805deb/research/agent-self-model-grounding-v0.1/result.md
[diagnosis]: https://github.com/sotiriosc/horus/blob/11b32a6ab54b803f0212ece834a4d7c7c75a23cb/research/agent-led-diagnosis-verified-introspection-v0/result.md
