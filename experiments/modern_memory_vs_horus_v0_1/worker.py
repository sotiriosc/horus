from __future__ import annotations

from argparse import ArgumentParser
import json
import time
from horus.live import _atomic_write
from .atomic import prepare, commit_pair, publish_snapshot, verify_pair, flush
from pathlib import Path

from horus.live import SessionStore
from horus.relation_routing import RelationEvidenceStore

from .harness import (empty_explorer_state, forecast_batch, load_clients,
                      new_controller, publish)
from .protocol import CONDITIONS, STAGE_A, STAGE_B_DECISIONS
from .storage import ModernMemory, file_hash


def _checkpoint(root: Path, store: SessionStore, memory: ModernMemory,
                routing: RelationEvidenceStore | None) -> dict:
    session = {}
    for name in ("authority.key", "checkpoint.json", "events.jsonl",
                 "model-calls.private.jsonl", "training-records.jsonl"):
        session[name] = file_hash(root / "session" / name)
    routed = None
    if routing is not None:
        routed = dict(router_state_sha256=file_hash(root / "registry/router-state.json"),
            routing_evidence_sha256=file_hash(root / "registry/routing-evidence.jsonl"),
            routing_registry_sha256=file_hash(root / "registry/routing-registry.json"))
    return dict(session_files_sha256=session, memory=memory.checkpoint(),
        routing=routed, current_state=store.checkpoint["current_state"],
        events=len(store.records["events"]), calls=len(store.records["calls"]),
        training=len(store.records["training"]))


def _open(output: Path, condition: str):
    root = output / "work" / condition
    store = SessionStore(root / "session", True)
    memory = ModernMemory(root / "memory.sqlite3", False)
    routing = RelationEvidenceStore(root / "registry") if condition == "MH" else None
    if routing is not None: routing.bind_session(store)
    state_path = root / "explorer-state.json"
    explorer = json.loads(state_path.read_text()) if state_path.exists() else empty_explorer_state()
    joint, specialists, _ = load_clients(condition, root / "registry" if condition == "MH" else None)
    return root, store, memory, routing, explorer, joint, specialists


def _close(root, store, memory, routing, explorer):
    (root / "explorer-state.json").write_text(json.dumps(explorer, indent=2, sort_keys=True) + "\n")
    if routing is not None: routing.close()
    memory.close(); store.close()


