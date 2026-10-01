# Horus Active Causal Experimentation v0

This prospective study compares frozen A0's own experiment choices with a fixed passive schedule. The authoritative registration is `prospective-design.json`. Qualification uses no scientific A0 responses. No parameters, incumbent policy, or prior studies are modified.

## Fixed reservations and sealing

Every machine has 84 reset probes over four opaque actuators: all sequences of lengths one, two and three. Five three-action probes are reserved before inference, one from each equality pattern AAA, AAB, ABA, ABB and ABC. Reservations exclude the fixed passive schedule. Active receives exactly the other 79 probes. Both arms are evaluated on the identical five reserved probes; replacement after execution is prohibited.

Length-one and length-two reservations cannot remain unobserved while all other 79 probes return their complete traces: a longer permitted sequence exposes its reserved prefix. Consequently, length balancing is infeasible under these requirements. All reservations use length three, with balanced repetition and order structures. This is a deliberately pattern-balanced evaluation, not a uniform sample of the 84-probe catalogue.

The abstract passive schedule is A, B, C, D, AB, BA, CD, DC, ABC, BCD, CDA, DAB. Actuator and sensor names are independently opaque. Discovery traces always start from reset; they are never concatenated into a continuous hidden-state trajectory.

## Dynamics and hypotheses

The new family combines Boolean interactions, negation, conditional selection, delays, latches and activation counters. Its synchronous semantics reuse the preserved simulator: toggle the chosen input; observe combinational values using the updated inputs and old registers; then update all registers simultaneously. Reset clears inputs and registers. Sensor roots have independent storage.

The frozen family has 576 root types, each represented by the lexicographically first normalized expression with that reset observation and those 84 probe traces. A complete machine is an ordered product of four roots. The evaluator maintains the exact product of root sets consistent with the public reset and every executed observation. Its uniform hypothesis prior is explicit; it is not an assertion that the qualified world generator is uniformly distributed over that family. Root factorization permits exact joint trace partitions, expected remaining counts, entropy reduction and worst-case counts without materializing billions of tuples. An independent small Cartesian enumeration verifies these calculations.

Neither the family, its hypotheses, hidden program, information scores, nor counts enter model-visible messages. The model worker receives only semantic messages built by the allowlisted interface. The offline oracle qualifies worlds; it never chooses Active's probe.

## Qualification

Each accepted world must leave at least two more bits of uncertainty under Passive than under twelve greedy oracle probes, restricted to the same 79 choices. The oracle's remaining hypotheses must agree on all five reserved traces. Every reserved trace must change internally, and all five full traces must be distinct.

These conditions make reset-state and arbitrary constant last-observation persistence exactly unsuccessful on all reserved endpoints. Any actuator-independent predictor returning the same position-specific trace across a world's five queries can match at most one, even if fitted with oracle access. Thus its exact ceiling is 20%, stricter than the registered 30% ceiling. The actual operational marginal baseline is fitted only to the corresponding executed discovery ledger.

The frozen populations contain 120 prediction machines and 40 separate control machines. Primary and control graphs are mutually distinct and disjoint from twelve engineering worlds and 3,440 preserved causal-study worlds under actuator and sensor renaming. Scientific seeds are 851703 and 851704; the control-planner seed is 851705. Engineering uses seed 715019.

## Runtime and validity

A0 is the exact pinned Qwen3-14B base with the successful temporal M1 adapter. Disk hashes and loaded base/adapter tensor fingerprints were verified. All parameters have gradients disabled. The preserved HF stack, tokenizer/template, NF4 quantization and greedy non-thinking decoding remain in use. Context is 4,096 tokens and maximum generation is 256 tokens; history is never truncated.

Synthetic prefill at batch four exceeded the existing 75% GPU memory cap. Batch one qualified successfully: seven synthetic schema requests passed, including the complete twelve-probe prediction ledger. Maximum synthetic prompt length across all 160 actual port sets is 1,794 tokens. No scientific calls influenced this adjustment. The runtime checks prompt length before each request.

Output validation is strict JSON, including duplicate-key rejection. There is no repair, retry, critic or constrained decoder. An invalid discovery selection terminates the campaign as a protocol failure; no fallback probe is substituted. An invalid prediction receives zero exact, bit and step credit. Registered gates are not weakened.

## Collection, scoring and control

Every model request intent, response and executed reset probe receives durable authenticated recording. Probe receipts bind world, arm, index, A0 identity, adapter, reset, chosen sequence, full observation trace and ledger hashes. The writer interoperates with the preserved Horus authentication verifier. Completed durable calls can be replayed without inference; an ambiguous interrupted call fails closed.

Collection computes no model-correctness or information metrics. All raw evidence must be hashed and its public manifest committed before either class of scientific scoring. Private model outputs, receipts, programs, keys and binary model artifacts remain outside Git. Subsequent scoring must require byte-identical zero-inference replay and audit actual prompt and receipt reconstruction.

The three separate gates and exact statistical conventions are frozen in `prospective-design.json`. Primary information advantage is the median paired difference in cumulative realized bits. The selection test is the one-sided exact paired sign test, with ties removed and p < .01. Probe ranking uses midranks over 79 choices; zero-information ties do not count as top-quartile selections. A zero Passive median regret cannot pass the 20% reduction criterion.

Control uses eight preselected three-action candidates per world, eight A0 predictions per arm, predicted final-state Hamming ranking, and at most four reset executions. Actual control observations do not change the frozen predictions or ranking. Both arms use the same target, candidates, metric, tie rule and budget. Report probe count and actuator count separately. Control success does not substitute for either evidence-acquisition gate.

Five prediction endpoints share each machine. The user-required endpoint McNemar test will be reported with this dependence limitation. Results apply to the qualified family, whose construction deliberately provides room for informative discovery. Comparative probe counts alone cannot establish the model's deliberateness.

## Freeze milestone

Method and World/Data Freeze commit identifiers are recorded separately. No scientific inference, training, publication, merge or promotion is part of this freeze milestone. Scientific results and the final publication handoff remain pending.
