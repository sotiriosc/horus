# Qwen Error-Driven QLoRA Learning v0 — prospective method

Base: `379912673e692c7b4b7c28aa5b3a17b2bffbc0d3`.
Branch: `research/qwen-error-driven-qlora-learning-v0`.
This externally designed experiment tests supervised adapter learning from independently verified mistakes. It does not modify Horus, Memory, S, E, policy, main, any prior study or the active model. No merge, deployment or promotion is authorized. Publish the audited research branch and stop at the registered gate.

## Identity and qualification

`upstream-provenance.json` pins Qwen/Qwen3-14B at `231c69a380487f6c0e52d02dcf0d5456d1918201`, its tokenizer, configuration, template and eight safetensor identities. The official pinned GGUF declares this upstream; the upstream weights have identical hashes at their initial upload, the contemporary revision and the latest inspected revision. The historical GGUF is not trained or used for M0. Its internal AWQ-compatible name is recorded as a provenance limitation; it does not override the official base declaration. The HF and GGUF templates differ. Every new arm uses the identical pinned HF template and NF4 representation.

Engineering qualification uses synthetic copy fixtures only, including all nine requested JSON value combinations, long neutral padding, full-context forward/backward passes, optimizer steps and exact adapter checkpoint save/reload. It must pass before Method Freeze. It reads no scientific case. The isolated package lock, GPU/driver/CUDA, all-GPU parameter placement, coverage, trainable count, loss/gradient checks and peak allocation are in `engineering-qualification.json`. Jinja2 was updated in the isolated environment to satisfy the tokenizer's template API before qualification; system packages were not changed. No scientific accuracy is used to select a recipe. The first synthetic qualification was interrupted by a reported computer freeze/restart; no completed qualification or scientific artifact resulted. See `restart-record.json`. Before Method Freeze, the engineering context was reduced from 3072 to 1536 (every generated prompt plus output fits below 1122), AdamW temporary allocation was reduced with foreach=False, CPU threads limited to four, and PyTorch GPU allocations capped at 75% of physical VRAM. A watchdog enforces host/GPU headroom; it stops this task rather than changing its scientific configuration.

Frozen recipe: 4-bit NF4, double quantization, BF16 compute; standard PEFT preparation (including its FP32 nonquantized parameters), non-reentrant gradient checkpointing; LoRA r=16, alpha=32, dropout=0, bias=none, all-linear (seven projections in each of 40 layers, excluding the output head); microbatch 1, accumulation 8, context 1536. All base parameters and quantization states are fingerprinted after preparation, before learning, and after learning. Only adapter parameters may require gradients. The original HF shards are independently SHA256-verified and retained outside Git.

One training recipe only: two complete passes, deterministic epoch shuffles, AdamW learning rate 0.0001, betas (0.9,0.999), epsilon 1e-8, weight decay 0.01, foreach=False; ceiling(5% of update count) linear warmup followed by linear decay to zero; gradient clipping 1.0. Versioned complete recovery checkpoints every 50 updates and at epoch boundaries preserve the adapter, optimizer, RNG, data hash and diagnostics. A resource interruption may resume the same fixed trajectory from the latest fully hashed checkpoint; incomplete checkpoints are not admissible, and recovery is reported. Final adapter is the candidate; no early stopping or validation-based recipe search. Validation loss before training and after each epoch is diagnostic only. Cycle 2 uses the same recipe and continues M1's adapter, with a fresh adapter-only optimizer. No reward model, RL, critic or self-scoring.

Seed 20260930, fixed in `runtime.py`; deterministic greedy inference (`do_sample=False`), native `enable_thinking=False`, 96 new tokens, left padding, batch 4, SDPA, no context truncation. TF32 disabled. Hardware kernels may have residual nondeterminism; no cross-run bitwise determinism claim is made. M0 is this prepared HF/NF4 base with adapters disabled; the zero initial adapter is checked against disabled inference synthetically. M1/M2 differ only by the adapter parameters. No scientific retries to repair output, prompt edits, changed decoding, or accuracy-conditioned changes are allowed. Schema mechanism is explicit prompt instructions plus strict JSON parsing, without grammar forcing or repair. Duplicate keys, extra keys, invalid values or extra text fail schema and joint correctness.

## Preserved semantics and fresh experience

