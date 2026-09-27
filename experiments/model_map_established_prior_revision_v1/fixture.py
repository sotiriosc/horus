"""External HOLD-only world and authenticated stage reconstruction; no core edits."""
from dataclasses import replace
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from experiments.realized_event_grounding_v0.framework import RealizedEventFramework
from experiments.realized_event_grounding_v0.receipt import ExternalExecutionBoundary
from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import receipt_provenance
from experiments.model_map_proposal_v0.adapter import DeterministicExplorer
from experiments.model_map_proposal_v0.boundary import execute

LENGTHS={"P0":2,"P1":3,"P2":4}
EXPECTED={arm+"/"+stage:([1]*n if arm=="CONTROL" else [1,1,-1,-1][:n])
          for arm in ("CONTROL","SHIFT") for stage,n in LENGTHS.items()}


class HoldWorld:
    """Driver-owned fixture intervention. No prediction enters execution."""
    def __init__(self):
        self.oracle=TrueWorldOracle(1)
        self.shifted=False
        self.switch_count=0
        self.last_actual=None

    def switch(self):
        if self.oracle.execution_count!=2 or self.shifted:
            raise ValueError("registered external switch is only after execution two")
        self.shifted=True
        self.switch_count+=1

    def execute(self,epoch,transaction_id,action):
        if action!="HOLD":raise ValueError("HOLD-only registered world")
        original=self.oracle.execute(epoch,transaction_id,action)
        if original.pre_state!=1 or original.next_state!=1:
            raise ValueError("outside registered state relation")
        self.last_actual=replace(original,consequence=-1) if self.shifted else original
        return self.last_actual


def fixture(d,emit_setup=None):
    world=HoldWorld()
    source=ExternalExecutionBoundary(world,f"EXTERNAL_MAP_PRIOR_{d['index']:03d}")
    system=RealizedEventFramework(source.reader(),1,1001)
    system.inner.explorer=DeterministicExplorer()
    authentic={}
    for number in range(1,LENGTHS[d["stage"]]+1):
        row=execute(system,source,world,authentic)
        if row["errors"] or not row["authorization"]["committed"]:
            raise RuntimeError("unsafe authenticated setup; stop")
        switched=d["arm"]=="SHIFT" and number==2
        if switched:world.switch()
        if emit_setup:emit_setup(dict(call_index=d["index"],setup_step=number,
                                      step=row,external_switch_after_execution=switched))
    records=system.inner.memory.records
    assert [r.consequence for r in records]==EXPECTED[d["arm"]+"/"+d["stage"]]
    assert all(r.pre_state==r.next_state==1 and r.action=="HOLD" for r in records)
    assert [r.transaction_id for r in records]==list(range(1,LENGTHS[d["stage"]]+1))
    assert [r.consequence for r in records[:2]]==[1,1]
    assert system.inner.map.current.state==1 and source.reader().current() is None
    assert world.switch_count==(1 if d["arm"]=="SHIFT" else 0)
    assert all(p["full_binding_verified"] and p["exact_authentic_object"] for p in receipt_provenance(system,authentic))
    system.assert_bounds()
    return system,source,world,authentic
