from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.realized_event_grounding_v0.framework import evidence
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
from horus.live import LiveController, SessionStore

from .harness import EVENTS, publish_event
from .storage import DurableMemory, file_hash


ROOT = Path(__file__).resolve().parents[2]


def verify_sources() -> bool:
    manifest = json.loads((ROOT / "research/zakhor-durable-memory-trial-v0/source-manifest.json").read_text())
    for group in ("protected_framework_sources", "trial_sources"):
        for relative, expected in manifest[group].items():
            if file_hash(ROOT / relative) != expected:
                raise RuntimeError(f"frozen source mismatch: {relative}")
    adapter = ROOT / manifest["model"]["adapter"]
    if file_hash(adapter) != manifest["model"]["adapter_sha256"]:
        raise RuntimeError("frozen model artifact mismatch")
    return True


def fake_predictions() -> dict:
    retrieval = dict(selected_memory_identities=[], contradictions_in_candidates=False,
                     contradictions_excluded=False)
    return {name: dict(call_id=f"preflight:{name}", condition=name, event_number=1,
        prediction=1, parse_error=None, retrieval=retrieval, prompt_sha256="preflight",
        context_tokens=0, retrieval_seconds=0.0, model_seconds=0.0)
        for name in ("M", "Z")}


def main() -> dict:
    checks = {"frozen_sources_verified": verify_sources()}
    # Equal-valued receipt substitution cannot pass object-identity authority.
    forged_controller = LiveController("PREFLIGHT:FORGED", 1, 9001, "A")
    forged_controller.begin_step("HOLD")
    original = forged_controller.execute_pending()
    before = list(forged_controller._active.framework.inner.memory.records)
    rejected = forged_controller.submit_package(evidence(replace(original)))
    checks["forged_equal_value_receipt_rejected"] = (
        not rejected.committed and before ==
        forged_controller._active.framework.inner.memory.records)
    forged_controller.release(original)

    # Failed external execution creates no receipt and cannot enter Memory.
    class FailingWorld:
        def execute(self, *_): raise RuntimeError("registered failure")
    source = ExternalExecutionBoundary(FailingWorld(), "PREFLIGHT:FAILED")
    framework = StatusBoundFramework(source.reader(), 1, 9002)
    framework.begin_step(forced_action="HOLD")
    failed = False
    try:
        source.execute(9002, 1, "HOLD")
    except RuntimeError:
        failed = True
    checks["failed_execution_no_receipt_or_memory"] = (
        failed and source.reader().current() is None and
        not framework.inner.memory.records and not framework.packages)

    with TemporaryDirectory() as directory:
        root = Path(directory)
        session_path, database_path = root / "session", root / "memory.sqlite3"
        with SessionStore(session_path, False) as store, \
                DurableMemory(database_path, True) as memory:
            store.configure_regime("A")
            epoch, identity = store.begin_runtime()
            controller = LiveController(identity, 1, epoch, "A")
            store.append("calls", "PREFLIGHT_REQUEST", {"call_id": "zero-inference"})
            store.append("calls", "PREFLIGHT_RESPONSE", {"call_id": "zero-inference"})
            row = publish_event(store, memory, controller, EVENTS[0], fake_predictions())
            checks["original_receipt_identity_retained"] = (
                row["receipt_identity"] == store.records["events"][0]["record"][
                    "receipt_identity"] and len(memory.history("1:HOLD")) == 1)
            try:
                memory.record(store, {"record": {"authorization_status": "REJECTED"}},
                              "unauthorized")
                checks["unauthorized_store_admission_rejected"] = False
            except RuntimeError:
                checks["unauthorized_store_admission_rejected"] = True
            before = memory.checkpoint()
        # Fresh objects restore only after both authenticated stores replay.
        with SessionStore(session_path, True) as restored, \
                DurableMemory(database_path, False) as memory:
            replay = memory.reconcile(restored)
            after = memory.checkpoint()
            checks["fresh_restore_authenticated_only"] = (
                replay == {"status": "PASS", "authenticated_events": 1} and
                before["event_store_sha256"] == after["event_store_sha256"] and
                before["zakhor_state_sha256"] == after["zakhor_state_sha256"])
            checks["call_and_evidence_chains_replay"] = (
                len(restored.records["calls"]) == 2 and
                len(restored.records["events"]) == 1 and
                len(restored.records["training"]) == 1)
    if not all(checks.values()):
        raise RuntimeError(f"protected preflight failed: {checks}")
    result = dict(status="PASS", inference_calls=0, checks=checks,
        protected_classes=["ExternalExecutionBoundary", "StatusBoundFramework",
                           "SessionStore"], call_budget=48)
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
