# Blind diagnostic replacement R1

R1 preserves the original frozen benchmark and failed campaign byte-for-byte.
Read preregistration.md before execution. The only scientific scorer remains the
original ../scorer.py; R1's score_campaign.py is an integrity-checked input/output
host, not new grading logic. Outcome naming retains the scorer's exact taxonomy
and records replacement_id: R1 separately.

Before Transport Freeze (zero model calls):

```sh
python research/blind-diagnostic-generalization-v0/replacement-r1/test_transport.py
```

qualification.json records local mock qualification. The complete saved 80-request
schedule is delivered only to the mock in that test. Temporary dummy outputs are
marked QUALIFICATION_ONLY, removed after tests, and rejected by the scientific
score host. guard.py verifies inherited files/hashes without regenerating cases.

After Transport Freeze and successful artifact/qualification checks, the separately
authorized one-time launch is:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r1/run_campaign.py --transport-freeze TRANSPORT_SHA
```

Never rerun this command after a start or stop. Do not repair frozen transport.
Private envelopes/reasoning/server logs stay outside the public Git tree. Commit
raw/ and raw-freeze.json before running the single primary score operation:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r1/score_campaign.py primary
python research/blind-diagnostic-generalization-v0/replacement-r1/score_campaign.py replay
```

Replay performs no inference and compares exact score bytes. It can be rerun without
altering stored scores. Any validity stop is preserved as the independent R1 outcome;
it never changes the original INVALID_STUDY / zero-call campaign. Stop after the
R1 result and safe evidence are published. No Horus diagnosis or improvement follows.
