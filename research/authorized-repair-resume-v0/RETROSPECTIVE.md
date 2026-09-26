# V0.9 failure eligibility retrospective

The retained v0.9 session ended at attempted decision 57 with 52 authorized
executions and state 2. The failed logical call is
`a67e675004193a13c31485bad53fbb86:e2007:b57:HOLD:J`.

- Request SHA-256: `beb7997f877f396815a9e3100e35db6314f0e967ce03c2565bf74746edbf6e22`
- Failed response SHA-256: `9e177280df0d138c5d65e05b99bb075132b0ea61e91123edd18f9234f9a87a97`
- Failure: `TimeoutError`
- Original call history: request intent, failed response, null parse; all retained
- Other decision-57 components: eight successful, durable parses
- Action after the failed prediction batch: none
- Receipt after it: none
- Memory publication after it: none
- Routing evidence after it: none
- Training target after it: none
- Current problem: `PR-0002`, unresolved
- Existing problem-specific evidence: ADVANCE only
- Missing problem-specific evidence: RETREAT

This satisfies the frozen causal retry rule. It does not establish that every
timeout is retryable. A timeout after execution or publication fails closed.

The retained request object and the ModelClient serialization rule reconstruct
the exact HTTP request body. V0.10 commits both the structured request SHA and
transport-byte SHA privately before reissue. Public evidence contains hashes,
not prompt or response content.
