# Horus grounded exploration v0 R1 replacement registration

Campaign identity: `HORUS_GROUNDED_EXPLORATION_V0_R1`.

This is one replacement campaign for the infrastructure failure preserved at
commit `5edc8894fb47709d8c40dd8f3eb2f6c968dfa173`. The original result remains
**NOT ESTABLISHED — external joint-model service failure** and is not rewritten,
replaced, or reinterpreted.

The executable scientific implementation remains exactly commit
`72cdc09`. No exploration rule, priority, threshold, contradiction rule, probe
budget, relation identity, specialist artifact, router behavior, Explorer
behavior, phase length, stopping rule, score, prompt, sampler, or hidden-regime
exclusion changed.

The sole correction is infrastructure: Ollama 0.1.16 runs in the independent
detached supervisor session `horus-v07-r1-ollama`, separate from the campaign
launcher. A separate-shell liveness check and one explicitly non-campaign health
request passed before any replacement session or call ledger was created.

The frozen schedule remains 18 A1, 9 B1, restart, 9 B2, and 18 A2 autonomous
decision attempts: 54 decisions and at most 486 campaign calls. No forced
calibration, per-call retry, ambiguous-call replacement, schedule extension, or
outcome-based continuation is permitted.

The optional non-authoritative unresolved-problem interface is deferred to
v0.8. Adding it here would modify code after the frozen implementation and make
the infrastructure-only replacement less exact.
