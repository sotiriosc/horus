# Model proposal role composition v2 — interrupted checkpoint

**C — NOT ESTABLISHED. Live evidence unavailable after reported computer crash.**

Exact campaign totals are unknown. No replacement inference was performed.

## 1. Parent identities

Parent `research/composition-empty-history-schema-contract-v0`, commit
`14b427a23e381ff3891564f9f9208355297a7334`. This branch is `research/model-proposal-role-composition-v2`.
Preregistration `7d018aefc771908ff325d2f274a4a8bb54b753ff` and implementation
`c4d241400feb455a3dfcd88af4117ae0c20f66a5` survived in Git. The temporary worktree and
live evidence directory were absent after the user reported a computer crash.
A durable checkout was restored without changing frozen experiment source.
The final status is **C — NOT ESTABLISHED**, due to unavailable complete evidence.

## 2. Preserved composition-v1 C

Composition-v1 `0dcc5d8` remains **C — NOT ESTABLISHED**: 12 Explorer calls,
nine valid/three malformed Explorer outputs, nine malformed Map outputs, zero
executions, commits or Recovery calls. Its seven-file recorded-response replay
was executed again after recovery and matched byte-for-byte. Nothing is replaced.

## 3. Schema-contract evidence motivating v2

The preceding 18-call paired experiment remains **SCHEMA-CONTRACT EFFECT SUPPORTED**:
original A 0/9 valid; explicit B 9/9; all nine pairs improve; all eight frozen
criteria pass. Its five-file replay was executed after recovery and matched.
That result established bounded schema compliance, not composition or accuracy.

## 4. Exact sole protocol change

Only Map system text changes to the already-tested explicit contract in section 12.
Explorer/Recovery text, user projections, parsers, sampler, mappings, seeds, world
and authority are preserved. V2 runtime, transport and bounded-control source files
are byte-identical to v1, with their relative protocol import selecting the v2 Map
constant. No prompt adjustment followed an observed outcome or the crash.

## 5. Research question

Can Explorer, Map and state-Recovery model proposals participate in one sequential
grounded loop once the existing Map schema is explicitly communicated, while
reality, Measure, Memory and authorization remain outside the model? The interrupted
run does not establish the full answer.

## 6. Architecture

Unchanged Explorer parse/admission → Map parse and trusted Prediction latch →
external world execution/receipt → non-model Measure → optional genuine state
Recovery proposal → independent authorization → authenticated publication or
atomic rejection. Model roles supply finite values; they do not supply authority.

## 7. UNKNOWN IS NOT MEMORY

The same projection renders UNTRIED / [] only when the exact state/action has
zero authorized observations. After authenticated evidence, the absence marker
vanishes from the next projection for that pair only. No marker is an event.
The recovered 288-context preflight matches the pre-crash committed digest exactly;
all 12 initial Explorer inputs are checked. All seven required synthetic UNKNOWN
cases pass. Complete live enforcement cannot be re-audited without the lost trace.

## 8. Model/config

Registered dolphin-mixtral:latest; Ollama 0.1.16; GGUF 47B Q4_0.
Temperature .2, top_p .9, top_k 40, num_ctx 2048, repeat_penalty 1.1;
num_predict 16 Explorer, 32 Map/Recovery. Stateless, no returned context or
raw-role transcript carryover. Pre-crash tool output reported successful full
verification of five blobs, including weights. The detailed new proof and runtime
metadata were in the missing directory; they are not claimed as retained evidence.

Frozen manifest SHA256:
`4b33b01bf33672a36945cd5925ffc9e3997a5e4d3119c7d59150bee0d2a0214a`.
Weights SHA256:
`bdb11b0699e03d791f0accd97279989d810d79615c6cf5ac21fb68e8f33e8ca3`.
No model server or live campaign was restarted during crash recovery.

## 9. World/episodes

Registered unchanged stationary four-state/three-action world, state 0 and empty
Memory at each episode start. Twelve scheduled episodes, up to eight executions
each. No regime changes or injected experience. The last surviving console excerpt
covers episode 0 through decision 6; later progress and campaign completion are
unknown. No replacement episode was run.

## 10. Mapping/seed schedule

