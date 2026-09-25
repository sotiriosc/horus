"""Execute the preregistered audit without modifying any framework runtime.

Exit 0: covered criteria pass. Exit 2: observed covered failure. Exit 3:
harness error or an unestablished required observation. Negative-control failures
are recorded separately and do not determine the protected verdict.
"""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import ExitStack
from dataclasses import FrozenInstanceError, asdict, replace
import hashlib
import json
from pathlib import Path
import tempfile
import traceback
from unittest.mock import patch

from experiments.base_framework_v0.environment import BoundedWorld
from experiments.base_framework_v0.framework import BaseFramework, Prediction
from experiments.base_framework_v1 import source_a, source_b
from experiments.base_framework_v1.framework import (
    CrossAuthorityState, CrossSourceFramework, StateCandidate, StepResult,
)
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.base_framework_v2.registry import corrupted_registry
from experiments.base_framework_v2.types import RegisteredSourceEvidence
from experiments.base_framework_v2 import witness_c


ACTIONS = ("ADVANCE", "HOLD", "RETREAT")
BASE = "b8e4245ef14b11ee5d94ce851aec4d8dc059963f"
PROTECTED = (
    "clean_loop", "memory_causal_v0", "memory_causal_v1", "memory_causal_v2",
    "map_memory", "measure_stale", "explorer_stale_map", "recovery_wrong_epoch",
    "memory_eviction", "epoch_disagreement", "valid_incumbent", "invalid_incumbent",
    "delayed_partial", "final_retry_success", "final_retry_reject", "quarantine_capacity",
    "repeated_rejection", "alternating_evidence", "fault_after_recovery",
    "fault_before_behavior", "combined_faults", "legacy_ingress",
    "stale_package", "old_prediction", "old_consequence", "epoch_stale",
    "evicted_reinsert", "duplicate_delivery", "delayed_old_b", "descending_epoch_repair",
)
ALIASES = tuple(f"alias_s{state}_{action}" for state in range(4) for action in ACTIONS)
ABLATIONS = ("provenance", "self_authorization", "memory_audit", "descendant",
             "incumbent", "quarantine", "early_continuation")
BOUNDARIES = ("prediction_replacement", "abc_common", "registry_corrupt")


def require(row, condition, criterion, detail):
    if not condition and not any(v["criterion"] == criterion and v["detail"] == detail
                                 for v in row["violations"]):
        row["violations"].append({"criterion": criterion, "detail": detail})


def coordinates(receipt):
    return receipt.epoch, receipt.transaction_id, receipt.channel_sequence


def independent_separation(registry, identities):
    nodes = {n.process_id: n for n in registry.nodes}
    paths = []
    for identity in identities:
        todo, seen, domains = [identity], set(), set()
        while todo:
            item = todo.pop()
            if item in seen:
                continue
            if item not in nodes:
                return False
            seen.add(item)
            domains.add(nodes[item].fault_domain)
            todo.extend(nodes[item].parents)
        paths.append((seen - {"TRUE_WORLD"}, domains - {"WORLD_ROOT"}))
    return all(not (a[0] & b[0] or a[1] & b[1])
               for i, a in enumerate(paths) for b in paths[i + 1:])


