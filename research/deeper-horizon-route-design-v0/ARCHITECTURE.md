# Bounded depth-2 trajectory route

For each current PR-0002 action, the route requires an authenticated immediate
consequence and authenticated first continuation state. It enumerates all
three legal second actions. For every branch it freezes one existing joint Map
request and independent G2/G3 consequence requests before receiving any of
their outputs. It consumes only `next_state` from the joint response and uses
the existing relation-local specialist choice for `c1`.

At each predicted second state it evaluates all legal actions with G2/G3 and
uses the maximum routed consequence as `c2`. This terminal layer requests no
next-state output. Requests are reused only when their complete canonical bytes
are identical, which binds state, action alias, specialist/model identity, and
input history.

Each branch is represented as `(c0,c1,c2)`:

- `c0` and the first continuation state come from authenticated receipts;
- `c1`, the second next state, and `c2` are model forecasts.

Comparison is lexicographic. There is no addition, discount, scalar reward,
recursion, fourth layer, world execution, training, or behavioral authority.

The call ceiling after exact-request deduplication is 30: 18 second-layer calls
(six joint and twelve consequence) plus at most 12 new terminal consequence
calls. The possible terminal states are the four registered states; requests
for states 1 and 3 are byte-identical to already frozen second-layer consequence
requests, leaving at most the six requests for state 0 and six for state 2.
