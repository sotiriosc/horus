# Map failure-context schema transfer v0 — preregistration

## Question and scope

Do the eleven specific moving-positive consequence failures retained by
`map-ranking-failure-forensics-v0` reproduce when their exact historical joint
Map request is issued again, and—only where a failure reproduces—does the
existing consequence-only response schema repair it?

This is a descriptive diagnostic. It has no A/B/C outcome, efficacy threshold,
prompt tuning or architecture change. Exactly eleven matched J/S pairs are
registered: 22 real Map attempts, no retries, replacements or extra calls.
Historical evidence and classifications remain unchanged.

## Frozen source contexts

The implementation selects these rows from the retained forensic evidence by
context number and verifies the failure, target action, mapping, history,
historical response and evidence hashes. No descriptor is manually reconstructed
at runtime.

| Context | World/state | Family | Mapping | Target alias/action | Seed | Authenticated target history | Historical J | Realized |
|---:|---|---|---:|---|---:|---|---|---|
| 2 | W0 / 0 | O2 | 1 | Q7 / ADVANCE | 96012 | tx2: (1,+1) | (1,0) | (1,+1) |
| 3 | W0 / 0 | O1 | 1 | K1 / ADVANCE | 96012 | tx2: (1,+1) | (1,0) | (1,+1) |
| 5 | W0 / 0 | O2 | 2 | M4 / ADVANCE | 96022 | tx2: (1,+1) | (1,0) | (1,+1) |
| 7 | W0 / 0 | O1 | 3 | K3 / ADVANCE | 96032 | tx2: (1,+1) | (1,0) | (1,+1) |
| 8 | W0 / 0 | O1 | 4 | K2 / ADVANCE | 96042 | tx2: (1,+1) | (1,0) | (1,+1) |
| 9 | W0 / 0 | O2 | 4 | M4 / ADVANCE | 96042 | tx2: (1,+1) | (1,0) | (1,+1) |
| 10 | W0 / 0 | O2 | 5 | Z2 / ADVANCE | 96052 | tx2: (1,+1) | (1,0) | (1,+1) |
| 27 | W3 / 3 | O1 | 1 | K2 / RETREAT | 96214 | tx2: (2,+1) | (1,−1) | (2,+1) |
| 30 | W3 / 3 | O2 | 3 | M4 / RETREAT | 96234 | tx2: (2,+1) | (1,−1) | (2,+1) |
| 32 | W3 / 3 | O1 | 4 | K1 / RETREAT | 96244 | tx2: (2,+1) | (0,−1) | (2,+1) |
| 33 | W3 / 3 | O2 | 4 | Q7 / RETREAT | 96244 | tx2: (2,+1) | (0,−1) | (2,+1) |

The exact mappings, full descriptors, source hashes, historical request hashes
and both new request hashes are frozen in `schedule.json`. W0 reconstructs
`HOLD, ADVANCE, RETREAT, RETREAT, ADVANCE`; W3 reconstructs
`HOLD, RETREAT, ADVANCE, ADVANCE, RETREAT`. Both sequences return to the target
state while preserving the original target observation as transaction 2.

## Requests and model

Model: `dolphin-mixtral:latest`. Both arms use temperature 0.2, top-k 40,
top-p 0.9, repeat penalty 1.1, context 2048 and `num_predict=32`, plus the
historical per-context seed in the table. Pair order alternates J/S then S/J.

J is the existing exact joint instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

S is the existing exact schema-only instruction:

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly one field: consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Within a pair, serialized task data, model, sampler, seed and envelope are
byte-identical. Only the middle response-format sentence differs. Replacing S's
system string with J's must make the complete request equal to J. Each J request
must also equal the retained historical request hash. Strict existing parsers
apply; invalid output is recorded without repair and consumes its one attempt.

## Execution and authority

Each probe follows:

`model response → durable record → strict parse → non-model control latch → actual execution → new original receipt → Measure/authorization/Memory → detached probe score`.

The probe response is not passed to `begin_step`, execution, receipt issuance,
Measure, authorization, recovery or Memory. W0's control is `(next_state=1,
consequence=+1)` for ADVANCE; W3's is `(2,+1)` for RETREAT. The target action
executes only after response and parse. Score uses transaction 6's new original
receipt, not a declared law or the control. Setup and new receipt publication
use the grounded path. Explorer and Recovery make zero model calls.

## Frozen descriptive definitions

- **Historical J failure reproduced:** the new J response is valid and its
  consequence differs from the new realized receipt consequence. Exact
  reproduction of the old numeric J value is reported separately.
- **S repaired it:** the historical J failure reproduced and S is valid with a
  consequence equal to its new realized receipt consequence.
- **S made a correct J worse:** J is valid and consequence-correct while S is
  invalid or consequence-incorrect.

The report gives the eleven rows and only these summaries: reproduced failures,
repairs among reproduced failures, S regressions from correct J, and the main
interpretation. The interpretation rule is frozen:

1. If at most 5/11 J failures reproduce, report that failure reproducibility /
   context sensitivity is the next problem and stop.
2. Otherwise, if S repairs every reproduced failure and causes zero regressions,
   report schema coupling in every reproduced failure and stop.
3. Otherwise report mixed schema-coupling and reproducibility evidence and stop.

These are reporting rules, not pass/fail thresholds and not evidence of an
internal causal mechanism.

## Preflight, durability and stopping

Before inference, zero-network preflight must verify all 11 historical J request
hashes, all 11 matched pairs, 22 future-event canaries, strict J/S parsers, 16
detachment variants, descriptive aggregation controls, ambiguous-call stopping,
a 22-response synthetic campaign and byte-identical synthetic replay.

The live archive records intent before each call. A transport ambiguity, failed
durable write, hash mismatch or control failure stops without reissue. After 22
attempts, stop. Exact replay must reproduce seven files and 22 snapshots. Publish
only compact results and verification; retain complete requests, journals and
private transport evidence outside the public tree. Do not start a split Map,
prompt change or follow-on experiment here.
