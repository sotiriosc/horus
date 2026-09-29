# R1 outcome: INVALID_STUDY (replacement_id: R1)

R1 stopped before the first completion dispatch: **0/80 attempted, 0/80 completed,
80/80 NOT_RUN**. The frozen real runtime accepted readiness and properties requests,
then returned **HTTP 501** to the first `POST /slots/0?action=erase`. This is a runtime
control-path compatibility failure, not a model answer or diagnostic-quality result.
The server was terminated. No flags were changed, no slot-clearing step bypassed,
and no request, startup or campaign was retried after this stop.

The exact original scorer taxonomy is preserved, as authorized: `INVALID_STUDY`
with `replacement_id: R1` separately in outcome.json. No scorer output was renamed.

## Chronology and freezes

| Entry | Classification | Model requests/completions |
| --- | --- | --- |
| Original v0 campaign, bb58926e0f2581bee38393e179b758b18d0879e4 | INVALID_STUDY | 0 / 0 |
| Independent R1 replacement | INVALID_STUDY, replacement_id R1 | 0 / 0 |

- R1 branch: `research/blind-diagnostic-generalization-v0-replacement-r1`.
- R1 Transport Freeze: `2600f2443662757f78487347bd329c5ca9d322ee`.
- R1 raw evidence committed before scoring:
  `e62632048d34ff227bc8e2194c0f0f03b7c760d3`.
- Original Method Freeze: `587ffedd39516b633376d222d6d84e6af186fcf8`, unchanged.
- Original Case Freeze: `2866e6bcf94539513c135df878b72058048e99cd`, unchanged.

## Zero-model transport qualification and real runtime checks

**21/21 tests passed**, including a full 80-request mock schedule delivered using
exact inherited request bytes. Actual HTTP tests covered readiness, properties,
slot erasure, slot inspection, completion POST, envelope handling, HTTP failures,
connection loss, timeout, at-most-once dispatch, no retries, preserved malformed/
empty/truncated finals, absent answer feedback, raw hashes, cleanup and mock/science
separation. Mock evidence remained QUALIFICATION_ONLY in temporary directories and
was removed; no dummy response was supplied to the scientific scorer.

The historical regression calls the real `http_request` helper against a loopback
mock and asserts HTTP 200 plus the parsed readiness envelope. The transport imports
`http.client as http_client` and never binds a helper named http. The full mock
runner and the actual real-runtime readiness/properties paths succeeded, so the
original name-shadowing failure did not recur.

Exact model, both runtime archive and installed executable hashes matched the
original model-runtime.json before launch and after stopping. Executable identity
reported build 11242 / commit 526c43b8f; the real properties endpoint reported
`b11242-526c43b8f` and one slot. Full frozen commit:
`526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`. Command/cwd were copied unchanged from
original campaign/launch.json. Sampling/seed/budgets remain in the exact frozen
requests. They were not exercised because no completion was dispatched.

## Exact stop and evidence order

Stop occurred at 2026-09-29T13:06:07.237486+00:00, before scheduled rendering
`e24ffa812432f3e62a4e` (call 1). The exception is preserved verbatim:
`TransportFailure: Slot erase HTTP 501`.

The transport cannot proceed without required fresh-context controls; the inherited
runtime/transport stop rule therefore takes precedence over completing the schedule.
All 80 statuses are NOT_RUN, not failed model answers. The HTTP error response body
was not retained by the frozen transport before its status check raised; this limits
attribution of the underlying 501 cause. No additional request was made to recreate
that body. The status, exception, successful properties response/hash and private
server log are preserved. No claim about the precise server-side cause is inferred.

Raw execution metadata and its SHA-256 were frozen, marked read-only and committed
at e626320 before primary scoring. There are no raw final strings because there were
no model responses; none were fabricated. The frozen scorer received the empty
final-string mapping and recorded violation, producing scores.json. Exact replay
reproduced score bytes with zero new inference. Private intent/properties/server
logs remain outside Git; their hashes are in private-evidence-manifest.json. No
private reasoning exists or entered scoring.

