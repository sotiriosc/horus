"""Preregistered descriptive rates and crossed-position classifications."""

from collections import Counter,defaultdict
from .adapter import ACTIONS
from .campaign import FAMILIES,TARGETS


def rate(hits,n):return dict(selected=hits,opportunities=n,rate=hits/n if n else None)


def evaluate(row):
    d=row["descriptor"];memory=row["authority_input_state"]["memory"]
    scores={}
    for action in d["underlying_option_order"]:
        values=[r["consequence"] for r in memory if r["pre_state"]==d["state"] and r["action"]==action]
        assert values
        scores[action]=sum(values)/len(values)
    winner=max(scores,key=scores.get)
    assert len(scores)==2 and len(set(scores.values()))==2
    surface=row["model_call"]["parsed_surface_proposal"];action=row["parsed_action"]
    return dict(index=d["index"],seed_index=d["seed_index"],target=d["target"],state=d["state"],
        family=d["condition"],action=action,surface=surface,winner=winner,scores=scores,
        higher_selected=action==winner,selected_value=scores.get(action),
        higher_option_position=d["underlying_option_order"].index(winner)+1,
        higher_evidence_position=d["underlying_evidence_order"].index(winner)+1,
        first_option_selected=surface==d["surface_option_order"][0],
        first_evidence_selected=surface==d["surface_evidence_order"][0],
        option_order=d["surface_option_order"],evidence_order=d["surface_evidence_order"],
        mapping=d["surface_to_underlying"])


def cell(rows):
    n=len(rows)
    return dict(calls=n,valid=sum(r["action"] is not None for r in rows),
        invalid=sum(r["action"] is None for r in rows),
        higher=rate(sum(r["higher_selected"] for r in rows),n),
        first_option=rate(sum(r["first_option_selected"] for r in rows),n),
        first_evidence=rate(sum(r["first_evidence_selected"] for r in rows),n),
        selected_values={str(v):sum(r["selected_value"]==v for r in rows) for v in (-1,0,1)},
        underlying_actions={a:sum(r["action"]==a for r in rows) for a in ACTIONS},
        surface_tokens=dict(Counter(r["surface"] for r in rows if r["surface"] is not None)))


def contrast(rows,left,right,gate):
    arms={a:cell([r for r in rows if r["family"]==a]) for a in (left,right)}
    groups=defaultdict(dict)
    for r in rows:
        if r["family"] in (left,right):
            groups[(r["seed_index"],r["target"],r["higher_option_position"],r["higher_evidence_position"])][r["family"]]=r
    pairs=[]
    for key,g in sorted(groups.items()):
        assert set(g)=={left,right}
        l,r=g[left],g[right]
        pairs.append(dict(seed_index=key[0],target=key[1],higher_option_position=key[2],higher_evidence_position=key[3],
            left_action=l["action"],right_action=r["action"],left_higher=l["higher_selected"],right_higher=r["higher_selected"]))
    lh=sum(p["left_higher"] and not p["right_higher"] for p in pairs)
    rh=sum(p["right_higher"] and not p["left_higher"] for p in pairs)
    delta=arms[right]["higher"]["rate"]-arms[left]["higher"]["rate"]
    support=bool(gate and abs(delta)>=.20 and (rh if delta>0 else lh)>=8)
    return dict(left=left,right=right,arms=arms,delta_right_minus_left=delta,
        left_favored_discordance=lh,right_favored_discordance=rh,concordant=len(pairs)-lh-rh,
        changed_underlying=sum(p["left_action"] is not None and p["right_action"] is not None and p["left_action"]!=p["right_action"] for p in pairs),
        effect="SUPPORTED" if support else "NOT_ESTABLISHED",
        direction=(right+" better" if delta>0 else left+" better") if support else "not established",pairs=pairs)


