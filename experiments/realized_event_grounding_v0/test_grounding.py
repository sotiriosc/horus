"""Boundary tests beyond the registered end-to-end campaign."""
from dataclasses import FrozenInstanceError, replace
import unittest

from experiments.base_framework_v1.framework import MeasureAuditor
from .campaign import setup, execute, published
from .framework import evidence


class GroundingTests(unittest.TestCase):
    def test_failed_execution_mints_nothing_and_receipt_is_immutable(self):
        system, source, world = setup("IMMUTABILITY")
        pending = system.begin_step(forced_action="HOLD")
        self.assertIsNone(source.reader().current())
        with self.assertRaises((ValueError, KeyError)):
            source.execute(pending.epoch, pending.transaction_id, "INVALID")
        self.assertIsNone(source.reader().current())
        receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
        with self.assertRaises(FrozenInstanceError):
            receipt.realized_consequence = -1
        self.assertFalse(hasattr(source.reader(), "execute"))
        with self.assertRaises(RuntimeError):
            source.execute(pending.epoch, pending.transaction_id, pending.action)
        self.assertTrue(system.submit_package(evidence(receipt)).committed)

    def test_direct_legacy_ingress_cannot_bypass_receipt(self):
        system, source, world = setup("BYPASS")
        pending = system.begin_step(forced_action="HOLD")
        before = published(system)
        result = system.inner.submit_receipt("A", None)
        self.assertFalse(result.committed)
        self.assertEqual(before, published(system))
        self.assertFalse(system.inner.continuation_authorized)

    def test_measure_repair_does_not_rewrite_realized_event(self):
        for wrong_repair in (False, True):
            system, source, world = setup("MEASURE" + str(wrong_repair))
            for action in ("HOLD", "ADVANCE", "RETREAT"):
                execute(system, source, world, action)
            pending = system.begin_step(forced_action="HOLD")
            receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
            before = published(system)
            result = system.submit_package(evidence(receipt), wrong_measure=True,
                                           wrong_measure_recovery=wrong_repair)
            self.assertIs(source.reader().current(), receipt)
            self.assertEqual(receipt.realized_consequence, -1)
            self.assertEqual(result.committed, not wrong_repair)
            if wrong_repair:
                self.assertEqual(before, published(system))
            else:
                self.assertEqual(system.inner.memory.records[-1].consequence, -1)
                self.assertFalse(system.inner.memory.records[-1].measurement_matches)

    def test_memory_repair_uses_receipt_bound_history(self):
        system, source, world = setup("MEMORY_REPAIR")
        row, receipt = execute(system, source, world, "HOLD")
        original = system.inner.memory.records[0]
        system.inner.memory.corrupt_consequence(1)
        pending = system.begin_step()
        self.assertEqual(system.inner.memory.records[0], original)
        self.assertEqual(pending.action, "HOLD")
        self.assertIs(system.packages[0].receipt, receipt)

    def test_shared_pair_and_memory_corruption_cannot_redefine_receipt(self):
        system, source, world = setup("RETAINED_CORRUPTION")
        execute(system, source, world, "HOLD")
        system.inner.memory.records[0] = replace(system.inner.memory.records[0], consequence=-1)
        system.inner.pairs.decisions[0] = replace(system.inner.pairs.decisions[0], consequence=-1)
        before = published(system)
        result = system.begin_step()
        self.assertFalse(result.committed)
        self.assertEqual(before, published(system))

    def test_post_check_root_swap_discards_staged_commit(self):
        system, source, world = setup("MID_STAGE_SWAP")
        pending = system.begin_step(forced_action="HOLD")
        receipt = source.execute(pending.epoch, pending.transaction_id, pending.action)
        source_ref = source

        class SwappingMeasure(MeasureAuditor):
            def __deepcopy__(self, memo):
                return self

            def verify(self, measurement, prediction, decision):
                # Test-only disturbance after initial binding, before publication.
                source_ref.release(receipt)
                source_ref.execute(pending.epoch, pending.transaction_id, pending.action)
                return super().verify(measurement, prediction, decision)

        system.inner.measure_auditor = SwappingMeasure()
        before = published(system)
        result = system.submit_package(evidence(receipt))
        self.assertFalse(result.committed)
        self.assertEqual(result.reason, "prediction_or_root_changed")
        self.assertEqual(before, published(system))
        self.assertFalse(system.inner.continuation_authorized)


if __name__ == "__main__":
    unittest.main()
