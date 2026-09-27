# Horus/Zakhor component attribution v0 — results

Execution status: **COMPLETE; PROTECTED-AUTHORIZATION CLAIMS NOT ESTABLISHED**.
The frozen 288-call campaign ran once with no retry,
training, extension, or post-result component change. Exact zero-inference replay
passed all four 169-record HMAC/hash chains, all 288 request/response pairs,
all 96 decision records, all recorded receipt-value hashes, and the four registered
perturbations. The result supports attribution only for this small workload.

The post-run validity audit found that the neutral harness used receipt-shaped
values rather than the current protected receipt capabilities and independent
authorization path. Therefore the behavioral prediction/routing evidence below
is replayable, but protected authorization, original-receipt identity, and
protected restart integrity are not established. See `validity-audit.md`.

## Frozen matrix and boundaries

| Condition | Zakhor OFF | Zakhor ON |
|---|---:|---:|
| Horus OFF | F | Z |
| Horus ON | H | HZ |

The neutral framework supplied the fixed Qwen base revision, both frozen G2/G3
adapters, deterministic next-state transition, world execution, original receipt
shaped values, append-only chained logging, and common scoring. It supplied no
adaptive decision state. Both specialists were called in every arm, including as
shadows when Horus was off.

Horus ON used the v0.22 current relation-local selector, authenticated
relation-history projection, and frozen grounded Explorer rule. The workload did
not invoke the v0.22 problem/route-handoff subsystem, so this result does not
attribute that dormant surface. Zakhor ON used the frozen current
architecture-aware `keeper` hooks, `soft` policy, default configuration, and
process-local per-layer scalar trackers. Zakhor did not supply semantic history,
receipt provenance, authorization, or durable tracker restore because its actual
interface does not implement them.

Structural preflight proved the single harness had only `horus_enabled` and
`zakhor_enabled`; disabled Horus arms had no router/Explorer/history projection,
disabled Zakhor arms created no controller/tracker, all arms used fresh model
instances, no state crossed arms, and the same artifact hashes were loaded. The
condition order was F, HZ, H, Z; fresh loads remove model/runtime carryover.

## Stage A — fixed observations

All arms received the same 18 external events: five stable, six changed, and
seven restored, with a scheduled restart before event 10 and a registered G2
wire corruption at event 14.

| Condition | Correct | Accuracy | Invalid | Executions | Realized sum |
|---|---:|---:|---:|---:|---:|
| F | 9/18 | 50.0% | 1 | 18 logged | 2 |
| H | 6/18 | 33.3% | 1 | 18 logged | 2 |
| Z | 9/18 | 50.0% | 1 | 18 logged | 2 |
| HZ | 6/18 | 33.3% | 1 | 18 logged | 2 |

The descriptive Stage-A Horus main effect was **−16.7 percentage points**,
Zakhor's was **0.0 points**, and the aggregate interaction was **0.0 points**.
These are paired descriptive differences, not significance estimates.

Neither F nor Z adapted to either changed state-1 relation within the observed
window. H first became correct on changed ADVANCE at its third changed
observation and never on changed HOLD. HZ did not become correct on either within
the change window. Restoration was immediate for both relations in F/Z; H did
not become correct on either restored relation; HZ was immediate on ADVANCE but
not HOLD.

False persistence after the change was F=6, H=5, Z=6, HZ=6. False persistence
of changed values after restoration was F=0, H=5, Z=0, HZ=4. Total restoration
errors were F=1, H=6, Z=1, HZ=5. Thus the Horus history/routing path did not show
reliable relation-local revision in this schedule and persisted stale changed
values during restoration.

The neutral value chain preserved both old and contradictory outcomes for two
relations in every arm. Those histories were model-visible only in H/HZ. F/Z
retained the evidence externally but did not project it to the model. Zakhor did
not expose semantic retrieval or provenance, so no such capability is attributed
to it.

## Stage B — autonomous trajectories

| Condition | Actions | Correct | Accuracy | Abstain | Realized sum |
|---|---|---:|---:|---:|---:|
| F | HOLD × 6 | 4/6 | 66.7% | 0 | 2 |
| H | HOLD, HOLD, HOLD, RETREAT, HOLD, HOLD | 3/6 | 50.0% | 0 | 1 |
| Z | HOLD × 6 | 4/6 | 66.7% | 0 | 2 |
| HZ | HOLD, HOLD, HOLD, RETREAT, HOLD, HOLD | 3/6 | 50.0% | 0 | 1 |

The Stage-B Horus main effect was **−16.7 accuracy points** and **−1 realized
consequence unit**. Zakhor and aggregate interaction effects were zero. Horus
issued two rule-qualified probes in both H arms. Neither probe's selected
prediction was correct; the second changed the trajectory by selecting RETREAT.
No preregistered threshold labels a qualified probe “unnecessary,” so the report
records this ex-post outcome without rewriting the rule.

H/HZ acquired 24 authenticated relation evidence rows, made three specialist
selection changes (A11 HOLD, A16 ADVANCE, B1 HOLD), and ended with no unresolved
contradictions. No capability problem, route request, or problem resolution was
created because that subsystem was not exercised. There were no autonomous
invalid forecasts and therefore no autonomous fail-closed event.

## Combined condition metrics

