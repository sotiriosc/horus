# R2 Execution Freeze — independent prospective replacement

Base: df2d0ebc41d7c1b53a85779c38dab45cb21ec2e9. Branch:
research/blind-diagnostic-generalization-v0-replacement-r2. No inherited file changes.
Original v0 remains INVALID_STUDY / zero calls at bb58926; R1 remains INVALID_STUDY /
zero calls at b156dd0. Engineering qualification remains
REAL_RUNTIME_CONTROL_PATH_QUALIFIED / zero completions at df2d0eb. R2 is a new
separately authorized campaign; neither prior failure is repaired or rerun.

## Unchanged science

Inherit Method Freeze 587ffedd39516b633376d222d6d84e6af186fcf8 and Case Freeze
2866e6bcf94539513c135df878b72058048e99cd byte-for-byte: 20 semantic worlds, six pairs,
80 renderings, exact saved request bytes and schedule, opaque maps, protocol/schema,
gold, scorer, seed and every gate. Do not regenerate, tune, change or reorder them.
No behavioral evidence exists from either prior blind campaign. No new cases,
thresholds, prompt/schema modifications or grading logic are introduced.

The original scorer's taxonomy remains exact, with replacement_id: R2 separately.
Supported requires every inherited scientific gate and valid execution; otherwise
valid execution is NOT_ESTABLISHED. A validity failure gives INVALID_STUDY. Never
rename output values or upgrade a failure via secondary interpretation.

## Prospective schema/runtime limitation

schema-runtime-audit.json pins exact source hashes/lines at llama.cpp commit
526c43b8f7dfea9032e9f35e7a1be9183ca7cc20. The server accepts response_format
{"type":"json_object","schema":...} for /v1/chat/completions. The grammar documentation
explicitly lists skipped/unsupported features including uniqueItems and conditionals
if/then/else. The frozen schema uses uniqueItems and if/then. It remains unchanged.
Server grammar is a generation constraint only. Original scorer.py performs Python
jsonschema validation with the frozen environment (Python 3.10.12, jsonschema 3.2.0),
which enforces these constraints. Synthetic validator checks verify this without
feeding mock responses into the scientific scorer.

A raw final violating a grammar-unenforced schema constraint is wrong scientific
data, not INVALID_STUDY. Preserve it and continue. A rejected HTTP request, unusable
transport envelope, context/runtime failure or another frozen validity breach still
stops the campaign. Static compatibility evidence is not a completion probe or a
guarantee of runtime acceptance; no extra probe or sample model call is authorized.

The earlier verified-introspection study used the same model artifact, runtime commit,
endpoint family, schema response_format, separated reasoning and post-response Python
validation successfully. This is prior interface evidence, not an R2 observation.
Its prompts/schema, seed and generation cap differed; no outcome is transferred.

## Qualified sole launch delta

launch-plan.json records the complete exact command/cwd. The only change relative
to R1 is --slot-save-path followed by a newly allocated private R2 directory, outside
Git, mode 0700, initially empty. No save/restore operation is implemented or allowed.
Terminate the server after execution; remove the empty directory, or privately archive
unexpected contents without restoring any state. No other argv change.

Use exact Qwen3-14B Q4_K_M model SHA-256
500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0,
b11242 server SHA-256
778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5,
and both frozen runtime archives. Preserve context 16384, parallel 1, native deepseek
reasoning budget 512, temperature .2, top-p .9, top-k 40, min-p .05, seed 417351046,
generation cap 2048, stream false, fresh contexts, disabled prompt/RAM cache reuse.
The sampling fields are already in the immutable request bytes. No tools, filesystem,
repository, web, conversational history or prior answers are exposed to the model.
Only the transport host reads files; it has no gold/scorer imports or scoring feedback.

## Before real startup and Execution Freeze

Run all zero-model mock tests, including the complete 80-request schedule, exact-byte
delivery, name-shadowing regression, control/complete error-body preservation,
positive n_erased counts, timeouts, malformed finals, no retry, cleanup and evidence
separation. Mock data stays in disposable QUALIFICATION_ONLY locations and is rejected
by the scientific scoring host. Verify every inherited parent file, both invalid
campaigns, engineering result, 80 hashes/schedule, no prior R2 finals/intents, exact
model/runtime hashes, schema/source audit and sole argv delta. Commit all R2 method
files and reports as R2 Execution Freeze before any real server starts.

