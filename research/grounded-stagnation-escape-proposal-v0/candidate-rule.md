# Frozen candidate rule: `BOUNDED_STAGNATION_ESCAPE`

This is a **specification**, not executable code. It changes one decision boundary of [`select_route`](../../experiments/grounded_authority_autonomous_agent_v0/protocol.py) in a future candidate arm only. The incumbent is untouched. All terms below refer to authenticated pre-decision assessments and original authorized realized receipts, never simulator metadata, model claims, or unexecuted outcomes.

## Qualifying execution

For a completed decision at pre-state `s` and selected action `a`, count **one** qualifying neutral fallback only if all are true:

1. Its pre-decision exact relation `(s, a)` was explicitly `DETERMINISTIC`, `ESTABLISHED`, and had established consequence **exactly `0`**.
2. The incumbent mixed route admitted `a` as its known fallback, and the model selected `a` (`SAFE_GROUNDED_FALLBACK`).
3. At least one *other* action at `s` had pre-decision kind `UNSEEN`; `UNRESOLVED` or empirical alternatives alone do not count.
4. No exact deterministic established `+1` action existed at that state; the existing ceiling route therefore retained priority.
5. The original authorized receipt for `(s, a)` reported realized consequence **`0`** and next state **`s`**.

The consecutive counter is the length of the **maximal suffix of completed decisions** satisfying these predicates with the **same exact `(s, a)`**, no intervening decision, and the same continuing state. It is derived from the signed decision/action record, its matching authorized event/receipt identity, and grounded pre-assessments replayed from durable Memory. It is *not* a new writable grounded fact or model-visible authority. If the action is invalid or no authorized receipt exists, no qualifying completion is recorded and no world execution may follow that invalid decision.

## Trigger and choice

At the next pre-decision boundary, if the suffix length is at least **3**, current state still equals `s`, `(s, a)` still has deterministic `ESTABLISHED` consequence `0`, no established deterministic `+1` action exists, and at least one **other** action is still `UNSEEN`, override the incumbent's mixed choice **once**. Select the **first currently unseen eligible action** in the frozen canonical order `ADVANCE`, `HOLD`, `RETREAT` ([source](../../experiments/base_framework_v0/framework.py)). The prior fallback `a` is excluded because it is established. The chosen action is a single evidence-acquisition execution tagged `ACQUIRE_MISSING_RELATION_EVIDENCE` / `STAGNATION_ESCAPE` in the future arm's auditable decision record. It does not involve an action-model call at that boundary and makes no reward claim.

After this one action, admit its original receipt through the **unchanged** protected path and derive its relation through the existing grounded fold. The next decision uses the ordinary incumbent route unless a *new* three-execution qualifying streak later occurs. One trigger never authorizes a batch or continued forced exploration.

## Reset and recovery

The qualifying suffix becomes zero if state changes, selected fallback action changes, fallback consequence is not `0`, a grounded `+1` action is available, no unseen alternative remains, or one escape action executes. A nonqualifying decision also breaks consecutiveness. `UNRESOLVED` alternatives without any `UNSEEN` action cannot activate the rule. Empirical observations never qualify as an established deterministic zero.

No durable counter is added. A future implementation must reconstruct the suffix from authenticated decision/action records and receipt-linked grounded pre-assessments after restart, verify it against the signed streams/ModernMemory replay, and reject an inconsistent reconstruction before selection. The escape action itself is nonqualifying, so its authenticated record resets the suffix naturally. A restart between the second and third qualifying executions must preserve the same reconstructed count as uninterrupted execution. The bounded decision context shown to the model remains the incumbent's; this reconstruction is controller-side and must not feed extra retrospective text into later prompts.

**Worked observed prefix, not an evaluation:** In archived Run C, D04 first discovers `0:HOLD=0` from `UNSEEN`, so it is not qualifying. D05, D06, and D07 are the first three qualifying fallbacks if replayed under this definition. S would consider an escape at D08, subject to fresh authenticated eligibility checks, and would choose `ADVANCE` before `RETREAT` because both are unseen and `ADVANCE` is first in the frozen order. This is a rule illustration; no D08 candidate outcome is asserted or simulated.
