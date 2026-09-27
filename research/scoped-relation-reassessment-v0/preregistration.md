# Horus v0.19 scoped relation reassessment preregistration

Parent: `3d4ec4ae30f16f42850abcc6f93358bab5488b0e`

The target is canonical problem `PR-0003` and relation `(state 1, ADVANCE)` only. The first stage performs zero model inference: authenticate and replay every eligible receipt-scored relation row, recompute the frozen six-row window, and compare the derived selection with retained router state.

The classification is exactly one of `ROUTING_CORRECT_AS_FROZEN`, `ROUTING_SHOULD_HAVE_SWITCHED`, or `ROUTING_EVIDENCE_INCONSISTENT`. Any replay inconsistency or missed required switch stops before live work.

Additional evidence is eligible only if routing is correct, the latest grounded comparison favors G3 over G2, and the challenger still lacks the frozen lead of two. The existing `RELATION_PROBE` or consumed deadlock route may be used only under their retained authority and budget. If neither is legally available, append a non-authoritative `MORE_RELATION_EVIDENCE` request scoped to `(1, ADVANCE)` and stop for external approval.

No destination, state-2 access, hidden transition, option profile, horizon extension, representation change, training, or new specialist may influence the request. A request does not authorize execution. With no authorized route, live limits are zero decisions and zero calls. PR-0002 must remain byte-for-byte equivalent as a canonical problem object.