def run_stage(output: Path, stage: str) -> dict:
    started = time.perf_counter()
    contexts = {condition: _open(output, condition) for condition in CONDITIONS}
    try:
        restart_verification = None
        if stage == "A1":
            publish_snapshot(output, contexts, "initial", 0)
            schedule = STAGE_A[:6]
        elif stage == "A2":
            schedule = STAGE_A[6:]
            expected = json.loads((output / "before-restart.json").read_text())
            observed = {condition: _checkpoint(*contexts[condition][:4])
                        for condition in CONDITIONS}
            if observed != expected["conditions"]:
                raise RuntimeError("fresh-process restart hash mismatch")
            verify_pair(contexts, 6)
            restart_verification = dict(status="PASS", exact_hash_match=True,
                                        conditions=observed)
            perturb_rows = {}
            for condition in CONDITIONS:
                root, store, memory, routing, explorer, joint, specialists = contexts[condition]
                controller = new_controller(store, "B")
                batch = prepare(contexts[condition], controller, "A:PERTURBATION",
                                forecast_batch, perturb=True)
                if batch["all_valid"] or not batch["decision"]["abstained"]:
                    raise RuntimeError("registered malformed response did not fail closed")
                record = dict(condition=condition, stage="A",
                    opportunity="REGISTERED_PERTURBATION", status="ABSTAINED",
                    execution_occurred=False, receipt_created=False,
                    memory_mutated=False, strict_parser_rejection=True,
                    operational_recovery="PENDING_NEXT_VALID_DECISION",
                    decision=batch["decision"], model_calls=batch["model_calls"],
                    context_tokens=batch["context_tokens"],
                    model_seconds=batch["model_seconds"])
                store.append("training", "REGISTERED_PARSER_PERTURBATION", record)
                store.save(state=store.checkpoint["current_state"],
                           next_transaction_id=store.checkpoint["next_transaction_id"],
                           attempted_decision=True)
                perturb_rows[condition] = record
            for condition in CONDITIONS:
                store = contexts[condition][1]
                bad = [e['record'] for e in store.records['calls']
                    if e['kind'] == 'PARSED' and e['record']['call_id'].startswith('A:PERTURBATION:')
                    and e['record']['parse_error'] is not None
                    and not (e['record']['call_id'].endswith(':HOLD:J')
                             and e['record']['outcome'] == 'MODEL_OUTPUT_INVALID')]
                if bad:
                    _atomic_write(output / 'stop.json', dict(status='PAIR_PREPARATION_FAILED',
                        opportunity='A:PERTURBATION', failures=bad))
                    publish_snapshot(output, contexts, 'failed-perturbation', 6)
                    raise RuntimeError('PAIR_PREPARATION_FAILED')
            (output / "perturbation.json").write_text(json.dumps(
                perturb_rows, indent=2, sort_keys=True) + "\n")
        elif stage == "B":
            verify_pair(contexts, 12)
            if not (output / 'stage-a2.json').exists():
                raise RuntimeError('Stage B requires completed valid Stage A')
            schedule = ()
        else:
            raise RuntimeError("unknown worker stage")

        rows = []
        controllers = {}
        for spec in schedule:
            batches, event_controllers = {}, {}
            for condition in CONDITIONS:
                root, store, memory, routing, explorer, joint, specialists = contexts[condition]
                key = (condition, spec["regime"])
                if key not in controllers:
                    controllers[key] = new_controller(store, spec["regime"])
                event_controllers[condition] = controllers[key]
                batches[condition] = prepare(contexts[condition], controllers[key],
                    f'A:{spec["event"]:02d}', forecast_batch)
            if not all(batch["all_valid"] for batch in batches.values()):
                failure = dict(status="PAIR_PREPARATION_FAILED", event=spec["event"],
                    matched=verify_pair(contexts, spec["event"] - 1),
                    readiness={arm: b["all_valid"] for arm, b in batches.items()})
                _atomic_write(output / "stop.json", failure)
                publish_snapshot(output, contexts, f'failed-{spec["event"]:02d}', spec["event"] - 1)
                raise RuntimeError("PAIR_PREPARATION_FAILED")
            event_rows = commit_pair(contexts, event_controllers, batches, spec, publish)
            publish_snapshot(output, contexts, f'event-{spec["event"]:02d}', spec["event"])
            rows.append(event_rows)
            print(f"stage={stage} event={spec['event']}/12", flush=True)

        if stage == "B":
            controllers = {condition: new_controller(contexts[condition][1], "A")
                           for condition in CONDITIONS}
            for decision_number in range(1, STAGE_B_DECISIONS + 1):
                paired = {}
                order = CONDITIONS if decision_number % 2 else tuple(reversed(CONDITIONS))
                for condition in order:
                    root, store, memory, routing, explorer, joint, specialists = contexts[condition]
                    batch = forecast_batch(condition=condition, store=store, memory=memory,
                        controller=controllers[condition], joint_client=joint,
                        specialists=specialists, routing_store=routing,
                        explorer_state=explorer, opportunity=f"B:{decision_number:02d}")
                    action = batch["decision"]["action"]
                    if not batch["all_valid"] or batch["decision"]["abstained"] or action is None:
                        record = dict(condition=condition, stage="B", event=decision_number,
                            status="ABSTAINED", decision=batch["decision"],
                            model_calls=batch["model_calls"], context_tokens=batch["context_tokens"],
                            model_seconds=batch["model_seconds"], execution_occurred=False)
                        store.append("training", "AUTONOMOUS_ABSTENTION", record)
                        store.save(state=store.checkpoint["current_state"],
                                   next_transaction_id=store.checkpoint["next_transaction_id"],
                                   attempted_decision=True)
                        explorer["attempted_decisions"] += int(condition == "MH")
                        paired[condition] = record
                    else:
                        paired[condition] = publish(condition=condition, stage="B",
                            event_number=decision_number, controller=controllers[condition],
                            store=store, memory=memory, batch=batch, action=action,
                            routing_store=routing, explorer_state=explorer)
                rows.append(paired)
                print(f"stage=B decision={decision_number}/{STAGE_B_DECISIONS}", flush=True)

        publish_snapshot(output, contexts, f"checkpoint-{stage}", 6 if stage == "A1" else 12)
        checkpoints = {condition: _checkpoint(*contexts[condition][:4])
                       for condition in CONDITIONS}
        result = dict(stage=stage, conditions=checkpoints, rows=rows,
                      restart_verification=restart_verification, wall_seconds=time.perf_counter() - started)
        name = "before-restart.json" if stage == "A1" else f"stage-{stage.lower()}.json"
        (output / name).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        return result
    except Exception as exc:
        for context in contexts.values(): flush(context[1])
        if not (output / 'stop.json').exists():
            _atomic_write(output / 'stop.json', dict(status='INVALID', error=repr(exc), stage=stage))
        raise
    finally:
        for context in contexts.values():
            _close(context[0], context[1], context[2], context[3], context[4])


if __name__ == "__main__":
    parser = ArgumentParser(); parser.add_argument("stage", choices=("A1", "A2", "B"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_stage(args.output, args.stage)
    print(json.dumps(dict(stage=args.stage, status="COMPLETE", wall_seconds=result["wall_seconds"]), sort_keys=True))
