# Future matched Phase-4 evaluation design — not run

Phase 4 requires a separate preregistration and implementation commit before any inference or execution. Preserve `I` as the frozen control and build `S` as an isolated candidate differing only by [`BOUNDED_STAGNATION_ESCAPE`](candidate-rule.md). Match initial state, task/world family, visible information, model identity/parameters, action order, allowed actions, goal, decision horizon, receipt path, and planned restart point across arms. Pair or prospectively fix seeds/schedules and disclose how diverging action trajectories affect comparability. Do not feed hidden schedule metadata or unexecuted counterfactual outcomes to either arm. Exact sample size, stopping rule, and analysis procedure must be frozen in that separate Phase-4 preregistration, not chosen after results.

| Registered case to include | Purpose / expected eligibility |
| --- | --- |
| C-like neutral stagnation: known deterministic zero fallback and multiple unseen alternatives | Test whether I repeats and whether S acquires one missing exact-relation receipt after three qualifying executions |
| Useful exploration case | Observe whether an acquired relation can supply useful evidence; do not assume its outcome at decision time |
| Costly exploration case | Measure an unseen action's realized negative consequence and downstream cost transparently |
| Grounded `+1` present | No-trigger control: established ceiling must retain mechanical authority |
| No unseen alternatives | No-trigger control: unresolved/empirical alternatives alone do not activate v0 |
| Fallback leaves state | State-change reset: no cross-state accumulation |
| Restart while counter is accumulating | Rebuild suffix from authenticated records; compare first post-restart eligibility and replay snapshot with uninterrupted arm |

The experimenter may register world scenarios using controlled outcome schedules; candidate decisions and model prompts may see only the preregistered decision context and authenticated receipts acquired so far. Outcomes of unexecuted actions remain analysis-only. Include both action-level and receipt-level audit traces so that a changed action does not silently alter the truth boundary.

Report **separately** for each arm and matched case: maximum qualifying zero-fallback streak, number and identities of previously unseen exact relations sampled, first authenticated receipt/provenance for each new relation, negative/neutral/positive acquisition outcomes, realized total consequence, action-model calls, mechanical decisions, trigger count, false-trigger count, grounded-state replay integrity, and restart integrity. Define false trigger as any S escape whose frozen predecision/suffix predicates are not all met. Do not combine endpoints into a single score. Report actions that fail authorization as integrity failures, not as evidence acquisitions.

Analysis should first verify action parsing and exact trigger eligibility from predecision evidence, then protected execution/receipt authorization, then durable Memory replay and restart, then primary relation acquisition, streak lengths, and realized costs. A positive result for acquisition alone is insufficient for promotion; [promotion criteria](promotion-criteria.md) remain a later decision. This document authorizes no Phase-4 run.
