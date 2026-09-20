import unittest
from .checks import Synthetic
from .runtime import Broker,setup,step
from .protocol import schedule,SYSTEMS
from .preflight import check
from .analysis import summarize,C
from experiments.model_map_proposal_v0.adapter import parse


class StudyTests(unittest.TestCase):
    def test_zero_call_gate_and_genuine_callback(self):
        gate=check();self.assertEqual(gate['projection_contexts'],288)
        self.assertEqual(len(gate['initial_episodes']),12);self.assertEqual(gate['actual_model_calls'],0)

    def test_schema_still_rejects_strings_and_extra_authority(self):
        for raw in ('{"next_state":1,"consequence":"K2"}',
                    '{"next_state":1,"consequence":"0"}',
                    '{"next_state":1,"consequence":true}',
                    '{"next_state":1,"consequence":0,"status":"AUTHORIZED"}'):
            with self.assertRaises(ValueError):parse(raw)

    def test_recovery_call_without_authorization_does_not_satisfy_G(self):
        b=Broker(Synthetic('Recovery','{}'));row=step(setup('V2_INVALID_RECOVERY_TEST'),b,schedule()[0],0)
        result,_=summarize([row],b.calls,[])
        self.assertEqual(result['Recovery']['calls'],1)
        self.assertFalse(result['live_path_coverage']['G_genuine_live_recovery_reaches_authorizer'])
        self.assertEqual(result['live_eligible_classification'],C)
        self.assertEqual(result['committed_events'],0)

    def test_legal_wrong_recovery_reaches_authorizer_and_rejects(self):
        b=Broker(Synthetic('Recovery','{"replacement_state":2}'));row=step(setup('V2_WRONG_RECOVERY_TEST'),b,schedule()[0],0)
        result,_=summarize([row],b.calls,[])
        self.assertTrue(result['live_path_coverage']['G_genuine_live_recovery_reaches_authorizer'])
        self.assertEqual(result['Recovery']['wrong_rejected'],1)
        self.assertEqual(row['probe']['before'],row['probe']['after'])
        self.assertEqual(result['classification'],C)

    def test_same_episode_history_is_consumed_and_no_unknown_record(self):
        class Hold(Synthetic):
            def generate(self,call):
                out=super().generate(call)
                if call['role']=='Explorer':out['raw_output']='K2'
                return out
        b=Broker(Hold());bundle=setup('V2_HISTORY_TEST');rows=[step(bundle,b,schedule()[0],d) for d in range(2)]
        result,chains=summarize(rows,b.calls,[])
        self.assertEqual(result['committed_events'],2)
        for key in ('C_later_decision_after_commit','D_live_explorer_absence_to_evidence','E_live_map_empty_to_same_pair_history','F_later_proposal_consumes_same_episode_memory'):
            self.assertTrue(result['live_path_coverage'][key])
        self.assertEqual(result['unknown_to_known_transitions'],1)
        self.assertTrue(all(c['structured_projection_exact'] for c in chains['request_projection_audit']))
        self.assertIsNone(result['integrity_requirements']['exact_replay_passes'])


if __name__=='__main__':unittest.main()
