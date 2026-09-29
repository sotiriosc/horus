# Blind diagnostic generalization v0 — prospective, zero inference

This branch starts at `11b32a6ab54b803f0212ece834a4d7c7c75a23cb`.
The completed verified-introspection result remains **INSUFFICIENT_CURRENT_EVIDENCE**.
Its valid selected evidence gap does not establish general diagnostic ability: two
incorrect raw candidates were rejected by external source-linked review. This
benchmark measures every raw first diagnosis, with no such selection or rescue.
The previous v0 failure and v0.1 Phase-A pass / Phase-B failure also remain intact.

## Authorization and chronology

This phase authorizes deterministic construction, testing, two commits that freeze
the method and cases, and publication of this research branch. **Zero model calls.**
There is no inference client or server startup in this implementation. Inference,
including any compatibility probe that invokes a model, requires a separate explicit
continuation. There is no solution generation or architecture-change authority.

1. Develop code and synthetic scorer fixtures using only seeds prefixed
   `development-only/`. These exercise templates but do not select the final seed.
2. Commit all method files before calling `generate`/`bundle` with the final public
   seed or writing final worlds. This is Method Freeze.
3. With that exact commit checked out and all method bytes unchanged, materialize
   once, regenerate byte-for-byte, verify, record hashes, and commit Case Freeze.
4. Audit all reachable public history; publish only this new branch. Stop.

**A generator bug discovered after Method Freeze requires STOP and a new
preregistration/replacement study.** Preserve the failed frozen version and report
it; do not amend the generator, prompt, schema, scorer, gates, seed, or cases.
No inference is permitted to diagnose or repair a construction problem.
A later integrity/prompt/case mutation, hidden answer leakage, scorer corruption,
unauthorized retry, model/runtime mismatch, or protocol breach gives INVALID_STUDY.
A runtime context/transport failure stops the campaign with INVALID_STUDY, remaining
calls NOT_RUN; never tune the prompt/budget or replace a failed call in this study.
A completed but malformed final answer is simply wrong, with no retry or repair.

## Ontology, worlds, and scientific unit

The five exact classes and definitions in `protocol.json` are authoritative.
Contradictory capture/deployment evidence takes precedence over operational
classification. Otherwise classify the explicitly deployed version. Incomplete
operational facts imply INSUFFICIENT_EVIDENCE where benign and defect completions
both exist. Demonstrated current violation implies SUPPORTED_CURRENT_DEFECT.
A repaired old violation with sufficient healthy current evidence implies
HISTORICAL_DEFECT_NOT_CURRENT; sufficient valid observations without either
violation imply NO_SUPPORTED_DIAGNOSIS. Claims are scoped to declared inputs,
contracts and evidence, not global absence of every possible defect.

| Class | Semantic worlds | Renderings |
| --- | ---: | ---: |
| SUPPORTED_CURRENT_DEFECT | 6 | 24 |
| NO_SUPPORTED_DIAGNOSIS | 4 | 16 |
| INSUFFICIENT_EVIDENCE | 4 | 16 |
| HISTORICAL_DEFECT_NOT_CURRENT | 3 | 12 |
| INVALID_OR_CONTRADICTORY_EVIDENCE | 3 | 12 |

The unit is a **semantic world**, not its four presentations. These are 20 designed
worlds from six templates, with deliberate paired dependence, not 20 independent
population draws and certainly not 80 independent samples. No confidence interval
or population-wide capability claim is preregistered.

| Family (grader only) | Independent system | Injected mechanism |
| --- | --- | --- |
| version_selection | Document formatting | Reads an inactive configuration |
| authority_precedence | Access decision service | Secondary decision overrides primary denial |
| entity_binding | Instrument catalogue | Publishes a reading from another entity's record |
| publication_update | Network attempt accounting | Acknowledges a batch without updating the total |
| operation_idempotence | Billing accumulator | Charges attempts instead of distinct operations |
| boundary_comparison | Pressure controller | Uses inclusive comparison at equality |

These are self-contained synthetic contracts, not transformed Horus behavioral
records. In particular billing idempotence, strict numeric boundaries, entity
binding, and access precedence require no stagnation-escape/evidence-acquisition
semantics. Generic software-principle overlap is unavoidable and not hidden.

Healthy controls include repeated valid formatting responses, permitted backup
routing, link-caused delivery failures despite correct accounting, and repeated
stable readings that already satisfy the objective. Unknown worlds omit the active
configuration, a decisive operation identity, batch/implementation observations, or
sensed level. Unit tests construct both benign and violating completions while
retaining every supplied known fact. Historical worlds show old/new implementation
traces for precedence, configuration, and billing; deployment is explicit, not
inferred from release order. Invalid worlds contradict an immutable event payload,
the simultaneous deployment identity, or two checksums asserted to describe the
same captured bytes. Capture contracts distinguish invalid evidence from observed
implementation violations, so an operational defect is not automatically invalid.

