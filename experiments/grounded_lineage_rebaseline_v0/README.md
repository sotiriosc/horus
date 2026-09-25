# Grounded lineage rebaseline v0

Zero-inference audit at parent `f44bd60`. Read [the report](../../research/grounded-lineage-rebaseline-v0-results.md) and [claim eligibility](claim_eligibility.json) before reusing a historical result.

`clean-root-manifest.json` pins current entrypoints and exact file versions. The eligibility manifest restricts research claims; it does not install runtime enforcement or remove historical code. Never replace old classifications with its current-use field.

Reproduce only the offline checks, from repository root, with an existing output directory outside the public tree:

```bash
python -m experiments.grounded_lineage_rebaseline_v0.verify --repository . --output "$rebaseline_evidence/authority-and-mutation.json"
python -m experiments.grounded_lineage_rebaseline_v0.dependencies --repository . --output "$rebaseline_evidence"
```

Set `rebaseline_evidence` to your chosen audit directory first. The verifier blocks sockets, HTTP, and legacy A/B/C law-authority functions. It executes existing tests and throwaway deterministic fixtures; it does not start a server, replay inference or alter historical evidence. Raw legacy imports in optional driver closures are not permission to use them as reality authority.

With access to the original separately retained R1 **real** archive, verify the committed event and later actual model input:

```bash
python -m experiments.grounded_lineage_rebaseline_v0.proof_chain --archive "$retained_r1_real_archive" --output "$rebaseline_evidence/retained-proof-chain.json"
```

This requires the retained journal, steps, model calls and referenced Memory snapshot. It does not regenerate missing evidence. Original Python object identity cannot be reconstructed from JSON; the source issuer, historical identity assertions and recorder remain trust assumptions. The public compact proof includes source-file hashes and exact finite identities without full raw model archives.

The per-checkpoint policy is an explicit reviewed interpretation; regenerating an import graph does not automatically establish claim eligibility. Retain that distinction when using these scripts on another revision.
