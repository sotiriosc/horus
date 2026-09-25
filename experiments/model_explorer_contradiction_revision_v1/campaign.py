"""Independent safe fixtures, prospective registration and real probe execution."""
from dataclasses import asdict
import hashlib
from itertools import permutations
import json

from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import (
    SEQUENCE, EXPECTED, step, receipt_provenance)
from experiments.realized_event_grounding_v0.campaign import TestWorld, published
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from .adapter import MODEL, OPTIONS, SYSTEM, render, serialize, propose

FAMILIES={"O1":("K1","K2","K3"),"O2":("Q7","M4","Z2")}
LENGTHS={"H0":3,"H1":6,"H2":7}


def schedule():
    mappings=list(permutations(("ADVANCE","HOLD","RETREAT")))
    plan=[]
    for j in range(12):
        for family in (("O1","O2") if j%2==0 else ("O2","O1")):
            mapping=dict(zip(FAMILIES[family],mappings[j%6]));inverse={a:s for s,a in mapping.items()}
            for si,stage in enumerate(LENGTHS):
                fi=("O1","O2").index(family)
                for arm in (("CONTROL","SHIFT") if (j+fi+si)%2==0 else ("SHIFT","CONTROL")):
                    order=("HOLD","ADVANCE") if j<6 else ("ADVANCE","HOLD")
                    plan.append(dict(index=len(plan),schedule_id=j,seed=40001+j,family=family,
                        stage=stage,arm=arm,mapping_index=j%6,mapping=mapping,
                        options=[inverse[a] for a in order]))
    assert len(plan)==144
    return plan


def fixture(d,emit_setup=None):
    world=TestWorld(1,d["arm"]=="SHIFT")
    source=ExternalExecutionBoundary(world,f"EXTERNAL_CALL_{d['index']:03d}")
    system=RealizedEventFramework(source.reader(),1,1001);authentic={}
    for number,action in enumerate(SEQUENCE[:LENGTHS[d["stage"]]],1):
        row=step(system,source,world,action,authentic,True)
        if emit_setup:emit_setup(dict(call_index=d["index"],setup_step=number,step=row))
        if row["errors"]:raise RuntimeError("unsafe setup; stop: "+repr(row["errors"]))
    history={a:[r.consequence for r in system.inner.memory.records if r.pre_state==1 and r.action==a]
             for a in ("HOLD","ADVANCE")}
    assert history==EXPECTED[d["arm"]+"/"+d["stage"]]
    assert system.inner.map.current.state==1
    assert all(p["full_binding_verified"] and p["exact_authentic_object"] for p in receipt_provenance(system,authentic))
    assert system.inner.memory.records[0].action=="HOLD" and system.inner.memory.records[0].consequence==1
    assert system.inner.memory.records[1].action=="ADVANCE" and system.inner.memory.records[1].consequence==-1
    return system,source,world,authentic


def registration():
    plan=[]
    for d in schedule():
        system,_,_,authentic=fixture(d)
        d={**d,"payload":render(system.inner.memory.records,d)}
        d["exact_prompt"]=serialize(d["payload"])
        d["prompt_sha256"]=hashlib.sha256(d["exact_prompt"].encode()).hexdigest()
        d["fixture_memory"]=[asdict(r) for r in system.inner.memory.records]
        d["fixture_provenance"]=receipt_provenance(system,authentic)
        plan.append(d)
    for family in FAMILIES:
        for j in range(12):
            group=[d for d in plan if d["family"]==family and d["schedule_id"]==j]
            assert len({tuple(d["options"]) for d in group})==1
            for stage in LENGTHS:
                a,b=[d for d in group if d["stage"]==stage]
                assert a["mapping"]==b["mapping"] and a["seed"]==b["seed"]
                if stage=="H0":assert a["exact_prompt"]==b["exact_prompt"]
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
    call=propose(transport,system.inner.memory.records,d)
    emit_call(dict(descriptor=d,model_call=call))  # preserve response before execution/audit
    if before!=published(system):raise RuntimeError("direct protected mutation during model transport")
    action=call["parsed_action"]
    if action is None:
        executions=world.oracle.execution_count
        result=system.begin_step(forced_action="INVALID_MODEL_PROPOSAL")
        assert not result.committed and not result.executed and not result.continued
        assert before==published(system) and executions==world.oracle.execution_count
        assert source.reader().current() is None and not system.inner.continuation_authorized
        event=dict(authorization=asdict(result),before=before,after=published(system),errors=[],
                   commit_delta=0,actual=None,receipt=None,prediction=None,observations=[],bounds=dict(
                   memory=len(system.inner.memory.records),pairs=len(system.inner.pairs.decisions),
                   packages=len(system.packages),trace=len(system.inner.trace),pending_authentic=0))
    else:
        event=step(system,source,world,action,authentic,True)
    row=dict(descriptor=d,model_call=call,probe=event,valid=action is not None,
             current_world_better="HOLD" if d["arm"]=="CONTROL" else "ADVANCE",
             current_world_correct=action==("HOLD" if d["arm"]=="CONTROL" else "ADVANCE"),
             history_retained=event["after"]["memory"][:len(before["memory"])]==before["memory"])
    return row


def controls(plan):
    rows=[]
    for family in FAMILIES:
        d=next(d for d in plan if d["family"]==family and d["schedule_id"]==0 and d["arm"]=="CONTROL" and d["stage"]=="H0")
        third=next(s for s in d["mapping"] if s not in d["options"])
        outputs=("X9","HOLD","ADVANCE"," ".join(d["options"]),d["options"][0]+" because it is better",third)
        for number,raw in enumerate(outputs):
            class Synthetic:
                def generate(self,prompt,seed):return raw,{"synthetic":True}
            row=probe(Synthetic(),d,None,lambda x:None)
            assert not row["valid"] and row["probe"]["commit_delta"]==0
            rows.append(dict(family=family,control_index=number,raw_output=raw,probe=row["probe"]))
    return rows
