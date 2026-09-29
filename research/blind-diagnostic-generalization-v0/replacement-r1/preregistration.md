# R1 replacement: prospective transport qualification and execution freeze

R1 exists solely because v0's transport helper shadowed Python's http package and
failed before dispatch. The original benchmark validity remains intact. Original
campaign **INVALID_STUDY**, zero requests/completions, remains permanently preserved
at bb58926e0f2581bee38393e179b758b18d0879e4. There are no prior model outputs to use.
R1 is an independently authorized replacement, not a retry/resumption of that run.
Only execution/transport infrastructure needed to deliver the frozen requests changes.

Branch: research/blind-diagnostic-generalization-v0-replacement-r1, based exactly on
the failed-study publication. All new files live in replacement-r1/. Every inherited
parent file, including the entire failed campaign/, remains byte-identical.

## Scientific inheritance

Method Freeze 587ffedd39516b633376d222d6d84e6af186fcf8 and Case Freeze
2866e6bcf94539513c135df878b72058048e99cd remain authoritative. Reuse every existing
protocol, schema, world, opaque rendering, request byte, gold fact, matched pair,
scorer, gate, seed, schedule and model/runtime configuration unchanged. **Do not
regenerate worlds or mappings.** The existing 80 request files are authoritative.
R1 does not import generator functions or use gold in the inference process.

The unchanged scorer's exact taxonomy is retained with `replacement_id: R1` in a
separate outcome wrapper. A supported result requires every inherited gate and valid
execution; valid gate failure is NOT_ESTABLISHED; execution/protocol failure is
INVALID_STUDY. The original v0 INVALID_STUDY is always reported separately. No
_R1 suffix is inserted into frozen scorer output values.

## Qualification and freeze order

Before any real server startup:

1. Run test_transport.py against loopback mock HTTP servers. These exercise the
   exact http_request helper and execute orchestration later used for science.
2. Verify actual readiness GET (the historical regression), properties GET, erase
   POST, slot GET, completion POST, envelope handling, HTTP errors, disconnects,
   bounded timeouts, stop behavior, cleanup, at-most-once dispatch and raw hashing.
3. Qualify an entire 80-request schedule using unchanged saved payload bytes and
   dummy envelopes. This tests transport delivery, not model output or scoring.
4. Ensure all mock evidence uses an exclusive temporary QUALIFICATION_ONLY namespace,
   never SCIENTIFIC_R1; the scoring host rejects it before importing the scorer.
   Temporary mock output trees are removed after tests. No dummy answer is graded.
5. Verify inheritance hashes/bytes, protected refs and exact artifact/runtime identity.
6. Commit the runner, transport, guards, scoring host, tests, this preregistration,
   and qualification/preflight evidence. This commit is **R1 Transport Freeze**.
7. Recheck all frozen replacement and inherited bytes and exact runtime hashes before
   starting the real server. Record the full Transport Freeze SHA in launch-preflight.

No runner, transport, tests, scorer host, runtime flags, interface or campaign rule
may be changed after Transport Freeze. Any subsequently discovered execution bug
or mandatory integrity failure stops R1 as INVALID_STUDY, including before inference.
Do not patch/restart/resume. Preserve and publish the failure. The user's explicit
conditional authorization permits the real campaign after these checks, without
an additional approval request.

## Transport and isolation

The helper is `http_request`, importing `http.client as http_client`. The actual
network regression GET must return the mock JSON envelope; syntax/name inspection
alone is insufficient. The runner loads schedule/request hashes, not case gold,
family, matched-pair identity, current scores or previous answers. Payloads are
read as bytes, checked against frozen hashes, and dispatched without JSON
reconstruction. Only non-generative health polling may repeat during startup.
There is exactly one completion dispatch per scheduled ID, no HTTP redirects or
retries, and an exclusive on-disk intent record before dispatch. Re-execution with
an existing output or private directory is refused.

