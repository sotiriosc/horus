"""Synthetic tests only; never represented as real model observations."""

from collections import Counter
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .adapter import ACTIONS,parse_surface
from .campaign import STATES,RELATIONS,registration,execute,fixture,verify_projection
from .analysis import summarize,evaluate,contrast
from .run import run_campaign,source_hashes


class SyntheticValueFollower:
    def generate(self,prompt,seed):
        entries=json.loads(prompt)["VERIFIED_PRIOR_OUTCOMES"]
        best=max(entries,key=lambda r:sum(r["observed_consequences"])/len(r["observed_consequences"]))
        return best["surface_action"],{"synthetic":True}


class SyntheticInvalid:
    def generate(self,prompt,seed):return "not a single option",{"synthetic":True}


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registered,cls.data=registration();cls.rows=[];cls.setup=[]
        execute(SyntheticValueFollower(),cls.rows.append,cls.setup.append,cls.registered)

    def test_authorized_fixtures_and_exact_registered_annex(self):
        for state in STATES:
            e,rows=fixture(state)
            self.assertEqual(rows,self.registered["fixtures"][str(state)]["setup_rows"])
            self.assertEqual((e.system.map.current.state,e.system.map.current.version,e.system.next_transaction_id),(state,5,6))
            self.assertEqual(len(e.system.memory.records),5)
        self.assertEqual(len(self.registered["plan"]),288)

    def test_mapping_order_and_matching_balance(self):
        for state in STATES:
            for relation,values in RELATIONS:
                cell=[d for d in self.registered["plan"] if d["state"]==state and d["relation"]==relation]
                opaque=[d for d in cell if d["condition"]=="O"]
                self.assertEqual(Counter(d["mapping_permutation"] for d in opaque),dict.fromkeys(range(6),2))
                token_positions=Counter((token,pos) for d in opaque for pos,token in enumerate(d["surface_option_order"],1))
                self.assertEqual(set(token_positions.values()),{4})
                underlying_positions=Counter((a,pos) for d in opaque for pos,a in enumerate(d["underlying_option_order"],1))
                self.assertEqual(set(underlying_positions.values()),{4 if relation=="three_way" else 6})
                for j in range(12):
                    pair=[d for d in cell if d["seed_index"]==j]
                    self.assertEqual(len(pair),2)
                    self.assertEqual(pair[0]["underlying_option_order"],pair[1]["underlying_option_order"])
                    self.assertEqual(pair[0]["seed"],pair[1]["seed"])
                self.assertEqual(sum(cell[i]["condition"]=="S" for i in range(0,24,2)),6)

    def test_all_mapping_bijections_and_out_of_pair_rejection(self):
        for d in self.registered["plan"]:
            self.assertEqual(set(d["surface_to_underlying"].values()),set(ACTIONS))
            for token in d["surface_option_order"]:
                self.assertEqual(parse_surface(" "+token+"\n",d),(token,d["surface_to_underlying"][token],None))
            for token in set(d["surface_to_underlying"])-set(d["surface_option_order"]):
                self.assertEqual(parse_surface(token,d),(None,None,"out_of_pair"))
            if d["condition"]=="O":
                self.assertTrue(all(parse_surface(a,d)[1] is None for a in ACTIONS))
                self.assertTrue(all(a not in d["exact_prompt"] for a in ACTIONS))

    def test_end_to_end_synthetic_campaign_and_controls(self):
        result=summarize(self.rows,len(self.setup))
        self.assertEqual(result["real_model_calls"],0)
        self.assertEqual(result["measured_calls"],288)
        self.assertEqual(result["controls"],48)
        self.assertEqual(result["control_executions"],0)
        self.assertEqual(result["control_commits"],0)
        self.assertEqual(result["setup_transactions"],1680)
        self.assertEqual(result["matched_state_checks"],144)
        self.assertEqual(result["projection_checks"],336)
        self.assertEqual(result["violations"],{})
        self.assertEqual(result["control_parse_failures"],dict(out_of_pair=18,malformed_or_unknown_label=30))
        for comparison in result["relations"].values():
            self.assertEqual(comparison["delta_S_minus_O"],0)
            self.assertEqual(comparison["arms"]["S"]["value_following"]["selected"],36)
            self.assertEqual(comparison["arms"]["O"]["value_following"]["selected"],36)

    def test_invalid_measured_proposals_never_execute(self):
        rows=[];setup=[]
        execute(SyntheticInvalid(),rows.append,setup.append,self.registered)
        self.assertEqual(len(rows),336)
        self.assertTrue(all(not r["authorization"]["executed"] and not r["authorization"]["committed"] for r in rows))
        self.assertTrue(all(r["authority_input_state"]==r["after"] for r in rows))
        self.assertFalse(summarize(rows,len(setup))["support_gate"])

    def test_projection_or_mapping_tampering_detected(self):
        original=next(r for r in self.rows if r["descriptor"]["condition"]=="O")
        d=original["descriptor"];setup=self.registered["fixtures"][str(d["state"])]["setup_rows"]
        row=copy.deepcopy(original)
        row["model_call"]["model_visible_input"]["VERIFIED_PRIOR_OUTCOMES"][0]["observed_consequences"]=[99]
        with self.assertRaises(AssertionError):verify_projection(row,setup,d)
        row=copy.deepcopy(original);row["model_call"]["parsed_action"]="WRONG"
        with self.assertRaises(AssertionError):verify_projection(row,setup,d)
        with self.assertRaises(AssertionError):verify_projection(original,[],d)

    def test_registered_effect_threshold_and_descriptive_only_boundary(self):
        rows=[evaluate(r) for r in self.rows if r["role"]=="measured" and r["descriptor"]["relation"]=="neutral_over_negative"]
        for changed,expected in ((7,"NOT_ESTABLISHED"),(8,"SUPPORTED")):
            altered=copy.deepcopy(rows)
            for row in [r for r in altered if r["condition"]=="O"][:changed]:
                row["higher_selected"]=False
                row["action"]=min(row["scores"],key=row["scores"].get)
            result=contrast(altered,True)
            self.assertEqual(result["semantic_prior_effect"],expected)
            self.assertEqual(result["S_favored_discordance"],changed)
            self.assertEqual(contrast(altered,False)["semantic_prior_effect"],"NOT_ESTABLISHED")
            self.assertEqual(contrast(altered,True,test_effect=False)["semantic_prior_effect"],"DESCRIPTIVE_ONLY")

    def test_public_cli_exact_replay_without_inference(self):
        root=Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/"source";source.mkdir();output=Path(directory)/"replay"
            summary=run_campaign(SyntheticValueFollower(),source,self.registered,self.data,progress=False)
            (source/"results.json").write_text(json.dumps(dict(summary=summary,source_sha256=source_hashes(root)),indent=2)+"\n")
            result=subprocess.run([sys.executable,"-m","experiments.model_explorer_semantic_prior_study_v0.run",
                "--replay",str(source/"model-calls.jsonl"),"--output",str(output)],cwd=root,
                env={**os.environ,"PYTHONDONTWRITEBYTECODE":"1"},capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn("Exact replay:",result.stdout)


if __name__=="__main__":unittest.main()
