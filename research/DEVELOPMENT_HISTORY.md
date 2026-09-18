# Public development sequence

This repository preserves the order in which the public Horus work developed.
The sequence matters because later experiments must not be read back into the
capabilities of the original hardware baseline.

1. The Horus baseline established reduced-precision arithmetic, normalization,
   scale tracking, local detection, repair/replay experiments, reference models,
   and their public regression suite.
2. The hardware-to-framework analysis found useful local Measure, Memory, and
   Recovery primitives, but no independent authority separating a repair
   proposal from permission to continue downstream.
3. `docs/NEXT_EXPERIMENT.md` proposed a bounded protected-source experiment to
   test that missing primitive.
4. The experiment was implemented later under
   `experiments/bounded_commit/`, around the unchanged public repair wrapper.
5. The declared protected-source campaign passed: 4,200 transactions, zero
   false accepts, zero false rejects, and zero duplicate accepts.
6. A deliberately correlated checker using descendant evidence falsely
   accepted 300 corrupted proposals. It remains a negative control and is not
   connected to the protected sink.
7. A follow-up tested 2,700 transactions across broader sign, mantissa,
   exponent, and multi-lane patterns. Unsupported patterns were rejected
   rather than described as repaired.
8. A cost, trace, and provenance follow-up measured standalone synthesis
   probes, verified lossless trace packing from 96 to 63 bits, and documented
   the assumptions under which the local provenance tuple is sufficient.
9. Base framework v0 froze five-component contracts and falsification criteria,
   then implemented the smallest bounded software loop connecting Explorer,
   Map, Measure, Memory, and Recovery.
10. Its 42 clean/failure scenario runs passed under the declared trust model;
    the prior RTL source and measured result files remained unchanged.

The Git history mirrors this sequence: baseline, public research context,
experiment implementation, measured results and reproduction guidance, then
the separately pre-registered software base framework.
The original private research repository and its history are not part of this
repository.
