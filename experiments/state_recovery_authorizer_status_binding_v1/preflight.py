"""Inspect legitimate producers and execute the unchanged historical campaign."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
from experiments.base_framework_v0 import framework as v0
from experiments.base_framework_v1 import framework as v1
from experiments.state_recovery_proposal_interface_v1 import campaign as previous
from experiments.state_recovery_proposal_interface_v1.framework import RecoveryOpportunity


def check():
    assert 'status=AuthorityState.RECOVERING' in inspect.getsource(v0.Recovery.state_candidate)
    assert 'value, CrossAuthorityState.RECOVERING' in inspect.getsource(v1.Recovery.state_candidate)
    assert 'return replace(native, value=value)' in inspect.getsource(RecoveryOpportunity.candidate)
    assert v1.StateCandidate.__dataclass_fields__['status'].default == v1.CrossAuthorityState.PROPOSED
    data = previous.run()
    native_events = [e for row in data['default_equivalence']['historical']['cases']
                     for e in row['native_observations'] if e['kind'] == 'native_recovery']
    rows = data['cases'] + [row for h in data['retained_history'] for row in (h['first'], h['second'])]
    injected_native = [e for row in rows for e in row['events'] if e['kind'] == 'native_attempt']
    assert all(e['candidate']['status'] == v1.CrossAuthorityState.RECOVERING
               for e in native_events + injected_native)
    ordinary = [e for row in rows if not row['callback_contexts'] for e in row['events']
                if e['kind'] == 'authorize']
    assert ordinary and all(e['accepted'] and e['candidate']['status'] == v1.CrossAuthorityState.PROPOSED
                            for e in ordinary)
    assert data['summary']['classification'] == 'C — NOT ESTABLISHED'
    assert data['summary']['wrong_status_acceptances_historical'] == 8
    matrix = [dict(enum=cls.__name__, name=status.name, value=status.value,
                   recovery_eligible=status == v1.CrossAuthorityState.RECOVERING)
              for cls in (v1.CrossAuthorityState, v0.AuthorityState) for status in cls]
    assert len(matrix) == 17 and sum(s['recovery_eligible'] for s in matrix) == 2
    return dict(contract='PASS_RECOVERY_SCOPE_ONLY', actual_model_calls=0,
        native_recovery_envelopes_checked=len(native_events) + len(injected_native),
        native_recovery_statuses=['RECOVERING'], ordinary_proposed_acceptances=len(ordinary),
        scope_required=True, scope_source='existing trusted coordinator recovery_authorized branch flag',
        previous_classification=data['summary']['classification'], old_wrong_status_acceptances=8,
        status_matrix=matrix, historical_campaign_sha256=hashlib.sha256(previous.serialized(data)).hexdigest()), data


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--historical-evidence', type=Path)
    args = parser.parse_args(); result, data = check()
    if args.historical_evidence:
        assert previous.serialized(data) == (args.historical_evidence / 'campaign.json').read_bytes()
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[2]):
        raise ValueError('private evidence must be external')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'preflight.json').write_bytes(previous.serialized(result))
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