| Episode | Family | Mapping index | Alias → underlying action | Base seed |
|---|---|---|---|---|
| 0 | O1 | 0 | K1 → ADVANCE, K2 → HOLD, K3 → RETREAT | 80001 |
| 1 | O1 | 1 | K1 → ADVANCE, K2 → RETREAT, K3 → HOLD | 80002 |
| 2 | O1 | 2 | K1 → HOLD, K2 → ADVANCE, K3 → RETREAT | 80003 |
| 3 | O1 | 3 | K1 → HOLD, K2 → RETREAT, K3 → ADVANCE | 80004 |
| 4 | O1 | 4 | K1 → RETREAT, K2 → ADVANCE, K3 → HOLD | 80005 |
| 5 | O1 | 5 | K1 → RETREAT, K2 → HOLD, K3 → ADVANCE | 80006 |
| 6 | O2 | 0 | M4 → HOLD, Q7 → ADVANCE, Z2 → RETREAT | 80001 |
| 7 | O2 | 1 | M4 → RETREAT, Q7 → ADVANCE, Z2 → HOLD | 80002 |
| 8 | O2 | 2 | M4 → ADVANCE, Q7 → HOLD, Z2 → RETREAT | 80003 |
| 9 | O2 | 3 | M4 → RETREAT, Q7 → HOLD, Z2 → ADVANCE | 80004 |
| 10 | O2 | 4 | M4 → ADVANCE, Q7 → RETREAT, Z2 → HOLD | 80005 |
| 11 | O2 | 5 | M4 → HOLD, Q7 → RETREAT, Z2 → ADVANCE | 80006 |

Same v1 schedule. For zero-based decision d: Explorer base+100*d+1; Map +2; Recovery +3. Each episode keeps one bijection across all roles. No new seeds.

## 11. Explorer instruction/context

> Choose an action using verified prior outcomes. Higher observed consequences are preferable. UNTRIED means no verified observation; it does not mean consequence 0. When evidence is insufficient, you may choose an UNTRIED action to gather information. Reply with exactly one allowed action and no explanation.

Unchanged current authorized state, three legal opaque actions, chronological authenticated consequences or UNTRIED. Accept one offered token only; no extraction from malformed structured text.

## 12. Explicit Map instruction/context

> Predict the next externally realized outcome for the specified action using only the verified chronological outcomes shown. Reply with exactly one JSON object with exactly two fields: next_state must be an integer in {0,1,2,3}, and consequence must be an integer in {-1,0,1}. Do not include any other fields or explanation.

Unchanged user keys: state, target_action, VERIFIED_CHRONOLOGICAL_HISTORY. Untried pair history is []. No examples, domain arrays, canonical actions, fake observations or evaluator truth. Original strict parser remains unchanged.

## 13. Recovery instruction/context

> Propose the replacement state using only the verified Recovery context shown. Reply with exactly one JSON object containing replacement_state and no explanation.

Unchanged legitimate verified callback context only. Model supplies replacement_state; framework owns identity, pair, RECOVERING status, scope and attempt. Independent authorizer accepts/rejects. No retry.

## 14. Real call counts

Exact totals and per-role totals are **unavailable**, represented as null in
compact results. The last retained console progress line reports **18 cumulative
real calls**; this is a lower bound, not the total. Original request/response logs
are missing. **Zero new inference after recovery**, zero replacement calls.
Registered maximum remains 96 per role / 288 total; full actual bound compliance
cannot be rechecked from the incomplete surviving evidence.

## 15. Episode completion

The surviving progress excerpt reports seven executed/committed decisions in
episode 0, ending at zero-based decision 6 with no termination reported there.
It does not establish completion of that episode or any later episode. Completed
episode count, final termination reasons and unused-slot totals remain unknown.

## 16. Live path-coverage checklist

| Required live path | Complete auditable evidence retained? |
|---|---|
| A External world execution | Unavailable from missing raw trace |
| B Authentic committed Memory | Unavailable from missing raw trace |
| C Later decision after commit | Unavailable from missing raw trace |
| D Live Explorer absence → evidence | Unavailable from missing raw trace |
| E Live same-pair Map [] → history | Unavailable from missing raw trace |
| F Later proposal consumes same-episode Memory | Unavailable from missing raw trace |
| G Genuine Recovery reaches independent authorizer | Unavailable from missing raw trace |

Console output reports progress consistent with execution/commit/continuation, and early tool output showed Recovery responses. Those fragments are not a substitute for the complete transaction and authorization trace. No missing opportunity is manufactured; all final live coverage fields are null.

## 17. Primary classification

