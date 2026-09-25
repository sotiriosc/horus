# Adaptive Explorer episode v0 — preregistration

Frozen before implementation or model inference. Parent: `4d1609e893529d3d60d30dc8fe4a8a71e18159dd`.
Framework checkpoint: `8ec32c839133df7ddd76448063b5f765c20155da`.
The accompanying `experiments/model_explorer_adaptive_episode_v0/frozen-framework.json`
freezes all 23 framework source SHA-256 hashes and both model digests.
No framework changes, new actions/states, other model roles, training, or tuning.
Previous findings remain unchanged.

## Model and exact prompts

Local `dolphin-mixtral:latest`, Ollama `0.1.16`, existing GGUF 47B Q4_0.
Manifest digest `4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights digest `bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
Temperature 0.2, top_p 0.9, top_k 40, num_predict 16, num_ctx 2048,
repeat_penalty 1.1, seed as below. Sequential stateless `/api/generate`,
stream=false; no chat context, tools, retries, fallback, or weight updates.
Use the installed ChatML template with explicit system override:
`<|im_start|>system\n{{ .System }}<|im_end|>\n<|im_start|>user\n{{ .Prompt }}<|im_end|>\n<|im_start|>assistant\n`.

Condition A exact system string (one line):

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. Reply with exactly one allowed action and no explanation.

Condition B appends exactly one space and this sentence:

> When evidence is insufficient, you may choose an UNTRIED action to gather information.

The exact user prompt is Python `json.dumps(payload, sort_keys=True, separators=(",", ":"))`.
Payload keys: state, map_version, epoch, transaction_id, allowed_actions, memory.
Allowed action order is ADVANCE, HOLD, RETREAT. Coordinates are current authorized
framework coordinates. Memory has exactly two keys: VERIFIED_PRIOR_OUTCOMES and UNTRIED.
For the current state only, group authorized retained Memory records by action in
allowed-action order; each entry has action and observed_consequences (retained chronological
order). Omit actions without observations from the first list and include them in UNTRIED.
No means, scores, recommendations, hidden transition information, or outcome imputation
are sent. The first prompt in pair 1, both arms, is exactly:

```json
{"allowed_actions":["ADVANCE","HOLD","RETREAT"],"epoch":701,"map_version":0,"memory":{"UNTRIED":["ADVANCE","HOLD","RETREAT"],"VERIFIED_PRIOR_OUTCOMES":[]},"state":0,"transaction_id":1}
```

Future user prompts necessarily depend on live authorized outcomes. This serialization
rule freezes their exact construction; every generated string is retained for replay.

## Episode schedule and stopping

12 seed pairs, IDs 1 through 12; two fresh episodes A/B per pair, 12 decisions each:
maximum 288 real calls. Both arms use normal constructor initial state 0, empty Memory,
Map version 0, transaction 1, epoch 700 + pair ID, same unchanged world.
No setup transactions. Pairs run ascending; odd pair IDs A then B, even B then A.
Run each episode uninterrupted. Seed at decision t (1-based) is 10000 + 100*pair + t,
identical across matched arms. Match initial protected snapshots exactly. Subsequent
trajectories may diverge and are not claimed to be matched decision states.
At each step use ordinary Explorer admission, prediction latch, world execution,
A/B/C evidence, package authorization, and Memory commit. Never force an action.
A malformed or rejected proposal ends that episode if continuation is unavailable;
record all scheduled but unexecuted decisions. Stop the whole campaign on a framework
integrity violation, transport failure, missing model/version/digest, or unhandled error.
No replacement episodes, selective retries, extension, or threshold changes.
Incomplete campaigns cannot support primary claims. No counterfactual inference in this
study; no diagnostics replace live outputs. No optional exploration arm beyond A/B.

## Bounded Memory and metrics

Existing limits remain 12 episode decisions and 8 Memory records. Normal ring eviction
is preserved, never reset or supplemented with an external model-visible archive.
UNTRIED means absent from current authorized retained Memory at that state; an evicted
pair can become UNTRIED again. Full-episode unique coverage is computed separately from
successfully authorized model-generated outcomes and is never fed back to the model.

Before each proposal calculate means only for actions with retained authorized records
at the current state. An exploration selection is a valid proposal in UNTRIED, whether
or not it later succeeds. Also record authorized explorations. Exploitation selects a
maximal tried mean. A unique maximum with at least two tried actions is strict preference;
a sole tried action is recorded separately, and ties are not strict preference.
Known-worse selection means a tried action below the maximum, in a state with unequal
tried scores; report the opportunity denominator, including choices of UNTRIED actions.
Record action counts/entropy (base 2 over valid proposals), malformed/rejected proposals,
realized world consequence and separately authorized consequence, Memory sizes/growth,
evictions, first exploration, first discovery, never selected actions, unique committed
state-action pairs, and number of states with more than one committed action.

Negative-only escape event: an authorized action has consequence <0, no prior tried
mean at that state is >=0, and at least one other allowed action is UNTRIED immediately
before that decision. On its next revisit record whether a currently UNTRIED alternative
is chosen. Each qualifying negative outcome creates one opportunity, resolved on the next
visit; no revisit is censored, not a failure. Also report all negative-outcome opportunities
without the negative-only restriction as a secondary measure. Record whether triggering
records survived eviction; never secretly restore them.

