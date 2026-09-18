# Base framework v0

This experiment implements the smallest bounded software loop in this
repository that connects Explorer, Map, Measure, Memory, and Recovery. Its
contracts and failure criteria were frozen in
[`research/base-framework-v0-preregistration.md`](../../research/base-framework-v0-preregistration.md)
before implementation.

The environment has four states and three actions. It is implemented separately
from the framework and emits protected receipts. The framework assigns explicit
epoch, transaction, observation, source, and lineage identities; stages Map and
Memory updates; and continues only after separate authority gates accept them.
Recovery proposes corrections but cannot authorize them.

Run the complete check with:

```bash
make base-framework-v0
```

The command runs 12 unit tests and 42 campaign scenarios: one clean episode and
13 clean/failure controls for each of three epoch seeds. It writes detailed
evidence to a new temporary directory outside the source tree. The checked-in
[`results.json`](results.json) is the compact approved summary; the full public
interpretation is in the
[`result report`](../../research/base-framework-v0-results.md).

The implementation is deliberately small and deterministic. It is a software
architecture experiment, not a general agent, causal graph, world model, or
safety proof. The protected environment receipt, evidence store, authorizers,
and coordinator are trusted for the tested scope.