class Driver:
    """Test-only observer. Truth does not enter runtime authorization."""

    def __init__(self, row, initial=0, registry=None):
        self.row = row
        self.system = EvidenceProvenanceFramework(initial, row["seed"] + 100, registry)
        self.oracle = TrueWorldOracle(initial)
        self.events = {}
        self.trace = []
        self.prediction = None
        self.pending_reference = None
        self.event = None
        self.last_evidence = None
        self.results = []
        self.maxima = {"memory": 0, "pairs": 0, "packages": 0, "items": 0,
                       "map_quarantine": 0, "memory_quarantine": 0,
                       "package_trace": 0, "runtime_trace": 0, "driver_trace": 0}

    def observe_bounds(self, aligned=False):
        s = self.system
        values = {"memory": len(s.memory.records), "pairs": len(s.pairs.decisions),
                  "packages": len(s.packages), "items": len(s.staged),
                  "map_quarantine": len(s.map.quarantine),
                  "memory_quarantine": len(s.memory.quarantine),
                  "package_trace": len(s.package_trace), "runtime_trace": len(s.trace),
                  "driver_trace": len(self.trace)}
        limits = {"memory": 8, "pairs": 8, "packages": 8, "items": 3,
                  "map_quarantine": 1, "memory_quarantine": 1,
                  "package_trace": 24, "runtime_trace": 24, "driver_trace": 24}
        for name, value in values.items():
            self.maxima[name] = max(self.maxima[name], value)
            require(self.row, value <= limits[name], "F8", f"{name} limit exceeded")
        s.assert_bounds()
        if aligned:
            identities = [tuple((r.epoch, r.transaction_id) for r in seq)
                          for seq in (s.memory.records, s.pairs.decisions, s.packages)]
            require(self.row, identities[0] == identities[1] == identities[2],
                    "F8", "Memory/pair/package chronological correspondence lost")

    def begin(self, action=None, old_prediction=None):
        s = self.system
        begun = s.begin_step(forced_action=action)
        if isinstance(begun, StepResult):
            self.results.append(begun)
            self.observe_bounds()
            return begun
        if old_prediction is not None:
            # Stale model output installed BEFORE outcome, not a changed oracle.
            begun.prediction = old_prediction
        self.prediction = asdict(begun.prediction)
        self.pending_reference = begun
        self.observe_bounds(aligned=True)
        corrupt = []
        for record in s.memory.records:
            event = self.events.get((record.epoch, record.transaction_id))
            if event and record.consequence != event.consequence:
                corrupt.append(record)
        if corrupt:
            repaired_view = [replace(r, consequence=self.events[(r.epoch, r.transaction_id)].consequence)
                             if (r.epoch, r.transaction_id) in self.events else r
                             for r in s.memory.records]
            expected = s.explorer.choose(s.map.current.state, repaired_view)
            require(self.row, begun.action == expected, "F7",
                    "corrupt unaudited Memory changed Explorer action")
        event = self.oracle.execute(begun.epoch, begun.transaction_id, begun.action)
        self.event = event
        key = event.epoch, event.transaction_id
        require(self.row, key not in self.events, "F3", "world transaction identity reused")
        self.events[key] = event
        if len(self.trace) >= 24:
            raise AssertionError("audit trace allocation exceeds preregistered bound")
        self.trace.append({"event": asdict(event), "prediction_before": dict(self.prediction),
                           "rounds": [], "result": None, "exception": None})
        return begun

    def evidence(self, mode="clean", cached=None):
        s = self.system
        request = s.observation_request(self.event.pre_state)
        a = RegisteredSourceEvidence(source_a.observe(request), "OBSERVATION_PATH_A",
                                     "source_a", s.registry.version)
        b = RegisteredSourceEvidence(source_b.observe(request), "OBSERVATION_PATH_B",
                                     "source_b", s.registry.version)
        c = witness_c.observe(request, s.registry.version)
        if mode == "a_bad":
            a = replace(a, receipt=source_a.observe(request, "wrong"))
        elif mode == "c_bad":
            c = replace(c, relation_code=(c.relation_code + 1) % 16)
        elif mode == "stale_c":
            c = replace(c, epoch=c.epoch - 1)
        elif mode == "wrong_epoch":
            a = replace(a, receipt=replace(a.receipt, epoch=a.receipt.epoch - 1))
        elif mode in ("alias", "derived_wrong", "abc_common", "registry_corrupt"):
            next_state = (self.event.next_state + 1) % 4
            consequence = ((c.relation_code - 1 - 3 * next_state) if mode == "alias"
                           else {-1: 0, 0: 1, 1: -1}[self.event.consequence])
            a = replace(a, receipt=replace(a.receipt, observed_next_state=next_state,
                                          observed_consequence=consequence))
            b = replace(b, receipt=replace(b.receipt, observed_next_state=next_state,
                                          observed_consequence=consequence))
            if mode != "alias":
                # Negative controls intentionally derive C; correct-C alias
                # cases never change C or its normal production path.
                c = replace(c, relation_code=3 * next_state + consequence + 1)
            if mode in ("derived_wrong", "registry_corrupt"):
                c = replace(c, process_id="DERIVED_WITNESS")
            if mode == "registry_corrupt":
                b = replace(b, process_id="DERIVED_B_REFERENCE")
        elif mode == "old_all":
            a, b, c = cached
        elif mode == "old_a":
            a = cached[0]
        elif mode == "old_b":
            b = cached[1]
        return a, b, c

    def submit(self, evidence, legacy=False, **kwargs):
        s = self.system
        pending = s.pending
        before_commits = s.inner.metrics["commits"]
        a, b, c = evidence
        entry = {"a": asdict(a), "b": asdict(b), "c": asdict(c), "legacy": legacy}
        self.trace[-1]["rounds"].append(entry)
        self.last_evidence = evidence
        try:
            if legacy:
                partial = s.submit_receipt("A", a.receipt)
                require(self.row, not partial.committed, "F2", "first A receipt committed")
                result = s.submit_receipt("B", b.receipt, **kwargs)
            else:
                result = s.submit_package(a, b, c, **kwargs)
        except Exception as error:
            self.trace[-1]["exception"] = {"type": type(error).__name__, "message": str(error),
                                           "commit_delta": s.inner.metrics["commits"] - before_commits}
            self.audit_after(pending, evidence, s.inner.metrics["commits"] > before_commits)
            raise
        self.results.append(result)
        self.trace[-1]["result"] = asdict(result)
        self.audit_after(pending, evidence, result.committed)
        if result.continued:
            require(self.row, result.committed, "F6", "continued without commit")
        return result

    def audit_after(self, pending, evidence, committed):
        s = self.system
        self.observe_bounds(aligned=committed)
        if self.pending_reference is not None:
            require(self.row, asdict(self.pending_reference.prediction) == self.prediction,
                    "F9", "prediction reference changed after outcome revelation")
        if not committed:
            return
        a, b, c = evidence
        expected_coords = pending.epoch, pending.transaction_id, pending.channel_sequence
        require(self.row, coordinates(a.receipt) == coordinates(b.receipt) == coordinates(c) == expected_coords,
                "F5", "stale evidence coordinates authorized for current transaction")
        require(self.row, independent_separation(s.registry, (a.process_id, b.process_id, c.process_id)),
                "F5", "registered descendant/shared paths authorized")
        require(self.row, bool(s.packages) and
                (s.packages[-1].epoch, s.packages[-1].transaction_id) == expected_coords[:2],
                "F2", "history committed without complete package decision")
        if not s.packages or (s.packages[-1].epoch, s.packages[-1].transaction_id) != expected_coords[:2]:
            require(self.row, False, "F6", "continuation granted before package authorization")
        require(self.row, s.map.current.state == self.event.next_state,
                "F1", "committed Map disagrees with hidden world transition")
        for record in s.memory.records:
            event = self.events.get((record.epoch, record.transaction_id))
            if event is None:
                require(self.row, False, "F5", "Memory record has no matching executed transaction")
                continue
            require(self.row,
                    (record.pre_state, record.action, record.next_state, record.consequence) ==
                    (event.pre_state, event.action, event.next_state, event.consequence),
                    "F1", "committed Memory disagrees with hidden world transition")
        latest = next(r for r in s.memory.records
                      if (r.epoch, r.transaction_id) == (self.event.epoch, self.event.transaction_id))
        expected_match = (
            self.prediction["epoch"], self.prediction["transaction_id"],
            self.prediction["pre_state"], self.prediction["action"],
            self.prediction["next_state"], self.prediction["consequence"]
        ) == (self.event.epoch, self.event.transaction_id, self.event.pre_state,
              self.event.action, self.event.next_state, self.event.consequence)
        # For corrupt evidence, a false verdict relative to truth is already F1.
        # On honest evidence, confirmation must equal the pre-outcome snapshot.
        if (a.receipt.observed_next_state, a.receipt.observed_consequence) == (self.event.next_state, self.event.consequence):
            require(self.row, latest.measurement_matches == expected_match,
                    "F9", "stored confirmation differs from original prediction/truth relation")

    def step(self, modes=("clean", "clean"), action=None, cached=None,
             old_prediction=None, legacy=False, **kwargs):
        begun = self.begin(action, old_prediction)
        if isinstance(begun, StepResult):
            return begun
        for mode in modes:
            result = self.submit(self.evidence(mode, cached), legacy=legacy, **kwargs)
            if not result.needs_reobservation:
                return result
        raise AssertionError("runtime requested more than the provided two rounds")

    def fill(self, count):
        for _ in range(count):
            result = self.step()
            if not result.committed:
                raise AssertionError("clean setup failed")