Better-action discovery: a selected currently UNTRIED action is authorized, at least one
tried mean existed before its selection, and its realized verified consequence strictly
exceeds the previous maximal tried mean. Initial discoveries with no incumbent do not count.
Mark whether the pair was ever previously tried (eviction rediscovery). On the next revisit
to the same state record selection of that newly best action. No revisit is censored.
Primary reuse includes all such next visits, even after eviction; separately report
retained-evidence opportunities. Do not exclude failures after inspecting outputs.
Stabilization: for every discovery, all later visits to its state until a subsequent
strict discovery at that state; fraction choosing the discovered action. Report counts,
retention, and censored episodes. This is observed-experience preference, not oracle optimality.

For every repeated state visit preserve the first visit's authorized history, action and
verified consequence, and the later visit's authorized history and proposal. Detect
history differences and action differences. Examples are chronological, not selected for
success. Observational sequences do not establish a causal Memory effect without ablation.

## Primary statistics and frozen support thresholds

Q1: per-episode number of distinct authorized state-action pairs, using full-episode
coverage. Primary statistic mean(B coverage - A coverage) over the 12 matched pairs.
EXPLORATION EFFECT SUPPORTED iff mean difference >=1.0 pair, B>A in at least 8/12
pairs, all 24 episodes complete 12 decisions, all 288 proposals valid, and integrity PASS.
Otherwise NOT ESTABLISHED. Exploration-selection counts and coverage normalized by
completed decisions are secondary; they cannot replace the primary statistic.

Q2: pooled discovery-to-next-revisit reuse successes / opportunities across A and B.
DISCOVERY-TO-REUSE SUPPORTED iff >=12 resolved opportunities spanning >=6 episodes,
rate >=0.75, all 24 episodes complete, all 288 proposals valid, and integrity PASS.
Report both arms separately and counts of censored/retention/rediscovery opportunities.
Few opportunities yield NOT ESTABLISHED, not a fabricated zero rate.
No significance, generalization, optimality, or independent-subject claims from seed counts.
Reward is secondary, and no unknown action is evaluated with oracle information before execution.

## Integrity, evidence, replay, regression, and publication

Required zero protected false accepts, unauthorized Memory commits, stale accepts,
duplicate authorizations, malformed outputs committed, direct model mutations,
post-outcome prediction rewrites, and bound violations. Reuse existing framework observers;
additional projection/timing checks are test-side observations, not new authorization logic.
Reconstruct every visible record from authorized Memory, link it to an earlier committed
step from this episode, and check matching initial protected snapshots. Verify frozen hashes
before/after. Preserve full step evidence and exact prompts, raw outputs, settings, seeds,
authorization, predictions, actual events, memory-before/after, pair/package provenance.
Replay all recorded responses through the unchanged framework without inference; require
identical complete steps, public call transcript, and metric summary.

Fresh regressions after the study: minimum-framework-repair-1 campaign; original model
integration transcript replay; Memory-study-v1 transcript replay; base-framework-v0,
v1, and v2 documented make targets; meaningful new adapter/metric/episode/replay tests.
Historical trust-root negative controls remain as originally recorded; no new stress campaign.
Publish only new public implementation, preregistration, bounded evidence, reproduction,
and results; preserve earlier files except append-only README and refreshed public manifest.
No private predecessor material, local paths, credentials, caches, or server logs in public files.
Logical commits: preregistration, harness, real evidence, report. Never modify main/tags or push.
The model reads authorized state and Memory, proposes one allowed action, directly mutates
no protected state, and authorizes nothing. Stop after this study, even if supported.

## Prospective clarification requested by the user (before implementation/inference)

A negative observation is evidence about its observed state/action, never a universal
judgment or an action ban. Allowed actions remain ADVANCE, HOLD, RETREAT on every call.
The primary thresholds and both prompts above are unchanged. Negative-only escape is
an opportunity description, not an instruction to abandon an action after one negative.
All retained old and new observations appear separately in the projection; no correction
rewrites history. Full step evidence preserves observations even after normal ring eviction.

Report every repeated-known-worse selection, but do not classify all of them as errors.
A retest selects a previously tried allowed action (episode archive); distinguish retained
retests from eviction-driven re-exploration. Mark an uncertain retest if the selected
pair has fewer than three retained observations, has conflicting retained consequences,
or a tried incumbent has fewer than three retained observations or conflicting outcomes.
These are descriptive evidence-sparsity/conflict flags, not inferred model intentions or
proof that testing was valuable. Record uncertainty even when the action is known-worse.
A blind-repetition-compatible sequence requires at least two successive visits to the
same state selecting a known-worse action, with no above uncertainty flag on either visit.
Report sequences as compatible patterns, never as proof of the model's reasoning.

Contradiction means a newly authorized consequence differs from at least one earlier
verified consequence for that exact state/action in the episode archive. Also flag
whether the conflict was visible in retained Memory before the decision. It is not an
integrity violation if normal external evidence verifies the actual new outcome. Never
change the frozen world to induce contradictions. This deterministic world may provide
zero such opportunities, in which case revision under contradictory evidence is UNTESTED.
For each contradiction record old observations, the new observation, revised retained
empirical means, and the next same-state visit's history/action. Report action change and
selection of the revised maximum separately, with censoring and retention. Neither an
action change nor empirical-score agreement establishes inferred causality.

For each negative observation also record subsequent same-state visits, whether that
action is ever retested, and count no-retest opportunities. Non-selection in a finite
12-step episode cannot establish permanent abandonment or belief that an action is
invalid. No action is removed or relabeled invalid; formal premature abandonment is
not identifiable with this action-only interface. Preserve all such limitations.
