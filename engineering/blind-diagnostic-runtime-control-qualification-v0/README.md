# Real runtime control qualification — engineering only

This branch starts at completed R1 b156dd01ce6f1deed049fa2589581888d36f34fb.
Original v0 and R1 remain INVALID_STUDY with zero completion requests. No R2 is
created, no scientific scorer is invoked, and no diagnostic benchmark is run.

## Source audit before launch

source-audit.json records exact source commit, archive commit comment, SHA-256 and
Git blob hashes, line references, immutable upstream links and relevant excerpts.
At pinned llama.cpp 526c43b8f7dfea9032e9f35e7a1be9183ca7cc20:

- tools/server/server.cpp:291 registers POST /slots/:id_slot.
- tools/server/server-context.cpp:4754 checks params.slot_save_path.empty(); the
  following error is NOT_SUPPORTED before any action dispatch.
- tools/server/server-common.cpp:60-63 maps NOT_SUPPORTED to HTTP code 501.
- tools/server/server-context.cpp:4777-4778 dispatches erase to handle_slots_erase.
- tools/server/server-context.cpp:5344-5368 posts the erase task and returns its result.
- common/arg.cpp:3611-3623 declares --slot-save-path PATH, requires an existing
  directory and assigns the parameter. README.md:225 documents it as disabled by default.

These are source-established facts. R1 independently observed HTTP 501 at its first
slot erase, and its preserved command omitted --slot-save-path. Connecting the
missing flag to R1's status is a source-supported inference, not observation or
reconstruction of the unretained R1 response body. Neither completed result changes.

The pinned API docs describe erase and its id_slot/n_erased response, but do not
explicitly guarantee repeated-empty idempotence. Prospectively omit a second erase.
Do not populate a slot by inference. The single authorized erase starts on an idle,
unused slot and must report id_slot 0 and n_erased 0.

## Prospective one-launch plan

plan.json preserves the complete exact command/cwd and four-request sequence.
The **only argv delta** versus R1 is `--slot-save-path` followed by the fresh private
0700 temporary directory recorded there. It is outside the repository and empty.
No unrelated flags are added. All model/runtime/archive hashes are checked against
the original frozen model-runtime.json, and inherited runtime environment overrides
are removed just as in R1. The existing --no-warmup and --offline flags are retained.

Before requests, launch-preflight.json records command, hashes, preservation and
source checks. Start the pinned server exactly once. Wait up to 180 seconds for
its source-backed listening log message, without issuing health polling requests.
Then perform exactly once, in order:

1. GET /health: HTTP 200 and status ok.
2. GET /props: HTTP 200, one slot, pinned build identity.
3. GET /slots: HTTP 200, one idle slot.
4. POST /slots/0?action=erase with bytes `{}`: HTTP 200, id_slot 0, n_erased 0.

No completion, inference, tokenization, save, restore or benchmark endpoint is
permitted by the helper's allowlist. No prompt is submitted. Generation endpoint
and nonempty prompt-body rejection are tested before any network connection.
This proves only the declared engineering controls, not future diagnostic outcomes.

For each request save method/path, UTC times, status, headers, full raw response
body and its SHA-256. Write the body and metadata before status or JSON validation
can raise. Do not reserialize or truncate bodies. Any failure stops the sequence;
there is no retry, flag change or second launch. The result taxonomy is only
REAL_RUNTIME_CONTROL_PATH_QUALIFIED or REAL_RUNTIME_CONTROL_PATH_NOT_QUALIFIED.

Always terminate the server. Remove the empty slot directory afterward; unexpected
contents would instead be archived privately and never restored. Startup logs remain
outside Git. Preserve their hashes and public control observations. No model-private
reasoning can arise because completion calls remain zero.

## Checks, evidence and publication

Mock tests (not model calls):

```sh
python engineering/blind-diagnostic-runtime-control-qualification-v0/test_transport.py
```

The tests exercise actual local HTTP, all four endpoint shapes, exact error-body
retention, malformed-success retention, and prohibited endpoint/body rejection.
Mock evidence is temporary and deleted. qualification-tests.json records results.
Commit source audit, plan, code and tests before the real launch. The single allowed
execution is qualify.py; never rerun it once observations/launch intent exist.

verify.py compares every file inherited from R1, all materialized hashes and 80
request hashes, original/R1 classifications and protected public branch heads.
It does not regenerate worlds, opaque mappings or gold. Runtime/source identity is
also checked. Run postflight preservation, hash public/private evidence separately,
then use the repository's unchanged full reachable-history publication audit.
Publish only the engineering branch; no private logs or slot-state files.

No Memory writes, Horus world execution, authenticated receipts, training, policy
changes or proposals. A pass provides engineering evidence for a separately reviewed
and preregistered R2 only. **Stop after publication; do not create or execute R2.**
