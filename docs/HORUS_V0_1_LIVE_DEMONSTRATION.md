# Horus v0.1 live demonstration

This engineering validation ran on 2026-09-25 with the existing
`dolphin-mixtral:latest` model (`4b33b01bf336`). It used six decisions in two
fresh Python processes, 36 actual Map calls, no retries, six original simulated
external receipts, and six authorized training records. The private session is
outside the repository; raw prompts and model responses are not published here.

| Step | Runtime / epoch | State | Exact-state/action history counts A/H/R | Chosen | Prediction `(next, consequence)` | Receipt `(next, consequence)` | Match |
|---:|---|---:|---|---|---|---|---|
| 1 | 1 / 2001 | 1 | 0/0/0 | ADVANCE | (1, +1) | (2, −1) | neither |
| 2 | 1 / 2001 | 2 | 0/0/0 | ADVANCE | (2, 0) | (3, +1) | neither |
| 3 | 1 / 2001 | 3 | 0/0/0 | HOLD | (0, +1) | (3, 0) | neither |
| 4 | 1 / 2001 | 3 | 0/1/0 | HOLD | (3, +1) | (3, 0) | next only |
| 5 | 2 / 2002 | 3 | 0/2/0 | ADVANCE | (0, +1) | (0, −1) | next only |
| 6 | 2 / 2002 | 0 | 0/0/0 | ADVANCE | (1, 0) | (1, +1) | next only |

The first pre-restart authenticated experience entered a Process B request at
call-log sequence 79. Its exact task payload contained the Step 3 and Step 4
records:

```json
{"VERIFIED_CHRONOLOGICAL_HISTORY":[{"consequence":0,"epoch":2001,"next_state":3,"surface_action":"K2","transaction_id":3},{"consequence":0,"epoch":2001,"next_state":3,"surface_action":"K2","transaction_id":4}],"state":3,"target_action":"K2"}
```

Process A's source identity ended in runtime 1 and emitted event IDs 1–4.
Process B used a fresh runtime-2 source identity, began epoch 2002, and emitted
new event IDs 1–2. Step 5 therefore demonstrates imported pre-restart evidence
in the proposal request followed by a new original receipt and authorization.
No Python receipt object was carried across the process boundary.

The final signed checkpoint registered 108 call-stream entries (36 request
intents, 36 responses, and 36 durable parse outcomes), six event records, and
six training records. Its stream heads were:

```text
calls    319a4e42d6b14ebb1921befc0b637dfddce3481530b1b15c9789e098ed1f716c
events   607b9a7dd275c8891bcaab983ab49ef3e9b75e01a27df0322f4c1f319f722d32
training a7089abe2623e2462b118554c7224ef5218eb7a7d4384fda7890064da17b056d
```

The run was not tuned. In particular, none of the six reconciled predictions
matched both realized fields. The later action change is not claimed as
model learning or causal inference; the trace establishes only that grounded
history entered later live requests and the loop continued across restart.
