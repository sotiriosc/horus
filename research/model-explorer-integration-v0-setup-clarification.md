# Setup description correction before matched trials

The original preregistration at `3b471a0` is preserved unchanged. While the
preregistered rollout campaign was running, inspection of the five deterministic
setup steps showed an incorrect descriptive sentence in that document:
the setup does **not** contain an observed HOLD=+1 record.

The five actual setup actions are ADVANCE. They end at state 1, Map version 5,
transaction 6. Relevant authorized Memory contains ADVANCE=-1; HOLD and RETREAT
are untried. Both untried actions have score zero under the preregistered
empirical-score convention. The sixth deterministic step would choose HOLD,
but it is not part of the registered five-step setup.

This correction was recorded after initial rollout outcomes were available
and **before any matched-pair model call**. It changes no runtime code, fixture,
call count, model input rule, seed, action, success threshold, or analysis rule.
The original six pairs and at-least-four strict empirical-score improvements
remain the behavioral criterion. No extra setup step or trial is introduced.

Interpretation is correspondingly narrow: a positive paired result supports
avoidance of a previously verified negative action, compared with an untried
action assigned neutral score. It cannot establish preference for an alternative
already demonstrated positive by this paired fixture. This setup-description
error must remain visible in the result report; it is neither a framework fault
nor permission to relabel unobserved outcomes as evidence.
