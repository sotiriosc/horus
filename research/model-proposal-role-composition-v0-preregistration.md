# Model proposal role composition v0 — zero-call gate

Parent: `2a145a3ebbe905ebafbf87559bbe97d062ed9103` (`research/model-recovery-proposal-v1`).
Freeze this protocol before executing the gate. Historical implementation, evidence,
main and tags remain unchanged. No push. No automatic interface repair.

Question: can the three already-tested Explorer, Map and state-Recovery proposal
adapters participate in one sequential grounded loop while reality, Measure,
Memory and authorization remain outside the model?

## Mandatory precondition

Use only deterministic synthetic sources and unchanged adapters. Check their
supported input domains before attempting inference. In particular the required
initial state is 0, with empty Memory and every action available. A domain guard
that prevents this required transaction is a failed completion requirement.
Stop with zero model calls if composition cannot be established; do not remove
guards, generalize historical adapters, seed Memory or change the start state.
This is not a claim that the underlying general framework cannot support a future
separately reviewed binding.

The gate must establish A–O: action-only Explorer; bounded Prediction-only Map;
replacement-value-only Recovery; no Explorer prediction capability; no Map action
capability; no Map receipt capability; no Recovery receipt/prediction mutation;
Recovery only after a genuine opportunity; one attempt; repaired status-bound
authorization; atomic wrong-candidate rejection; authentic Memory; staged
coexistence; no continuation/retry after rejection; existing bounds. An early
domain failure leaves unreached properties unestablished, not vacuously passed.

Diagnostic plan: characterize the existing Map adapter over 4 states × 3 actions;
then attempt the three required state-0 first actions with the unchanged canonical
Explorer adapter, existing Map adapter and installed Recovery v1 proposer using
synthetic transports. These are component diagnostics, not opaque-family episodes.
Separately check the existing opaque Explorer projections on empty Memory across
the 12 planned mappings. Keep diagnostic and model-call counts separate. Exact
repeat must reproduce diagnostic rows and compact results without inference.

## Conditional live design (not authorized to run unless gate passes)

Stationary original four-state/three-action world; state 0 and empty Memory.
O1=(K1,K2,K3), O2=(Q7,M4,Z2). Map these tokens to each permutation of
(ADVANCE,HOLD,RETREAT), in that enumeration order, once per family. One mapping
is shared by every role throughout each episode. Base seed=80001+mapping index.
Decision index is zero-based 0–7; seed=base+100*decision+role offset, where
Explorer=1, Map=2, Recovery=3. The two families share matched seeds.

12 episodes, at most 8 executed decisions each: 96 decision slots, at most 192
Explorer/Map requests and 288 total requests. Recovery only when genuinely
triggered; no retry, replacement, extension or forced Recovery. Malformed role
output, wrong Recovery rejection, protected failure or transport failure ends
that episode. Record unused slots. Never ban an allowed action on learned
preference or rewrite older verified observations.

Same pinned dolphin-mixtral:latest, Ollama 0.1.16, GGUF 47B Q4_0; inherit verified
weight digest `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Every request stateless: same weights do not imply shared chat. Temperature .2,
top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1; num_predict 16 for Explorer,
32 for Map and Recovery. Reverify bytes before any conditional inference.

Use exactly the supplied exploration-aware instruction, unchanged Map instruction
and unchanged Recovery instruction. Explorer sees current state, all three opaque
allowed actions, authenticated relevant observations and UNTRIED. Map sees current
state, accepted opaque action and authentic chronological history for that exact
pair (empty if untried). Recovery sees only pre_state, opaque action, verified event,
measurement_matches and allowed replacement states. No future, oracle, raw text
from other roles, hidden chat, or model-supplied authority/identity fields.

Primary A requires all 18 user-specified integrity conditions, including genuine
Recovery routing, independent authorization, atomic rejection, no retry/leakage/
rewriting, bounds, exact replay and historical regressions. B is an observed
protected authority failure. C is another missing completion requirement.
No aggregate behavioral threshold. Report role-specific validity, coverage,
preference/retest metrics, Map accuracies by prior-observation count, Recovery
opportunities and authorizations separately. Retain all experience/revisit and
correction chains. Report realized and authorized consequence independently.
Changes in proposals are observational, not causal evidence of learning.

After a successful live run, conduct only the bounded role-parser negative
controls specified in the request, then exact recorded-response replay and the
historical regression set. If the precondition blocks, report model behavior,
live replay and post-live controls as not run; deterministic diagnostics and
historical regressions remain permissible. Produce all 38 report sections and
stop; do not launch a repair or another campaign.