The exact scope and output definitions are imported from the immutable temporal-state study. Current refers only to the explicitly deployed trial. Prior is YES if some older trial is determinately violating; NO if all are determinately compliant; otherwise UNKNOWN. Separate provenance contradictions do not change resolved trial truths. No five-class ontology is included.

Six coherent primitive trial types cross reference match/mismatch with known determinate input, unknown but determinate input, and unknown underdetermined input. Each generated case has a finite admissible-input witness. An independent truth-set evaluator checks all possible current outcomes and propagates existential prior truth across admissible worlds. Gold never comes from a model.

Before any M0 scientific call, generate and freeze BOTH cycles and all possible admitted neighbors:

| Pool | Count | Prior counts | Purpose |
|---|---:|---|---|
| H1 | 1980 | 2–7 | M0 mistake harvest |
| V1 | 360 | 2–7 | Diagnostic validation loss |
| T1 | 540 | 8–9 | Sealed first test |
| R1 | 360 | 1–7 | Regression |
| H2 | 1980 | 10–12 | Conditional M1 mistake harvest |
| V2 | 360 | 10–12 | Diagnostic validation loss |
| T2 | 540 | 13–15 | Sealed second test |
| R2 | 360 | 10–12 | Regression |

Each T set contains 60 cases for each of the nine joint outputs. Each H set has 660 per current label, with prior NO/YES/UNKNOWN counts 24/318/318 within each current label. Each V set uses 8/56/56. This deliberate nonuniform harvest preserves fresh unique all-compliant states for regression rather than counting repeated decorative variants as fresh experience. R contains 60 NO/NO, 60 YES/NO, 120 NO/YES and 120 YES/YES. R1 includes the available selected single-prior cases; it does not claim a large single-prior sample. Complete realized distributions are in the data manifest.

The generator enumerates semantic multisets, chooses by fixed seeded order, and allocates R then V then H without replacement. It excludes the earlier published primitive/state projections (read only input state objects, never predictions or historical gold). Tests reserve entirely different prior-count ranges across both cycles. Test order places uncertain trials at the boundaries and reverses determinate order; other pools use a deterministic shuffle. Thus held-out combinations of length, positions, current/prior interactions and package values are prospective, not selected from model failures. The generator and concrete materialization are frozen. Sealing means no model test calls, scoring, training use or outcome-responsive selection until the relevant learned adapter is frozen; offline authoring and independent gold/coherence checks occur before M0.

Normalized identity removes IDs, wording, explanatory decorations and semantically irrelevant prior order. It retains the complete primitive multiset, its multiplicity and package consistency. T1/T2 must overlap neither each other nor any H/V/R/neighbor/training/replay state. A stricter trial-only, package-ignored overlap audit is also recorded. Abstract truth patterns and logical concepts necessarily recur. Repeated compliant trials can be logically redundant: this tests synthetic length/composition generalization, not discovery of new logic or broad real-task transfer.

## Mistake admission and training targets

Freeze all H1 raw endpoints in a Git-committed hash manifest BEFORE any H1 scoring. Preserve private exact messages, rendered prompts, final text and token IDs; publish strict parsed final JSON and raw hashes. E1 contains EVERY schema-invalid or joint-incorrect H1 endpoint.

D1 includes every E1 input with independently verified correct final JSON, and no previous wrong answer in its prompt. Prospective neighbors toggle exactly one reference relation, one coherent evidence-sufficiency field, or package consistency. Exclude reserved V/T/R and historical normalized states. For each H input, precompute at most two neighbors before inference: prefer a target-changing neighbor, then hash order. At admission, select neighbors only for errors and deduplicate their normalized states against admitted errors/neighbors in frozen pool order. Neighbors can coincide with another H case. Include exactly |E1| correct replay exposures, round-robin across nonempty joint-gold strata, seeded shuffle within strata, cycling with replacement as necessary. Publish exposures and unique counts separately. No manual rebalancing.

If no errors exist, an error-driven update is undefined; if no correct H endpoints exist, mandatory correct replay cannot be constructed. Either condition stops with the applicable cycle claim not established, preserving the observed harvest and explaining the reason; a cycle-2 admission stop preserves any first-cycle success. It does not authorize replacement data.

