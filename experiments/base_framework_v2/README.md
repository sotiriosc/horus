# Base Framework v2: evidence provenance

This bounded software experiment keeps the v1 four-state world and complete
Explorer/Map/Measure/Memory/Recovery loop unchanged. It adds a nine-node
immutable process registry, a smaller independently implemented witness C, and
an evidence-package gate. Source A, Source B, and C are data producers only;
the package authorizer alone can admit their evidence to the inherited loop.

The protected campaign passed. Identical wrong A+B evidence was blocked whenever
C remained correct or disagreed differently. The hidden oracle separately found
3/3 false accepts when A+B+C shared the same wrong relation and 3/3 when the
trusted registry falsely declared derived paths to be separate. These controls
are retained as the explicit v2 trust boundary.

Run the tests and 57 predeclared scenarios with:

```bash
make base-framework-v2
```

Detailed evidence is written to a new directory outside the repository. The
checked-in `results.json` is a compact summary. See the
[frozen preregistration](../../research/base-framework-v2-preregistration.md)
and [results report](../../research/base-framework-v2-results.md).