**C — NOT ESTABLISHED.** The frozen A rule requires all 20 integrity requirements
and all seven live paths, including exact replay. Exact live replay is unavailable;
therefore A cannot be claimed regardless of the partial progress. This is an
interruption/evidence-completeness result, not evidence that the model cannot compose
and not an observed protected authority failure B. Live integrity counts are
unknown, not silently reported as zero.

## 18. Explorer validity/behavior

Campaign calls, valid/malformed counts, action distribution, strict higher-mean
choices, known-worse choices, uncertain/sparse/conflicting and negative retests
cannot be recovered. No aggregate Explorer pass threshold was registered. The
unchanged analysis preserves retest distinctions and never bans an allowed action
because of one negative outcome.

## 19. Explorer coverage/revisits

Campaign state/action distributions, proposed/executed coverage, UNTRIED versus
tried selections and revisit opportunities are unavailable. They are not inferred
from episode progress lines. Historical Explorer results are preserved by executed
regressions; those are separate from v2 live behavior.

## 20. Map schema compliance

Complete valid/malformed and empty-history schema-compliance counts are unavailable.
Early surviving tool output contains two valid numeric Map objects, but this is
not a complete sample or an appropriate campaign denominator. The prior paired
9/9 explicit-contract result is retained separately and is not substituted for v2.

## 21. Map predictive metrics

Exact-outcome, next-state, consequence accuracy and prediction/receipt mismatch
counts cannot be computed without the retained paired predictions and receipts.
No accuracy is inferred from valid JSON or reported successful publication.

## 22. Map metrics by history depth

Depth 0, 1 and >=2 denominators and accuracy/compliance breakdowns are unavailable.
The frozen analysis supports these counts; missing input traces are not reconstructed
from model expectations or synthetic controls.

## 23. V1/v2 matched-format comparison

All nine historical v1 Map contexts remain malformed. Corresponding complete v2
raw calls are unavailable after the crash, so matched validity is unavailable.
This is **lost evidence**, not proof that Explorer failed to reach those contexts.
No missing comparison call was issued and no v1 response was changed.

## 24. Recovery opportunities/calls

Early console-visible raw responses show Recovery was invoked, but total genuine
opportunities, calls and routing records are unavailable. New synthetic routing
tests verify the wrapper; they do not fill the missing live denominator.

## 25. Recovery proposal outcomes

Complete correct/legal-wrong/malformed counts and target-state/action/token
breakdowns are unavailable. No usefulness threshold is introduced and no missing
proposal is replaced.

## 26. Independent Recovery authorization

The original authority implementation is unchanged. Post-interruption tests show
correct callback routing, legal wrong independent rejection and that malformed
Recovery alone does not satisfy coverage G. The lost live authorizer trace prevents
complete audit of live accept/reject counts, attempt ownership and atomicity.

## 27. UNKNOWN→known transitions

Live transition totals and before/immediate-next projection records are unavailable.
The seven reported commits are not assumed to be seven distinct first-observation
transitions. Regenerated preflight and historical binding replay preserve the
correct absence-to-authenticated-evidence behavior.

## 28. Stale-UNTRIED audit

Zero stale markers are established in the executed bounded synthetic checks.
The full live stale-marker count is unknown; there is no claim that missing live
records passed an audit. No marker was newly inserted during crash recovery.

## 29. []→history transitions

The recovered routing/history unit test demonstrates same-episode authenticated
Map history and removal of the initial empty view in a synthetic fixture. The
required live same-pair projection transitions cannot be certified without raw
requests. Synthetic evidence is not counted as live path E.

## 30. Experience-use chains

Complete Explorer, Map and Recovery chains are unavailable. The original recorder
and analysis source survived; its missing input events were not invented. No
in-context behavior is described as weight learning.

## 31. Explorer revisit chains

Explorer → execution → receipt → commit → later same-state Explorer chains cannot
be enumerated after loss of the live trace. Console continuity alone does not
identify which authenticated observations a later proposal consumed.

## 32. Map revisit chains

Wrong→exact, exact→exact, exact→wrong, wrong→different-wrong, same-wrong and malformed
revisit counts are unavailable. No revision or causal learning claim is made.

## 33. End-to-end Recovery chains

Wrong-state Prediction → receipt → Measure → Recovery → independent decision →
later behavior chains require the missing detailed trace. Early Recovery outputs
and console commits are not enough to reconstruct their binding or certify all
paths. No external event or wrong prediction was injected to replace a lost chain.

## 34. Realized/authorized consequence