| Metric | F | H | Z | HZ |
|---|---:|---:|---:|---:|
| Consequence accuracy | 54.2% | 37.5% | 54.2% | 37.5% |
| Next-state accuracy | 100% | 100% | 100% | 100% |
| Exact accuracy | 54.2% | 37.5% | 54.2% | 37.5% |
| Logged external executions | 24 | 24 | 24 | 24 |
| Abstentions | 0 | 0 | 0 | 0 |
| Invalid selected outputs | 1 | 1 | 1 | 1 |
| Realized consequence | 4 | 3 | 4 | 3 |
| Router switches | 0 | 3 | 0 | 3 |
| Explorer probes | 0 | 2 | 0 | 2 |
| Model calls | 72 | 72 | 72 | 72 |
| Model time (s) | 2.418 | 2.318 | 24.961 | 46.275 |
| Arm wall time (s) | 8.671 | 4.044 | 26.792 | 48.160 |

Next-state accuracy is 100% by construction because the neutral deterministic
transition is shared infrastructure; it is not evidence of model next-state
learning. Exact accuracy therefore equals consequence accuracy here.

Across combined accuracy, the Horus main effect was −16.7 points, Zakhor's was
0.0, and H×Z was 0.0. F and Z produced identical predictions, actions, and
aggregate outcomes. H and HZ produced identical actions and aggregate outcomes,
but Zakhor changed two Stage-A G2 predictions: it made changed A10 worse and
restored A12 better, canceling in the aggregate. This is context-sensitive
interaction without net benefit, not evidence of synergy.

## Endurance windows

| Condition | Early 1–8 | Middle 9–16 | Late 17–24 | Worst rolling 6 |
|---|---:|---:|---:|---:|
| F | 50.0% | 50.0% | 62.5% | 0.0% (start 5) |
| H | 50.0% | 12.5% | 50.0% | 0.0% (start 11) |
| Z | 50.0% | 50.0% | 62.5% | 0.0% (start 5) |
| HZ | 50.0% | 12.5% | 50.0% | 0.0% (start 5) |

All arms had one invalid in the middle window and none early or late. H's worst
window included the invalid; the others' worst windows did not. Every condition
reached a zero-accuracy rolling window, so none maintained strong prediction
coherence throughout. F/Z were the least degraded on this schedule; H/HZ showed
the largest middle-window drop.

## Perturbation and restart

The one matched wire corruption per arm produced exactly one strictly rejected
G2 value. The next ordinary selected prediction was valid in every arm, giving a
one-opportunity recovery count. Since Stage A presents externally controlled
observations, execution proceeded independently of the prediction; this does not
test autonomous fail-closed authorization. Zakhor did not detect the wire-level
corruption; strict neutral parsing did.

At restart every arm used a fresh recorded source identity and epoch. H/HZ
retained all nine prior receipt values and nine routing rows.
Zakhor's pre/post tracker hashes differed and its state was explicitly not
restored, matching the frozen component's lack of a durable restore interface.
The final tracker hashes prove distinct process-local evolution in Z/HZ, but the
full scalar snapshots were not written. Internal regime-event, stranger-element,
and drift curves therefore cannot be recovered from this completed campaign.
Because the harness never held current protected receipt objects, causal receipt
identity and protected restart recovery are not established.

## Attribution

Horus caused history projection, relation-specific specialist switching, two
probe decisions, and a different autonomous trajectory. In this workload those
changes reduced accuracy and realized consequence and increased stale-value
persistence after restoration. This does not generalize to untested workloads or
to Horus's dormant problem/route-handoff path.

Zakhor caused substantial inference overhead and process-local tracker evolution.
It caused no net accuracy, action, or trajectory change. Its two HZ prediction
changes canceled. The evidence supports behavioral redundancy with F in the Z
arm and mostly redundancy with H in HZ, plus a large latency interaction from
longer Horus history prompts passing through Zakhor hooks.

The descriptive model-time Zakhor main effect was +33.25 seconds across an arm;
H×Z added +21.41 seconds beyond additive timing. Z took about 10.3× F model time,
while HZ took about 20.0× H. Timing includes this machine and short run and should
not be treated as a general throughput benchmark.

What persists without either component is the authenticated external evidence,
strict parsing, deterministic next-state path, and the base G2 behavior. Removing
Horus removed adaptive routing/history projection and produced the better results
here. Removing Zakhor left the same aggregate behavior with much lower latency.
Nothing beneficial emerged only in HZ in this campaign.

## Limitations

- One deterministic schedule, one execution order, 24 opportunities per arm,
  and no statistical replication support only descriptive attribution.
- The neutral deterministic next-state path prevents attributing next-state
  reasoning to either component.
- The neutral harness bypassed current protected receipt capabilities and the
  status-bound authorizer. Its `authorized_executions` JSON field means logged
  executions; protected authorization and original-receipt identity are not
  established.
- Horus's full problem manager and durable route-handoff recovery remained
  dormant; this is direct attribution of the decision-relevant router/history/
  Explorer surface, not every v0.22 subsystem.
- Stage-A execution is observation-controlled, so its registered invalid tests
  parsing and recovery but not autonomous fail-closed authorization.
- Zakhor has no durable semantic-memory/provenance interface. The harness also
  failed to preserve full tracker scalar snapshots, so internal drift and regime
  curves are unavailable. The campaign was not rerun after this reporting defect.
- The large Zakhor latency cost and lack of behavioral separation argue against
  scaling this exact study before a more focused, prospectively registered reason
  exists. Per the preregistration, no scale-up follows.
