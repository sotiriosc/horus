# Horus v0.5 grounded expert routing

Status: frozen before live inference.

V0.5 does not train or alter a model. It retains generation 2 as the global
ACTIVE model and generation 3 as globally REJECTED, while making both exact
artifacts eligible in a separate routing registry. Generation 3R is excluded.

## Separate adaptation layers

- **Memory** is the signed chronological record of authorized realized events.
- **Weights** are the unchanged generation-2 and generation-3 adapters.
- **Routing** is a signed record of which retained adapter controlled the
  consequence forecasts and how both frozen adapters scored against later
  receipts.

Routing eligibility never changes lifecycle status. A prediction is not
evidence of correctness. Only its later comparison with the matching authorized
original receipt may update the router.

## Frozen causal order

For all three legal actions, the existing joint next-state request and both
specialist consequence requests are durably committed before any response is
used. Both specialists consume the same permitted authenticated-history prompt.
Neither receives the other prediction, the router decision, predicted
next-state, simulator regime, law, or future outcome.

The runtime then follows this order:

```text
all joint and G2/G3 requests committed
→ all responses parsed and committed
→ router selects from prior receipt-scored evidence
→ mechanical Explorer selects an action
→ external execution
→ original receipt authorization and Memory publication
→ both frozen selected-action predictions scored
→ append-only router evidence update
→ any switch applies only to the next decision
```

Missing artifacts or lineage, artifact hash mismatch, corrupt router evidence,
receipt mismatch, absent pre-execution commitments, a late shadow prediction,
hidden-regime input, or unauthenticated scoring fails closed. Invalid component
output also prevents execution; it cannot silently remove a specialist.

## Frozen router

`horus/routing_policy.json` is authoritative. G2 is the cold-start specialist.
The router uses the most recent six shared authorized receipt-scored events.
It requires at least four events, and switches only when the challenger leads
the incumbent by at least two correct consequence predictions. Ties retain the
incumbent. The same hysteresis applies after every switch.

The live endurance analysis uses a rolling six-event accuracy window. A switch
is descriptively called unnecessary only if the former specialist exceeds the
new specialist by at least two correct predictions over the next four executed
events; fewer than four later events is reported as not assessable. This label
does not affect routing.

## Frozen A→B→A demonstration

The schedule is exactly 36 attempted decisions, with no retries, replacements,
or outcome-based extension:

| Phase | Hidden external regime | Attempts | Process boundary |
|---|---|---:|---|
| A1 | A | 12 | start |
| B | B | 12 | restart after B attempt 6 |
| A2 | A | 12 | restart and explicit B→A transition |

Each attempt issues exactly three existing joint next-state calls, three G2
consequence calls, and three G3 consequence calls: nine model calls and 324
scheduled calls overall. An invalid response may reduce executed receipts but
does not increase the attempt or call budget.

The simulator uses the unchanged v0.4 laws. At state 1, A gives `ADVANCE=-1`
and `HOLD=+1`; B gives `ADVANCE=+1` and `HOLD=-1`. Transitions and receipt
authority are unchanged. Regime is audit-only and absent from both model and
router inputs.

Always-G2 and always-G3 comparisons score their already-frozen predictions only
on the actions the routed system actually executed. They are not
counterfactual-action claims.

## Private operation

Initialize a self-contained routing registry from the checked-in v0.4 evidence:

```sh
python -m horus.learn init-routing \
  --source-registry research/learning-stability-v0/registry \
  --routing-registry /safe/private/horus-routing
```

Run a routed segment:

```sh
python -m horus.run --live \
  --consequence-model routed \
  --routing-registry /safe/private/horus-routing \
  --session /safe/private/horus-session \
  --steps 12 --external-regime A
```

Private routing authority keys, raw model-call streams, and session checkpoints
must remain outside the public repository. The public result may retain compact
receipt-linked evidence and aggregate metrics without those secrets.
