"""Frozen exact-outcome criteria, separate consequence/state descriptive scores."""
from collections import Counter
from .campaign import FAMILIES, LENGTHS

OLD=dict(next_state=1,consequence=1)
NEW=dict(next_state=1,consequence=-1)


def summarize(rows,controls):
    errors=Counter(e for r in rows for e in r["probe"]["errors"])
    integrity=not errors and all(r["history_retained"] for r in rows)
    valid=sum(r["valid"] for r in rows)
    latched=all(r["probe"]["latched_before_execution"] for r in rows if r["valid"])
    receipt_ok=all(r["probe"]["receipt_unchanged"] and not any(e in r["probe"]["errors"] for e in ("protected_false_accept","receipt_mismatch_accept")) for r in rows)
    global_gate=len(rows)==valid==144 and integrity and latched and receipt_ok
    families={}
    for family in FAMILIES:
        selected=[r for r in rows if r["descriptor"]["family"]==family]
        cells={};lookup={}
        for arm in ("CONTROL","SHIFT"):
            for stage in LENGTHS:
                cell=[r for r in selected if r["descriptor"]["arm"]==arm and r["descriptor"]["stage"]==stage]
                predictions=[r["model_call"]["parsed_prediction"] for r in cell]
                counts=Counter("invalid" if p is None else f"{p['next_state']},{p['consequence']}" for p in predictions)
                cells[arm+"/"+stage]=dict(observed=len(cell),registered_denominator=12,
                    exact_predictions=dict(sorted(counts.items())),invalid=sum(p is None for p in predictions),
                    old_exact=predictions.count(OLD),new_exact=predictions.count(NEW),
                    consequences={str(c):sum(p is not None and p["consequence"]==c for p in predictions) for c in (-1,0,1)},
                    exact_outcome_accuracy=sum(r["model_call"]["parsed_prediction"]==r["evaluator_outcome"] for r in cell),
                    next_state_accuracy=sum(p is not None and p["next_state"]==1 for p in predictions),
                    consequence_accuracy=sum(p is not None and p["consequence"]==(1 if arm=="CONTROL" else -1) for p in predictions),
                    prediction_receipt_mismatches=sum(r["valid"] and r["probe"]["measurement_matches"] is False for r in cell))
                for r in cell:lookup[(arm,stage,r["descriptor"]["schedule_id"])]=r["model_call"]["parsed_prediction"]
        paired=[dict(schedule_id=j,control=lookup.get(("CONTROL","H2",j)),shift=lookup.get(("SHIFT","H2",j))) for j in range(12)]
        favorable=sum(p["control"]==OLD and p["shift"]==NEW for p in paired)
        reverse=sum(p["control"]==NEW and p["shift"]==OLD for p in paired)
        criteria=dict(shift_h0_old=cells["SHIFT/H0"]["old_exact"]>=10,
            shift_h2_new=cells["SHIFT/H2"]["new_exact"]>=9,
            control_h2_old=cells["CONTROL/H2"]["old_exact"]>=9,
            favorable_pairs=favorable>=8,reverse_pairs=reverse<=1,
            all_144_complete_valid=len(rows)==valid==144,framework_integrity=integrity,
            latched_before_execution=latched,actual_commits_equal_receipts=receipt_ok)
        families[family]=dict(cells=cells,matched_h2=paired,h2_favorable=favorable,h2_reverse=reverse,
            trajectories=[dict(schedule_id=j,arm=arm,**{stage:lookup.get((arm,stage,j)) for stage in LENGTHS})
                          for j in range(12) for arm in ("CONTROL","SHIFT")],
            criteria=criteria,revision="SUPPORTED" if all(criteria.values()) else "NOT_ESTABLISHED")
    return dict(real_model_calls=len(rows),registered_calls=144,valid_proposals=valid,
        invalid_proposals=len(rows)-valid,complete=len(rows)==144,framework_integrity="PASS" if integrity else "FAIL",
        global_behavioral_gate=global_gate,error_counts=dict(errors),
        protected_false_accepts=errors["protected_false_accept"],receipt_mismatch_accepts=errors["receipt_mismatch_accept"],
        unauthorized_commits=errors["provenance_failure"],stale_duplicate_authorizations=sum(r["probe"]["metric_delta"].get("duplicate_authorizations",0) for r in rows),
        malformed_prediction_commits=errors["malformed_prediction_commit"],direct_protected_mutations=errors["direct_protected_mutation"],
        post_execution_prediction_rewrites=errors["prediction_rewrite"],historical_receipt_rewrites=errors["historical_receipt_rewrite"],bound_violations=errors["bound_violation"],
        probe_commits=sum(r["probe"]["authorization"]["committed"] for r in rows),
        predictions_latched_before_execution=sum(r["probe"]["latched_before_execution"] for r in rows),
        prediction_receipt_mismatches=sum(r["valid"] and r["probe"]["measurement_matches"] is False for r in rows),
        map_quarantines=sum(o["kind"]=="map_quarantine" for r in rows for o in r["probe"]["observations"]),
        recovery_proposals=dict(Counter(o["kind"] for r in rows for o in r["probe"]["observations"])),
        state_recovery_authorizations=sum(r["probe"]["authorization"]["recovery_authorized"] for r in rows),
        old_histories_preserved=sum(r["history_retained"] for r in rows),
        maxima={k:max((r["probe"]["bounds"][k] for r in rows),default=0) for k in ("memory","pairs","packages","trace","pending_authentic","map_quarantine","memory_quarantine")},
        parser_controls=len(controls),parser_control_commits=sum(r["probe"]["authorization"]["committed"] for r in controls),
        families=families,overall="CONTRADICTION-DRIVEN MAP REVISION REPLICATED" if all(f["revision"]=="SUPPORTED" for f in families.values()) else "CONTRADICTION-DRIVEN MAP REVISION NOT ESTABLISHED")
