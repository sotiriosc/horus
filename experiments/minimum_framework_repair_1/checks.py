"""Direct repair acceptance probes, using the frozen audit's independent world."""

from dataclasses import asdict, replace
from unittest.mock import patch

from experiments.base_framework_v1.framework import Recovery
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.minimum_framework_audit import run as frozen
from experiments.minimum_framework_repair_1.run import Driver


def driver(seed=1, initial=0):
    return Driver(dict(seed=seed, violations=[], observations={}), initial)


def snapshot(s):
    """Everything the transaction may publish as authorized state/history."""
    return dict(map=asdict(s.map.current), memory=list(s.memory.records),
                pairs=list(s.pairs.decisions), packages=list(s.packages),
                ledger=set(s.inner.state_authorizer.authorized),
                commits=s.inner.metrics["commits"], evictions=s.memory.evictions,
                map_quarantine=list(s.map.quarantine), memory_quarantine=list(s.memory.quarantine))


def aligned(s):
    ids = [[(r.epoch, r.transaction_id) for r in records]
           for records in (s.memory.records, s.pairs.decisions, s.packages)]
    assert ids[0] == ids[1] == ids[2], ids
    assert len(ids[0]) <= 8
    s._audit_package_ring()
    s.assert_bounds()
    return ids[0]


def no_violations(d):
    assert not d.row["violations"], d.row["violations"]


def rejection_probe(seed, mode="alias", field=None, value=None, initial=0, action="ADVANCE"):
    d = driver(seed, initial)
    s = d.system
    before = snapshot(s)
    d.begin(action)
    for _ in range(2):
        a, b, c = d.evidence(mode)
        if field == "relation_code":
            c = replace(c, relation_code=value)
        elif field:
            a = replace(a, receipt=replace(a.receipt, **{field: value}))
            b = replace(b, receipt=replace(b.receipt, **{field: value}))
        result = d.submit((a, b, c))
        assert not result.committed and not result.continued
        assert not s.continuation_authorized
        assert snapshot(s) == before
    assert not result.needs_reobservation
    no_violations(d)
    return dict(rejected=True, commit_delta=0, authorized_state_unchanged=True)


