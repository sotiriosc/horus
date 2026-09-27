"""Synthetic correctness checks; no generated model behavior."""

from collections import Counter
import copy
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .adapter import ACTIONS,parse_surface
from .campaign import FAMILIES,TARGETS,registration,execute,verify_projection
from .analysis import summarize,evaluate,contrast,position_metrics,classify
from .run import run_campaign,source_hashes
from experiments.model_explorer_semantic_prior_study_v0.test_study import SyntheticValueFollower,SyntheticInvalid


class FactorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registered,cls.data=registration();cls.rows=[];cls.setup=[]
        execute(SyntheticValueFollower(),cls.rows.append,cls.setup.append,cls.registered)

    def test_authorized_targets_and_exact_annex(self):
        for target,state,values in TARGETS:
            f=self.registered["fixtures"][str(state)]
            self.assertEqual(f["verified_outcomes"]["RETREAT"],[values[0]])
            self.assertEqual(f["verified_outcomes"]["HOLD" if target=="A" else "ADVANCE"],[values[1]])
            self.assertEqual(len(f["setup_rows"]),5)
            self.assertTrue(all(r["authorization"]["committed"] and not r["violations"] for r in f["setup_rows"]))
        self.assertEqual(len(self.registered["plan"]),216)

    def test_full_independent_mapping_option_evidence_crossing(self):
        plan=self.registered["plan"]
        for target,state,values in TARGETS:
            for family in FAMILIES:
                group=[d for d in plan if d["target"]==target and d["condition"]==family]
                self.assertEqual(Counter((d["seed_index"],d["higher_option_position"],d["higher_evidence_position"]) for d in group),
                                 {key:1 for key in itertools.product(range(6),(1,2),(1,2))})
                self.assertTrue(all(set(d["surface_to_underlying"].values())==set(ACTIONS) for d in group))
                if family!="S":
                    exposed=Counter((t,a,d["surface_option_order"].index(t)+1,d["surface_evidence_order"].index(t)+1)
                        for d in group for t,a in d["surface_to_underlying"].items() if t in d["surface_option_order"])
                    self.assertEqual(len(exposed),24)
                    self.assertEqual(set(exposed.values()),{2})
            for op,ep in itertools.product((1,2),(1,2)):
                group=[d for d in plan if d["target"]==target and d["higher_option_position"]==op and d["higher_evidence_position"]==ep]
                self.assertEqual(len(set(tuple(d["condition"] for d in group[i:i+3]) for i in range(0,18,3))),6)

    def test_all_surface_parsers_and_bounded_rejection_controls(self):
        for d in self.registered["plan"]:
            for t in d["surface_option_order"]:self.assertEqual(parse_surface(' '+t+'\n',d),(t,d["surface_to_underlying"][t],None))
            omitted=next(t for t in d["surface_to_underlying"] if t not in d["surface_option_order"])
            self.assertEqual(parse_surface(omitted,d)[2],"out_of_pair")
            if d["condition"]!="S":
                self.assertTrue(all(a not in d["exact_prompt"] for a in ACTIONS))
                self.assertTrue(all(parse_surface(a,d)[1] is None for a in ACTIONS))
        controls=[r for r in self.rows if r["role"]=="control"]
        self.assertEqual(len(controls),14)
        self.assertEqual(Counter(r["control"] for r in controls),dict(canonical_in_opaque=2,unknown_alias=3,omitted_action=3,multiple_labels=3,explanatory_text=3))
        self.assertTrue(all(not r["authorization"]["executed"] and not r["authorization"]["committed"] for r in controls))

    def test_end_to_end_counts_and_synthetic_never_supports_real_claim(self):
        s=summarize(self.rows,len(self.setup))
        self.assertEqual((s["measured_calls"],s["real_model_calls"],s["setup_transactions"]),(216,0,1150))
        self.assertEqual((s["projection_checks"],s["matched_triples"]),(230,72))
        self.assertEqual(s["violations"],{})
        self.assertFalse(s["support_gate"])
        self.assertEqual(len(s["opaque_token_strata"]),144)
        self.assertEqual({r["opportunities"] for r in s["opaque_token_strata"]},{2})
        for target in s["targets"].values():
            for f in target["families"].values():self.assertEqual(f["higher"]["selected"],24)

    def test_invalid_real_standins_rejected_without_mutation(self):
        rows=[];setup=[];execute(SyntheticInvalid(),rows.append,setup.append,self.registered)
        self.assertTrue(all(not r["authorization"]["executed"] and not r["authorization"]["committed"] and r["authority_input_state"]==r["after"] for r in rows))
        self.assertFalse(summarize(rows,len(setup))["support_gate"])

    def test_evidence_order_facts_and_translation_tampering_detected(self):
        original=next(r for r in self.rows if r["descriptor"]["condition"]=="O1" and r["descriptor"]["evidence_relative_order"]=="reversed")
        d=original["descriptor"];setup=self.registered["fixtures"][str(d["state"])]["setup_rows"]
        self.assertNotEqual(d["surface_option_order"],d["surface_evidence_order"])
        for kind in ("order","fact","mapping"):
            row=copy.deepcopy(original)
            if kind=="order":row["model_call"]["model_visible_input"]["VERIFIED_PRIOR_OUTCOMES"].reverse()
            if kind=="fact":row["model_call"]["model_visible_input"]["VERIFIED_PRIOR_OUTCOMES"][0]["observed_consequences"]=[99]
            if kind=="mapping":row["model_call"]["parsed_action"]="WRONG"
            with self.assertRaises(AssertionError):verify_projection(row,setup,d)
        with self.assertRaises(AssertionError):verify_projection(original,[],d)

    def test_classifications_separate_option_evidence_value_and_conjunction(self):
        original=[evaluate(r) for r in self.rows if r["role"]=="measured" and r["descriptor"]["target"]=="C" and r["descriptor"]["condition"]=="O1"]
        for pattern,expected in (("option","OPTION_POSITION_DOMINATES"),("evidence","EVIDENCE_POSITION_DOMINATES"),("value","VERIFIED_VALUE_DOMINATES"),("aligned","CONJUNCTION_EFFECT")):
            rows=copy.deepcopy(original)
            for r in rows:
                higher=(r["higher_option_position"]==1 if pattern=="option" else r["higher_evidence_position"]==1 if pattern=="evidence" else r["higher_option_position"]==r["higher_evidence_position"] if pattern=="aligned" else True)
                r["higher_selected"]=higher
                r["first_option_selected"]=(r["higher_option_position"]==1)==higher
                r["first_evidence_selected"]=(r["higher_evidence_position"]==1)==higher
            p=position_metrics(rows,True)
            self.assertEqual(classify(p,True)["classifications"],[expected])
            self.assertEqual(classify(p,False)["classifications"],["UNRESOLVED"])
            if pattern in ("option","evidence"):
                self.assertEqual(p[pattern]["effect"],"SUPPORTED")
                self.assertEqual(p["evidence" if pattern=="option" else "option"]["effect"],"NOT_ESTABLISHED")
        # Four successes per cell cannot meet a five-of-six classification.
        p=position_metrics(original,True)
        for c in p["crossed"]:c["higher"]["selected"]=4
        self.assertEqual(classify(p,True)["classifications"],["UNRESOLVED"])

    def test_eight_discordances_and_both_opaque_families_required(self):
        evaluated=[evaluate(r) for r in self.rows if r["role"]=="measured" and r["descriptor"]["target"]=="A"]
        for n,status in ((7,"NOT_ESTABLISHED"),(8,"SUPPORTED")):
            rows=copy.deepcopy(evaluated)
            for r in [r for r in rows if r["family"]=="S"][:n]:r["higher_selected"]=False
            self.assertEqual(contrast(rows,"S","O1",True)["effect"],status)
            self.assertEqual(contrast(rows,"S","O1",False)["effect"],"NOT_ESTABLISHED")
        rows=copy.deepcopy(self.rows)
        for r in rows:
            if r["role"]=="measured":r["model_call"]["response_metadata"]["synthetic"]=False
            if r["role"]=="measured" and r["descriptor"]["condition"]=="S":
                ev=evaluate(r);loser=min(ev["scores"],key=ev["scores"].get)
                r["parsed_action"]=loser;r["model_call"]["parsed_surface_proposal"]=loser
        self.assertEqual(summarize(rows,len(self.setup))["retreat_lexical_replication"],"SUPPORTED")
        for r in rows:
            if r["role"]=="measured" and r["descriptor"]["condition"]=="O2":
                ev=evaluate(r);loser=min(ev["scores"],key=ev["scores"].get)
                r["parsed_action"]=loser;r["model_call"]["parsed_surface_proposal"]=next(t for t,a in ev["mapping"].items() if a==loser)
        self.assertEqual(summarize(rows,len(self.setup))["retreat_lexical_replication"],"NOT_ESTABLISHED")

    def test_public_cli_exact_replay_without_inference(self):
        root=Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/"source";source.mkdir();output=Path(directory)/"replay"
            summary=run_campaign(SyntheticValueFollower(),source,self.registered,self.data,progress=False)
            (source/"results.json").write_text(json.dumps(dict(summary=summary,source_sha256=source_hashes(root)),indent=2)+'\n')
            r=subprocess.run([sys.executable,"-m","experiments.model_explorer_prior_factorial_v1.run","--replay",str(source/'model-calls.jsonl'),"--output",str(output)],cwd=root,env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertIn("Exact replay:",r.stdout)


if __name__=="__main__":unittest.main()
