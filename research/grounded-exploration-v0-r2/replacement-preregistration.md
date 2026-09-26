# Horus v0.7 grounded exploration R2 replacement preregistration

## Identity and lineage

- Campaign identity: `HORUS_GROUNDED_EXPLORATION_V0_R2`
- Original frozen implementation: `72cdc095b9e35fb58e1bc353f1eae5de6c8aad39`
- Original external-service failure: `5edc8894fb47709d8c40dd8f3eb2f6c968dfa173`
- Preserved R1 failure: `d5620234f3523d45ae7a443593f82ce8874c025c`
- R2 repair commit: `a460bd9106dc1c80885b50f8d6e07c3a6f190de6`

R1 remains `NOT ESTABLISHED — incomplete campaign after protected
episode-bound exhaustion`. Its evidence is not resumed, rewritten, or used as
R2 behavioral evidence.

R2 changes only the protected-runtime schedule and adds defensive handling for
the legitimate `PendingTransaction | StepResult` result of `begin_step`. The
scientific exploration policy, model artifacts, prompts, scoring, phase
definitions, decision count, interpretation, and stopping rule are unchanged.

## Registered runtime schedule

| Segment | Decision attempts | Regime | Resume | Prior runtime count |
|---|---:|---|---|---:|
| `R2_A1_1` | 1–9 | A | no | 0 |
| `R2_A1_2` | 10–18 | A | yes | 1 |
| `R2_B1` | 19–27 | B | yes, transition | 2 |
| `R2_B2` | 28–36 | B | yes | 3 |
| `R2_A2_1` | 37–45 | A | yes, transition | 4 |
| `R2_A2_2` | 46–54 | A | yes | 5 |

Each runtime has exactly nine decision attempts and can execute at most nine
times. Rollover follows only this table and cannot depend on outcomes,
predictions, probe/exploit status, abstentions, routing, or discovered regime
information. The protected `EPISODE_LIMIT=12` remains unchanged.

## Frozen campaign

- 54 autonomous decision attempts.
- Nine calls per decision: three joint next-state, three G2 consequence, and
  three G3 consequence calls.
- Maximum and expected behavioral calls: 486.
- No forced calibration action.
- No extension, replacement decision, or added retry.
- External regimes remain A for decisions 1–18, B for 19–36, and A for 37–54.
- A rejected `StepResult` completes the frozen decision as a fail-closed
  framework rejection and creates no execution, receipt, Memory, or routing
  evidence.
- An `INTERNAL_ROUTE_PROBLEM` is observational and non-authoritative.

## Frozen hashes

- R2 implementation tree: `974d388a9524286aba01b2299b1dd1648135cfe1`
- `grounded_exploration.py`: `d539807a19fd5d83e4f8d00d0dd535e4dbafdea20337677c3610c0a3453da4d0`
- Exploration policy: `f6f963403a6ffaa827069288df49340035a4f9a7556d7111de9ba426382db7b3`
- Joint system instruction: `805542ebed5d2fa09b9b36f4895bdbd917b5d2af58db56d744478887a824b3e7`
- Consequence system instruction: `9fa97c24f33f7e25497bce9bb23a70cea52f91f6e02a3a01bd8e2d571ea37df8`
- G2 artifact: `effb5eebef0649818c0697f1dfbadc73bc9e047eb1eaf6e3d5f6c63e0a35d39a`
- G3 artifact: `edb9f6ff90dff7af75ece168825f04839ab720dc8a79ce166225a5ffcc1efb24`

## Stopping rule

If a new runtime, code, or infrastructure defect interrupts R2, preserve it and
stop. Do not patch or resume R2, and do not start R3 without new explicit
authorization. Behavioral under-exploration, over-exploration, or failed
adaptation are results and do not authorize an extension.