def memory_causal(row, version):
    observations = []
    for without in (False, True):
        if version == "v0":
            s = BaseFramework(BoundedWorld(), epoch=row["seed"] + 100)
            for _ in range(5):
                if not s.run_step().committed:
                    raise AssertionError("v0 causal setup failed")
            before = (s.map.current.state, s.map.current.version, s.epoch, s.next_transaction_id)
            if without:
                s.memory.records.clear(); s.evidence.receipts.clear()
            result = s.run_step()
        elif version == "v1":
            s = CrossSourceFramework(epoch=row["seed"] + 100)
            world = TrueWorldOracle()
            def advance():
                pending = s.begin_step()
                event = world.execute(pending.epoch, pending.transaction_id, pending.action)
                request = s.observation_request(event.pre_state)
                s.submit_receipt("A", source_a.observe(request))
                return s.submit_receipt("B", source_b.observe(request))
            for _ in range(5):
                if not advance().committed:
                    raise AssertionError("v1 causal setup failed")
            before = (s.map.current.state, s.map.current.version, s.epoch, s.next_transaction_id)
            if without:
                s.memory.records.clear(); s.pairs.decisions.clear()
            result = advance()
        else:
            d = Driver(row); d.fill(5); s = d.system
            before = (s.map.current.state, s.map.current.version, s.epoch, s.next_transaction_id)
            if without:
                s.memory.records.clear(); s.pairs.decisions.clear(); s.packages.clear()
            result = d.step()
        observations.append({"without_history": without, "before": before,
                             "action": result.action, "committed": result.committed})
    row["observations"]["causal_pair"] = observations
    require(row, observations[0]["before"] == observations[1]["before"], "F10",
            "Memory ablation changed an input other than authorized history")
    require(row, [o["action"] for o in observations] == ["HOLD", "ADVANCE"], "F10",
            "Memory removal did not restore original action")


