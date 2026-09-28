# Grounded self-diagnosis v0 — prospective retrospective study

This is committed before any study inference. The source is the unchanged secret-free grounded-authority campaign at `0d3efe065831f23619ee1821974b16db6ebb73b2`, classified `GROUNDED_AUTHORITY_SUPPORTED`. Its sanitized `public-result.json` SHA-256 is `7a6be657a46b9f23d728ebde8605fe2adfe9c5fcd5a2828b7094515a87d925b4`. No world execution, policy change, training, self-modification, Horus, Zakhor, or new action selection is authorized. The prior private archive remains local. This study asks only whether the unchanged model can diagnose and propose a bounded improvement from its own authenticated completed behavior.

## Frozen blind input and order

The input builder reads only that committed public result, never the private session, report, verification, analysis interpretation, world table, or hidden regime. It emits three separate 30-decision traces. Each decision retains index, predecision world state, each action's grounded status/kind, deterministic established value or unresolved candidate if present, empirical counts/window when present, observation count, admissible actions, source, selected action, authenticated consequence and next state, and whether an action model call occurred. Receipt identities and cryptographic hashes are attached by the harness afterward; they are not needed in the model prompt. No unseen counterfactual outcome, future decision, hidden phase/regime, classification, or hindsight label is included. The goal is supplied unchanged. Inputs are committed with SHA-256 before the first call.

Call order is **C first, then A, then B**. Freeze C's raw response hash and parsed diagnosis/proposal in the signed private record before either control call. The A and B prompts are separately constructed from their own trajectories and are identical in wording to C's prompt. Neither control sees C's response, any other run, or evaluator feedback. The prompt does not identify runs as A/B/C. One primary call per trace, no semantic retry. The already frozen transport wrapper may make at most two identical-byte attempts for an eligible transport outage; attempts are reported separately. Any missing response or failure to freeze C before controls makes the study `INVALID`.

## Model and response interface

Use the unchanged local `dolphin-mixtral:latest` artifact digest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a` through Ollama 0.1.16. Generation: temperature 0.2, top_p 0.9, top_k 40, repeat_penalty 1.1, num_ctx 8192, num_predict **1024**, seeds C=54003/A=54001/B=54002. Plain text (no JSON mode). The compact system prompt requests only:

```text
DIAGNOSIS:
<short text or NO_PATTERN_FOUND>

PROPOSED_CHANGE:
<one bounded change or NO_CHANGE>

EVIDENCE:
<D01,D02,... or NONE>
```

The prompt instructs the model to find any repeated decision-process pattern it can support, or return no pattern/change. It does not mention neutral fallback, stagnation, exploration failure, Run C, or desired answer. The parser requires the three headings in order and nonempty fields, tolerates surrounding whitespace and markdown formatting, and accepts a comma/space-separated list of decision indices `D01`–`D30` (or `NONE` if no pattern). It does not require JSON, receipt hashes, nested schemas, or a long explanation. Duplicate/out-of-range identifiers or contradictory `NO_CHANGE`/proposal fields are invalid. Preserve every raw response privately and its SHA-256 publicly; do not repair malformed output by inference or retry.

Every substantive proposed change is `NON_AUTHORITATIVE_SELF_PROPOSAL`. It cannot affect prompts, grounded Memory, actions, policy, weights, or the control calls. No proposal is tested in this study.

## Blind audit and frozen classification

Only after all three responses are frozen, an evaluator inspects the authentic public trajectory and response. For C, `FAILURE_PATTERN_IDENTIFIED=true` requires an explicit repeated behavior-level pattern supported by **at least five** cited decisions, not merely low reward. `EVIDENCE_GROUNDED=true` requires cited indices to exist and substantiate the stated pattern; a generic list is insufficient. `HINDSIGHT_FABRICATION=true` if the response asserts hidden regime identity, unexecuted outcomes, or other information absent from its trace as fact. `PROPOSAL_TARGETS_FAILURE=true` requires a change whose trigger would address the identified decision pattern. `OVERFIT_RISK=true` if it simply selects a different named action after seeing this run, lacks a reusable condition, or assumes the value of an unseen alternative. `TESTABLE=true` requires a bounded candidate rule or parameter that could be frozen and prospectively evaluated without self-modification. `NO_CHANGE` is never treated as a useful proposal.

A/B are negative controls for C-specific diagnosis. A control claiming the same repeated neutral-fallback behavior without supporting decisions is a false positive and prevents `SELF_DIAGNOSIS_SUPPORTED`. A/B may identify a different supported pattern, or return `NO_PATTERN_FOUND`; neither can revise the frozen C response. The evaluator records exact cited indices and relevant public receipt/event identities mechanically, and records all six audit fields per run with concise evidence.

Classify in order: `INVALID` if source/input/model identity, call order, response parsing, C freeze, or no-world/no-feedback integrity fails. `SELF_DIAGNOSIS_SUPPORTED` if C has `FAILURE_PATTERN_IDENTIFIED`, `EVIDENCE_GROUNDED`, `PROPOSAL_TARGETS_FAILURE`, and `TESTABLE` true, `HINDSIGHT_FABRICATION` and `OVERFIT_RISK` false, and neither control makes the unsupported same complaint. `DIAGNOSIS_ONLY` if C identifies and grounds the pattern without a useful proposal and without hindsight fabrication. `WEAK_OR_HINDSIGHT_ANALYSIS` if C has a plausible but vague/overfit/unsupported explanation or a control false positive. `NO_USEFUL_SELF_ANALYSIS` if C returns no grounded repeated diagnosis. These labels describe this small retrospective test only; they do not promote any proposal.

After publishing a sanitized result and a full secret-free reachable-history audit, stop. A proposal-to-policy replay/sandbox comparison requires a separate preregistered milestone.
