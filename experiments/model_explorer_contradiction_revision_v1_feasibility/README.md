# Contradiction revision v1 — feasibility only

Construct the complete seven-step CONTROL and SHIFT fixtures through the unchanged realized-event grounding repair. No model prompts, parser controls, inference or model runtime startup. Read the [frozen protocol](../../research/model-explorer-contradiction-revision-v1-feasibility-preregistration.md) and [results report](../../research/model-explorer-contradiction-revision-v1-feasibility-results.md).

From the repository root, choose two distinct, previously nonexistent output directories outside the public tree:

```sh
python3 -m experiments.model_explorer_contradiction_revision_v1_feasibility.run --output "$HORUS_FIXTURE_EVIDENCE"
python3 -m experiments.model_explorer_contradiction_revision_v1_feasibility.run --replay "$HORUS_FIXTURE_EVIDENCE" --output "$HORUS_FIXTURE_REPLAY"
```

Standard-library Python only. Each invocation executes 14 primary fixture transactions plus an uninstrumented 14-transaction validation of observer noninterference. A read-only profiling hook records actual returns from original Recovery/quarantine functions; no historical function is replaced or modified. The uninstrumented execution must match all other evidence exactly. Detailed `fixture.json` includes steps, packages, receipts, Memory, six stage snapshots, provenance audits, projections, matching and metadata. Detailed logs remain outside the public tree. `results.json` is compact evidence with source/evidence hashes. Exact replay regenerates both files byte-for-byte.

Source preservation includes 23 historical framework sources and the additional repair/fixture inputs in `frozen-inputs.json`, checked before and after execution. Campaign gate is provisional until exact replay and historical regressions complete; `verification.json` records final classification and actual regression execution. Exit 2 means stop and review a failed new feasibility boundary, with no automatic framework patch.

O1/O2 previews are chronological authorized-Memory data, with epoch/transaction/event IDs, surface actions and observed consequences. Full source provenance is separately audited; no hidden regime label or source-lifetime arm label enters the preview. The experiment's audit archive is never given to the framework or used for authorization. Two external source lifetimes intentionally have different source identities. A/B retain shared receipt ancestry, not independent physical observation.

Historical commands and expected exits are recorded in `verification.json`. The old contradiction-v0 diagnostic must still return 2 and reproduce its original false accept. Repair campaign/replay must pass unchanged. Prior Semantic/Factorial model-study replays use their separately retained historical transcripts; they perform no new inference. Neither private transcripts nor network access are needed for this new fixture.

Success establishes safely constructed contradictory histories in the declared software trust root. It does not establish model revision, adaptation, causal understanding or physically verified truth. Stop before any 144-call behavioral campaign.