Every world contains the same evidence-record categories, both version traces,
and neutral capture records. Gold is computed by a contract oracle over the
structured observations and checked against the intended mutation classification;
rendering never accepts the enclosing gold-bearing case object.

## Six matched pairs

The exact JSON paths are frozen in `materialize.DECLARED_PAIR_PATHS`; materialization
asserts equality with computed diffs. Quantities and nondecisive observations are
shared within each family. Duplicated captured output changes are consistency
consequences, not additional independent interventions.

| Pair | Changed fact(s) | Expected direction |
| --- | --- | --- |
| d1 / h1 | Used configuration, derived output and mirrored capture | Current defect / healthy |
| d2 / t1 | Deployment version and matching capture version | Current defect / historical only |
| d3 / h2 | Owner of selected record | Current defect / healthy |
| d4 / h3 | Publication field set, derived total and capture | Current defect / healthy |
| d5 / u1 | Key column and second operation identity become UNKNOWN | Current defect / insufficient |
| d6 / h4 | Comparator and computed result/output/capture | Current defect / healthy |

Counterfactual success requires both semantic endpoints correct and at least three
of the four matching label/order cells jointly correct. All six left endpoints are
current defects; directions are not chosen after seeing responses.

## Seed, rendering and anti-coaching

The immutable public final seed is `blind-diagnostic-generalization-v0`.
`derive(seed,domain) = SHA256(UTF8(seed + U+0000 + domain))`.
Quantity: first eight digest bytes interpreted big-endian, modulo 20, plus 11.
Domains are `quantity/<family-index>`. Semantic IDs use the first 16 hex digits of
`semantic/<spec-id>`. Each opaque ID is `z` plus the first 16 hex digits of
`opaque/<case-id>/<A-or-B>/<canonical-id>`. Model seed is the first four bytes of
`model-seed`, big-endian, masked with `0x7fffffff`: **417351046**.
Render IDs use the first 20 hex digits of `render/<case-id>/<label>/<order>`.
The fixed future schedule sorts render IDs by `derive(seed,'schedule/'+render-id)`.
No random-library behavior, output-based seed search or accepted-seed filtering.

Every world has A/B opaque mappings crossed with order 1/2: exactly 80 requests.
Map component, action, source, configuration, entity, operation, attempt, event,
system, evidence and version IDs; preserve numerical values, contracts and explicit
chronology. For each list of components, versions or records, order 1 sorts by
`derive(seed,'order/'+case-id+'/'+canonical-id)`; order 2 reverses. Thus the order
factor is independent of label mapping. Top-level keys similarly sort by
`sections/<case-id>/<key>` and reverse. Do not reorder chronological event entries
or readings within records. Roundtrip tests reconstruct the same world from every
rendering. Meaningful property names and domain names remain visible.

`renderer.anti_coaching` rejects known gold/mutation/family keys, implementation
comment keys, classification labels within case evidence, loaded defect words,
canonical aliases, Horus/model/action names and standalone historical S/E labels.
The generic definitions/schema legitimately contain classification enums; no case
contains its expected enum. Tests compare every payload's SYSTEM_RECORDS with the
allowlisted rendered object, confirm prompt identity, and reject gold-bearing
objects. Lexical checks cannot prove absence of every unintended cue; structural
blinding and exact payload review provide the complementary boundary.

Gold, maps, manifests and generator source are published for reproducibility but
are **never included in a request**. This is model-input blinding, not blinding the
benchmark author or hiding publicly reconstructible answers. Future sessions must
have no repository/filesystem/web/tools or conversational history. Public release
allows later contamination and limits use as a long-lived secret evaluation.

## Interface and raw scoring

`protocol.json` contains the only system/user prompts. `diagnostic-schema.json`
is strict, disallows extra properties, and requires classification, affected IDs,
evidence IDs, observed/inferred/unknown, statement, mechanism, alternative and
falsifier. No solution, modification or experiment proposal is requested. There is
one native first final-channel string per fresh context. Save that string verbatim;
transport/private reasoning is never input to `scorer.py`. The scorer has no file,
network or model access and rejects response envelopes in place of raw strings.
Do not select a better candidate, strip fences, fix JSON, retry, route to a critic,
or let a human auditor repair class, IDs, evidence or localization.

JSON duplicate keys, non-JSON numbers, extra fields, malformed objects or wrong
field types count as wrong. Evidence and component IDs must exist in the correct
category. Unknown opaque IDs even in prose invalidate that rendering; detected
invented IDs additionally trip the conservative global zero-invention gate.
Schema-invalid answers still count as current-defect false positives when their
parsed classification says SUPPORTED_CURRENT_DEFECT. Malformed strings with no
parseable class are wrong and inconsistent, not credited as correct abstention.

