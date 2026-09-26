# Horus v0.4 learning-stability result

## Decision

Outcome **D** was observed: neither candidate was safe to promote. Pure
generation 3 adapted to the new heldout batch but catastrophically forgot the
historical negative class. The one permitted grounded-rehearsal candidate 3R
recovered two aggregate historical answers but retained the same six
correct-to-wrong events and the same negative-class collapse. Both were
rejected, and generation 2 remains ACTIVE.

This is one bounded result in a small deterministic world. It establishes that
the lifecycle detects and blocks the observed forgetting. It does not show
that the current training or rehearsal strategy can safely combine both
regimes.

## Evaluation bank

Bank version 1 contained the largest prior set with proven heldout status: 12
v0.2 and 12 v0.3 authenticated examples. Its class distribution was six `-1`,
ten `0`, and eight `+1`; manifest SHA-256
`11255c91addfa2c611ca4cbcff64a886b145f1547a6660ae8c3dbfdb32554864`.
The 84 prior training examples were excluded for optimizer exposure, and the
12 prior validation examples were conservatively excluded because validation
influenced training observations. The exclusion ledger names every identity.

Each retained row binds the stable example ID, originating active generation,
authenticated receipt identity (including runtime/source identity, epoch, and
transaction), input-context hash, realized consequence/class, batch/regime,
source split, and first eligible generation. The legacy convenience field
`originating_runtime` is null on imported v0.2/v0.3 rows; their exact runtime
identity remains present in `authenticated_receipt_identity`. No bank identity
entered either candidate optimizer.

After both decisions, the 12 fresh heldout examples were appended as bank
version 2. It has 36 rows, class distribution 8/18/10, and manifest SHA-256
`0b81eb9160ed6bc87f9a58cb88ad4c249810f33decff7943cda0c6dd20e06497`.
Version 1 remains immutable and is the bank actually used for both decisions.

## Controlled regime shift and collection

The simulator-only change preserved transitions and receipt semantics. At
state 1, `ADVANCE` changed from consequence `-1` in A to `+1` in B, while
`HOLD` changed from `+1` to `-1`. The regime identifier was recorded for audit
and never entered a learner prompt.

The fixed target produced 60 authorized receipts: three A and 57 B. There were
61 attempted decisions and one fail-closed abstention. The abstention created
no event or training record. The preserved recovery amendment explains an
empty-session initialization bug and binds the five authorized and six
attempted records that existed before resumption; none was repeated.

| Realized consequence | Count |
|---|---:|
| `-1` | 12 |
| `0` | 36 |
| `+1` | 12 |

The session-level split was 42 training, six validation, and 12 evaluation
examples. Its evaluation distribution was 2/8/2. The fresh dataset manifest is
`9f01faa28a01973ded36a101c423e1b9b5b4ae9730a133685c3b18917021bce8`;
the pure training manifest is
`8b1203fa3fb1f6de2b17b4488efb3e3c8e79793569e2284f18df0e2214d9310e`.

## Live adaptation and restart

The last three A predictions were all correct `HOLD → +1`. The first B receipt
for the same state/action recorded `HOLD → -1` as a new contradictory fact
without changing the three A facts. It entered Memory at bridge event 4. The
next two bridge forecasts, including one after another process restart, still
predicted `+1`; immediate Memory evidence therefore did **not** revise this
forecast in the observed bridge. Across the first six B decisions consequence
accuracy was 1/6, compared with 3/3 immediately before the shift.

The bridge preserved three pre-shift and three post-shift records across three
runtime indices and three distinct source identities. Six post-restart
consequence requests included legitimate old history, and 21 audited bridge
requests contained no hidden regime label. After candidate rejection, a fresh
process reloaded generation 2 with artifact SHA-256
`effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a`
and made zero model calls.

## Candidate lineage and evaluations

Pure generation 3 continued from the exact generation-2 adapter, used 42 new
training examples, and ran 55 optimizer steps under the unchanged rank-8 LoRA
configuration. Its artifact SHA-256 is
`edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24`.

