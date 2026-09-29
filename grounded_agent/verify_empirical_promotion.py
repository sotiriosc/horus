"""Identical zero-inference suite before/after changing the active alias."""
from contextlib import ExitStack
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import argparse, json, unittest
import grounded_agent
from grounded_agent.policy import promoted_decide
from grounded_agent.empirical_policy import integrated_decide
from horus.live import ModelClient

MODULES = (
    'grounded_state.test_core',
    'grounded_agent.test_promotion',
    'grounded_agent.test_empirical_promotion',
    'experiments.empirical_evidence_acquisition_proposal_v0.test_candidate',
    'experiments.grounded_stagnation_escape_evaluation_v0.test_candidate',
    'experiments.grounded_stagnation_escape_replication_v0.test_scenarios',
    'experiments.realized_event_grounding_v0.test_grounding',
    'experiments.modern_memory_vs_horus_v0.test_study',
    'horus.test_live',
)


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('before','after'));p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    expected=promoted_decide if args.stage=='before' else integrated_decide
    if grounded_agent.decide is not expected:raise RuntimeError('active alias disagrees with activation stage')
    with ExitStack() as stack:
        model=stack.enter_context(patch.object(ModelClient,'generate',side_effect=AssertionError('model inference forbidden in promotion suite')))
        network=stack.enter_context(patch('socket.socket.connect',side_effect=AssertionError('network forbidden in promotion suite')))
        suite=unittest.defaultTestLoader.loadTestsFromNames(MODULES)
        result=unittest.TextTestRunner(verbosity=1).run(suite)
        evidence=dict(stage=args.stage,status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
            model_inference_calls=model.call_count,network_calls=network.call_count,modules=list(MODULES),active_selector=expected.__module__+'.'+expected.__name__,
            verification_suite_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        args.output.write_text(json.dumps(evidence,indent=2)+'\n')
        if not result.wasSuccessful() or model.call_count or network.call_count:raise SystemExit(1)
    print(json.dumps(evidence))

if __name__=='__main__':main()
