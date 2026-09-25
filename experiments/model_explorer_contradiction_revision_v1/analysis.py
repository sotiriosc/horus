"""Preregistered paired criteria; no pooling or post-hoc H1 threshold."""
from .campaign import FAMILIES, LENGTHS


def summarize(rows, controls):
    integrity=all(not r["probe"]["errors"] and r["history_retained"] for r in rows)
    complete=len(rows)==144
    valid=sum(r["valid"] for r in rows)
    global_gate=integrity and complete and valid==144
    families={}
    for family in FAMILIES:
        selected=[r for r in rows if r["descriptor"]["family"]==family]
        cells={}
        lookup={}
        for arm in ("CONTROL","SHIFT"):
            for stage in LENGTHS:
                cell=[r for r in selected if r["descriptor"]["arm"]==arm and r["descriptor"]["stage"]==stage]
                cells[arm+"/"+stage]={a:sum(r["model_call"]["parsed_action"]==a for r in cell) for a in ("HOLD","ADVANCE")}
                cells[arm+"/"+stage].update(observed=len(cell),registered_denominator=12,
                    invalid=sum(not r["valid"] for r in cell),current_world_correct=sum(r["current_world_correct"] for r in cell))
                for r in cell:lookup[(arm,stage,r["descriptor"]["schedule_id"])]=r["model_call"]["parsed_action"]
        paired=[];transitions=[];latency={"H1":0,"H2":0,"no_observed_switch":0,"initially_advance":0,"initially_invalid_or_missing":0}
        for j in range(12):
            c=lookup.get(("CONTROL","H2",j));s=lookup.get(("SHIFT","H2",j))
            paired.append(dict(schedule_id=j,control=c,shift=s))
            for arm in ("CONTROL","SHIFT"):
                h=[lookup.get((arm,stage,j)) for stage in LENGTHS]
                transitions.append(dict(schedule_id=j,arm=arm,H0=h[0],H1=h[1],H2=h[2],
                    h0_h1_switch=h[0] is not None and h[1] is not None and h[0]!=h[1],
                    h1_h2_switch=h[1] is not None and h[2] is not None and h[1]!=h[2],
                    h0_h2_switch=h[0] is not None and h[2] is not None and h[0]!=h[2]))
            h=[lookup.get(("SHIFT",stage,j)) for stage in LENGTHS]
            key=("initially_advance" if h[0]=="ADVANCE" else "initially_invalid_or_missing" if h[0]!="HOLD"
                 else "H1" if h[1]=="ADVANCE" else "H2" if h[2]=="ADVANCE" else "no_observed_switch")
            latency[key]+=1
        favorable=sum(p["shift"]=="ADVANCE" and p["control"]=="HOLD" for p in paired)
        reverse=sum(p["shift"]=="HOLD" and p["control"]=="ADVANCE" for p in paired)
        criteria=dict(old_preference=cells["SHIFT/H0"]["HOLD"]>=10,
            shift_h2_advance=cells["SHIFT/H2"]["ADVANCE"]>=9,
            control_h2_hold=cells["CONTROL/H2"]["HOLD"]>=9,
            favorable_pairs=favorable>=8,reverse_pairs=reverse<=1,global_gate=global_gate)
        families[family]=dict(cells=cells,h2_favorable=favorable,h2_reverse=reverse,matched_h2=paired,
            transitions=transitions,latency=latency,criteria=criteria,
            revision="SUPPORTED" if all(criteria.values()) else "NOT_ESTABLISHED")
    return dict(real_model_calls=len(rows),registered_calls=144,valid_proposals=valid,complete=complete,
        framework_integrity="PASS" if integrity else "FAIL",global_behavioral_gate=global_gate,
        protected_false_accepts=sum("protected_false_accept" in r["probe"]["errors"] for r in rows),
        receipt_mismatch_accepts=sum("receipt_mismatch_accept" in r["probe"]["errors"] for r in rows),
        prediction_rewrites=sum("prediction_rewritten" in r["probe"]["errors"] for r in rows),
        history_rewrites=sum(not r["history_retained"] for r in rows),
        probe_commits=sum(r["probe"]["authorization"]["committed"] for r in rows),
        probe_contradiction_opportunities=sum(r["probe"].get("contradiction_opportunity",False) for r in rows),
        probe_recovery_authorizations=sum(r["probe"]["authorization"]["recovery_authorized"] for r in rows),
        parser_controls=len(controls),parser_control_commits=sum(r["probe"]["authorization"]["committed"] for r in controls),
        families=families,overall="CONTRADICTION-DRIVEN BEHAVIORAL REVISION REPLICATED" if all(f["revision"]=="SUPPORTED" for f in families.values()) else "CONTRADICTION-DRIVEN BEHAVIORAL REVISION NOT ESTABLISHED")
