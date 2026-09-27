"""Persistent-location durability gate plus unchanged scientific gate; zero model I/O."""
import argparse
import unittest
from pathlib import Path
from experiments.model_proposal_role_composition_v2.preflight import check
from . import test_durability
from .durable import require_durable,atomic_write
from .run import infrastructure_frozen,ROOT


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    location=require_durable(args.output.parent,ROOT);location.mkdir(parents=True,exist_ok=True)
    registration=infrastructure_frozen();science=check();test_durability.BASE=str(location)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(test_durability.DurabilityTests)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    proof=dict(passed=result.wasSuccessful(),actual_model_calls=0,tests=result.testsRun,
        scientific_gate_status=science['status'],projection_contexts=science['projection_contexts'],initial_contexts=len(science['initial_episodes']),
        infrastructure_sha256=registration['sha256'],simulated_crash_states=['NOT_ISSUED','REQUEST_INTENT_RECORDED','RESPONSE_RECEIVED','PARSED','TRANSACTION_FINALIZED'],
        automatic_reissue_allowed=False,unchanged_transaction_equivalence=result.wasSuccessful())
    atomic_write(args.output,proof)
    if not proof['passed']:raise SystemExit(2)
    print('PASS: durable write-ahead/fsync, five crash states, exact frozen routing, UNKNOWN; ZERO MODEL CALLS.')


if __name__=='__main__':main()
