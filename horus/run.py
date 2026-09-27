"""Command-line entrypoint for reference v0 and live v0.1 sessions."""
import argparse
from pathlib import Path

from .core import run_demo


def render(artifact):
    for row in artifact["episodes"]:
        print(f"Episode {row['episode']}")
        print(f"State: {row['state']}")
        used = {action: len(history) for action, history in row["memory_used"].items()}
        print(f"Memory used: {used}")
        print("Map forecasts:")
        for forecast in row["map_forecasts"]:
            print(f"  {forecast['action']} -> next_state={forecast['next_state']}, "
                  f"consequence={forecast['consequence']}, history={forecast['history_count']}")
        print(f"Explorer chose: {row['explorer']['action']} ({row['explorer']['reason']})")
        receipt = row["receipt"]
        print(f"Realized receipt: next_state={receipt['next_state']}, "
              f"consequence={receipt['realized_consequence']}, event_id={receipt['event_id']}")
        print(f"Prediction match: {row['prediction_match']}")
        memory = row["memory_published"]
        print(f"Memory published: epoch={memory['epoch']}, tx={memory['transaction_id']}, "
              f"action={memory['action']}, consequence={memory['consequence']}")
        print()
    causal = artifact["causal_moment"]
    print(f"Grounded behavior change: {causal['earlier_action']} -> {causal['later_action']}")


def render_live(artifact):
    print(f"Horus live session: {artifact['session_id']}")
    print(f"Runtime {artifact['runtime_index']} / epoch {artifact['epoch']}")
    if artifact.get("active_model"):
        model = artifact["active_model"]
        print(f"Consequence model generation: {model['generation']}")
        print(f"Parent generation: {model['parent_generation']}")
        print(f"Artifact hash: {model['artifact_sha256']}")
    for row in artifact["steps"]:
        print(f"\nStep {row['step']}")
        print("Prior authenticated observations used: " +
              ", ".join(f"{key}={value}" for key, value in
                        row["prior_authenticated_observations_used"].items()))
        print("Map:")
        for forecast in row["map_forecasts"]:
            print(f"  {forecast['action']} -> next_state={forecast['next_state']}, "
                  f"consequence={forecast['consequence']}, "
                  f"history={forecast['history_count']}, "
                  f"abstained={forecast['abstained']}")
        print(f"Explorer chose: {row['explorer']['action']} "
              f"({row['explorer']['reason']})")
        if row["status"] == "ABSTAINED":
            print("Executed: no (Map abstained)")
            continue
        receipt = row["receipt"]
        print(f"Executed: {receipt['action']}")
        print(f"Original receipt: source={receipt['source_identity']}, "
              f"event={receipt['event_id']}, next_state={receipt['next_state']}, "
              f"consequence={receipt['realized_consequence']}")
        print(f"Prediction vs realization: {row['prediction_match']}")
        print(f"Memory publication: {row['memory_publication']}")
        print("Behavioral change attributable to prior experience: not established; "
              "the authenticated-history counts above show request-level use only")
    print(f"\nActual model calls this process: {artifact['actual_model_calls']}")
    print(f"Checkpoint: {Path(artifact['session']) / 'checkpoint.json'}")


def render_routed(artifact):
    print(f"Horus routed session: {artifact['session_id']}")
    print(f"Runtime {artifact['runtime_index']} / epoch {artifact['epoch']}")
    print("Consequence specialists:")
    for row in artifact["consequence_specialists"]:
        print(f"  {row['id']}: generation {row['generation']} "
              f"{row['artifact_sha256']} "
              f"(global={row['global_lifecycle_status']}, "
              f"routing={row['routing_eligibility']})")
    for row in artifact["steps"]:
        before = row["router_before"]
        print(f"\nAttempt {row['decision_id']}")
        print(f"Router selected: {row['selected_specialist']}")
        for specialist in ("G2", "G3"):
            score = before["scores"][specialist]
            print(f"  recent {specialist}: {score['correct']}/{score['total']}")
        print("Specialist forecasts:")
        for specialist in ("G2", "G3"):
            values = ", ".join(
                f"{item['action']}={item['consequence']}"
                for item in row["specialist_forecasts"][specialist])
            print(f"  {specialist}: {values}")
        print(f"Explorer: {row['explorer']['action']} ({row['explorer']['reason']})")
        if row["status"] == "ABSTAINED":
            print("Executed: no (routed component set failed closed)")
            continue
        receipt = row["receipt"]
        print(f"Receipt: consequence={receipt['realized_consequence']}, "
              f"identity={[receipt['source_identity'], receipt['event_id'], receipt['epoch'], receipt['transaction_id']]}")
        print("Shadow scoring:")
        for specialist in ("G2", "G3"):
            score = row["shadow_scoring"][specialist]
            print(f"  {specialist} predicted {score['predicted']} -> "
                  f"{'correct' if score['correct'] else 'wrong'}")
        route = row["routing_evidence"]
        if route["switch_occurred"]:
            print("ROUTER SWITCH")
            print(f"{route['selected_specialist']} -> "
                  f"{route['selected_specialist_after']}")
            print(f"reason: {route['switch_reason']}")
    final = artifact["router_final"]
    print(f"\nFinal router selection: {final['selected_specialist']}")
    print(f"Actual model calls this process: {artifact['actual_model_calls']}")
    print(f"Checkpoint: {Path(artifact['session']) / 'checkpoint.json'}")


