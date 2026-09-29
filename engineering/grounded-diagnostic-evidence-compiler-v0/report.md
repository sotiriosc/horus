# Grounded diagnostic evidence compiler v0

Result: **`GROUNDED_DIAGNOSTIC_EVIDENCE_COMPILER_FEASIBLE_V0`**. The declared mechanical facts were reproducibly extracted from supplied case evidence without model inference or diagnostic gold. This is an engineering feasibility result on reused fixtures, not diagnostic capability, improved Qwen performance, correct final classifications, Horus self-diagnosis, self-improvement or evidence that a future hybrid architecture would help.

Branch: `engineering/grounded-diagnostic-evidence-compiler-v0`. Base: `5687d82cc3eede8561ef435b980f23d919518c26`. The final publication SHA is the audited remote head returned in the publication report; a commit cannot embed its own SHA.

| Freeze | Commit |
|---|---|
| Mechanical contract and mutation expectations | `11776ad70b29a82f85c34115c088a494370a0f04` |
| Qualified implementation | `c6a04593237ec5af5b2661c5b9813ef274e13448` |
| Compiled results and byte replay | `c601974af21f495c36df8a3a2e1e7667452a64c6` |

The mechanical contract was committed before implementation results. The implementation freeze followed 25 passing synthetic tests and preceded all R2 fixture compilation. No frozen contract, compiler, worker, normalizer, harness or test was repaired after the fixture run began. R2 and its postmortem are preserved without score changes or reinterpretation.

## Inputs and dependency boundary

The compiler receives only `{case, contract}`: the raw diagnosis-time case object and the frozen generic evidence-format contract. It receives no rendering/case grouping metadata, gold, family, selected class, model final, score, witness, postmortem code or matched-pair information. The outer harness uses public render-manifest grouping metadata solely to associate the four representations of each world and name artifacts. All fixture bytes are hash-checked.

The pure compiler imports only `json`. Its static audit scanned 100 rendering/group identifiers and rejects literal opaque IDs, diagnostic labels, family names, expected operational field lookups, forbidden file names, non-allowlisted imports, IO calls, dynamic evaluation and reflection. Forbidden strings occur only in the audit/tests that verify their absence. The implementation contains no diagnostic output classes as operational labels.

Each compiler runs under `python -I -S`. After loading its source and standard-library bootstrap, a runtime audit hook denies every file open, network/subprocess activity and dynamic import; the explicit import wrapper permits only the already-loaded `json` module. Malicious-module probes confirmed that attempted file access and imports of filesystem/network modules fail. During the real engineering run, the harness read exactly 81 allowlisted paths: 80 public case files and the mechanical contract. No forbidden read was attempted, no gold file was read, and the scientific scorer was not imported. The dependency tokens used for absence testing are not compiler decisions.

Preservation and publication checks operate separately after compiler execution. They hash inherited public Git files without feeding their contents into compilation. No private reasoning, envelopes, logs or Memory databases were opened.

## Feasibility observations

All **20/20 semantic evidence packages** were processed through **80/80 renderings**. All 80 outputs passed the published JSON schema and independent extraction checks. All 20 groups had identical normalized full outputs across A/B labels and both presentation orders. Counts below use one A/order-1 representative per world unless explicitly labeled otherwise; the four renderings are not independent scientific samples.

| Mechanical measurement | 20 representative packages | All 80 renderings |
|---|---|---|
| Record entries preserved exactly | 160 | 640 |
| Exact UNKNOWN locations | 12 | 48 |
| Explicit record-to-event links | 60 | 240 |
| Explicit output/capture links | 20 | 80 |
| Typed field-inventory entries, including containers | 733 | 2932 |
| Evidence graph nodes | 300 | 1200 |
| Evidence graph edges | 280 | 1120 |

**Deployment:** explicit current deployment was recovered in 20/20 worlds. Their records partitioned into 59 current, 41 non-current/historical, 60 unversioned and zero unresolved. These are version-binding facts only. Release ordinal was never used to select deployment; the synthetic switch-to-another-declared-version and remove-deployment tests verified that boundary.

**UNKNOWN:** 12 exact locations occurred across four representative packages, with package counts 1, 2, 3 and 6; 16 packages had none. Every occurrence retains its record ID, exact JSON pointer, literal value and binding status. No value was filled, equation solved, default guessed or epistemic class assigned. The substring test verified that ordinary prose containing the word is not an exact UNKNOWN value.