Realized sums, committed-realized sums and authorized consequence totals are
unavailable. Successful-commit console labels do not reveal consequences or prove
the complete equality check. Historical grounded receipt results remain intact.

## 35. Memory growth

The surviving console reports at least seven commit events in episode 0. Final
Memory size/content, complete growth, eviction and historical retention cannot be
audited from that excerpt. No new Memory was seeded and no unknown marker, model
text or unexecuted choice was substituted for the missing records.

## 36. Representation breakdown

Both O1 and O2 remain in the unchanged registered schedule. Complete actual family
counts, termination patterns and role metrics are unavailable. The surviving
excerpt is O1 episode 0 only; it does not establish O2 coverage or neutrality.

## 37. Cross-role leak audit

Frozen transport constructs stateless requests from only model/system/prompt/options;
raw texts pass only through existing finite parsers. The recovered source equality
and synthetic routing tests pass. Complete request-by-request live verification
cannot be repeated, so the live leak count remains unknown, not asserted zero.

## 38. Role-boundary controls

After recovery, the exact inherited bounded control set was executed once with
zero inference: **5 Explorer / 14 Map / 22 Recovery**, all passing. This is recorded
as **post-interruption synthetic evidence**, not completion of the live campaign.
No additional attack campaign was created. Five v2 unit tests also passed.

## 39. Model authority audit

Unchanged roles: Explorer action proposal only; Map finite Prediction proposal
only; Recovery replacement-state proposal only. Reality is the external receipt
source. Measure, authenticated Memory and authorizers are non-model. Frozen source
hashes and historical authority/interface/status regressions pass. Full live
operation remains unauditable because its records are missing; no self-authorization
or general intelligence claim follows.

## 40. Exact replay

**Unavailable for v2.** Its live schedule/prompts, raw responses, transactions,
receipts, decisions, Memory, stops and chains were in the missing temporary archive.
Replaying synthetic fixtures or old studies cannot substitute for this exact replay.
The old v2 finalizer was not run with fabricated assurance. Original live totals
and integrity metrics remain null in the interrupted result.

Available historical exact replays were actually executed: schema contract (five
files), forensic diagnosis (two), composition-v1 (seven), bindings (three) and
composition-v0 (two), all byte-identical. The recovered preflight also matches its
pre-crash committed private-evidence digest. No new model inference was used.

## 41. Regressions

**41 zero-inference commands/checks executed after recovery**, all with expected
exit status: 33 inherited historical commands, five additional preserved-checkpoint
replays, recovered preflight, v2 tests and one inherited bounded-control invocation.
Expected negative checkpoints returned their registered nonzero exit statuses.
These cover Recovery v1/status/interface, Map v1/v0, Explorer contradiction,
feasibility, factorial, semantic, adaptive, Memory/original, realized-event grounding,
minimum repair 1, base v0/v1/v2 and the old contradiction-v0 diagnostic.
`verification.json` retains actual commands, timestamps, exits and log digests.
V2 live replay is explicitly absent and is not counted as a passing check.
All 456 substantive inherited files remain byte-identical; only root README and
public manifest add the new interruption checkpoint. Main/tags remain unchanged.

## 42. Limitations

The live archive was written under temporary storage and was not durably copied
before the computer crash. That storage choice prevented reliable continuation
and exact replay. The complete original call count and progress after the last
observed console line are unknown. The precise crash/deletion mechanism is not
established. A console excerpt is weak partial evidence, not a replacement dataset.
Synthetic/historical passes do not repair this missing live evidence. Even an
uninterrupted original design would remain a small fixed-model, fixed-world study.

## 43. Narrowest defensible conclusion

The preregistered v2 implementation survived and passes its zero-call checks.
Partial surviving console output reports at least 18 model calls and seven commits,
but the complete live evidence and exact replay are unavailable after the reported
crash. Therefore **full multi-role composition is NOT ESTABLISHED by this run**.
The earlier schema-contract SUPPORTED result and all historical checkpoints remain
unchanged. This is not a scientific finding of model inability or authority failure.

## 44. Recommendation

Preserve this interrupted checkpoint. If the original live evidence is recovered,
inspect it before any continuation and never duplicate a completed/in-flight call.
Otherwise a fresh campaign requires a separate explicit decision because the
original protocol forbids replacement calls/episodes and another composition run.
Use durable, incrementally flushed evidence storage before any future authorization.
No live campaign was restarted, prompt tuned, parser relaxed, Memory fabricated,
architecture altered, or result pushed during this recovery.
