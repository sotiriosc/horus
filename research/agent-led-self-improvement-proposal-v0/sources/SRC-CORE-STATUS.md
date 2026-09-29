# Grounded state core v0

This is a source consolidation of completed registered studies, not a new scientific claim. Horus and Zakhor are parked. Their historical code remains in the secret-free source snapshot, but neither is the new core, and neither is being reintroduced as a router, explorer, keeper, planner, or training path.

The supported foundation is: protected external reality → original receipt → Measure/authorization → durable authenticated Memory → exact-relation grounded state → external consumer. A prediction cannot overwrite a grounded fact. The package is named `grounded_state`.

## Layout and API

- `grounded_state.deterministic.fold`: exact copied semantics of the uncertainty study. `UNSEEN`, `ESTABLISHED`, and `UNRESOLVED_CHANGE` retain the first-contradiction and confirmation/rejection rules and every receipt's provenance.
- `grounded_state.empirical.fold`: exact registered four-receipt comparison and six-prior-observation rule from the stochastic study. `EMPIRICALLY_STABLE` means only that the current observed segment contains one observed outcome; `VARIABLE_RELATION` and `POSSIBLE_REGIME_CHANGE` preserve frequencies and uncertainty. It is not a probability model.
- `RelationKey(pre_state, action)`: exact relation identity. `RelationType.DETERMINISTIC` or `.EMPIRICAL` is required explicitly. No automatic type discovery occurs.
- `AuthenticatedMemory(store, memory)`: adapter to the existing signed `SessionStore` and `ModernMemory`. `append(current_event_envelope, context_identifier)` admits only the current authenticated publication through the unchanged `ModernMemory.record` check. `rows` reconciles durable evidence before deriving. The core does not mint receipts or replace authorization.
- `derive_relation_state(memory, relation_key, relation_type)`: returns an immutable `DerivedRelationState` with a frozen evidence snapshot and `ReceiptProvenance` tuples containing the exact event identity, receipt SHA-256, stream sequence, and realized value. No unsupported receipt is invented. Accessors return copies.
- `assess_relation(relation_key, state, optional_model_generalization)`: returns `UNSEEN`, `GROUNDED`, or `UNRESOLVED`. It carries a supplied model proposal only when the relation is `UNSEEN`; it neither calls a model nor grants model authority. Deterministic contradictions and empirical possible changes stay unresolved. Empirical grounded means observed evidence exists, not that the relation is certain.
- `deterministic_action_labels(state, application_semantics)`: separate, optional decision-label helper. An application must supply an acceptable consequence minimum and a consequence ceiling. The helper returns `action_justified` and `optimality_established` only for established deterministic states and rejects empirical states. It does not choose actions or generalize H_SAFE to variable outcomes.

A typical caller records the original protected receipt through its existing event stream, admits it via `AuthenticatedMemory.append`, then calls `derive_relation_state` and `assess_relation`. The model-facing consumer can supply a proposal for `UNSEEN`; the proposal remains outside the receipt-derived state and authorization chain. A relation with no explicit type fails clearly.

## Evidence and limits

The zero-inference [regression verdict](regression.json) checks the stored classifications and replay verdicts of the grounded uncertainty, hybrid, and safe-fallback studies; their first-contradiction, model-to-grounded handoff, false-certainty, and justified-versus-optimal results; and semantic replay of all 432 sanitized stochastic receipt summaries. Every new deterministic and empirical fold agrees with its frozen predecessor before and after each public stochastic event. The local archival branches retain the complete signed raw records for full HMAC replay. The public root contains cryptographic hashes and summaries, so its replay validates recorded semantics and source equality but cannot independently authenticate the omitted raw sessions.

The empirical rule is supported only on the registered traces. A long stationary process can produce a chance run of four uncommon outcomes, and a subtle shift might not produce such a run. Exact relation type is configured, never inferred. Application-specific safety guarantees and model generalization quality remain separate research boundaries. No live inference, training, controller change, or new decision policy was performed here.
