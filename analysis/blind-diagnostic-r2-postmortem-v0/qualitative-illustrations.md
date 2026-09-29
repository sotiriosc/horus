# QUALITATIVE ILLUSTRATIONS — NOT SCORED

Selection rules were committed in codebook freeze
`36a2f7f4b498707cbb71b26e68cc25226918982a`. Exact example IDs and public-final hashes
were committed with all deterministic results at
`7b8ba59444df26ef4e4fdb40dab678f6d031e337`, before reviewing their prose. Each example
is the first qualifying rendering in the original request schedule, not a
representative sample. Only these five selected examples receive qualitative
interpretation. These notes introduce no quantitative categories, semantic grades,
corrections, or changes to the frozen result.

## Historical evidence selected as current: schedule position 11

Render `c87f1c5cf6b59ecb5c54`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/c87f1c5cf6b59ecb5c54.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/c87f1c5cf6b59ecb5c54.json).

The structured class is `SUPPORTED_CURRENT_DEFECT`, but the diagnostic statement
says: “The current system has no active defect related to this rule.” Deployment
record `z4704a5c2dfcafa63` identifies current version `ze7eb460a5b8fafa7`. Its output
`z5cb258823ac8c0aa` reports `DENY`, while the older version's output
`z06955534bb7133f3` reports `ALLOW`. The final's prose itself distinguishes those
versions and says the current one correctly implements priority. This illustrates
a prose/class self-inconsistency in this example only. It does not create a new
counted category or earn historical-class credit.

## Insufficient evidence selected as current: schedule position 1

Render `e24ffa812432f3e62a4e`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/e24ffa812432f3e62a4e.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/e24ffa812432f3e62a4e.json).

Input `z4628edd3b127c8d2` records `attempt_total_before: 14` and
`batch_size: "UNKNOWN"`; publication fields and other writes are also `UNKNOWN`.
Output `zd19ba4a4149299b8` records `attempt_total_after: 19`. The final infers
“batch_size must be 5 to satisfy attempt_total_after=14+5=19” and treats the omitted
batch size as a component defect. Contract `z587ffca10dd5d46a` says UNKNOWN denotes
omitted information, never a default. This illustrates the selected
`INSUFFICIENT_AS_CURRENT` example; it does not establish that all insufficient
cases failed through the same interpretation.

## Invalid evidence selected as current: schedule position 5

Render `3b310ba249b0818e7e77`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/3b310ba249b0818e7e77.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/3b310ba249b0818e7e77.json).

Output `z61f8caf436dd1ea7` gives `published_reading: 27` and capture
`z038c0dac75a7b8fb` gives `published_reading: 28` for the same immutable event
`z6d8c6b5036566bf3`. Capture contract `z3f993a58ccd56c74` states that one immutable
event ID has one payload. The final notices the contradiction, yet says the
input/output worker “is responsible for the discrepancy” and selects a current
component defect. This illustrates diagnosis despite contradictory evidence in
this particular final. No causal attribution is credited or generalized.

## Correct component with an inexact witness: schedule position 7

Render `1fa86b8dd54b091e3ad3`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/1fa86b8dd54b091e3ad3.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/1fa86b8dd54b091e3ad3.json).

The final selects the correct component `z93b99a7c7cf13c6b` and describes a command
issued at equality. Its witness points to the input record, uses decisive field
`/data`, and puts serialized input objects into the observed/required value
strings. The frozen accepted witness instead uses output `zee9b747d8c7b724b`,
field `/command_issued`, and boolean values `true` and `false`. It also omits the
required deployment citation `z14c06969d2d49e5a`. These exact mismatches already
appear in the deterministic artifact; the prose earns no informal localization
credit.

## Healthy evidence selected as current: schedule position 20

Render `514366f8d50c91a4fba2`:
[public final](../../research/blind-diagnostic-generalization-v0/replacement-r2/raw/finals/514366f8d50c91a4fba2.txt),
[public source](../../research/blind-diagnostic-generalization-v0/materialized/rendered/514366f8d50c91a4fba2.json).

Contract `z299561fbc696df15` explicitly says: “Repeated identical requests may
return identical values indefinitely.” The final instead says the contract
“prohibits identical outputs for repeated identical requests” and selects a
current defect. Both execution versions use the active configuration's value 23
and return 23. This example illustrates the already-counted healthy false-current
selection. The apparent reversal of the contract statement is not introduced as
a new quantitative category.
