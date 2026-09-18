# Evidence retention

Only four existing artifacts are retained directly. Each is a required, synthetic numerical golden used by the original tile benches. The historical Make recipe does not regenerate these files, so retaining their exact bytes preserves the measured 1,000-case sets without inventing a replacement distribution.

| File | Decision / reason | SHA-256 |
|---|---|---|
| `tests/fixtures/tile/TILE_E4M3_OPS.hex` | KEEP: required original tile operand or expected-output fixture | `e1a5d4af3fc91d61ea19a348c8518fb4c56e5d67847ce4b41c2d7dfa422d34b9` |
| `tests/fixtures/tile/TILE_E4M3_OUT.hex` | KEEP: required original tile operand or expected-output fixture | `ba65d0d6454ff73b79e5c9564d76ba6eea4b35433eb772c0073a68c25ad7a32d` |
| `tests/fixtures/tile/TILE_E3M6_OPS.hex` | KEEP: required original tile operand or expected-output fixture | `6ba8d12a5a6142fec7a924abf1cc15a88e0a947936aa3a52f0120cda2219b433` |
| `tests/fixtures/tile/TILE_E3M6_OUT.hex` | KEEP: required original tile operand or expected-output fixture | `fc73e9cfda6637bebf6e2249567533c7866a2b7b71ab1519f63b58bfc749b25f` |

All ten previously nominated historical CSV/log evidence files are excluded from this candidate and preserved in the original research archive. Decision: REGENERATE the applicable current measurements using `make experiments` or `make synthesis`; do not claim a regenerated file is the historic artifact. Full long-sweep data is not represented as freshly reproduced.

Normalizer/Jacobi/vector data is generated before its consumer runs. Routine JSON, CSV, PNG, NPZ, synthesis logs, simulator binaries and waveforms are not shipped. Each retained fixture can be checked against the export manifest; no directory of generated results is approved wholesale.