Classification credit requires valid schema, valid IDs and exact gold class.
Semantic credit requires at least three of four correct renderings. Evidence
credit additionally requires the frozen minimal set: contract/deployment/current
input/output for ordinary cases, both traces for historical, and contradiction
witness/capture contract for invalid. Semantic evidence credit also requires 3/4.

Localization credit requires correct classification, exact responsible component,
contract/cause/effect evidence links, all those citations, and the decisive field's
observed and contract-required values. The field is a JSON pointer relative to the
specified evidence record's `data`. For the six families the decisive violations
are respectively used_config (or the equivalent returned_value), final_decision,
record_owner, attempt_total_after, posted_units, and command_issued. Gold values
are mechanically derived. Thus mere generic input/output citations or plausible
prose cannot earn mechanism credit. This is a **structured mechanism-family proxy**,
not a scored natural-language causal explanation. Prose, alternative explanations,
falsifiers and their quality are preserved for secondary review but unscored;
contradictions in prose cannot improve primary scores. No semantic auditor is part
of the primary metric. Exact witness requirements can under-credit alternative
valid explanations; the configuration/output equivalence is explicitly accepted.

Representation consistency requires four schema/ID-valid outputs with identical
classes, even if consistently wrong. Report all 80 raw scores, 20 semantic rows,
six pair results, accuracy for each label mapping (40 each) and order (40 each),
and label/order disagreements (40 paired contrasts each). No independence claim.

## Mandatory gates and result taxonomy

All gates must pass; none may be loosened after Freeze 1:

- At least 17/20 semantic classifications correct (3/4 rule).
- At least 5/6 current defects classified correctly; at least 4/6 localized by
  the structured mechanism test, each with at least 3/4 correct renderings.
- All 4/4 healthy controls avoid current-defect classification, with **zero**
  current-defect false positives among their 16 renderings.
- All 3/3 historical controls avoid current-defect classification, with **zero**
  current-defect false positives among their 12 renderings.
- At least 3/4 insufficient-evidence worlds classified correctly.
- All 3/3 invalid-evidence worlds classified correctly.
- At least 5/6 matched pairs correct in the specified direction.
- At least 16/20 worlds classification-consistent across all four renderings.
- Additional conservative gate: at least 17/20 worlds evidence-grounded (3/4).
- Additional conservative gate: zero renderings containing detected invented IDs.

Only all-gates success yields BLIND_DIAGNOSTIC_CAPABILITY_SUPPORTED_V0. Any gate
failure yields BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0. A validity-destroying
breach yields INVALID_STUDY regardless of scores. **This zero-inference phase has
no measured capability result**, only FROZEN_ZERO_INFERENCE_AWAITING_SEPARATE_APPROVAL.
Synthetic perfect-answer fixtures validate software, never scientific capability.

## Prospective model/runtime freeze

Use the exact Qwen3-14B Q4_K_M artifact and llama.cpp b11242 family verified in the
parent study. `model-runtime.json` records full model/archive/server SHA-256 values
and llama.cpp commit `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`.
The inherited parent verification is explicitly marked as such; runtime bytes must
be rechecked before a separately authorized campaign. No server is started now.

Context 16384; native separated deepseek-format reasoning, budget 512; temperature
0.2, top-p 0.9, top-k 40, min-p 0.05; fixed seed 417351046; maximum generated tokens
2048 including reasoning/final; one isolated localhost slot, fresh context for each
call, no KV/cache reuse, tools, filesystem or web. Future 80 calls exactly, one per
frozen scheduled rendering. No runtime substitution, fallback model or retry.
Server grammar uses the frozen JSON schema; the raw first answer still must pass
schema validation. Server-side schema support is inherited, not empirically tested
by invoking a server during this task. The method reserves prompt UTF-8 bytes plus
schema bytes plus 2048 generation tokens plus 512 template tokens against 16384,
a conservative byte-token bound for the frozen byte-BPE family without tokenizing
through a server. An actual compatibility/context failure later invalidates and
stops this frozen campaign instead of justifying prompt/budget changes.

## Preservation and interpretation limits

`preservation-baseline.json` hashes every parent-tracked file and protected public
heads. Verification checks these bytes/refs, exact method bytes at Method Freeze,
all materialized hashes, deterministic regeneration and private-archive exclusion.
No active source imports/execution, authenticated receipts, Memory writes, training,
policy/threshold/model changes or proposals. Parent study results and promoted
S+E architecture remain untouched. Only this branch is published, after unchanged
repository secret-hygiene checks of every reachable public commit/path/blob.

The study is finite, small, synthetic and contract-explicit. Reused templates and
matched pairs make observations correlated. The author knows gold and constructed
the tests; model-input blinding is not independent benchmark authorship. Obvious
UNKNOWN/checksum cues are evidence deliberately needed to solve those tasks, but
can make some classes easier. Uniform record shapes reduce gratuitous cues without
removing semantics. A pass supports only this frozen bounded measurement; it does
not establish broad real-world diagnosis, causal prose competence, autonomous
improvement, or permission to change the incumbent.
