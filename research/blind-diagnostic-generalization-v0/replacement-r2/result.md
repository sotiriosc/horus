# R2 result: blind diagnostic capability not established

The original unchanged scorer returned
`BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0`.
Separate metadata: `replacement_id: R2`.
The campaign completed 80 attempted / 80 completed calls with no validity stop.
Only 1 of 13 mandatory gates passed. This is a valid negative capability result
under the frozen benchmark, not an INVALID_STUDY or a Horus diagnosis.

Branch: `research/blind-diagnostic-generalization-v0-replacement-r2`.
The final publication commit is the audited remote head reported with publication;
the committed audit records its immediate predecessor, and the final head is
audited again before the exact-SHA push.

| Milestone | Commit |
|---|---|
| Original Method Freeze | `587ffedd39516b633376d222d6d84e6af186fcf8` |
| Original Case Freeze | `2866e6bcf94539513c135df878b72058048e99cd` |
| R2 base / engineering qualification | `df2d0ebc41d7c1b53a85779c38dab45cb21ec2e9` |
| R2 Execution Freeze | `d7df165e08a20e6302d8b4e72224ac69dc69df63` |
| R2 raw-evidence commit, before scoring | `364c3eb06635751b47d540d46c5792fd45a4fb7d` |

## Primary scores and all mandatory gates

Semantic classification requires at least three correct renderings out of four.
The 20 semantic cases are the designed scientific units; 80 renderings are not
80 independent samples. A correct rendering requires full schema validation,
valid IDs, and the correct class. Localization and evidence grounding impose
additional frozen conditions.

| Mandatory gate | Observed | Required | Result |
|---|---:|---:|---|
| Semantic classification | 9/20 | at least 17/20 | FAIL |
| Current-defect classification | 6/6 | at least 5/6 | PASS |
| Current-defect mechanical localization | 0/6 | at least 4/6 | FAIL |
| Healthy worlds avoiding current defect in every rendering | 2/4 | 4/4 | FAIL |
| Healthy rendering current-defect false positives | 3/16 | 0 | FAIL |
| Historical worlds avoiding current defect in every rendering | 0/3 | 3/3 | FAIL |
| Historical rendering current-defect false positives | 10/12 | 0 | FAIL |
| Insufficient-evidence classification | 0/4 | at least 3/4 | FAIL |
| Invalid-evidence classification | 0/3 | 3/3 | FAIL |
| Matched counterfactual pairs | 3/6 | at least 5/6 | FAIL |
| Representation-consistent worlds | 11/20 | at least 16/20 | FAIL |
| Evidence-grounded worlds | 0/20 | at least 17/20 | FAIL |
| Invented-ID outputs | 3/80 | 0 | FAIL |

Schema-valid finals: **77/80**. All 80 finals were strictly parseable JSON and
contained a recognized classification. Three failed full schema validation at
`causal_mechanism` under a conditional constraint. None was repaired.
Frozen rendering classification credit was 40/80.

## Confusion matrix and per-class performance

Rows are gold classes and columns are raw, strictly parsed selected classes,
including schema-invalid answers. This matrix is descriptive; scientific credit
also requires schema and ID validity. There were zero unparseable/no-class finals.

- D: `SUPPORTED_CURRENT_DEFECT`
- H: `NO_SUPPORTED_DIAGNOSIS`
- U: `INSUFFICIENT_EVIDENCE`
- T: `HISTORICAL_DEFECT_NOT_CURRENT`
- X: `INVALID_OR_CONTRADICTORY_EVIDENCE`

| Gold / selected | D | H | U | T | X |
|---|---:|---:|---:|---:|---:|
| D | 24 | 0 | 0 | 0 | 0 |
| H | 3 | 13 | 0 | 0 | 0 |
| U | 14 | 1 | 0 | 1 | 0 |
| T | 10 | 1 | 0 | 1 | 0 |
| X | 8 | 2 | 0 | 0 | 2 |

| Gold class | Schema valid | Correct renderings | Correct semantic cases |
|---|---:|---:|---:|
| D | 24/24 | 24/24 | 6/6 |
| H | 15/16 | 13/16 | 3/4 |
| U | 16/16 | 0/16 | 0/4 |
| T | 11/12 | 1/12 | 0/3 |
| X | 11/12 | 2/12 | 0/3 |

