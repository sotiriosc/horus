# Blind diagnostic replacement R2

Read preregistration.md, schema-runtime-audit.json and launch-plan.json. Original
scientific inputs and both invalid campaigns/engineering qualification are unchanged.

Zero-model qualification before the Execution Freeze:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r2/test_transport.py
```

After the committed Execution Freeze and successful zero-model preflight, the
user-authorized once-only launch is:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r2/run_campaign.py --transport-freeze EXECUTION_FREEZE_SHA
```

Never rerun after a start/stop. No frozen code or flag repair is allowed.
Raw finals and safe metadata are separate from private envelopes/reasoning/logs.
Commit raw/ and raw-freeze.json before primary scoring:

```sh
python research/blind-diagnostic-generalization-v0/replacement-r2/score_campaign.py primary
python research/blind-diagnostic-generalization-v0/replacement-r2/score_campaign.py replay
```

The host invokes original unchanged ../scorer.py and retains its exact classification,
adding replacement_id R2 separately. Replay verifies identical score bytes without
inference. Mock outputs cannot enter this path. Publish only the independent R2
branch after preservation/secret audits, then stop without Horus diagnosis or proposals.
