# Split Map independent prediction v0 — results

**FAILURE REPRODUCIBILITY TOO WEAK TO EVALUATE SPLIT MAP**

| Ctx | World | Family | Map | Alias | Seed | Historical Map | New J | N | C | Reconciled | Receipt | J next | J cons | Split next | Split cons | J exact | Split exact | J failure reproduced | C repaired | J rank repaired | Split rank repaired |
|---:|---|---|---:|---|---:|---|---|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | W0 | O2 | 1 | Q7 | 96012 | (1,+0) | (1,+1) | 1 | +1 | (1,+1) | (1,+1) | True | True | True | True | True | True | False | False | True | True |
| 3 | W0 | O1 | 1 | K1 | 96012 | (1,+0) | (1,+0) | 1 | +1 | (1,+1) | (1,+1) | True | False | True | True | False | True | True | True | False | True |
| 5 | W0 | O2 | 2 | M4 | 96022 | (1,+0) | (1,+1) | 1 | +1 | (1,+1) | (1,+1) | True | True | True | True | True | True | False | False | True | True |
| 7 | W0 | O1 | 3 | K3 | 96032 | (1,+0) | (1,+1) | 1 | +1 | (1,+1) | (1,+1) | True | True | True | True | True | True | False | False | True | True |
| 8 | W0 | O1 | 4 | K2 | 96042 | (1,+0) | (1,+0) | 1 | +1 | (1,+1) | (1,+1) | True | False | True | True | False | True | True | True | False | True |
| 9 | W0 | O2 | 4 | M4 | 96042 | (1,+0) | (1,+1) | 1 | +1 | (1,+1) | (1,+1) | True | True | True | True | True | True | False | False | True | True |
| 10 | W0 | O2 | 5 | Z2 | 96052 | (1,+0) | (1,+1) | 1 | +1 | (1,+1) | (1,+1) | True | True | True | True | True | True | False | False | True | True |
| 27 | W3 | O1 | 1 | K2 | 96214 | (1,-1) | (2,+1) | 0 | +1 | (0,+1) | (2,+1) | True | True | False | True | True | False | False | False | True | True |
| 30 | W3 | O2 | 3 | M4 | 96234 | (1,-1) | (2,+1) | 0 | +1 | (0,+1) | (2,+1) | True | True | False | True | True | False | False | False | True | True |
| 32 | W3 | O1 | 4 | K1 | 96244 | (0,-1) | (2,+1) | 0 | +1 | (0,+1) | (2,+1) | True | True | False | True | True | False | False | False | True | True |
| 33 | W3 | O2 | 4 | Q7 | 96244 | (0,-1) | (2,+1) | 1 | +1 | (1,+1) | (2,+1) | True | True | False | True | True | False | False | False | True | True |

- Historical joint consequence failures reproduced: **2/11**.
- Reproduced failures repaired by independent consequence: **2/2**.
- Consequence accuracy: joint **9/11**; split **11/11**.
- Next-state accuracy: joint **11/11**; independent **7/11**.
- Exact accuracy: joint **9/11**; split **7/11**.
- Original ranking failure repaired: joint **9/11**; split **11/11**.
- Regressions: consequence **0**; exact **4**.
- Mechanical reconciliation errors: **0**.

All 33 registered attempts completed without retry or replacement. Zero-inference controls established that the consequence request bytes are invariant to synthetic next-state outputs, both component parses precede reconciliation, invalid components abstain, and no probe gains execution or publication authority. Exact replay passed. This remains a detached research implementation; production Map and Explorer were not modified.

Reporting note: the frozen package `__init__.py` docstring was copied from the 22-call predecessor and incorrectly says “Twenty-two detached Map probes.” The operative preregistration, schedule, call limit, journal, metadata and evidence all specify and record 33 calls. The nonoperative frozen file remains unchanged.
