"""Mandatory zero-inference equality, projection and genuine-routing gate."""
import hashlib
import json
from pathlib import Path
from .protocol import SYSTEMS, OPTIONS, schedule, seed
from .runtime import Broker, setup, step, views
from .checks import unknown_preflight, Synthetic
from experiments.realized_event_grounding_v0.campaign import published
from experiments.model_proposal_role_composition_v1 import protocol as prior
from experiments.composition_empty_history_schema_contract_v0.protocol import SYSTEMS as CONTRACT

ROOT=Path(__file__).resolve().parents[2]


def frozen():
    data=json.loads((Path(__file__).parent/'frozen-inputs.json').read_text())
    for name,digest in data['sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    return data


def check():
    registration=frozen()
    assert SYSTEMS['Explorer']==prior.SYSTEMS['Explorer']
    assert SYSTEMS['Recovery']==prior.SYSTEMS['Recovery']
    assert SYSTEMS['Map']==CONTRACT['B']
    assert [r for r in SYSTEMS if SYSTEMS[r]!=prior.SYSTEMS[r]]==['Map']
    assert OPTIONS==prior.OPTIONS and schedule()==prior.schedule()
    for d in schedule():
        for decision in range(8):
            for role in SYSTEMS:assert seed(d,decision,role)==prior.seed(d,decision,role)
    for name in ('runtime.py','transport.py','checks.py'):
        assert (ROOT/'experiments/model_proposal_role_composition_v2'/name).read_bytes()==(ROOT/'experiments/model_proposal_role_composition_v1'/name).read_bytes(),name
    unknown=unknown_preflight();assert unknown['status']=='PASS' and unknown['all_seven_unknown_requirements']
    initial=[]
    for d in schedule():
        projection=views(0,published(setup(d['episode'])[0]),d['mapping'])
        assert all(a['verified_outcomes']=='UNTRIED' for a in projection['Explorer']['actions'])
        assert all(p['VERIFIED_CHRONOLOGICAL_HISTORY']==[] and set(p)=={'state','target_action','VERIFIED_CHRONOLOGICAL_HISTORY'} for p in projection['Map'].values())
        initial.append(dict(episode=d['episode'],family=d['family'],views=projection))
    broker=Broker(Synthetic());row=step(setup('V2_PREFLIGHT_ROUTING'),broker,schedule()[0],0)
    assert row['genuine_recovery'] and row['probe']['authorization']['committed']
    assert [c['role'] for c in broker.calls]==['Explorer','Map','Recovery']
    assert broker.calls[-1]['input']['VERIFIED_REALIZED_EVENT']==dict(next_state=1,consequence=1)
    assert any(e['kind']=='status_authorizer' and e['scope'] and e['accepted'] for e in row['events'])
    return dict(status='PASS',actual_model_calls=0,sole_system_change='Map',
        all_inherited_hashes_unchanged=True,identical_runtime_transport_controls=True,
        projection_contexts=unknown['projection_contexts'],initial_episodes=initial,
        schedule=schedule(),role_systems=SYSTEMS,role_options=OPTIONS,
        unknown=unknown,genuine_recovery_routing=dict(calls=broker.calls,row=row))


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    result=check();args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('PASS: unchanged sources/schedule, 12 initial inputs, 288 UNKNOWN projections, genuine Recovery routing. ZERO MODEL CALLS.')
