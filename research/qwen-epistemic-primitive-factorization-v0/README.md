# Qwen Epistemic Primitive Factorization v0

Prospective 28-pair, 56-state, 112-call study of seven separate epistemic primitives and five-class reduction on identical aligned factual states. Base: verified remote publication 2170b160527c41f4084ca6268dcb03a79b8d3641. Method Freeze: 767bf35fb87f77229929468b7af28151057250cc.

method.md, case-spec.json and schemas.json specify the experiment. materialized/ holds frozen states, pairs, offline gold/proofs, neutral messages and exact requests. verify.py independently checks all seven primitive judgments, classes, minimal deltas, coupling, schedule, freshness and leakage. score.py applies the frozen gates and descriptive matched comparisons. Runtime transport is one-shot; raw responses must be committed before scoring.

All model-native reasoning and full envelopes remain outside the repository. No compiler, comparator, Horus action, training or intervention is included. Combined-system capability is not tested.

After execution, report.md and capability-boundary.md provide results; pair-coupling-audit.md documents every paired change, scores.json holds exact endpoint/pair scoring, replay.json records deterministic replay, and publication-audit.json records the reachable-history audit before the final audit-record commit. The final exact-head audit and verified remote SHA are reported in the completion handoff.