def must_commit(row, result):
    require(row, result.committed and result.continued, "F12", "declared recoverable case did not commit")


def must_reject(row, result):
    require(row, not result.committed and not result.continued, "F2", "invalid evidence/candidate committed or continued")


def expect_guard(row, function, label):
    try:
        function()
    except (RuntimeError, ValueError) as error:
        row["observations"][label] = {"type": type(error).__name__, "message": str(error)}
        return
    require(row, False, "F8", f"{label} guard did not halt")


def protected_case(row, name):
    if name.startswith("memory_causal_"):
        memory_causal(row, name[-2:]); return None
    initial = 1 if name == "valid_incumbent" else int(name[7]) if name.startswith("alias_s") else 0
    d = Driver(row, initial); s = d.system
    row["_driver"] = d
    if name == "clean_loop":
        d.fill(12)
    elif name.startswith("alias_s"):
        action = name.split("_", 2)[2]
        result = d.step(("alias", "alias"), action=action)
        must_reject(row, result)
    elif name in ("map_memory", "combined_faults", "fault_before_behavior"):
        d.fill(5); s.memory.corrupt_consequence(2)
        if name != "fault_before_behavior":
            s.map.current.state = 3
        result = d.step(("a_bad", "clean") if name == "combined_faults" else ("clean", "clean"),
                        wrong_measure=name == "combined_faults")
        if name == "fault_before_behavior":
            must_commit(row, result)
            require(row, result.action == "HOLD", "F7", "corrupt Memory changed imminent behavior")
    elif name == "measure_stale":
        must_commit(row, d.step(("stale_c", "clean"), wrong_measure=True))
    elif name == "explorer_stale_map":
        s.map.current.state = 3
        must_reject(row, d.step(action="INVALID"))
        require(row, d.oracle.execution_count == 0, "F2", "invalid action reached world")
    elif name == "recovery_wrong_epoch":
        s.map.current.state = 3
        must_reject(row, d.step(("wrong_epoch", "wrong_epoch"), failed_recovery=True))
    elif name == "memory_eviction":
        d.fill(8); s.memory.corrupt_consequence(1)
        must_commit(row, d.step())
        require(row, s.memory.evictions == 1 and len(s.memory.records) == 8, "F8", "eviction boundary failed")
    elif name == "epoch_disagreement":
        d.fill(1); s.start_epoch(row["seed"] + 1000)
        must_commit(row, d.step(("a_bad", "clean")))
    elif name == "valid_incumbent":
        result = d.step(action="HOLD", candidate_value=2)
        must_commit(row, result)
        require(row, result.incumbent_retained, "F11", "valid incumbent unnecessarily discarded")
    elif name == "invalid_incumbent":
        result = d.step(candidate_value=3)
        require(row, not result.incumbent_retained, "F11", "invalid incumbent retained")
    elif name == "delayed_partial":
        d.begin(); a, b, c = d.evidence()
        before = (s.map.current.state, len(s.memory.records), len(s.packages))
        s.stage("source_a", a); s.stage("source_b", b)
        require(row, (s.map.current.state, len(s.memory.records), len(s.packages)) == before,
                "F2", "partial evidence changed committed state")
        expect_guard(row, s.begin_step, "pending_begin")
        must_commit(row, d.submit((a, b, c)))
        row["observations"]["timeout"] = "No software clock/timeout contract; bounded waiting only"
    elif name == "final_retry_success":
        must_commit(row, d.step(("c_bad", "clean")))
        require(row, s.inner.metrics["reobservations"] == 1, "F8", "retry count differs from one")
    elif name == "final_retry_reject":
        must_reject(row, d.step(("c_bad", "c_bad")))
        expect_guard(row, lambda: s.submit_package(*d.last_evidence), "third_round")
    elif name == "quarantine_capacity":
        s.map.current.state = 3; s.map.quarantine_incumbent()
        expect_guard(row, lambda: d.step(candidate_value=2), "full_quarantine")
        require(row, not s.memory.records and len(s.map.quarantine) == 1, "F8", "quarantine exceeded or committed")
    elif name == "repeated_rejection":
        must_reject(row, d.step(("c_bad", "c_bad")))
        s.start_epoch(row["seed"] + 1000)
        must_reject(row, d.step(("c_bad", "c_bad")))
        expect_guard(row, lambda: s.start_epoch(row["seed"] + 2000), "third_epoch")
    elif name == "alternating_evidence":
        for index in range(6):
            must_commit(row, d.step(("a_bad", "clean") if index % 2 == 0 else ("clean", "clean")))
    elif name == "fault_after_recovery":
        s.map.current.state = 3; must_commit(row, d.step())
        must_commit(row, d.step(("c_bad", "clean")))
    elif name == "legacy_ingress":
        result = d.step(legacy=True)
        must_reject(row, result)
    elif name in ("stale_package", "old_consequence", "epoch_stale", "delayed_old_b", "old_prediction"):
        d.fill(1); cached = d.last_evidence
        old_prediction = Prediction(**d.prediction)
        if name == "epoch_stale":
            s.start_epoch(row["seed"] + 1000)
        elif name == "delayed_old_b":
            d.fill(1)
        if name == "old_prediction":
            must_commit(row, d.step(old_prediction=old_prediction))
            require(row, not s.memory.records[-1].measurement_matches, "F9", "stale prediction confirmed")
        elif name == "stale_package":
            must_reject(row, d.step(("old_all", "old_all"), cached=cached))
        else:
            mode = {"old_consequence": "old_a", "epoch_stale": "old_all", "delayed_old_b": "old_b"}[name]
            must_commit(row, d.step((mode, "clean"), cached=cached))
    elif name == "evicted_reinsert":
        d.fill(1); old = s.memory.records[0]; d.fill(8)
        s.memory.records[0] = old
        before = d.oracle.execution_count
        expect_guard(row, s.begin_step, "evicted_record")
        require(row, d.oracle.execution_count == before, "F7", "evicted history affected execution")
    elif name == "duplicate_delivery":
        d.fill(1); count = s.inner.metrics["commits"]
        expect_guard(row, lambda: s.submit_package(*d.last_evidence), "duplicate_delivery")
        require(row, s.inner.metrics["commits"] == count, "F3", "duplicate delivery committed")
    elif name == "descending_epoch_repair":
        d.fill(2); s.start_epoch(row["seed"]); d.fill(1)
        s.memory.corrupt_consequence(1)
        try:
            must_commit(row, d.step())
        except RuntimeError as error:
            row["observations"]["recovery_exception"] = str(error)
            require(row, False, "F12", "single-record recovery failed across distinct descending epochs")
        d.observe_bounds(aligned=True)
    else:
        raise KeyError(name)
    return d