def run_checks():
    rows = []

    def check(name, operation):
        try:
            evidence = operation()
            rows.append(dict(name=name, status="PASS", evidence=evidence))
        except Exception as error:
            rows.append(dict(name=name, status="FAIL", error=f"{type(error).__name__}: {error}"))

    for state in range(4):
        for action in frozen.ACTIONS:
            def legitimate(state=state, action=action):
                d = driver(initial=state)
                result = d.step(action=action)
                assert result.committed and result.continued
                aligned(d.system)
                no_violations(d)
                return dict(state=state, action=action, next_state=d.system.map.current.state)
            check(f"legitimate_s{state}_{action}", legitimate)
            for seed in (1, 2, 3):
                check(f"alias_s{state}_{action}_seed{seed}",
                      lambda state=state, action=action, seed=seed:
                      rejection_probe(seed, initial=state, action=action))

    boundaries = [(field, value) for field in ("pre_state", "observed_next_state") for value in (-1, 4)]
    boundaries += [("observed_consequence", value) for value in (-2, 2)]
    boundaries += [("relation_code", value) for value in (-1, 12)]
    boundaries += [("action", "INVALID"), ("observed_next_state", True),
                   ("observed_consequence", 1.0), ("relation_code", True)]
    for field, value in boundaries:
        for seed in (1, 2, 3):
            check(f"domain_{field}_{value}_seed{seed}",
                  lambda field=field, value=value, seed=seed:
                  rejection_probe(seed, "clean", field, value))

    for seed in (1, 2, 3):
        for nested in (False, True):
            def ingress(seed=seed, nested=nested):
                d = driver(seed)
                s = d.system
                before = snapshot(s)
                d.begin()
                a, b, _ = d.evidence()
                endpoint = s.inner if nested else s
                for port, receipt in (("A", a.receipt), ("B", b.receipt)):
                    result = endpoint.submit_receipt(port, receipt)
                    assert not result.committed and not result.continued
                    assert snapshot(s) == before and not s.continuation_authorized
                return dict(endpoint="inner" if nested else "facade", commit_delta=0)
            check(f"mandatory_ingress_{nested}_seed{seed}", ingress)

    def public_methods():
        s = EvidenceProvenanceFramework()
        methods = [name for name in dir(s) if not name.startswith("_") and callable(getattr(s, name))]
        assert set(methods) == {"begin_step", "start_epoch", "observation_request", "stage",
                                "submit_receipt", "submit_package", "assert_bounds"}
        for forbidden in ("_complete_pair", "_recover_memory", "_reject", "_dispute"):
            assert not hasattr(s, forbidden)
        return methods
    check("public_ingress_inventory", public_methods)

    for count in (0, 8):
        for failure in ("final_check", "package_identity", "pair_identity", "package_length"):
            def atomicity(count=count, failure=failure):
                d = driver()
                d.fill(count)
                d.system.map.current.state = (d.oracle.state + 2) % 4
                d.begin()
                s = d.system
                before = snapshot(s)
                original = s._audit_package_ring

                def fail(candidate=None, packages=None):
                    # Exercise actual correspondence checks on staged mutations;
                    # final_check also rejects a fully valid proposed transaction.
                    if failure == "package_identity":
                        packages[-1] = replace(packages[-1], transaction_id=99)
                    elif failure == "pair_identity":
                        candidate.pairs.decisions[-1] = replace(candidate.pairs.decisions[-1], epoch=99)
                    elif failure == "package_length":
                        packages.pop()
                    original(candidate, packages)
                    if failure == "final_check":
                        raise RuntimeError("injected final validation failure")

                raised = False
                with patch.object(s, "_audit_package_ring", fail):
                    try:
                        s.submit_package(*d.evidence())
                    except RuntimeError:
                        raised = True
                assert raised
                assert snapshot(s) == before
                assert not s.continuation_authorized
                aligned(s)
                return dict(retained=count, fault=failure, commit_delta=0,
                            authorized_state_unchanged=True)
            check(f"atomic_{failure}_retained{count}", atomicity)

    for first, second in ((101, 1), (1, 101)):
        for count in (2, 8, 9):
            def temporal(first=first, second=second, count=count):
                d = driver()
                d.system = EvidenceProvenanceFramework(epoch=first)
                d.fill(count)
                s = d.system
                s.start_epoch(second)
                d.fill(1)
                chronology = aligned(s)
                target = s.memory.records[0]
                # Address the exact immutable identity, including epoch.
                s.memory.records[0] = replace(target, consequence=target.consequence + 5)
                before_recovery = [(r.epoch, r.transaction_id) for r in s.memory.records]
                d.begin()
                assert aligned(s) == before_recovery
                assert s.memory.records[0] == target
                assert d.submit(d.evidence()).committed
                assert aligned(s) == (chronology + [(second, 2)])[-8:]
                assert d.step().committed
                assert aligned(s) == (chronology + [(second, 2), (second, 3)])[-8:]
                no_violations(d)
                return dict(epochs=[first, second], setup=count, repaired_identity=before_recovery[0],
                            next_transaction_continued=True, identities=aligned(s))
            check(f"temporal_{first}_{second}_setup{count}", temporal)

    for seed in (1, 2, 3):
        def prediction(seed=seed):
            row = frozen.one_case("prediction_replacement", seed, "boundary")
            assert row["outcome"] == "PASS", row
            assert row["observations"]["replacement_committed"]
            assert not row["observations"]["manufactured_confirmation"]
            return row["observations"]
        with patch.object(frozen, "Driver", Driver):
            check(f"prediction_latch_seed{seed}", prediction)

    def recovery_budget():
        d = driver()
        d.fill(5)
        s = d.system
        s.memory.corrupt_consequence(2)
        s.map.current.state = 3
        counts = dict(memory_record=0, measurement=0, state_candidate=0)
        from contextlib import ExitStack
        with ExitStack() as stack:
            for name in counts:
                original = getattr(Recovery, name)
                def counted(self, *args, _name=name, _original=original, **kwargs):
                    counts[_name] += 1
                    return _original(self, *args, **kwargs)
                stack.enter_context(patch.object(Recovery, name, counted))
            assert d.step(wrong_measure=True).committed
        assert counts == dict(memory_record=1, measurement=1, state_candidate=1), counts
        no_violations(d)
        return dict(per_subsystem=counts, total=sum(counts.values()), evidence_reobservation_limit=1)
    check("recovery_budget_three_subsystems", recovery_budget)
    return dict(total=len(rows), passed=sum(r["status"] == "PASS" for r in rows),
                failed=sum(r["status"] == "FAIL" for r in rows), rows=rows)
