# Base framework v0 and Dream-RSI

**Status:** scoped comparison; no general novelty claim.

[Dream-RSI](https://arxiv.org/abs/2609.14858v1) constrains replay policies to
prefix-observable information and uses incumbent retention to provide
non-regression on fixed replay histories. Its realized exploration history
supports evaluation and revision of later exploration policy.

Horus base framework v0 investigates a complementary execution-boundary
problem: whether a candidate correction can be authorized using evidence that
is both provenance-matched and causally independent of the candidate being
checked. Its incumbent rule is narrower: retain a currently valid state as a
candidate, quarantine it when external evidence verifies it is invalid, and
authorize a replacement only through the declared protected evidence path.

The bounded Horus experiment does not establish general recursive
self-improvement, general non-regression, automatic discovery of causal
independence, or a general solution to grounding. It does not show that Horus
is the first system to address these questions, and it does not imply that
Dream-RSI targets the same hardware authorization problem. A broader novelty
claim would require a dedicated literature review.
