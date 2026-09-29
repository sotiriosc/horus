# Canonical compact action view — proposal only

The approved controlled-pairing canonical projection already removes opaque receipt identity and hash fields from the model view while retaining grounded decision semantics. The frozen action system message was kept unchanged for this comparison. A public-safe C:D05 decision from the completed grounded-authority result supplies state, allowed actions, every semantic assessment field, and the three bounded prior decisions in the exact current canonical projection shape. No private raw call or receipt is used.

A candidate human-readable rendering of those same public-safe values is:

    Goal: Maximize useful realized consequence over the run using the evidence available to you.
    Decision C:D05; index 5; state 0.
    Allowed: ADVANCE, HOLD, RETREAT.
    Grounded assessments:
    ADVANCE: 0:ADVANCE; DETERMINISTIC; UNSEEN; status=UNSEEN; observations=0; established=none; candidate=none; candidate_count=0.
    HOLD: 0:HOLD; DETERMINISTIC; ESTABLISHED; status=GROUNDED; observations=1; established=next=0,consequence=0; candidate=none; candidate_count=0.
    RETREAT: 0:RETREAT; DETERMINISTIC; UNSEEN; status=UNSEEN; observations=0; established=none; candidate=none; candidate_count=0.
    Recent authenticated decision context:
    C:D02: state=2, action=ADVANCE, consequence=1, source=MODEL_FOR_UNSEEN.
    C:D03: state=3, action=ADVANCE, consequence=-1, source=MODEL_FOR_UNSEEN.
    C:D04: state=0, action=HOLD, consequence=0, source=MODEL_FOR_UNSEEN.
    Return only one selected_action from Allowed.

The renderer in benchmark_compact.py maps every field present in the canonical projection: goal, decision identity/index, current state, allowed actions, relation identity/type/kind/status/count, deterministic established and candidate values/counts or empirical segment/frequency/window/change fields, and bounded recent decision source and authenticated consequence. It relies on the already approved exclusion of only recent receipt provenance from the canonical model view. The example above contains no empirical or unresolved relation, but the renderer has branches for those fields. This is a proposed serialization, not a deployed interface.

| Public-safe view with the unchanged frozen action system | Rendered input tokens by the local historical tokenizer |
| --- | ---: |
| Canonical JSON projection for public C:D05 | 550 |
| Candidate compact rendering of the same projection | 448 |

The candidate removes 102 rendered tokens, or 18.5%, for this one example. The count uses the local runner /tokenize endpoint without generation; it is not an Ollama prompt_eval_count from a model call. Calibration against the separately measured synthetic B3 shape differed by about one token. There is no measured compact-prompt latency or behavioral result. A shorter textual rendering can change model choices even if its listed fields are semantically aligned; equivalence needs a separate matched scientific validation before active use. The promoted incumbent continues to use the frozen canonical view and prompt.
