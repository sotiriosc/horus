# Horus v0.4 learning stability

V0.4 adds historical retention checks to the existing bounded consequence-model
learning lifecycle. Generation 2 begins ACTIVE. Receipt authority, explicit
Memory, mechanical Explorer, Mixtral next-state prediction, candidate isolation,
and atomic selection remain unchanged.

## Frozen external regime

The machine-readable definition is `horus/regime_config.json`. Regime A is the
stationary world used through generation 2. Regime B keeps every state
transition unchanged and prospectively changes only two realized consequences:

| Pre-state | Action | Regime A | Regime B |
|---:|---|---:|---:|
| 1 | ADVANCE | -1 | +1 |
| 1 | HOLD | +1 | -1 |

Receipts report whichever deterministic external consequence actually occurred.
The framework does not rewrite prior observations. The regime version is an
audit field on the event and receipt-linked training record, with
`regime_model_visible=false`; it is never added to the consequence prompt.

The fixed 60-authorized-receipt schedule begins with a bridge session: three Regime-A
decisions, an explicit process restart and prospective A-to-B transition, then
three Regime-B decisions. Nine additional six-step sessions run in B. The
schedule therefore contains 3 A and 57 B authorized events. Each session has a
recovery-amendment bound of 12 attempted decisions, frozen before resumption,
so a fail-closed model
abstention cannot be reinterpreted as experience. A later decision may fill the
fixed receipt target, but collection cannot extend based on realized outcomes
or predictive performance.

The original collection implementation incorrectly initialized a new empty
Regime-B session as Regime A. It stopped after five authorized bridge records
and one fail-closed abstention, before training or evaluation. The retained
records are not repeated. `HORUS_V0_4_RECOVERY_AMENDMENT.md` records the exact
failure and the bounded continuation rule.

## Evaluation bank

`evaluation-bank/current.json` points to an immutable, hash-addressed bank
version. Each version binds its ordered examples, parent version, class and
batch distributions, and content hash. New versions append examples; old
versions remain present.

The initial bank uses only prior heldout evaluation examples whose usage maps
prove no optimizer exposure:

- 12 v0.2 heldout examples; and
- 12 v0.3 heldout examples.

Prior training examples are excluded because ancestor adapters optimized them.
Prior validation examples are conservatively excluded because validation loss
was inspected during training, even though they did not enter backpropagation.
No replacement labels are manufactured.

Every bank row retains stable example and receipt identity, source dataset,
originating generation/runtime, input-context hash, consequence class, batch,
hidden regime version, model-visibility status, and first eligible generation.

## Three frozen evaluations

Every candidate is reloaded from disk and compared with the unchanged incumbent
on three separate datasets:

1. **Fresh:** the newest session-separated heldout examples.
2. **Historical:** the untouched bank version frozen before candidate training.
3. **Combined:** the exact union of fresh heldout and historical bank examples.

Reports preserve consequence class, source batch, early/middle/recent historical
window, regime, and prediction transitions. A forgetting event is exactly an
example the incumbent predicted correctly and the candidate predicts wrongly.

## Frozen stability rule

`horus/stability_promotion_rule.json` is frozen before generation-3 inference.
A candidate becomes ACTIVE only if all conditions pass:

- fresh correct predictions increase by at least one;
- historical correct predictions decrease by no more than one;
- historical forgetting events are at most one;
- a historical consequence class with at least four examples does not lose
  more than 0.25 absolute accuracy;
- combined correct predictions do not decrease;
- invalid responses do not increase on fresh, historical, or combined sets;
- fresh has at least 12 and historical has at least 24 examples; and
- provenance, artifact, optimizer-separation, and fresh-reload checks pass.

Training loss has no selection authority.

## One conditional correction

Generation 3 is always a pure continuation from ACTIVE generation 2 using only
the new 42-example training split. If and only if it is rejected specifically
for historical forgetting, one candidate labelled `3R` is permitted. The
integer registry represents it as the next candidate generation while recording
`candidate_label=3R` and parent generation 2.

The deterministic rehearsal set contains exactly 12 OLD TRAINING examples:
the two lexicographically first authenticated example IDs for each consequence
class from generation-1 and generation-2 training splits. Evaluation-bank rows
are structurally excluded. Generation 3R trains on 42 new plus 12 rehearsal
examples, so new experience remains dominant. It uses the same LoRA and
optimizer configuration and the same untouched fresh, historical, and combined
evaluations. No other correction is allowed.

## Commands

Create a private stability registry from the checked-in generation-2 registry:

```sh
python -m horus.learn init-stability \
  --registry /safe/private/horus-stability-models
```

Collect the fixed hidden-regime batch:

```sh
python -m horus.learn collect-regime-shift \
  --registry /safe/private/horus-stability-models \
  --session-root /safe/private/horus-regime-b-sessions \
  --target 60
```

Run one stability cycle:

```sh
python -m horus.learn stability-cycle \
  --registry /safe/private/horus-stability-models \
  --session-root /safe/private/horus-regime-b-sessions
```

Inspect generations and the current bank:

```sh
python -m horus.learn history \
  --registry /safe/private/horus-stability-models
```

The stability-cycle command creates generation 3 and at most the one conditional
3R candidate. It does not collect another batch or start a later generation.

## Endurance and restart evidence

The collector records early, middle, late, and worst rolling-10 windows with
consequence accuracy, invalid rate, action distribution, and realized outcome
distribution. It separately reports the three decisions immediately before the
shift and first six after it.

The bridge restart must retain all first-runtime A records, create a fresh
runtime/source identity for B, and place legitimate A history values into later
requests without regime labels. Contradictory authenticated consequences remain
chronological records; neither side overwrites the other.

This tests bounded adaptation and stability in one finite simulator. It does not
add regime detection, change-point inference, online SGD, Explorer learning,
next-state learning, distillation, EWC, or autonomous generation scheduling.