def render_relation_routed(artifact):
    print(f"Horus relation-routed session: {artifact['session_id']}")
    print(f"Segment {artifact['segment']} / runtime {artifact['runtime_index']} / "
          f"epoch {artifact['epoch']}")
    for row in artifact["rows"]:
        print(f"\nPrediction batch {row['prediction_batch_sequence']}: "
              f"{row['execution_kind']}")
        print("Relation selections: " + ", ".join(
            f"{action}={specialist}" for action, specialist in
            row["relation_selections_before"].items()))
        print("Explorer comparisons: " + ", ".join(
            f"{name}={choice['action']}" for name, choice in row["choices"].items()))
        if row.get("status") == "ABSTAINED":
            print("Executed: no (relation-routed component set failed closed)")
        elif row["execution_kind"] == "COMPARISON_ONLY_NO_EXECUTION":
            print("Executed: no (frozen comparison-only path)")
        else:
            receipt = row["receipt"]
            print(f"Executed: {receipt['action']} ({row['action_source']})")
            print(f"Receipt: consequence={receipt['realized_consequence']}, "
                  f"identity={[receipt['source_identity'], receipt['event_id'], receipt['epoch'], receipt['transaction_id']]}")
            route = row["routing_evidence"]
            if route["switch_occurred"]:
                relation = route["relation"]
                print(f"RELATION ROUTER SWITCH ({relation['pre_state']}, "
                      f"{relation['action']}): {route['selected_specialist']} -> "
                      f"{route['selected_specialist_after']}")
                print(f"reason: {route['switch_reason']}")
    target = artifact["target_relation"]
    print(f"\nTarget relation selected: {target['selected_specialist']}")
    print(f"Target local scores: {target['scores']}")
    print(f"Actual model calls this process: {artifact['actual_model_calls']}")
    print(f"Checkpoint: {Path(artifact['session']) / 'checkpoint.json'}")