## Scientific measurements: not observed

Schema-valid answers: **0 of 0 returned**, not a measured 0/80 model success rate.
All primary performance counts and gates are NOT_EVALUATED: the inherited scorer
returns INVALID_STUDY before calculating them. A PASS/FAIL label for unexecuted
scientific gates would fabricate an observation. secondary-analysis.json contains
all 80 rendering statuses, 20 semantic statuses, six pairs and every frozen gate.

| Mandatory gate | Inherited requirement | R1 measurement |
| --- | --- | --- |
| Semantic classification | >=17/20, each >=3/4 renders | Not evaluated |
| Current-defect classification | >=5/6 | Not evaluated |
| Mechanical localization | >=4/6 | Not evaluated |
| Healthy avoidance | 4/4 | Not evaluated |
| Healthy-rendering current false positives | 0/16 | Not evaluated |
| Historical avoidance | 3/3 | Not evaluated |
| Historical-rendering current false positives | 0/12 | Not evaluated |
| Insufficient evidence | >=3/4 | Not evaluated |
| Invalid evidence | 3/3 | Not evaluated |
| Counterfactual pairs | >=5/6 | Not evaluated |
| Representation consistency | >=16/20 | Not evaluated |
| Evidence grounding | >=17/20 | Not evaluated |
| Invented-ID outputs | 0 | Not evaluated |

| True class | Current selected | Healthy selected | Insufficient selected | Historical selected | Invalid selected | NOT_RUN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Current defect | 0 | 0 | 0 | 0 | 0 | 24 |
| Healthy | 0 | 0 | 0 | 0 | 0 | 16 |
| Insufficient evidence | 0 | 0 | 0 | 0 | 0 | 16 |
| Historical only | 0 | 0 | 0 | 0 | 0 | 12 |
| Invalid evidence | 0 | 0 | 0 | 0 | 0 | 12 |

Labels A/B each completed 0/40; presentation orders 1/2 each completed 0/40. Accuracy
and disagreements are unmeasured. Component errors, causal-witness errors, ID errors,
false positives, historical/current confusion and abstention behavior are unknown.

| Family | Scheduled renders | Completed | Classification/localization |
| --- | ---: | ---: | --- |
| Version selection | 20 | 0 | Not measured |
| Authority precedence | 8 | 0 | Not measured |
| Entity binding | 12 | 0 | Not measured |
| Publication update | 16 | 0 | Not measured |
| Operation idempotence | 12 | 0 | Not measured |
| Boundary comparison | 12 | 0 | Not measured |

Each family includes one current-defect world with four unexecuted renderings.
No conclusion about model diagnostic capability follows.

## Preservation, publication and limits

All **1599 inherited parent files**, including the original failed campaign, remain
byte-identical. All nine R1 Transport Freeze files remain unchanged. All 184
materialized hashes and 80 request hashes match; no worlds or opaque maps were
regenerated. Seven protected branch heads remain unchanged, including the original
v0 branch. All 15 private-archive heads remain outside this public ancestry.

No retries, answer repairs, critics, auditor rescue, Horus world execution, receipts,
Memory writes, training, policy/threshold changes, architecture modification or
improvement proposals. One R1 model-server process was started and terminated;
completion requests and completions remained zero. Active S+E and earlier research
classifications are preserved. Only R1 is published after the repository's unchanged
full reachable-history secret audit; the exact final head is rescanned before push.

Mock qualification establishes client transport behavior against its declared mock
contract; it does **not** prove that a frozen real runtime enables every control
endpoint. R1 exposed that distinction at slot erasure. The benchmark itself is
unchanged, and there is no model behavior on which to tune it. The 501-body retention
limitation above also remains preserved rather than repaired after the freeze.

Replay without inference:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r1/score_campaign.py replay
```

**STOP after publication.** Neither original campaign nor R1 may be repaired or
resumed under this authorization. No Horus diagnosis or self-improvement follows.
