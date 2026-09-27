# Horus v0.20 scoped evidence authorization

Parent: `a5472be42355c45e4accb85142f6d3d83cfa2083`.

The zero-inference proof freezes `ROUTE_GATING_DEADLOCK` for PR-0003, relation `(1, ADVANCE)`, capability `MORE_RELATION_EVIDENCE`, blocked by `RELATION_PROBE_CADENCE`. At the v0.19 endpoint, the next authorized index is 56, the prior ordinary probe index is 54, distance is 2, and the unchanged minimum is 3. Abstention changes neither authorized-execution count nor the prior-probe index, so repeated abstention cannot move the distance.

The externally authorized route is `PROBLEM_SCOPED_RELATION_PROBE`, available only to this exact problem and relation while the ordinary evidence route remains blocked. It freezes action `ADVANCE` solely for `GROUND_RELATION_FOR_SPECIALIST_SELECTION`. It receives no destination, desired state, simulator law, future receipt, or counterfactual outcome. All nine prediction components must be valid before execution.

The global probe policy and cadence remain unchanged. A scoped probe uses mode `PROBLEM_SCOPED_PROBE`, so it does not consume or reset the ordinary probe marker. Like any authenticated execution, it advances the authorized-execution count; eligibility is reassessed before any second scoped probe.

At most two scoped probes are authorized, with early stop if the unchanged router reaches its required lead, the request otherwise resolves, the ordinary route becomes available, the target relation is no longer current, or an operational failure occurs. After each original receipt, the exact six-observation window is reconstructed and G2/G3 scores, selection, lead, and threshold status are recorded. No result is assumed in advance.

If the original state-1 tie disappears, at most one subsequent ordinary decision may run without a scoped route or option-profile override. Otherwise no follow-up runs.

The total live ceiling is three behavioral decisions and 27 local model calls: nine calls per existing decision structure, at most two scoped probes plus at most one ordinary follow-up. There are no retries, training runs, model changes, router-threshold changes, option-profile changes, horizon changes, global route changes, or follow-on experiments.

Outcomes are `RELATION_ROUTING_RESOLVED`, `VALUE_TIE_PERSISTS`, `MORE_RELATION_EVIDENCE_REQUIRED`, or `OPERATIONAL_FAILURE` according to the frozen rules above.
