"""Authorized fixture construction, frozen scheduling, and test-side observers."""

import hashlib
import itertools
import json
from pathlib import Path
from unittest.mock import patch

from experiments.model_explorer_integration_v0 import campaign as previous
from experiments.model_explorer_integration_v0.adapter import ACTIONS, ForcedOutput
from experiments.base_framework_v2.framework import EvidenceProvenanceFramework
from experiments.base_framework_v1.hidden_oracle import TrueWorldOracle
from .adapter import SYSTEM, SurfaceAdapter

STATES=(0,1,3)
SETUP=("ADVANCE","RETREAT","HOLD","RETREAT","ADVANCE")
PERMUTATIONS=tuple(itertools.permutations(ACTIONS))
ORDER_INDICES=(0,1,5,2,3,4)
RELATIONS=(("neutral_over_negative",(0,-1)),("positive_over_neutral",(1,0)),
           ("positive_over_negative",(1,-1)),("three_way",(1,0,-1)))


def fresh(state,epoch):
    episode=previous.Episode(epoch,lambda row:None)
    episode.system=EvidenceProvenanceFramework(initial_state=state,epoch=epoch)
    episode.world=TrueWorldOracle(initial_state=state)
    return episode


def fixture(state):
    e=fresh(state,800+state);rows=[]
    for action in SETUP:
        row=e.step("model",ForcedOutput(action),0,role="fixture_setup")
        assert row["authorization"]["committed"] and not row["violations"]
        rows.append(row)
    assert e.system.map.current.state==state
    return e,rows


def plan(fixtures):
    calls=[]
    for j in range(12):
        for state_index,state in enumerate(STATES):
            f=fixtures[str(state)]
            for relation_index,(relation,values) in enumerate(RELATIONS):
                scores={a:sum(v)/len(v) for a,v in f["verified_outcomes"].items()}
                offered=[a for a in ACTIONS if scores[a] in values]
                if relation=="three_way":
                    offered=list(PERMUTATIONS[ORDER_INDICES[j%6]])
                if j>=6:offered.reverse()
                mapping=dict(zip(("K1","K2","K3"),PERMUTATIONS[j%6]))
                for condition in (("S","O") if (j+state_index+relation_index)%2==0 else ("O","S")):
                    aliases={a:a for a in ACTIONS} if condition=="S" else {a:t for t,a in mapping.items()}
                    payload=dict(state=state,available_actions=[aliases[a] for a in offered],
                        VERIFIED_PRIOR_OUTCOMES=[dict(surface_action=aliases[a],observed_consequences=f["verified_outcomes"][a]) for a in offered])
                    calls.append(dict(index=len(calls),seed_index=j,state=state,relation=relation,condition=condition,
                        seed=20001+j,mapping_permutation=j%6,surface_to_underlying={v:k for k,v in aliases.items()},
                        underlying_option_order=offered,surface_option_order=[aliases[a] for a in offered],
                        decision_number=6,system=SYSTEM,payload=payload,exact_prompt=json.dumps(payload,sort_keys=True,separators=(",",":"))))
    return calls


def registration():
    probes=[]
    for state in range(4):
        for action in ACTIONS:
            e=fresh(state,800+state)
            row=e.step("model",ForcedOutput(action),0,role="fixture_preflight")
            assert row["authorization"]["committed"] and not row["violations"]
            probes.append(row)
    fixtures={}
    for state in STATES:
        e,rows=fixture(state)
        protected=previous.protected_state(e.system)
        values={a:[r["consequence"] for r in protected["memory"] if r["pre_state"]==state and r["action"]==a] for a in ACTIONS}
        assert all(len(v)==1 for v in values.values()) and {v[0] for v in values.values()}=={-1,0,1}
        fixtures[str(state)]=dict(initial_state=state,epoch=800+state,setup_actions=list(SETUP),setup_rows=rows,
            protected_state=protected,verified_outcomes=values,decision_number=6)
    result=dict(fixtures=fixtures,plan=plan(fixtures),preflight_probes=probes)
    data=(json.dumps(result,indent=2)+"\n").encode()
    expected=json.loads((Path(__file__).parent/"registration-digests.json").read_text())["registered_annex_sha256"]
    assert hashlib.sha256(data).hexdigest()==expected,"prospective fixture/prompt annex changed"
    return result,data