def ablation_case(row, name, weakened):
    d = Driver(row, initial=1 if name == "provenance" else 0)
    row["_driver"] = d; s = d.system
    with ExitStack() as stack:
        if name == "provenance":
            d.step(action="HOLD"); cached = d.last_evidence
            if weakened:
                original_package = s.package_authorizer.authorize
                original_pair = s.inner.pair_authorizer.authorize
                def package(pending, a, b, c, registry):
                    fields = dict(epoch=pending.epoch, transaction_id=pending.transaction_id,
                                  channel_sequence=pending.channel_sequence)
                    return original_package(pending, replace(a, receipt=replace(a.receipt, **fields)),
                                            replace(b, receipt=replace(b.receipt, **fields)),
                                            replace(c, **fields), registry)
                def pair(pending, a, b):
                    fields = dict(epoch=pending.epoch, transaction_id=pending.transaction_id,
                                  channel_sequence=pending.channel_sequence)
                    return original_pair(pending, replace(a, **fields), replace(b, **fields))
                stack.enter_context(patch.object(s.package_authorizer, "authorize", package))
                stack.enter_context(patch.object(s.inner.pair_authorizer, "authorize", pair))
            result = d.step(("old_all", "old_all"), action="HOLD", cached=cached)
            if not weakened:
                must_reject(row, result)
        elif name == "self_authorization":
            s.map.current.state = 3
            if weakened:
                stack.enter_context(patch.object(s.inner.state_authorizer, "authorize", lambda *args: True))
            result = d.step(failed_recovery=True)
            if not weakened:
                must_reject(row, result)
            elif result.committed:
                require(row, False, "F4", "unchecked wrong Recovery candidate authorized")
        elif name == "memory_audit":
            d.fill(5); s.memory.corrupt_consequence(2)
            if weakened:
                stack.enter_context(patch.object(s.memory, "audit", lambda store: (list(s.memory.records), [])))
            result = d.step()
            row["observations"]["next_action"] = result.action
            if not weakened:
                require(row, result.action == "HOLD", "F7", "normal audit lost behavior")
        elif name == "descendant":
            if weakened:
                stack.enter_context(patch.object(s.registry, "declared_separate", lambda *args: True))
            result = d.step(("derived_wrong", "derived_wrong"))
            if not weakened:
                must_reject(row, result)
        elif name == "incumbent":
            if weakened:
                original = s.inner._complete_pair
                def select_incumbent(decision, **kwargs):
                    candidate = StateCandidate(decision.epoch, decision.transaction_id,
                                               decision.pair_decision_id, s.map.current.state)
                    if candidate.value != decision.next_state:
                        allowed = s.inner.state_authorizer.authorize(candidate, decision)
                        if not allowed:
                            return s.inner._reject("ablation incumbent rejected by retained state gate", executed=True)
                        raise AssertionError("retained state gate unexpectedly authorized wrong incumbent")
                    return original(decision, **kwargs)
                stack.enter_context(patch.object(s.inner, "_complete_pair", select_incumbent))
            result = d.step(candidate_value=3)
            row["observations"]["downstream_defense"] = result.reason
            if not weakened:
                must_commit(row, result)
        elif name == "quarantine":
            s.map.current.state = 3
            if weakened:
                stack.enter_context(patch.object(s.map, "quarantine_incumbent", lambda: None))
            result = d.step(failed_recovery=True)
            must_reject(row, result)
            row["observations"]["quarantine_entries"] = len(s.map.quarantine)
        elif name == "early_continuation":
            result = d.step(("c_bad", "c_bad"), legacy=weakened)
            if not weakened:
                must_reject(row, result)
        else:
            raise KeyError(name)
    return d