def render_grounded_exploration(artifact):
    print(f"Horus grounded-exploration session: {artifact['session_id']}")
    print(f"Segment {artifact['segment']} / runtime {artifact['runtime_index']} / "
          f"epoch {artifact['epoch']}")
    for row in artifact["rows"]:
        explorer = row["explorer"]
        print(f"\nDecision {row['prediction_batch_sequence']}")
        print(f"State: {row['pre_state'] if 'pre_state' in row else row['state']}")
        for action, confidence in explorer["relation_confidence"].items():
            forecasts = row["forecasts"][action]
            print(f"Relation {action}: specialist={confidence['selected_specialist']} "
                  f"G2={forecasts['G2_consequence']} "
                  f"G3={forecasts['G3_consequence']} "
                  f"observations={confidence['authenticated_observations']} "
                  f"status={','.join(confidence['qualifying_probe_reasons']) or 'GROUNDED'}")
        print(f"Explorer: mode={explorer['mode']} action={explorer['action']} "
              f"reason={explorer['reason']}")
        if row["status"] == "ABSTAINED":
            print("Executed: no (invalid or tied component set failed closed)")
            continue
        if row["status"] == "FRAMEWORK_REJECTED":
            problem = row["problem"]
            print("Executed: no (protected framework rejected begin_step)")
            print(f"Problem: {problem['type']} / {problem['observed_constraint']}")
            continue
        print(f"Receipt: {row['receipt']['action']} -> "
              f"{row['receipt']['realized_consequence']}")
        print("Memory: published")
        route = row["routing_evidence"]
        score = route["router_score_after"]
        print(f"Relation router: G2={score['G2']['correct']}/{score['G2']['total']} "
              f"G3={score['G3']['correct']}/{score['G3']['total']}")
        if route["switch_occurred"]:
            print(f"SWITCH {route['selected_specialist']} -> "
                  f"{route['selected_specialist_after']}")
    print(f"\nActual model calls this process: {artifact['actual_model_calls']}")
    print(f"Checkpoint: {Path(artifact['session']) / 'checkpoint.json'}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the bounded Horus v0 closed loop")
    parser.add_argument("--output", type=Path, default=Path("horus-v0-run.json"))
    parser.add_argument("--live", action="store_true",
                        help="use real model predictors and durable session state")
    parser.add_argument("--steps", type=int, default=1)
    parser.add_argument("--session", type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--consequence-model",
                        choices=("mixtral", "base", "trained", "active", "routed",
                                 "relation-routed", "grounded-exploration",
                                 "problem-route"),
                        default="mixtral")
    parser.add_argument("--trained-adapter", type=Path)
    parser.add_argument("--model-registry", type=Path)
    parser.add_argument("--routing-registry", type=Path)
    parser.add_argument("--relation-segment", choices=("A1", "B1", "B2", "A2"))
    parser.add_argument("--exploration-segment", choices=(
        "A1", "B1", "B2", "A2", "R2_A1_1", "R2_A1_2", "R2_B1",
        "R2_B2", "R2_A2_1", "R2_A2_2", "V08_A1_1", "V08_A1_2",
        "V08_B1", "V08_B2", "V08_A2_1", "V08_A2_2"))
    parser.add_argument("--consequence-base-model", type=Path,
                        help="optional local directory for the pinned Qwen base snapshot")
    parser.add_argument("--external-regime", choices=("A", "B"), default="A",
                        help="external audit regime; never added to model input")
    parser.add_argument("--transition-regime", action="store_true",
                        help="authorize one prospective registered A/B transition")
    args = parser.parse_args(argv)
    if args.live:
        if args.session is None:
            parser.error("--live requires --session")
        if args.resume and not args.live:
            parser.error("--resume requires --live")
        from .live import run_live
        consequence_client = None
        active_spec = None
        if args.consequence_model == "problem-route":
            if args.routing_registry is None or args.exploration_segment is None:
                parser.error("problem-route requires --routing-registry and --exploration-segment")
            from .problem_routing import run_problem_route_segment
            artifact = run_problem_route_segment(args.session,
                args.routing_registry, args.exploration_segment, args.resume)
            render_grounded_exploration(artifact)
            return
        if args.consequence_model == "grounded-exploration":
            if args.routing_registry is None or args.exploration_segment is None:
                parser.error("grounded-exploration requires --routing-registry and --exploration-segment")
            from .grounded_exploration import run_grounded_exploration_segment
            runtime_schedule = ("R2" if
                args.exploration_segment.startswith("R2_") else "V0")
            artifact = run_grounded_exploration_segment(args.session,
                args.routing_registry, args.exploration_segment, args.resume,
                runtime_schedule=runtime_schedule)
            render_grounded_exploration(artifact)
            return
        if args.consequence_model == "relation-routed":
            if args.routing_registry is None or args.relation_segment is None:
                parser.error("relation-routed requires --routing-registry and --relation-segment")
            from .relation_routing import run_relation_segment
            artifact = run_relation_segment(args.session, args.routing_registry,
                args.relation_segment, args.resume)
            render_relation_routed(artifact)
            return
        if args.consequence_model == "routed":
            if args.routing_registry is None:
                parser.error("--consequence-model routed requires --routing-registry")
            from .routing import run_routed
            artifact = run_routed(args.session, args.routing_registry, args.steps,
                args.resume, args.external_regime, args.transition_regime)
            render_routed(artifact)
            return
        if args.consequence_model == "active":
            if args.model_registry is None:
                parser.error("--consequence-model active requires --model-registry")
            from .learning_cycle import active_client
            consequence_client, active_spec = active_client(args.model_registry)
        elif args.consequence_model != "mixtral":
            from .grounded_learning import QwenConsequenceClient, default_adapter_path
            adapter = None
            if args.consequence_model == "trained":
                adapter = args.trained_adapter or default_adapter_path()
                if not adapter.exists():
                    parser.error(f"trained adapter does not exist: {adapter}")
            consequence_client = QwenConsequenceClient(
                adapter_path=adapter, model_path=args.consequence_base_model)
        artifact = run_live(args.session, args.steps, args.resume,
                            consequence_client=consequence_client,
                            regime_version=args.external_regime,
                            allow_regime_transition=args.transition_regime)
        if active_spec is not None:
            artifact["active_model"] = active_spec
        render_live(artifact)
        return
    if args.resume or args.session is not None:
        parser.error("--resume/--session require --live")
    artifact = run_demo(args.output)
    render(artifact)
    print(f"Machine-readable artifact: {args.output}")


if __name__ == "__main__":
    main()