Healthy semantic correctness (3/4) differs from the stricter healthy avoidance
gate (2/4): one erroneous current-defect rendering can fail avoidance despite
three correct renderings. Similarly, representation consistency can include a
consistently wrong class and is not a substitute for correctness.

The model selected U zero times. Of 16 insufficient-evidence renderings, 14 were
labeled D, one H, and one T. Thus the observed abstention failure was failure to
withhold a diagnosis, rather than excessive abstention on current defects.
Historical-to-current errors occurred in 10/12 renderings. Invalid evidence was
correctly selected in only 2/12 renderings and mislabeled D in 8/12.

## Defect families, localization and evidence

All-variant columns include the family's current-defect case and its controls.
Each family has one current-defect semantic case with four renderings.

| Family | All-variant correct renderings | All-variant correct worlds | Current-defect correct renderings | Current-defect localized worlds |
|---|---:|---:|---:|---:|
| Version selection | 6/20 | 1/5 | 4/4 | 0/1 |
| Authority precedence | 4/8 | 1/2 | 4/4 | 0/1 |
| Entity binding | 8/12 | 2/3 | 4/4 | 0/1 |
| Publication update | 9/16 | 2/4 | 4/4 | 0/1 |
| Operation idempotence | 5/12 | 1/3 | 4/4 | 0/1 |
| Boundary comparison | 8/12 | 2/3 | 4/4 | 0/1 |

Among the 24 schema-valid current-defect renderings, 23 matched the exact affected
component list and one did not. None matched an accepted frozen structured causal
witness, including the preregistered alternatives. All 23 with correct components
therefore still failed the witness requirement. Frozen localization was 0/24
renderings and 0/6 worlds. This does not assign any informal semantic credit to
the unscored prose.

Evidence grounding passed for 2/80 renderings, both in the invalid-evidence class,
and for 0/20 semantic worlds. Required evidence was missing from 75/77 schema-valid
finals and 38/40 correctly classified finals. The frozen scorer flagged three
outputs for bad/invented IDs, comprising four output-ID pairs and four distinct
IDs. The precise per-render diagnostics and IDs are in `secondary-analysis.json`.

## Representation factors and matched pairs

Label-map A: 19/40 correct. Label-map B: 21/40 correct.
Presentation order 1: 21/40 correct. Presentation order 2: 19/40 correct.
Selected classes disagreed across label maps in 9/40 matched contrasts and across
presentation orders in 7/40 contrasts. These are descriptive comparisons of
correlated renderings, not significance claims.

Matched-pair results: P1 failed (2/4 jointly correct cells); P2 failed (0/4);
P3 passed (4/4); P4 passed (3/4); P5 failed (0/4); P6 passed (4/4).
The unchanged scorer also requires both semantic endpoints to be correct.

## Runtime, controls and prospective schema limitation

Before inference, all 23 zero-model transport tests passed, including an 80-call
mock schedule isolated from scientific scoring. The execution freeze committed
the preregistration, exact inherited hashes, launch command, transport, preflight
and pinned-source compatibility audit. None of those 11 frozen R2 files changed.

Runtime: Qwen3-14B Q4_K_M, llama.cpp b11242, commit
`526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`.
Model SHA-256:
`500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0`.
Installed server SHA-256:
`778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5`.
Runtime archives and installed binary were rehashed in postflight.

The exact frozen request bytes supplied temperature 0.2, top-p 0.9, top-k 40,
min-p 0.05, seed 417351046, max_tokens 2048, stream false, and the unchanged schema.
The launch used context 16384, parallel 1, native deepseek reasoning with budget
512, no prompt cache, no cache reuse, and no model tools, web, filesystem,
repository access or conversational history. Server `/props` reports baseline
generation defaults; those are not the per-request overrides in the saved bytes.

The sole launch change from R1 was `--slot-save-path` with a fresh private R2
directory. The pinned server launched once. Startup health and props each returned
HTTP 200. All 81 slot inspections and 80 per-request erases returned HTTP 200.
All 80 completions returned HTTP 200 with `finish_reason: stop`, and all 80 had
native reasoning separated from the final string. No call reported length termination.
Both reported cached-token counts and timing cache counts were zero for every
call. The first erase reported zero; the following 79 reported positive erasures
(maximum 3324), which is expected clearing behavior. Save/restore was never used.
Prompt tokens ranged 1367–1534; completion tokens ranged 820–1829. Completion-token
counts include generated reasoning and finals as reported by the server.

