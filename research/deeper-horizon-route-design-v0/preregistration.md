# V0.15 bounded depth-2 trajectory preregistration

This preregistration follows completed v0.14 commit
`79c7a709ed7a333e9ad3760f717ff1d71dcc22fb` and implementation checkpoint
`ee52469980fe954f641e271ba6e6bef0e7665218`.

## Frozen question and structural gate

Can finite enumeration of `(c0,c1,c2)` consequence sequences distinguish the
two PR-0002 current actions without changing the objective?

The zero-inference analysis is bound by SHA-256
`726f8494aedd9a672e230f5f161630d713312c62f32a405d7335ea4d78bb17e4`.
It establishes that v0.14's routed vectors `[-1,0,+1]` and `[+1,+1,0]` are
distinct but both collapse to maximum `+1`. The candidate route adds each
second action's predicted next state and the consequence opportunity at that
state, so it does not algebraically reduce to the v0.14 comparison. This passes
the live route-design gate without assigning a preference to either vector.

## Source state

- Session: 85 attempted decisions, 54 authenticated executions, state 2.
- Streams: 2,304 call envelopes, 86 evaluation/training envelopes.
- Problem Manager: 31 events.
- PR-0002: `REASSESSED`, request `DEEPER_HORIZON_VALUE`.
- PR-0002 one-step route: consumed 1/1 with `STILL_TIED_AT_ONE_STEP`.
- ADVANCE: authenticated `c0=+1`, authenticated first continuation state 3.
- RETREAT: authenticated `c0=+1`, authenticated first continuation state 1.
- PR-0003 digest:
  `52abbc28b599fafd771452499e9503738fedf212434062f4526317b7d4eaba8b`.

## Authorization

Authorization SHA-256
`f18e905beb690ae645ef44c32eca6c93fc56d278350c7267e8d4a841367648f0`
grants one evaluation of `BOUNDED_DEPTH2_TRAJECTORY_VALUE` for PR-0002. It
does not grant world execution, training, recursion, depth 3, or a new objective.

## Frozen route

For each current action, enumerate ADVANCE, HOLD, and RETREAT as second actions.
For every second-action branch, freeze one existing joint request and independent
G2/G3 consequence requests before any response. Consume only the joint
`next_state`. Route `c1` by the existing exact `(state,action)` specialist.

For each predicted second state, evaluate G2/G3 consequences for all three
legal actions, route each relation, and set `c2` to their maximum. Stop there.
Every candidate is the lexicographic sequence `(c0,c1,c2)`. Select the maximum
sequence within each current action, retaining all tied second-action identities,
then compare the two current-action sequences. Do not sum or discount.

Provenance is fixed as:

- `c0`: `AUTHENTICATED_RECEIPT`;
- first continuation state: `AUTHENTICATED_RECEIPT`;
- `c1`: `MODEL_FORECAST`;
- second next state: `MODEL_FORECAST`;
- `c2`: `MODEL_FORECAST`.

The predicted second state chooses the terminal state context. It is not added
to verified history, represented as a receipt, or included in any consequence
request as a `predicted_next_state` field.

## Exact deduplication and bounds

A terminal consequence request may reuse a second-layer consequence result only
when the complete canonical request bytes are identical. Those bytes include
state, action alias, exact verified history, specialist/model identity, system
instruction, options, and stream setting. Hash equality without byte equality
is insufficient. No joint request is deduplicated.

The absolute ceiling is 30 calls:

- six joint second-action calls;
- twelve G2/G3 second-action consequence calls;
- at most twelve new terminal consequence calls after byte-identical reuse.

The registered state domain is 0--3. Second-layer consequences already cover
states 1 and 3, so terminal requests at those states are identical and reused;
only state 0 and state 2 can add six consequence calls each. No retry or
extension is permitted.

## Outcomes and stop rules

- `DEPTH2_DISTINGUISHES`: return the unique preferred current action and stop.
  Do not execute it.
- `STILL_TIED_AT_DEPTH2`: return no action, record
  `DEPTH2_TRAJECTORY_INSUFFICIENT`, request
  `ALTERNATIVE_VALUE_REPRESENTATION` with external-approval-only status, and
  stop. Do not request depth 3 automatically.
- `INVALID_ROUTE`: localize the operational failure, preserve evidence, and
  stop without retry.

PR-0002 remains the owner. PR-0003 must remain unchanged. Maximum depth is
exactly 2, recursive calls are 0, behavioral executions are 0, and training
runs are 0.

## Frozen implementation

- `horus/problem_manager.py`:
  `759300c432f9f33761dd646ac30e7b3df222b44be34020a11113372f40688c58`
- `horus/depth2_value.py`:
  `7ffcbb5b45fa63edba78381afca048d421565f73e0fcd1fc36f665380e385499`
- `horus/depth2_value_cli.py`:
  `37fe4c18504a0efd53610181f73f5703cbbf7a188df7a4644503074fd72cb718`
- `horus/live.py`:
  `7a9d78692e2c07b1d3fc9ee24a0c079fe6b4b4cd247485f5bdf1024027faf92e`
- `horus/one_step_value.py`:
  `fb730785835dea2f2636eb6e926b030fbb0f800b3ca1690a017271907897bc3f`
- `horus/relation_routing.py`:
  `4845d0fdeb34ac3101fca915f1cd5979048b4b1d80c89a91c913e8fc3962d396`
- `horus/grounded_exploration.py`:
  `88f744965f661b0a2c0bf610ff82e145a692da98d3ec58aea49c2ae07327af34`

The result is preserved whether it distinguishes, remains tied, or fails.