def boundary_case(row, name):
    d = Driver(row, registry=corrupted_registry() if name == "registry_corrupt" else None)
    row["_driver"] = d; s = d.system
    if name == "prediction_replacement":
        s.map.current.state = 3
        pending = d.begin()
        frozen = False
        try:
            pending.prediction.next_state = d.event.next_state
        except FrozenInstanceError:
            frozen = True
        row["observations"]["prediction_fields_frozen"] = frozen
        pending.prediction = Prediction(d.event.epoch, d.event.transaction_id,
                                        d.event.pre_state, d.event.action,
                                        d.event.next_state, d.event.consequence)
        result = d.submit(d.evidence())
        row["observations"]["replacement_committed"] = result.committed
        row["observations"]["manufactured_confirmation"] = s.memory.records[-1].measurement_matches
    else:
        d.step((name, name))
    return d


def one_case(name, seed, category, weakened=False):
    row = {"name": name, "seed": seed, "category": category, "weakened": weakened,
           "violations": [], "observations": {}, "harness_error": None}
    try:
        if category == "protected":
            protected_case(row, name)
        elif category in ("ablation_control", "ablation"):
            ablation_case(row, name, weakened)
        else:
            boundary_case(row, name)
    except Exception as error:
        row["harness_error"] = {"type": type(error).__name__, "message": str(error),
                                "traceback": traceback.format_exc()}
    d = row.pop("_driver", None)
    if d is not None:
        row["trace"] = d.trace
        row["maxima"] = d.maxima
        row["runtime_metrics"] = dict(d.system.inner.metrics)
        row["package_metrics"] = dict(d.system.metrics)
        row["observations"]["final_map"] = asdict(d.system.map.current)
        row["observations"]["ring_identities"] = {
            label: [[r.epoch, r.transaction_id] for r in records]
            for label, records in (("memory", d.system.memory.records),
                                   ("pairs", d.system.pairs.decisions), ("packages", d.system.packages))}
    row["outcome"] = "INCONCLUSIVE" if row["harness_error"] else "VIOLATION" if row["violations"] else "PASS"
    return row


