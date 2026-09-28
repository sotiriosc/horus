"""Pure pre-inference rule checks; no model or world execution."""
import unittest
from .analyze import expected_escape,independent_suffix
from .worker import scenario_override

def view(kind,consequence=None):
    return dict(kind=kind,relation_type='DETERMINISTIC',
        established_value=None if consequence is None else dict(next_state=0,consequence=consequence))

def fallback(index,state=0,action='HOLD',consequence=0,next_state=0,unseen=True):
    assessments=dict(ADVANCE=view('UNSEEN') if unseen else view('ESTABLISHED',-1),
        HOLD=view('ESTABLISHED',0),RETREAT=view('UNSEEN'))
    return dict(index=index,state=state,selected_action=action,
        decision_source='SAFE_GROUNDED_FALLBACK',policy_route='MODEL',
        action_parse_status='VALID',grounded_assessments_before=assessments,
        realized=dict(next_state=next_state,consequence=consequence))

class CandidateRuleTests(unittest.TestCase):
    def test_third_fallback_triggers_first_unseen(self):
        history=[fallback(i) for i in range(1,4)]
        self.assertEqual(independent_suffix(history),(3,(0,'HOLD')))
        self.assertEqual(expected_escape(history,0,history[-1]['grounded_assessments_before']),("ADVANCE",3))

    def test_reset_and_no_trigger_controls(self):
        history=[fallback(1),fallback(2),fallback(3,next_state=1)]
        self.assertEqual(independent_suffix(history),(0,None))
        good=[fallback(i) for i in range(1,4)]
        plus=good[-1]['grounded_assessments_before'].copy();plus['ADVANCE']=view('ESTABLISHED',1)
        self.assertEqual(expected_escape(good,0,plus)[0],None)
        grounded={a:view('ESTABLISHED',0 if a=='HOLD' else -1) for a in ('ADVANCE','HOLD','RETREAT')}
        self.assertEqual(expected_escape(good,0,grounded)[0],None)
        self.assertEqual(expected_escape(good,1,good[-1]['grounded_assessments_before'])[0],None)

    def test_world_cases_are_driver_only(self):
        self.assertEqual(scenario_override('B',0,'ADVANCE',1,8),(0,-1))
        self.assertEqual(scenario_override('C',0,'ADVANCE',1,8),(0,1))
        self.assertEqual(scenario_override('D',0,'ADVANCE',1,8),(0,0))
        self.assertIsNone(scenario_override('B',0,'ADVANCE',1,7))
        self.assertEqual(scenario_override('G',0,'HOLD',2,1),(1,0))

if __name__=='__main__':unittest.main()
