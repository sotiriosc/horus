# Map failure-context schema transfer v0 — results

**DESCRIPTIVE DIAGNOSTIC COMPLETE — no A/B/C classification.**

| Historical context | World | Family | Mapping | Alias | Seed | Historical J consequence | New J consequence | S consequence | Realized receipt | Historical J failure reproduced | S repaired it |
|---:|---|---|---:|---|---:|---:|---:|---:|---:|---|---|
| 2 | W0 | O2 | 1 | Q7 | 96012 | 0 | 0 | 1 | 1 | True | True |
| 3 | W0 | O1 | 1 | K1 | 96012 | 0 | 0 | 1 | 1 | True | True |
| 5 | W0 | O2 | 2 | M4 | 96022 | 0 | 0 | 1 | 1 | True | True |
| 7 | W0 | O1 | 3 | K3 | 96032 | 0 | 0 | 1 | 1 | True | True |
| 8 | W0 | O1 | 4 | K2 | 96042 | 0 | 0 | 1 | 1 | True | True |
| 9 | W0 | O2 | 4 | M4 | 96042 | 0 | 0 | 1 | 1 | True | True |
| 10 | W0 | O2 | 5 | Z2 | 96052 | 0 | 1 | 1 | 1 | False | False |
| 27 | W3 | O1 | 1 | K2 | 96214 | -1 | 1 | 1 | 1 | False | False |
| 30 | W3 | O2 | 3 | M4 | 96234 | -1 | -1 | 1 | 1 | True | True |
| 32 | W3 | O1 | 4 | K1 | 96244 | -1 | 1 | 1 | 1 | False | False |
| 33 | W3 | O2 | 4 | Q7 | 96244 | -1 | 1 | 1 | 1 | False | False |

1. Historical joint failures reproduced: **7/11**.
2. Reproduced failures repaired by consequence-only: **7/7**.
3. Cases where S made a correct J prediction worse: **0**.
4. Assessment: **SCHEMA COUPLING APPEARS IN EVERY REPRODUCED FAILURE**. The other **4/11** historical failures did not reproduce, so context sensitivity remains a limit on the scope of that result.

The 22 registered calls completed with no retries or replacements. J and S were matched within each pair; all J requests reproduced the retained historical request hash. Probes remained detached and were scored only after new original receipts. Exact replay passed. See `experiments/map_failure_context_schema_transfer_v0/results.json` and `verification.json` for compact evidence.

Reporting note: the frozen finalizer stopped because it reserialized sorted-key JSONL objects for a byte-order-sensitive request hash. The preserved frozen finalizer is unchanged. The post-replay reporter uses each recorder intent's already-preserved `exact_request_json` bytes; no request, response, score or decision changed.