Candidate 3R was allowed only after generation 3 failed for forgetting. It
started again from generation 2 and added exactly 12 old authenticated
**training** examples: two per consequence class from each of generations 1
and 2, selected by lexicographically first stable ID. Thus new examples remained
42/54 of optimizer rows. It ran 70 optimizer steps; artifact SHA-256 is
`b252190a6fb0d10538820958527b43279d06813aec86361b34f2fa70d72020af`.
Its training manifest is
`e08579be68eaece9afe24fcd45cda25da5b97ee41b45a656ddf5f1b7115a271d`.

| Evaluation | Generation 2 | Generation 3 | Candidate 3R |
|---|---:|---:|---:|
| Fresh B | 8/12 (66.7%) | 10/12 (83.3%) | 10/12 (83.3%) |
| Historical bank A | 18/24 (75.0%) | 12/24 (50.0%) | 14/24 (58.3%) |
| Combined | 26/36 (72.2%) | 22/36 (61.1%) | 24/36 (66.7%) |
| Invalid responses | 0 | 0 | 0 |
| Historical forgetting events | — | 6 | 6 |

For generation 3 the historical transitions were 12 correct→correct, six
correct→wrong, zero wrong→correct, and six wrong→wrong. For 3R they were
12 correct→correct, six correct→wrong, two wrong→correct, and four wrong→wrong.
Both candidates reduced the six-example historical `-1` class from 6/6 to 0/6,
the worst subgroup delta at -100 percentage points.

| Historical window | Generation 2 | Generation 3 | Candidate 3R |
|---|---:|---:|---:|
| Early (8) | 4/8 | 1/8 | 2/8 |
| Middle (8) | 6/8 | 4/8 | 5/8 |
| Recent (8) | 8/8 | 7/8 | 7/8 |

## Live endurance windows

All 60 live records used active generation 2. Invalid rate was zero throughout.

| Window | Consequence accuracy | Actions (`ADVANCE`/`HOLD`) | Outcomes (`-1`/`0`/`+1`) |
|---|---:|---:|---:|
| Early 20 | 11/20 | 3/17 | 6/8/6 |
| Middle 20 | 14/20 | 3/17 | 3/14/3 |
| Late 20 | 14/20 | 3/17 | 3/14/3 |
| Worst rolling 10 (start 4) | 4/10 | 1/9 | 5/4/1 |

## Frozen promotion rule

A candidate had to improve fresh correct count by at least one; lose at most
one historical correct answer; cause at most one historical forgetting event;
avoid an absolute accuracy drop greater than 0.25 for any historical class
with at least four examples; preserve combined correct count with zero
tolerance; avoid increased invalid responses; provide sufficient evidence; and
pass integrity checks. The rule SHA-256 is
`fb1a419e5021274ccce5489defea73e018a7c5707246d97f4338669178d5c3fa`.

Both candidates passed fresh adaptation, validity, evidence, and integrity.
Both failed historical accuracy retention, forgetting bound, class-collapse,
and combined-retention criteria. The registry therefore rejected both and
kept generation 2 as its sole ACTIVE generation. The final registry state
SHA-256 is
`fcb3207684f13c092e76bf7c91e97a28701f5eb88a9bb7a83ebe3be107b5b05d`.

## Evidence and operation

The checked-in registry preserves both rejected adapters, lineage, frozen
datasets, per-example evaluations, usage maps, bank versions, decisions, state
history, and post-cycle reload proof. Inspect it with:

```sh
python -m horus.learn history \
  --registry research/learning-stability-v0/registry
```

The public evidence deliberately excludes session authority keys and raw
private model-call streams. `collection.json` preserves the compact collection,
restart, contradiction, and endurance evidence; `FAILED_ATTEMPT_R0.json`
preserves the interruption without exposing those private streams.

## Limitations

The deterministic four-state world and 12-example fresh evaluation are small
and repetitive. Only one changed state/action pair was actually observed in
both A and B. The bridge showed no immediate selected-forecast revision from
Memory, so this run does not establish Memory adaptation to contradiction.
Both candidates learned the fresh heldout positives while failing every old
negative, which may reflect representation, sampling, or training dynamics;
this experiment does not identify the cause. The fixed 12-row rehearsal did
not solve the failure. No alternative rehearsal size, hyperparameter,
change-point detector, regime token, next-state training, or further generation
was tested.
