import copy,itertools,random,unittest
from dsl import *
from worlds import history_signature,messages,Hypotheses
class SimulatorTests(unittest.TestCase):
 def trace(self,e,actions):
  m=Circuit([e]);s=m.initial;out=[m.observation(s)[0]]
  for a in actions:s,o=m.step(s,a);out.append(o[0])
  return out
 def test_old_register_new_input_delay_semantics(self):
  self.assertEqual(self.trace(('delay',2,('input',0)),[0,0,0,0]),[0,0,0,1,0])
 def test_latch_reset_priority_and_previous_state(self):
  self.assertEqual(self.trace(('latch',('input',0),('input',1)),[0,1,1,1]),[0,0,1,0,1])
 def test_counter_threshold_and_wrap(self):
  self.assertEqual(self.trace(('counter',3,2,('input',0)),[0,1,1,1]),[0,0,0,1,0])
 def test_inactive_branch_registers_also_update(self):
  e=('select',('input',0),('delay',1,('input',1)),('delay',1,('input',2)))
  self.assertEqual(self.trace(e,[1,0]),[0,0,1])
 def test_independent_interpreter_every_declared_root(self):
  rng=random.Random(988);actions=[rng.randrange(N_INPUTS) for _ in range(28)]
  for c in catalog():self.assertEqual(self.trace(c['expression'],actions),[o[0] for o in reference([c['expression']],actions)])
 def test_reference_continuation_matches_uninterrupted(self):
  roots=[('xor',('counter',3,2,('input',0)),('delay',2,('latch',('input',1),('input',2))))];actions=[0,1,2,3,1,2,0,2,1]
  full=reference(roots,actions);a,state=reference(roots,actions[:4],return_state=True);b=reference(roots,actions[4:],state=state);self.assertEqual(full,a+b[1:])
 def test_program_isomorphism_under_port_renaming(self):
  roots=[('and',('delay',1,('input',0)),('input',1)),('or',('input',2),('input',3))];perm=(2,3,1,0);other=[normalize(e,perm) for e in reversed(roots)]
  self.assertEqual(program_signature(roots),program_signature(other));self.assertEqual(behavior_signature(roots),behavior_signature(other))
 def test_behavior_normalization_catches_redundant_program(self):
  a=[('input',0)];b=[('or',('input',0),('input',0))]
  self.assertNotEqual(program_signature(a),program_signature(b));self.assertEqual(behavior_signature(a),behavior_signature(b))
 def test_longer_relevant_delay_is_different_behavior(self):
  self.assertNotEqual(behavior_signature([('delay',1,('input',0))]),behavior_signature([('delay',2,('input',0))]))
 def test_history_normalization_strips_names_and_sensor_order(self):
  a=dict(actuators=['A1','B2','C3','D4'],sensors=['Z0','Y0'],history=[['RESET','00'],['A1','10'],['C3','01']],candidate_action='D4')
  b=dict(actuators=['K0','L0','M0','N0'],sensors=['R0','Q0'],history=[['RESET','00'],['K0','01'],['M0','10']],candidate_action='N0')
  self.assertEqual(history_signature(a),history_signature(b));b['candidate_action']='L0';self.assertEqual(history_signature(a),history_signature(b)) # both unused actuator roles are symmetric
  b['candidate_action']='K0';self.assertNotEqual(history_signature(a),history_signature(b))
 def test_exhaustive_checker_rejects_genuinely_ambiguous_query(self):
  h=Hypotheses.__new__(Hypotheses);h.roots=[('and',('delay',1,('input',0)),('input',1)),('or',('delay',1,('input',0)),('input',1))];h.tables={};h.schedules=[((2,2),1)]
  self.assertIsNone(h.check(0,[(0,0,0,0)]*3))
  h.tables={};h.schedules=[((0,2),1)];result=h.check(0,[(0,0,0,0)]*3)
  self.assertEqual(result['values'],[1]*4)
 def test_program_fields_cannot_enter_message_builder(self):
  visible=dict(actuators=[],sensors=[],history=[],candidate_action='x',program='secret')
  with self.assertRaises(AssertionError):messages(visible)
if __name__=='__main__':unittest.main()
