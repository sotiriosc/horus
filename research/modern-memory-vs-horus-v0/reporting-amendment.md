# Post-stop reporting amendment

The preregistered campaign stopped during MH Stage-A event 5. All nine MH calls
for that batch completed their durable request/response/parse chains, but the
joint next-state request for ADVANCE recorded `TimeoutError`. The existing
all-components-valid rule therefore made the batch invalid. The harness refused
to execute or publish MH event 5.

M event 5 had already executed because the prospectively frozen alternating
condition order placed M first on odd events. This left five authenticated M
events and four authenticated MH events. Continuing would violate the matched
observation sequence. Rerunning would violate the no-retry rule. Neither was
done.

`invalid_report.py` and `invalid_replay.py` are zero-inference reporting tools
added after the stop. They do not modify any request, response, receipt, Memory,
routing evidence, policy, threshold, or frozen source. The source manifest still
identifies the exact pre-inference implementation. The campaign is classified
`INVALID`; no comparative conclusion about Horus capability is drawn.
