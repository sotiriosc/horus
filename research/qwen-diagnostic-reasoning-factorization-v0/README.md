# Diagnostic Reasoning Factorization v0

Base: `98acb89c75a4ecd2a05463fa46bddead0c60c316`. Method Freeze: `e1c5932870a074ec24a5d58ff69994125676a33a`.

Twenty fresh worlds each receive four independent calls: O operational computation, S evidence-state reasoning, R epistemic reduction, E end-to-end diagnosis. Method, exact operands/facts and schemas are frozen in method.md, case-spec.json and schemas.json. Each diagnostic class has four worlds; there are ten operation families with two worlds each. These are correlated, internally authored synthetic tasks, not external/open-world tests.

The 262 materialized files contain twenty raw worlds, eighty arm-specific fixtures, eighty neutral message/schema tasks, eighty exact runtime requests, offline gold/proofs and schedule. No arm receives a previous model response. S sees raw evidence plus independently supplied mechanical values. R is directly authored from frozen lower-level facts, with no opaque IDs or verdict flags; it is not produced by S output, a raw-evidence parser or the existing compiler. E receives unprocessed authored raw evidence. Model-visible fixture functions never receive the gold class. Deterministic software creates/verifies fixtures and scores responses; it never chooses a scientific model answer.

verify.py separately implements each operation, joins raw evidence, verifies R/state alignment while preserving operand order, checks gold, audits all preserved diagnostic/analysis/compiler fixtures and verifies exact regeneration and schedule balance. qualification.json records 40 zero-model tests. The pinned grammar may not enforce all uniqueItems constraints; Python Draft7 is authoritative. The independent S test includes structured-output burden, so failure alone cannot identify an internal cognitive cause.

After Case Freeze run exactly once with `python research/qwen-diagnostic-reasoning-factorization-v0/run_campaign.py --case-freeze <SHA>`. The runner imports no verifier, scorer or gold. It dispatches only exact frozen request bytes. Preserve private envelopes/reasoning, public safe first finals and hashes; commit raw evidence BEFORE score.py. Replay scoring without inference. Any runtime/transport failure or discovered generator defect stops INVALID_STUDY, no retries/restarts or adaptive repairs.

No compiler use, comparator, stage chaining, training, Horus/Memory/policy/architecture modification or improvement proposal. Combined-system capability is not tested. Publish only this audited branch, verify its remote head, then stop without intervention design.