**Event linkage:** 60 explicit record/event relations yielded 20 output/capture links. All relationships use identifier equality, never payload resemblance. Breaking/removing an explicit event identifier removed the link and exposed missing-link ambiguity in the synthetic tests.

**Field inventory:** 733 entries preserve relative-to-data and full raw-case JSON pointers, exact values and exact JSON types. Roots and containers are explicitly marked; they are not selected as decisive fields. Pointer escaping, booleans versus integers/numbers, nested arrays and opaque dictionary keys are tested. Every inventory entry was checked against source data.

**Graph:** 280 representative edges have declared mechanical reasons and exact source-field provenance. An additional read-only verification checked all 1,120 edges across all renderings against their source fields, endpoint kinds, identifier equality and chronology. No semantic causes edge exists. Contract record IDs are merely present context, not a claim of relevance.

**Input/output candidates and ambiguity:** 40 representative output records each had one structural input candidate; the original fixture packages generated no ambiguity flags. Synthetic tests retained both inputs when two candidates qualified, reported missing links instead of guessing, preserved duplicate-ID occurrences with ambiguity, and left deployment unresolved when declarations were absent or conflicting. A single structural candidate is not a causal assertion.

## Capture and provenance facts

The generic `capture_contract` statement was recorded prospectively and qualified as byte-identical common format text in every fixture. The compiler never parses operational contract prose. Equality of supplied digest strings does not recompute a digest or authenticate physical evidence. Explicit linkage depends on the supplied identifiers and declared format semantics.

| Declared check | Equal/consistent | Unequal/inconsistent | Unknown |
|---|---|---|---|
| Capture deployment vs declared current snapshot | 19 | 1 | 0 |
| Recorded vs supplied recomputed digest | 19 | 1 | 0 |
| Payloads claiming the same immutable event | 19 | 1 | 0 |
| Linked output version vs capture deployment version | 18 | 2 | 0 |

Sixteen representative packages had all applicable declared checks consistent; four had at least one inconsistency. The checks overlap, so their false counts do not sum to distinct packages. These are format-check facts only. They were not compared with diagnostic gold and were not mapped to any diagnostic class.

The linked-version equality is a separately declared binding rule in this engineering contract: it compares an output record’s explicit version with its linked capture’s deployment-version field. The observed equality or inequality is mechanical. Treating that equality as a required invariant depends on the supplied format contract; this study does not establish that every other capture format must require it. Likewise, `integrity_consistent=true` covers only the checks implemented under this contract, not general evidence sufficiency or operational correctness.

Per-package counts and exact conflicting values/paths are available in [feasibility-results.json](results/feasibility-results.json) and the linked [compiled JSON directory](results/compiled).

## Normalization, mutations and replay

Raw full pointers preserve the actual record/component/version array positions. They therefore change when the source arrays are reordered. For comparison only, the harness anchors those positions by input entity ID, then derives label correspondence from ID-masked evidence structure. It consults no family, gold mapping or expected witness. Ambiguous structural alignment would fail the normalization gate rather than choose a gold-compatible mapping. All 20/20 complete outputs matched across all four representations, including graph edges, integrity facts, UNKNOWN status and partitioning.

All **19/19 preregistered mutation tests** passed:

| Mutation | Expected mechanical behavior verified |
|---|---|
| reverse_records | Anchored normalized output byte-identical; raw full pointers remain correct |
| reverse_components | Anchored normalized output byte-identical |
| reverse_versions | Anchored normalized output byte-identical; deployment not inferred from ordinal |
| rename_opaque_labels | Reverse-map output labels then anchor; all facts identical, no original opaque label leaked |
| introduce_unknown | One additional exact UNKNOWN location; value preserved; no class or imputation |
| remove_unknown | Original output bytes restored |
| switch_deployment | Current/historical partition swaps for bound records; capture snapshot mismatch exposed; no diagnosis |
| break_event_equality | Matching output/capture link removed; missing-capture-link ambiguity; no similarity join |
| payload_conflict | Payload integrity false; exact two source pointers and values present |
| digest_conflict | Digest check false at exact two paths; no recomputation claim |
| remove_explicit_event_link | No output/capture edge for that capture; missing-event-link ambiguity and unknown payload linkage |
| multiple_input_candidates | Both candidates retained; ambiguity; no nearest/gold-selected candidate |
| remove_deployment | current_version null; versioned records unresolved; ambiguity; ordinal cannot rescue |
| conflicting_deployment | current_version null; deployment ambiguity |
| typed_payload_conflict | Typed mismatch reported, never equal via Python coercion |
| unknown_payload | Payload check unknown rather than asserted equality/conflict |
| reorder_object_keys | Compiler bytes identical |
| unknown_prose_substring | No exact-UNKNOWN hit for that string |
| duplicate_record_id | Both occurrences retained, duplicate-ID ambiguity; no silent overwrite |

