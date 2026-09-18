# Base framework v1: cross-source observation

This experiment keeps the v0 world and five-component loop fixed while
replacing its single protected receipt with two registered observation
channels. Source A is table-driven; Source B uses separately written
conditional logic. Incomplete or disagreeing evidence cannot commit. One
re-observation is permitted, after which the framework stops.

Run:

```bash
make base-framework-v1
```

The command runs 10 unit tests and 69 scenario runs and writes full evidence to
a new temporary directory outside the repository. The frozen design is in the
[`pre-registration`](../../research/base-framework-v1-preregistration.md), the
compact result is [`results.json`](results.json), and the interpretation is in
the [`public report`](../../research/base-framework-v1-results.md).

The hidden oracle is imported only by the campaign and tests. It never supplies
runtime evidence. The out-of-model common-mode control produced three false
accepts: both sources agreed on the same wrong observation and the runtime
trusted the pair during recovery. Those failures are retained prominently; they
define the remaining trust boundary rather than changing the protected
single-channel-fault result.
