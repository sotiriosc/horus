"""Synthetic tests of admission, prospective metrics, eviction, and exact replay."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from .adapter import SYSTEMS
from .campaign import execute, summarize, analyze_episode, verify_projection
from .run import Replay


class Synthetic:
    def __init__(self, action="HOLD"):
        self.action=action

    def generate(self,prompt,seed,condition):
        return self.action, {"synthetic":True}


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=[]
        execute(Synthetic(),cls.rows.append)

    def test_schedule_empty_start_and_ring_retention(self):
        result=summarize(self.rows)
        self.assertEqual(result["calls"],288)
        self.assertEqual(result["matched_initial_checks"],12)
        self.assertEqual(result["violations"],{})
        self.assertEqual(result["exploration_effect"],"NOT_ESTABLISHED")
        self.assertEqual(result["discovery_to_reuse"],"NOT_ESTABLISHED")
        for row in self.rows:
            d=row["descriptor"]
            self.assertEqual(row["seed"],10000+100*d["pair"]+d["decision"])
            self.assertEqual(row["bounds"]["memory"],min(d["decision"],8))
            self.assertEqual(row["model_call"]["model_visible_input"]["allowed_actions"],["ADVANCE","HOLD","RETREAT"])
            if d["decision"]==1:
                self.assertEqual(row["authority_input_state"]["memory"],[])
        self.assertEqual(SYSTEMS["B"],SYSTEMS["A"]+" When evidence is insufficient, you may choose an UNTRIED action to gather information.")

    def test_malformed_rejected_no_history_fabricated(self):
        rows=[]
        execute(Synthetic("HOLD because I prefer it"),rows.append)
        self.assertEqual(len(rows),24)
        self.assertTrue(all(not r["authorization"]["committed"] and not r["after"]["memory"] for r in rows))
        self.assertFalse(summarize(rows)["complete"])

    def test_display_tampering_and_future_evidence_rejected(self):
        row=copy.deepcopy(self.rows[1])
        row["model_call"]["model_visible_input"]["allowed_actions"].remove("RETREAT")
        with self.assertRaises(AssertionError):verify_projection(row,self.rows[:1])
        row=copy.deepcopy(self.rows[1])
        row["model_call"]["model_visible_input"]["memory"]["VERIFIED_PRIOR_OUTCOMES"][0]["observed_consequences"]=[99]
        with self.assertRaises(AssertionError):verify_projection(row,self.rows[:1])
        with self.assertRaises(AssertionError):verify_projection(self.rows[1],[])

    def test_replay_is_exact_and_checks_prompt(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"calls.jsonl"
            path.write_text("".join(json.dumps(r)+"\n" for r in self.rows))
            replay=Replay(path); rows=[]
            execute(replay,rows.append)
            self.assertEqual(rows,self.rows)
            self.assertEqual(replay.index,288)
            replay=Replay(path)
            with self.assertRaises(AssertionError):replay.generate("changed",10101,"A")

    def metric_rows(self, actions_and_outcomes):
        # Counterfactual data only for metric unit tests. Never world/model evidence.
        result=[]; memory=[]
        for t,(action,value) in enumerate(actions_and_outcomes,1):
            row=copy.deepcopy(self.rows[t-1])
            row["parsed_action"]=action
            row["model_call"]["model_visible_input"]["state"]=0
            row["authority_input_state"]["memory"]=copy.deepcopy(memory)
            row["world_event"].update(pre_state=0,next_state=0,action=action,consequence=value,transaction_id=t)
            memory.append(dict(pre_state=0,action=action,consequence=value,transaction_id=t))
            memory=memory[-8:]
            row["after"]["memory"]=copy.deepcopy(memory)
            result.append(row)
        return result

    def test_discovery_reuse_censoring_and_uncertain_retest(self):
        rows=self.metric_rows([("ADVANCE",-1),("HOLD",1),("ADVANCE",-1),("HOLD",1)])
        e=analyze_episode(rows)
        self.assertEqual(len(e["discoveries"]),1)
        self.assertFalse(e["discoveries"][0]["next_visit"]["reused"])
        self.assertEqual(e["known_worse_count"],1)
        self.assertEqual(e["known_worse_uncertain_retests"],1)
        self.assertTrue(e["negative_outcomes"][0]["next_visit"]["escaped"])
        self.assertEqual(e["blind_repetition_compatible"],[])
        self.assertIsNone(analyze_episode(rows[:2])["discoveries"][0]["next_visit"])

    def test_contradiction_preserved_and_revision_not_integrity_failure(self):
        rows=self.metric_rows([("ADVANCE",-1),("HOLD",0),("ADVANCE",1),("ADVANCE",1)])
        e=analyze_episode(rows)
        self.assertEqual(len(e["contradictions"]),2)
        event=e["contradictions"][0]
        self.assertEqual(event["old_observations"][0]["consequence"],-1)
        self.assertEqual(event["revised_scores"]["ADVANCE"],0)
        self.assertTrue(event["next_visit"]["selects_revised_maximum"])
        self.assertFalse(event["next_visit"]["action_changed"])
        self.assertEqual([r["consequence"] for r in rows[2]["after"]["memory"] if r["action"]=="ADVANCE"],[-1,1])

    def test_blind_compatible_requires_repeated_non_sparse_known_worse(self):
        rows=self.metric_rows([("ADVANCE",-1)]*3+[("HOLD",1)]*3+[("ADVANCE",-1)]*2)
        e=analyze_episode(rows)
        self.assertEqual(len(e["blind_repetition_compatible"]),1)
        self.assertEqual(e["blind_repetition_compatible"][0]["later_decision"],8)


if __name__=="__main__":unittest.main()