Complete HTTP bodies were preserved privately before status or JSON validation.
Postflight verified 243 private HTTP bodies and 80 preserved completion envelopes
against their recorded hashes, and all 80 dispatched request hashes and positions
against the frozen schedule. The server terminated, the dedicated port closed,
and the still-empty private slot directory was removed.

`schema-runtime-audit.json` prospectively verified the exact source's support for
`response_format={"type":"json_object","schema":...}` at `/v1/chat/completions`.
It also recorded unsupported/skipped grammar constraints, including `uniqueItems`
and `if`/`then`/`else`, which occur in the frozen schema. Grammar is a generation
constraint only; the unchanged Python jsonschema 3.2.0 validator is authoritative.
The three returned conditional-schema violations count as wrong, not as runtime
invalidity. No schema was weakened. Earlier verified-introspection success with
the same artifact/runtime/interface was recorded solely as prior interface
evidence, not as an R2 observation or guarantee.

## Evidence order, replay, preservation and publication

Execution finished at `2026-09-29T14:30:54.439209+00:00`; raw hashing finished at
`2026-09-29T14:30:54.451527+00:00`. The 162 raw files were made read-only, verified
against the manifest and mechanically scanned for publication secrets.
Raw commit `364c3eb06635751b47d540d46c5792fd45a4fb7d` was created at
`2026-09-29T10:31:39-04:00`, directly after the Execution Freeze, before the single
primary scorer invocation. That commit contains all raw evidence and no scores
or secondary analysis. `postflight.json` verifies these facts against Git objects.

The original unchanged `../scorer.py` scored raw first final-channel strings once
for the primary result. A separate no-inference replay reproduced the score file
byte for byte. Score SHA-256:
`961dbaec40add7673aba15328efe9fd3f8d8eae5cd676b7da0c9043dc52f1883`.
`analyze_results.py` only describes already-scored evidence and verifies that it
does not change the primary score bytes. No retry, repair, re-prompt, answer
selection, critic, semantic correction, or auditor rescue occurred.

Preserved chronology:

| Study | Preserved result | Model calls | Preserved public head |
|---|---|---:|---|
| Original v0 campaign | INVALID_STUDY; Python transport name shadowing | 0 | `bb58926e0f2581bee38393e179b758b18d0879e4` |
| R1 | INVALID_STUDY; slot erase HTTP 501 | 0 | `b156dd01ce6f1deed049fa2589581888d36f34fb` |
| Engineering qualification | REAL_RUNTIME_CONTROL_PATH_QUALIFIED | 0 | `df2d0ebc41d7c1b53a85779c38dab45cb21ec2e9` |
| R2 | BLIND_DIAGNOSTIC_CAPABILITY_NOT_ESTABLISHED_V0; replacement_id R2 | 80 | This separate branch |

Postflight verified all 1643 inherited tracked files byte-for-byte, all 184
materialized hashes, all 80 request hashes, nine protected branch heads and all
11 Execution Freeze files. No worlds or requests were regenerated. Fifteen
private-archive heads remain excluded from reachable ancestry.

Active Horus remains grounded authority -> S -> E -> ordinary model. Architecture,
Memory, policy and thresholds are unchanged. No Horus world execution, new Horus
receipts, Memory writes, training or improvement proposal occurred. This
attestation rests on file/ref checks and the isolated operation history; no
private Memory database was opened for inspection.

Publication uses the unchanged full reachable-history secret audit over every
reachable commit/path and every unique blob. `publication-audit.json` preserves
the first passing result; the final head is audited again before an exact-SHA
push of this branch alone, with follow-tags disabled, followed by remote head
verification. Public evidence consists of raw final strings, safe metadata,
hashes, scores and reports. Private reasoning, response envelopes and server logs
remain outside Git; `private-evidence-manifest.json` records hashes of 809 private
files. No authentication keys, raw signed streams or private Memory databases are
published.

This small synthetic benchmark and exact structured-witness scoring support only
the stated frozen result. They do not establish a general diagnostic capability,
change any prior study, or authorize applying an outcome to Horus. No merge,
model switch, follow-up study or improvement proposal is performed. Stop after
publication verification.
