"""Mandatory synthetic-only interface gate. No transport or inference import."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from experiments.model_explorer_contradiction_revision_v1.campaign import fixture
from .adapter import MapProposalAdapter, DeterministicExplorer, INVALID, render, serialize
from .boundary import execute


class SyntheticProposer:
    def __init__(self,raw,fail=False): self.raw,self.fail,self.inputs=raw,fail,[]
    def __call__(self,prompt,seed):
        assert type(prompt) is str and type(seed) is int
        self.inputs.append(dict(prompt=prompt,seed=seed))
        if self.fail: raise ValueError("synthetic proposal failure")
        return self.raw


def run():
    rows=[]
    cases=[("correct_changed",'{"next_state":1,"consequence":-1}',"SHIFT",{},True),
           ("wrong_old",'{"next_state":1,"consequence":1}',"SHIFT",{},True),
           ("wrong_state_and_consequence",'{"next_state":0,"consequence":0}',"SHIFT",{},True),
           ("correct_stationary",'{"next_state":1,"consequence":1}',"CONTROL",{},True),
           ("measure_recovery",'{"next_state":1,"consequence":1}',"SHIFT",{"wrong_measure":True},True),
           ("measure_recovery_rejected",'{"next_state":1,"consequence":1}',"SHIFT",{"wrong_measure":True,"wrong_measure_recovery":True},False)]
    cases += [("invalid_"+str(i),raw,"SHIFT",{},False) for i,raw in enumerate(INVALID)]
    cases += [("proposal_failure",None,"SHIFT",{},False)]
    for index,(name,raw,arm,faults,commit) in enumerate(cases):
        d=dict(index=index,arm=arm,stage="H1",mapping={"K1":"ADVANCE","K2":"HOLD","K3":"RETREAT"})
        system,source,world,authentic=fixture(d)
        proposer=SyntheticProposer(raw,raw is None)
        prompt=serialize(render(system.inner.memory.records,d))
        adapter=MapProposalAdapter(system.inner.map,proposer,prompt,50001)
        copied=deepcopy(adapter)
        isolated=copied.base is not adapter.base and copied.current is not adapter.current and copied.proposer is proposer
        system.inner.map=adapter;system.inner.explorer=DeterministicExplorer()
        row=execute(system,source,world,authentic,faults)
        if row["authorization"]["committed"]!=commit: row["errors"].append("unexpected_gate_authorization")
        if not isolated: row["errors"].append("staged_map_alias")
        if len(proposer.inputs)!=1 or proposer.inputs[0]!={"prompt":prompt,"seed":50001}:
            row["errors"].append("proposer_boundary")
        if name.startswith("measure_recovery") and not any(o["kind"]=="recovery_measurement" for o in row["observations"]):
            row["errors"].append("recovery_not_observed")
        rows.append(dict(case=name,raw=raw,proposer_inputs=proposer.inputs,staging_isolated=isolated,probe=row))
    errors=[dict(case=r["case"],errors=r["probe"]["errors"]) for r in rows if r["probe"]["errors"]]
    return dict(summary=dict(gate="PASS" if not errors else "FAIL",actual_model_calls=0,
        cases=len(rows),synthetic_commits=sum(r["probe"]["authorization"]["committed"] for r in rows),
        errors=errors,boundary="existing MapModel.predict -> CrossSourceFramework.begin_step latch",
        authority="proposer receives only prompt string and integer seed; supplies bounded numeric prediction"),cases=rows)


def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--replay",type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    result=run();data=json.dumps(result,sort_keys=True,indent=2).encode()+b"\n"
    (a.output/"gate.json").write_bytes(data)
    if a.replay: assert data==a.replay.read_bytes(),"gate replay mismatch"
    print(json.dumps(result["summary"],indent=2));print("Evidence SHA256",hashlib.sha256(data).hexdigest())
    if result["summary"]["gate"]!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
