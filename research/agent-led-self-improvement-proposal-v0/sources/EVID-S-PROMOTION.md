# Bounded stagnation escape: explicit incumbent promotion

Status: PROMOTED. The completed eligibility study recommended PROMOTE_S, subject to external approval; the user subsequently granted that approval. This separate commit activates the exact frozen S = BOUNDED_STAGNATION_ESCAPE candidate through grounded_agent.decide. No new scientific world campaign was run.

## Incumbent and rollback

The previous incumbent is the canonical grounded-authority I decision path in experiments/grounded_stagnation_escape_promotion_controlled_v0/worker.py, preserved unchanged at source commit af7b83dd9c929cf33c1e01d453e4ce86ec1624f4 (file SHA-256 83d6cb5b0d336558f6b459eaa9eb8da8939e57f59f89a7638c2c36b3fa8d6a74). The exact pre-activation selector and tests are preserved at rollback commit 7bd264862b7e060724b01081b9d988a984db3a99; at that commit, grounded_agent.decide points to previous_incumbent_decide. To roll back without reconstructing code, restore grounded_agent/__init__.py from 7bd2648 and commit the restoration, or revert the activation commit. The previous_incumbent_decide function remains available.

The new active definition is grounded-authority policy + BOUNDED_STAGNATION_ESCAPE. grounded_agent.policy.promoted_decide constructs the same canonical decision context as the evaluated controlled-pairing study and delegates directly to its frozen S decision function. That function delegates to the unchanged frozen candidate and protected escape implementation. Historical study entry points remain frozen and are not rerouted retroactively.

## Evidence basis

| Record | Commit | Preserved conclusion |
| --- | --- | --- |
| Phase 3 proposal | dbc13eae7e062ebc07b3b2bf5de14a4610156119 | Frozen candidate specification. |
| Phase 4 support | e715b8590d7d1ac33b4ca26481cfb4930d6d5189 | STAGNATION_ESCAPE_SUPPORTED. |
| Replication | fae30db7c60294fd52a9fd57a2797be9bc3ad24a | Original cost/scope classification unchanged. |
| Action-model audit | b75c80ae9bbbd9ff0d13ac5bec5adcf9cf5d4037 | Stochastic configured action model. |
| Controlled stochastic pairing | afc1c856aecbae65a1389d0abf144b6a50d09133 | Original MORE_EVIDENCE_REQUIRED classification unchanged. |
| Eligibility completion | af7b83dd9c929cf33c1e01d453e4ce86ec1624f4 | Final PROMOTE_S recommendation, subject to external approval. |

The eligibility completion observed four naturally eligible prefixes and four S escapes, all four new controls with zero false triggers, 31/31 equal I/S actions at matched inactive boundaries, and restart reconstruction of suffix 2 in each eligible case. Negative first receipts remain recorded as acquisition costs. Complete private authenticated evidence remains in local archival branches, outside this publication lineage.

## Source and behavior freeze

Candidate source SHA-256: 2293c46be58684f6dcf903b82dff7d29bc9fdef69790b4c22e154c750c8a5b92.
Controlled S decision source SHA-256: 83d6cb5b0d336558f6b459eaa9eb8da8939e57f59f89a7638c2c36b3fa8d6a74.
Protected execution worker SHA-256: 5e9b1734e10da48883e55281b883db2ae7df94664fd8334940f6841e759354d2.
These files are byte-identical to evaluated source at af7b83d.

The threshold is exactly 3. Eligibility requires consecutive authenticated realized zero fallbacks for the same state and relation, deterministic established zero, another UNSEEN action, and no established +1 ceiling. The first unseen action follows ADVANCE, HOLD, RETREAT. A state change, fallback identity change, or escape breaks the qualifying suffix. Restart derives it from authenticated receipts and Memory, never a mutable counter. The escape freezes one action without an action-model call. Receipt, Measure, authorization, and Memory paths are unchanged.

## Verification

While I remained active at 7bd2648, the targeted promotion, frozen candidate, grounded-authority policy/worker, and grounded-state suites passed 20/20 zero-inference tests. These checked source digests, threshold and action order, +1 ceiling, absent or unresolved-only alternatives, empirical fallback rejection, state and fallback reset, one-shot reset, signed restart, model-free escape, and authorized receipt/Memory publication. Post-activation tests and a full reachable-history secret audit are required before publication and are recorded in the final handoff.

No new exploration rule, Horus, Zakhor, self-analysis, self-modification, model/runtime replacement, prompt redesign, threshold tuning, or training change is part of this promotion. The rule remains subject to later evidence and may be rolled back if material harm appears.
