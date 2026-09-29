# Qwen diagnostic composition and binding v0

Base: `827e568a9de26324990ed837a2f773a20d0ff43e`. Method Freeze: `240f48e62b820259985af89b1138809d42e48534`.

`method.md` and `case-spec.json` prospectively fix ten additive five-level ladders and ten one-fact pairs, separate scoring gates, interpretation, runtime and balanced schedule. Cases are internally authored research-program tasks, not external independent tasks or open-world evidence. Ten mechanism families are new relative to both preserved benchmarks and reused across differently parameterized domains within this study.

`materialized/` contains 70 raw evidence objects, 70 model-neutral message/schema tasks, 70 exact Qwen payloads, author gold/proofs, schedule and structural specifications. Offline canonical comparison is only for auditing; model-visible evidence is authored directly without the evidence compiler or other preprocessing. `verify.py` independently evaluates operational requirements, confirms genuine UNKNOWN alternatives, exact single-leaf counterfactual deltas and additive-only ladders, and audits prior-case non-reuse and prompt leakage. `preflight.json` records these checks and all 213 materialized file hashes.

`transport.py` and `run_campaign.py` adapt the qualified one-shot runner to 70 calls. The runner reads no gold/proof/scorer. `qualification.json` records 36 zero-model tests. `score.py` requires a committed raw freeze, then extracts selected final classes and computes separate H1/H2 results. No private reasoning is scored. Model-neutral tasks are preserved for a future separately authorized comparator; no comparator is executed here.

After Case Freeze execute once with `python research/qwen-diagnostic-composition-binding-v0/run_campaign.py --case-freeze <SHA>`. Any runtime/transport failure or discovered generator defect stops INVALID_STUDY, with no restart. Commit raw final strings, metadata and hashes before scoring. Deterministic score replay makes zero model calls. Publish only this audited branch, verify the remote head and stop without intervention design or Horus changes.