def position_metrics(rows,gate):
    crossed=[]
    for op in (1,2):
        for ep in (1,2):
            group=[r for r in rows if r["higher_option_position"]==op and r["higher_evidence_position"]==ep]
            crossed.append(dict(higher_option_position=op,higher_evidence_position=ep,**cell(group)))
    effects={}
    for factor,other in (("option","evidence"),("evidence","option")):
        marginal=[dict(position=p,**cell([r for r in rows if r["higher_"+factor+"_position"]==p])) for p in (1,2)]
        delta=marginal[0]["higher"]["rate"]-marginal[1]["higher"]["rate"]
        strata=[]
        for pos in (1,2):
            strata.append(dict(other_position=pos,delta_first_minus_second=
                next(c for c in crossed if c["higher_"+factor+"_position"]==1 and c["higher_"+other+"_position"]==pos)["higher"]["rate"]-
                next(c for c in crossed if c["higher_"+factor+"_position"]==2 and c["higher_"+other+"_position"]==pos)["higher"]["rate"]))
        supported=bool(gate and abs(delta)>=.20 and all((x["delta_first_minus_second"] if delta>0 else -x["delta_first_minus_second"])>=.20 for x in strata))
        effects[factor]=dict(marginal=marginal,delta_first_minus_second=delta,stratified=strata,
            effect="SUPPORTED" if supported else "NOT_ESTABLISHED",
            favored_position=(1 if delta>0 else 2) if supported else None)
    p={(c["higher_option_position"],c["higher_evidence_position"]):c["higher"]["rate"] for c in crossed}
    interaction=p[1,1]+p[2,2]-p[1,2]-p[2,1]
    return dict(crossed=crossed,**effects,interaction=interaction,agreement_difference=interaction/2)


def classify(positions,gate):
    c=positions["crossed"];labels=[];alignment=None
    if gate:
        for metric,label in (("first_option","OPTION_POSITION_DOMINATES"),("first_evidence","EVIDENCE_POSITION_DOMINATES"),("higher","VERIFIED_VALUE_DOMINATES")):
            if all(x[metric]["selected"]>=5 and x[metric]["opportunities"]==6 for x in c):labels.append(label)
        aligned=[x for x in c if x["higher_option_position"]==x["higher_evidence_position"]]
        opposed=[x for x in c if x["higher_option_position"]!=x["higher_evidence_position"]]
        for high,low,direction in ((aligned,opposed,"aligned"),(opposed,aligned,"opposed")):
            if all(x["higher"]["selected"]>=5 for x in high) and all(x["higher"]["selected"]<=1 for x in low) and abs(positions["agreement_difference"])>=.5:
                labels.append("CONJUNCTION_EFFECT");alignment=direction
    return dict(classifications=labels or ["UNRESOLVED"],conjunction_favors=alignment)


