"""Zero-inference direct-history and receipt-independence preflight."""
import argparse
import hashlib
import json
from pathlib import Path
from experiments.realized_event_grounding_v0.campaign import published
from experiments.model_explorer_contradiction_revision_v1_feasibility.fixture import receipt_provenance
from .fixture import fixture, LENGTHS, EXPECTED
from .campaign import registration, probe


def run():
    plan,data=registration()
    stages={};cases=[]
    for arm in ("CONTROL","SHIFT"):
        for stage in LENGTHS:
            d=next(d for d in plan if d["family"]=="O1" and d["schedule_id"]==0 and d["arm"]==arm and d["stage"]==stage)
            setup=[];system,source,world,authentic=fixture(d,setup.append)
            key=arm+"/"+stage
            stages[key]=dict(history=d["payload"]["VERIFIED_CHRONOLOGICAL_HISTORY"],
                protected=published(system),provenance=receipt_provenance(system,authentic),
                external_switch_count=world.switch_count,setup=setup)
            outcomes=[]
            for raw in ('{"next_state":1,"consequence":1}','{"next_state":0,"consequence":0}'):
                class Synthetic:
                    def generate(self,prompt,seed):return raw,{"synthetic":True}
                row=probe(Synthetic(),d,None,lambda x:None)
                event=row["probe"]
                assert not event["errors"] and event["authorization"]["committed"]
                assert event["latched_before_execution"] and event["receipt_unchanged"]
                assert event["old_history_unchanged"] and event["after"]["memory"][:2]==event["before"]["memory"][:2]
                assert event["receipt"]["next_state"]==1
                assert event["receipt"]["realized_consequence"]==(1 if arm=="CONTROL" else -1)
                assert event["bounds"]["memory"]<=5
                outcomes.append(event["receipt"])
                cases.append(dict(arm=arm,stage=stage,synthetic_raw=raw,probe=event))
            assert outcomes[0]==outcomes[1],"prediction affected external realized receipt"
    summary=dict(preflight="PASS",actual_model_calls=0,stages=6,synthetic_probes=12,
        constructed_histories={k:[r["consequence"] for r in v["history"]] for k,v in stages.items()},
        histories_match=all([r["consequence"] for r in v["history"]]==EXPECTED[k] for k,v in stages.items()),
        maximum_probe_memory=max(c["probe"]["bounds"]["memory"] for c in cases),
        protected_errors=[],annex_calls=len(plan),annex_sha256=hashlib.sha256(data).hexdigest())
    assert summary["histories_match"] and len(plan)==144
    return dict(summary=summary,stages=stages,cases=cases),data


def main():
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);p.add_argument("--replay",type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    result,annex=run();data=json.dumps(result,sort_keys=True,indent=2).encode()+b"\n"
    (a.output/"preflight.json").write_bytes(data);(a.output/"registered-prompts.json").write_bytes(annex)
    if a.replay:
        assert data==(a.replay/"preflight.json").read_bytes()
        assert annex==(a.replay/"registered-prompts.json").read_bytes()
    print(json.dumps(result["summary"],indent=2))
    print("Preflight SHA256",hashlib.sha256(data).hexdigest())

if __name__=="__main__":main()
