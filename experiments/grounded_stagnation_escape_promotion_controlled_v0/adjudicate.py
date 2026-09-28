"""Read-only preregistered gate adjudication after a source-frozen audit bug was found."""
from argparse import ArgumentParser
from pathlib import Path
import json
from horus.live import SessionStore,_atomic_write
from experiments.modern_memory_vs_horus_v0.storage import ModernMemory
from experiments.grounded_autonomous_agent_v0_2.worker import rows_of
from experiments.grounded_stagnation_escape_evaluation_v0.analyze import independent_suffix
from .analyze import analyze
from .worker import ELIGIBLE,CONTROLS

def adjudicate(root):
    report=analyze(root)
    original=report['recommendation']
    prefix={}
    for case in ELIGIBLE:
        path=root/'cases'/case/'S'
        with SessionStore(path/'session',True) as store, ModernMemory(path/'memory.sqlite3',False) as memory:
            memory.reconcile(store)
            decisions=rows_of(store,'AUTONOMOUS_AGENT_DECISION')
            count,relation=independent_suffix(decisions[:3])
            prefix[case]=dict(eligible=count==3,count=count,relation=relation,
                              first_trigger=report['per_case'][case]['trigger_indices'][0]
                              if report['per_case'][case]['trigger_indices'] else None)
    report['registered_D4_prefix_eligibility']=prefix
    report['original_frozen_analyzer_recommendation']=original
    report['audit_implementation_erratum']='The frozen analyzer conflated a model-driven ineligible D1-D3 prefix with candidate mechanism failure. The preregistration explicitly assigns an ineligible prefix with otherwise supported mechanism to MORE_EVIDENCE_REQUIRED.'
    eligible_failure=any(prefix[c]['eligible'] and not report['per_case'][c]['first_receipt_endpoint'] for c in ELIGIBLE)
    ineligible=any(not prefix[c]['eligible'] for c in ELIGIBLE)
    if not report['control_pass'] or report['counts']['false_triggers'] or eligible_failure or not report['negative_cost_gate_pass']:
        recommendation='RETAIN_INCUMBENT'
    elif ineligible or not report['restart_pass'] or report['counts']['shared_model_draws']==0:
        recommendation='MORE_EVIDENCE_REQUIRED'
    elif report['mechanism_pass']:
        recommendation='PROMOTE_S'
    else:
        recommendation='MORE_EVIDENCE_REQUIRED'
    report['recommendation']=recommendation
    report['recommendation_gate_provenance']='committed preregistration b8aa4062a06e3946fb313aa103de599ad9b16ca0'
    raw=json.loads((root/'analysis.private.json').read_text())
    _atomic_write(root/'analysis.original-analyzer.private.json',raw)
    raw['report']=report
    _atomic_write(root/'analysis.private.json',raw)
    _atomic_write(root/'analysis.public.json',report)
    return report

if __name__=='__main__':
    p=ArgumentParser();p.add_argument('--private-root',type=Path,required=True)
    print(json.dumps(adjudicate(p.parse_args().private_root),sort_keys=True))
