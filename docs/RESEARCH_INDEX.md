# Research and evidence index

This is navigation, not a new experimental result. Audited 2026-09-29 against
`main` at `c214511531396312c9214387541cf3e3f277c940` and the public branch heads
listed below. Relative links refer to files present on that `main` snapshot;
research-only links pin published commits. No research implementation was moved
onto `main` for the README refresh.

For each study, read its preregistration before its result, then inspect the
source manifest, compact outcomes and verification/replay artifacts. A newer
supported result does not relabel an earlier failed gate. “Promoted” denotes an
external architecture decision on the named lineage, not a merge or a universal
performance claim.

## Default-branch history

The original [development sequence](../research/DEVELOPMENT_HISTORY.md) and
[checkpoint catalogue](../research/CHECKPOINTS.md) cover hardware through the
bounded base frameworks. The [previous README at the audited main commit](https://github.com/sotiriosc/horus/blob/c214511531396312c9214387541cf3e3f277c940/README.md)
retains the complete earlier experiment-by-experiment narrative. All original
reports remain in [research/](../research/).

| Phase | Read first | Interpretation to retain |
| --- | --- | --- |
| Hardware, local repair and independent authorization | [Checkpoint catalogue](../research/CHECKPOINTS.md), [authorization results](../research/bounded-independent-authorization-results.md), [hardware mapping](HARDWARE_FRAMEWORK_MAPPING.md) | Protected-source checks passed within their fault model. Correlated evidence and common-mode trust-root failures remain visible. |
| Explorer / Map / Measure / Memory / Recovery | [v0](../research/base-framework-v0-results.md), [v1](../research/base-framework-v1-results.md), [v2](../research/base-framework-v2-results.md) | Historical bounded architectures; later grounded work does not inherit their stationary-law authority. |
| Model proposals, labels and evidence | [Explorer integration](../research/model-explorer-integration-v0-results.md), [Memory study](../research/model-explorer-memory-study-v1-results.md), [semantic priors](../research/model-explorer-semantic-prior-study-v0-results.md), [factorial study](../research/model-explorer-prior-factorial-v1-results.md) | Integrity and model usefulness are separate. Action labels/order are experimental variables. |
| Realized-event authority | [Realized-event repair](../research/realized-event-grounding-v0-results.md), [status-bound authorization](../research/state-recovery-authorizer-status-binding-v1-results.md) | Original executed receipts replace prediction/law agreement as the grounding source; trusted-root limits persist. |
| Contradiction and revision | [Explorer v1](../research/model-explorer-contradiction-revision-v1-results.md), [Map v0](../research/model-map-proposal-v0-results.md), [established-prior Map v1](../research/model-map-established-prior-revision-v1-results.md) | Earlier NOT ESTABLISHED results remain unchanged; later bounded Map revision replicated. |
| Role composition | [Original interrupted v2](../research/model-proposal-role-composition-v2-results.md), [independent R1](../research/model-proposal-role-composition-v2-replacement-r1-results.md), [history ablation](../research/composition-map-memory-ablation-v0-results.md) | R1 supports composition integrity; unavailable original live evidence was not pooled or repaired. |
| Cross-episode evidence | [Boundary failure](../research/cross-episode-authenticated-memory-boundary-v0-results.md), [initialization repair](../research/cross-episode-initialization-boundary-v1-results.md), [transfer](../research/cross-episode-model-transfer-v0-results.md), [history depth](../research/cross-episode-map-history-depth-v1-results.md) | Feasibility, scoped repair and behavioral transfer have distinct gates. |
| Stale Memory | [Feasibility](../research/cross-episode-stale-memory-feasibility-v0-results.md), [Map revision](../research/cross-episode-stale-memory-map-revision-v1-results.md), [Explorer revision](../research/cross-episode-stale-memory-explorer-revision-v1-results.md) | Map REPLICATED and Explorer NOT ESTABLISHED; no persistent-weight-learning inference. |
| Forecasting and action comparison | [Temporal negative](../research/map-temporal-relation-forecast-v0-results.md), [decomposition](../research/map-explorer-oracle-decomposition-v0-results.md), [finite comparator](../research/explorer-finite-value-comparator-v0-results.md), [Split Map](../research/split-map-independent-prediction-v0-results.md) | Semantic/predictive and comparison limitations are not hidden by successful parsing. |
| Grounded rebaseline and dated review | [Rebaseline](../research/grounded-lineage-rebaseline-v0-results.md), [claim eligibility](../experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json), [review guide](../REVIEW_GUIDE.md), [executed verification](../review/VERIFICATION.md) | Review/state documents describe their recorded snapshot, not the latest research branch. |
| Runnable system and training | [v0](HORUS_V0.md), [v0.1](HORUS_V0_1_LIVE.md), [v0.2](HORUS_V0_2_GROUNDED_LEARNING.md), [training results](../research/grounded-learning-v0/RESULTS.md) | v0.2's small Qwen2.5 consequence adapter is a real bounded parameter-update result with regressions; it is distinct from Qwen3 substitution. |

## Preserved research branches

The following reports and implementations are **not present on the audited main
snapshot**. The commit in each link is immutable even if a branch later advances.
This is a selected evolutionary path, not a claim that every branch is active.

| Phase | Published branch / commit | Result and boundary |
| --- | --- | --- |
| [Grounded core / parking older Horus and Zakhor][core] | `build/grounded-state-core-v0` · `373b1ec` | Source consolidation of grounded evidence; older architectures parked, retained mechanisms preserved. |
| [Mechanical decision authority][authority] | `research/grounded-authority-autonomous-agent-v0` · `0d3efe0` | GROUNDED_AUTHORITY_SUPPORTED within the registered campaign; distinct from S. |
| [S replication checkpoint][s-replication] | `research/grounded-stagnation-escape-replication-v0` · `fae30db` | COST_OR_SCOPE_BLOCKS_PROMOTION remains the original result. |
| [S eligibility completion][s-eligibility] | `research/grounded-stagnation-escape-eligibility-completion-v0` · `af7b83d` | Later bounded evidence supported PROMOTE_S; prior classifications were not overwritten. |
| [S promotion][s-promotion] | `research/grounded-stagnation-escape-promotion-v0` · `8bc396b` | External approval activates the exact deterministic stagnation rule on this lineage. |
| [Qwen runtime qualification][qwen-runtime] | `engineering/grounded-agent-development-runtime-v0` · `48ac31c` | Engineering qualification; not model promotion or transferred behavior. |
| [Qwen substitution][qwen-substitution] | `research/qwen3-grounded-agent-substitution-v0` · `4e3053c` | QWEN_FAST_BUT_BEHAVIORALLY_UNSUITABLE. Retrospective review structure improved, but citation/authority interpretation had limits. |
| [Invalid bounded-thinking checkpoint][qwen-invalid] | `research/qwen3-bounded-thinking-action-v0` · `fc98de7` | INVALID after unauthorized fixture execution; interface observations do not repair validity. |
| [Read-only semantic gate][qwen-semantic] | `research/qwen3-bounded-thinking-action-v0.1` · `a02af95` | Semantic responsiveness supported only in the registered diagnostic. |
| [R128 autonomous test][qwen-r128] | `research/qwen3-r128-autonomous-grounded-agent-v0` · `40dbe69` | QWEN_R128_STILL_POLICY_LIMITED; no Qwen action promotion. |
| [E replication][e-replication] | `research/empirical-evidence-acquisition-replication-v0` · `f90a844` | EMPIRICAL_EVIDENCE_ACQUISITION_REPLICATED; candidate/control mechanism trials, not an autonomous promoted-incumbent campaign. |
| [E promotion][e-promotion] | `research/empirical-evidence-acquisition-promotion-v0` · `69947aa` | E_PROMOTED, exact S+E routing and rollback preserved; 61 tests before and after, no new scientific campaign. |
| [Self-model v0][self-v0] | `research/agent-led-self-improvement-proposal-v0` · `ba698e9` | AGENT_SELF_MODEL_GROUNDING_FAILED at reconstruction; diagnosis/proposal NOT_RUN. |
| [Self-model v0.1][self-v01] | `research/agent-self-model-grounding-v0.1` · `ecd097a` | Reconstruction PASS, application FAIL; overall AGENT_SELF_MODEL_GROUNDING_FAILED. |
| [Verified-introspection diagnosis][diagnosis] | `research/agent-led-diagnosis-verified-introspection-v0` · `11b32a6` | INSUFFICIENT_CURRENT_EVIDENCE; one bounded gap survived, two candidates rejected; no proposal. |

The [E promotion report][e-promotion] links its diagnosis, frozen proposal,
evaluation, replication, activation tests and source-equivalence checks. The
[S promotion record][s-promotion] preserves its full earlier evidence chain.
The [grounded-core contracts][core] describe the retained uncertainty, hybrid,
safe-fallback and empirical-state lineage. Its narrower findings should not be read as
proof of general adaptation or safety.

## Reproduction and provenance boundaries

- [Baseline commands](REPRODUCIBILITY.md) cover Python/RTL checks and optional
  numerical/synthesis work. [Review verification](../review/VERIFICATION.md)
  records a later isolated installation and core pass; the older installation
  caveat remains historical, not silently rewritten.
- Some preservation checks hash historical README/source bytes. Check out the
  study's recorded commit before running those checks. A documentation refresh
  does not update frozen experiment manifests.
- Later public studies contain safe summaries and hashes; private model traffic,
  signed streams, keys and Memory databases are not download links in this index.
  Public semantic replay cannot independently authenticate omitted raw sessions.
  Legacy raw-evidence locations are intentionally not surfaced here.
- Old `HORUS_STATE.md`, `REVIEW_GUIDE.md` and architecture reports describe their
  own commits. Claims in those snapshots are not automatically current or
  transferred to a different model, interface or authority path.
- Tags `v0.1-horus-baseline` through `v0.5-evidence-provenance-v2` identify early
  hardware/framework checkpoints; they are not release tags for the later S+E
  agent. See the [checkpoint catalogue](../research/CHECKPOINTS.md).

No completed blind-diagnostic generalization study was identified in the audited
public heads. That remains a prospective research question. The latest completed
result is the [bounded evidence-gap diagnosis][diagnosis], not demonstrated RSI.

[core]: https://github.com/sotiriosc/horus/blob/373b1ec5b6269d6d3bb8bd853da2e692800568c3/research/grounded-state-core-v0/architecture.md
[authority]: https://github.com/sotiriosc/horus/blob/0d3efe065831f23619ee1821974b16db6ebb73b2/research/grounded-authority-autonomous-agent-v0/result.md
[s-promotion]: https://github.com/sotiriosc/horus/blob/8bc396b96662ff7fa04b87a7a3300008e12228b9/research/grounded-stagnation-escape-promotion-v0/promotion-record.md
[s-eligibility]: https://github.com/sotiriosc/horus/blob/af7b83dd9c929cf33c1e01d453e4ce86ec1624f4/research/grounded-stagnation-escape-eligibility-completion-v0/result.md
[s-replication]: https://github.com/sotiriosc/horus/blob/fae30db7c60294fd52a9fd57a2797be9bc3ad24a/research/grounded-stagnation-escape-replication-v0/result.md
[e-promotion]: https://github.com/sotiriosc/horus/blob/69947aa243a69e7ae26db534727a7122922d978d/research/empirical-evidence-acquisition-promotion-v0/result.md
[e-replication]: https://github.com/sotiriosc/horus/blob/f90a84444ab320e13db4b1573d454c3d0d7f90d5/research/empirical-evidence-acquisition-replication-v0/result.md
[qwen-runtime]: https://github.com/sotiriosc/horus/blob/48ac31cb3f111c74f1ef2eea77af2d7c26435299/engineering/grounded-agent-development-runtime-v0/qualification.md
[qwen-substitution]: https://github.com/sotiriosc/horus/blob/4e3053c05e6bafb5c3f53b08ce1ceedf0ebb65a3/research/qwen3-grounded-agent-substitution-v0/result.md
[qwen-semantic]: https://github.com/sotiriosc/horus/blob/a02af959d18b69a34cfc20ce87c7feb5e0296471/research/qwen3-bounded-thinking-action-v0.1/result.md
[qwen-r128]: https://github.com/sotiriosc/horus/blob/40dbe69673e9b146888fdbb08c3df713aef6f336/research/qwen3-r128-autonomous-grounded-agent-v0/result.md
[qwen-invalid]: https://github.com/sotiriosc/horus/blob/fc98de7be5df6a20d76c6917ceca96bd2a2e7ded/research/qwen3-bounded-thinking-action-v0/result.md
[self-v0]: https://github.com/sotiriosc/horus/blob/ba698e948e2ae27427bac1e9f772cf6c8b485de8/research/agent-led-self-improvement-proposal-v0/result.md
[self-v01]: https://github.com/sotiriosc/horus/blob/ecd097af2f007cb431e3ae736832960f86805deb/research/agent-self-model-grounding-v0.1/result.md
[diagnosis]: https://github.com/sotiriosc/horus/blob/11b32a6ab54b803f0212ece834a4d7c7c75a23cb/research/agent-led-diagnosis-verified-introspection-v0/result.md