def verify_projection(row,setup,descriptor):
    call=row["model_call"];shown=call["model_visible_input"];before=row["authority_input_state"]
    assert shown["state"]==before["map"]["state"]==descriptor["state"]
    assert set(shown)=={"state","available_actions","VERIFIED_PRIOR_OUTCOMES"}
    records=[r for r in before["memory"] if r["pre_state"]==shown["state"]]
    assert records==call["authorized_relevant_records"]
    for record in before["memory"]:
        assert record["authorization"]=="AUTHORIZED"
        assert any(s["authorization"]["committed"] and all(s["world_event"][k]==record[k] for k in
            ("epoch","transaction_id","pre_state","action","next_state","consequence")) for s in setup)
    expected=[]
    for token in descriptor["surface_option_order"]:
        underlying=descriptor["surface_to_underlying"][token]
        values=[r["consequence"] for r in records if r["action"]==underlying]
        assert values
        expected.append(dict(surface_action=token,observed_consequences=values))
    assert shown["available_actions"]==descriptor["surface_option_order"]
    assert shown["VERIFIED_PRIOR_OUTCOMES"]==expected
    assert shown==descriptor["payload"] and call["exact_prompt"]==descriptor["exact_prompt"]
    assert call["system"]==SYSTEM and call["surface_to_underlying"]==descriptor["surface_to_underlying"]
    if descriptor["condition"]=="O":
        assert not any(a in call["exact_prompt"] for a in ACTIONS)
    if call["parsed_action"] is not None:
        assert call["parsed_surface_proposal"] in shown["available_actions"]
        assert descriptor["surface_to_underlying"][call["parsed_surface_proposal"]]==call["parsed_action"]==row["parsed_action"]
    else:
        assert not row["authorization"]["executed"] and not row["authorization"]["committed"]
    old={(r["epoch"],r["transaction_id"]):r for r in before["memory"]}
    for r in row["after"]["memory"]:
        if (r["epoch"],r["transaction_id"]) in old:assert r==old[r["epoch"],r["transaction_id"]]
    return True


def execute(transport,emit,emit_setup,registered=None):
    registered=registered or registration()[0];rows=[];matched={}
    def run(descriptor,chosen,role,control=None):
        e,setup=fixture(descriptor["state"])
        expected=registered["fixtures"][str(descriptor["state"])]
        assert setup==expected["setup_rows"]
        assert previous.protected_state(e.system)==expected["protected_state"]
        for s in setup:emit_setup(dict(descriptor=descriptor,role=role,control=control,step=s))
        def factory(*args,**kwargs):return SurfaceAdapter(*args,**kwargs,descriptor=descriptor)
        with patch.object(previous,"ModelExplorerAdapter",factory):
            row=e.step("model",chosen,descriptor["seed"] if role=="measured" else 0,role=role,label=descriptor["condition"])
        row["descriptor"]=descriptor;row["control"]=control
        try:row["projection_verified"]=verify_projection(row,setup,descriptor)
        except AssertionError as error:
            row["projection_verified"]=False;row["violations"].append("projection_or_mapping_integrity: "+str(error))
        if role=="control" and (row["authorization"]["executed"] or row["authorization"]["committed"]):
            row["violations"].append("invalid_control_executed_or_committed")
        row["pair_verified"]=False
        if role=="measured":
            key=descriptor["seed_index"],descriptor["state"],descriptor["relation"]
            if key in matched:
                other=matched.pop(key)
                assert row["authority_input_state"]==other["authority_input_state"]
                assert descriptor["underlying_option_order"]==other["descriptor"]["underlying_option_order"]
                assert row["model_call"]["options"]==other["model_call"]["options"]
                row["pair_verified"]=True
            else:matched[key]=row
        rows.append(row);emit(row)
        if row["violations"]:raise RuntimeError("integrity failed")
    for descriptor in registered["plan"]:run(descriptor,transport,"measured")
    assert not matched
    for descriptor in registered["plan"]:
        if descriptor["seed_index"]!=0:continue
        missing=next((t for t in descriptor["surface_to_underlying"] if t not in descriptor["surface_option_order"]),"FLY")
        for name,output in (("unoffered_or_unknown",missing),("malformed","not a single option")):
            run(descriptor,ForcedOutput(output),"control",name)
    return rows
