"""Pure audit boundary checks; no model, stores or protected fixtures."""
import copy,unittest
from run_study import audit_A
class AuditTests(unittest.TestCase):
 def sample(self):
  return dict(diagnoses=[dict(diagnosis_id='D1',statement='Audit fixture only.',type='EVIDENCE_GAP',current_relevance='Audit fixture only.',evidence_ids=['EVID-SELF-V01'],system_versions_used=['S_PLUS_E_ACTIVE'],already_addressed_by_S=False,already_addressed_by_E=False,observed=[],inferred=[],unknown=[],falsifier='Audit fixture only.',minimum_new_evidence_needed='Audit fixture only.')],no_supported_diagnosis=False)
 def test_empty_valid(self):
  self.assertTrue(audit_A(dict(diagnoses=[],no_supported_diagnosis=True))['empty_answer_consistent'])
 def test_empty_inconsistent(self):
  self.assertFalse(audit_A(dict(diagnoses=[],no_supported_diagnosis=False))['empty_answer_consistent'])
 def test_historical_anchor_fails(self):
  v=self.sample();v['diagnoses'][0].update(evidence_ids=['EVID-QWEN-R128'],system_versions_used=['S_ACTIVE']);r=audit_A(v)
  self.assertEqual(r['diagnoses'][0]['mechanical_status'],'FAIL')
 def test_invented_id_fails(self):
  v=self.sample();v['diagnoses'][0]['evidence_ids'].append('INVENTED');self.assertEqual(audit_A(v)['diagnoses'][0]['mechanical_status'],'FAIL')
 def test_wrong_version_and_solved_flags_fail(self):
  for field,value in [('system_versions_used',['PRE_S']),('already_addressed_by_S',True),('already_addressed_by_E',True)]:
   v=self.sample();v['diagnoses'][0][field]=value;self.assertEqual(audit_A(v)['diagnoses'][0]['mechanical_status'],'FAIL')
 def test_mechanical_pass_never_bypasses_semantic_review(self):
  r=audit_A(self.sample());self.assertEqual(r['diagnoses'][0]['mechanical_status'],'PASS');self.assertEqual(r['full_gate'],'PENDING_SOURCE_LINKED_REVIEW')
if __name__=='__main__':unittest.main()
