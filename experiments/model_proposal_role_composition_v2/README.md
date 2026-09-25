# Model proposal role composition v2

**C — NOT ESTABLISHED: interrupted; original live evidence unavailable after a
reported computer crash.** The code/preregistration survived in Git. Temporary
request/response and transaction records did not survive. Exact campaign totals
and live metrics are null, not zero. Last surviving console progress reports at
least 18 calls and seven committed decisions; this is not an exact replayable
archive. No live inference was restarted or replaced.

Read the [44-section report](../../research/model-proposal-role-composition-v2-results.md),
[preregistration](../../research/model-proposal-role-composition-v2-preregistration.md),
[compact interruption result](results.json) and [executed verification](verification.json).

One intended change from composition-v1: use the already-tested explicit Map
integer/domain contract. All other instructions, projections, parsers, world,
schedule, seeds, runtime and authority are frozen. Runtime/transport/control source
is byte-identical to v1. The original schema-contract result remains SUPPORTED;
composition-v1 remains C. Nothing was pushed.

Available zero-inference checks from repository root:

```sh
python3 -m unittest experiments.model_proposal_role_composition_v2.test_study -v
python3 -m experiments.model_proposal_role_composition_v2.preflight --output "$PREFLIGHT_OUTPUT"
```

Use a durable external output path. These checks validate frozen sources, all
12 initial contexts, 288 UNKNOWN projections and genuine Recovery callback routing.
The regenerated preflight matched its original committed digest exactly. The same
5 Explorer / 14 Map / 22 Recovery bounded controls passed after interruption.
Historical regressions and available original recorded-response replays also passed:
41 executed commands/checks total, with negative expected statuses preserved.
See verification for exact commands; no v2 live replay pass is claimed.

If the **original** v2 raw archive is recovered, the retained replay interface is:

```sh
python3 -m experiments.model_proposal_role_composition_v2.run --replay "$ORIGINAL_V2_EVIDENCE" --baseline "$COMPOSITION_V1_EVIDENCE/model-calls.jsonl" --output "$V2_REPLAY_OUTPUT"
```

It requires the complete original seven-file evidence set and recomputes UNKNOWN
from authenticated Memory. It cannot reconstruct lost live data. `finalize.py`
requires complete live evidence and actual replay/regression assurance; no fabricated
assurance was supplied. The interruption summary is separate from a completed
campaign's normal finalization path.

The retained live runner is **not authorization to restart this study**. The original
protocol forbids replacement calls/episodes and another run. Preserve this C
checkpoint; any new campaign needs a separate explicit protocol decision and
durable incremental evidence storage. No parser, Explorer, Recovery, authority or
Memory behavior was changed during recovery.
