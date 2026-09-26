# Horus v0.4 collection recovery amendment

Status: frozen before collection resumption; no candidate training or evaluation
had begun.

The first collection process stopped after five authorized bridge records and
one fail-closed abstention. It then created an empty second session and failed
before its first decision because a new session requested directly in registered
Regime B was incorrectly initialized as Regime A. The failure was in session
configuration, not in receipt authority or the already recorded evidence.

The five authorized records and all six attempted-decision call records remain
unchanged. They must not be repeated. The empty second session is reused. A new
decision identity may fill the missing authorized receipt; it is not a retry of
the abstained decision.

The fixed evidence target remains exactly 60 authorized receipts: three from
Regime A and 57 from Regime B. To make recovery finite without selecting on
model performance, each of the ten fixed sessions may issue at most 12 total
attempted decisions. An abstention remains visible and contributes no event or
training record. Collection fails if any session reaches that bound before six
authorized receipts. Collection cannot be extended because of realized
consequences, forecast correctness, or candidate results.

The code repair permits a genuinely empty session to begin directly in a
registered regime. Existing sessions with evidence continue to infer Regime A
when no older audit field exists, preserving backward compatibility. The
restart proof and model-call totals are derived from durable records rather
than assumed runtime counts.
