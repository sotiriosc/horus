# Horus v0.7 grounded exploration R1 failure

## Classification

R1 is permanently classified as **NOT ESTABLISHED — incomplete campaign after
runtime failure**. No scientific conclusion is drawn from its partial behavior.
The campaign was not resumed, truncated, overwritten, or reinterpreted.

R1 used campaign identity `HORUS_GROUNDED_EXPLORATION_V0_R1`, the frozen v0.7
implementation at `72cdc095b9e35fb58e1bc353f1eae5de6c8aad39`, and parent failed
evidence commit `5edc8894fb47709d8c40dd8f3eb2f6c968dfa173`. Its preflight and
reservation were committed at `7cc6494025158d3da58dbf42428259129a19fe77`.

## Preserved partial state

- 14 autonomous decision batches reached prediction and decision freezing.
- 13 decisions completed: 12 authorized executions and one fail-closed model
  abstention.
- The 14th Explorer decision was frozen before execution but never completed.
- Exactly 126 campaign model calls completed: 42 joint next-state, 42 G2, and
  42 G3 calls. One joint call timed out; the other 125 calls parsed.
- The last complete session checkpoint records 13 attempted decisions, 12
  completed steps, transaction 13, state 1, and 351 call-journal envelopes.
- The private call stream additionally preserves the complete nine-call batch
  for frozen decision 14, giving 378 envelopes and 126 calls in total.
- The confidence journal contains 14 frozen and 13 completed decisions. Its
  terminal record is the frozen decision 14.
- The routing journal and realized-event journal each contain 12 authenticated
  records.
- No completion sentinel exists. The process exited with code 1.

The authority keys and raw private model-call stream are excluded from this
public evidence directory. Their byte hashes and authenticated stream heads are
committed in `failure-evidence-manifest.json`.

## Failure

The terminal traceback was:

```text
Traceback (most recent call last):
  File "<worktree>/horus/grounded_exploration.py", line 766, in run_grounded_exploration_segment
    rows = [runtime.execute_autonomous() for _ in range(plan["decisions"])]
  File "<worktree>/horus/grounded_exploration.py", line 606, in execute_autonomous
    if _plain(asdict(pending.prediction)) != _plain(asdict(prediction)):
AttributeError: 'StepResult' object has no attribute 'prediction'
```

Only the local worktree prefix is normalized; frames, lines, expressions, and
the exception are preserved.

The Ollama service was available through the crash. The final three joint
requests immediately preceding the exception returned HTTP 200, including the
last response at 03:51:16 EDT. The Python exception followed before 03:51:17.
The service was terminated separately five minutes later; it did not cause the
exception.

## Runtime diagnosis

`StepResult` is the protected framework's immutable outcome type. It contains
transaction identity, authority status, action, execution/commit/continuation
flags, recovery flags, and a reason. It deliberately contains no prediction.
Successful `begin_step` calls instead return `PendingTransaction`, whose
`prediction` is the pre-execution value latched in the protected core.

At decision 14, the R1 runtime had already completed 12 executions in a single
A1 runtime. The protected framework's unchanged `EPISODE_LIMIT` is 12. Its
receipt-bound wrapper caught the resulting bound exception, failed closed, and
returned a rejected `StepResult` with no pending transaction and continuation
revoked. The exploration runtime assumed every non-abstained Explorer choice
produced a `PendingTransaction` and accessed `.prediction` without checking the
sum type.

The existing deterministic campaign test did not reach this path. Its fixed
model responses produced only 10 authorized A1 executions and eight model
abstentions, so it stayed below the 12-execution bound while still completing
18 decision attempts.

A separate zero-inference boundary reproduction completed 12 authenticated
executions, then confirmed that the next `begin_step` returned `StepResult` with
reason `begin validation failed`, `continued=False`, no `.prediction` member,
and no protected pending transaction. The intended pre-execution `Prediction`
still existed only as a local candidate; it was never accepted or exposed to
execution. This proves that replacing the missing member with post-execution
receipt data would violate the causal boundary rather than repair it.

A local field substitution cannot repair this failure: after the rejected
`StepResult`, there is no pending prediction or authorized pending execution.
Continuing up to 18 executable A1 decisions would require an additional
epoch/runtime rollover or a changed episode bound. Either changes the frozen
lifecycle rather than merely repairing the broken attribute access.

The authorized R2 stop condition therefore applies. No source repair was made,
no R2 identity was reserved, and no R2 model call was issued.

## Verification

- All 74 package-qualified Horus tests passed.
- The documented core regression passed all 53 checks.
- The exact grounded-exploration test module passed all 16 tests.
- Every public partial-evidence copy is byte-identical to its R1 source and
  matches the committed SHA-256 manifest.
- All retained JSON and JSONL records parse.
- The frozen policy, prompts, model configuration, schedule, and source remain
  unchanged from the R1 preregistration.

## Narrowest defensible conclusion

R1 verifies that the persistent joint service could serve real campaign calls
and that 12 receipts entered the protected evidence path. It does not answer
whether autonomous exploration discovers or responds to the changing relation.
The frozen 18-attempt A1 schedule is not robust to more than 12 executable
decisions in one protected runtime under the current bounded framework.