def execute():
    rows = []
    for seed in (1, 2, 3):
        for name in PROTECTED + ALIASES:
            rows.append(one_case(name, seed, "protected"))
        for name in ABLATIONS:
            rows.append(one_case(name, seed, "ablation_control"))
            rows.append(one_case(name, seed, "ablation", True))
        for name in BOUNDARIES:
            rows.append(one_case(name, seed, "boundary"))
    protected = [r for r in rows if r["category"] == "protected"]
    failures = [r for r in protected if r["violations"]]
    errors = [r for r in rows if r["harness_error"]]
    controls = [r for r in rows if r["category"] == "ablation_control" and r["violations"]]
    result = {"baseline_commit": BASE, "recommendation": "B" if failures else "C" if errors or controls else "A",
              "protected_status": "FAIL" if failures else "INCONCLUSIVE" if errors or controls else "PASS",
              "counts": {"total_runs": len(rows), "protected_runs": len(protected),
                         "protected_violation_runs": len(failures), "harness_errors": len(errors),
                         "ablation_control_violations": len(controls),
                         "ablation_violation_runs": sum(r["category"] == "ablation" and bool(r["violations"]) for r in rows),
                         "boundary_violation_runs": sum(r["category"] == "boundary" and bool(r["violations"]) for r in rows)},
              "rows": rows}
    return result


def compact(result):
    groups = {}
    for row in result["rows"]:
        key = row["category"], row["name"]
        groups.setdefault(key, []).append(row)
    cases = []
    for (category, name), rows in groups.items():
        violations = sorted({(v["criterion"], v["detail"]) for row in rows for v in row["violations"]})
        cases.append({"name": name, "category": category,
                      "seeds": [r["seed"] for r in rows],
                      "outcomes": dict(Counter(r["outcome"] for r in rows)),
                      "violations": [{"criterion": c, "detail": d} for c, d in violations]})
    examples = {}
    for name in ("memory_causal_v0", "memory_causal_v1", "memory_causal_v2",
                 "alias_s0_ADVANCE", "legacy_ingress", "descending_epoch_repair",
                 "prediction_replacement"):
        row = next(r for r in result["rows"] if r["name"] == name and r["seed"] == 1)
        examples[name] = row["observations"]
        if name in ("alias_s0_ADVANCE", "legacy_ingress", "descending_epoch_repair"):
            examples[name] = {**examples[name], "final_transaction": row["trace"][-1]}
    return {**{k: v for k, v in result.items() if k != "rows"},
            "cases": cases, "examples": examples}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    output = args.output or Path(tempfile.mkdtemp(prefix="horus-minimum-audit-"))
    if output.resolve().is_relative_to(root):
        raise ValueError("raw evidence must be outside the source tree")
    if args.output:
        output.mkdir(parents=True, exist_ok=False)
    result = execute()
    paths = [p for version in ("base_framework_v0", "base_framework_v1", "base_framework_v2", "minimum_framework_audit")
             for p in (root / "experiments" / version).glob("*.py")]
    paths += [root / "research/minimum-framework-completion-definition.md",
              root / "research/minimum-framework-stress-preregistration.md"]
    result["source_sha256"] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (output / "compact.json").write_text(json.dumps(compact(result), indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("recommendation", "protected_status", "counts")}, indent=2))
    print(f"Evidence: {output}")
    for row in result["rows"]:
        if row["harness_error"]:
            print("HARNESS ERROR", row["name"], row["seed"], row["harness_error"]["message"])
    raise SystemExit(3 if result["counts"]["harness_errors"] else 2 if result["protected_status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
