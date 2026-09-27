"""Zero-inference tests for OPTION_PROFILE_DOMINANCE."""
from copy import deepcopy
import hashlib,inspect,json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .core import digest
from .option_profile import EXPECTED_PROVENANCE,compare_profiles,reconstruct_profiles
from .problem_manager import POLICY,ProblemManager,decision_scope

def profile(*sequences):
    return [dict(rank=i+1,second_action=("ADVANCE","HOLD","RETREAT")[i],
        sequence=list(value),provenance=deepcopy(EXPECTED_PROVENANCE))
        for i,value in enumerate(sequences)]

def problem(pid,request):
    return dict(problem_id=pid,problem_type="UNRESOLVED_VALUE_TIE",
        scope=decision_scope(2,["ADVANCE","RETREAT"]),owner="EVIDENCE_COVERAGE",
        lifecycle_state="REASSESSED",capability_assessment="CURRENT_OBJECTIVE_CANNOT_DISTINGUISH",
        requested_capability=request,created_decision_sequence=1,route_budgets={},route_request_count=0,
        probe_evidence={},evidence=[],imported_snapshot={},imported_snapshot_sha256=digest({}),history=[],
        **{k:False for k in POLICY["manager_authority"]})

class OptionProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path=Path(__file__).resolve().parents[1]/"research/deeper-horizon-route-design-v0/results.json"
        cls.source=json.loads(cls.path.read_text()); cls.profiles=reconstruct_profiles(cls.source)
    def test_01_complete_multiset_retained(self):
        self.assertEqual({k:len(v) for k,v in self.profiles.items()},{"ADVANCE":3,"RETREAT":3})
        self.assertEqual({r["second_action"] for r in self.profiles["ADVANCE"]},
                         {"ADVANCE","HOLD","RETREAT"})
    def test_02_duplicate_trajectories_preserved(self):
        values=[r["sequence"] for r in self.profiles["RETREAT"]]
        self.assertEqual(values.count([1,1,1]),2)
    def test_03_sorting_is_deterministic(self):
        self.assertEqual(self.profiles,reconstruct_profiles(self.source))
        self.assertEqual([r["sequence"] for r in self.profiles["ADVANCE"]],
                         [[1,1,1],[1,0,1],[1,-1,1]])
    def test_04_trajectory_order_is_lexicographic(self):
        p={"ADVANCE":profile((1,1,-1),(1,0,1),(0,1,1)),
           "RETREAT":profile((1,0,1),(1,0,0),(0,1,1))}
        self.assertEqual(compare_profiles(p)["rank_comparisons"][0]["relation"],"ADVANCE_GREATER")
    def test_05_dominance_requires_no_worse_at_every_rank(self):
        p={"ADVANCE":profile((1,1,1),(1,0,1),(1,-1,1)),
           "RETREAT":profile((1,1,1),(1,1,1),(1,0,1))}
        self.assertEqual(compare_profiles(p)["outcome"],"RETREAT_PROFILE_DOMINATES")
    def test_06_dominance_requires_strict_improvement(self):
        p=profile((1,1,1),(1,0,1),(1,-1,1))
        self.assertEqual(compare_profiles({"ADVANCE":p,"RETREAT":deepcopy(p)})["outcome"],"PROFILES_EQUAL")
    def test_07_identical_profiles_remain_tied(self):
        p=profile((1,1,1),(1,0,1),(1,-1,1))
        self.assertIsNone(compare_profiles({"ADVANCE":p,"RETREAT":deepcopy(p)})["selected_action"])
    def test_08_crossing_profiles_are_incomparable(self):
        a=profile((1,1,1),(1,0,0),(1,0,0)); b=profile((1,0,1),(1,1,1),(1,-1,1))
        self.assertEqual(compare_profiles({"ADVANCE":a,"RETREAT":b})["outcome"],"PROFILES_INCOMPARABLE")
    def test_09_no_scalar_value_generated(self):
        result=compare_profiles(self.profiles); self.assertIsNone(result["scalar_value"])
        source=inspect.getsource(compare_profiles)
        self.assertNotIn("sum(",source); self.assertNotIn("weight",source); self.assertNotIn("discount",source)
    def test_10_no_hidden_world_information(self):
        visible=set().union(*(row.keys() for rows in self.profiles.values() for row in rows))
        self.assertEqual(visible,{"rank","current_action","second_action","sequence","provenance"})
    def test_11_only_permitted_forecasts_used(self):
        self.assertTrue(all(row["provenance"]["c1"]==row["provenance"]["c2"]=="MODEL_FORECAST"
            for rows in self.profiles.values() for row in rows))
    def test_12_grounded_and_predicted_provenance_preserved(self):
        self.assertTrue(all(row["provenance"]==EXPECTED_PROVENANCE
            for rows in self.profiles.values() for row in rows))
    def test_13_representation_cannot_replace_global_explorer(self):
        import horus.option_profile as module
        source=inspect.getsource(module)
        self.assertNotIn("GroundedExplorer",source); self.assertNotIn("MechanicalExplorer",source)
    def test_14_pr0003_remains_unchanged(self):
        with TemporaryDirectory() as d:
            p2=problem("PR-0002","ALTERNATIVE_VALUE_REPRESENTATION")
            p3=problem("PR-0003",None); p3["scope"]=decision_scope(1,["ADVANCE","HOLD"])
            manager=ProblemManager.create(Path(d),session_id="s",attempted_decisions=85,
                authorized_executions=54,imported_problems=[p2,p3],edges=[])
            try:
                before=deepcopy(manager.state["problems"]["PR-0003"])
                manager.authorize_option_profile("PR-0002","a"*64)
                manager.record_option_profile(problem_id="PR-0002",outcome="RETREAT_PROFILE_DOMINATES",
                    selected_action="RETREAT",evaluation={})
                self.assertEqual(manager.state["problems"]["PR-0003"],before)
            finally: manager.close()
    def test_15_v015_evidence_is_byte_identical(self):
        root=self.path.parent; manifest=json.loads((root/"evidence-manifest.json").read_text())
        for name,expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),expected)

if __name__=="__main__": unittest.main()