Use the **exact command and cwd from original campaign/launch.json**, which implements
the original model-runtime.json and preregistration: Qwen3-14B Q4_K_M, llama.cpp
b11242, context 16384, native deepseek separated reasoning 512, temperature .2,
top-p .9, top-k 40, min-p .05, seed 417351046, generation cap 2048. Sampling values
are already in the unchanged request bytes. No runtime flag is changed in R1.
Original launch cache/warmup/offline flags, localhost port 18085, one slot, exact
library paths and GPU flags are inherited. Environment LLAMA_ARG_/LLAMA_LOG_
overrides are removed as in the original launch. Models receive text-only frozen
messages, no repository contents outside their evidence, tool loop, filesystem or
web tools, previous conversation, scores or other responses. Host-level file access
is used only to deliver frozen inputs and preserve outputs, not exposed to the model.

Before each completion, erase slot 0 and inspect that the one slot is idle. Prompt
and RAM caches are disabled by the inherited launch command; request cache_prompt
is false. Save control-response hashes/metadata. Health readiness allows up to 180
seconds for expected startup; completion timeout is 600 seconds, with no retry.
After success or error, terminate/wait for the server; force kill only if graceful
termination exceeds 30 seconds. No fallback runtime or configuration change.

A completed malformed, truncated (finish_reason length), empty, incorrect or
schema-invalid final string is preserved unchanged and the schedule continues.
No JSON extraction/repair, critic, semantic auditor or quality-dependent early stop.
A connection/HTTP/runtime/context error, invalid transport envelope, or missing
final-channel string stops the campaign, records attempted/completed counts and
marks remaining requests NOT_RUN. Missing final-channel strings cannot be invented
or converted from private reasoning. Partial results never rescue invalid execution.

## Evidence and scoring sequence

For each request preserve order, exact request hash, start/end UTC, wall time,
HTTP/transport status, finish reason, usage/token counts, response hash, and raw
first final UTF-8 bytes. Private response envelopes, reasoning and server logs remain
in /tmp/horus-blind-diagnostic-generalization-v0-replacement-r1-private outside Git.
Only final content and safe metadata may enter the public tree. Do not inspect
answer quality during generation. Progress reports contain completed counts only.

After 80 calls or stop, hash all raw public files, record raw-freeze.json, make raw
files read-only and commit them **before primary scoring**. The scoring host checks
the committed raw freeze, exact raw hashes, SCIENTIFIC_R1 purpose, unchanged inherited
files and Transport Freeze. It passes only verbatim final strings and the frozen
violation record to unchanged scorer.py. It neither imports nor reads private
reasoning. Primary scores are written once; a separate deterministic replay must
match exact score bytes, without new inference. Mock evidence is never accepted.

All inherited mandatory gates apply exactly: >=17/20 semantics (>=3/4 each), >=5/6
current defects, >=4/6 localized, healthy 4/4 with zero current-defect false positives
among 16 renders, historical 3/3 with zero among 12, insufficient >=3/4, invalid 3/3,
pairs >=5/6, consistency >=16/20, evidence-grounded >=17/20, invented-ID outputs zero.
Malformed finals are wrong. The scorer's exact mechanics remain authoritative.
Secondary confusion, family, component/witness, citation, abstention and factor
analyses describe the result only and cannot change any primary score.

## Preservation, publication and stopping

guard.inheritance compares all files at the parent publication, frozen hashes,
requests and protected branch heads, including the original failed-study branch.
Do not invoke original verify.py/tests that regenerate worlds. Do not modify active
S+E, Memory, policy, thresholds, world state, receipts, previous classifications,
or train/generate proposals/run Horus. Models are used only for the 80 diagnostic
requests. All original private archive heads must remain outside public ancestry.

After success or stop: preserve raw evidence and exact runtime identity, score/replay,
verify preservation, scan all reachable history with unchanged repository secret
rules, and publish **only R1**. Private reasoning/logs never enter public ancestry.
Report original v0 INVALID_STUDY / zero calls alongside independent R1 outcome.
The original limitations of small synthetic, correlated, author-known/public-gold
cases and unscored prose apply unchanged. Stop after publication; no Horus diagnosis,
follow-up calls, repair, policy change or improvement study is authorized.