def summarize(rows,setup_count):
    measured=[r for r in rows if r["role"]=="measured"];controls=[r for r in rows if r["role"]=="control"]
    evaluated=[evaluate(r) for r in measured]
    violations=Counter(v for r in rows for v in r["violations"])
    integrity=not violations and all(r["projection_verified"] for r in rows)
    real=sum(not r["model_call"]["response_metadata"].get("synthetic",False) for r in measured)
    valid=sum(r["parsed_action"] is not None for r in measured)
    control_ok=all(not r["authorization"]["executed"] and not r["authorization"]["committed"] for r in controls)
    complete=len(measured)==216 and len(controls)==14 and setup_count==1150
    gate=bool(complete and real==216 and valid==216 and control_ok and integrity)
    targets={}
    for target,state,values in TARGETS:
        selected=[r for r in evaluated if r["target"]==target];families={}
        for family in FAMILIES:
            group=[r for r in selected if r["family"]==family];pos=position_metrics(group,gate)
            families[family]=dict(**cell(group),positions=pos,strong_value_following=bool(gate and sum(r["higher_selected"] for r in group)>=20),
                stable_across_positions=bool(gate and all(c["higher"]["selected"]>=5 for c in pos["crossed"])))
            if target=="C":families[family]["order_classification"]=classify(pos,gate)
        comparisons={left+"_vs_"+right:contrast(selected,left,right,gate) for left,right in (("S","O1"),("S","O2"),("O1","O2"))}
        lexical=all(comparisons["S_vs_"+f]["effect"]=="SUPPORTED" and comparisons["S_vs_"+f]["delta_right_minus_left"]>0 for f in ("O1","O2"))
        bases=[]
        if comparisons["O1_vs_O2"]["effect"]=="SUPPORTED":bases.append("matched_value_following_difference")
        if target=="C":
            a,b=(set(families[f]["order_classification"]["classifications"])-{"UNRESOLVED"} for f in ("O1","O2"))
            if a and b and not a.intersection(b):bases.append("disjoint_supported_order_classifications")
        targets[target]=dict(state=state,verified_values=list(values),families=families,comparisons=comparisons,
            retreat_lexical_replication=("SUPPORTED" if lexical else "NOT_ESTABLISHED") if target in ("A","B") else "NOT_APPLICABLE",
            opaque_value_replication="SUPPORTED" if all(families[f]["stable_across_positions"] for f in ("O1","O2")) else "NOT_ESTABLISHED",
            all_surface_value_stability="SUPPORTED" if all(families[f]["stable_across_positions"] for f in FAMILIES) else "NOT_ESTABLISHED",
            vocabulary_dependence="OBSERVED" if bases else "NOT_ESTABLISHED",vocabulary_dependence_basis=bases)
    exposures=[]
    for r in evaluated:
        if r["family"]=="S":continue
        for p,t in enumerate(r["option_order"],1):
            a=r["mapping"][t]
            exposures.append(dict(family=r["family"],target=r["target"],token=t,underlying_action=a,value=r["scores"][a],
                option_position=p,evidence_position=r["evidence_order"].index(t)+1,selected=r["surface"]==t))
    def table(fields):
        groups=defaultdict(list)
        for r in exposures:groups[tuple(r[k] for k in fields)].append(r)
        return [dict(zip(fields,key),**rate(sum(r["selected"] for r in group),len(group))) for key,group in sorted(groups.items())]
    token_value=table(("family","target","value","underlying_action","token"));flags=[]
    for family in ("O1","O2"):
        for target,state,values in TARGETS:
            for value in values:
                group=[r for r in token_value if r["family"]==family and r["target"]==target and r["value"]==value]
                assert len(group)==3
                gap=max(r["rate"] for r in group)-min(r["rate"] for r in group)
                flags.append(dict(family=family,target=target,value=value,range=gap,descriptive_token_asymmetry=gap>=.20))
    return dict(framework_integrity="PASS" if integrity else "FAIL",violations=dict(violations),complete=complete,support_gate=gate,
        measured_calls=len(measured),real_model_calls=real,valid_proposals=valid,invalid_proposals=len(measured)-valid,
        measured_commits=sum(r["authorization"]["committed"] for r in measured),controls=len(controls),
        control_executions=sum(r["authorization"]["executed"] for r in controls),control_commits=sum(r["authorization"]["committed"] for r in controls),
        control_results=[dict(family=r["descriptor"]["condition"],name=r["control"],parse_failure=r["model_call"]["parse_failure"],executed=r["authorization"]["executed"],committed=r["authorization"]["committed"]) for r in controls],
        setup_transactions=setup_count,projection_checks=sum(r["projection_verified"] for r in rows),matched_triples=sum(r["triple_verified"] for r in rows),
        targets=targets,retreat_lexical_replication="SUPPORTED" if all(targets[t]["retreat_lexical_replication"]=="SUPPORTED" for t in ("A","B")) else "NOT_ESTABLISHED",
        opaque_token_marginals=table(("family","token")),opaque_token_by_value=token_value,
        opaque_token_by_position=table(("family","token","option_position","evidence_position")),
        opaque_token_strata=table(("family","target","value","underlying_action","option_position","evidence_position","token")),
        opaque_token_flags=flags,maxima={k:max(r["bounds"][k] for r in rows) for k in rows[0]["bounds"]})
