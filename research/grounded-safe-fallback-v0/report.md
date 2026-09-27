# Grounded safe fallback v0: completed interpretation

**Classification: `SAFE_FALLBACK_SUPPORTED`.** In this registered finite world, uncertainty about the optimal action did not always require complete abstention. H_SAFE took a grounded action with established consequence 0 in six situations where unchanged H_ABSTAIN abstained. All six fallbacks realized 0; none harmed the system or converted an unresolved relation into established knowledge. Every fallback was recorded as `action_justified=true` and `optimality_established=false`.

The [preregistration](preregistration.md), [scenarios](scenarios.json), and [source manifest](source-manifest.json) were committed before live inference. The existing consequence scale is `+1 > 0 > -1`, and `horus/core.py` already labels 0 neutral. The frozen rule treats only an **established** consequence of at least 0 as an acceptable fallback. This is a decision preference for this simulator, not a guarantee that historical evidence cannot become stale in a changing external world. The prior grounded-hybrid evidence remains unchanged.

Eight prospectively frozen scenarios provided 11 decision opportunities per arm. Four independent protected sessions received matched authorized controlled seed receipts before their first autonomous decisions. Selected actions used the original receipt → Measure → authorization → durable ModernMemory path. Follow-up probes in P2, P5, and P6 were controlled, authenticated observations; second decisions are within-arm trajectories after autonomous histories diverged. No model inference modified grounded state.

## Decision results

| Arm | Actions / 11 | Abstentions | Realized consequence sum over actions | Incorrect confident actions | Model calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| H_ABSTAIN | 4 | 7 | 3 | 0 | 2 |
| H_SAFE | 10 | 1 | 3 | 0 | 2 |
| FORCED_GROUNDED | 11 | 0 | 7 | 2 | 0 |
| MODEL | 11 | 0 | −3 | 7 | 48 |

The consequence sums use different action counts and are not a single performance ranking. The six extra H_SAFE actions were neutral, so **H_SAFE did not increase its consequence sum** over H_ABSTAIN in this run. It reduced abstentions from seven to one while maintaining zero incorrect confident actions. FORCED_GROUNDED sometimes happened to find +1 across unresolved relations, but its selected point was wrong twice; broad MODEL forecasting had seven wrong selected points in this small deterministic sample.

P1 had a grounded +1 action; both hybrids used the parent ceiling rule, with no safe-fallback override. P3 had only a grounded −1 alternative and both hybrids abstained. P4 kept two alternatives unresolved while H_SAFE selected the grounded 0 action. P7 included an unseen ADVANCE relation as well as unresolved HOLD; both hybrids used the frozen model **only** to assess that unseen relation, and H_SAFE still chose the grounded neutral fallback without using the model to settle HOLD. H_ABSTAIN remained unchanged at every decision.

P5 shows the tradeoff: H_SAFE took a justified 0 while unresolved ADVANCE would have yielded +1. A later authenticated ADVANCE receipt confirmed +1, and both hybrids then selected it as grounded. P6 shared the contradictory prefix but a later HOLD receipt rejected the anomaly; both hybrids then selected restored grounded HOLD for +1. P2's later −1 HOLD receipt confirmed the candidate and its second decision selected grounded RETREAT for 0. P2, P6, and restart scenario P8 share the same four-receipt value prefix before those different futures. Their first unresolved assessments correctly remain uncertain.

**Three of the six fallbacks were safe but suboptimal in hindsight** (P4, P5, P7): an unresolved or unseen alternative would have yielded +1. This does not make the grounded 0 action epistemically false. H_SAFE had four missed positive opportunities including the P3 abstention; H_ABSTAIN also had four, all from abstention. Retrospective world outcomes were used only by the analyzer, never by the decision policies. The extra actions demonstrate a way to act acceptably while admitting optimality is unknown; they do not show that the fallback finds the best action.

Across 24 action assessments in each hybrid arm, 14 used established receipt values, one used model generalization on an unseen relation, and nine kept contradictions explicitly unresolved. `FALSE_CERTAINTY=0` and `MISSED_KNOWN_VALUE=0` for both arms. H_SAFE recorded seven executed actions with `optimality_established=false`, including its six fallback actions. That flag is conservative: this implementation marks global optimality established by a grounded +1 ceiling, not merely by choosing the highest currently assessed point.

## Restart, costs, and integrity

P8 restarted in a fresh process with unresolved `1:HOLD` and established neutral `1:RETREAT`. Durable file hashes, both grounded states, exact receipt supports, H_ABSTAIN's abstention status, and H_SAFE's fallback eligibility matched across restart. A non-current Memory admission was rejected; neither receipts, grounded states, nor fallback eligibility changed.

H_SAFE and H_ABSTAIN each used **two model calls** and 42 input context tokens for the single unseen relation in P7. MODEL made 48 calls and used 3,304 input context tokens; FORCED_GROUNDED made none. All 52 logical calls had one physical attempt. Total measured decision time across 11 opportunities was 9.00 seconds for H_SAFE, 9.17 for H_ABSTAIN, 329.47 for MODEL, and 0.40 for FORCED_GROUNDED. H_SAFE's receipt-derived state folds totaled 0.00060 seconds. Timings include execution and logging and are descriptive service measurements.

Grounded state was derived on demand; no materialized state table was added to operational Memory. A serialized H_SAFE relation state averaged 772 bytes per assessed candidate, including provenance. The eight H_SAFE SQLite Memory files totaled 270,336 bytes versus H_ABSTAIN's 262,144 bytes, reflecting additional protected action receipts and page allocation, not a separate state representation. The study's audit training stream used 96,376 bytes for H_SAFE and is separate from operational Memory.

The [exact replay](evidence/replay.json) passed authenticated Memory reconciliation; matched seed observations and independent receipt sources; reconstruction of every predecision epistemic state; exact H_ABSTAIN/H_SAFE/forced/model choice reproduction; binding of autonomous actions to original protected receipts; the P2/P6/P8 information boundary; restart and perturbation checks; and exact analysis reproduction. The protected and transport preflights passed before inference.

This supports a narrow architecture: preserve what is established, unresolved, and unseen; use a grounded action established as neutral when the winner is unknown; keep `action_justified` separate from `optimality_established`; otherwise abstain or use the frozen model only for unseen relations. The neutral threshold is application-specific. A different consequence scale or risk preference needs its own registered criterion rather than silently inheriting this one. No planner or agent was added.
