"""Pure grader checks; oracle objects are test-only and never Qwen input/output."""
import importlib.util,unittest,copy
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('study',P/'run_study.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
def oracle_a():
 m=s.read('architecture-manifest.json');g=s.read('authority-graph.json')
 return dict(self_model=dict(active_architecture={k:g[k] for k in ('ordered_decision_layers','rollback_component','model_route_position')},components=[dict(component_id=c['component_id'],status=c['status'],role=c['role'],can_select_action=c['can_select_action'],can_execute_world=c['can_execute_world'],can_write_memory=c['can_write_memory'],uses_model_when_triggered=c['uses_model_call_when_triggered'],evidence_ids=c['source_ids']) for c in m['components']],authority_distinctions=g['distinctions'],failure_behavior=g['failure_behavior'],uncertainties=[]),mandatory_distinction=dict(is_grounded_mechanical_authority_the_same_component_as_S=False,explanation='Grounded mechanical authority resolves established relations; S is distinct deterministic stagnation escape.',evidence_ids=['SRC-ROUTING','SRC-S']))
def oracle_b():return dict(cases=[dict(case_id=c['case_id'],**c['expected'],evidence_ids=['SRC-SELECTOR']) for c in s.read('routing-cases.json')['cases']])
class GraderTests(unittest.TestCase):
 def test_exact_oracles_pass(self):
  self.assertEqual(s.audit('A',oracle_a())['status'],'PASS');self.assertEqual(s.audit('B',oracle_b())['status'],'PASS')
 def test_each_authority_boolean_flip_fails(self):
  for i in range(10):
   for key in ('can_select_action','can_execute_world','can_write_memory','uses_model_when_triggered'):
    x=oracle_a();x['self_model']['components'][i][key]=not x['self_model']['components'][i][key]
    self.assertEqual(s.audit('A',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
 def test_distinction_and_order_are_hard_gates(self):
  x=oracle_a();x['mandatory_distinction']['is_grounded_mechanical_authority_the_same_component_as_S']=True
  self.assertEqual(s.audit('A',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
  x=oracle_a();x['self_model']['authority_distinctions'][1]['relationship']='SAME_COMPONENT'
  self.assertEqual(s.audit('A',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
  x=oracle_a();x['self_model']['active_architecture']['ordered_decision_layers'].reverse()
  self.assertEqual(s.audit('A',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
 def test_invented_id_and_rollback_fail(self):
  x=oracle_a();x['self_model']['components'][0]['evidence_ids']=['SRC-INVENTED']
  self.assertEqual(s.audit('A',x)['status'],'FAIL')
  x=oracle_a();x['self_model']['active_architecture']['rollback_component']='ORDINARY_MODEL_ROUTE'
  self.assertEqual(s.audit('A',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
 def test_every_routing_error_is_material(self):
  for i in range(20):
   x=oracle_b();x['cases'][i]['model_called']=not x['cases'][i]['model_called']
   self.assertEqual(s.audit('B',x)['classification'],'AGENT_SELF_MODEL_GROUNDING_FAILED')
 def test_no_quote_contract(self):
  self.assertEqual(s.audit('A',oracle_a())['quote_comparisons'],0)
if __name__=='__main__':unittest.main()
