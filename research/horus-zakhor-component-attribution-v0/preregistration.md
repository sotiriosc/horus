# Horus/Zakhor component attribution v0 — preregistration

Status: frozen before model inference. This is a descriptive 2×2 component
attribution study, not a winner selection or training campaign.

## Frozen source boundaries

- Parent system: Horus v0.22 at
  `1007622b8817ab82ba208ce6a198e85b24f3960d`.
- Horus ON: the current relation-local G2/G3 grounded selector, its authenticated
  chronological history projection, and the current finite grounded-exploration
  rule. The v0.22 durable runtime/receipt invariants remain the provenance model;
  no weights, thresholds, routes, or problem policy are changed.
- Zakhor ON: the current architecture-aware living-memory `keeper` controller,
  `soft` policy, default `MemoryConfig`, on-device path. The upstream Zakhor
  working tree is not a clean commit, so its exact current Python runtime is
  copied into this experiment and every file is content-addressed in
  `source-manifest.json`.
- Zakhor exposes process-local scalar activation trackers. It does not expose a
  durable authenticated semantic-memory or tracker-restore interface. This study
  will not claim those capabilities or add them.

## Neutral framework and toggles

One harness has exactly two registered booleans, `horus_enabled` and
`zakhor_enabled`, yielding F=(0,0), H=(1,0), Z=(0,1), HZ=(1,1).

The neutral base supplies fixed Qwen transport, a deterministic four-state task,
external execution, an append-only authenticated receipt/log chain, exact replay,
common scoring, and deterministic next-state transition prediction. These do not
adapt decisions. With Horus off, G2 is always selected and no authenticated
history is projected to the model. With Zakhor off, no hook/controller/tracker is
created. With both off neither adaptive state is available.

All arms load and call the same Qwen base revision and both identical frozen G2
and G3 adapter artifacts. G3 remains a shadow call when Horus is off so call count
and model assets do not change with condition. The only intended differences are
the two toggles: Horus may project authenticated relation history, select G2/G3,
and choose Stage-B actions; Zakhor may transform attention outputs and update its
existing online scalar trackers. Models are reloaded for each arm; no KV state,
hook, tracker, prompt history, routing state, artifact object, or receipt crosses
arms. Execution order is fixed and counterbalanced as F, HZ, H, Z.

No training, retries, threshold tuning, outcome-driven extension, or architecture
change is permitted.

## Workload

Stage A has 18 fixed events. Events 1–5 are stable; 6–11 use the prospective
state-1 reversal (ADVANCE becomes +1 and HOLD becomes -1); 12–18 restore the
original relations. The sequence repeatedly samples both changed relations,
retains contradictory old/new/restored receipts, and includes state-2 RETREAT
controls. A runtime restart occurs before event 10, solely by schedule. The
neutral receipt/history state and Horus routing evidence persist under a fresh
source identity and epoch. Zakhor trackers restart empty because the frozen
component has no restore interface.

The one registered disruption occurs at Stage-A event 14 in every matched arm:
after the real G2 call, its returned wire value is replaced with the invalid JSON
domain value `{"consequence":2}` before strict parsing. G3 and execution truth are
untouched. Recovery is the number of subsequent opportunities until an ordinary
valid selected prediction appears. There are no retries.

Stage B has six autonomous opportunities, beginning at state 1. Its hidden phase
schedule is stable, stable, change, change, restoration, restoration. Each arm
calls both specialists for all three actions. Horus arms use the frozen grounded
Explorer and relation selector; non-Horus arms use the existing mechanical
Explorer with fixed G2. An abstention executes nothing and manufactures no
counterfactual receipt.

## Call budget and execution order

- Stage A: 18 events × 2 specialist calls × 4 arms = 144 calls.
- Stage B: 6 opportunities × 3 actions × 2 specialists × 4 arms = 144 calls.
- Total: exactly 288 real local Qwen calls; no retries or extra calls.

The comparable v0.7 486-call campaign completed in about seven minutes. This
smaller campaign is expected to take roughly five to ten minutes without Zakhor
overhead; the first completion check will therefore be delayed, with backoff if
needed. The process writes a durable log and one result directory per arm.

## Measurements and inference

Report each condition separately: consequence, next-state, and exact accuracy;
authorized executions; abstentions; realized consequence; invalid outputs;
change and restoration latency; contradictory-history preservation; routing
switches; probes; unresolved contradictions; restart behavior; perturbation
recovery; call count; and model/wall time. Report early (1–8), middle (9–16),
late (17–24), and worst rolling six-opportunity windows.

Zakhor tracker integrity, drift, regime events, and restart continuity are
reported only from its actual tracker snapshots. Semantic provenance/retrieval
and authenticated durable restore are explicitly unsupported rather than
imputed from neutral receipts.

For numeric outcomes compute descriptive effects:

`H main = ((H + HZ) - (F + Z))/2`

`Z main = ((Z + HZ) - (F + H))/2`

`interaction = HZ - H - Z + F`

No combined score or significance claim is permitted. If this modest run shows
no measurable separation, report that and stop rather than scaling.

