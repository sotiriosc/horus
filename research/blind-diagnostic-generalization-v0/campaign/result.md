# Inference campaign outcome: INVALID_STUDY

The campaign stopped before request 1. **0/80 attempted, 0/80 completed; all 80
NOT_RUN.** This is an implementation failure in the new transport wrapper, not a
model diagnostic failure and not evidence for or against model capability.

The committed transport defines a function named `http`, shadowing its imported
`http` package. Its first health-check attempt accesses `http.client.HTTPConnection`
and raises `'function' object has no attribute 'client'`. The exception handler
also refers to the shadowed package. The server process had been launched, but no
completion request was dispatched. It was terminated in the cleanup handler.
The server log is empty. The exact stop timestamp and first scheduled render ID
`e24ffa812432f3e62a4e` are preserved in `raw/execution.json`.

The assistant introduced this transport defect. Syntax compilation passed but did
not catch the name collision; the transport was not exercised with a mock before
launch. The frozen runtime/transport stopping rule was applied. The wrapper has
not been repaired, restarted or retried. No benchmark file changed.

## Provenance and scoring order

- Branch: `research/blind-diagnostic-generalization-v0`.
- Previously published benchmark: `2ebe61d8aff86c37584f4019a8bcaf3e492825ae`.
- Unchanged Method Freeze: `587ffedd39516b633376d222d6d84e6af186fcf8`.
- Unchanged Case Freeze: `2866e6bcf94539513c135df878b72058048e99cd`.
- Transport/preflight committed before launch: `16dcde1`.
- Raw stop record frozen and committed before primary scoring:
  `4eec8c4d4133779504504fdcaab0779b09c8f4c7`.

The raw freeze contains the complete 80-entry execution inventory; no final strings
or per-completion metadata exist because there were no completion attempts.
`raw-freeze.json` records SHA-256 before scoring; raw evidence files were made
read-only. No empty or invented model answers were substituted for missing calls.
The unchanged scorer received an empty raw-final mapping and the recorded transport
violation. Its primary result is `scores.json`: INVALID_STUDY. The separately
requested exact replay reproduced identical score bytes, with zero new inference.
Private server/intent evidence remains outside the public tree; only hashes appear
in `private-evidence-manifest.json`. No reasoning output exists or entered scoring.

## Measurements

Schema-valid answers: **0 of 0 returned answers**, not 0/80 measured performance.
All semantic, localization, control, pair, evidence, invention and representation
metrics are **not measured**. Assigning diagnostic FAIL or PASS to unexecuted gates
would fabricate observations. The frozen scorer exits with INVALID_STUDY before
computing gate measurements. `secondary-analysis.json` records each mandatory
gate and exact frozen threshold as NOT_EVALUATED, all 80 rendering rows, all 20
semantic rows and all six matched pairs as NOT_RUN.

| True class | Current selected | Healthy selected | Insufficient selected | Historical selected | Invalid selected | NOT_RUN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Current defect | 0 | 0 | 0 | 0 | 0 | 24 |
| Healthy | 0 | 0 | 0 | 0 | 0 | 16 |
| Insufficient evidence | 0 | 0 | 0 | 0 | 0 | 16 |
| Historical only | 0 | 0 | 0 | 0 | 0 | 12 |
| Invalid evidence | 0 | 0 | 0 | 0 | 0 | 12 |

A/B mapping performance: neither measured, 0 completed of 40 scheduled each.
Orders 1/2: neither measured, 0 completed of 40 scheduled each. Label/order
sensitivity, hallucination, historical-to-current confusion, abstention behavior,
component accuracy, causal-witness accuracy and evidence-ID mistakes are unknown.

| Family | All scheduled renderings | Completed | Current-defect classification/localization |
| --- | ---: | ---: | --- |
| Version selection | 20 | 0 | Not measured |
| Authority precedence | 8 | 0 | Not measured |
| Entity binding | 12 | 0 | Not measured |
| Publication update | 16 | 0 | Not measured |
| Operation idempotence | 12 | 0 | Not measured |
| Boundary comparison | 12 | 0 | Not measured |

Each family had one current-defect semantic world (four renderings), all unexecuted.
No secondary diagnosis of model strengths or weaknesses is possible.

## Verification and preservation

Preflight passed: all Method/Case Freeze bytes, all 80 request hashes, 1383
parent-tracked files and all six protected public branch heads. Model, both runtime
archives and installed server hashes exactly match model-runtime.json. Executable
identity reports build 11242, commit 526c43b8f; the full frozen commit is
526c43b8f7dfea9032e9f35e7a1be9183ca7cc20. Runtime identity passed; runtime readiness
and completion behavior were never established because the client failed first.

No prior outputs existed. The transport uses only frozen request bytes and schedule,
with no gold/scorer import, tool loop, repository payload, prior conversation or
previous-answer feedback. Intended flags implement the unchanged sampling/context
configuration, disabled caches, slot erasure and localhost isolation. No request
was sent, so these prospective inference controls were not empirically exercised.

Postflight confirms all 201 files present at Case Freeze remain byte-identical,
all 80 request hashes match, and all protected parent files/heads remain unchanged.
No active Horus source, architecture, Memory, policy, thresholds, receipts or world
state was modified. No world execution, training, proposal, critic, auditor rescue,
answer repair or retry occurred. One server process was started and terminated;
model completion calls remained zero. No private archive is in public ancestry.
Publication uses the unchanged repository full-history secret audit; the audit
record accompanies this result, with the exact final head rescanned before push.

## Reproduction and stop boundary

Without starting any server or invoking a model:

```sh
python research/blind-diagnostic-generalization-v0/campaign/score_campaign.py replay
```

The replay mode refuses to alter scores; it verifies raw hashes and byte-identical
scorer output. It creates replay.json exclusively, so reproducing in a separate
checkout requires directing/removing only that derived replay report first.
The raw evidence and benchmark must remain unchanged. Do not rerun run_campaign.py.

**STOP.** The failure is preserved and no repair or subsequent study is authorized
by this completed campaign. There is no model capability result to interpret.