Supervised next-token cross entropy covers only correct final JSON plus EOS. Prompt tokens carry no loss; the model materializes logits only for target prediction positions. Initial and final adapter files, parameter fingerprints, optimizer state, actual examples/steps, full loss curve, gradient finiteness/norms and wall time are preserved. Base and NF4 quantization-state fingerprints must remain identical. Save/reload must preserve adapter tensors exactly. Adapter/optimizer binaries remain in immutable local research storage; their hashes, sizes, configuration and learning evidence are published. They are not deployed or pushed as Git binaries.

Freeze M1 artifact hashes in a commit BEFORE any T1 inference. Evaluate M0 and M1 with identical prompts, batching, runtime and parsing on T1 and R1. Freeze all evaluation raw outputs before scoring. No T1-dependent adjustment or additional learning is allowed.

## First hard gate

`ERROR_DRIVEN_PARAMETER_LEARNING_SUPPORTED` requires ALL:

1. T1 joint gain >=8 percentage points.
2. Two-sided exact McNemar p<0.01 (twice the Binomial(discordant,0.5) lower tail through the smaller discordance count, capped at 1; p=1 with no discordance).
3. >=10-point joint gain on the fixed target subset: current UNKNOWN, any underdetermined prior, OR multiple priors with mixed truth statuses.
4. M1 T1 schema validity >=99%.
5. No major R1 capability metric loses >3 points. Metrics: clear YES joint; clear NO joint; contradiction-independent joint; current-determinate current field; all-prior-determinate prior field; schema validity. Membership is determined entirely by input/gold, never baseline success. Their pretraining accuracy is reported; they are intended strength probes, not guaranteed strong in the new stack.
6. Noncollapsed T1 distribution: each of YES/NO/UNKNOWN occurs in at least 5% of all endpoints in EACH predicted field; invalid outputs do not count toward any label.
7. Adapter parameters changed.
8. Base parameters and quantization states unchanged.
9. Exact/normalized leakage audit passes.

Otherwise `ERROR_DRIVEN_PARAMETER_LEARNING_NOT_ESTABLISHED`: publish and STOP. All checks are conjunctive; a promising subset cannot override the gate.

## Conditional second cycle

Only a full first-gate pass authorizes M1 on already frozen H2. Freeze all outputs before scoring; E2 consists of M1's own joint errors. D2 follows the same all-error, frozen-neighbor and matched-count correct-replay rules, plus exactly 512 D1 exposures stratified by target with deterministic cycling. This contains no T1, T2, V or regression case. Continue M1's adapter, never reset to M0. Freeze M2 before any T2 inference.

Evaluate M1/M2 on T2; M2 on T1 retention and R1; M1/M2 on R2. Relevant regression incumbent is M1 for both R1 and R2. Reuse frozen M1 T1/R1 outputs from cycle 1. Freeze new raw outputs before scoring.

`TWO_CYCLE_ERROR_DRIVEN_LEARNING_SUPPORTED` requires T2 joint gain >=4 points; two-sided exact McNemar p<0.05; T1 loss <=2 absolute percentage points (the prospectively selected retention interpretation); no R1/R2 family metric loss >3 points versus M1; M2 schema >=99% on T2, T1 and R1/R2; adapter changes again; base remains frozen; leakage audit passes. Otherwise `SECOND_LEARNING_CYCLE_NOT_ESTABLISHED`. Preserve a successful first cycle even if the second fails. Publish both and stop.

## Interpretation and preservation

A pass establishes externally designed parameter-efficient supervised learning from verified mistakes on this bounded synthetic task. Two passes establish two-cycle error-driven parameter learning. Neither establishes RSI, autonomous learning, self-awareness or consciousness. Training loss is engineering evidence, never the competence gate. The prior Qwen2.5-0.5B experiment's recorded 540,672 trainable parameters and changed adapter hashes are preserved as historical precedent; no historical training examples are reused. Historical Dolphin/Mixtral remained inference-only; Memory-conditioned changes are not weight learning.

Future authorized integration could connect real experience → authenticated receipt → verified correction → training admission → candidate parameter update → sealed evaluation → reject or separately authorize promotion. Memory would provide evidence; gradients would change parameters. This study does not implement that integration.

RSI still requires useful real tasks, authenticated consequences, system-led diagnosis and bounded change proposals with prospective predictions, protected external authorization, implementation, sealed real-task validation, measured retention and repetition by the improved system. No later study, comparator, RL experiment, model substitution or prompt workaround is authorized here.
