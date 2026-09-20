"""One new R1 execution or its own exact replay, with durable call/transaction WAL."""
import argparse
import json
from pathlib import Path
from experiments.model_proposal_role_composition_v2 import runtime
from experiments.model_proposal_role_composition_v2.protocol import schedule,SYSTEMS,OPTIONS
from experiments.model_proposal_role_composition_v2.transport import LocalModel,Replay
from experiments.model_proposal_role_composition_v2.preflight import check,frozen
from experiments.model_proposal_role_composition_v2.analysis import summarize
from experiments.model_proposal_role_composition_v2.checks import controls
from experiments.model_proposal_role_composition_v2.run import FILES as SCIENTIFIC_FILES
from experiments.model_recovery_proposal_v1.transport import metadata as verify_server
from .durable import CAMPAIGN,Journal,atomic_write,append_line,file_digest,require_durable,inspect,DurabilityFailure
from .instrumentation import DurableTransport,observe_boundaries

FILES=(*SCIENTIFIC_FILES,'journal.jsonl','campaign-state.json','durability-audit.json')
ROOT=Path(__file__).resolve().parents[2]


def infrastructure_frozen():
    data=json.loads((Path(__file__).parent/'frozen-infrastructure.json').read_text())
    for name,sha in data['sha256'].items():assert file_digest(ROOT/name)==sha,name
    return data


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--live',action='store_true');mode.add_argument('--replay',type=Path)
    p.add_argument('--baseline',required=True,type=Path);p.add_argument('--model-bytes',type=Path);p.add_argument('--durability-proof',type=Path)
    args=p.parse_args();registration=frozen();infra=infrastructure_frozen();gate=check()
    assert file_digest(args.baseline)==registration['baseline_calls_sha256']
    baseline=[json.loads(s) for s in args.baseline.read_text().splitlines()];baseline=[c for c in baseline if c['role']=='Map'];assert len(baseline)==9
    output=require_durable(args.output,ROOT)
    if output.exists():raise RuntimeError('existing campaign directory: inspect it; automatic rerun/resume forbidden')
    if not args.replay:
        proof=json.loads(args.durability_proof.read_text());assert proof['passed'] and proof['actual_model_calls']==0
        assert proof['infrastructure_sha256']==infra['sha256']
        base=LocalModel();old=json.loads((ROOT/'experiments/model_recovery_proposal_v1/frozen-inputs.json').read_text())
        meta=verify_server(base,old,json.loads(args.model_bytes.read_text()));meta.pop('system',None);meta.pop('options',None)
        meta.update(role_systems=SYSTEMS,role_options=OPTIONS,stateless=True,campaign_id=CAMPAIGN)
    else:
        base=Replay(args.replay/'model-calls.jsonl');meta=json.loads((args.replay/'metadata.json').read_text())
        assert meta['role_systems']==SYSTEMS and meta['role_options']==OPTIONS and meta['campaign_id']==CAMPAIGN
    journal=Journal(output);atomic_write(output/'metadata.json',meta);atomic_write(output/'schedule.json',schedule())
    rows=[];terminations={};client=DurableTransport(base,journal)
    try:
        with (output/'model-calls.jsonl').open('x') as cf,(output/'steps.jsonl').open('x') as sf:
            def emit(call):journal.parsed(call);append_line(cf,call)
            broker=runtime.Broker(client,emit)
            for descriptor in schedule():
                ep=descriptor['episode'];bundle=runtime.setup(f'{CAMPAIGN}:episode={ep}')
                for decision in range(8):
                    assert frozen()==registration and infrastructure_frozen()==infra
                    journal.episode=ep;journal.decision=decision
                    with observe_boundaries(journal):row=runtime.step(bundle,broker,descriptor,decision)
                    rows.append(row);append_line(sf,row)
                    terminations[str(ep)]=row['termination'] or ('eight_decisions_completed' if decision==7 else 'ONGOING')
                    journal.finalize(row,broker.calls,terminations)
                    print(f'episode={ep} decision={decision} calls={len(broker.calls)} executed={row["probe"]["authorization"]["executed"]} commit={row["probe"]["authorization"]["committed"]} stop={row["termination"]}',flush=True)
                    if row['termination']:break
            if args.replay:assert base.requests==len(base.rows)
            synthetic=controls();assert synthetic['counts']==dict(Explorer=5,Map=14,Recovery=22)
            result,chains=summarize(rows,broker.calls,baseline)
            result.update(study='model-proposal-role-composition-v2-replacement-r1',campaign_id=CAMPAIGN,
                original_v2='C — NOT ESTABLISHED / INTERRUPTED / LIVE EVIDENCE UNAVAILABLE',original_data_pooled=False,
                source_sha256=registration['sha256'],infrastructure_sha256=infra['sha256'],post_live_controls=synthetic['counts'],
                unknown_preflight=dict(status=gate['status'],projection_contexts=gate['projection_contexts']),baseline_calls_sha256=registration['baseline_calls_sha256'])
            for name,value in (('controls.json',synthetic),('chains.json',chains),('results.json',result)):atomic_write(output/name,value)
            state=json.loads((output/'campaign-state.json').read_text());state['status']='LIVE_CAMPAIGN_COMPLETED';state['completed_episodes']=12
            # No new journal entry: finalized head remains the atomic state's reference.
            atomic_write(output/'campaign-state.json',state)
            audit=inspect(output);assert audit['journal_valid'] and not audit['ambiguous_calls'] and audit['campaign_state_matches_journal']
            assert len(audit['call_states'])==len(broker.calls) and all(s=='TRANSACTION_FINALIZED' for s in audit['call_states'].values())
            atomic_write(output/'durability-audit.json',audit)
    except BaseException as exc:
        atomic_write(output/'STOP.json',dict(campaign_id=CAMPAIGN,classification='C — NOT ESTABLISHED',
            status='INTERRUPTED_DO_NOT_REISSUE',error_type=type(exc).__name__,reason=str(exc),inspection=inspect(output)))
        raise
    finally:journal.close()
    if args.replay:
        for name in FILES:assert (output/name).read_bytes()==(args.replay/name).read_bytes(),name
        for path in (args.replay/'memory-snapshots').glob('*.json'):assert path.read_bytes()==(output/'memory-snapshots'/path.name).read_bytes(),path.name
        print('All ten registered evidence files and Memory snapshots byte-identical; ZERO NEW INFERENCE.')
    print(result['live_eligible_classification']);print(result['real_calls']);print('Final classification awaits replay and regressions.')


if __name__=='__main__':main()
