# Map-guided Explorer interface v0 — zero-call registration

Parent `6448aaca17bdc748f468a93e72a355bdb5331450`. Both Explorer negative checkpoints remain permanent; Map revision remains REPLICATED. This is a new architectural input-binding study, not prompt tuning or a behavioral campaign. **ZERO MODEL CALLS**, no live mode, no push, no main/tags changes.

## Roles and scope

Memory stores authenticated realized historical events. Map proposes finite current estimates from exact-pair authenticated history. Explorer proposes a legal action from those estimates. Neither proposal authenticates reality or authorizes execution. Ordinary external execution/receipt, Measure, non-model authorization and downstream Recovery are unchanged. The interface ends at a detached, non-authoritative action proposal; later driver integration and model behavior are not established here.

Use the unchanged epoch-visible Map projection and strict historical Map/opaque Explorer parsers. Never modify old adapters, replace historical Memory with summaries, or pass raw Map text, context, explanation or parser errors to Explorer. Sources receive only immutable system/prompt strings; never a reader, coordinator, framework, executor, receipt source or authority capability.

## New type and freshness

Frozen `CurrentActionForecast` is distinct from MemoryRecord and RealizedEventReceipt. It binds opaque alias, underlying action, proposal ID, parsed finite Prediction, current state/epoch, decision ID, source Memory hash, full authenticated snapshot hash and exact Map-input hash. All metadata remains internal. Prediction's transaction ID is prospective metadata, not an executed event or grant.

The trusted reader audits already-realized receipts and projects Memory without executing or querying future world truth. Each decision obtains a fresh authenticated snapshot. Check current snapshot before/after every synthetic source invocation and before rendering/using a proposal. A new coordinator decision invalidates the old one. Snapshot changes (state, epoch, Memory, transaction/source counters) invalidate old forecasts. Reject missing actions, substituted/copy-rebound forecasts and alias/action mismatch. No cache crosses realized events. The trusted driver must repeat freshness checking before any future ordinary execution; a returned Python dataclass is never authorization.

This is a trusted single-process binding, not a cryptographic or hostile same-process Python isolation boundary. Only serialized detached values cross the prospective model-facing boundary.

## Collection, rendering, ties and bounded failure

Collect independently once for each legal underlying action in **ADVANCE, HOLD, RETREAT** order, independent of alias mapping. Each source gets its own exact-pair history. Render in frozen opaque mapping-key order: O1 K1/K2/K3; O2 Q7/M4/Z2, with all six complete mappings in each family. Never infer an unqueried action.

Explorer view contains only current authorized `state` and three rows `{action, map_prediction: {next_state, consequence}}`. Domain: exact integer next_state 0..3, consequence −1/0/+1. No raw authenticated-history arrays, UNTRIED value, source identities, provenance capabilities or raw source text in this view. Its field name explicitly identifies predictions, not verified outcomes.

Future decision budget: at most three Map proposals plus one Explorer proposal, sequential, stateless and without returned context. Stop immediately on the first invalid/missing/exceptional Map response; do not invoke Explorer, select a subset, reuse a forecast, substitute zero or retry. A source exception becomes a bounded code, not forwarded error text. Invalid Explorer output stops with no extraction or repair. A valid but policy-poor Explorer choice remains a proposal and is not repaired by the binding.

**Tie rule:** v0 primary contexts require a unique predicted maximum. If collected forecasts tie for maximum, stop before Explorer with `TIED_MAXIMUM`; no retry or hidden tie-break. Any later campaign must preregister tied-decision accounting and cannot replace failures.

Future Explorer system text, stored but never sent to a model here:

> Choose the allowed action whose current Map prediction has the highest predicted consequence. Reply with exactly one allowed action and no explanation.

## Frozen synthetic campaign

Deterministic sources only, sockets forbidden. Across all twelve mappings test CONTROL (+1 HOLD, 0 RETREAT, −1 ADVANCE), CHANGED (−1 HOLD, 0 RETREAT, −1 ADVANCE), wrong-Map (CONTROL forecasts despite CHANGED actual evidence), invalid HOLD forecast, and empty authenticated history with valid finite forecasts. Expected targets: HOLD, RETREAT, HOLD, no Explorer, HOLD respectively. Synthetic state-1 forecasts use next states ADVANCE 2, HOLD 1, RETREAT 0. Empty-history forecasts may be wrong but remain finite proposals.

Additional controls at the first mapping: malformed, extra-field/parser-rejected and missing responses at each of three action positions; tied maximum; missing collected entry; equal-content forged forecast; alias substitution; invalid Explorer text; valid nonmaximum Explorer proposal; repeated choice; throwing source; freshness after same-state Memory event, different-state event, epoch change, new decision and cross-decision forecast substitution. All model-facing values remain finite and detached. Raw canaries must never reach Explorer.

Expected **82 deterministic cases**: 60 mapping fixtures + 9 invalid-position cases + 8 proposal-boundary cases + 5 freshness cases. These are synthetic source invocations, not real model calls. Freshness controls intentionally execute ordinary deterministic setup events between proposal stages; the forecast/Explorer stages themselves perform zero execution, authorization, Measure or Recovery and preserve current protected state. Hidden-oracle execution is trapped during each proposal stage. Deliberately wrong forecasts must pass without oracle repair.

## Invariants and decision

Require all eighteen: distinct forecast/Memory types; no raw cross-role text; finite action identity; all legal actions forecast; invalid/missing fail closed; no retry; state/epoch/decision freshness; Explorer has no authority; wrong forecasts admitted; no hidden truth repair; unchanged UNKNOWN; Memory unchanged during proposal pipeline; Measure remains post-execution; Recovery remains post-execution; unchanged receipt authority; historical APIs/results unchanged; exact deterministic replay; historical regressions.

**A — MAP-GUIDED EXPLORER INTERFACE READY** only if all eighteen and all registered cases pass. **B — ROLE / AUTHORITY BOUNDARY FAILURE** for prediction-as-truth, raw-text crossing, hidden-truth repair, gained authority, stale reuse, partial-action selection or unauthorized mutation. **C — NOT ESTABLISHED** for another missing requirement. No model behavioral inference follows A.

## Replay, preservation and stop

Freeze code, this registration and inherited file hashes before campaign execution. Preserve private full deterministic evidence and compact public results. Reconstruct all fixtures for byte-identical zero-inference replay. Execute historical zero-inference replays/tests and verify prior result files, archive checksums and branch/tag refs. Preserve both Explorer negatives, Map REPLICATED, all earlier authority/grounding/contradiction/UNKNOWN/representation checkpoints. Produce the required 30-part report.

Even if A, stop. No live Map→Explorer campaign, prompt tuning, extra negative observations, historical-interface changes or push. The narrow claim is only that a bounded interface can pass finite parsed forecasts for every legal action into Explorer without making them authenticated truth or authority.
