"""Independent authenticated fixtures; sole model role is Map prediction."""
import hashlib
import json
from experiments.model_explorer_contradiction_revision_v1.campaign import schedule as old_schedule, FAMILIES
from .fixture import fixture, LENGTHS, EXPECTED
from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import receipt_provenance
from experiments.realized_event_grounding_v0.campaign import published
from experiments.model_map_proposal_v0.adapter import MODEL, OPTIONS, SYSTEM, INVALID, MapProposalAdapter, DeterministicExplorer, render, serialize, parse
from experiments.model_map_proposal_v0.boundary import execute
from experiments.model_map_proposal_v0.campaign import RecordedProposer


def schedule():
    plan=old_schedule()
    for d in plan:
        d.pop("options")
        d["seed"]=60001+d["schedule_id"]
        d["stage"]="P"+d["stage"][1]
    return plan


def registration():
    plan=[]
    for d in schedule():
        system,_,_,authentic=fixture(d)
        d={**d,"payload":render(system.inner.memory.records,d)}
        d["exact_prompt"]=serialize(d["payload"])
        d["prompt_sha256"]=hashlib.sha256(d["exact_prompt"].encode()).hexdigest()
        d["fixture_memory"]=published(system)["memory"]
        d["fixture_provenance"]=receipt_provenance(system,authentic)
        history=d["payload"]["VERIFIED_CHRONOLOGICAL_HISTORY"]
        assert [r["transaction_id"] for r in history]==list(range(1,LENGTHS[d["stage"]]+1))
        assert all(r["next_state"]==1 for r in history)
        assert [r["consequence"] for r in history]==EXPECTED[d["arm"]+"/"+d["stage"]]
        plan.append(d)
    for family in FAMILIES:
        for j in range(12):
            group=[d for d in plan if d["family"]==family and d["schedule_id"]==j]
            for stage in LENGTHS:
                a,b=[d for d in group if d["stage"]==stage]
                assert a["mapping"]==b["mapping"] and a["seed"]==b["seed"]
                if stage=="P0": assert a["exact_prompt"]==b["exact_prompt"]
                else:
                    pa=json.loads(a["exact_prompt"]);pb=json.loads(b["exact_prompt"])
                    for p in (pa,pb):
                        for r in p["VERIFIED_CHRONOLOGICAL_HISTORY"]:r["consequence"]=None
                    assert pa==pb
    data=json.dumps(dict(system=SYSTEM,model=MODEL,options=OPTIONS,plan=plan),sort_keys=True,indent=2).encode()+b"\n"
    return plan,data


def probe(transport,d,emit_setup,emit_call):
    system,source,world,authentic=fixture(d,emit_setup)
    before=published(system)
    assert before["memory"]==d["fixture_memory"]
    assert serialize(render(system.inner.memory.records,d))==d["exact_prompt"]
    proposer=RecordedProposer(transport,d,emit_call)
    system.inner.explorer=DeterministicExplorer()
    system.inner.map=MapProposalAdapter(system.inner.map,proposer,d["exact_prompt"],d["seed"])
    event=execute(system,source,world,authentic)
    if proposer.transport_error is not None: raise RuntimeError("transport failure; no retry") from proposer.transport_error
    if proposer.call is None: raise RuntimeError("no recorded model proposal")
    parsed=proposer.call["parsed_prediction"]
    if parsed is not None:
        if event["prediction"] is None or any(event["prediction"][k]!=v for k,v in parsed.items()):
            event["errors"].append("model_latch_mismatch")
        if not event["authorization"]["committed"]: event["errors"].append("clean_event_rejected")
    elif event["authorization"]["committed"] or event["prediction"] is not None:
        event["errors"].append("malformed_prediction_commit")
    return dict(descriptor=d,model_call=proposer.call,probe=event,valid=parsed is not None,
        history_retained=event["old_history_unchanged"],
        evaluator_outcome=dict(next_state=1,consequence=1 if d["arm"]=="CONTROL" else -1))


def controls(plan):
    rows=[]
    for family in FAMILIES:
        d=next(d for d in plan if d["family"]==family and d["schedule_id"]==0 and d["arm"]=="CONTROL" and d["stage"]=="P0")
        for number,raw in enumerate(INVALID):
            class Synthetic:
                def generate(self,prompt,seed): return raw,{"synthetic":True}
            row=probe(Synthetic(),d,None,lambda x:None)
            assert not row["valid"] and row["probe"]["commit_delta"]==0 and not row["probe"]["errors"]
            rows.append(dict(family=family,control_index=number,raw_output=raw,probe=row["probe"]))
    return rows
