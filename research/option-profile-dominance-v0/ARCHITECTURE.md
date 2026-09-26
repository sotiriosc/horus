# Option-profile dominance

`OPTION_PROFILE` is the complete finite multiset of depth-2 consequence
trajectories available beneath one current action. Trajectories remain bound to
their second-action identities and preserve duplicates. They are sorted from
best to worst by the existing lexicographic consequence order; canonical action
order breaks display-order ties between identical sequences without changing
their value.

Profile X dominates profile Y only when the profiles have equal finite
cardinality, every ranked X trajectory is lexicographically no worse than the
corresponding Y trajectory, and at least one rank is strictly better. This is a
partial order. Equal or crossing profiles produce no selected action.

The representation produces no scalar, sum, average, weight, discount,
probability, diversity value, novelty value, or uncertainty value. It reads
only the committed v0.15 trajectory identities, consequence sequences, and
provenance. It makes zero model calls and has zero behavioral authority.

For PR-0002, a unique retrospective dominance result may request a separately
authorized `OPTION_PROFILE_BEHAVIORAL_INTEGRATION` step. This milestone does not
install the representation as the global Explorer objective or execute the
selected action.