After that commit do not change R2 runner, transport, launch plan, tests, scoring
host, scientific inputs, flags or rules. A discovered problem means STOP and preserve
another INVALID_STUDY, even before first inference. Do not patch, restart or resume.
The user's explicit authorization permits the once-only run after all gates pass;
no additional permission request is needed.

## Startup, per-call controls and no retries

Launch once. Use the engineering-qualified log listening signal to wait up to 180
seconds without HTTP polling. Preserve and validate GET /health, GET /props and
GET /slots. The first per-call erase also establishes erase availability before
scientific request 1; there is no redundant extra startup erase.

For each of the exact 80 scheduled IDs:

1. POST /slots/0?action=erase; require HTTP 200, id_slot 0, nonnegative integer
   n_erased. A positive count after a previous call is expected, not failure.
2. GET /slots; require one isolated idle slot.
3. Exclusively record intent/hash/order; mark attempted before dispatch.
4. Send the exact saved request bytes once to /v1/chat/completions (600s timeout).
5. Preserve complete envelope privately, raw first final string verbatim publicly,
   and safe metadata, then advance without inspecting answer quality.

Every HTTP response, including control/error responses, is written privately with
headers, method/path, UTC timestamps, SHA-256 and full body before status or JSON
validation. Public control metadata references those hashes. Responses cannot enter
later prompts. No completion retries, redirects, alternate candidates or early stop
based on score. Existing raw output or execution intent blocks reruns.

Completed wrong, malformed, schema-invalid, empty or truncated final strings are
preserved and scored normally; finish_reason length alone is not a validity failure.
No stripping, JSON extraction, repair, critic or auditor rescue. Genuine server/
transport/context failure, malformed envelope or absent final-channel string stops
the campaign, terminates the server, preserves any received body and marks the rest
NOT_RUN. Never replace absent content with private reasoning or fabricated finals.
Server cleanup is mandatory on success/failure, including a forced kill only if
termination exceeds 30 seconds.

## Raw-first scoring and inherited gates

Record render ID, frozen request hash, order, start/end, wall time, HTTP status,
finish reason, prompt/completion tokens, raw final hash and envelope/reasoning hashes.
Private reasoning/envelopes/logs stay outside public ancestry. After 80 calls or a
validity stop: hash public raw evidence, mark it read-only, record raw-freeze.json
and commit raw evidence BEFORE invoking the original unchanged scorer.

score_campaign.py is only an integrity/input/output host. It checks committed raw
freeze, hashes, SCIENTIFIC_R2 purpose and unchanged inherited/method bytes, then
passes raw final strings plus any stop violation to original scorer.py. Primary
scoring runs once. Exact replay must reproduce identical score bytes without any
inference. No R2-specific scientific grading or override layer exists.

Every inherited gate is mandatory: >=17/20 semantic classifications (>=3/4 renders),
>=5/6 current defects, >=4/6 mechanical localization, healthy 4/4 avoidance with zero
current-defect false positives across 16 renders, historical 3/3 avoidance with zero
across 12, insufficient >=3/4, invalid 3/3, pairs >=5/6, consistency >=16/20,
evidence-grounded >=17/20 and invented-ID outputs zero. protocol.json and scorer.py
are authoritative. Secondary class/family/representation/localization/citation/error
analyses are descriptive only and cannot revise the primary score.

## Preservation, publication and stop

Verify all inherited bytes, protected branches, runtime identity and original v0/R1/
engineering classifications afterward. No Horus Memory, world execution, receipts,
training, policy, thresholds, S+E architecture change or improvement proposals.
All private archives/logs/reasoning remain outside the published ancestry. Scan all
reachable public history with unchanged repository secret rules and publish only R2.
Report chronology separately, plus raw-before-score commit, replay, all metrics/gates,
limitations and exact runtime/control observations. Stop after publication. No Horus
diagnosis, follow-up model calls, repair or self-improvement work is authorized.
