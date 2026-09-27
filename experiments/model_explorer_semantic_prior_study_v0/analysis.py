"""Descriptive analysis of choices against authorized pre-decision evidence only."""

from collections import Counter,defaultdict
from .adapter import ACTIONS
from .campaign import RELATIONS,STATES


def evaluate(row):
    d=row["descriptor"];memory=row["authority_input_state"]["memory"]
    scores={}
    for action in d["underlying_option_order"]:
        values=[r["consequence"] for r in memory if r["pre_state"]==d["state"] and r["action"]==action]
        assert values
        scores[action]=sum(values)/len(values)
    winner=max(scores,key=scores.get)
    assert sum(v==scores[winner] for v in scores.values())==1
    action=row["parsed_action"];surface=row["model_call"]["parsed_surface_proposal"]
    return dict(index=d["index"],seed_index=d["seed_index"],state=d["state"],relation=d["relation"],
        condition=d["condition"],action=action,surface=surface,scores=scores,winner=winner,
        higher_selected=action==winner,selected_value=scores.get(action),
        selected_position=d["surface_option_order"].index(surface)+1 if surface in d["surface_option_order"] else None,
        winner_position=d["underlying_option_order"].index(winner)+1,
        surface_order=d["surface_option_order"],mapping=d["surface_to_underlying"])


def rate(hits,n):return dict(selected=hits,opportunities=n,rate=hits/n if n else None)


def cell(rows):
    n=len(rows);valid=sum(r["action"] is not None for r in rows)
    return dict(calls=n,valid=valid,invalid=n-valid,value_following=rate(sum(r["higher_selected"] for r in rows),n),
        selected_values={str(v):sum(r["selected_value"]==v for r in rows) for v in (-1,0,1)},
        underlying_actions={a:sum(r["action"]==a for r in rows) for a in ACTIONS},
        surface_tokens=dict(Counter(r["surface"] for r in rows if r["surface"] is not None)),
        higher_selection_by_best_position={str(p):rate(
            sum(r["higher_selected"] for r in rows if r["winner_position"]==p),
            sum(r["winner_position"]==p for r in rows)) for p in (1,2,3)},
        positions={str(p):rate(sum(r["selected_position"]==p for r in rows),sum(len(r["surface_order"])>=p for r in rows)) for p in (1,2,3)})


def contrast(rows,gate,test_effect=True):
    arms={a:cell([r for r in rows if r["condition"]==a]) for a in ("S","O")}
    paired=defaultdict(dict)
    for r in rows:paired[r["seed_index"],r["state"],r["relation"]][r["condition"]]=r
    pairs=[]
    for key,v in sorted(paired.items()):
        assert set(v)=={"S","O"}
        s,o=v["S"],v["O"]
        pairs.append(dict(seed_index=key[0],state=key[1],relation=key[2],winner=s["winner"],
            S_action=s["action"],O_action=o["action"],S_higher=s["higher_selected"],O_higher=o["higher_selected"],
            changed_underlying=s["action"] is not None and o["action"] is not None and s["action"]!=o["action"]))
    delta=arms["S"]["value_following"]["rate"]-arms["O"]["value_following"]["rate"]
    sh=sum(p["S_higher"] and not p["O_higher"] for p in pairs)
    oh=sum(p["O_higher"] and not p["S_higher"] for p in pairs)
    supported=test_effect and gate and abs(delta)>=.20 and (sh if delta>0 else oh)>=8
    return dict(arms=arms,delta_S_minus_O=delta,S_favored_discordance=sh,O_favored_discordance=oh,
        concordant=len(pairs)-sh-oh,changed_underlying=sum(p["changed_underlying"] for p in pairs),
        semantic_prior_effect=("SUPPORTED" if supported else "NOT_ESTABLISHED") if test_effect else "DESCRIPTIVE_ONLY",
        direction=(("semantic labels helped" if delta>0 else "semantic labels hurt") if supported else "no established effect") if test_effect else "descriptive comparison only",
        strong_value_following={a:bool(gate and arms[a]["value_following"]["rate"]>=.8) for a in ("S","O")},pairs=pairs)