The full synthetic suite passed **25/25 tests**, including independent inventories, dependency rejection and normalization/provenance cases. The entire frozen fixture run was then replayed into a fresh directory. All **81/81 artifacts**—80 compiled outputs and the engineering result—were byte-identical. Replay made no model calls. An independent full-schema check passed for all 80 outputs. Post-run verification added no mutation, scoring rule or compiler behavior.

## Responsibility boundary

| Fact / responsibility | Mechanical now? | Still requires semantic judgment? |
|---|---|---|
| Declared current deployment | Yes, with explicit consistent declaration and known version | Trust or adjudication beyond those supplied declarations is outside scope |
| Record/version partition | Yes; unresolved is retained when binding cannot be established | Whether any non-current behavior matters to a diagnosis |
| Record, component, version and event IDs | Yes, copied from input | Relevance of a record to a diagnostic claim |
| Exact field paths, values and types | Yes, all structured data nodes exposed | Which fact is decisive |
| UNKNOWN locations | Yes, exact inventory; no imputation | Whether omitted information prevents a justified diagnosis |
| Digest equality | Yes, supplied strings compared | Authenticity/provenance beyond declared fields is not established |
| Explicit event linkage | Yes, identifier equality with source paths | Causal significance is not inferred |
| Capture payload conflicts and version differences | Yes, under the frozen generic format contract | Whether the assumed format applies and what the facts imply diagnostically |
| Input/output relationships | All structural candidates retained | Which relation is causally decisive when semantics are needed |
| Evidence graph and candidate witness addresses | Yes, with explicit reasons and provenance | Selecting a correct causal witness |
| Meaning of operational contract prose | No | Yes |
| Whether current facts violate that contract | No | Yes |
| Plausibility of benign alternatives | No | Yes |
| Required value implied by operational semantics | No; only supplied actual values are inventoried | Yes when the requirement is semantic |
| Sufficiency for a positive diagnosis | No | Yes |
| Final epistemic class | No class emitted | Downstream semantic responsibility; not tested here |

The compiler exposes addresses and exact facts. It does not choose the correct defect, decisive field, operationally required value, accepted witness or final class. No downstream architecture was designed, promoted or evaluated.

## Preservation, zero inference and publication

Postflight verified **1,852 inherited tracked files**, **80 fixture hashes**, **162 R2 raw hashes**, the frozen mechanical/implementation commits and results, and **11 protected local plus 11 protected remote heads**. R2, its raw evidence and score bytes, its deterministic postmortem, original v0/R1 INVALID_STUDY histories, runtime-control qualification, S, E and active Horus architecture remain unchanged. R2 score SHA-256 remains `961dbaec40add7673aba15328efe9fd3f8d8eae5cd676b7da0c9043dc52f1883`. Memory/policy/threshold source bytes are preserved.

The previously documented main difference remains untouched: local main `b8e4245ef14b11ee5d94ce851aec4d8dc059963f`, remote main `f79b1e5df3deae6941e62349aeea5eeec310e581`. All protected remote heads are verified again after publishing only this engineering branch.

**Qwen calls: 0; other model calls: 0; model-server starts: 0; Horus world executions: 0; receipts: 0; Memory writes: 0; training: 0; policy changes: 0; architecture promotion: 0; self-improvement proposals: 0.** The compiler workers are ordinary deterministic Python processes, not model inference.

The unchanged reachable-history publication audit examines every reachable commit/path and unique blob. A passing audit is committed as `publication-audit.json`; the exact final head is audited again before its SHA alone is pushed with follow-tags disabled. Fifteen private-archive heads remain outside public ancestry. No private archives, reasoning, response envelopes, credentials or Memory databases are published. The final publication SHA and remote verification are returned to the user.

Artifacts: [mechanical contract](mechanical-contract.json), [mutation contract](mutation-contract.json), [output schema](output-schema.json), [synthetic qualification](synthetic-test-results.json), [engineering results](results/feasibility-results.json), [exact replay hashes](exact-replay.json), [structural edge verification](structural-verification.json), [preservation verification](preservation-verification.json), and [reproduction instructions](README.md).

Stop after publication verification. No fresh diagnostic benchmark, two-arm model study, final diagnosis or architecture promotion follows this result.
