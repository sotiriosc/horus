# REAL_RUNTIME_CONTROL_PATH_QUALIFIED

The exact pinned real runtime, launched once with the prospectively declared private
slot-save directory, successfully exposed all four required control endpoints.
**Model completion calls = 0; benchmark requests = 0; prompts submitted = 0.**
This is engineering qualification only, with no diagnostic-capability classification.

Branch: `engineering/blind-diagnostic-runtime-control-qualification-v0`.
Parent R1 publication: `b156dd01ce6f1deed049fa2589581888d36f34fb`.
Source audit, plan and tested client committed before startup:
`8a22e1d16de60c525ea080631801377867108fda`.

## Source-backed explanation, separate from historical observation

Exact upstream source commit: `526c43b8f7dfea9032e9f35e7a1be9183ca7cc20`.
Downloaded from the commit-pinned upstream codeload URL; the archive's Git commit
comment independently matched that exact SHA. source-audit.json preserves archive
hash, per-file SHA-256/Git blob hashes, line references, links and excerpts.

- Registered route: tools/server/server.cpp:291, POST /slots/:id_slot.
- Gate: tools/server/server-context.cpp:4754-4756 checks
  `params.slot_save_path.empty()` and returns NOT_SUPPORTED before action dispatch.
- Error mapping: tools/server/server-common.cpp:60-63 assigns code 501.
- Dispatch: tools/server/server-context.cpp:4777-4778 routes action erase to
  handle_slots_erase; lines 5344-5368 implement that handler.
- Parameter: common/arg.cpp:3611-3623 declares --slot-save-path, requires an existing
  directory and sets the field. tools/server/README.md:225 documents default disabled.

**Source-established behavior:** an empty slot-save path rejects slot actions.
**R1-observed behavior:** its first erase received HTTP 501; its stored command omitted
--slot-save-path. **Inference:** the missing flag explains R1's status through the
pinned source gate. R1's unretained response body was neither observed nor recreated.
The preserved original v0 and R1 classifications remain INVALID_STUDY / zero calls.

| Pinned source file | SHA-256 |
| --- | --- |
| tools/server/server.cpp | `9cf6bf6f464fad94172c09b2f9e6a4eea3e69b96117ed1b14b31e0de094c130e` |
| tools/server/server-context.cpp | `9661214669507b14f35b53e65f6a0fd0496b0f79fc142ee5bb843bb31f7a6109` |
| tools/server/server-common.cpp | `28e058d1ab9f290b35d382fcd8869012f6d40276cb440ddf7a585ca33a8367fb` |
| tools/server/server-task.cpp | `0fd5c8df2525e61214986e8abe3fc4edbb92f5dd652c9c2bfd1bc2712218a585` |
| common/arg.cpp | `8ef15365dd8fd2001f3c328e81ca8be11de1ac25029a7a3a07c1ab0944079c41` |
| tools/server/README.md | `37866b6b348e49a44205f776467afc16322d136bfa06c4448354a6c93b74f52e` |

## Sole command delta and isolation

The complete command/cwd is preserved in plan.json and launch-preflight.json. Compared
with R1, the sole argv addition was:

```text
--slot-save-path /tmp/horus-runtime-control-qualification-v0-private/slots-af1oco9d
```

Every other flag, artifact, library path, GPU setting and localhost address was
unchanged. The directory was fresh, outside the repository, mode 0700 and empty
before launch. No save or restore action occurred. It remained empty and was removed
after server termination. No slot-state files needed archiving. Private startup logs
and launch intent remain outside Git, with hashes in private-evidence-manifest.json.

The pinned API docs do not explicitly guarantee repeated-empty idempotence, so the
prospective plan omitted a second erase. No inference was used to populate the slot.

## Exact runtime/model identity

Model: Qwen3-14B Q4_K_M. Runtime: llama.cpp b11242, commit
526c43b8f7dfea9032e9f35e7a1be9183ca7cc20. The actual /props body reports
b11242-526c43b8f and one slot. Artifact hashes matched before and after the launch.

| Artifact | SHA-256 |
| --- | --- |
| model/Qwen3-14B-Q4_K_M.gguf | `500a8806e85ee9c83f3ae08420295592451379b4f8cf2d0f41c15dffeb6b81f0` |
| engine/llama-b11242-bin-ubuntu-cuda-12.8-x64.tar.gz | `6ab3e1d60a6cab34806ae23c90956ba668047c3bc056eab3be2bfa73eca24fac` |
| engine/cudart-llama-b11242-bin-ubuntu-cuda-12.8-x64.tar.gz | `e67423c1553f8f4cd22d6412c74604a6d50b9b3cccb48546758b55e912407603` |
| installed_server | `778f1b3fbbb76e921af1d7f25a5b61d82859962dcd18c71ce86ab84d7f4884e5` |

## Real control observations

Exactly four requests, in the declared order, each once. Startup readiness was
observed from the server's listening log before the first request; no health polling
or additional HTTP request occurred. Every complete response body was persisted
before status or JSON validation, with method/path, timestamps, headers and SHA-256.

| Request | HTTP | Complete response SHA-256 | Evidence |
| --- | ---: | --- | --- |
| GET /health | 200 | `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` | [body](observations/1-response.txt) |
| GET /props | 200 | `eae08e0d576a8e94b305ccf9863e77cb392bf8deccf230f8c19a1074ed96d80e` | [body](observations/2-response.txt) |
| GET /slots | 200 | `17cbc9057408bdd04d592843e68758399cb7e770c716b5d71c8536539e6921d4` | [body](observations/3-response.txt) |
| POST /slots/0?action=erase | 200 | `3877222144555dd01aabfc7f20c7b27229c25f48fdb0e2ef1254b18bd7bf2fd8` | [body](observations/4-response.txt) |

/health returned status ok. /props confirmed the pinned build and single slot.
/slots showed the single slot idle. Erase returned exactly the JSON values
`{"id_slot":0,"n_erased":0}`, establishing that the formerly failing control endpoint
works under the sole prospectively declared configuration addition. Full raw bodies
are retained without reserialization, truncation or answer repair.

Six mock tests passed before startup, including complete 501-body preservation before
raising, malformed-success retention, all four real HTTP code paths and rejection
of generation endpoints and prompt bodies before connection. Mock outputs were
removed and are not scientific observations. One real server was started and
terminated; no retries or flag changes were made after startup.

## Preservation and interpretation

Postflight checks preserve every one of the 1620 inherited parent files byte-for-byte,
including original Method/Case Freeze, 80 requests, grading, scorer, protocol, the
original invalid campaign and the R1 invalid campaign. All 184 materialized hashes
and 80 request hashes match. The eight prospective engineering files also match
their pre-startup commit. Protected public heads remain unchanged; private archive
heads remain outside public ancestry. No worlds, opaque labels or gold were regenerated.

No Horus Memory writes, world execution, authenticated receipts, training, policy or
threshold change, proposals or active S+E modification. No benchmark was scored.
Full public history is audited using unchanged repository secret rules, including
an exact-final-head audit before publishing only this engineering branch.

This provides a clean **control-path engineering basis** for a separately reviewed
and preregistered R2 that explicitly includes the slot-save-path configuration and
complete error-body preservation. It does not establish completion-endpoint/schema
compatibility, populated-cache erasure, Qwen behavior, benchmark performance,
diagnostic ability, Horus self-diagnosis or RSI. Those were not tested here.

**STOP after publication. R2 has not been created or executed.**
