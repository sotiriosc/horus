"""Independent finite-data checks; never imports old runtime or chooser."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from .analyze import PACKAGE, analyze, write

ROOT=PACKAGE.parents[1]
PARENT='004ec5a6952d6b1c2c793eabe7200215611ea7b0'


def verify():
    manifest=json.loads((PACKAGE/'source-manifest.json').read_text())
    raw=(PACKAGE/'retained-evidence.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==manifest['finite_evidence_sha256']
    evidence=json.loads(raw);old=deepcopy(evidence);result=analyze(evidence)
    assert evidence==old and result==analyze(deepcopy(evidence))
    expected={(f,w,m) for f in ('O1','O2') for w in ('W0','W1','W3','D1') for m in range(6)}
    assert {(r['family'],r['world'],r['mapping_index']) for r in evidence}==expected
    assert sorted(r['context_index'] for r in evidence)==list(range(48))
    mechanical=json.loads((ROOT/'experiments/mechanical_exploitation_baseline_v0/results.json').read_text())
    old_scores={c['context_index']:c for c in mechanical['contexts']}
    n=0; latest_matches=0;exact=0;consequence=0;history_rows=0
    for e,c in zip(evidence,result['contexts']):
        assert c['classification']==old_scores[c['context_index']]['Map_partition']
        def independent_ranking(which):
            values={r['action']:r[which]['consequence'] for r in e['actions']}
            # Pairwise rank positions, independent of analyze.ranking().
            rank={a:sum(v>values[a] for v in values.values()) for a in values}
            return [[a for a in ('ADVANCE','HOLD','RETREAT') if rank[a]==i] for i in sorted(set(rank.values()))]
        assert c['predicted_ranking']==independent_ranking('parsed_prediction')
        assert c['actual_ranking']==independent_ranking('retained_detached_outcome')
        assert c['latest_ranking']==independent_ranking('latest_observation')
        for a in e['actions']:
            p=a['parsed_prediction'];t=a['retained_detached_outcome'];h=a['history']
            assert len(h)==a['history_depth'] and h[-1]==a['latest_observation']
            assert e['mapping'][a['alias']]==a['action']
            assert all(x['surface_action']==a['alias'] for x in h)
            assert all(set(x)=={'epoch','transaction_id','surface_action','next_state','consequence'} for x in h)
            assert [(x['epoch'],x['transaction_id']) for x in h]==sorted((x['epoch'],x['transaction_id']) for x in h)
            assert len(set((x['epoch'],x['transaction_id']) for x in h))==len(h)
            for observation in [p,t,*h]:
                assert type(observation['consequence']) is int and observation['consequence'] in (-1,0,1)
                assert type(observation['next_state']) is int and observation['next_state'] in range(4)
            assert h[-1]['consequence']==t['consequence']
            latest_matches+=p['consequence']==h[-1]['consequence'];exact+=p==t;consequence+=p['consequence']==t['consequence'];n+=1;history_rows+=len(h)
    assert (n,history_rows,latest_matches,consequence,exact)==(144,180,116,116,111)
    assert result['total']['latest_copy']['matches']==latest_matches
    assert result['total']['exact_accuracy']['matches']==exact
    original=json.loads((ROOT/'experiments/map_explorer_oracle_decomposition_v0/results.json').read_text())
    assert original['total']['Map']['exact']==exact and original['total']['Map']['consequence_correct']==consequence
    errors=[c for c in result['contexts'] if c['classification']!='MAP_TRUE_BEST_UNIQUE']
    assert len(errors)==23 and all(c['failure_class']=='A_TRUE_BEST_ACTION_UNDERPREDICTED' and not c['non_best_overpredicted'] and len(c['consequence_error_actions'])==1 for c in errors)
    assert Counter(c['world'] for c in errors)=={'W0':7,'W1':12,'W3':4}
    assert all(c['predicted_triple']==[-1,0,0] for c in result['contexts'] if c['world']=='W1')
    assert all(c['latest_ranking_true_best_unique'] for c in result['contexts'])
    # Sum every marginal group back to all 144 forecasts.
    for groups in result['groups'].values():
        assert sum(x['n'] for x in groups.values())==144
        assert sum(x['latest_copy']['matches'] for x in groups.values())==116
        assert sum(x['exact_accuracy']['matches'] for x in groups.values())==111
        assert sum(x['erroneous_tie_creators'] for x in groups.values())==19
        assert sum(x['wrong_unique_max_members'] for x in groups.values())==4
    assert len(result['seed_pairs'])==72
    inherited=0
    entries=subprocess.check_output(['git','ls-tree','-r',PARENT],cwd=ROOT,text=True).splitlines()
    for line in entries:
        meta,path=line.split('\t');mode,kind,oid=meta.split();assert kind=='blob'
        raw=(ROOT/path).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid,path
        assert bool((ROOT/path).stat().st_mode&0o111)==(mode=='100755'),path
        inherited+=1
    for path,h in manifest['inherited_file_hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==h
    firewall=json.loads((ROOT/'experiments/grounded_lineage_rebaseline_v0/claim_eligibility.json').read_text())
    entry=next(x for x in firewall['checkpoints'] if x['checkpoint']=='map_explorer_oracle_decomposition_v0')
    assert entry['evidence_category']=='D' and 'authenticated_past_to_detached_world_forecast_scores' in entry['permitted_current_claim_types']
    assert not [m for m in sys.modules if m.startswith('experiments.') and not m.startswith('experiments.map_ranking_failure_forensics_v0')]
    return dict(status='RETAINED-DATA VERIFICATION PASSED',parent_files_preserved=inherited,contexts_checked=48,action_forecasts_checked=n,
        visible_history_rows=history_rows,independent_pairwise_rankings_checked=144,all_marginals_reconcile=True,
        exact_replay=True,detached_input_unchanged=True,mechanical_scores_preserved=True,original_Map_totals_preserved=True,
        claim_firewall_preserved=True,source_scope=entry['current_evidentiary_use'],runtime_and_chooser_modules_imported=0,
        historical_receipt_object_identity_reconstructed=False,new_model_calls=0,new_world_executions=0,
        interpretation='Checks validate reconstruction and arithmetic, not a model-performance pass threshold or causal/internal-mechanism identification.')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    value=verify();args.out.mkdir(parents=True,exist_ok=True);write(args.out/'verification.json',value);print(json.dumps(value,sort_keys=True))


if __name__=='__main__':main()
