from __future__ import annotations

from dataclasses import asdict, replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.realized_event_grounding_v0.framework import evidence
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.state_recovery_authorizer_status_binding_v1.framework import StatusBoundFramework
from horus.live import LiveController, SessionStore, _plain
from horus.core import digest

from .protocol import G2_ADAPTER, G3_ADAPTER, ISSUED_REQUEST_BUDGET
from .storage import ModernMemory, file_hash


ROOT = Path(__file__).resolve().parents[2]


def verify_sources() -> bool:
    manifest = json.loads((ROOT / "research/modern-memory-vs-horus-v0/source-manifest.json").read_text())
    for group in ("protected_framework_sources", "experiment_sources", "policy_sources"):
        for relative, expected in manifest[group].items():
            if file_hash(ROOT / relative) != expected:
                raise RuntimeError(f"frozen source mismatch: {relative}")
    if file_hash(G2_ADAPTER) != manifest["models"]["G2"] or \
            file_hash(G3_ADAPTER) != manifest["models"]["G3"]:
        raise RuntimeError("frozen specialist identity mismatch")
    return True


def main() -> dict:
    checks = {"frozen_sources_verified": verify_sources()}
    forged = LiveController("PREFLIGHT:FORGED", 1, 9001, "A")
    forged.begin_step("HOLD"); original = forged.execute_pending()
    before = list(forged._active.framework.inner.memory.records)
    rejected = forged.submit_package(evidence(replace(original)))
    checks["equal_value_receipt_rejected"] = (not rejected.committed and before ==
        forged._active.framework.inner.memory.records)
    forged.release(original)

    class FailingWorld:
        def execute(self, *_): raise RuntimeError("registered failure")
    source = ExternalExecutionBoundary(FailingWorld(), "PREFLIGHT:FAILED")
    framework = StatusBoundFramework(source.reader(), 1, 9002)
    framework.begin_step(forced_action="HOLD")
    try: source.execute(9002, 1, "HOLD")
    except RuntimeError: pass
    checks["failed_execution_excluded"] = (source.reader().current() is None and
        not framework.inner.memory.records and not framework.packages)

    with TemporaryDirectory() as directory:
        root = Path(directory)
        with SessionStore(root / "session", False) as store, \
                ModernMemory(root / "memory.sqlite3", True) as memory:
            store.configure_regime("A"); epoch, identity = store.begin_runtime()
            controller = LiveController(identity, 1, epoch, "A")
            controller.begin_step("HOLD"); receipt = controller.execute_pending()
            result = controller.submit_package(evidence(receipt))
            record = controller._active.framework.inner.memory.records[-1]
            value = _plain(asdict(receipt))
            event = dict(receipt=value, receipt_identity=list(receipt.identity()),
                receipt_provenance_sha256=digest(value),
                authorization_status=result.status.value, memory_record=_plain(asdict(record)),
                source_scope=dict(runtime_index=1, source_identity=receipt.source_identity))
            envelope = store.append("events", "AUTHORIZED_REALIZED_EVENT", event)
            memory.record(store, envelope, "preflight")
            store.save(state=receipt.next_state,
                next_transaction_id=controller._active.framework.inner.next_transaction_id,
                completed_step=True, attempted_decision=True)
            controller.release(receipt)
            before_checkpoint = memory.checkpoint()
            try:
                memory.record(store, {"record": {"authorization_status": "REJECTED"}}, "bad")
                checks["unauthorized_memory_rejected"] = False
            except RuntimeError:
                checks["unauthorized_memory_rejected"] = True
        with SessionStore(root / "session", True) as store, \
                ModernMemory(root / "memory.sqlite3", False) as memory:
            checks["authenticated_restart"] = (memory.reconcile(store)["status"] == "PASS" and
                memory.checkpoint()["event_store_sha256"] ==
                before_checkpoint["event_store_sha256"])
            checks["chains_replay"] = len(store.records["events"]) == 1
    if not all(checks.values()):
        raise RuntimeError(f"preflight failed: {checks}")
    return dict(status="PASS", inference_calls=0, checks=checks,
        issued_request_budget=ISSUED_REQUEST_BUDGET)


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
