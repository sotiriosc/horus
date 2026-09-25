"""Frozen factorial schedule and test-side authorized projection observers."""

import hashlib
import itertools
import json
from pathlib import Path
from unittest.mock import patch

from experiments.model_explorer_integration_v0 import campaign as previous
from experiments.model_explorer_integration_v0.campaign import protected_state
from experiments.model_explorer_integration_v0.adapter import ACTIONS, ForcedOutput
from experiments.model_explorer_semantic_prior_study_v0.campaign import fixture
from .adapter import SYSTEM, SurfaceAdapter

FAMILIES={'S':ACTIONS,'O1':('K1','K2','K3'),'O2':('Q7','M4','Z2')}
TARGETS=(('A',3,(1,0)),('B',3,(1,-1)),('C',1,(0,-1)))
PERMUTATIONS=tuple(itertools.permutations(ACTIONS))
FAMILY_ORDERS=tuple(itertools.permutations(FAMILIES))

def build():
 fixtures={}
 for state in (1,3):
  e,rows=fixture(state);protected=protected_state(e.system)
  values={a:[r['consequence'] for r in protected['memory'] if r['pre_state']==state and r['action']==a] for a in ACTIONS}
  assert all(len(v)==1 for v in values.values())
  fixtures[str(state)]=dict(state=state,epoch=800+state,setup_rows=rows,protected_state=protected,verified_outcomes=values,decision_number=6)
 for target,state,values in TARGETS:
  f=fixtures[str(state)]['verified_outcomes']
  assert f['RETREAT']==[values[0]]
  assert f['HOLD' if target=='A' else 'ADVANCE']==[values[1]]
 calls=[]
 for j in range(6):
  for ti,(target,state,values) in enumerate(TARGETS):
   f=fixtures[str(state)];scores={a:sum(v)/len(v) for a,v in f['verified_outcomes'].items()}
   higher=[a for a in ACTIONS if scores[a]==values[0]];lower=[a for a in ACTIONS if scores[a]==values[1]]
   assert len(higher)==len(lower)==1
   for op in (1,2):
    order=higher+lower if op==1 else lower+higher
    for ri,relative in enumerate(('same','reversed')):
     evidence=order if relative=='same' else list(reversed(order))
     for family in FAMILY_ORDERS[(j+ti+2*(op-1)+ri)%6]:
      mapping=dict(zip(FAMILIES[family],ACTIONS if family=='S' else PERMUTATIONS[j]))
      inverse={a:t for t,a in mapping.items()}
      payload=dict(state=state,available_actions=[inverse[a] for a in order],VERIFIED_PRIOR_OUTCOMES=[dict(surface_action=inverse[a],observed_consequences=f['verified_outcomes'][a]) for a in evidence])
      calls.append(dict(index=len(calls),seed_index=j,seed=30001+j,target=target,state=state,condition=family,
       mapping_permutation=None if family=='S' else j,surface_to_underlying=mapping,underlying_option_order=order,
       surface_option_order=payload['available_actions'],underlying_evidence_order=evidence,surface_evidence_order=[inverse[a] for a in evidence],
       higher_option_position=op,higher_evidence_position=evidence.index(higher[0])+1,evidence_relative_order=relative,
       decision_number=6,system=SYSTEM,payload=payload,exact_prompt=json.dumps(payload,sort_keys=True,separators=(',',':'))))
 controls=[]
 for family in FAMILIES:
  d=next(d for d in calls if d['target']=='C' and d['condition']==family and d['seed_index']==0 and d['higher_option_position']==1 and d['evidence_relative_order']=='reversed')
  a,b=d['surface_option_order'];missing=next(t for t in d['surface_to_underlying'] if t not in (a,b))
  outputs=[('unknown_alias','X9'),('omitted_action',missing),('multiple_labels',a+' '+b),('explanatory_text',a+' because it is better')]
  if family!='S':outputs.insert(0,('canonical_in_opaque','RETREAT'))
  controls.extend(dict(descriptor_index=d['index'],name=name,output=raw) for name,raw in outputs)
 return dict(fixtures=fixtures,plan=calls,controls=controls)



def registration():
    result=build();data=(json.dumps(result,indent=2)+"\n").encode()
    expected=json.loads((Path(__file__).parent/"registration-digests.json").read_text())["registered_annex_sha256"]
    assert hashlib.sha256(data).hexdigest()==expected,"registered fixtures/prompts changed"
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
    for token in descriptor["surface_evidence_order"]:
        underlying=descriptor["surface_to_underlying"][token]
        values=[r["consequence"] for r in records if r["action"]==underlying]
        assert values
        expected.append(dict(surface_action=token,observed_consequences=values))
    assert shown["available_actions"]==descriptor["surface_option_order"]
    assert shown["VERIFIED_PRIOR_OUTCOMES"]==expected
    assert shown==descriptor["payload"] and call["exact_prompt"]==descriptor["exact_prompt"]
    assert call["system"]==SYSTEM and call["surface_to_underlying"]==descriptor["surface_to_underlying"]
    if descriptor["condition"]!="S":
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
        assert protected_state(e.system)==expected["protected_state"]
        for s in setup:emit_setup(dict(descriptor=descriptor,role=role,control=control,step=s))
        def factory(*args,**kwargs):return SurfaceAdapter(*args,**kwargs,descriptor=descriptor)
        with patch.object(previous,"ModelExplorerAdapter",factory):
            row=e.step("model",chosen,descriptor["seed"] if role=="measured" else 0,
                       role=role,label=descriptor["condition"])
        row["descriptor"]=descriptor;row["control"]=control
        try:row["projection_verified"]=verify_projection(row,setup,descriptor)
        except AssertionError as error:
            row["projection_verified"]=False
            row["violations"].append("projection_or_mapping_integrity: "+str(error))
        if role=="control" and (row["authorization"]["executed"] or row["authorization"]["committed"]):
            row["violations"].append("invalid_control_executed_or_committed")
        row["triple_verified"]=False
        if role=="measured":
            key=(descriptor["seed_index"],descriptor["target"],descriptor["higher_option_position"],
                 descriptor["evidence_relative_order"])
            group=matched.setdefault(key,[])
            for other in group:
                assert row["authority_input_state"]==other["authority_input_state"]
                for field in ("underlying_option_order","underlying_evidence_order","seed","decision_number"):
                    assert descriptor[field]==other["descriptor"][field]
                assert row["model_call"]["options"]==other["model_call"]["options"]
            group.append(row)
            if len(group)==3:
                assert {r["descriptor"]["condition"] for r in group}==set(FAMILIES)
                row["triple_verified"]=True;del matched[key]
        rows.append(row);emit(row)
        if row["violations"]:raise RuntimeError("integrity failed")
    for descriptor in registered["plan"]:run(descriptor,transport,"measured")
    assert not matched
    for control in registered["controls"]:
        run(registered["plan"][control["descriptor_index"]],ForcedOutput(control["output"]),"control",control["name"])
    return rows

