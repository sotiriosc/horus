# Scale tracking: public behavior and limits

`rtl/skpr.v` and `sim/scale_keeper_golden.py` implement a local estimator of the block's maximum stored exponent. This document describes the visible implementation and its tests; it is not a broader recovery architecture.

The state uses an unsigned 14-bit Q6.8 representation. Tested defaults are a shift by four for the integrator, persistence count four, and settling count four. The reference calibration uses 64 samples and the 95th-percentile deviation statistics. These defaults and arithmetic remain unchanged.

A valid observation is compared with the previous state and guarded ceiling. A sustained deviation can reseed the estimate; isolated observations above the ceiling can be excluded from the update. Tags distinguish nominal, outlier, settling, and reseeded conditions. The reported state exponent reflects the updated state; the ceiling output is computed from the prior state. Reset clears state; it does not restore a remembered known-good checkpoint.

The six directed streams, random determinism check, and RTL co-simulation in `sim/test_scale_keeper.py` verify the specified implementation. Run `make skpr_sim` from the root, or `make -C sim skpr_sim`. No document outside this candidate is needed at runtime.

Tags are local classifications, not calibrated claims about truth or safety. The tracker does not authenticate observations, store causal lineage, or validate a correction against independent evidence. Its persistent state can alter subsequent tags and reseeding decisions; that does not establish a self-improving policy.