def summarize(rows,setup_count):
    measured=[r for r in rows if r["role"]=="measured"]
    controls=[r for r in rows if r["role"]=="control"]
    evaluated=[evaluate(r) for r in measured]
    violations=Counter(v for r in rows for v in r["violations"])
    real=sum(not r["model_call"]["response_metadata"].get("synthetic",False) for r in measured)
    valid=sum(r["parsed_action"] is not None for r in measured)
    integrity=not violations and all(r["projection_verified"] for r in rows)
    complete=len(measured)==288 and len(controls)==48 and setup_count==1680
    gate=integrity and complete and real==288 and valid==288
    relations={name:contrast([r for r in evaluated if r["relation"]==name],gate,test_effect=name!="three_way") for name,values in RELATIONS}
    winner_identity=[];by_state=[];position=[]
    for relation,values in RELATIONS:
        for condition in ("S","O"):
            chosen=[r for r in evaluated if r["relation"]==relation and r["condition"]==condition]
            for action in ACTIONS:
                selected=[r for r in chosen if r["winner"]==action]
                winner_identity.append(dict(relation=relation,condition=condition,winner=action,**cell(selected)))
            for state in STATES:
                selected=[r for r in chosen if r["state"]==state]
                by_state.append(dict(relation=relation,condition=condition,state=state,**cell(selected)))
            conditional=[]
            for p in range(1,4 if relation=="three_way" else 3):
                selected=[r for r in chosen if r["winner_position"]==p]
                conditional.append(dict(best_position=p,**rate(sum(r["higher_selected"] for r in selected),len(selected))))
            rates=[x["rate"] for x in conditional if x["rate"] is not None]
            gap=max(rates)-min(rates)
            position.append(dict(relation=relation,condition=condition,raw=cell(chosen)["positions"],
                higher_selection_by_best_position=conditional,range=gap,strong_descriptive_association=gap>=.20))
    exposures=[]
    for r in evaluated:
        if r["condition"]!="O":continue
        for pos,token in enumerate(r["surface_order"],1):
            exposures.append(dict(relation=r["relation"],state=r["state"],token=token,
                value=r["scores"][r["mapping"][token]],position=pos,selected=r["surface"]==token))
    def exposure_table(fields):
        groups=defaultdict(list)
        for row in exposures:groups[tuple(row[k] for k in fields)].append(row)
        return [dict(zip(fields,key),**rate(sum(x["selected"] for x in group),len(group))) for key,group in sorted(groups.items())]
    token_value=exposure_table(("relation","value","token"));token_flags=[]
    for rel,vals in RELATIONS:
        for val in vals:
            group=[r for r in token_value if r["relation"]==rel and r["value"]==val]
            assert len(group)==3
            gap=max(r["rate"] for r in group)-min(r["rate"] for r in group)
            token_flags.append(dict(relation=rel,value=val,range=gap,token_asymmetry=gap>=.20))
    retreat=[r for r in evaluated if r["state"]==3 and r["relation"] in ("positive_over_neutral","positive_over_negative","three_way")]
    other_retreat=[r for r in evaluated if r["state"]==1 and r["relation"]=="neutral_over_negative"]
    return dict(framework_integrity="PASS" if integrity else "FAIL",violations=dict(violations),
        measured_calls=len(measured),real_model_calls=real,valid_proposals=valid,invalid_proposals=len(measured)-valid,
        measured_commits=sum(r["authorization"]["committed"] for r in measured),
        controls=len(controls),control_executions=sum(r["authorization"]["executed"] for r in controls),
        control_commits=sum(r["authorization"]["committed"] for r in controls),
        control_parse_failures=dict(Counter(r["model_call"]["parse_failure"] for r in controls)),
        setup_transactions=setup_count,projection_checks=sum(r["projection_verified"] for r in rows),
        matched_state_checks=sum(r["pair_verified"] for r in rows),complete=complete,support_gate=gate,
        relations=relations,winner_identity=winner_identity,by_state=by_state,
        retreat_best_positive=contrast(retreat,gate),retreat_best_offered_neutral=contrast(other_retreat,False,test_effect=False),
        position_effects=position,opaque_token_marginals=exposure_table(("token",)),
        opaque_token_by_value=token_value,opaque_token_by_position=exposure_table(("token","position")),
        opaque_token_strata=exposure_table(("relation","state","value","position","token")),opaque_token_flags=token_flags,
        maxima={k:max(r["bounds"][k] for r in rows) for k in rows[0]["bounds"]})
