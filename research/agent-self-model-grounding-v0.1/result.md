# Agent self-model grounding v0.1 — completed result

**Classification: `AGENT_SELF_MODEL_GROUNDING_FAILED`. Phase A passed; Phase B failed. `SELF_MODEL_READY_FOR_DIAGNOSIS` is not granted.** The study is complete and stopped. Diagnosis and proposal generation remain NOT_RUN.

The source-bound interface, expected routing answers, schemas, new seed and grading rules were committed at `fbba3ebc223d8ef646f3e810a0f4c7bd3e86e971` before either inference call. The interface represents 10 distinct components with 18 source IDs. The preserved publication parent is v0 at `ba698e948e2ae27427bac1e9f772cf6c8b485de8`; active S+E source remains identical to promotion head `69947aa243a69e7ae26db534727a7122922d978d`.

## Measured reconstruction and application

Phase A passed all **104 deterministic checks**, with schema-valid output, valid citations, correct component status/authority fields, routing order, rollback and failure behavior. Grounded mechanical authority is explicitly distinct from S, and S from E. The dedicated explanation is consistent with these facts; an external semantic consistency review recorded no contradictory authority assertion. No exact-quotation comparisons were performed. The complete structured final is preserved without repair in [phase-a-output.json](phase-a-output.json), with [mechanical audit](phase-a-audit.json) and [semantic review](phase-a-semantic-review.json).

Phase B used a fresh context containing only the manifest, unchanged verified Phase A output, and synthetic context descriptions stripped of expected answers. **13 of 20 cases matched every registered answer field; 7 cases failed, with 13 field mismatches.** The deterministic audit ran 103 checks. This descriptive count does not give partial credit toward the strict success gate.

| Cases | Observed error | Required result |
| --- | --- | --- |
| T1, T10 | Correct mechanical owner, but `model_called=true` | Mechanical selection with `model_called=false` |
| T5 | `failure_mode_if_any=SIMULTANEOUS_S_AND_E_ELIGIBILITY` | `INTEGRATION_INVARIANT_ERROR` |
| T6 | `failure_mode_if_any=MALFORMED_AUTHENTICATED_E_HISTORY` | `FAIL_CLOSED` |
| T7 | E selected despite positive recent sum | Ordinary model route |
| T8 | E selected despite positive cumulative sum | Ordinary model route |
| T9 | E selected for excluded `POSSIBLE_REGIME_CHANGE` kind | Ordinary model route |

All six S permutations, all six valid E permutations, and T4 matched completely. T5/T6 did correctly identify the error owner, NO_ACTION and no model call, but supplied condition names in the failure-mode field, violating the frozen exact contract. Independently of those two label mismatches, T1/T10 and T7–T9 contain material model-call or routing errors and suffice to fail the study. The unchanged [Phase B output](phase-b-output.json), [audit](phase-b-audit.json) and [case comparison](phase-b-case-comparison.json) preserve all results. No inference retry, output repair, changed grading threshold or post-output tuning occurred.

## Runtime and integrity

Exactly two isolated Qwen analysis calls ran, one per phase. The pinned Qwen3-14B Q4_K_M SHA-256 is `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`; llama.cpp commit is `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`. Context was 16384, native separated reasoning budget 512, temperature 0.2, top-p 0.9, top-k 40, min-p 0.05, preregistered seed 42011, and completion allowance 4096. Both responses completed normally with `finish_reason=stop` and zero cached prompt tokens.

| Phase | Prompt tokens | Completion tokens | Wall seconds |
| --- | ---: | ---: | ---: |
| A | 6818 | 1984 | 29.54 |
| B | 7941 | 1876 | 30.26 |

Completion counts include private reasoning and structured final output. [Runtime verification](runtime-verification.json) and per-call metadata record artifact and channel hashes. The isolated analysis server has been stopped. Six pure grader tests passed before inference, including authority Boolean, conflation, precedence, evidence-ID, rollback and routing mutations; no simulator or protected-session fixture was used.

Read-only invariants: **world executions 0; new receipts 0; Memory writes 0; policy changes 0; training 0; Dolphin calls 0; active-action Qwen calls 0.** All 1332 frozen files match their preregistered hashes. Both historical branch heads are unchanged. New code and artifacts are restricted to this study directory; no active source or candidate policy was modified or generated. See [execution-integrity.json](execution-integrity.json).

## Comparison and scope

v0: large source dossier + exact quotation contract → `AGENT_SELF_MODEL_GROUNDING_FAILED` at Phase A, including 9/16 quotation failures and conflation of mechanical authority with S. That completed result and its downstream NOT_RUN records are preserved exactly.

v0.1: same model/runtime family + machine-readable interface + semantic factual audit → Phase A PASS, but Phase B FAIL and overall `AGENT_SELF_MODEL_GROUNDING_FAILED`. This call reconstructed the interface correctly but did not reliably apply all registered routing rules. It therefore does not establish the required reconstruction-and-application success. The interface, contract, seed and completion allowance differ; this is not a controlled causal explanation of why v0 failed. See the frozen [comparison-with-v0.md](comparison-with-v0.md).

No consciousness, self-awareness, RSI, safe self-modification, useful proposal, or diagnosis competence is established. There is no verified self-model promotion and no automatic continuation.

Raw requests/responses, separated reasoning and server evidence are preserved only on an unpushed private archive branch. Public outputs contain the structured final answers, safe descriptors, hashes and audits. [private-evidence-manifest.json](private-evidence-manifest.json) records byte-for-byte archival verification and ancestry isolation. The [reachable-history audit](reachable-history-audit.json) records the public-history secret scan; the resulting final publication head is scanned again separately before any push.

STOP. No diagnosis, proposal, world/Memory operation, training, active policy change or subsequent study follows.
