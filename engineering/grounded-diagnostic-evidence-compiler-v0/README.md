# Grounded diagnostic evidence compiler v0

Pure interface: `compile_evidence(case, contract)`. Runtime consumes raw case evidence and the frozen generic format contract only. It returns machine facts and candidate addresses, never a diagnosis.

Contracts and mutations were committed before implementation results. After the implementation freeze, run the 80-rendering/20-world engineering analysis with:

```sh
python engineering/grounded-diagnostic-evidence-compiler-v0/run_feasibility.py --implementation-freeze SHA --output-dir engineering/grounded-diagnostic-evidence-compiler-v0/results
```

Repeat into a fresh temporary directory for exact byte replay, never overwrite artifacts. After results begin, do not repair frozen implementation. Preserve any validity failure or unestablished engineering outcome. Synthetic tests and the dependency audit are separate from the fixture campaign.

Full input-array positions remain in raw JSON pointers. Normalization anchors those positions by source entity IDs, then derives label correspondence from evidence-only masked structure. Ambiguous alignments fail closed. Candidate execution links are not causal assertions. Capture integrity is limited to supplied generic format invariants, not a semantic judgment about operational behavior.

All compiler filesystem/network/subprocess access is denied after bootstrap. The harness permits only exact public fixture and mechanical-contract reads during execution. Preservation checks and publication audits run separately. No model, Horus or private data is involved.
